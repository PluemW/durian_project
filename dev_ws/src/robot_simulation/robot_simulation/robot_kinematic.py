#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry

class Kinematic(Node):
    def __init__(self):
        super().__init__('kinematic_controller')

        # Publishers for steering joints
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriptions
        self.sub_imu = self.create_subscription(Imu, '/imu', self.imu_callback, 10)
        self.sub_target = self.create_subscription(PoseStamped, '/goal_pose', self.target_callback, 10)
        self.sub_odom = self.create_subscription(Odometry, '/robot/odom', self.odom_callback, 10)

        # Timer to control loop
        self.timer = self.create_timer(0.1, self.timer_callback)

        # State
        self.yaw = None
        self.target_pose = None
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = None

    def imu_callback(self, msg: Imu):
        q = msg.orientation
        self.yaw = self.quaternion_to_yaw(q.x, q.y, q.z, q.w)

    def odom_callback(self, msg: Odometry):
        pose = msg.pose.pose
        self.current_x = pose.position.x
        self.current_y = pose.position.y
        q = pose.orientation
        self.current_yaw = self.quaternion_to_yaw(q.x, q.y, q.z, q.w)

    def target_callback(self, msg: PoseStamped):
        self.target_pose = msg

    def quaternion_to_yaw(self, x, y, z, w):
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return yaw

    def timer_callback(self):
        yaw = self.current_yaw if self.current_yaw is not None else self.yaw
        if yaw is None or self.target_pose is None:
            self.get_logger().info('Waiting for yaw and target pose...')
            return
        target_x = self.target_pose.pose.position.x
        target_y = self.target_pose.pose.position.y

        desired_yaw = math.atan2(target_y - self.current_y, target_x - self.current_x)
        angle_diff = desired_yaw - yaw 
        cmd = Twist()
        
        if abs(angle_diff) > 0.08:
            cmd.linear.x = 3.0
            cmd.angular.z = 5.0 if angle_diff > 0 else -5.0
        else:
            cmd.linear.x = 5.0
            cmd.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = Kinematic()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
