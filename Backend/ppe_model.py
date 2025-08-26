import os
import cv2
from ultralytics import YOLO

CLASS_NAMES = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle']
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../Models/PPE-Detection/ppe.pt')
ppe_model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def detect_ppe(img):
    if not ppe_model:
        return []
    results = ppe_model(img)
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = CLASS_NAMES[cls] if cls < len(CLASS_NAMES) else str(cls)
            detections.append({
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "confidence": conf,
                "label": label
            })
    return detections
