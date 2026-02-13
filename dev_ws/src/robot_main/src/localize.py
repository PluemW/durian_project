#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class Localizeation(Node):
    def __init__(self):
        super().__init__('localize_node')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos
        )
        self.drive_subscription = self.create_subscription(
            Twist, 'drive_info', self.drive_callback, qos
        )
        self.localize_info = self.create_publisher(Twist, 'localize_info', qos)
        self.timer = self.create_timer(0.5, self.timer_callback)

    def scan_callback(self, msg: LaserScan):
        pass

    def drive_callback(self, msg: Twist):
        pass

    def timer_callback(self):
        msg = Twist()
        self.localize_info.publish(msg)

def main():
    rclpy.init()
    node = Localizeation()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()