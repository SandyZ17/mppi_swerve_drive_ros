"""Verify goal invalidation and late-result suppression in the Nav2 bridge."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
rclpy = pytest.importorskip('rclpy')
from geometry_msgs.msg import PoseStamped


def test_stop_invalidates_late_plans():
    path = Path(__file__).resolve().parents[1] / 'src/bringup/mppi_bringup/scripts/planner_bridge.py'
    spec = importlib.util.spec_from_file_location('planner_bridge_under_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rclpy.init()
    node = module.PlannerBridge()
    published = []
    node.pub = SimpleNamespace(publish=published.append)
    try:
        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.pose.position.x = 2.5
        goal.pose.orientation.w = 1.0
        node.on_goal(goal)
        assert node.goal is not None
        old_token = (node.generation, node.request_id)
        node.on_stop(None)
        assert node.goal is None
        assert len(published[-1].poses) == 0
        count = len(published)
        # A result for a goal cancelled by the user must never restore motion.
        node.completed(object(), old_token)
        assert len(published) == count
        # Reject a goal without a valid orientation quaternion.
        invalid = PoseStamped()
        invalid.header.frame_id = 'map'
        invalid.pose.orientation.w = 0.0
        node.on_goal(invalid)
        assert node.goal is None
    finally:
        node.destroy_node()
        rclpy.shutdown()
