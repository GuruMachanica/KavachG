import os
import time
import cv2
import numpy as np
import torch
from ultralytics import YOLO

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MODEL_PATH = os.path.join(BASE_DIR, "Models", "Fall_Detection", "yolov8s-pose.pt")
ONNX_PATH = os.path.join(BASE_DIR, "Models", "Fall_Detection", "yolov8s-pose.onnx")
ENGINE_PATH = os.path.join(BASE_DIR, "Models", "Fall_Detection", "yolov8s-pose.engine")

_fall_model = None
_person_history = {}


def get_fall_model():
    global _fall_model
    if _fall_model is None:
        target_path = None
        if os.path.exists(ENGINE_PATH) and torch.cuda.is_available():
            target_path = ENGINE_PATH
        elif os.path.exists(ONNX_PATH):
            target_path = ONNX_PATH
        elif os.path.exists(MODEL_PATH):
            target_path = MODEL_PATH

        if target_path:
            _fall_model = YOLO(target_path, task="pose")
    return _fall_model


def unload_fall_model() -> None:
    global _fall_model
    _fall_model = None


def _calculate_angle_with_horizontal(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0 and dy == 0:
        return 90.0
    angle_rad = np.arctan2(abs(dy), abs(dx))
    return np.degrees(angle_rad)


def detect_fall(
    img,
    conf_threshold=0.5,
    angle_threshold=38.0,
    velocity_threshold=40.0,
    persistence_frames=2,
    device=None,
):
    global _person_history
    model = get_fall_model()
    if not model:
        return []

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    half_precision = True if device == "cuda" else False

    results = model(img, conf=conf_threshold, device=device, half=half_precision, verbose=False)
    detections = []
    current_time = time.time()

    for r in results:
        boxes = r.boxes
        keypoints = r.keypoints

        if boxes is None or keypoints is None:
            continue

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf[0])
            box_coords = [int(x1), int(y1), int(x2), int(y2)]

            kpts = keypoints[i].data[0].cpu().numpy()
            if len(kpts) < 17:
                continue

            left_shoulder = kpts[5][:2]
            right_shoulder = kpts[6][:2]
            left_hip = kpts[11][:2]
            right_hip = kpts[12][:2]

            # Midpoints for spine vector
            mid_shoulder = (left_shoulder + right_shoulder) / 2.0
            mid_hip = (left_hip + right_hip) / 2.0

            # Spine angle with horizontal
            spine_angle = _calculate_angle_with_horizontal(mid_shoulder, mid_hip)

            # Spatial vertical velocity calculation
            current_hip_y = mid_hip[1]
            track_key = f"{int(x1/50)}_{int(x2/50)}"
            velocity = 0.0

            if track_key in _person_history:
                last_state = _person_history[track_key]
                dt = max(0.01, current_time - last_state["last_time"])
                dy = current_hip_y - last_state["last_hip_y"]
                velocity = dy / dt

                if spine_angle < angle_threshold:
                    last_state["fall_counter"] += 1
                else:
                    last_state["fall_counter"] = max(0, last_state["fall_counter"] - 1)

                last_state["last_hip_y"] = current_hip_y
                last_state["last_time"] = current_time
            else:
                _person_history[track_key] = {
                    "last_hip_y": current_hip_y,
                    "last_time": current_time,
                    "fall_counter": 1 if spine_angle < angle_threshold else 0,
                }

            fall_counter = _person_history[track_key]["fall_counter"]
            is_fall = (fall_counter >= persistence_frames) or (
                spine_angle < angle_threshold and velocity > velocity_threshold
            )

            detections.append(
                {
                    "box": box_coords,
                    "confidence": conf,
                    "class_id": 1 if is_fall else 0,
                    "label": f"{'FALL DETECTED' if is_fall else 'Standing/Nominal'} (Angle: {spine_angle:.1f}°)",
                    "fall": is_fall,
                    "spine_angle": float(spine_angle),
                    "velocity": float(velocity),
                }
            )

    return detections
