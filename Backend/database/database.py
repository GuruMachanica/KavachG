import os
import sqlite3

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../Database/factory.db")
)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    try:
        yield conn
    finally:
        try:
            conn.close()
        except sqlite3.ProgrammingError:
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
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        c = conn.cursor()
        
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'operator',
            verified INTEGER DEFAULT 1
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
        ensure_column(c, "incidents", "severity", "TEXT DEFAULT 'Medium'")
        ensure_column(c, "incidents", "ai_analysis", "TEXT")

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
            changed_at TEXT,
            changed_by TEXT
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

        c.execute("""CREATE TABLE IF NOT EXISTS restricted_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER DEFAULT 0,
            name TEXT NOT NULL,
            polygon_json TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        # Performance Indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents(created_at DESC)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidents(type)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_events_state ON incident_events(state, incident_type)")

        conn.commit()

