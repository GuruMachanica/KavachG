from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from database import init_db
from people import router as people_router
from incidents import router as incidents_router
from video import router as video_router
from detection import router as detection_router
from auth import router as auth_router
from realtime import router as realtime_router
from settings import router as settings_router
from cameras import router as cameras_router
from report import router as report_router

# --- APP SETUP ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve incident video clips
CLIPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Database/incident_clips'))
app.mount("/clips", StaticFiles(directory=CLIPS_DIR), name="clips")

# --- INIT DB ---
init_db()

# --- INCLUDE ROUTERS ---
app.include_router(people_router)
app.include_router(incidents_router)
app.include_router(video_router)
app.include_router(detection_router)
app.include_router(auth_router)
app.include_router(realtime_router)
app.include_router(settings_router)
app.include_router(cameras_router)
app.include_router(report_router)

@app.get("/")
def root():
    return {"message": "Factory Safety Backend Running"}
