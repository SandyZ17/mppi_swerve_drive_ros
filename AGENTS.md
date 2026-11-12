# Repository Guidelines

## Project Structure & Module Organization

This ROS Noetic catkin workspace implements MPPI control for a four-wheel independent steering and driving robot.

- `src/control/`: `mppi_3d`, `mppi_4d`, and hybrid `mppi_h` controllers.
- `src/planning/`: reference costmap generation.
- `src/simulation/gazebo/`: vehicle models, worlds, velocity driver, and ground-truth odometry.
- `src/operation/`, `src/visualization/`, and `src/custom_msgs/`: joystick control, map visualization, and evaluation messages.
- Packages contain `src/`, `include/`, `config/`, and `launch/` directories as applicable. Root `launch/` and `config/` integrate navigation; `data/` stores maps and RViz settings. `scripts/` contains scenario generation, `docs/` setup instructions, and `media/` demonstrations.

## Build, Test, and Development Commands

Use Ubuntu 20.04 with ROS Noetic, or the supplied Docker environment. Run commands from the repository root.

- `make setup_docker`: build the Docker image; `make run_docker`: enter/start the container through Docker and rocker.
- `rosdep install -y --from-paths src --ignore-src --rosdistro noetic`: install ROS dependencies after rosdep initialization.
- `make build`: build with catkin tools, Clang 11, Release mode, and `-O2`.
- `make clean`: remove generated catkin build directories and configuration.
- `make gazebo_world`: launch the simulator; `make navigation`: launch autonomous navigation with MPPI-H.

To select another controller, use Bash:

```bash
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch launch/navigation.launch workspace:="$PWD" local_planner:=mppi_4d
```

## Coding Style & Naming Conventions

Match surrounding code: four-space indentation and separate-line braces in C++; four spaces in Python; two spaces in launch XML. Use `snake_case` filenames and variables, trailing underscores for C++ members, and existing CamelCase class/method conventions. Keep ROS parameters in package YAML files. No repository formatter or linter configuration is provided.

## Testing Guidelines

No automated test suite or coverage threshold is configured. Build affected packages and smoke-test navigation in Gazebo's `maze` world. Check goal completion, collision behavior, RViz trajectories, and `rostopic echo /mppi/eval_info`. Record planner, parameters, and environment because sampling and multithreading affect results. For new automated tests, use catkin-integrated gtest/rostest under the relevant package's `test/` directory and document execution.

## Commit & Pull Request Guidelines

History uses short, action-oriented subjects such as `Fix Dockerfile` and `improve visualization on rviz`; no enforced prefix scheme appears. Keep commits focused. PRs should explain behavior changes, link relevant issues, list build/simulation checks and parameter changes, and include screenshots or clips for visualization changes. Keep generated build outputs, results, and rosbags out of commits.
