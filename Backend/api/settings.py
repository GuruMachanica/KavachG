# settings.py - Detection sensitivity and app settings endpoints
from fastapi import APIRouter, Body, Depends, HTTPException, Query
import sqlite3
from database import get_db

router = APIRouter()


@router.get("/settings/sensitivity")
def get_sensitivity(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT confidence_threshold FROM settings LIMIT 1")
    row = c.fetchone()
    threshold = float(row[0]) if row and row[0] is not None else 0.5
    return {
        "confidence_threshold": threshold,
        "sensitivity": int(threshold * 100)
    }


@router.post("/settings/sensitivity")
def set_sensitivity(
    data: dict = Body(default={}),
    confidence_threshold: float | None = Query(default=None),
    db: sqlite3.Connection = Depends(get_db)
):
    val = confidence_threshold
    if val is None and "confidence_threshold" in data:
        try:
            val = float(data["confidence_threshold"])
        except ValueError:
            val = 0.5
    elif val is None and "value" in data:
        try:
            val = float(data["value"]) / 100.0
        except ValueError:
            val = 0.5
    elif val is None:
        val = 0.5

    c = db.cursor()
    c.execute("UPDATE settings SET confidence_threshold = ?, updated_at = CURRENT_TIMESTAMP", (val,))
    if c.rowcount == 0:
        c.execute("INSERT INTO settings (confidence_threshold) VALUES (?)", (val,))
    db.commit()
    return {
        "message": "Sensitivity updated.",
        "confidence_threshold": val,
        "sensitivity": int(val * 100)
    }
