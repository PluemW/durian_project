#!/usr/bin/env python3
from textwrap import wrap

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import math

# PathTracker Class เหมือนเดิม (ข้ามไปส่วน Localization เลยนะครับ)
class PathTracker:
    def __init__(self):
        self.current_x = 0.0
        self.current_y = 0.0
        self.last_tick_l = 0.0
        self.last_tick_r = 0.0
        self.is_initialized = False
        
    def update(self, tick_l, tick_r, yaw_deg):
        if not self.is_initialized:
            self.last_tick_l = tick_l
            self.last_tick_r = tick_r
            self.is_initialized = True
            return
        delta_l = tick_l - self.last_tick_l
        delta_r = tick_r - self.last_tick_r
        avg_delta_tick = (delta_l + delta_r) / 2.0
        rad = math.radians(yaw_deg)
        self.current_x += avg_delta_tick * math.cos(rad)
        self.current_y += avg_delta_tick * math.sin(rad)
        self.last_tick_l = tick_l
        self.last_tick_r = tick_r

    def get_home_vector(self):
        distance_ticks = math.sqrt(self.current_x**2 + self.current_y**2)
        angle_deg = math.degrees(math.atan2(-self.current_y, -self.current_x))
        return distance_ticks, angle_deg

    def reset(self):
        self.current_x = 0.0
        self.current_y = 0.0
        self.is_initialized = False

class Localization(Node):
    def __init__(self):
        super().__init__('localize_node')
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST, depth=10)
        
        self.tracker = PathTracker()
        self.state = 0
        self.yaw_now = 0.0
        
        # ตัวแปรควบคุมการเดินกลับ
        self.target_dist = 0.0
        self.target_angle = 0.0
        self.bring_initial = False
        self.rotate_done = False
        self.pre_back_home_tick = 0.0
        self.current_back_home_tick = 0.0

        self.drive_sub = self.create_subscription(Twist, 'drive_info', self.drive_callback, qos)
        self.pos_sub = self.create_subscription(Twist, 'control_drive_info', self.local_position_callback, qos)
        self.localize_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def drive_callback(self, msg: Twist):
        self.yaw_now = msg.angular.x
        self.tracker.update(msg.angular.y, msg.angular.z, self.yaw_now)
        self.current_back_home_tick = (msg.angular.y + msg.angular.z) / 2.0

    def local_position_callback(self, msg: Twist):
        self.state = int(msg.angular.z)
        if self.state == 0:
            self.tracker.reset()
            self.bring_initial = False
            self.rotate_done = False
    
    def wrap_angle(self, angle):
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    def timer_callback(self):
        cmd = Twist()
        if self.state == 4 and not self.bring_initial:
            self.target_dist, self.target_angle = self.tracker.get_home_vector()
            self.bring_initial = True
            self.get_logger().info(f'Home Target Locked: Dist {self.target_dist:.2f}, Angle {self.target_angle:.2f}')
        if self.bring_initial:
            if not self.rotate_done:
                angle_error = self.target_angle - self.wrap_angle(self.yaw_now)
                self.get_logger().info(f'Rotating: Target {self.target_angle:.2f}, Yaw {self.yaw_now:.2f}, Error {angle_error:.2f}')
                if abs(angle_error) > 5.0:  # มุมยังไม่ตรง (Tolerance 5 องศา)
                    cmd.angular.x = 3.0 if angle_error < 0 else 4.0
                else:
                    cmd.angular.x = 0.0
                    self.rotate_done = True
                    self.pre_back_home_tick = self.current_back_home_tick # บันทึก Tick เริ่มต้นตอนที่ตัวตรงแล้ว
                    self.get_logger().info('Rotation Done, Starting to walk...')
            else:
                distance_walked = abs(self.current_back_home_tick - self.pre_back_home_tick)
                # if abs(angle_error) > 5.0:  # มุมยังไม่ตรง (Tolerance 5 องศา)
                #     cmd.angular.x = 3.0 if angle_error < 0 else 4.0
                # else:
                #     cmd.angular.x = 0.0
                if distance_walked < self.target_dist:
                    cmd.linear.x = 1.0 # สั่งเดินหน้า
                else:
                    cmd.linear.x = 0.0 # ถึงจุดหมาย
                    self.get_logger().info('Reached Home!')
        self.localize_pub.publish(cmd)

def main():
    rclpy.init()
    node = Localization()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()