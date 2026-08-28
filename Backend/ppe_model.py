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
def _find_ppe_model_path():
    search_dirs = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Models")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "Models")),
        os.path.abspath(os.path.join(os.getcwd(), "Models")),
        os.path.abspath(os.path.join(os.getcwd(), "..", "Models")),
        "/app/Models",
    ]
    for d in search_dirs:
        p = os.path.join(d, "PPE-Detection", "ppe.pt")
        if os.path.exists(p):
            return p
    return os.path.join(search_dirs[0], "PPE-Detection", "ppe.pt")


MODEL_PATH = _find_ppe_model_path()
_ppe_model = None


def get_ppe_model():
    global _ppe_model
    if _ppe_model is None:
        target = _find_ppe_model_path()
        if os.path.exists(target):
            try:
                _ppe_model = YOLO(target)
            except Exception as e:
                print(f"[PPE_MODEL] Error loading model: {e}")
                return None
    return _ppe_model



def unload_ppe_model() -> None:
    global _ppe_model
    _ppe_model = None


def _calculate_iou(boxA, boxB):
    # Determine intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    if boxAArea + boxBArea - interArea == 0:
        return 0.0
    return interArea / float(boxAArea + boxBArea - interArea)


def _is_inside_or_overlapping(gear_box, person_box, min_overlap=0.3):
    """Checks if gear box is primarily contained within person bounding box."""
    gx1, gy1, gx2, gy2 = gear_box
    px1, py1, px2, py2 = person_box

    # Calculate gear area
    g_area = max(1, (gx2 - gx1) * (gy2 - gy1))
    
    # Intersection area
    ix1 = max(gx1, px1)
    iy1 = max(gy1, py1)
    ix2 = min(gx2, px2)
    iy2 = min(gy2, py2)
    
    inter_w = max(0, ix2 - ix1)
    inter_h = max(0, iy2 - iy1)
    inter_area = inter_w * inter_h

    return (inter_area / float(g_area)) >= min_overlap


def detect_ppe(img, conf_threshold=0.25):
    model = get_ppe_model()
    if not model:
        return []

    device = "cuda" if torch.cuda.is_available() else "cpu"
    results = model(img, conf=conf_threshold, device=device, verbose=False)
    detections = []
    
    person_boxes = []
    gear_items = []

    model_names = getattr(model, "names", CLASS_NAMES)

    for r in results:
        boxes = getattr(r, "boxes", None)
        if boxes is None:
            continue
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            if isinstance(model_names, dict):
                raw_label = model_names.get(cls, str(cls))
            elif isinstance(model_names, list) and cls < len(model_names):
                raw_label = model_names[cls]
            else:
                raw_label = str(cls)

            item = {
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "confidence": round(conf, 2),
                "label": raw_label,
            }

            if raw_label.lower() == "person":
                person_boxes.append(item)
            else:
                gear_items.append(item)

    # Hierarchical Association: Link gear to individual persons
    for p_idx, person in enumerate(person_boxes):
        p_box = person["bbox"]
        associated_gear = []
        violations = []

        for gear in gear_items:
            if _is_inside_or_overlapping(gear["bbox"], p_box):
                associated_gear.append(gear["label"])
                if "NO-" in gear["label"]:
                    violations.append(gear["label"])

        worker_status = "Non-Compliant" if violations else "Compliant"
        person["worker_id"] = p_idx + 1
        person["status"] = worker_status
        person["violations"] = violations
        person["gear"] = associated_gear
        detections.append(person)

    # Also include raw gear detections for canvas overlays
    for gear in gear_items:
        detections.append(gear)

    return detections

