import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory

package_name = 'robot_main'

def generate_launch_description():
    package_share = FindPackageShare(package_name).find(package_name)
    executable_paths = {
        "state_control": os.path.join(package_share, "src", "state_control.py"),
        "detection": os.path.join(package_share, "src", "detection.py"),
        "motion_control": os.path.join(package_share, "src", "motion_control.py"),
    }

    return LaunchDescription([
        ExecuteProcess(
            cmd=['python3', executable_paths["state_control"]],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['python3', executable_paths["detection"]],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['python3', executable_paths["motion_control"]],
            output='screen'
        ),
        Node(
            package="micro_ros_agent",
            executable="micro_ros_agent",
            output="screen",
            arguments=["serial", "--dev", "/dev/ttyUSB0"],
        ),
    ])
