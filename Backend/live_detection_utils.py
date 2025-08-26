import cv2
import numpy as np
import time
from threading import Timer
from ppe_model import detect_ppe
from fire_smoke_model import detect_fire_smoke
from fall_model import detect_fall
from incidents_storage import save_incident_clip
import requests

INCIDENT_API = 'http://localhost:8080/incidents/'


def gen_live_detection(model_type):
    cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS) or 20  # fallback to 20 if FPS not available
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
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if model_type == 'ppe':
                detections = detect_ppe(frame_rgb)
                anomaly = any('NO-' in det.get('label','') for det in detections)
            elif model_type == 'fire-smoke':
                detections = detect_fire_smoke(frame_rgb)
                anomaly = any(det.get('label','fire')=='fire' or det.get('label','smoke')=='smoke' for det in detections)
            elif model_type == 'fall':
                detections = detect_fall(frame_rgb)
                anomaly = any(det.get('label','fall')=='fall' for det in detections)
            else:
                detections = []
                anomaly = False
            # Draw detections
            for det in detections:
                if 'bbox' in det:
                    x1, y1, x2, y2 = map(int, det['bbox'])
                    label = det.get('label', 'object')
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            now = time.time()
            if anomaly:
                if anomaly_start is None:
                    anomaly_start = now
                elif not recording and (now - anomaly_start > persistence_threshold) and not incident_recorded and (now - last_incident_time > incident_cooldown):
                    # Start recording
                    recording = True
                    frames_buffer = []
                    record_start = now
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
                    description = f"{model_type.capitalize()} anomaly detected and persisted for {persistence_threshold}s. Clip saved."
                    try:
                        requests.post(INCIDENT_API, json={"type": model_type, "description": description + f" Clip: {clip_path}"})
                    except Exception as e:
                        print(f"Failed to create incident: {e}")
                    last_incident_time = now
                    incident_recorded = True
                    recording = False
                    frames_buffer = []
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()
