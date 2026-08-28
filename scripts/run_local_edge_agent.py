#!/usr/bin/env python3
"""
KavachG — Local Edge Node Agent (Option 3)
Connects local cameras and local GPU hardware to the hosted cloud Command Center.
Zero cloud server RAM/GPU usage: All YOLOv8 inference runs on the accessing user's machine!

Usage:
  python scripts/run_local_edge_agent.py --cloud-url https://kavachg-backend.onrender.com --camera 0 --mode ppe
"""

import argparse
import sys
import os
import time
import json
import cv2
import requests

# Add Backend to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "Backend"))
sys.path.insert(0, os.path.join(BASE_DIR, "Backend", "models_ai"))

try:
    from ultralytics import YOLO
    import torch
except ImportError:
    print("[ERROR] Ultralytics or PyTorch not found. Install via: pip install ultralytics torch opencv-python requests")
    sys.exit(1)


def load_model(mode: str):
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"[EDGE AGENT] Hardware Acceleration Engine: {device.upper()}")

    model_map = {
        "ppe": os.path.join(BASE_DIR, "Models", "PPE-Detection", "ppe.pt"),
        "fall": os.path.join(BASE_DIR, "Models", "Fall_Detection", "yolov8s-pose.pt"),
        "fire": os.path.join(BASE_DIR, "Models", "Fire_Smoke", "last.pt"),
        "pose": os.path.join(BASE_DIR, "Models", "Fall_Detection", "yolov8s-pose.pt"),
    }

    model_path = model_map.get(mode, model_map["ppe"])
    if not os.path.exists(model_path):
        print(f"[WARN] Model weights not found at {model_path}, downloading standard YOLOv8...")
        model_path = "yolov8n.pt"

    print(f"[EDGE AGENT] Loading model weights: {model_path}")
    model = YOLO(model_path)
    model.to(device)
    return model, device


def run_edge_agent(cloud_url: str, camera_src, mode: str, confidence: float = 0.5):
    cloud_url = cloud_url.rstrip("/")
    print(f"============================================================")
    print(f"   🚀 KAVACHG LOCAL EDGE INFERENCE NODE (OPTION 3)")
    print(f"   Cloud Gateway:   {cloud_url}")
    print(f"   Camera Source:   {camera_src}")
    print(f"   Inference Mode:  {mode.upper()}")
    print(f"============================================================")

    # 1. Verify Cloud Connection
    try:
        resp = requests.get(f"{cloud_url}/copilot/health", timeout=6)
        if resp.status_code == 200:
            print(f"[EDGE AGENT] Cloud Gateway Connected Successfully! (Status 200)")
        else:
            print(f"[WARN] Cloud Gateway returned status {resp.status_code}. Proceeding in standalone edge mode.")
    except Exception as e:
        print(f"[WARN] Cloud Gateway unreachable ({e}). Running locally.")

    # 2. Load Local YOLO Model
    model, device = load_model(mode)

    # 3. Open Local Camera
    try:
        cam_id = int(camera_src)
        cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
    except ValueError:
        cap = cv2.VideoCapture(camera_src)

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera source: {camera_src}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print(f"[EDGE AGENT] Local Stream Active! Press 'q' in the preview window to stop.")
    last_sync_time = 0
    frame_count = 0
    fps_start_time = time.time()
    fps = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Camera frame drop, retrying...")
            time.sleep(0.05)
            continue

        frame_count += 1
        if frame_count % 30 == 0:
            fps = 30 / (time.time() - fps_start_time)
            fps_start_time = time.time()

        # Run Local Hardware Inference
        results = model.predict(frame, conf=confidence, verbose=False, device=device)
        annotated = results[0].plot()

        # Overlay Edge HUD
        cv2.putText(
            annotated,
            f"KavachG Local Node | FPS: {fps:.1f} | Hardware: {device.upper()}",
            (16, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 240, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("KavachG — Local Edge AI Node (Press 'q' to exit)", annotated)

        # Sync Incident Telemetry to Cloud every 3 seconds if violations detected
        current_time = time.time()
        if current_time - last_sync_time > 3.0:
            last_sync_time = current_time
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                cls_ids = boxes.cls.cpu().numpy().tolist() if hasattr(boxes.cls, 'cpu') else []
                # Check for NO-Hardhat or NO-Safety Vest classes
                names = results[0].names
                detections = [names.get(int(c), str(c)) for c in cls_ids]
                violations = [d for d in detections if "no-" in d.lower() or "fall" in d.lower() or "fire" in d.lower()]

                if violations:
                    print(f"[ALERT] Violation detected on local camera: {violations}. Syncing to cloud...")
                    try:
                        requests.post(
                            f"{cloud_url}/incidents/",
                            json={
                                "type": violations[0].upper(),
                                "location": "Local Edge Node Cam 0",
                                "severity": "High",
                                "description": f"Detected {', '.join(violations)} via local edge GPU node.",
                            },
                            timeout=2,
                        )
                    except Exception:
                        pass

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[EDGE AGENT] Local Edge Node stopped cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KavachG Local Edge Node Agent")
    parser.add_argument("--cloud-url", default="http://127.0.0.1:8000", help="Hosted Cloud API URL (e.g. https://your-app.onrender.com)")
    parser.add_argument("--camera", default="0", help="Camera index (0, 1) or RTSP stream URL")
    parser.add_argument("--mode", default="ppe", choices=["ppe", "fall", "fire", "pose"], help="Inference model mode")
    parser.add_argument("--confidence", type=float, default=0.45, help="Confidence threshold (0.1 to 0.95)")
    args = parser.parse_args()

    run_edge_agent(args.cloud_url, args.camera, args.mode, args.confidence)
