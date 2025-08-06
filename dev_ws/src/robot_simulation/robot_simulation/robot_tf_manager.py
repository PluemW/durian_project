import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan, NavSatFix
from geometry_msgs.msg import PointStamped, TransformStamped
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3, PoseStamped
from rclpy.qos import qos_profile_system_default, qos_profile_sensor_data

from tf_transformations import euler_from_quaternion
from functools import partial

from tf2_ros import TransformBroadcaster
import math

class TransformPublisher(Node):
    def __init__(self):
        super().__init__('tf_publisher')
        self.get_logger().info('Simulated sensor coverter node has started')
        self.robot_name = 'robot'

        self.odom = Odometry()

        self.odom_sub_ = self.create_subscription(Odometry, "/robot/odom", self.odometry_callback, qos_profile_system_default)

        self.odom_tf = TransformStamped()
        self.tf_pub_ = TransformBroadcaster(self)

        self.timer_ = self.create_timer(0.1, self.tf_publisher)
            
    def odometry_callback(self, msg):
        self.odom = msg

    def tf_publisher(self):
        if self.odom == None:
            self.get_logger().warn('No odometry or navsat data received yet')
            return
        self.get_logger().info('Publishing tf')
        time_now = self.get_clock().now()
        
        self.odom_tf.header.stamp = time_now.to_msg()
        self.odom_tf.header.frame_id = 'odom'
        self.odom_tf.child_frame_id = 'base_link'

        self.odom_tf.transform.translation.x = self.odom.pose.pose.position.x 
        self.odom_tf.transform.translation.y = self.odom.pose.pose.position.y 
        self.odom_tf.transform.translation.z = self.odom.pose.pose.position.z
        self.odom_tf.transform.rotation.x = self.odom.pose.pose.orientation.x
        self.odom_tf.transform.rotation.y = self.odom.pose.pose.orientation.y
        self.odom_tf.transform.rotation.z = self.odom.pose.pose.orientation.z
        self.odom_tf.transform.rotation.w = self.odom.pose.pose.orientation.w

        self.tf_pub_.sendTransform(self.odom_tf)

def main(args=None):
    rclpy.init(args=args)
    tf_publisher_node = TransformPublisher()
    rclpy.spin(tf_publisher_node)
    tf_publisher_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()