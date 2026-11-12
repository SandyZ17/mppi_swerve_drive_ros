from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    share = Path(get_package_share_directory('mppi_bringup'))
    planner = LaunchConfiguration('local_planner').perform(context)
    if planner not in ('mppi_3d_a', 'mppi_3d_b', 'mppi_4d', 'mppi_h'):
        raise ValueError('Unsupported local_planner: ' + planner)
    world = LaunchConfiguration('gazebo_world_name').perform(context)
    if world not in ('maze', 'empty_garden', 'cylinder_garden'):
        raise ValueError('Navigation requires a saved map: maze, empty_garden, cylinder_garden')
    controller_pkg = 'mppi_3d' if planner.startswith('mppi_3d') else planner
    config = Path(get_package_share_directory(controller_pkg)) / 'config' / (planner + '.yaml')
    nav2 = str(share / 'config/nav2.yaml')
    nodes = [
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(
            share / 'launch/gazebo_world.launch.py')),
            launch_arguments={'gazebo_world_name': world, 'gui': LaunchConfiguration('gui'),
                              'use_joystick': 'false'}.items()),
        # Ground-truth demo: Gazebo world == map == odom. No AMCL is started.
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['--frame-id', 'map', '--child-frame-id', 'odom'],
             parameters=[{'use_sim_time': True}]),
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[nav2, {'yaml_filename': str(share / 'map' / world / 'map.yaml')}]),
        Node(package='nav2_planner', executable='planner_server', name='planner_server',
             output='screen', parameters=[nav2]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_navigation', output='screen',
             parameters=[{'use_sim_time': True, 'autostart': True,
                          'node_names': ['map_server', 'planner_server'], 'bond_timeout': 10.0}]),
        Node(package='mppi_bringup', executable='planner_bridge.py', output='screen',
             parameters=[{'use_sim_time': True}]),
        Node(package='reference_costmap_generator', executable='reference_costmap_generator_node',
             parameters=[{'use_sim_time': True, 'map_resolution_scale': 2.0}], output='screen'),
        Node(package=controller_pkg, executable=controller_pkg + '_node', output='screen',
             parameters=[str(config), {'use_sim_time': True}]),
    ]
    if LaunchConfiguration('open_rviz').perform(context).lower() == 'true':
        nodes.append(Node(package='rviz2', executable='rviz2',
                          arguments=['-d', str(share / 'rviz/navigation.rviz')],
                          parameters=[{'use_sim_time': True}], output='screen'))
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('local_planner', default_value='mppi_h'),
        DeclareLaunchArgument('gazebo_world_name', default_value='maze'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('open_rviz', default_value='true'),
        OpaqueFunction(function=setup),
    ])
