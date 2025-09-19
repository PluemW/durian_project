#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from std_msgs.msg import Int8MultiArray
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class Calibration():
    def __init__(self, drive_info: Int8MultiArray, target_info: Int8MultiArray):
        self.drive_info = drive_info # [orientation, direction]
        self.target_info = target_info # [state, x_offset, y_offset]
    
    def orientation_calibration(self):
        pass

    def direct_calibration(self):
        pass

class ros_node(Node):
    def __init__(self):
        super().__init__('calibration_publisher')
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10)
        self.detecion_subscription = self.create_subscription(
            Int8MultiArray, 'detection_info', self.detecion_callback, qos_profile)
        self.drive_subscription = self.create_subscription(
            Int8MultiArray, 'drive_info', self.drive_callback, qos_profile)
        self.cmd_calibrate_publisher = self.create_publisher(Twist, 'cmd_calibrate', qos_profile)
        self.timer = self.create_timer(0.5, self.timer_callback)

    def detecion_callback(self, msg: Int8MultiArray):
        self.target_info = msg.data # [state, x_offset, y_offset]

    def drive_callback(self, msg: Int8MultiArray):
        self.drive_info = msg.data # [orientation, direction]

    def timer_callback(self):
        pass

def main(args=None):
    rclpy.init(args=args)
    calibration_publisher = ros_node()
    rclpy.spin(calibration_publisher)
    calibration_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()