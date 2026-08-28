# config.py - Enterprise Configuration & Environment Settings
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv("SECRET_KEY", "kavachg_enterprise_secure_secret_key_2026_x89a")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../Database/factory.db"))
CLIPS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../Database/incident_clips"))
REPORTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../Database/incident_reports"))
IMAGES_DIR = os.path.abspath(os.path.join(BASE_DIR, "../Database/incident_images"))
JOBS_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../Database/incident_jobs"))

for d in [os.path.dirname(DB_PATH), CLIPS_DIR, REPORTS_DIR, IMAGES_DIR, JOBS_ROOT]:
    os.makedirs(d, exist_ok=True)
