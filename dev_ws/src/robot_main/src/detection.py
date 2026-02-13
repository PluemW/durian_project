#!/usr/bin/env python3
import cv2
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from ament_index_python.packages import get_package_share_directory
import os
import threading
import time

hight = 0
package_path = get_package_share_directory('robot_main')
model_path = os.path.join(package_path, 'model', 'hd3_ncnn_model')

class CameraThread(threading.Thread):
    def __init__(self, cam_id=2):
        super().__init__(daemon=True)
        self.cap = cv2.VideoCapture(cam_id)
        self.running = True
        self.frame = None
        self.lock = threading.Lock()

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret: time.sleep(0.01); continue
            h, w = frame.shape[:2]
            min_dim = min(h, w)
            start_x = w // 2 - min_dim // 2
            start_y = h // 2 - min_dim // 2
            center_crop = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]
            frame_resized = cv2.resize(center_crop, (320, 320))
            with self.lock: self.frame = frame_resized

    def get_frame(self):
        with self.lock: return None if self.frame is None else self.frame.copy()

    def stop(self): self.running = False; self.cap.release()

class YOLOThread(threading.Thread):
    def __init__(self, model_path, cam_thread):
        super().__init__(daemon=True)
        self.model = YOLO(model_path)
        self.cam_thread = cam_thread
        self.running = True
        self.result = None
        self.frame = None
        self.lock = threading.Lock()

    def run(self):
        while self.running:
            frame = self.cam_thread.get_frame()
            if frame is None: time.sleep(0.01); continue
            result = self.model(frame, verbose=False)[0]
            with self.lock: self.result = result; self.frame = frame; time.sleep(0.005)

    def get_result(self):
        with self.lock: return self.result, self.frame

    def stop(self): self.running = False

class DetectionDurian:
    def __init__(self, yolo_thread):
        self.yolo_thread = yolo_thread
        self.x_min = self.y_min = self.x_max = self.y_max = 0

    def call_predict(self):
        result, frame = self.yolo_thread.get_result()
        if result is None or frame is None: return [], None
        best_human = None
        best_human_conf = 0.0
        durian_boxes = []
        for box in result.boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            xyxy = box.xyxy[0].tolist()
            if cls_id == 1 and conf > best_human_conf: best_human_conf = conf; best_human = xyxy; continue
            if cls_id == 0 and conf > 0.7: durian_boxes.append(xyxy)
        labels = []
        if best_human is not None: labels.append(("human", best_human))
        for durian in durian_boxes: labels.append(("durian", durian))
        return labels, frame

    def count_durians(self):
        labels, _ = self.call_predict()
        return sum(1 for cls, _ in labels if cls == 'durian')

    def get_durian_drop(self):
        labels, _ = self.call_predict()
        durians = [p for cls, p in labels if cls == 'durian']
        other = next((p for cls, p in labels if cls != 'durian'), None)
        if not durians or not other: return None
        def rect(p): return ((min(p[0], p[2]) + abs(p[2]-p[0])/2,
                    min(p[1], p[3]) + abs(p[3]-p[1])/2),
                    (abs(p[2]-p[0]), abs(p[3]-p[1])), 0)
        best_point, best_ratio = None, 0.0
        R_other = rect(other)
        for d in durians:
            _, pts = cv2.rotatedRectangleIntersection(rect(d), R_other)
            if pts is None: continue
            ratio = cv2.contourArea(pts) / min(
                abs(d[2]-d[0]) * abs(d[3]-d[1]),
                abs(other[2]-other[0]) * abs(other[3]-other[1])
            )
            if ratio > best_ratio: best_ratio, best_point = ratio, d
        return best_point if best_ratio >= 0.7 else None
    
    def calc_scale_from_pixel(self, pixel_size):
        size_real = 0.155  # m
        a = (3 - 6) / (45 - 10)   # -0.06
        b = 3 - a * 45            # 7.2
        return pixel_size / size_real, a * pixel_size + b

    def get_detection_info(self):
        durian_point = self.get_durian_drop()
        if not durian_point: return 0, 0, 0, 0
        x1, y1, x2, y2 = map(int, durian_point)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        h = y2 - y1
        ppm, _ = self.calc_scale_from_pixel(h)
        offset_y_px = int(ppm * 0.7)
        self.x_min, self.x_max = (320 // 2) - 7, (320 // 2) + 7
        self.y_min, self.y_max = ((320 // 2) + offset_y_px) - 7, ((320 // 2) + offset_y_px) + 7
        dx = ((320 // 2) - cx) 
        dy = (((320 // 2) + offset_y_px) - cy) 
        if self.x_min <= cx <= self.x_max and self.y_min <= cy <= self.y_max:
            return 2, dx, dy, h   # อยู่ในตำแหน่ง drop
        return 1, dx, dy, h       # ยังต้องปรับตำแหน่ง

    def show_frame(self):
        labels, frame = self.call_predict()
        if frame is None: return
        for cls, xyxy in labels:
            x1, y1, x2, y2 = map(int, xyxy)
            color = (0, 0, 255) if cls == 'durian' else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.circle(frame, ((x1+x2)//2, (y1+y2)//2), 5, (255, 255, 255), -1)
            cv2.rectangle(frame,
                            (self.x_min, self.y_min),
                            (self.x_max, self.y_max),
                            (255, 255, 255), 2
                        )
            cv2.putText(frame, cls, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.imshow("Detection", frame)
        cv2.waitKey(1)

class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.publisher_ = self.create_publisher(Twist, 'detection_info', qos_profile)
        self.cam_thread = CameraThread(2)
        self.yolo_thread = YOLOThread(model_path, self.cam_thread)
        self.cam_thread.start()
        self.yolo_thread.start()
        self.detection = DetectionDurian(self.yolo_thread)
        self.timer = self.create_timer(0.05, self.timer_callback)

    def timer_callback(self):
        x, y, z, hight = self.detection.get_detection_info()
        total_durians = self.detection.count_durians()
        # self.get_logger().info(f"Detection Info: x={x}, y={y}, z={z} Total Durians: {total_durians}")
        msg = Twist()
        if x or y or z or total_durians is not None:
            msg.linear.x = float(x) # state
            msg.linear.y = float(y) # diff x
            msg.linear.z = float(z) # diff y
            msg.angular.x = float(total_durians) # sum durian
            msg.angular.z = float(hight)  # hight
        self.publisher_.publish(msg)
        self.detection.show_frame()

def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cam_thread.stop()
        node.yolo_thread.stop()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()