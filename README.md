# KavachG - Safety Command Center

KavachG is an industrial safety monitoring and incident response platform.
It combines live camera monitoring, AI-based detection (PPE, fire/smoke,
fall), incident tracking, and reporting in one web interface.

## Features

- FastAPI backend with JWT authentication and role-based access.
- Browser-based command center frontend.
- AI detection APIs:
  - PPE detection
  - Fire and smoke detection
  - Fall detection
- Live monitoring streams:
  - Raw camera feed
  - PPE live detection
  - Fire/smoke live detection
  - Fall live detection
- Incident lifecycle management:
  - create, list, status update, feedback
- Protected incident clip access.
- Detection sensitivity settings API.
- Fall incident CSV export.

## Monitoring Runtime Behavior

KavachG uses on-demand model runtime for live monitoring:

- Models are loaded when a monitoring mode is activated.
- Only one live model stream is active at a time.
- Switching to another live model sleeps the previous model.
- Pausing monitoring (or switching to raw feed) stops monitoring and
  unloads models.

## Tech Stack

- Backend: Python, FastAPI, SQLite, OpenCV, Ultralytics YOLO
- Frontend: HTML, CSS, Vanilla JavaScript
- Auth: OAuth2 password flow + JWT

## Repository Layout

- `Backend/`: API server, auth, detection, monitoring runtime, DB access
- `Frontend/`: command center UI
- `Database/`: sqlite DB and incident clips
- `Models/`: model weights/assets included in this repository
- `scripts/`: optional model utility scripts

## Prerequisites

- Python 3.10+ (3.11 recommended)
- Windows/Linux/macOS
- Webcam/camera access for live monitoring endpoints

## Setup

### 1) Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r Backend/requirements.txt
```

### 3) Configure environment variables

Copy `Backend/.env.example` to `Backend/.env` and set secure values.

Required variables:

- `SECRET_KEY`
- `ADMIN_PASSWORD`
- `ADMIN_EMAIL`
- `ALLOWED_ORIGINS`
- `INCIDENT_API`

Example:

```env
SECRET_KEY=change_this_to_a_long_random_secret
ADMIN_PASSWORD=change_this_admin_password
ADMIN_EMAIL=admin@kavachg.com
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500
INCIDENT_API=http://localhost:8000/incidents/
```

## Run

### Start backend

From project root:

```powershell
cd Backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL: `http://127.0.0.1:8000`

### Start frontend

In another terminal:

```powershell
cd Frontend
python -m http.server 5500
```

Frontend URL: `http://127.0.0.1:5500`

## First Login

Use values from `Backend/.env`:

- Email: `ADMIN_EMAIL`
- Password: `ADMIN_PASSWORD`

If admin user does not exist:

```powershell
cd Backend
..\.venv\Scripts\python.exe create_admin_user.py
```

## API Overview

### Auth

- `POST /auth/login`
- `POST /auth/register`
- `POST /auth/admin/create`

### Incidents

- `GET /incidents/`
- `POST /incidents/`
- `PATCH /incidents/{incident_id}/status`
- `POST /incidents/{incident_id}/feedback`

### Detection (image upload)

- `POST /detect/ppe/`
- `POST /detect/fire-smoke/`
- `POST /detect/fall/`

### Live Monitoring

- `GET /video_feed`
- `GET /live/ppe`
- `GET /live/fire-smoke`
- `GET /live/fall`
- `POST /monitoring/stop`

### Reports

- `GET /report/fall`

## Development Checks

```powershell
c:/Desktop/KavachG/.venv/Scripts/python.exe -m ruff check Backend --select E,F --line-length 79
```

## Notes

- Camera endpoints require camera availability and permissions.
- Detection speed/accuracy depend on hardware and model quality.
- Incident clips are stored in `Database/incident_clips`.

## Security

- Do not commit `Backend/.env`.
- Use strong `SECRET_KEY` and admin credentials.
- Restrict `ALLOWED_ORIGINS` in production.
