import sys
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for sub in ["api", "core", "database", "models_ai", "services", "scripts"]:
    sub_path = os.path.join(BASE_DIR, sub)
    if sub_path not in sys.path:
        sys.path.insert(0, sub_path)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlite3
from database import init_db, DB_PATH
from people import router as people_router
from incidents import router as incidents_router
from video import router as video_router
from detection import router as detection_router
from auth import router as auth_router, decode_access_token, get_current_user
from realtime import router as realtime_router
from settings import router as settings_router
from cameras import router as cameras_router
from report import router as report_router
from copilot_router import router as copilot_router
from incident_worker import start_incident_worker

# --- APP SETUP ---
app = FastAPI(title="KavachG Industrial AI Safety Core", version="2.5.0")
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:5500,http://localhost:5500").split(
        ","
    )
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Incident clip directory
CLIPS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../Database/incident_clips")
)
REPORTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../Database/incident_reports")
)
IMAGES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../Database/incident_images")
)


def _validate_user_token(authorization: str | None, token: str | None):
    bearer_token = None
    if authorization and authorization.startswith("Bearer "):
        bearer_token = authorization.split(" ", 1)[1]
    elif token:
        bearer_token = token

    payload = decode_access_token(bearer_token) if bearer_token else None
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE id=?", (payload.get("id"),))
        if not c.fetchone():
            raise HTTPException(status_code=401, detail="User not found")


@app.get("/clips/{clip_name}")
def get_clip(
    clip_name: str,
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _validate_user_token(authorization, token)
    safe_name = os.path.basename(clip_name)
    file_path = os.path.join(CLIPS_DIR, safe_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(file_path, media_type="video/mp4")


@app.get("/incident_reports/{report_name}")
def get_report_file(
    report_name: str,
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _validate_user_token(authorization, token)
    safe_name = os.path.basename(report_name)
    file_path = os.path.join(REPORTS_DIR, safe_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(file_path, media_type="application/pdf")


@app.get("/incident_images/{image_name}")
def get_incident_image(
    image_name: str,
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _validate_user_token(authorization, token)
    safe_name = os.path.basename(image_name)
    file_path = os.path.join(IMAGES_DIR, safe_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Incident image not found")
    return FileResponse(file_path, media_type="image/jpeg")


@app.on_event("startup")
def on_startup():
    init_db()
    start_incident_worker()


# --- INCLUDE ROUTERS ---
app.include_router(people_router, prefix="", tags=["People"])
app.include_router(incidents_router, prefix="", tags=["Incidents"])
app.include_router(video_router, prefix="", tags=["Video"])
app.include_router(detection_router, prefix="", tags=["Detection"])
app.include_router(auth_router, prefix="", tags=["Auth"])
app.include_router(realtime_router, prefix="", tags=["Realtime"])
app.include_router(settings_router, prefix="", tags=["Settings"])
app.include_router(cameras_router, prefix="", tags=["Cameras"])
app.include_router(report_router, prefix="", tags=["Reports"])
app.include_router(copilot_router, prefix="", tags=["Copilot"])


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "KavachG Industrial AI Safety Core",
        "version": "2.5.0",
        "docs": "/docs",
    }
