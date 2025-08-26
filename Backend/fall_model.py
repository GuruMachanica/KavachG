import os
import cv2
from ultralytics import YOLO

# Load the pose model for fall detection
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../Models/fall_detection_yolov8s/yolov8s-pose.pt')
fall_model = YOLO(MODEL_PATH, task="pose") if os.path.exists(MODEL_PATH) else None

def detect_fall(img):
    if not fall_model:
        return []
    results = fall_model(img, imgsz=640, device="cuda" if cv2.cuda.getCudaEnabledDeviceCount() > 0 else "cpu")
    detections = []
    frame_fall = False
    for result in results:
        try:
            boxes = result.boxes
            kpts = result.keypoints
            for idx, box in enumerate(boxes):
                x = boxes.xywh[idx][0]
                y = boxes.xywh[idx][1]
                w = boxes.xywh[idx][2]
                h = boxes.xywh[idx][3]
                fall_detected = w/h > 1.4
                label = "Fallen" if fall_detected else "Stable"
                if fall_detected:
                    frame_fall = True
                # Draw keypoints on the image (optional, for visualization)
                if kpts is not None:
                    nk = kpts.shape[1]
                    for i in range(nk):
                        keypoint = kpts.xy[idx, i]
                        xk, yk = int(keypoint[0].item()), int(keypoint[1].item())
                        cv2.circle(img, (xk, yk), 5, (0, 255, 0), -1)
                # Optionally draw label
                cv2.putText(img, label, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                detections.append({
                    "bbox": [int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])],
                    "confidence": float(box.conf[0]),
                    "label": label
                })
        except Exception:
            continue
    return detections
