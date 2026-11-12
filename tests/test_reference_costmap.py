"""Exercise DDS delivery and map coordinates with a late-subscribing ROS 2 node."""
import subprocess
import time

import pytest

rclpy = pytest.importorskip('rclpy')
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid, Path
from grid_map_msgs.msg import GridMap
from rclpy.qos import DurabilityPolicy, QoSProfile


def test_shifted_map_origin_and_latched_map():
    rclpy.init()
    node = rclpy.create_node('reference_costmap_test')
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
    map_pub = node.create_publisher(OccupancyGrid, '/test/map', qos)
    path_pub = node.create_publisher(Path, '/test/path', 1)
    received = []
    sub = node.create_subscription(GridMap, '/test/distance', received.append, qos)
    grid = OccupancyGrid()
    grid.header.frame_id = 'map'
    grid.info.resolution = 1.0
    grid.info.width = grid.info.height = 10
    grid.info.origin.position.x = 20.0
    grid.info.origin.position.y = 30.0
    grid.info.origin.orientation.w = 1.0
    grid.data = [0] * 100
    map_pub.publish(grid)  # Publish before the generator exists.
    process = subprocess.Popen([
        'ros2', 'run', 'reference_costmap_generator', 'reference_costmap_generator_node',
        '--ros-args', '-p', 'map_topic:=/test/map', '-p', 'ref_path_topic:=/test/path',
        '-p', 'distance_error_map_topic:=/test/distance', '-p', 'ref_yaw_map_topic:=/test/yaw'],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        path = Path()
        path.header.frame_id = 'map'
        for x in (22.0, 23.0, 24.0):
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x, pose.pose.position.y = x, 32.0
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        deadline = time.monotonic() + 20
        while not received and time.monotonic() < deadline:
            assert process.poll() is None, process.stderr.read()
            path_pub.publish(path)
            rclpy.spin_once(node, timeout_sec=0.1)
        assert received, 'No reference costmap delivered over DDS'
        info = received[-1].info
        assert info.pose.position.x == pytest.approx(25.0)
        assert info.pose.position.y == pytest.approx(35.0)
        assert info.length_x == pytest.approx(10.0)
        assert 'distance_error' in received[-1].layers
        # An empty path must not crash the generator or produce a bogus map.
        path_pub.publish(Path())
        rclpy.spin_once(node, timeout_sec=0.2)
        assert process.poll() is None
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        node.destroy_node()
        rclpy.shutdown()
