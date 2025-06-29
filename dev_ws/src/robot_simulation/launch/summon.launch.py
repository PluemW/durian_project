#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
import launch_ros
import launch

import xacro

def generate_launch_description():

    # Check if we're told to use sim time
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Process the URDF file
    pkg_path = os.path.join(get_package_share_directory('robot_simulation'))
    robot_path = os.path.join(get_package_share_directory('robot_description'))

    bridge_path = os.path.join(pkg_path,"config","robot_config.yaml")

    xacro_file = os.path.join(robot_path,'urdf','robot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    
    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config.toxml(), 'use_sim_time': use_sim_time}
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

     # Spawn
    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=[
                    '-name', 'robot',
                    # '-x', '0',
                    # '-z', '0',
                    # '-y', '0',
                    # '-Y', '-1.48',
                    '-topic', '/robot_description'],
                 output='screen')

    bridge = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name="controller_bridge",
            parameters=[{
                "config_file": bridge_path,
                "use_sim_time": LaunchConfiguration('use_sim_time'),
            }]
        )

    # launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='True',
    #                                         description='Flag to enable use_sim_time')
    
    # tf_manager = Node(
    #     package='robot_simulation',
    #     executable='xgateway_tf_manager',
    #     name='tf_manager',
    #     output='screen',
    #     parameters=[{
    #         "use_sim_time": LaunchConfiguration('use_sim_time'),
    #     }]
    # )
    
    # tf_odom2base_link = Node(
    #         package='robot_simulation',
    #         executable='odom_transform',
    #         name="odom_transform",
    # )

    # tf_map2odom_ = ExecuteProcess(
    #         cmd=['/opt/ros/humble/lib/tf2_ros/static_transform_publisher',
    #              '--frame-id', 'world',
    #              '--child-frame-id', 'odom'],
    #         output='screen',
    # )

    # xgateway_controller = Node(
    #     package="xgateway_nav2",
    #     executable="xgateway_controller.py"
    # )

    # Launch
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use sim time if true'),
        robot_state_publisher,
        bridge,
        spawn,
        # tf_manager,
        # tf_odom2base_link,
        # tf_map2odom_,
        # xgateway_controller
    ])
