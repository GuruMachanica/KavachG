# fire_smoke_detector.py - OOP Fire and Smoke Vision Detector
import os
from vision.base_detector import BaseVisionDetector

class FireSmokeVisionDetector(BaseVisionDetector):
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "../../Models/Fire_Smoke/Fire_Smoke/last.pt")
        super().__init__(model_path)

    def detect(self, img, conf_threshold: float = 0.18) -> list:
        if not self.model:
            return []
        results = self.model(img, conf=conf_threshold, device=self._device, verbose=False)
        detections = []
        model_names = getattr(self.model, "names", {})

        for r in results:
            boxes = getattr(r, "boxes", None)
            if not boxes:
                continue
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                raw_label = model_names.get(cls, str(cls))
                label = str(raw_label).strip().lower()
                if conf >= conf_threshold:
                    detections.append({
                        "bbox": [int(x1), int(y1), int(x2), int(y2)],
                        "confidence": round(conf, 2),
                        "label": label,
                    })
        return detections


fire_smoke_detector = FireSmokeVisionDetector()
