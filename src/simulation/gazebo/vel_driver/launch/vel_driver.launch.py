from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from pathlib import Path


def generate_launch_description():
    config = str(Path(get_package_share_directory('vel_driver')) / 'config' / 'vel_driver.yaml')
    nodes = [Node(package='vel_driver', executable='vel_driver_node', output='screen',
                  parameters=[config, {'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)}])]
    return LaunchDescription([DeclareLaunchArgument('use_sim_time', default_value='false')] + nodes)
