#!/usr/bin/env python3
import cv2
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from ament_index_python.packages import get_package_share_directory
import os

package_path = get_package_share_directory('robot_main')
model_path = os.path.join(package_path, 'model', 'best.pt')

class DetectionDurian:
    def __init__(self):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(2)
        self.threshold = {"x1": 310, "y1": 290, "x2": 330, "y2": 310, "x_center": 320, "y_center": 300}

    def call_predict(self):
        ret, frame = self.cap.read()
        if not ret: return [], None
        results = self.model(frame)[0]
        class_names = self.model.names
        best_boxes = {}
        for box in results.boxes:
            conf = float(box.conf)
            cls_id = int(box.cls[0])
            xyxy = box.xyxy[0].tolist()
            if conf < 0.7: continue
            if cls_id not in best_boxes or conf > best_boxes[cls_id]["conf"]:
                best_boxes[cls_id] = {"xyxy": xyxy, "conf": conf}
        return [(class_names[cls_id], data["xyxy"]) for cls_id, data in best_boxes.items()], frame

    def get_durian_drop(self):
        labels, _ = self.call_predict()
        durian_point = next((p for cls, p in labels if cls == 'durian'), None)
        other_point = next((p for cls, p in labels if cls != 'durian'), None)
        if not durian_point or not other_point: return None
        r1, r2 = [(min(p[0], p[2]), min(p[1], p[3]), abs(p[2]-p[0]), abs(p[3]-p[1])) for p in [durian_point, other_point]]
        R1 = ((r1[0]+r1[2]/2,r1[1]+r1[3]/2),(r1[2],r1[3]),0)
        R2 = ((r2[0]+r2[2]/2,r2[1]+r2[3]/2),(r2[2],r2[3]),0)
        _, pts = cv2.rotatedRectangleIntersection(R1, R2)
        return durian_point if pts is not None and cv2.contourArea(pts)/min(r1[2]*r1[3], r2[2]*r2[3]) >= 0.7 else None
        # return durian_point
    
    def threshold_check(self, pixel_size):
        target_cy = 240 + int((pixel_size / 0.155) * 0.4)
        self.threshold["y1"] = target_cy - 10
        self.threshold["y2"] = target_cy + 10
        self.threshold["y_center"] = target_cy

    def get_detection_info(self):
        durian_point = self.get_durian_drop()
        if not durian_point: return 0, 0, 0  # no durian
        x1, y1, x2, y2 = map(int, durian_point)
        center_drop = ((x1+x2)//2, (y1+y2)//2)
        # self.threshold_check(y2 - y1)
        x_min, x_max = self.threshold["x1"], self.threshold["x2"]
        y_min, y_max = min(self.threshold["y1"], self.threshold["y2"]), max(self.threshold["y1"], self.threshold["y2"])
        if x_min <= center_drop[0] <= x_max and y_min <= center_drop[1] <= y_max:
            return 2, self.threshold["x_center"]-center_drop[0], self.threshold["y_center"]-center_drop[1]  # in drop zone
        return 1, self.threshold["x_center"]-center_drop[0], self.threshold["y_center"]-center_drop[1]  # not in drop zone

    def show_frame(self):
        labels, frame = self.call_predict()
        if frame is None: return
        for cls, xyxy in labels:
            x1, y1, x2, y2 = map(int, xyxy)
            color = (0, 0, 255) if cls == 'durian' else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.circle(frame, (int((x1+x2)/2), int((y1+y2)/2)), 5, (255,255,255), -1)
            cv2.rectangle(frame, (self.threshold["x1"], self.threshold["y1"]), (self.threshold["x2"], self.threshold["y2"]), (255,255,255), 2)
            cv2.putText(frame, cls, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.imshow("Detection", frame)
        cv2.waitKey(1)

class ros_node(Node):
    def __init__(self):
        super().__init__('detection_service_node')
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.srv = self.create_service(Trigger, 'detection_service', self.toggle_callback)
        self.publisher_ = self.create_publisher(Twist, 'detection_info', qos_profile)
        self.detection = DetectionDurian()
        self.active = False
        self.timer = self.create_timer(0.05, self.timer_callback)

    def toggle_callback(self, request, response):
        self.active = not self.active
        response.success = True
        response.message = "Detection active" if self.active else "Detection stopped"
        # self.get_logger().info(response.message)
        return response

    def timer_callback(self):
        msg = Twist()
        x, y, z = self.detection.get_detection_info()
        msg.linear.x = float(x)
        msg.linear.y = float(y)
        msg.linear.z = float(z)
        self.publisher_.publish(msg)
        self.detection.show_frame()

def main(args=None):
    rclpy.init(args=args)
    node = ros_node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.detection.cap.release()   
        cv2.destroyAllWindows()        
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
