#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class Motion_control():
    def __init__(self, drive_info: Twist, target_info: Twist):
        self.drive_info = drive_info
        self.target_info = target_info # [diff x, diff y]

    def motion(self):
        linear = 0.0
        angular = 0.0
        
        ##------------------- y command ----------------##
        if self.target_info[1] > 50:
            linear = 2
        elif self.target_info[1] < -50:
            linear = 1
        elif 50 > self.target_info[1] > 12:
            linear = -2
        elif -50 < self.target_info[1] < -12:
            linear = -1
        else:
            linear = 0
        ##----------------------------------------------##
        ##------------------- x command ----------------##
        if self.target_info[0] > 50:
            angular = 3
        elif self.target_info[0] < -50: 
            angular = 4
        elif 50 > self.target_info[0] > 25:
            angular = -3
        elif -50 < self.target_info[0] < -25:
            angular = -4
        else:
            angular = 0
        ##----------------------------------------------##
        return float(linear), float(angular)

class ros_node(Node):
    def __init__(self):
        super().__init__('motion_publisher')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10)
        self.detecion_subscription = self.create_subscription(
            Twist, 'control_drive_info', self.control_callback, qos)
        self.drive_subscription = self.create_subscription(
            Twist, 'drive_info', self.drive_callback, qos)
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.target_info = [0, 0, 0]
        self.drive_info = 0.0
        self.pre_count = 0
        self.count = 0
        self.set_grip = 0

    def control_callback(self, msg: Twist):
        self.target_info[0] = msg.linear.x # diff x
        self.target_info[1] = msg.linear.y # diff y
        self.count = msg.linear.z # sum durian

    def drive_callback(self, msg: Twist):
        self.set_grip = msg.linear.z

    def timer_callback(self):
        msg = Twist()
        if self.count > self.pre_count and self.set_grip == 0.0:
            msg.linear.z = 1.0
        elif self.set_grip == 1.0:
            msg.linear.z = 0.0
            self.pre_count = self.count
        drive_cmd = Motion_control(self.drive_info, self.target_info)
        msg.linear.x, msg.angular.x, = drive_cmd.motion()
        msg.angular.z = float(self.count)
        self.cmd_vel_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    motion_publisher = ros_node()
    rclpy.spin(motion_publisher)
    motion_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()