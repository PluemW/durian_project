#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import py_trees
from geometry_msgs.msg import Twist
from std_msgs.msg import Int8
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class SimpleStateBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.state = None  # "failure" | "running" | "success"

    def update(self):
        if self.state == "success":
            return py_trees.common.Status.SUCCESS
        elif self.state == "failure":
            return py_trees.common.Status.FAILURE
        else:
            return py_trees.common.Status.RUNNING

class SetupBehaviour(SimpleStateBehaviour):
    pass

class DetectBehaviour(SimpleStateBehaviour):
    pass

class DropBehaviour(SimpleStateBehaviour):
    pass

class MainControl(Node):
    def __init__(self):
        super().__init__('bt_control')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.setup_bt  = SetupBehaviour("SETUP")
        self.detect_bt = DetectBehaviour("DETECT")
        self.drop_bt   = DropBehaviour("DROP")
        self.catch_bt = py_trees.composites.Sequence("CATCH", memory=True)
        self.catch_bt.add_children([
            self.detect_bt,
            self.drop_bt
        ])
        root = py_trees.composites.Sequence("ROOT", memory=True)
        root.add_children([
            self.setup_bt,
            self.catch_bt
        ])
        self.tree = py_trees.trees.BehaviourTree(root)
        self.setup_sub = self.create_subscription(
            Twist, 'drive_info', self.setup_cb, qos
        )
        self.detect_sub = self.create_subscription(
            Twist, 'detection_info', self.detect_cb, qos
        )
        self.drop_sub = self.create_subscription(
            Int8, 'drop_state', self.drop_cb, qos
        )
        self.control_drive_pub = self.create_publisher(Twist, 'control_drive_info', qos)
        self.timer = self.create_timer(0.5, self.tick_tree)
        self.initial = [0.0, 0.0]
        self.pre_count_durian = 0
        self.count_durian = 0
        self.trig_drop = False

    def setup_cb(self, msg: Twist):
        start_switch = msg.angular.x
        lat = msg.angular.y
        log = msg.angular.z
        if start_switch == 0 and self.setup_bt.state == "failure":
            self.setup_bt.state = "failure"
        elif start_switch == 1 and (lat == 0 and log == 0) and self.setup_bt.state != "success":
            self.setup_bt.state = "running"
        elif start_switch == 1 and (lat != 0 or log != 0) and self.initial != [0.0, 0.0]:
            self.setup_bt.state = "success"
            if self.initial[0] == 0.0 and self.initial[1] == 0.0:
                self.initial[0] = lat
                self.initial[1] = log

    def detect_cb(self, msg: Twist):
        # if self.setup_bt.state == "success" and msg is not None:
        if msg is not None:
            control_drive = Twist()
            control_drive.linear.x = msg.linear.y  # diff x
            control_drive.linear.y = msg.linear.z  # diff y
            if msg.linear.x == 0:
                self.detect_bt.state = "failure"
                if self.pre_count_durian != msg.angular.x and self.trig_drop:
                    self.count_durian += 1
                    self.pre_count_durian = 0
                    self.trig_drop = False
            elif msg.linear.x == 1:
                self.detect_bt.state = "running"
                if self.pre_count_durian == 0:
                    self.pre_count_durian = msg.angular.x
            elif msg.linear.x == 2:
                self.detect_bt.state = "success"
                if not self.trig_drop:
                    self.trig_drop = True
            else:
                self.detect_bt.state = None
            control_drive.linear.z = float(self.count_durian)
            control_drive.angular.x = float(self.pre_count_durian)
            self.control_drive_pub.publish(control_drive)

    def drop_cb(self, msg: Int8):
        pass

    def tick_tree(self):
        self.get_logger().info(
            f"[BT] SETUP={self.setup_bt.state} | "
            f"[BT] DETECT={self.detect_bt.state} | "
            f"[BT] DROP={self.drop_bt.state}"
        )
        self.tree.tick()

def main(args=None):
    rclpy.init(args=args)
    node = MainControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
