import os
import torch
import cv2
from ultralytics import YOLO

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MODEL_PATHS = [
    os.path.join(BASE_DIR, "Models", "Pose", "best.pt"),
    os.path.join(BASE_DIR, "Models", "Fall_Detection", "yolov8s-pose.pt"),
    os.path.join(BASE_DIR, "Models", "Pose", "last.pt"),
]

ONNX_PATH = os.path.join(BASE_DIR, "Models", "Pose", "best.onnx")
ENGINE_PATH = os.path.join(BASE_DIR, "Models", "Pose", "best.engine")

_pose_model = None
_pose_model_path = None
_pose_model_error = None


def get_pose_model():
    global _pose_model, _pose_model_error, _pose_model_path
    if _pose_model is not None:
        return _pose_model

    _pose_model_error = None

    if os.path.exists(ENGINE_PATH) and torch.cuda.is_available():
        try:
            _pose_model = YOLO(ENGINE_PATH, task="pose")
            _pose_model_path = ENGINE_PATH
            return _pose_model
        except Exception:
            pass

    if os.path.exists(ONNX_PATH):
        try:
            _pose_model = YOLO(ONNX_PATH, task="pose")
            _pose_model_path = ONNX_PATH
            return _pose_model
        except Exception:
            pass

    for model_path in MODEL_PATHS:
        if not os.path.exists(model_path):
            continue
        try:
            _pose_model = YOLO(model_path, task="pose")
            _pose_model_path = model_path
            return _pose_model
        except Exception as exc:
            _pose_model_error = str(exc)

    return _pose_model


def unload_pose_model() -> None:
    global _pose_model, _pose_model_path
    _pose_model = None
    _pose_model_path = None


def get_pose_model_error() -> str | None:
    return _pose_model_error


def get_pose_model_path() -> str | None:
    return _pose_model_path


def detect_pose(img):
    model = get_pose_model()
    if not model:
        return []

    device = "cuda" if torch.cuda.is_available() else "cpu"
    half = True if device == "cuda" else False
    
    results = model(
        img,
        imgsz=640,
        device=device,
        half=half,
        verbose=False,
    )

    detections = []
    for result in results:
        boxes = getattr(result, "boxes", None)
        kpts = getattr(result, "keypoints", None)
        if boxes is None:
            continue

        for idx, box in enumerate(boxes):
            keypoints = []
            if kpts is not None and hasattr(kpts, "xy") and idx < len(kpts.xy):
                keypoints = kpts.xy[idx].tolist()

            detections.append(
                {
                    "box": [
                        int(box.xyxy[0][0]),
                        int(box.xyxy[0][1]),
                        int(box.xyxy[0][2]),
                        int(box.xyxy[0][3]),
                    ],
                    "confidence": float(box.conf[0]),
                    "label": f"Worker #{idx + 1}: Pose Tracked",
                    "compliant": True,
                    "keypoints": keypoints,
                }
            )

    return detections
