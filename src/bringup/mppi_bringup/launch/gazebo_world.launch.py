from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    share = Path(get_package_share_directory('world_handler'))
    nodes = [
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(share / 'launch/gazebo_world.launch.py')),
            launch_arguments={'gazebo_world_name': LaunchConfiguration('gazebo_world_name'),
                              'gui': LaunchConfiguration('gui')}.items()),
        Node(package='groundtruth_odom_publisher', executable='groundtruth_odom_publisher_node',
             parameters=[{'use_sim_time': True}], output='screen'),
        Node(package='vel_driver', executable='vel_driver_node',
             parameters=[{'use_sim_time': True}], output='screen'),
    ]
    if LaunchConfiguration('use_joystick').perform(context).lower() == 'true':
        config = Path(get_package_share_directory('joy_controller')) / 'config/joy_controller.yaml'
        joy_config = Path(get_package_share_directory('joy_controller')) / 'config/joy.yaml'
        nodes += [Node(package='joy', executable='joy_node', parameters=[str(joy_config), {'use_sim_time': True}]),
                  Node(package='joy_controller', executable='joy_controller_node',
                       parameters=[str(config), {'use_sim_time': True}])]
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('gazebo_world_name', default_value='maze'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('use_joystick', default_value='false'),
        OpaqueFunction(function=setup)])
