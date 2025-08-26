import os
import cv2
from ultralytics import YOLO
import torch

FIRE_CLASSES = ["fire", "smoke"]
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../Models/fire-and-smoke-detection-yolov8/weights/last.pt')
fire_model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def detect_fire_smoke(img, conf_threshold=0.25, device=None):
    if not fire_model:
        return []
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    results = fire_model(img, conf=conf_threshold, device=device)
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = FIRE_CLASSES[cls] if 0 <= cls < len(FIRE_CLASSES) else str(cls)
            if conf >= conf_threshold:
                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": conf,
                    "label": label
                })
    return detections
