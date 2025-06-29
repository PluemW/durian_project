from launch_ros.substitutions import FindPackageShare
import launch_ros.actions

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution

import sys
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_path = get_package_share_directory('robot_simulation')
    gz_worlds_path = os.path.join(get_package_share_directory('robot_world'))
    world_path = os.path.join(gz_worlds_path,'world','empty_world.sdf')
    gui = "-r"
    for arg in sys.argv:
        if arg.startswith("gui:="):
            gui = str(arg.split(":=")[1])

    gazebo_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('ros_gz_sim'),
                    'launch',
                    'gz_sim.launch.py'
                ])
            ]),
            launch_arguments={
                'gz_args': TextSubstitution(text=f"{gui} {world_path}")
            }.items()
        )

    spawn_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    pkg_path,
                    'launch',
                    'summon.launch.py'
                ])
            ])
        )
    
    return LaunchDescription([
        gazebo_launch,
        spawn_launch
    ])
