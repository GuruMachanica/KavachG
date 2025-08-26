from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3
from database import get_db
from realtime import broadcast_incident
import asyncio

router = APIRouter()

class IncidentCreate(BaseModel):
    type: str
    description: str

class IncidentOut(BaseModel):
    id: int
    type: str
    description: str
    status: str
    created_at: str | None
    clip_path: str | None = None

@router.post("/incidents/", response_model=IncidentOut)
def add_incident(incident: IncidentCreate, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    # If incident has a clip_path attribute, use it; else None
    clip_path = getattr(incident, 'clip_path', None)
    c.execute("INSERT INTO incidents (type, description, clip_path) VALUES (?, ?, ?)", (incident.type, incident.description, clip_path))
    db.commit()
    incident_id = c.lastrowid
    c.execute("SELECT id, type, description, status, created_at, clip_path FROM incidents WHERE id=?", (incident_id,))
    row = c.fetchone()
    incident_obj = IncidentOut(id=row[0], type=row[1], description=row[2], status=row[3], created_at=row[4], clip_path=row[5])
    # Broadcast to WebSocket clients
    asyncio.create_task(broadcast_incident(incident_obj.dict()))
    return incident_obj

@router.get("/incidents/", response_model=List[IncidentOut])
def get_incidents(status: str = None, type: str = None, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    query = "SELECT id, type, description, status, created_at, clip_path FROM incidents"
    params = []
    filters = []
    if status:
        filters.append("status = ?")
        params.append(status)
    if type:
        filters.append("type = ?")
        params.append(type)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY created_at DESC"
    c.execute(query, params)
    return [IncidentOut(id=row[0], type=row[1], description=row[2], status=row[3], created_at=row[4], clip_path=row[5]) for row in c.fetchall()]

@router.patch("/incidents/{incident_id}/status")
def update_incident_status(incident_id: int, status: str, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT id FROM incidents WHERE id=?", (incident_id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Incident not found.")
    c.execute("UPDATE incidents SET status=? WHERE id=?", (status, incident_id))
    c.execute("INSERT INTO incident_audit (incident_id, status, changed_at) VALUES (?, ?, ?)", (incident_id, status, datetime.utcnow().isoformat()))
    db.commit()
    return {"message": "Status updated."}

@router.get("/incidents/audit/{incident_id}")
def get_incident_audit(incident_id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT status, changed_at FROM incident_audit WHERE incident_id=? ORDER BY changed_at DESC", (incident_id,))
    return [{"status": row[0], "changed_at": row[1]} for row in c.fetchall()]

# --- Feedback Endpoint ---
from fastapi import Body

@router.post("/incidents/{incident_id}/feedback")
def submit_feedback(incident_id: int, comment: str = Body(...), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("INSERT INTO feedback (incident_id, comment) VALUES (?, ?)", (incident_id, comment))
    db.commit()
    return {"message": "Feedback submitted."}
