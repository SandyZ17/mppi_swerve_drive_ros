# mppi_swerve_drive_ros
**MPPI (Model Predictive Path-Integral) Controller for a Swerve Drive Robot — ROS 2 Humble / Docker**

<div align="center">

![image](https://github.com/user-attachments/assets/56d055e7-f3a4-4c89-940f-577b00e4f088)

[[Website]](https://mizuhoaoki.github.io/projects/iros2024)
[[PDF]](https://mizuhoaoki.github.io/media/papers/IROS2024_paper_mizuhoaoki.pdf)
[[Arxiv]](https://arxiv.org/abs/2409.08648)
[[IEEE Xplore]](https://ieeexplore.ieee.org/document/10802359)
[[Poster]](https://mizuhoaoki.github.io/projects/iros2024_poster.pdf)

[![ROS Distro: Humble](https://img.shields.io/badge/ROS_2-Humble-blue.svg)](https://docs.ros.org/en/humble/)
[![Docker](https://img.shields.io/badge/-Docker-EEE.svg?logo=docker&style=flat)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Conference: IROS](https://img.shields.io/badge/Publication-IROS2024-purple.svg)](https://iros2024-abudhabi.org/)

<!-- 1-min presentation movie -->
<!-- https://github.com/user-attachments/assets/0b18bb4d-c6ad-407b-919c-c8c3c219d75c -->

<!-- eyecatch movie -->
![eyecatch_anim_3drviz](./media/eyecatch_anim_3drviz.gif)

</div>

## Citation
If you use this work in an academic context, please cite the following publication:
```bibtex
@inproceedings{mizuho2024iros,
  author={Aoki, Mizuho and Honda, Kohei and Okuda, Hiroyuki and Suzuki, Tatsuya},
  booktitle={2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)}, 
  title={Switching Sampling Space of Model Predictive Path-Integral Controller to Balance Efficiency and Safety in 4WIDS Vehicle Navigation}, 
  year={2024},
  volume={},
  number={},
  pages={3196-3203},
  doi={10.1109/IROS58592.2024.10802359}}
```

> [!IMPORTANT]  
> **More Advanced Controller is Also Open Source!**  
> Check **[Nullspace MPC Repository](https://github.com/MizuhoAOKI/nullspace_mpc)**  
> Compared to MPPI, it achieves **faster navigation** while ensuring **higher safety**,  
> at the cost of **increased computational demand**.

## ROS 2 Humble: Docker quick start

This branch ports the controllers to native `rclcpp`, custom messages to `rosidl`, and packages to `ament_cmake`/`colcon`. It targets **Ubuntu 22.04 + ROS 2 Humble + Gazebo Classic 11** inside Docker. The Linux host only needs Docker Engine, the Compose v2 plugin, and Make.

```bash
make setup_docker       # Build mppi-swerve:humble with all dependencies
make build              # Compile all 11 packages in Docker
make navigation GUI=false RVIZ=false   # Headless Gazebo + Nav2 + MPPI-H
```

In a second terminal, send a map-frame goal:

```bash
make run_docker
# Inside the container:
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  '{header: {frame_id: map}, pose: {position: {x: 2.5, y: 0.0}, orientation: {w: 1.0}}}'
```

Stop navigation with `ros2 topic pub --once /stop_navigation std_msgs/msg/Empty '{}'`. Use Ctrl+C in the launch terminal to shut down the simulation.

For Gazebo/RViz windows on Linux with X11 or XWayland:

```bash
xhost +si:localuser:$(id -un)
make navigation
# When finished:
xhost -si:localuser:$(id -un)
```

Use RViz's **2D Goal Pose** tool to set goals. Software rendering is enabled by default; set `LIBGL_ALWAYS_SOFTWARE=0` only when your Docker GPU/display setup supports it. See [Docker setup](docs/setup_env_on_docker_detail.md) for host UID/GID, networking, and troubleshooting.

## Controllers and worlds

```bash
make navigation PLANNER=mppi_3d_a
make navigation PLANNER=mppi_3d_b
make navigation PLANNER=mppi_4d
make navigation PLANNER=mppi_h WORLD=cylinder_garden
```

`mppi_3d_a` and `mppi_3d_b` sample vehicle velocities `(vx, vy, omega)` with different weights. `mppi_4d` samples front-left/rear-right steering angles and wheel velocities. `mppi_h` switches sampling space according to distance/yaw tracking error and transfers the optimized velocity sequence between modes.

Navigation worlds: `maze` (default), `empty_garden`, `cylinder_garden`. Simulator-only mode additionally supports `empty`:

```bash
make gazebo_world WORLD=empty GUI=false
```

## Architecture

```text
/goal_pose -> planner_bridge -> Nav2 ComputePathToPose
                                  |
                          /reference_path
                                  |
/map -> reference_costmap_generator -> distance/yaw maps
                                  |
/groundtruth_odom + /global_costmap/costmap -> MPPI -> /cmd_vel
                                                       |
                                      vel_driver -> ros2_control -> Gazebo
```

Nav2 provides its map server, NavFn global planner, and a full global costmap with static, laser obstacle, and inflation layers. A separate MPPI node generates velocity commands; this branch does not start Nav2's controller server or expose `NavigateToPose`. Send goals to `/goal_pose`.

The supplied navigation demo uses simulator ground truth: Gazebo world, `map`, and `odom` share an origin, with identity `map -> odom`. AMCL is not started. Replace the ground-truth adapter and TF setup when connecting real localization or hardware.

## Configuration and development

- Controller parameters: `src/control/<package>/config/*.yaml`, in ROS 2 `ros__parameters` format with dotted parameter names.
- Nav2/SLAM configuration and RViz: `src/bringup/mppi_bringup/`.
- Robot, controllers, worlds: `src/simulation/gazebo/world_handler/`.
- Historical Noetic settings: `docs/ros1/`; these are not loaded by ROS 2.

```bash
make run_docker
# Inside the container:
ros2 launch mppi_bringup navigation.launch.py local_planner:=mppi_h gui:=false open_rviz:=false
ros2 topic echo /mppi/eval_info
ros2 control list_controllers -c /fwids/controller_manager
```

The entrypoint sources Humble and an existing `/ws/install` overlay. After manually building in an already-open shell, run `source install/setup.bash`. Source is bind-mounted; rebuild C++ with `make build`. Build artifacts belong to your host UID/GID. Use `make clean` to remove `build/`, `install/`, and `log/`.

## Validation

```bash
make test                # Parameter/model checks and DDS reference-map regression test
# While headless navigation runs, in a second terminal:
make smoke_test          # Check controllers, planning, motion, goal completion, and stop
```

`smoke_test` targets `(2.5, 0)` from the initial pose and expects the default maze navigation demo. It is a functional smoke check, not a navigation benchmark. Sampling, simulation rate, CPU load, and thread count affect results. `OMP_NUM_THREADS` defaults to 4 in Compose.

## Mapping and recording

ROS 1 gmapping is replaced with SLAM Toolbox. Run mapping separately from navigation:

```bash
make slam GUI=false
# In another container shell, drive with /cmd_vel or an attached joystick.
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.2}}'
# Ctrl+C stops publication; the driver watchdog stops wheel rotation.
ros2 run nav2_map_server map_saver_cli -f /ws/data/my_map
ros2 bag record -o /ws/rosbag/demo /groundtruth_odom /cmd_vel /mppi/eval_info /tf /tf_static
```

Enable a joystick with `ros2 launch mppi_bringup gazebo_world.launch.py use_joystick:=true`, and pass `/dev/input` to Docker explicitly. It is disabled during autonomous navigation to avoid competing commands. SLAM launch publishes its own `map -> odom`; do not run it with the ground-truth navigation launch.

See [native setup](docs/setup_env_on_native_detail.md) and [migration details](docs/ros2_migration.md).
