from pathlib import Path
import xacro
import xml.etree.ElementTree as ET
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.logging import get_logger
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    share = Path(get_package_share_directory('world_handler'))
    world = LaunchConfiguration('gazebo_world_name').perform(context)
    if world not in ('maze', 'empty', 'empty_garden', 'cylinder_garden'):
        raise ValueError('Unknown world: ' + world)
    description = xacro.process_file(str(share / 'xacro/fwids_vehicle.xacro'),
        mappings={'controllers_file': str(share / 'config/fwids_controller.yaml')}).toxml()
    # Drop XML comments before gazebo_ros2_control forwards the description as a parameter.
    description = ET.tostring(ET.fromstring(description), encoding='unicode')
    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource(str(
        Path(get_package_share_directory('gazebo_ros')) / 'launch/gazebo.launch.py')),
        launch_arguments={'world': str(share / 'world' / (world + '.world')),
                          'gui': LaunchConfiguration('gui'), 'verbose': 'false'}.items())
    state_publisher = Node(package='robot_state_publisher', executable='robot_state_publisher',
        parameters=[{'robot_description': description, 'use_sim_time': True}],
        remappings=[('joint_states', '/fwids/joint_states')], output='screen')
    spawn = Node(package='gazebo_ros', executable='spawn_entity.py',
        arguments=['-entity', 'fwids', '-topic', '/robot_description', '-z', '0.6', '-timeout', '120'],
        output='screen')
    controllers = Node(package='controller_manager', executable='spawner',
        arguments=['joint_state_broadcaster', 'steering_controller', 'wheel_controller',
                   '-c', '/fwids/controller_manager', '--controller-manager-timeout', '120',
                   '--switch-timeout', '30', '--service-call-timeout', '30'], output='screen')
    def spawned(event, _context):
        if event.returncode != 0:
            get_logger('world_handler').error('Vehicle spawn failed; stopping simulation')
            return [EmitEvent(event=Shutdown(reason='Vehicle spawn failed'))]
        return [controllers]

    def controllers_finished(event, _context):
        if event.returncode != 0:
            get_logger('world_handler').error('Controller activation failed; stopping simulation')
            return [EmitEvent(event=Shutdown(reason='Controller activation failed'))]
        return []

    return [gazebo, state_publisher,
            RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=spawned)),
            RegisterEventHandler(OnProcessExit(target_action=controllers, on_exit=controllers_finished)), spawn]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('gazebo_world_name', default_value='maze'),
        DeclareLaunchArgument('gui', default_value='true'), OpaqueFunction(function=setup)])
