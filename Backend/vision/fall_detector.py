# fall_detector.py - OOP Fall Detector with Pose Keypoints & Skeletal Angle
import os
import numpy as np
from vision.base_detector import BaseVisionDetector

class FallVisionDetector(BaseVisionDetector):
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "../../Models/Fall_Detection/yolov8s-pose.pt")
        super().__init__(model_path, task="pose")

    def _calc_spine_angle(self, p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if dx == 0 and dy == 0:
            return 90.0
        return np.degrees(np.arctan2(abs(dy), abs(dx)))

    def detect(self, img, conf_threshold: float = 0.35) -> list:
        if not self.model:
            return []
        results = self.model(img, imgsz=640, device=self._device, verbose=False)
        detections = []

        for result in results:
            boxes = getattr(result, "boxes", None)
            kpts = getattr(result, "keypoints", None)
            if not boxes:
                continue

            for idx, box in enumerate(boxes):
                try:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue
                    xyxy = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                    w = max(1, x2 - x1)
                    h = max(1, y2 - y1)
                    aspect_ratio = w / float(h)
                    spine_angle = 90.0
                    is_fall = False

                    if kpts is not None and hasattr(kpts, "xy") and idx < len(kpts.xy):
                        kp = kpts.xy[idx].cpu().numpy()
                        if len(kp) >= 17:
                            ls, rs = kp[5], kp[6]
                            lh, rh = kp[11], kp[12]
                            if (ls[0] > 0 or rs[0] > 0) and (lh[0] > 0 or rh[0] > 0):
                                s_mid = [(ls[0] + rs[0]) / 2.0, (ls[1] + rs[1]) / 2.0]
                                h_mid = [(lh[0] + rh[0]) / 2.0, (lh[1] + rh[1]) / 2.0]
                                spine_angle = self._calc_spine_angle(s_mid, h_mid)
                                if spine_angle < 38.0 and aspect_ratio > 1.1:
                                    is_fall = True
                                elif spine_angle < 25.0:
                                    is_fall = True

                    if not is_fall and aspect_ratio > 1.6 and h < 180:
                        is_fall = True

                    detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": float(conf),
                        "label": "Fallen" if is_fall else "Stable",
                        "spine_angle": float(spine_angle),
                        "aspect_ratio": round(aspect_ratio, 2),
                    })
                except Exception:
                    continue
        return detections


fall_detector = FallVisionDetector()
