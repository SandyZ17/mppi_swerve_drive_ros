# vel_driver (ROS 2 Humble)

Converts base-frame `/cmd_vel` (`geometry_msgs/msg/Twist`) into four steering positions and four wheel angular velocities under the no-slip kinematic assumption.

Outputs accept `std_msgs/msg/Float64MultiArray`:

- `/fwids/steering_controller/commands`: steering angles in radians.
- `/fwids/wheel_controller/commands`: wheel angular velocities in rad/s.

Both arrays use front-left, front-right, rear-left, rear-right order. Equivalent reverse wheel motion keeps steering in ±pi/2. Zero velocity preserves steering; non-finite commands or command loss stop wheel rotation. The timeout defaults to 0.5 seconds of ROS time.

```bash
source install/setup.bash
ros2 launch vel_driver vel_driver.launch.py use_sim_time:=true
```

Geometry, topics, and timeout are configured in `config/vel_driver.yaml`. This driver is started by the integrated simulation launch.
