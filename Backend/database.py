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
    def ensure_column(cursor, table_name, column_name, definition):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {row[1] for row in cursor.fetchall()}
        if column_name not in columns:
            cursor.execute(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {definition}"
            )

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
        ensure_column(c, "incidents", "source", "TEXT DEFAULT 'manual'")
        ensure_column(c, "incidents", "confidence", "REAL")
        ensure_column(c, "incidents", "evidence_image", "TEXT")
        ensure_column(c, "incidents", "report_path", "TEXT")
        ensure_column(c, "incidents", "camera_id", "INTEGER")
        ensure_column(c, "incidents", "event_id", "INTEGER")
        c.execute("""CREATE TABLE IF NOT EXISTS incident_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_type TEXT NOT NULL,
            camera_id INTEGER,
            state TEXT NOT NULL,
            started_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            resolved_at TEXT,
            incident_count INTEGER DEFAULT 0
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
