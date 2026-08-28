import os
import torch
import cv2
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None



def _find_pose_model_path():
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
    # Fallback default
    return os.path.join(search_dirs[0], "Fall_Detection", "yolov8s-pose.pt")


_pose_model = None
_pose_model_path = None
_pose_model_error = None


def get_pose_model():
    global _pose_model, _pose_model_error, _pose_model_path
    if _pose_model is not None:
        return _pose_model

    _pose_model_error = None
    target_path = _find_pose_model_path()
    if os.path.exists(target_path):
        try:
            _pose_model = YOLO(target_path, task="pose")
            _pose_model_path = target_path
            return _pose_model
        except Exception as e:
            _pose_model_error = str(e)
            return None
    return None


def get_pose_model_error():
    global _pose_model_error
    return _pose_model_error


def unload_pose_model() -> None:
    global _pose_model, _pose_model_path, _pose_model_error
    _pose_model = None
    _pose_model_path = None
    _pose_model_error = None



def detect_pose(img, conf_threshold=0.25, device=None):
    model = get_pose_model()
    if not model:
        return []
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        results = model(img, conf=conf_threshold, device=device, verbose=False)
    except Exception as e:
        print(f"[POSE_MODEL] Inference error: {e}")
        return []

    detections = []
    for r in results:
        boxes = getattr(r, "boxes", None)
        keypoints = getattr(r, "keypoints", None)

        if boxes is not None and keypoints is not None:
            xyxy_list = boxes.xyxy.tolist() if len(boxes) > 0 else []
            conf_list = boxes.conf.tolist() if len(boxes) > 0 else []
            kp_data = keypoints.data.tolist() if len(keypoints) > 0 else []

            for i in range(len(xyxy_list)):
                box = [int(x) for x in xyxy_list[i]]
                conf = float(conf_list[i]) if i < len(conf_list) else 0.0
                kps = kp_data[i] if i < len(kp_data) else []

                detections.append(
                    {
                        "class": "Person",
                        "confidence": conf,
                        "bbox": box,
                        "keypoints": kps,
                    }
                )
    return detections
