<div align="center">

# KavachG (कवच-G)
### Autonomous Edge-AI Industrial Safety, Computer Vision Defense & 3D Digital Twin Platform

[![License: Inspiration-Only](https://img.shields.io/badge/License-Inspiration--Only-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00ffff.svg)](https://docs.ultralytics.com)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-000000.svg)](https://threejs.org/)
[![OSHA 1910](https://img.shields.io/badge/Compliance-OSHA_1910-orange.svg)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910)
[![Team IronLogic](https://img.shields.io/badge/Developed%20By-Team%20IronLogic-cyan.svg)](#team-ironlogic)

<p align="center">
  <b>High-throughput multi-camera computer vision surveillance, real-time PPE compliance auditing, temporal slip/fall kinematic tracking, thermal/optical flame localization, autonomous multi-agent safety swarm, and 3D Metaverse Digital Twin for industrial manufacturing facilities.</b>
</p>

* **Repository:** [https://github.com/GuruMachanica/KavachG](https://github.com/GuruMachanica/KavachG)
* **Command Console:** `http://127.0.0.1:5500/console.html`
* **Public Portal:** `http://127.0.0.1:5500/index.html`
* **API Documentation:** `http://127.0.0.1:8000/docs`
* **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

</div>

---

## 👥 Team IronLogic & Core Engineering Roles

KavachG was architected and developed by **Team IronLogic**:

| Engineer | Core Responsibilities & Contributions |
| :--- | :--- |
| 💻 **Mohammad Saad** | **Frontend UI/UX Architecture & Command Center Interface**<br>• Designed the modern glassmorphism operator console & responsive multi-page marketing portal<br>• Built the real-time Live Vision HUD, interactive 2×2 CCTV matrix, and Three.js 3D Metaverse Plant Twin |
| ⚙️ **Mohnish Narayan Gupta** | **Complete Backend Architecture & Streaming Services**<br>• Engineered the FastAPI microservice gateway, RESTful API endpoints, and WebSocket push channels<br>• Built token-gated JWT authentication, DirectShow video streaming, and background clip encoder workers |
| 🔍 **Ashutosh Mishra** | **Machine Learning & Computer Vision Models**<br>• Trained custom YOLOv8 PPE detection weights (`ppe.pt`) with IoU worker-to-gear bounding association<br>• Developed 17-point skeletal pose kinematic fall velocity tracking and dual optical/thermal flame localization |
| 🛡️ **Mohammad Huzaifa**<br>([@GuruMachanica](https://github.com/GuruMachanica)) | **Deployment, CI/CD Pipeline, Agentic AI & Database Architecture**<br>• Built the production deployment configurations (`render.yaml`, `vercel.json`, `netlify.toml`, Docker containers, and `DEPLOYMENT.md`)<br>• Developed the Autonomous Multi-Agent Safety Swarm (Sentinel, Dispatcher, Auditor, Watchdog) and model quantization pipeline<br>• Architected the SQLite WAL high-concurrency database connection pooling and automated migration seeders |

**Contact & Permissions:** `ironlogic@zohomail.in`

---

## 🌟 Core System Capabilities

1. **Autonomous Multi-Agent Safety Swarm**:
   * **Sentinel Vision Agent**: 24/7 autonomous multi-camera perception scanner.
   * **Forensic Dispatcher Agent**: Automatically captures incident pre-roll video clips, logs SHA256 hashes, and creates OSHA Form 301 records.
   * **Compliance Auditor Agent**: Supervisor shift briefings and OSHA 1910 standard mappings.
   * **Watchdog Guardian Agent**: Self-healing camera stream buffer monitor maintaining zero stream dropouts.
   * **Autonomous Patrol Mode**: Toggleable camera cycler with live agent thought stream logs in the HUD.

2. **Realistic Three.js 3D Plant Digital Twin**:
   * **4 Sector Factory Floor**: Robotic Assembly (Sector A) with moving conveyor workpieces, High-Voltage Substation (Sector B), High-Bay Warehouse (Sector C), and Logistics Storage (Sector D).
   * **Volumetric Vision Cones**: Semi-transparent 3D camera frustums visualizing CCTV coverage.
   * **Live 3D Worker Avatars**: Moving worker models with real-time safety halo status (Emerald Green for compliant, Red for breach).
   * **360° Orbit Navigation**: Mouse drag to orbit, scroll to zoom, and click nodes to switch edge streams.

3. **Universal Command & Search Palette (`Ctrl + K` / `⌘K`)**:
   * Instant keyboard launcher searching SQLite workers (*Rajesh Kumar, Priya Sharma*), active incidents, system navigation, and one-click actions.

4. **17-Point Skeletal Pose & Kinematic Fall Tracking (OSHA 1910.28)**:
   * Real-time 17-point full-body skeletal joint tracking and spine inclination velocity vectors (`θ < 38°`) to eliminate false alarms.

5. **PPE Association & IoU Binding (OSHA 1910.132 / 1910.135)**:
   * Hardhat, high-vis vest, protective eyewear, and face mask bounding box overlap geometry.

6. **Dual Optical / Thermal Flame Early Warning (OSHA 1910.39)**:
   * Rapid smoke plume localization and optical flame hazard warning with automated EmailJS dispatch.

7. **SQLite WAL Concurrency Engine**:
   * Bounded semaphore read pooling (up to 32 parallel readers) + write mutex with sub-millisecond query execution.

8. **FP16 Half-Precision & ONNX Quantization Pipeline**:
   * Built-in model quantization script (`scripts/optimize_and_quantize_models.py`) reducing VRAM by 50% with ~2x FPS acceleration.

---

## 🏛️ System Topology

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
                 +-- 3D Metaverse Digital Twin                   +-- OpenCV DirectShow Ingestion
                 +-- Universal Search (Ctrl+K)                   +-- Autonomous 4-Agent Swarm
                 +-- Multi-Cam Viewport Matrix                   +-- YOLOv8 PPE Detector (ppe.pt)
                 +-- OSHA 301 PDF Audit Generator                +-- Flame Model (last.pt)
                 +-- Audio Siren & Web Speech PA                 +-- YOLOv8s 17-Pt Pose Engine
                                                                 +-- Incident Clip Worker
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

### Quick Deployment Steps:
1. **Backend on Render**:
   * Open [Render Dashboard](https://dashboard.render.com/) $\rightarrow$ **New Blueprint** $\rightarrow$ select `GuruMachanica/KavachG` (uses [`render.yaml`](render.yaml)).
   * Attaches a 1GB Persistent Disk to `/opt/render/project/src/Database`.
2. **Frontend on Vercel / Netlify**:
   * Import repo $\rightarrow$ set Root Directory to `Frontend`.
   * Deploy as a static Single Page Application.
3. **Connecting Frontend to Cloud Backend**:
   * Open browser DevTools on your deployed frontend and run:
     ```javascript
     localStorage.setItem("apiUrl", "https://your-backend.onrender.com");
     location.reload();
     ```

For the complete step-by-step production deployment manual, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 🏃 Local Quickstart

### Prerequisites
* Python 3.10+ (Recommended: Python 3.11.9)
* WebCam / DirectShow hardware video input

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/GuruMachanica/KavachG.git
cd KavachG

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the FastAPI Backend Gateway
cd Backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# 5. In a new terminal, serve the Frontend
python -m http.server 5500
```

Open your browser at `http://127.0.0.1:5500/console.html` to access the Command Center.

---

## ⚖️ License & Attribution
Distributed under the **Team IronLogic Inspiration-Only License**. See [LICENSE](LICENSE) for terms.  
Commercial inquiries: `ironlogic@zohomail.in`.
