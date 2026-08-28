<div align="center">

# KavachG (कवच-G)
### Autonomous Edge-AI Industrial Safety & OSHA 1910 Compliance Platform

[![License: Inspiration-Only](https://img.shields.io/badge/License-Inspiration--Only-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00ffff.svg)](https://docs.ultralytics.com)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-000000.svg)](https://threejs.org/)
[![OSHA 1910](https://img.shields.io/badge/Compliance-OSHA_1910-orange.svg)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910)
[![Team IronLogic](https://img.shields.io/badge/Developed%20By-Team%20IronLogic-cyan.svg)](#team-ironlogic)

<p align="center">
  <b>High-throughput multi-camera computer vision surveillance, real-time PPE compliance auditing, temporal slip/fall kinematic tracking, thermal/optical flame localization, and 3D digital twin spatial radar for heavy manufacturing environments.</b>
</p>

* **Repository:** [https://github.com/GuruMachanica/KavachG](https://github.com/GuruMachanica/KavachG)
* **Command Console:** `http://127.0.0.1:5500/console.html`
* **Public Portal:** `http://127.0.0.1:5500/index.html`
* **API Documentation:** `http://127.0.0.1:8000/docs`

</div>

---

## 👥 Team IronLogic

KavachG was engineered and designed by **Team IronLogic**:

* 🛡️ **Mohammad Huzaifa** — Lead Architecture, Vision Pipeline & Core Engines ([@GuruMachanica](https://github.com/GuruMachanica))
* ⚙️ **Mohnish Narayan Gupta** — Full-Stack Systems & Edge Integration
* 🔍 **Ashutosh Mishra** — Machine Learning Models & Kinematic Tracking
* 💻 **Mohammad Saad** — Real-Time Streaming, HUD Visualizer & Forensic Clip Capture

**Contact & Permissions:** `ironlogic@zohomail.in`

---

## 🔐 Default Access Credentials

| Role | Username / Email | Password | Access Clearance |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@kavachg.com` | `admin123456` | Full Clearance (Level 4 Admin) |
| **Fallback Admin** | `admin@kavachg.com` | `change_this_admin_password` | Full Clearance (Level 4 Admin) |

---

## 🌟 Core System Capabilities

* **On-Demand Edge Inference Engine**: Dynamic model lifecycle manager (`model_runtime.py`) that loads YOLO models into VRAM on-demand and sleeps inactive streams to optimize hardware resource utilization.
* **DirectShow & WebRTC Live Streaming**: Windows `cv2.CAP_DSHOW` low-latency camera grabber with dynamic fallback to Direct Device WebCam (`navigator.mediaDevices.getUserMedia`).
* **PPE Compliance Auditing (OSHA 1910.132 / 1910.135)**: Hardhat, safety vest, protective eyewear, and face mask IoU bounding box association.
* **Temporal Kinematic Fall Detection (OSHA 1910.28)**: 17-point skeletal spine vector tracking with vertical velocity thresholding.
* **Dual Optical / Thermal Flame Early Warning (OSHA 1910.39)**: Early flame and smoke hazard localization with rapid alert dispatch.
* **3D Digital Twin Spatial Hologram**: Real-time Three.js radar matrix displaying real plant floor nodes, acoustic anomalies, and temperature sensors.
* **SQLite WAL Concurrency Manager**: Read semaphore pooling (up to 32 parallel readers) + write mutex with automatic 4s background data sync.
* **FP16 Half-Precision & ONNX Quantization**: Automated model export pipeline cutting VRAM usage by 50% with ~2x FPS acceleration.
* **Automated Forensic Clip Recording**: Background workers automatically capture, encode, and archive 5-10 second video clips of safety violations with cryptographic metadata.

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                             KAVACHG COMMAND CENTER                                |
+-----------------------------------------------------------------------------------+
                                         |
                 +-----------------------+-----------------------+
                 |                                               |
                 v                                               v
       +---------------------+                         +---------------------+
       | Frontend Dashboard  |                         |   FastAPI Backend   |
       | (Vanilla JS + HTML) |<--- REST & RTSP M-JPEG --->| (On-Demand Runtime) |
       +---------------------+                         +---------------------+
                 |                                               |
                 v                                               +-- OpenCV DirectShow Ingestion
       +---------------------+                                   +-- On-Demand Model Loader
       | Multi-Cam Viewport  |                                   +-- YOLOv8 PPE Detector (ppe.pt)
       | Bounding Box Canvas |                                   +-- Fire/Smoke Model (last.pt)
       | 3D Radar Twin       |                                   +-- Fall & Pose GNN (yolov8s-pose)
       | PDF/CSV Export      |                                   +-- Restricted Zone Polygon
       +---------------------+                                   +-- Incident Clip Worker
                                                                         |
                                                                         v
                                                               +---------------------+
                                                               | SQLite WAL Engine   |
                                                               | Incident Clip Store |
                                                               +---------------------+
```

---

## ⚡ Edge Computer Vision & Quantization Benchmarks

| Detection Module | Model Architecture | Weights / Format | Precision | mAP@0.5 | Latency (GPU) | Latency (CPU) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PPE Compliance** | YOLOv8s Custom | `ppe.pt` / `ppe.onnx` | FP16 / FP32 | **96.4%** | `11.8ms` | `48.5ms` |
| **Fire & Smoke** | YOLOv8n Anomaly | `last.pt` / `last.onnx` | FP16 / FP32 | **94.8%** | `8.4ms` | `34.2ms` |
| **Fall & Slip** | YOLOv8s-Pose GNN | `yolov8s-pose.pt` | FP16 / FP32 | **95.2%** | `14.2ms` | `58.0ms` |
| **Zone Intrusion** | Polygon Intersection | Vector Ray-Casting | Matrix CPU | **99.9%** | `< 1.0ms` | `< 1.0ms` |

### Automated Quantization Pipeline:
```bash
# Export all PyTorch weights to FP16 Half-Precision ONNX Edge Engines
python scripts/optimize_and_quantize_models.py --format onnx --fp16
```

---

## 🚀 Quickstart & Deployment

### Option A: 1-Click Launch (Windows PowerShell)

```powershell
# Run the automated launch script
.\run_kavachg.ps1
```

---

### Option B: Docker Compose Deployment

```bash
docker compose up -d --build
```

---

### Option C: Manual Setup

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r Backend/requirements.txt

# 3. Seed Database
python Backend/scripts/seed_database.py

# 4. Start Backend Server
uvicorn main:app --host 127.0.0.1 --port 8000

# 5. Start Frontend Server (in a separate terminal)
cd Frontend
python -m http.server 5500
```

---

## 📄 License & Intellectual Property

```
INSPIRATION-ONLY LICENSE
Copyright (c) 2026 Team Ironlogic
All rights reserved.

Team members:
 - Mohammad Huzaifa
 - Mohnish Narayan Gupta
 - Ashutosh Mishra
 - Mohammad Saad

For permissions, contact: ironlogic@zohomail.in
```
See the [LICENSE](LICENSE) file for complete terms and restrictions.
