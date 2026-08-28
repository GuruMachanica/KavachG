import os
from ultralytics import YOLO
import torch

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MODEL_PATH = os.path.join(BASE_DIR, "Models", "Fire_Smoke", "last.pt")
ONNX_PATH = os.path.join(BASE_DIR, "Models", "Fire_Smoke", "last.onnx")
ENGINE_PATH = os.path.join(BASE_DIR, "Models", "Fire_Smoke", "last.engine")

_fire_model = None


def get_fire_model():
    global _fire_model
    if _fire_model is None:
        target_path = None
        if os.path.exists(ENGINE_PATH) and torch.cuda.is_available():
            target_path = ENGINE_PATH
        elif os.path.exists(ONNX_PATH):
            target_path = ONNX_PATH
        elif os.path.exists(MODEL_PATH):
            target_path = MODEL_PATH

        if target_path:
            _fire_model = YOLO(target_path)
    return _fire_model


def unload_fire_model() -> None:
    global _fire_model
    _fire_model = None


def detect_fire_smoke(img, conf_threshold=0.15, device=None):
    model = get_fire_model()
    if not model:
        return []

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    half_precision = True if device == "cuda" else False

    results = model(img, conf=conf_threshold, device=device, half=half_precision, verbose=False)
    detections = []
    model_names = getattr(model, "names", {})

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            raw_label = model_names.get(cls, str(cls))
            label = str(raw_label).strip().lower()

            box_coords = [int(x1), int(y1), int(x2), int(y2)]
            detections.append(
                {
                    "box": box_coords,
                    "confidence": conf,
                    "class_id": cls,
                    "label": f"HAZARD: {label.upper()}",
                }
            )

    return detections
