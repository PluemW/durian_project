#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import math

class Measurement:
    def __init__(self, drive_info, local_position):
        R = 6371000.0  # Earth radius (m)
        lat1 = math.radians(local_position[0])
        lon1 = math.radians(local_position[1])
        lat2 = math.radians(drive_info[0])
        lon2 = math.radians(drive_info[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + \
            math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        self.r = R * c   # meter
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - \
            math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        theta = math.atan2(y, x)
        theta = math.degrees(theta)
        self.theta = (theta + 360) % 360

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
        self.local_position_subscription = self.create_subscription(
            Twist, 'local_position_info', self.local_position_callback, qos
        )
        self.localize_info = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.setup = False
        self.intial = [0, 0] # lat, long
        self.current_position = [0, 0] # lat, long
        self.yaw_delta = 0.0
        self.initial_scan_points = []   # [(angle_deg, distance)]
        self.scan_saved = False

    def extract_scan_points(self, scan_msg: LaserScan, min_dist=0.5):
        points = []
        angle = scan_msg.angle_min
        for r in scan_msg.ranges:
            # skip invalid values
            if math.isinf(r) or math.isnan(r):
                angle += scan_msg.angle_increment
                continue
            # threshold distance
            if r < min_dist:
                angle += scan_msg.angle_increment
                continue
            angle_deg = math.degrees(angle)
            points.append((angle_deg, r))
            angle += scan_msg.angle_increment
        return points

    def angle_error(self, target, current):
        err = target - current
        if err > 180: err -= 360
        if err < -180: err += 360
        return err

    def scan_callback(self, msg: LaserScan):
        if self.setup and not self.scan_saved:
            self.initial_scan_points = self.extract_scan_points(
                msg,
                min_dist=0.5
            )
            self.scan_saved = True

    def drive_callback(self, msg: Twist):
        self.yaw_delta = msg.angular.x
        self.current_position[0] = msg.angular.y
        self.current_position[1] = msg.angular.z

    def local_position_callback(self, msg: Twist):
        self.intial[0] = msg.linear.x
        self.intial[1] = msg.linear.y
        if msg.angular.z == 1.0 and not self.setup:
            self.setup = True

    def timer_callback(self):
        measurement = Measurement(self.current_position, self.intial)
        msg = Twist()
        heading_err = self.angle_error(measurement.angle, self.yaw_delta)
        msg.linear.x = measurement.r
        msg.linear.y = measurement.theta
        self.get_logger().info(
            f"Distance: {measurement.r:.2f} m, Angle: {measurement.theta:.2f}°, hading error: {heading_err:.2f}°"
        )
        self.localize_info.publish(msg)

def main():
    rclpy.init()
    node = Localizeation()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()