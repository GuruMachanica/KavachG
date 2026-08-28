# copilot_router.py - Safety Copilot & Stream Health Endpoints
from fastapi import APIRouter, Body, Depends, Header
from auth import get_current_user
from safety_copilot import ask_safety_copilot, generate_daily_safety_briefing, analyze_incident_with_ai
from stream_watchdog import get_watchdog_health
from restricted_area_model import set_active_zones, get_active_zones
import json
import sqlite3
from database import get_db

router = APIRouter()


@router.get("/copilot/briefing")
def get_briefing(user: dict = Depends(get_current_user)):
    return generate_daily_safety_briefing()


@router.post("/copilot/ask")
def query_copilot(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    query = payload.get("query", "")
    return ask_safety_copilot(query)


@router.get("/copilot/health")
def get_system_health():
    watchdog = get_watchdog_health()
    return {
        "status": "healthy",
        "watchdog": watchdog,
        "engine": "active",
        "self_healing": "enabled"
    }


@router.get("/zones")
def list_zones(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS restricted_zones (id INTEGER PRIMARY KEY AUTOINCREMENT, camera_id INTEGER, name TEXT, polygon_json TEXT, is_active INTEGER)")
    c.execute("SELECT id, camera_id, name, polygon_json, is_active FROM restricted_zones")
    rows = c.fetchall()
    zones = []
    for r in rows:
        zones.append({
            "id": r["id"],
            "camera_id": r["camera_id"],
            "name": r["name"],
            "polygon": json.loads(r["polygon_json"]) if r["polygon_json"] else [],
            "is_active": bool(r["is_active"])
        })
    return zones


@router.post("/zones")
def save_zone(payload: dict = Body(...), db: sqlite3.Connection = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS restricted_zones (id INTEGER PRIMARY KEY AUTOINCREMENT, camera_id INTEGER, name TEXT, polygon_json TEXT, is_active INTEGER)")
    c.execute(
        "INSERT INTO restricted_zones (camera_id, name, polygon_json, is_active) VALUES (?, ?, ?, ?)",
        (payload.get("camera_id", 0), payload.get("name", "Zone"), json.dumps(payload.get("polygon", [])), 1)
    )
    db.commit()
    return {"message": "Zone configured successfully"}
