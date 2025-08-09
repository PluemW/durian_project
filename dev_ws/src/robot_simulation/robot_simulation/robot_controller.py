#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist

class CommandController(Node):
    def __init__(self):
        super().__init__('drive_controller')

        # Publishers for steering joints
        self.pub_1 = self.create_publisher(Float64, '/steering_1_joint/command', 10)
        self.pub_2 = self.create_publisher(Float64, '/steering_2_joint/command', 10)
        self.pub_3 = self.create_publisher(Float64, '/steering_3_joint/command', 10)
        self.pub_4 = self.create_publisher(Float64, '/steering_4_joint/command', 10)

        # Publishers for wheels (rear only in your setup)
        self.pub_rl = self.create_publisher(Float64, '/wheel_2_joint/command', 10)  
        self.pub_rr = self.create_publisher(Float64, '/wheel_4_joint/command', 10)  

        # Subscriptions
        self.sub_cmd = self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)

        # Timer loop
        self.timer = self.create_timer(0.1, self.timer_callback)

        self.direct = [0.0, 0.0]  # left-right
        self.speed = 0.0
        self.angular = 0.0

    def cmd_callback(self, msg: Twist):
        self.speed = msg.linear.x
        self.angular = msg.angular.z

    def turn(self):
        self.pub_1.publish(Float64(data=-5.0))
        self.pub_2.publish(Float64(data=5.0))
        self.pub_3.publish(Float64(data=5.0))
        self.pub_4.publish(Float64(data=-5.0))
        self.pub_rl.publish(Float64(data=-self.speed)) if self.angular > 0.0 else self.pub_rl.publish(Float64(data=self.speed))
        self.pub_rr.publish(Float64(data=self.speed)) if self.angular > 0.0 else self.pub_rl.publish(Float64(data=-self.speed))

    def go_straight(self):
        self.pub_1.publish(Float64(data=5.0))
        self.pub_2.publish(Float64(data=-5.0))
        self.pub_3.publish(Float64(data=-5.0))
        self.pub_4.publish(Float64(data=5.0))
        self.pub_rl.publish(Float64(data=self.speed))
        self.pub_rr.publish(Float64(data=self.speed))

    def timer_callback(self):
        if self.angular > 0.0:
            self.turn()
        else:
            self.go_straight()

def main(args=None):
    rclpy.init(args=args)
    node = CommandController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
