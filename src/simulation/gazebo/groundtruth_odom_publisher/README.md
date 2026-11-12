# groundtruth_odom_publisher (ROS 2 Humble)

Subscribes to Gazebo's `/sim/groundtruth_odom`, republishes `/groundtruth_odom`, and broadcasts `odom -> base_link` using the simulator message timestamp. The supplied demo aligns simulator world, map, and odom origins; the republished pose is labeled `map`.

```bash
source install/setup.bash
ros2 launch groundtruth_odom_publisher groundtruth_odom_publisher.launch.py use_sim_time:=true
```

This is a simulation adapter. A real localization system must supply map-frame poses and a consistent TF tree. The navigation launch adds an identity `map -> odom`; the SLAM launch lets SLAM Toolbox provide that transform.
