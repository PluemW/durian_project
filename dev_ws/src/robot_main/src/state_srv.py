#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import py_trees
from std_msgs.msg import Int16MultiArray
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_srvs.srv import Trigger

class ServiceClient(Node):
    def __init__(self, parent_node: Node):
        super().__init__('bt_service_client')
        self.parent_node = parent_node
        self.service_clients = {
            "detect": self.create_client(Trigger, 'detection_service'),
        }
        for name, client in self.service_clients.items():
            while not client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f'waiting for {name}_service...')

    def call_service(self, name: str):
        if name not in self.service_clients:
            self.get_logger().error(f"Service {name} not found")
            return
        request = Trigger.Request()
        client = self.service_clients[name]
        future = client.call_async(request)
        future.add_done_callback(lambda f: self.callback(f, name))

    def callback(self, future, name):
        try:
            resp = future.result()
            self.get_logger().info(
                f"[ServiceClient] {name} success={resp.success}, msg='{resp.message}'"
            )
        except Exception as e:
            self.get_logger().error(f"[ServiceClient] {name} failed: {e}")

class ServiceBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, name, node: Node, service_client: ServiceClient = None, service_name: str = None):
        super().__init__(name)
        self.node = node
        self.state = None  # "success", "failure", หรือ None
        self.service_client = service_client
        self.service_name = service_name
        self.service_called = False
        self.service_on = False

    def initialise(self):
        self.service_called = False

    def update(self):
        if self.service_client and self.service_name and not self.service_called:
            # self.node.get_logger().info(f"[BT] call service (start): {self.service_name}")
            self.service_client.call_service(self.service_name)
            self.service_called = True
        if self.state == "success":
            if not self.service_on:
                # self.node.get_logger().info(f"[BT] {self.service_name} SUCCESS → mark service_on")
                self.service_on = True
            return py_trees.common.Status.SUCCESS
        elif self.state == "running":
            return py_trees.common.Status.RUNNING
        else:  # failure
            return py_trees.common.Status.FAILURE

    def terminate(self, new_status):
        if self.state != "success":
            return
        if self.service_on and new_status == py_trees.common.Status.SUCCESS:
            self.node.get_logger().info(f"[BT] terminate → shutdown {self.service_name}")
            self.service_client.call_service(self.service_name)
            self.service_on = False
        super().terminate(new_status)

class MainControl(Node):
    def __init__(self):
        super().__init__('bt_control')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.sub_detection = self.create_subscription(
            Twist, 'detection_info', self.detection_cb, qos)
        self.service_client = ServiceClient(self)
        self.behaviour_tree = self.build_tree()
        self.timer = self.create_timer(0.5, self.tick_tree)

    def build_tree(self):
        root = py_trees.composites.Sequence("Main", memory=True)
        self.detect_bt = ServiceBehaviour("Detect", self, self.service_client, "detect")
        sequence = py_trees.composites.Sequence("SequenceAll", memory=True)
        sequence.add_children([self.detect_bt])
        root.add_child(sequence)
        return py_trees.trees.BehaviourTree(root)

    def detection_cb(self, msg: Twist):
        if msg.linear.x and msg.linear.x == 0: self.detect_bt.state = "failure"
        # elif msg.data and msg.data[0] == 1: self.detect_bt.state = "running"
        elif msg.linear.x and msg.linear.x == 2: self.detect_bt.state = "success"
        else: self.detect_bt.state = None

    def tick_tree(self):
        self.get_logger().info(f"Detect status: {self.detect_bt.status}")
        self.behaviour_tree.tick()

def main(args=None):
    rclpy.init(args=args)
    node = MainControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
