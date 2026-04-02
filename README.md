# KavachG - Safety Command Center

KavachG is an industrial safety monitoring and incident response platform.
It combines live camera monitoring, AI-based detection (PPE, fire/smoke, fall), incident tracking, and reporting in a single web interface.

## What This Project Includes

- FastAPI backend with JWT authentication and role-aware access control.
- Browser-based command center frontend.
- Detection endpoints for:
  - PPE detection
  - Fire and smoke detection
  - Fall detection
- Live video streaming endpoints.
- Incident lifecycle management (create, view, update status, feedback).
- Protected incident clip access.
- Settings management for detection sensitivity.
- CSV fall report export.

## Tech Stack

- Backend: Python, FastAPI, SQLite, OpenCV, Ultralytics YOLO
- Frontend: HTML, CSS, Vanilla JavaScript
- Auth: OAuth2 password flow + JWT

## Repository Structure

- Backend: API server, auth, detection logic, database layer
- Frontend: SPA-style command center UI
- Database: SQLite file and stored incident clips
- Models: YOLO model weights and model assets

## Prerequisites

- Python 3.10+ (3.11 recommended)
- Windows, Linux, or macOS
- Camera access for live monitoring endpoints

## Setup

### 1) Create and activate a virtual environment

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

### 2) Install backend dependencies

pip install -r Backend/requirements.txt

### 2.1) Fetch model files (after clone)

This repository is configured to keep heavy model binaries out of git.

1. Update model URLs in `scripts/model_manifest.json` for your private/public model storage.
2. Set environment variables for private model URLs as needed:

KAVACHG_PPE_MODEL_URL=https://your-storage/ppe.pt
KAVACHG_FIRE_MODEL_URL=https://your-storage/fire_last.pt
KAVACHG_POSE_BEST_MODEL_URL=https://your-storage/pose_best.pt
KAVACHG_POSE_LAST_MODEL_URL=https://your-storage/pose_last.pt

The fall model (`yolov8s-pose.pt`) has a public default URL in the manifest.
3. Run:

python scripts/fetch_models.py

If you want to re-download existing files:

python scripts/fetch_models.py --force

### 3) Configure environment variables

Copy Backend/.env.example to Backend/.env and set secure values.

Required variables:

- SECRET_KEY: long random secret used for JWT signing
- ADMIN_PASSWORD: initial admin password
- ADMIN_EMAIL: initial admin email
- ALLOWED_ORIGINS: comma-separated frontend origins
- INCIDENT_API: backend incident endpoint URL

Example:

SECRET_KEY=change_this_to_a_long_random_secret
ADMIN_PASSWORD=change_this_admin_password
ADMIN_EMAIL=admin@kavachg.com
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500
INCIDENT_API=http://localhost:8000/incidents/

## Run the Project

### Start backend

From project root:

cd Backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

Backend URL:

http://127.0.0.1:8000

### Start frontend

In a new terminal:

cd Frontend
python -m http.server 5500

Frontend URL:

http://127.0.0.1:5500

## First Login

Use the admin credentials configured in Backend/.env:

- Email: value of ADMIN_EMAIL
- Password: value of ADMIN_PASSWORD

If the admin user does not exist yet, run:

cd Backend
..\.venv\Scripts\python.exe create_admin_user.py

## API Highlights

- Auth:
  - POST /auth/login
  - POST /auth/register
  - POST /auth/admin/create
- Incidents:
  - GET /incidents/
  - POST /incidents/
  - PATCH /incidents/{incident_id}/status
  - POST /incidents/{incident_id}/feedback
- Detection:
  - POST /detect/ppe/
  - POST /detect/fire-smoke/
  - POST /detect/fall/
- Live video:
  - GET /video_feed
  - GET /live/ppe
  - GET /live/fire-smoke
  - GET /live/fall
- Reports:
  - GET /report/fall

## Security Notes

- Never commit Backend/.env or real secrets.
- Keep SECRET_KEY and ADMIN_PASSWORD strong and private.
- Restrict ALLOWED_ORIGINS to trusted origins in production.

## Development Quality Checks

Run backend lint checks (strict E/F selection):

c:/Desktop/KavachG/.venv/Scripts/python.exe -m ruff check Backend --select E,F --line-length 79

## Known Operational Notes

- Live camera endpoints depend on local camera availability.
- Detection accuracy and speed depend on model quality and hardware.
- Incident clips are stored under Database/incident_clips.

## Keeping Models Out of Git

The `.gitignore` excludes model binaries and training datasets, including:

- `Models/**/*.pt`
- `Models/**/weights/`
- `Models/**/Datasets/`

Recommended storage options for model files:

- GitHub Releases assets
- S3 / Cloudflare R2 / GCS bucket
- Private artifact server

Then point each model entry in `scripts/model_manifest.json` to the hosted URL and run `python scripts/fetch_models.py` on any machine after cloning.
