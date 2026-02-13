import cv2
from ultralytics import YOLO
import numpy as np

model = YOLO("dev_ws/src/robot_main/model/best_ncnn_model")
cap = cv2.VideoCapture(2)

# =====================================
# 📏 Dynamic pixel ↔ distance function
# =====================================
def calc_scale_from_pixel(pixel_size):
    """
    คำนวณค่าระยะ (m) และ scale (pixels per meter)
    จากขนาดพิกเซลของวัตถุที่ตรวจจับได้
    โดยอ้างอิงจากข้อมูล:
        70 px -> 3 m
        20 px -> 6 m
        ขนาดจริงวัตถุ = 0.155 m
    """
    size_real = 0.155  # m

    # Linear relation: distance = a * pixel + b
    a = (3 - 6) / (70 - 20)  # -0.06
    b = 3 - a * 70           # 7.2

    distance = a * pixel_size + b
    ppm = pixel_size / size_real
    return ppm, distance


# =====================================
# 🧭 Target config
# =====================================
target_box_size = 15
center_x_image, center_y_image = 320, 240
target_cx, target_cy = center_x_image, center_y_image
target_drop_m = 0.40  # 30 cm ต่ำจากศูนย์กลาง

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    results = model(frame, verbose=False)

    found_ref = False
    distance_est = None
    scale_now = None

    # =====================================
    # 🔍 เลือกกล่องคลาส 0 ที่มีความมั่นใจมากที่สุด
    # =====================================
    best_box = None
    best_conf = 0.0

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if cls_id == 0 and conf > best_conf:
                best_conf = conf
                best_box = box

    # =====================================
    # ✅ ถ้ามีกล่องที่ดีที่สุดของคลาส 0
    # =====================================
    if best_box is not None:
        found_ref = True
        x1, y1, x2, y2 = map(int, best_box.xyxy[0])
        h = y2 - y1
        h = np.clip(h, 10, 200)  # ป้องกัน noise จาก detection

        # คำนวณระยะและสเกล
        scale_now, distance_est = calc_scale_from_pixel(h)
        offset_y_px = int(scale_now * target_drop_m)

        target_cx = center_x_image
        target_cy = center_y_image + offset_y_px

        # วาดจุดตำแหน่งของกล่องที่เลือก
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(frame, (cx, cy), 7, (0, 255, 0), -1)

        # cv2.putText(frame,
        #             f"conf={best_conf:.2f} | d={distance_est:.2f}m | scale={scale_now:.1f}px/m",
        #             (x1, y2 + 20),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5,
        #             (0, 255, 255), 2)

    # =====================================
    # วาดกล่องเป้าหมาย
    # =====================================
    half = target_box_size // 2
    cv2.rectangle(frame,
                  (target_cx - half, target_cy - half),
                  (target_cx + half, target_cy + half),
                  (0, 0, 255), 2)

    cv2.line(frame, (0, center_y_image), (640, center_y_image), (200, 200, 200), 1)
    cv2.circle(frame, (center_x_image, center_y_image), 3, (200, 200, 200), -1)

    status = "Ref Found" if found_ref else "Hold Last"
    text = f"{status} | Target Y={target_cy}"
    if distance_est:
        text += f" | {distance_est:.2f} m"
    cv2.putText(frame, text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0) if found_ref else (0, 255, 255), 2)

    cv2.imshow("Dynamic Distance Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
