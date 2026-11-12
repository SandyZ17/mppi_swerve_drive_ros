# Native ROS 2 Humble development

The supported native target is Ubuntu 22.04 with ROS 2 Humble and Gazebo Classic 11. Prefer the Docker workflow on other host distributions.

After installing Humble, rosdep, and colcon:

```bash
source /opt/ros/humble/setup.bash
# Run sudo rosdep init only if rosdep has never been initialized.
rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
make local_build
source install/setup.bash
ros2 launch mppi_bringup navigation.launch.py local_planner:=mppi_h
```

The controller requires Eigen3 and OpenMP. Ubuntu's standard compiler supplies OpenMP; Clang 11 is no longer required. All C++ targets use C++17.

Run tests with `python3 -m pytest -q tests` after installing pytest/PyYAML and sourcing the overlay. In a second terminal during a headless launch, run `python3 scripts/smoke_test_ros2.py --require-goal`.

See the main README for map-frame goals, stop commands, standalone controller launch files, and SLAM Toolbox mapping.
