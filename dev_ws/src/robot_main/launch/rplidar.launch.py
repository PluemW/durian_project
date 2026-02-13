#!/usr/bin/env python3
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import ExecuteProcess


def generate_launch_description():

    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    serial_baudrate = LaunchConfiguration('serial_baudrate', default='115200')
    frame_id = LaunchConfiguration('frame_id', default='laser')

    return LaunchDescription([

        DeclareLaunchArgument(
            'serial_port',
            default_value=serial_port,
            description='USB port of RPLIDAR'),

        DeclareLaunchArgument(
            'serial_baudrate',
            default_value=serial_baudrate,
            description='Baudrate of RPLIDAR A1'),

        DeclareLaunchArgument(
            'frame_id',
            default_value=frame_id,
            description='Frame ID'),

        # ================= RPLIDAR =================
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='rplidar',
            parameters=[{
                'channel_type': 'serial',
                'serial_port': serial_port,
                'serial_baudrate': serial_baudrate,
                'frame_id': frame_id,
                'inverted': False,
                'angle_compensate': True,
                'scan_mode': 'Sensitivity'
            }],
            output='screen'
        ),

        # ================= Lidar Plot (RViz Marker) =================
        ExecuteProcess(
            cmd=['python3',
                '/home/pwwq/durian_project/dev_ws/install/robot_main/share/robot_main/lidar/plot.py'],
            output='screen'
        ),

    ])
