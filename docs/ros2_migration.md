# ROS 2 Humble migration

## Target and layout

Development branch: `ros2-humble-docker`. The Docker image targets Ubuntu 22.04, ROS 2 Humble, and Gazebo Classic 11. The host needs no ROS installation. `compose.yaml` mounts the repository at `/ws`, uses host networking/IPC for DDS, and runs with the host user's UID/GID.

All 11 packages use `ament_cmake`; the custom evaluation message uses `rosidl`. Native C++ nodes use `rclcpp` publishers/subscriptions, explicitly declared parameters, ROS-time timers, typed messages, and ROS 2 TF broadcasting. There is no ROS 1 compatibility shim or bridge dependency.

The MPPI optimization cores and original controller variants are retained. Native Python launches replace ROS 1 XML launches. Configurations use `ros__parameters` and dotted names. Original Noetic navigation/RViz configuration is archived under `docs/ros1/`.

## Navigation integration

Nav2's map server and NavFn planner replace `move_base`. The planner's global costmap includes static obstacles, laser observations, and inflation; full occupancy grids are published periodically for MPPI. MPPI remains a standalone controller node, with its original sampler and cost functions, rather than becoming a Nav2 controller plugin.

`planner_bridge.py` accepts `/goal_pose` (`geometry_msgs/msg/PoseStamped`, frame `map`) and requests `ComputePathToPose` periodically. Successful paths are published on `/reference_path`. New goals invalidate the old path; stale action responses are ignored. Planning failure, timeout, or `/stop_navigation` clears the path so MPPI stops. This entrypoint does not provide the full Nav2 `NavigateToPose` action, behavior-tree navigation, or recovery behaviors.

The reference-map generator uses transient-local map delivery and preserves the incoming map's position. The controller waits for all required inputs, stops for an empty path, and stops when odometry, path, or obstacle-map updates become stale. Timers and freshness checks use ROS time.

## Simulation and mapping

`gazebo_ros2_control` replaces `gazebo_ros_control`. The controller manager activates a joint-state broadcaster and group position/velocity controllers. Steering and wheel-speed arrays follow front-left, front-right, rear-left, rear-right order.

The velocity driver retains base-frame no-slip kinematics, selects equivalent reverse wheel motion to avoid unnecessary steering rotation, preserves steering at zero speed, rejects non-finite commands, and stops wheels after command loss. Gazebo's ROS 2 ray and P3D plugins supply scans and ground truth. Worlds include their light/ground definitions to avoid downloading Gazebo models during launch. Launch manages child processes; the ROS 1 global `killall -9` signal handler was removed.

The navigation demo uses ground truth, with Gazebo world, map, and odom origins aligned. An identity `map -> odom` and simulated `odom -> base_link` provide its TF tree. AMCL and real hardware localization are not configured. Mapping runs separately through SLAM Toolbox and owns its `map -> odom` transform. ROS 1 bag files require separate conversion before ROS 2 playback.

The ROS 1 JSK overlay becomes a plain controller-name String topic; RViz2 uses native map, robot, path, scan, and trajectory displays.

## Validation

Reproduce the checks with:

```bash
make setup_docker
make build
make test
make navigation GUI=false RVIZ=false
# Second terminal, from a fresh simulation:
make smoke_test
```

Automated tests check ROS 2 manifests, Python launch syntax, controller parameter dimensions/types, simulator interfaces, late-subscriber map delivery, shifted map origins, wheel kinematics, and the driver watchdog. The smoke script checks active controllers, map/scan/odometry delivery, planning, nonzero commands, vehicle displacement, optional goal completion, and wheel stop delivery.

Target-container validation results:

| Check | Result |
| --- | --- |
| Native Humble colcon build | All 11 packages built |
| Automated regression tests | 7 passed, covering configuration, launch imports, DDS maps, kinematics/watchdog, and bridge invalidation |
| MPPI-3D(a), empty_garden, goal `(2.5, 0)` | Goal reached; stop command verified |
| MPPI-3D(b), empty_garden, goal `(2.5, 0)` | Goal reached; stop command verified |
| MPPI-4D, empty_garden, goal `(2.5, 0)` | Goal reached; stop command verified in an independent container |
| MPPI-H, empty_garden and maze, goal `(2.5, 0)` | Goal reached; stop command verified |
| SLAM Toolbox, maze | Scan registration and occupancy-map publication verified |

One sequential multi-launch run timed out while activating the wheel controllers for MPPI-4D. A fresh independent container activated all controllers and completed navigation; the startup timeout was not reproduced there or in a subsequent Compose run using the final image. The spawner now allows 30 seconds for controller switching/service responses, and launch shuts down with an explicit error if spawning or activation fails. Keep launch logs when investigating repeat startup failures. GUI display, joystick hardware, physical robot operation, long-run reliability, and benchmark parity have not been verified. The SLAM check establishes initial map publication, not complete map quality.

## API references

- [Humble gazebo_ros2_control integration](https://control.ros.org/humble/doc/gazebo_ros2_control/doc/index.html)
- [Humble group position command interface](https://control.ros.org/humble/doc/ros2_controllers/position_controllers/doc/userdoc.html)
- [Nav2 Humble PlannerServer implementation](https://github.com/ros-navigation/navigation2/blob/humble/nav2_planner/src/planner_server.cpp)
- [grid_map Humble ROS converter API](https://github.com/ANYbotics/grid_map/blob/humble/grid_map_ros/include/grid_map_ros/GridMapRosConverter.hpp)
