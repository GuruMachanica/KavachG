# ppe_detector.py - OOP PPE Compliance Detector with Person-to-Gear Binding
import os
from vision.base_detector import BaseVisionDetector

CLASS_NAMES = [
    "Hardhat", "Mask", "NO-Hardhat", "NO-Mask", "NO-Safety Vest",
    "Person", "Safety Cone", "Safety Vest", "machinery", "vehicle"
]

class PPEVisionDetector(BaseVisionDetector):
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "../../Models/PPE-Detection/ppe.pt")
        super().__init__(model_path)

    def _is_overlapping(self, gear_box, person_box, min_overlap=0.3):
        gx1, gy1, gx2, gy2 = gear_box
        px1, py1, px2, py2 = person_box
        g_area = max(1, (gx2 - gx1) * (gy2 - gy1))
        ix1, iy1 = max(gx1, px1), max(gy1, py1)
        ix2, iy2 = min(gx2, px2), min(gy2, py2)
        inter_area = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        return (inter_area / float(g_area)) >= min_overlap

    def detect(self, img, conf_threshold: float = 0.25) -> list:
        if not self.model:
            return []
        results = self.model(img, conf=conf_threshold, device=self._device, verbose=False)
        detections = []
        persons = []
        gears = []

        model_names = getattr(self.model, "names", CLASS_NAMES)
        for r in results:
            boxes = getattr(r, "boxes", None)
            if not boxes:
                continue
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                raw_label = model_names.get(cls, str(cls)) if isinstance(model_names, dict) else str(cls)
                item = {
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(conf, 2),
                    "label": raw_label,
                }
                if raw_label.lower() == "person":
                    persons.append(item)
                else:
                    gears.append(item)

        for idx, p in enumerate(persons):
            violations = [g["label"] for g in gears if self._is_overlapping(g["bbox"], p["bbox"]) and "NO-" in g["label"]]
            p["worker_id"] = idx + 1
            p["status"] = "Non-Compliant" if violations else "Compliant"
            p["violations"] = violations
            detections.append(p)

        detections.extend(gears)
        return detections


ppe_detector = PPEVisionDetector()
