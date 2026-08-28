import os
from ultralytics import YOLO
import torch


def _find_model_path():
    search_paths = [
        os.path.join(os.path.dirname(__file__), "../Models/Fire_Smoke/last.pt"),
        os.path.join(os.path.dirname(__file__), "../../Models/Fire_Smoke/last.pt"),
        os.path.join(os.getcwd(), "Models/Fire_Smoke/last.pt"),
        os.path.join(os.getcwd(), "../Models/Fire_Smoke/last.pt"),
        "/app/Models/Fire_Smoke/last.pt",
    ]
    for p in search_paths:
        if os.path.exists(p):
            return p
    return search_paths[0]


MODEL_PATH = _find_model_path()
_fire_model = None


def get_fire_model():
    global _fire_model
    if _fire_model is None:
        target_path = _find_model_path()
        if os.path.exists(target_path):
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
    try:
        results = model(img, conf=conf_threshold, device=device, verbose=False)
    except Exception as e:
        print(f"[FIRE_MODEL] Inference error: {e}")
        return []

    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            name = model.names.get(cls_id, str(cls_id))
            detections.append(
                {
                    "class": name,
                    "confidence": conf,
                    "bbox": [int(x) for x in xyxy],
                }
            )
    return detections
