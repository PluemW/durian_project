import math
import sys

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry

import numpy as np

import rclpy
from rclpy.node import Node

from tf2_ros import TransformBroadcaster

class OdomFramePublisher(Node):

    def __init__(self):
        super().__init__('odom_broadcaster')

        self.tf_broadcaster = TransformBroadcaster(self)

        self.odom_sub = self.create_subscription(Odometry, "/robot/odom", self.odom_cb, 10)

    def odom_cb(self, msg: Odometry):
        t = TransformStamped()

        t.header.stamp = msg.header.stamp
        t.header.frame_id = msg.header.frame_id
        t.child_frame_id = msg.child_frame_id

        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation.x = msg.pose.pose.orientation.x
        t.transform.rotation.y = msg.pose.pose.orientation.y
        t.transform.rotation.z = msg.pose.pose.orientation.z
        t.transform.rotation.w = msg.pose.pose.orientation.w

        self.tf_broadcaster.sendTransform(t)

def main():

    # pass parameters and initialize node
    rclpy.init()
    node = OdomFramePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()