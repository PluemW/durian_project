#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math
import time

class ScanObjectDistance(Node):

    def __init__(self):
        super().__init__('scan_object_distance')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.object_threshold = 1.0   # meters
        self.print_interval = 0.1     # seconds
        self.last_print_time = time.time()

        self.get_logger().info('Scan object distance (1 degree) started')

    def scan_callback(self, msg: LaserScan):
        print("\n--- LiDAR Scan (1° resolution) ---")

        # Convert scan limits to degrees
        angle_min_deg = int(math.degrees(msg.angle_min))
        angle_max_deg = int(math.degrees(msg.angle_max))

        # Initialize bins for each degree
        degree_bins = {}
        for deg in range(angle_min_deg, angle_max_deg + 1):
            degree_bins[deg] = []

        # Fill bins
        angle = msg.angle_min
        for r in msg.ranges:
            if math.isinf(r) or math.isnan(r):
                angle += msg.angle_increment
                continue

            deg = int(round(math.degrees(angle)))

            if deg in degree_bins:
                degree_bins[deg].append(r)

            angle += msg.angle_increment

        # Print per degree
        for deg in sorted(degree_bins.keys()):
            if 0 < deg < 20:
                if len(degree_bins[deg]) == 0:
                    print(f"Angle: {deg:4d}° | Distance: inf")
                    continue

                dist = min(degree_bins[deg])

                if dist < self.object_threshold:
                    print(f"Angle: {deg:4d}° | Distance: {dist:5.2f} m | OBJECT")
                else:
                    print(f"Angle: {deg:4d}° | Distance: {dist:5.2f} m")

def main():
    rclpy.init()
    node = ScanObjectDistance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
