# ROS 2 Humble in Docker

Use Docker Engine with Compose v2 on a Linux host. The image contains Ubuntu 22.04, Humble, Gazebo Classic 11, Nav2, grid_map, ros2_control, RViz2, and build dependencies. ROS does not need to be installed on the host.

## Build and run

From the repository root:

```bash
make setup_docker
make build
make navigation GUI=false RVIZ=false
```

`make` exports your host UID/GID to Compose. The image creates a matching user, and `/ws` is a bind mount of the repository. Files written by builds remain editable on the host. The dependency image is reusable; C++ changes require `make build`, not an image rebuild.

To use Compose directly, export these first:

```bash
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)
docker compose build dev
docker compose run --rm dev bash
```

The entrypoint sources `/opt/ros/humble/setup.bash` and `/ws/install/setup.bash` when present. An already-open shell needs `source install/setup.bash` after its first manual build. Set `ROS_DOMAIN_ID` consistently across terminals if running several ROS projects on the same host.

## GUI

For an available X11/XWayland display:

```bash
xhost +si:localuser:$(id -un)
make navigation
xhost -si:localuser:$(id -un)  # Revoke when finished
```

Compose passes `DISPLAY` and the X11 socket. On a remote server without a display, use `GUI=false RVIZ=false`. Software OpenGL rendering is the default. GPU passthrough is environment-specific and is not needed for the controller or headless simulation.

## Goals, checks, and stopping

```bash
make run_docker
# In the container:
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  '{header: {frame_id: map}, pose: {position: {x: 2.5, y: 0.0}, orientation: {w: 1.0}}}'
ros2 topic echo /mppi/eval_info
ros2 control list_controllers -c /fwids/controller_manager
ros2 topic pub --once /stop_navigation std_msgs/msg/Empty '{}'
```

Ctrl+C shuts down launch and its child processes. There is no global `killall` handler. `make test` runs automated checks; `make smoke_test` checks a running default navigation launch.

## Optional joystick and bags

Pass the device explicitly when using a joystick:

```bash
export LOCAL_UID=$(id -u) LOCAL_GID=$(id -g)
docker compose run --rm --device /dev/input:/dev/input dev \
  ros2 launch mppi_bringup gazebo_world.launch.py use_joystick:=true
```

The container user also needs the device's group permissions; add the corresponding numeric GID with Compose `group_add` if necessary. Autonomous navigation disables joystick commands.

`ros2 bag record` writes to the bind mount if you choose a `/ws/...` output path. Play ROS 2 bags with `ros2 bag play <directory> --clock`; ROS 1 `.bag` files require separate conversion.

## Troubleshooting

- Docker socket permission errors: configure Docker access for your Linux user before running Make targets.
- `Package ... not found`: run `make build` and open a new `make run_docker` shell.
- Missing wheel controllers: inspect launch output and `ros2 control list_controllers -c /fwids/controller_manager`.
- DDS discovery: containers use host networking and host IPC. Keep `ROS_DOMAIN_ID` and ROS middleware consistent.
- Build memory pressure: use `make build JOBS=1`. `OMP_NUM_THREADS` controls runtime solver parallelism, not build parallelism.
- Old catkin artifacts: remove the old `devel/`, `build/`, and `.catkin_tools/` before the first ROS 2 build; do not source a Noetic overlay.
