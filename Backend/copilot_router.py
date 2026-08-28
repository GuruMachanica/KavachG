# copilot_router.py - Safety Copilot & Stream Health Endpoints
from fastapi import APIRouter, Body, Depends
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
def get_system_health(user: dict = Depends(get_current_user)):
    watchdog = get_watchdog_health()
    return {
        "watchdog": watchdog,
        "engine": "active",
        "self_healing": "enabled"
    }


@router.get("/zones")
def list_zones(db: sqlite3.Connection = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.cursor()
    c.execute("SELECT id, camera_id, name, polygon_json, is_active FROM restricted_zones")
    rows = c.fetchall()
    zones = []
    for r in rows:
        try:
            pts = json.loads(r[3])
        except Exception:
            pts = []
        zones.append({
            "id": r[0],
            "camera_id": r[1],
            "name": r[2],
            "points": pts,
            "is_active": bool(r[4])
        })
    set_active_zones(zones)
    return zones


@router.post("/zones")
def create_or_update_zone(payload: dict = Body(...), db: sqlite3.Connection = Depends(get_db), user: dict = Depends(get_current_user)):
    name = payload.get("name", "Restricted Area")
    camera_id = payload.get("camera_id", 0)
    points = payload.get("points", [])
    pts_json = json.dumps(points)
    
    c = db.cursor()
    c.execute(
        "INSERT INTO restricted_zones (camera_id, name, polygon_json, is_active) VALUES (?, ?, ?, 1)",
        (camera_id, name, pts_json)
    )
    db.commit()
    zone_id = c.lastrowid
    
    # Refresh active zones in memory
    c.execute("SELECT id, camera_id, name, polygon_json, is_active FROM restricted_zones WHERE is_active=1")
    active_rows = c.fetchall()
    active_zones = [{"id": r[0], "camera_id": r[1], "name": r[2], "points": json.loads(r[3])} for r in active_rows]
    set_active_zones(active_zones)
    
    return {"message": "Zone saved successfully", "id": zone_id, "name": name}
