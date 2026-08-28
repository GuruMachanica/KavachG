import cv2
import time
import numpy as np
from camera_stream import ensure_camera_started, get_camera_index, get_frame
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
from pose_model import detect_pose
from incident_worker import enqueue_incident_job
from realtime import broadcast_incident
import asyncio

# SKELETAL CONNECTIONS (COCO 17-keypoint graph)
POSE_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4), # Head
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10), # Arms
    (5, 11), (6, 12), (11, 12), # Torso
    (11, 13), (13, 15), (12, 14), (14, 16) # Legs
]


def gen_live_detection(model_type):
    if not ensure_camera_started():
        return

    session_id = activate_model(model_type)

    fps = 20
    anomaly_start = None
    recording = False
    frames_buffer = []
    incident_recorded = False
    last_incident_time = 0
    incident_cooldown = 10
    record_duration = 8
    persistence_threshold = 3
    max_buffer = int(fps * record_duration)
    inactive_stream = False
    last_confidence = None

    try:
        while True:
            if not is_active(model_type, session_id):
                if not inactive_stream:
                    sleep_model(model_type)
                    inactive_stream = True

                frame = get_frame(timeout_seconds=1.0)
                if frame is None:
                    continue

                encoded, buffer = cv2.imencode(".jpg", frame)
                if not encoded:
                    continue
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )
                continue

            inactive_stream = False
            frame = get_frame(timeout_seconds=1.0)
            if frame is None:
                continue

            # 1. RUN TARGET DETECTION MODEL
            detections = []
            anomaly = False

            if model_type == "ppe":
                try:
                    detections = detect_ppe(frame)
                    anomaly = any(
                        not det.get("compliant", True) or "NO-" in det.get("label", "").upper()
                        for det in detections
                    )
                except Exception as e:
                    detections = []
            elif model_type == "fire-smoke":
                try:
                    detections = detect_fire_smoke(frame)
                    anomaly = any(
                        "HAZARD" in det.get("label", "").upper() or "FIRE" in det.get("label", "").upper() or "SMOKE" in det.get("label", "").upper()
                        for det in detections
                    )
                except Exception as e:
                    detections = []
            elif model_type == "fall":
                try:
                    detections = detect_fall(frame)
                    anomaly = any(
                        det.get("fall", False) or "FALL" in det.get("label", "").upper()
                        for det in detections
                    )
                except Exception as e:
                    detections = []
            elif model_type == "pose":
                try:
                    detections = detect_pose(frame)
                except Exception as e:
                    detections = []
                anomaly = False

            if detections:
                confs = [
                    float(det.get("confidence", 0.0))
                    for det in detections
                    if det.get("confidence") is not None
                ]
                if confs:
                    last_confidence = max(confs)

            # 2. DRAW HIGH-CONTRAST INDUSTRIAL HUD OVERLAYS
            for det in detections:
                box = det.get("box") or det.get("bbox")
                if box and len(box) == 4:
                    x1, y1, x2, y2 = map(int, box)
                    label = det.get("label", "Object")
                    conf = det.get("confidence", 0.0)
                    compliant = det.get("compliant", True)
                    is_fall = det.get("fall", False)
                    is_danger = not compliant or is_fall or any(k in label.upper() for k in ["NO-", "FALL", "HAZARD", "FIRE", "SMOKE"])

                    if is_danger:
                        box_color = (0, 0, 255) # Red for hazard
                        tag_bg = (0, 0, 220)
                        tag_text = f"VIOLATION: {label} [{int(conf * 100)}%]"
                    else:
                        box_color = (0, 235, 120) # Emerald Green for safe
                        tag_bg = (0, 180, 80)
                        tag_text = f"{label} [{int(conf * 100)}%]"

                    # Draw Bounding Box with Corner Accents
                    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                    corner_len = min(16, (x2 - x1) // 4, (y2 - y1) // 4)
                    if corner_len > 0:
                        # Top-Left
                        cv2.line(frame, (x1, y1), (x1 + corner_len, y1), (0, 255, 255), 3)
                        cv2.line(frame, (x1, y1), (x1, y1 + corner_len), (0, 255, 255), 3)
                        # Bottom-Right
                        cv2.line(frame, (x2, y2), (x2 - corner_len, y2), (0, 255, 255), 3)
                        cv2.line(frame, (x2, y2), (x2, y2 - corner_len), (0, 255, 255), 3)

                    # Tag Badge
                    text_size = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
                    badge_w = text_size[0] + 12
                    badge_h = text_size[1] + 10
                    tag_y1 = max(0, y1 - badge_h)
                    cv2.rectangle(frame, (x1, tag_y1), (x1 + badge_w, tag_y1 + badge_h), tag_bg, -1)
                    cv2.putText(
                        frame,
                        tag_text,
                        (x1 + 6, tag_y1 + badge_h - 4),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA,
                    )

                # Skeletal Keypoints & Bones
                keypoints = det.get("keypoints", [])
                if keypoints:
                    pts = []
                    for pt in keypoints:
                        if len(pt) >= 2 and pt[0] > 0 and pt[1] > 0:
                            pts.append((int(pt[0]), int(pt[1])))
                        else:
                            pts.append(None)

                    # Draw Bones
                    for p1_idx, p2_idx in POSE_CONNECTIONS:
                        if p1_idx < len(pts) and p2_idx < len(pts):
                            p1, p2 = pts[p1_idx], pts[p2_idx]
                            if p1 is not None and p2 is not None:
                                cv2.line(frame, p1, p2, (0, 240, 255), 2)

                    # Draw Joints
                    for pt in pts:
                        if pt is not None:
                            cv2.circle(frame, pt, 4, (0, 0, 255), -1)
                            cv2.circle(frame, pt, 2, (255, 255, 255), -1)

            # 3. AUTONOMOUS FORENSIC CAPTURE & BROADCAST
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
                    enqueued = enqueue_incident_job(
                        model_type=model_type,
                        frames=frames_buffer.copy(),
                        confidence=last_confidence,
                        persistence_threshold=persistence_threshold,
                        camera_id=get_camera_index(),
                    )
                    last_incident_time = now
                    incident_recorded = True
                    recording = False
                    frames_buffer = []

            # Stream Frame
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )
    finally:
        if is_active(model_type, session_id):
            deactivate_models()
        if get_active_model() != model_type:
            sleep_model(model_type)
