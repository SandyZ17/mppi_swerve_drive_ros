#!/usr/bin/env python3
"""Validate a running headless navigation launch, including motion and stop delivery."""
import argparse
import json
import math
import time

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from mppi_eval_msgs.msg import MPPIEval
from nav_msgs.msg import Odometry, OccupancyGrid, Path
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Empty, Float64MultiArray
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from controller_manager_msgs.srv import ListControllers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=float, default=120.0)
    parser.add_argument('--require-goal', action='store_true')
    parser.add_argument('--goal-x', type=float, default=2.5)
    parser.add_argument('--goal-y', type=float, default=0.0)
    args = parser.parse_args()
    rclpy.init()
    node = rclpy.create_node('mppi_smoke_test')
    state = {'odom': None, 'map': None, 'scan': None, 'path': None, 'eval': None,
             'wheels': None, 'moving_command': False}
    subscriptions = []
    def store(key):
        return lambda msg: state.update({key: msg})
    latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
    for typ, topic, key, qos in [
        (Odometry, '/groundtruth_odom', 'odom', qos_profile_sensor_data),
        (OccupancyGrid, '/map', 'map', latched),
        (LaserScan, '/laser_link/scan', 'scan', qos_profile_sensor_data),
        (Path, '/reference_path', 'path', latched),
        (MPPIEval, '/mppi/eval_info', 'eval', 10),
        (Float64MultiArray, '/fwids/wheel_controller/commands', 'wheels', 10),
    ]:
        subscriptions.append(node.create_subscription(typ, topic, store(key), qos))
    def command(msg):
        if math.hypot(msg.linear.x, msg.linear.y) > 0.01:
            state['moving_command'] = True
    subscriptions.append(node.create_subscription(Twist, '/cmd_vel', command, 10))
    goal_pub = node.create_publisher(PoseStamped, '/goal_pose', 1)
    stop_pub = node.create_publisher(Empty, '/stop_navigation', 1)
    client = node.create_client(ListControllers, '/fwids/controller_manager/list_controllers')
    deadline = time.monotonic() + args.timeout
    def wait_for(predicate, message):
        while time.monotonic() < deadline:
            if predicate():
                return
            rclpy.spin_once(node, timeout_sec=0.1)
        raise RuntimeError(message)
    try:
        wait_for(lambda: all(state[k] is not None for k in ('odom', 'map', 'scan')) and
                 goal_pub.get_subscription_count() > 0 and client.service_is_ready(),
                 'Simulator/map/scan/controller manager did not become ready')
        def controllers_ready():
            future = client.call_async(ListControllers.Request())
            rclpy.spin_until_future_complete(node, future, timeout_sec=2)
            if not future.done():
                return False
            active = {c.name for c in future.result().controller if c.state == 'active'}
            return {'joint_state_broadcaster', 'steering_controller', 'wheel_controller'} <= active
        wait_for(controllers_ready, 'Wheel controllers did not become active')
        start = state['odom'].pose.pose.position
        start_xy = (start.x, start.y)
        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.header.stamp = node.get_clock().now().to_msg()
        goal.pose.position.x, goal.pose.position.y = args.goal_x, args.goal_y
        goal.pose.orientation.w = 1.0
        goal_pub.publish(goal)
        def moved():
            p = state['odom'].pose.pose.position
            return (state['eval'] is not None and state['path'] is not None and
                    len(state['path'].poses) > 1 and state['moving_command'] and
                    math.hypot(p.x - start_xy[0], p.y - start_xy[1]) > 0.2)
        wait_for(moved, 'No MPPI evaluation/path/nonzero control/robot motion')
        if args.require_goal:
            wait_for(lambda: state['eval'].goal_reached, 'Robot did not reach the goal')
        p = state['odom'].pose.pose.position
        report = {'planner': state['eval'].header.frame_id,
                  'displacement_m': math.hypot(p.x-start_xy[0], p.y-start_xy[1]),
                  'calc_time_ms': state['eval'].calc_time_ms,
                  'goal_reached': state['eval'].goal_reached}
        state['wheels'] = None
        stop_pub.publish(Empty())
        wait_for(lambda: state['wheels'] is not None and len(state['wheels'].data) == 4 and
                 all(abs(v) < 1e-9 for v in state['wheels'].data), 'Stop did not reach wheel controllers')
        report['stop_verified'] = True
        print(json.dumps(report, indent=2))
    finally:
        stop_pub.publish(Empty())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
