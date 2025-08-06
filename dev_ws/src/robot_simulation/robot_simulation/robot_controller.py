#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class CmdVelToJointController(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_joint_controller')

        # สร้าง Publisher สำหรับล้อทั้ง 4
        self.pub_fl = self.create_publisher(Float64, '/wheel_1_joint/command', 10)  # front-left
        self.pub_fr = self.create_publisher(Float64, '/wheel_2_joint/command', 10)  # front-right
        self.pub_rl = self.create_publisher(Float64, '/wheel_3_joint/command', 10)  # rear-left
        self.pub_rr = self.create_publisher(Float64, '/wheel_4_joint/command', 10)  # rear-right

        # Subscribe /cmd_vel
        self.sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        # พารามิเตอร์ของรถ
        self.wheel_base = 0.5  # ระยะระหว่างล้อซ้าย-ขวา (เมตร)
        self.wheel_radius = 0.1  # รัศมีล้อ (เมตร)

    def cmd_vel_callback(self, msg: Twist):
        linear = msg.linear.x
        angular = msg.angular.z

        # คำนวณความเร็วแต่ละล้อ (unit: m/s)
        left_speed = linear - angular * self.wheel_base / 2.0
        right_speed = linear + angular * self.wheel_base / 2.0

        # แปลงเป็น angular velocity ของล้อ (rad/s)
        left_wheel_vel = left_speed / self.wheel_radius
        right_wheel_vel = right_speed / self.wheel_radius

        # Publish ไปยังล้อ
        self.pub_fl.publish(Float64(data=left_wheel_vel))   # wheel_1_joint
        self.pub_rl.publish(Float64(data=left_wheel_vel))   # wheel_3_joint
        self.pub_fr.publish(Float64(data=right_wheel_vel))  # wheel_2_joint
        self.pub_rr.publish(Float64(data=right_wheel_vel))  # wheel_4_joint

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelToJointController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
