import cv2
import time
from camera_stream import ensure_camera_started, get_frame
from live_session import (
    activate_model,
    deactivate_models,
    get_active_model,
    is_active,
)
from model_runtime import sleep_model
from ppe_model import detect_ppe
from fire_smoke_model import detect_fire_smoke
from fall_model import detect_fall
from incidents_storage import save_incident_clip
import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

INCIDENT_API = os.getenv("INCIDENT_API", "http://localhost:8000/incidents/")


def gen_live_detection(model_type):
    if not ensure_camera_started():
        return

    session_id = activate_model(model_type)

    fps = 20  # fallback FPS for clip buffering
    anomaly_start = None
    recording = False
    frames_buffer = []
    incident_recorded = False
    last_incident_time = 0
    incident_cooldown = 15  # seconds to prevent duplicate incidents
    record_duration = 10  # seconds
    persistence_threshold = 5  # anomaly must persist for 5s
    max_buffer = int(fps * record_duration)
    try:
        while True:
            # Sleep previous model streams when a new model is activated.
            if not is_active(model_type, session_id):
                break

            frame = get_frame(timeout_seconds=1.0)
            if frame is None:
                continue

            if model_type == "ppe":
                detections = detect_ppe(frame)
                anomaly = any(
                    "NO-" in det.get("label", "") for det in detections
                )
            elif model_type == "fire-smoke":
                detections = detect_fire_smoke(frame)
                anomaly = any(
                    det.get("label", "").lower() in {"fire", "smoke"}
                    for det in detections
                )
            elif model_type == "fall":
                detections = detect_fall(frame)
                anomaly = any(
                    det.get("label", "").lower() in {"fall", "fallen"}
                    for det in detections
                )
            else:
                detections = []
                anomaly = False

            # Draw detections for all model types.
            for det in detections:
                if "bbox" in det:
                    x1, y1, x2, y2 = map(int, det["bbox"])
                    label = det.get("label", "object")
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )
            now = time.time()
            if anomaly:
                if anomaly_start is None:
                    anomaly_start = now
                elif (
                    not recording
                    and (now - anomaly_start > persistence_threshold)
                    and not incident_recorded
                    and (now - last_incident_time > incident_cooldown)
                ):
                    # Start recording
                    recording = True
                    frames_buffer = []
            else:
                anomaly_start = None
                recording = False
                frames_buffer = []
                incident_recorded = False

            if recording:
                frames_buffer.append(frame.copy())
                if len(frames_buffer) >= max_buffer:
                    # Save clip
                    clip_path = save_incident_clip(frames_buffer, model_type)
                    # Create incident
                    description = (
                        f"{model_type.capitalize()} anomaly detected "
                        f"and persisted for {persistence_threshold}s. "
                        "Clip saved."
                    )
                    try:
                        payload = {
                            "type": model_type,
                            "description": description,
                            "clip_path": os.path.basename(clip_path)
                            if clip_path
                            else None,
                        }
                        requests.post(INCIDENT_API, json=payload, timeout=5)
                    except Exception as e:
                        print(f"Failed to create incident: {e}")
                    last_incident_time = now
                    incident_recorded = True
                    recording = False
                    frames_buffer = []

            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                + frame_bytes
                + b"\r\n"
            )
    finally:
        # If this was still the active session, monitoring has ended.
        if is_active(model_type, session_id):
            deactivate_models()
        # Keep currently active model warm; sleep models when inactive.
        if get_active_model() != model_type:
            sleep_model(model_type)
