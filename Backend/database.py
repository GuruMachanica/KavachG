import os
import sqlite3

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../Database/factory.db")
)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        try:
            conn.close()
        except sqlite3.ProgrammingError:
            # FastAPI may finalize dependency cleanup from another thread.
            # Ignore close-time mismatch to prevent false 500 responses.
            pass


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # c.execute('''DROP TABLE IF EXISTS users''')
        # Do not drop users table.
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            verified INTEGER DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            extra TEXT,
            admin INTEGER DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Open',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            clip_path TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS incident_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            status TEXT,
            changed_at TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        conn.commit()
