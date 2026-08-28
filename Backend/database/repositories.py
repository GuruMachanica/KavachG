# repositories.py - OOP Database Repository Layer
import sqlite3
import json
from datetime import datetime
from core.config import DB_PATH

class BaseRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn


class UserRepository(BaseRepository):
    def get_by_id(self, user_id: int) -> dict | None:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, email, role, verified FROM users WHERE id=?", (user_id,))
            row = c.fetchone()
            if not row:
                return None
            return {"id": row[0], "name": row[1], "email": row[2], "role": row[3], "verified": bool(row[4])}

    def get_by_email(self, email: str) -> tuple | None:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, email, password, role, verified FROM users WHERE email=?", (email,))
            return c.fetchone()

    def create(self, name: str, email: str, hashed_pass: str, role: str = "operator") -> int:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (name, email, password, role, verified) VALUES (?, ?, ?, ?, 1)",
                (name, email, hashed_pass, role),
            )
            conn.commit()
            return c.lastrowid


class IncidentRepository(BaseRepository):
    def list_all(self, status: str = None, itype: str = None) -> list:
        with self.get_connection() as conn:
            c = conn.cursor()
            query = "SELECT id, type, description, status, created_at, clip_path, source, confidence, evidence_image, report_path, camera_id, event_id FROM incidents"
            params = []
            filters = []
            if status:
                filters.append("status = ?")
                params.append(status)
            if itype:
                filters.append("type = ?")
                params.append(itype)
            if filters:
                query += " WHERE " + " AND ".join(filters)
            query += " ORDER BY created_at DESC"
            c.execute(query, params)
            rows = c.fetchall()
            return [
                {
                    "id": r[0], "type": r[1], "description": r[2], "status": r[3],
                    "created_at": r[4], "clip_path": r[5], "source": r[6], "confidence": r[7],
                    "evidence_image": r[8], "report_path": r[9], "camera_id": r[10], "event_id": r[11]
                }
                for r in rows
            ]

    def update_status(self, incident_id: int, new_status: str) -> bool:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE incidents SET status=? WHERE id=?", (new_status, incident_id))
            c.execute("INSERT INTO incident_audit (incident_id, status, changed_at) VALUES (?, ?, ?)",
                      (incident_id, new_status, datetime.utcnow().isoformat()))
            conn.commit()
            return c.rowcount > 0


class ZoneRepository(BaseRepository):
    def list_active(self) -> list:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, camera_id, name, polygon_json FROM restricted_zones WHERE is_active=1")
            rows = c.fetchall()
            zones = []
            for r in rows:
                try:
                    pts = json.loads(r[3])
                except Exception:
                    pts = []
                zones.append({"id": r[0], "camera_id": r[1], "name": r[2], "points": pts})
            return zones

    def save(self, name: str, camera_id: int, points: list) -> int:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO restricted_zones (camera_id, name, polygon_json, is_active) VALUES (?, ?, ?, 1)",
                (camera_id, name, json.dumps(points)),
            )
            conn.commit()
            return c.lastrowid


user_repository = UserRepository()
incident_repository = IncidentRepository()
zone_repository = ZoneRepository()
