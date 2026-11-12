"""Exercise wheel kinematics and command-loss stopping over native ROS 2 topics."""
import math
import subprocess
import time

import pytest
rclpy = pytest.importorskip('rclpy')
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray


def test_body_velocity_conversion_and_watchdog():
    rclpy.init()
    node = rclpy.create_node('vel_driver_test')
    angles, wheels = [], []
    angle_sub = node.create_subscription(Float64MultiArray, '/test/steer', angles.append, 10)
    wheel_sub = node.create_subscription(Float64MultiArray, '/test/wheels', wheels.append, 10)
    pub = node.create_publisher(Twist, '/test/cmd', 1)
    process = subprocess.Popen([
        'ros2', 'run', 'vel_driver', 'vel_driver_node', '--ros-args',
        '-p', 'control_cmd_vel_topic:=/test/cmd', '-p', 'steering_topic:=/test/steer',
        '-p', 'wheel_topic:=/test/wheels', '-p', 'command_timeout:=0.3'],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    def wait_for(predicate, timeout=10):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            assert process.poll() is None, process.stderr.read()
            if predicate():
                return
            rclpy.spin_once(node, timeout_sec=0.02)
        pytest.fail('Timed out waiting for velocity driver')
    try:
        wait_for(lambda: pub.get_subscription_count() > 0)
        for vx, vy, omega in [(1., 0., 0.), (0., 1., 0.), (-1., 0., 0.), (0., 0., 1.)]:
            angles.clear()
            wheels.clear()
            cmd = Twist()
            cmd.linear.x, cmd.linear.y, cmd.angular.z = vx, vy, omega
            pub.publish(cmd)
            wait_for(lambda: bool(angles) and any(any(abs(x) > 0 for x in w.data) for w in wheels))
            values = next(w.data for w in wheels if any(abs(x) > 0 for x in w.data))
            for i, (x, y) in enumerate([(0.5, 0.5), (0.5, -0.5), (-0.5, 0.5), (-0.5, -0.5)]):
                speed = values[i] * 0.2
                angle = angles[-1].data[i]
                assert speed * math.cos(angle) == pytest.approx(vx - omega*y, abs=1e-6)
                assert speed * math.sin(angle) == pytest.approx(vy + omega*x, abs=1e-6)
        wheels.clear()
        wait_for(lambda: any(len(w.data) == 4 and all(abs(v) < 1e-9 for v in w.data) for w in wheels), 2)
        # An invalid command must cause an immediate zero wheel-speed publication.
        wheels.clear()
        cmd = Twist()
        cmd.linear.x = float('nan')
        pub.publish(cmd)
        wait_for(lambda: any(all(abs(v) < 1e-9 for v in w.data) for w in wheels), 2)
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        node.destroy_node()
        rclpy.shutdown()
