#!/usr/bin/env python3
"""
VajraNetra — Factory Database Seeder
Populates Database/factory.db with operational worker personnel and real-time incident records.
"""

import sqlite3
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DB_PATH = os.path.join(BASE_DIR, "Database", "factory.db")

WORKERS = [
    ("Aarav Sharma", "Senior Machinist • Sector 4", 0),
    ("Vikram Singh", "Forklift Logistics Operator • Sector 2", 0),
    ("Priya Patel", "Quality Control Engineer • Sector 1", 0),
    ("Rajesh Kumar", "Maintenance Lead • Substation C", 1),
    ("Sneha Verma", "Assembly Line Tech • Sector 1", 0),
    ("Ananya Roy", "Safety Compliance Officer", 1),
    ("Karan Mehta", "Welding & Fabrication Specialist", 0),
    ("Rohan Deshmukh", "High-Voltage Electrician", 0),
    ("Sunita Rao", "Inventory & Crane Coordinator", 0),
    ("Deepak Joshi", "Plant Operations Supervisor", 1),
    ("Amitabh Sen", "Robotics Calibration Tech", 0),
    ("Neha Gupta", "Material Handling Specialist", 0),
    ("Suresh Reddy", "Structural Steel Fabricator", 0),
    ("Meera Nair", "Environmental Safety Auditor", 1),
    ("Pooja Hegde", "Assembly Line Operator", 0),
]

NOW = datetime.utcnow()

SAMPLE_INCIDENTS = [
    (
        "PPE Violation (No Hardhat)",
        "Missing Hardhat detected in Sector 4 (Heavy Machining Bay). Worker in proximity of overhead gantry.",
        "Open",
        1,
        0.96,
        None,
        "assets/cctv_factory_1.jpg",
        (NOW - timedelta(minutes=14)).isoformat(),
    ),
    (
        "Proximity Intrusion Warning",
        "Worker entered active automated forklift lane within 1.8m boundary fence.",
        "In Progress",
        2,
        0.91,
        None,
        "assets/cctv_factory_2.jpg",
        (NOW - timedelta(minutes=42)).isoformat(),
    ),
    (
        "Acoustic / Vibration Anomaly",
        "Elevated dB levels (88dB) detected near Compressor Unit B. Maintenance ticket #492 dispatched.",
        "In Progress",
        0,
        0.88,
        None,
        None,
        (NOW - timedelta(hours=2, minutes=10)).isoformat(),
    ),
    (
        "PPE Violation (No Safety Vest)",
        "Worker observed without high-visibility vest during night logistics transition.",
        "Resolved",
        3,
        0.94,
        None,
        "assets/cctv_factory_2.jpg",
        (NOW - timedelta(hours=5, minutes=30)).isoformat(),
    ),
    (
        "Skeletal Slip / Fall Event",
        "Rapid downward vertical velocity detected on wet epoxy surface near wash bay. Operator recovered safely.",
        "Resolved",
        1,
        0.89,
        None,
        "assets/cctv_factory_1.jpg",
        (NOW - timedelta(hours=8, minutes=15)).isoformat(),
    ),
    (
        "Fire & Thermal Signature Test",
        "Routine optical heat signature calibration scan executed on furnace perimeter.",
        "Resolved",
        0,
        0.99,
        None,
        None,
        (NOW - timedelta(hours=14, minutes=0)).isoformat(),
    ),
]


def seed_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Seed People Directory
    c.execute("DELETE FROM people")
    c.executemany(
        "INSERT INTO people (name, extra, admin) VALUES (?, ?, ?)",
        WORKERS,
    )

    # 2. Seed Incident Records
    c.execute("DELETE FROM incidents")
    c.executemany(
        """INSERT INTO incidents (type, description, status, camera_id, confidence, clip_path, evidence_image, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        SAMPLE_INCIDENTS,
    )

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Database seeded cleanly with {len(WORKERS)} workers and {len(SAMPLE_INCIDENTS)} operational incidents in {DB_PATH}")


if __name__ == "__main__":
    seed_db()
