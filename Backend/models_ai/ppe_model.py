import os
import cv2
import torch
from ultralytics import YOLO

CLASS_NAMES = [
    "Hardhat",
    "Mask",
    "NO-Hardhat",
    "NO-Mask",
    "NO-Safety Vest",
    "Person",
    "Safety Cone",
    "Safety Vest",
    "machinery",
    "vehicle",
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MODEL_PATH = os.path.join(BASE_DIR, "Models", "PPE-Detection", "ppe.pt")
ONNX_PATH = os.path.join(BASE_DIR, "Models", "PPE-Detection", "ppe.onnx")
ENGINE_PATH = os.path.join(BASE_DIR, "Models", "PPE-Detection", "ppe.engine")

_ppe_model = None


def get_ppe_model():
    global _ppe_model
    if _ppe_model is None:
        target_path = None
        if os.path.exists(ENGINE_PATH) and torch.cuda.is_available():
            target_path = ENGINE_PATH
        elif os.path.exists(ONNX_PATH):
            target_path = ONNX_PATH
        elif os.path.exists(MODEL_PATH):
            target_path = MODEL_PATH

        if target_path:
            _ppe_model = YOLO(target_path)
    return _ppe_model


def unload_ppe_model() -> None:
    global _ppe_model
    _ppe_model = None


def _calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    unionArea = float(boxAArea + boxBArea - interArea)
    if unionArea <= 0:
        return 0.0
    return interArea / unionArea


def detect_ppe(img, conf_threshold=0.3, iou_threshold=0.2, device=None):
    model = get_ppe_model()
    if not model:
        return []

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    half_precision = True if device == "cuda" else False

    results = model(img, conf=conf_threshold, device=device, half=half_precision, verbose=False)
    persons = []
    gear_items = []
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

            if label in ["person", "worker"]:
                persons.append(
                    {
                        "box": box_coords,
                        "confidence": conf,
                        "has_helmet": False,
                        "has_vest": False,
                    }
                )
            else:
                gear_items.append(
                    {"box": box_coords, "label": label, "confidence": conf}
                )

    # IoU person-to-gear association
    for person in persons:
        p_box = person["box"]
        for gear in gear_items:
            g_box = gear["box"]
            iou = _calculate_iou(p_box, g_box)
            g_label = gear["label"]

            if iou > iou_threshold:
                if any(k in g_label for k in ["hardhat", "helmet"]):
                    if not any(k in g_label for k in ["no-", "no_"]):
                        person["has_helmet"] = True
                elif any(k in g_label for k in ["vest", "jacket"]):
                    if not any(k in g_label for k in ["no-", "no_"]):
                        person["has_vest"] = True

    detections = []
    for p in persons:
        is_compliant = p["has_helmet"] and p["has_vest"]
        verdict = (
            "COMPLIANT"
            if is_compliant
            else (
                "NO-HARDHAT & NO-VEST"
                if not p["has_helmet"] and not p["has_vest"]
                else ("NO-HARDHAT" if not p["has_helmet"] else "NO-SAFETY VEST")
            )
        )
        detections.append(
            {
                "box": p["box"],
                "confidence": p["confidence"],
                "class_id": 0,
                "label": f"Worker: {verdict}",
                "compliant": is_compliant,
            }
        )

    for g in gear_items:
        detections.append(
            {
                "box": g["box"],
                "confidence": g["confidence"],
                "class_id": 1,
                "label": g["label"],
                "compliant": not g["label"].startswith("no-"),
            }
        )

    return detections
