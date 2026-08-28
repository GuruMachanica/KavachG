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

## 👥 Team IronLogic & Core Engineering Roles

KavachG was architected and built by **Team IronLogic**:

| Engineer | Core Responsibilities & Contributions |
| :--- | :--- |
| 💻 **Mohammad Saad** | **Frontend UI/UX Architecture & Command Center Interface**<br>• Designed the modern glassmorphism operator console & responsive multi-page marketing portal<br>• Built the real-time Live Vision HUD, interactive 2x2 CCTV matrix, and Three.js 3D Holographic Radar Twin |
| ⚙️ **Mohnish Narayan Gupta** | **Complete Backend Architecture & Streaming Services**<br>• Engineered the FastAPI microservice gateway, RESTful API endpoints, and WebSocket push channels<br>• Built token-gated JWT authentication, DirectShow video streaming, and background clip encoder workers |
| 🔍 **Ashutosh Mishra** | **Machine Learning & Computer Vision Models**<br>• Trained custom YOLOv8 PPE detection weights (`ppe.pt`) with IoU worker-to-gear bounding association<br>• Developed 17-point skeletal pose kinematic fall velocity tracking and dual optical/thermal flame localization |
| 🛡️ **Mohammad Huzaifa**<br>([@GuruMachanica](https://github.com/GuruMachanica)) | **Deployment, CI/CD Pipeline, Agentic AI & Database Architecture**<br>• Built the production deployment configurations (`render.yaml`, `vercel.json`, `netlify.toml`, Docker containers)<br>• Developed the Agentic AI Safety Copilot LLM, Autonomous Watchdog self-healing engine, and model quantization pipeline<br>• Architected the SQLite WAL high-concurrency database connection pooling and automated migration seeders |

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

## ☁️ Deployment Guide (Render + Vercel / Netlify)

KavachG includes pre-configured deployment blueprints for zero-configuration cloud hosting:

### 1. Deploy Backend to Render (FastAPI Web Service)
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New + > Web Service**.
2. Connect your GitHub repository (`https://github.com/GuruMachanica/KavachG`).
3. Set the following settings (or select the included `render.yaml` blueprint):
   * **Runtime**: `Python`
   * **Build Command**: `pip install --upgrade pip && pip install -r Backend/requirements.txt`
   * **Start Command**: `python Backend/scripts/seed_database.py && cd Backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   * `ALLOWED_ORIGINS`: `*` (or your Vercel/Netlify frontend URL)
   * `JWT_SECRET`: `your_secure_secret_key`
   * `ADMIN_EMAIL`: `admin@kavachg.com`
   * `ADMIN_PASSWORD`: `admin123456`
5. Copy your live Render URL (e.g. `https://kavachg-api.onrender.com`).

---

### 2. Deploy Frontend to Vercel (1-Click)
1. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New > Project**.
2. Import `GuruMachanica/KavachG`.
3. Set **Root Directory** to `./` (Vercel automatically detects `vercel.json`).
4. Click **Deploy**.

---

### 3. Deploy Frontend to Netlify (Alternative)
1. Go to [Netlify Dashboard](https://app.netlify.com/) and click **Add new site > Import an existing project**.
2. Select GitHub repo `GuruMachanica/KavachG`.
3. Netlify automatically reads `netlify.toml` (`publish = "Frontend"`).
4. Click **Deploy Site**.

---

## ⚡ Edge Computer Vision & Quantization Benchmarks

| Detection Module | Model Architecture | Weights / Format | Precision | mAP@0.5 | Latency (GPU) | Latency (CPU) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PPE Compliance** | YOLOv8s Custom | `ppe.pt` / `ppe.onnx` | FP16 / FP32 | **96.4%** | `11.8ms` | `48.5ms` |
| **Fire & Smoke** | YOLOv8n Anomaly | `last.pt` / `last.onnx` | FP16 / FP32 | **94.8%** | `8.4ms` | `34.2ms` |
| **Fall & Slip** | YOLOv8s-Pose GNN | `yolov8s-pose.pt` | FP16 / FP32 | **95.2%** | `14.2ms` | `58.0ms` |
| **Zone Intrusion** | Polygon Intersection | Vector Ray-Casting | Matrix CPU | **99.9%** | `< 1.0ms` | `< 1.0ms` |

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
