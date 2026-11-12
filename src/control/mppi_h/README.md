# mppi_h

MPPI-H local planner for autonomous navigation of a 4wids vehicle.
MPPI-H switches between MPPI-3D and MPPI-4D controllers depending on the situation in real-time.

## Subscribing Topics

| Topic name      | Type                 | Description                                                  |
| --------------- | -------------------- | ------------------------------------------------------------ |
| /groundtruth_odom | nav_msgs/msg/Odometry | The ground truth odometry data. |
| /reference_path | nav_msgs/msg/Path | The global path data. |
| /global_costmap/costmap | nav_msgs/msg/OccupancyGrid | The local costmap data. |
| /distance_error_map | grid_map_msgs/msg/GridMap | The distance error map data. |
| /ref_yaw_map | grid_map_msgs/msg/GridMap | The reference yaw map data. |

## Publishing Topics

| Topic name      | Type              | Description                                                  |
| --------------- | ----------------- | ------------------------------------------------------------ |
| /cmd_vel | geometry_msgs/msg/Twist | The velocity command consisting of linear and angular velocities (vx, vy, omega). |
| `cmd.absvel` | std_msgs/msg/Float32 | The absolute velocity command. i.e. absvel = sqrt(vx^2 + vy^2). |
| `cmd.vx` | std_msgs/msg/Float32 | The linear velocity command. The front direction of the vehicle is positive. |
| `cmd.vy` | std_msgs/msg/Float32 | The lateral velocity command. The left direction of the vehicle is positive. |
| `cmd.omega` | std_msgs/msg/Float32 | The angular velocity command. The counter-clockwise direction is positive. |
| `calc_time` | std_msgs/msg/Float32 | The calculation time of the MPPI controller. |
| `overlay_text` | std_msgs/msg/String | The controller name as a plain String (the ROS 1 JSK overlay plugin is not used).|
| `optimal_traj` | visualization_msgs/msg/MarkerArray | The optimal trajectory for visualization. |
| `sampled_traj` | visualization_msgs/msg/MarkerArray | The sampled trajectory for visualization. |
| `eval_info` | mppi_eval_msgs/msg/MPPIEval | The evaluation information of the MPPI controller. |

## Node Parameters

Parameters are declared on the controller node and configured under `ros__parameters`. Use dotted names with `ros2 param get`, for example `ros2 param get /mppi_h navigation.xy_goal_tolerance`.

### Common Parameters

| Parameter name               | Type   | Description                                                  |
| ---------------------------- | ------ | ------------------------------------------------------------ |
| `navigation.xy_goal_tolerance` | double | The tolerance [m] to judge that the goal is reached. |
| `navigation.yaw_goal_tolerance` | double | The tolerance [rad] to judge that the goal is reached. |
| `target_system.d_l` | double | The distance [m] from the center of the vehicle to the left wheel. |
| `target_system.d_r` | double | The distance [m] from the center of the vehicle to the right wheel. |
| `target_system.l_f` | double | The distance [m] from the center of the vehicle to the front axle. |
| `target_system.l_r` | double | The distance [m] from the center of the vehicle to the rear axle. |
| `target_system.tire_radius` | double | The radius [m] of the tire. |
| `controller.common.control_interval` | double | The control interval [s]. |
| `controller.mode1.num_samples`, `controller.mode2.num_samples` | int | The number of samples [samples]. |
| `controller.common.prediction_horizon` | int | The prediction horizon [steps]. |
| `controller.common.step_len_sec` | double | The step length [s] in the prediction horizon. |
| `controller.mode1.param_exploration` | double | The exploration parameter of MPPI. |
| `mode_selector.yaw_error_threshold` | double | The yaw error threshold [rad] to switch between MPPI-3D and MPPI-4D. |
| `mode_selector.dist_error_threshold` | double | The distance error threshold [m] to switch between MPPI-3D and MPPI-4D. |

### Parameters of Mode 1 Controller (MPPI-3D)

| Parameter name               | Type   | Description                                                  |
| ---------------------------- | ------ | ------------------------------------------------------------ |
| `controller.mode1.param_lambda` | double | The lambda parameter of MPPI. |
| `controller.mode1.param_alpha` | double | The alpha parameter of MPPI. |
| `controller.mode1.sigma` | double[3] | The standard deviation of the noise for [vx, vy, omega]. |
| `controller.mode1.reduce_computation` | bool | If true, noise sampling is done only once and the same noise is used for all processes. |
| `controller.mode1.weight_cmd_change` | double[3] | The penalty weight for the variation of [vx, vy, omega]. |
| `controller.mode1.weight_vehicle_cmd_change` | double[8] | The penalty weight for the variation of [fl_steer, fr_steer, rl_steer, rr_steer, fl_vel, fr_vel, rl_vel, rr_vel]. |
| `controller.mode1.reference_velocity` | double | The reference velocity [m/s]. |
| `controller.mode1.weight_velocity_error` | double | The penalty weight for the velocity error. |
| `controller.mode1.weight_angular_error` | double | The penalty weight for the angular error. |
| `controller.mode1.weight_collision_penalty` | double | The penalty weight for the collision. |
| `controller.mode1.weight_distance_error_penalty` | double | The penalty weight for the distance error. |
| `controller.mode1.weight_terminal_state_penalty` | double | The penalty weight for the terminal state. |
| `controller.mode1.use_sg_filter` | bool | If true, Savitzky-Golay filter is used for smoothing the control input. |
| `controller.mode1.sg_filter_half_window_size` | int | The half window size of the Savitzky-Golay filter. |
| `controller.mode1.sg_filter_poly_order` | int | The polynomial order of the Savitzky-Golay filter. |

### Parameters of Mode 2 Controller (MPPI-4D)

| Parameter name               | Type   | Description                                                  |
| ---------------------------- | ------ | ------------------------------------------------------------ |
| `controller.mode2.param_lambda` | double | The lambda parameter of MPPI. |
| `controller.mode2.param_alpha` | double | The alpha parameter of MPPI. |
| `controller.mode2.sigma` | double[4] | The standard deviation of the noise for [fl_steer, rr_steer, fl_vel, rr_vel]. |
| `controller.mode2.reduce_computation` | bool | If true, noise sampling is done only once and the same noise is used for all processes. |
| `controller.mode2.weight_cmd_change` | double[4] | The penalty weight for the variation of [fl_steer, rr_steer, fl_vel, rr_vel]. |
| `controller.mode2.weight_vehicle_cmd_change` | double[8] | The penalty weight for the variation of [fl_steer, fr_steer, rl_steer, rr_steer, fl_vel, fr_vel, rl_vel, rr_vel]. |
| `controller.mode2.reference_velocity` | double | The reference velocity [m/s]. |
| `controller.mode2.weight_velocity_error` | double | The penalty weight for the velocity error. |
| `controller.mode2.weight_angular_error` | double | The penalty weight for the angular error. |
| `controller.mode2.weight_collision_penalty` | double | The penalty weight for the collision. |
| `controller.mode2.weight_distance_error_penalty` | double | The penalty weight for the distance error. |
| `controller.mode2.weight_terminal_state_penalty` | double | The penalty weight for the terminal state. |
| `controller.mode2.use_sg_filter` | bool | If true, Savitzky-Golay filter is used for smoothing the control input. |
| `controller.mode2.sg_filter_half_window_size` | int | The half window size of the Savitzky-Golay filter. |
| `controller.mode2.sg_filter_poly_order` | int | The polynomial order of the Savitzky-Golay filter. |

## Usage

To launch the node individually, run the following commands.

For mppi_h node:
```
source install/setup.bash
ros2 launch mppi_h mppi_h.launch.py
```

## Note

`ros2 topic echo /mppi/eval_info` will show you the evaluation information of the MPPI controller in real-time.
An example output is shown below.

```
header: 
  seq: 126
  stamp: 
    secs: 13
    nsecs: 660000000
  frame_id: "mppi_3d_b"
state_cost: 1134.80859375
global_x: 6.007351875305176
global_y: 2.598604202270508
global_yaw: 0.27291983366012573
cmd_vx: 1.464385747909546
cmd_vy: -0.19296832382678986
cmd_yawrate: 0.28070420026779175
cmd_steer_fl: -0.03971844166517258
cmd_steer_fr: -0.03277630731463432
cmd_steer_rl: -0.24662145972251892
cmd_steer_rr: -0.20479810237884521
cmd_rotor_fl: 6.625393390655518
cmd_rotor_fr: 8.028000831604004
cmd_rotor_rl: 6.826725959777832
cmd_rotor_rr: 8.1949462890625
calc_time_ms: 3.0
goal_reached: False
```
