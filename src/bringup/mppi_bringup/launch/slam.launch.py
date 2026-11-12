from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = Path(get_package_share_directory('mppi_bringup'))
    return LaunchDescription([
        DeclareLaunchArgument('gazebo_world_name', default_value='maze'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('use_joystick', default_value='false'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(share / 'launch/gazebo_world.launch.py')),
            launch_arguments={'gazebo_world_name': LaunchConfiguration('gazebo_world_name'),
                              'gui': LaunchConfiguration('gui'),
                              'use_joystick': LaunchConfiguration('use_joystick')}.items()),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(
            Path(get_package_share_directory('slam_toolbox')) / 'launch/online_async_launch.py')),
            launch_arguments={'use_sim_time': 'true',
                              'slam_params_file': str(share / 'config/slam.yaml')}.items()),
    ])
