#!/usr/bin/env python3
"""Request Nav2 global paths for standalone MPPI nodes (no Nav2 controller server)."""
import math

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import ComputePathToPose
from nav_msgs.msg import Path
from std_msgs.msg import Empty


class PlannerBridge(Node):
    def __init__(self):
        super().__init__('planner_bridge')
        self.declare_parameter('replan_period', 2.0)
        self.declare_parameter('planning_timeout', 5.0)
        self.goal = None
        self.generation = 0
        self.request_id = 0
        self.pending = False
        self.pending_since = self.get_clock().now()
        self.goal_handle = None
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(Path, '/reference_path', qos)
        self.goal_sub = self.create_subscription(PoseStamped, '/goal_pose', self.on_goal, 1)
        self.stop_sub = self.create_subscription(Empty, '/stop_navigation', self.on_stop, 1)
        self.client = ActionClient(self, ComputePathToPose, '/compute_path_to_pose')
        self.timer = self.create_timer(self.get_parameter('replan_period').value, self.replan)

    def clear_path(self):
        path = Path()
        path.header.frame_id = 'map'
        path.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(path)

    def on_stop(self, _msg):
        self.generation += 1
        self.goal = None
        self.pending = False
        if self.goal_handle is not None:
            self.goal_handle.cancel_goal_async()
            self.goal_handle = None
        self.clear_path()

    def on_goal(self, msg):
        # This demo expects map-frame goals. Reject invalid inputs before planning.
        p, q = msg.pose.position, msg.pose.orientation
        if msg.header.frame_id != 'map' or not all(math.isfinite(v) for v in
                (p.x, p.y, p.z, q.x, q.y, q.z, q.w)):
            self.get_logger().error('Goal must contain finite values in the map frame')
            return
        norm = math.sqrt(q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w)
        if norm < 1e-6:
            self.get_logger().error('Goal orientation quaternion is invalid')
            return
        q.x, q.y, q.z, q.w = q.x/norm, q.y/norm, q.z/norm, q.w/norm
        self.on_stop(None)
        self.goal = msg
        self.replan()

    def replan(self):
        if self.goal is None:
            return
        if self.pending:
            elapsed = (self.get_clock().now() - self.pending_since).nanoseconds * 1e-9
            if elapsed < self.get_parameter('planning_timeout').value:
                return
            self.get_logger().warning('Planning timed out; stopping and retrying')
            self.request_id += 1  # Discard a late response to the expired request.
            self.pending = False
            self.clear_path()
            if self.goal_handle is not None:
                self.goal_handle.cancel_goal_async()
                self.goal_handle = None
        if not self.client.server_is_ready():
            self.clear_path()
            self.get_logger().warning('Waiting for Nav2 compute_path_to_pose')
            return
        request = ComputePathToPose.Goal()
        request.goal = self.goal
        request.goal.header.stamp = self.get_clock().now().to_msg()
        request.planner_id = 'GridBased'
        request.use_start = False
        self.pending = True
        self.pending_since = self.get_clock().now()
        self.request_id += 1
        token = (self.generation, self.request_id)
        future = self.client.send_goal_async(request)
        future.add_done_callback(lambda f: self.accepted(f, token))

    def current(self, token):
        return token == (self.generation, self.request_id)

    def accepted(self, future, token):
        try:
            handle = future.result()
            if not self.current(token):
                if handle.accepted:
                    handle.cancel_goal_async()
                return
            if not handle.accepted:
                self.pending = False
                self.clear_path()
                return
            self.goal_handle = handle
            handle.get_result_async().add_done_callback(lambda f: self.completed(f, token))
        except Exception as exc:
            self.failed(exc, token)

    def completed(self, future, token):
        if not self.current(token):
            return
        self.pending = False
        self.goal_handle = None
        try:
            result = future.result()
            if result.status != GoalStatus.STATUS_SUCCEEDED or len(result.result.path.poses) < 2:
                self.clear_path()
                return
            self.pub.publish(result.result.path)
        except Exception as exc:
            self.failed(exc, token)

    def failed(self, exc, token):
        if self.current(token):
            self.pending = False
            self.clear_path()
            self.get_logger().error('Planning failed: ' + str(exc))


def main():
    rclpy.init()
    node = PlannerBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
