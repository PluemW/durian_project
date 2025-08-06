#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    robot_description_pkg = get_package_share_directory('robot_description')
    simulation_pkg = get_package_share_directory('robot_simulation')

    xacro_file = os.path.join(robot_description_pkg, 'urdf', 'robot.urdf.xacro')
    bridge_config_file = os.path.join(simulation_pkg, 'config', 'robot_config.yaml')

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro', ' ', xacro_file]),
            'use_sim_time': use_sim_time,
        }]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': Command(['xacro', ' ', xacro_file])
        }],
    )

    # Gazebo spawn node
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'robot',
            '-z', '0.4',
            '-topic', '/robot_description'
        ],
        output='screen'
    )

    # Gazebo bridge
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name="controller_bridge",
        parameters=[{
            "config_file": bridge_config_file,
            "use_sim_time": use_sim_time,
        }],
        output='screen'
    )

    # Custom TF and controller nodes (optional, include if used)
    tf_manager = Node(
        package='robot_simulation',
        executable='robot_tf_manager',
        name='tf_manager',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    tf_odom_transform = Node(
        package='robot_simulation',
        executable='odom_transform',
        name='odom_transform',
        output='screen'
    )

    robot_controller = Node(
        package='robot_simulation',
        executable='robot_controller',
        name='robot_controller',
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        robot_state_publisher,
        joint_state_publisher,
        spawn_robot,
        gz_bridge,
        tf_manager,
        tf_odom_transform,
        robot_controller,
    ])
