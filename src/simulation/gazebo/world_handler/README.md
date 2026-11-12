# world_handler (ROS 2 Humble)

Installs the vehicle xacro, self-contained Gazebo Classic worlds, ros2_control settings, and the simulator launch file. Process shutdown is handled by ROS 2 launch.

```bash
source install/setup.bash
ros2 launch world_handler gazebo_world.launch.py gazebo_world_name:=maze gui:=true
```

For odometry, wheel-command conversion, and optional joystick control, use `ros2 launch mppi_bringup gazebo_world.launch.py` instead. Worlds: `empty`, `maze`, `empty_garden`, `cylinder_garden`.

The `gazebo_ros2_control` plugin runs `/fwids/controller_manager` with `joint_state_broadcaster`, `steering_controller`, and `wheel_controller`. The two command topics accept `std_msgs/msg/Float64MultiArray`; joint order is front-left, front-right, rear-left, rear-right. The laser publishes `/laser_link/scan`; the P3D plugin publishes world-frame `/sim/groundtruth_odom`.
