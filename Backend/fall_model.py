import os
import time
import cv2
import numpy as np
import torch
try:
    from ultralytics import YOLO  # type: ignore
except ImportError:
    YOLO = None



def _find_fall_model_path():
    search_dirs = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Models")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "Models")),
        os.path.abspath(os.path.join(os.getcwd(), "Models")),
        os.path.abspath(os.path.join(os.getcwd(), "..", "Models")),
        "/app/Models",
    ]
    candidates = [
        ("Fall_Detection", "yolov8s-pose.pt"),
        ("Pose", "best.pt"),
        ("Pose", "yolov8s-pose.pt"),
    ]
    for d in search_dirs:
        for sub, name in candidates:
            p = os.path.join(d, sub, name)
            if os.path.exists(p):
                return p
    return os.path.join(search_dirs[0], "Fall_Detection", "yolov8s-pose.pt")


MODEL_PATH = _find_fall_model_path()
_fall_model = None

# Track person states across frames for temporal fall analysis
# dict: track_id -> {"last_hip_y": float, "last_time": float, "fall_counter": int}
_person_history = {}


def get_fall_model():
    global _fall_model
    if _fall_model is None:
        target = _find_fall_model_path()
        if os.path.exists(target):
            try:
                _fall_model = YOLO(target, task="pose")
            except Exception as e:
                print(f"[FALL_MODEL] Error loading model: {e}")
                return None
    return _fall_model



def unload_fall_model() -> None:
    global _fall_model
    _fall_model = None


def _calculate_angle_with_horizontal(p1, p2):
    """Calculates angle of line (p1 -> p2) with the horizontal ground plane (0 = horizontal, 90 = vertical)."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0 and dy == 0:
        return 90.0
    angle_rad = np.arctan2(abs(dy), abs(dx))
    return np.degrees(angle_rad)


def detect_fall(img, conf_threshold=0.35):
    model = get_fall_model()
    if not model:
        return []

    device = "cuda" if torch.cuda.is_available() else "cpu"
    results = model(img, imgsz=640, device=device, verbose=False)
    detections = []
    current_time = time.time()

    for result in results:
        boxes = getattr(result, "boxes", None)
        kpts = getattr(result, "keypoints", None)
        if boxes is None or len(boxes) == 0:
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

                is_fall = False
                confidence_score = conf
                spine_angle = 90.0

                # Analyze Pose Keypoints if available
                if kpts is not None and hasattr(kpts, "xy") and idx < len(kpts.xy):
                    kp = kpts.xy[idx].cpu().numpy()  # shape (17, 2)
                    
                    # Keypoints mapping for COCO Pose:
                    # 5: left_shoulder, 6: right_shoulder, 11: left_hip, 12: right_hip
                    # 13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle
                    if len(kp) >= 17:
                        left_shoulder, right_shoulder = kp[5], kp[6]
                        left_hip, right_hip = kp[11], kp[12]

                        has_shoulders = (left_shoulder[0] > 0 or right_shoulder[0] > 0)
                        has_hips = (left_hip[0] > 0 or right_hip[0] > 0)

                        if has_shoulders and has_hips:
                            # Midpoint of shoulders
                            shoulder_mid = [
                                (left_shoulder[0] + right_shoulder[0]) / 2.0,
                                (left_shoulder[1] + right_shoulder[1]) / 2.0,
                            ]
                            # Midpoint of hips
                            hip_mid = [
                                (left_hip[0] + right_hip[0]) / 2.0,
                                (left_hip[1] + right_hip[1]) / 2.0,
                            ]

                            spine_angle = _calculate_angle_with_horizontal(shoulder_mid, hip_mid)
                            
                            # Fall criterion: Spine angle < 38 degrees (horizontal) AND box aspect ratio > 1.15
                            if spine_angle < 38.0 and aspect_ratio > 1.1:
                                is_fall = True
                            elif spine_angle < 25.0:
                                is_fall = True

                # Fallback to aspect ratio only if keypoints could not be resolved
                if not is_fall and aspect_ratio > 1.6 and h < 180:
                    is_fall = True

                label = "Fallen" if is_fall else "Stable"
                color = (0, 0, 255) if is_fall else (0, 255, 0)

                # Overlay box and status on image
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    img,
                    f"{label} ({int(spine_angle)}deg)",
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

                detections.append(
                    {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": float(conf),
                        "label": label,
                        "spine_angle": float(spine_angle),
                        "aspect_ratio": round(aspect_ratio, 2),
                    }
                )
            except Exception:
                continue

    return detections

