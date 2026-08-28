<div align="center">

# KavachG (कवच-G)
### Autonomous Edge-AI Industrial Safety, Computer Vision Defense & 3D Digital Twin Platform

[![License: Inspiration-Only](https://img.shields.io/badge/License-Inspiration--Only-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00ffff.svg)](https://docs.ultralytics.com)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-000000.svg)](https://threejs.org/)
[![OSHA 1910](https://img.shields.io/badge/Compliance-OSHA_1910-orange.svg)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910)
[![Live on Vercel](https://img.shields.io/badge/Frontend-Vercel%20Live-brightgreen.svg)](https://kavach-g.vercel.app)
[![Live on Render](https://img.shields.io/badge/Backend-Render%20Live-46e3b7.svg)](https://kavachg.onrender.com)
[![Team IronLogic](https://img.shields.io/badge/Developed%20By-Team%20IronLogic-cyan.svg)](#team-ironlogic)

<p align="center">
  <b>High-throughput multi-camera computer vision surveillance, real-time PPE compliance auditing, temporal slip/fall kinematic tracking, thermal/optical flame localization, autonomous multi-agent safety swarm, Mistral AI safety reasoning copilot, and 3D Metaverse Digital Twin for industrial manufacturing facilities.</b>
</p>

* **🌐 Live Production Portal:** [https://kavach-g.vercel.app](https://kavach-g.vercel.app)
* **🛡️ Live Safety Command Console:** [https://kavach-g.vercel.app/console](https://kavach-g.vercel.app/console)
* **⚡ Live Backend Cloud API:** [https://kavachg.onrender.com](https://kavachg.onrender.com)
* **📖 Interactive API Documentation:** [https://kavachg.onrender.com/docs](https://kavachg.onrender.com/docs)
* **📂 GitHub Repository:** [https://github.com/GuruMachanica/KavachG](https://github.com/GuruMachanica/KavachG)
* **🚀 Cloud Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

</div>

---

## 👥 Team IronLogic & Core Engineering Roles

KavachG was architected and developed by **Team IronLogic**:

| Engineer | Core Responsibilities & Contributions |
| :--- | :--- |
| 💻 **Mohammad Saad** | **Frontend UI/UX Architecture & Command Center Interface**<br>• Designed the modern glassmorphism operator console & responsive multi-page marketing portal<br>• Built the real-time Live Vision HUD, interactive 2×2 CCTV matrix, and Three.js 3D Metaverse Plant Twin |
| ⚙️ **Mohnish Narayan Gupta** | **Complete Backend Architecture & Streaming Services**<br>• Engineered the FastAPI microservice gateway, RESTful API endpoints, and WebSocket push channels<br>• Built token-gated JWT authentication, DirectShow video streaming, and background clip encoder workers |
| 🔍 **Ashutosh Mishra** | **Machine Learning & Computer Vision Models**<br>• Trained custom YOLOv8 PPE detection weights (`ppe.pt`) with IoU worker-to-gear bounding association<br>• Developed 17-point skeletal pose kinematic fall velocity tracking and dual optical/thermal flame localization |
| 🛡️ **Mohammad Huzaifa**<br>([@GuruMachanica](https://github.com/GuruMachanica)) | **Deployment, CI/CD Pipeline, Agentic AI & Database Architecture**<br>• Built the production deployment configurations (`render.yaml`, `vercel.json`, Docker containers, and `DEPLOYMENT.md`)<br>• Developed the Autonomous Multi-Agent Safety Swarm (Sentinel, Dispatcher, Auditor, Watchdog) and model quantization pipeline<br>• Architected the SQLite WAL high-concurrency database connection pooling, Mistral AI Copilot, and automated migration seeders |

**Contact & Permissions:** `ironlogic@zohomail.in`

---

## ⚡ 3-Tier Multi-Environment AI Perception Engine

KavachG operates across three compute environments, allowing zero-cost cloud hosting alongside local hardware acceleration:

```
+----------------------------------------------------------------------------------------------------+
| TIER 1: CLOUD GATEWAY (Render Free Hosting - $0.00/mo)                                             |
+----------------------------------------------------------------------------------------------------+
|  • FastAPI REST APIs, WebSocket live incident streaming, SQLite WAL database                       |
|  • Simulated optical CCTV surveillance stream with live timecode HUD                               |
|  • URL: https://kavachg.onrender.com                                                               |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| TIER 2: CLIENT-SIDE IN-BROWSER WEBGPU PERCEPTION (Option 2 - 0ms Server Latency)                   |
+----------------------------------------------------------------------------------------------------+
|  • Runs 100% on the accessing client's laptop/phone browser via WebRTC & Canvas WebGPU             |
|  • Real-time hardhat, safety vest bounding, and 17-point skeletal joints with 0 bytes sent to cloud|
|  • Activation: Click "📹 Use Laptop Camera" in the console HUD                                     |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| TIER 3: LOCAL EDGE NODE AGENT (Option 3 - 60+ FPS Hardware Acceleration)                           |
+----------------------------------------------------------------------------------------------------+
|  • Runs YOLOv8 models directly on user's GPU (NVIDIA CUDA / Apple Silicon MPS / DirectML)          |
|  • Connects local camera streams and syncs incident telemetry to cloud in real time                |
|  • Launch: python scripts/run_local_edge_agent.py --cloud-url https://kavachg.onrender.com          |
+----------------------------------------------------------------------------------------------------+
```

---

## 🌟 Core System Capabilities

1. **Autonomous Multi-Agent Safety Swarm**:
   * **Sentinel Vision Agent**: 24/7 autonomous multi-camera perception scanner.
   * **Forensic Dispatcher Agent**: Automatically captures incident pre-roll video clips, logs SHA256 hashes, and creates OSHA Form 301 records.
   * **Compliance Auditor Agent**: Supervisor shift briefings and OSHA 1910 standard mappings.
   * **Watchdog Guardian Agent**: Self-healing camera stream buffer monitor maintaining zero stream dropouts.
   * **Autonomous Patrol Mode**: Toggleable camera cycler with live agent thought stream logs in the HUD.

2. **AI Safety Copilot with Mistral AI & OSHA 1910 Reasoning**:
   * Powered by **Mistral AI (`mistral-small-latest`)** for conversational safety reasoning.
   * Built-in offline regulatory rule engine covering PPE compliance (1910.132/135), Fall protection (1910.28), and Fire suppression (1910.38).

3. **Realistic Three.js 3D Plant Digital Twin**:
   * **4 Sector Factory Floor**: Robotic Assembly (Sector A) with moving conveyor workpieces, High-Voltage Substation (Sector B), High-Bay Warehouse (Sector C), and Logistics Storage (Sector D).
   * **Volumetric Vision Cones**: Semi-transparent 3D camera frustums visualizing CCTV coverage.
   * **Live 3D Worker Avatars**: Moving worker models with real-time safety status halos (Emerald Green for compliant, Red for breach).
   * **360° Orbit Navigation**: Mouse drag to orbit, scroll to zoom, and click nodes to switch edge streams.

4. **Universal Command & Search Palette (`Ctrl + K` / `⌘K`)**:
   * Instant keyboard launcher searching SQLite personnel (*Rajesh Kumar, Priya Sharma*), active incidents, quick navigation, and one-click actions.

5. **17-Point Skeletal Pose & Kinematic Fall Tracking (OSHA 1910.28)**:
   * Real-time 17-point full-body skeletal joint tracking and spine inclination velocity vectors (`θ < 38°`) to eliminate false alarms.

6. **PPE Association & IoU Binding (OSHA 1910.132 / 1910.135)**:
   * Hardhat, high-vis vest, protective eyewear, and face mask bounding box overlap geometry.

7. **Dual Optical / Thermal Flame Early Warning (OSHA 1910.39)**:
   * Rapid smoke plume localization and optical flame hazard warning with automated EmailJS dispatch.

8. **SQLite WAL Concurrency Engine**:
   * Bounded semaphore read pooling (up to 32 parallel readers) + write mutex with sub-millisecond query execution.

---

## 🔐 Master Super-Admin Credentials

* **Email:** `ironlogic.admin@kavachg.io`
* **Password:** `KavachG#Secured2026!IronLogic`
* **Clearance Level:** `Super-Admin (Role: admin)`

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Setup Python Virtual Environment
```bash
git clone https://github.com/GuruMachanica/KavachG.git
cd KavachG

python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Initialize Database & Start Backend
```bash
python Backend/scripts/seed_database.py
cd Backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Launch Frontend Console
```bash
# In a new terminal:
cd Frontend
python -m http.server 5500
```
Open **`http://127.0.0.1:5500/console.html`** in your browser.

---

## 📜 Inspiration-Only License

Copyright (c) 2026 Team IronLogic. All rights reserved.

This software and associated documentation files are licensed under the **Inspiration-Only License**. You are free to view, learn from, and draw inspiration from the architecture, designs, and concepts. **Direct commercial redistribution, rebranding, or reselling of this source code without written permission from Team IronLogic is strictly prohibited.**

For enterprise licensing inquiries: `ironlogic@zohomail.in`
