import os
import sqlite3
import threading
from contextlib import contextmanager

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../Database/factory.db")
)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Concurrency Control: Read/Write Connection Semaphore
_DB_WRITE_LOCK = threading.Lock()
_MAX_CONCURRENT_READS = 32
_READ_SEMAPHORE = threading.BoundedSemaphore(value=_MAX_CONCURRENT_READS)


def _configure_connection(conn: sqlite3.Connection):
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 10000;")  # 10 second busy timeout
    conn.execute("PRAGMA cache_size = -64000;")   # 64MB memory page cache
    conn.execute("PRAGMA mmap_size = 268435456;") # 256MB memory-mapped IO
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """FastAPI Dependency for concurrent connection retrieval."""
    _READ_SEMAPHORE.acquire()
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)
        _configure_connection(conn)
        yield conn
    finally:
        if conn:
            try:
                conn.close()
            except sqlite3.ProgrammingError:
                pass
        _READ_SEMAPHORE.release()


@contextmanager
def get_write_db():
    """Context manager for thread-safe concurrent database writes."""
    with _DB_WRITE_LOCK:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)
        _configure_connection(conn)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def init_db():
    def ensure_column(cursor, table_name, column_name, definition):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {row["name"] for row in cursor.fetchall()}
        if column_name not in columns:
            cursor.execute(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {definition}"
            )

    with get_write_db() as conn:
        c = conn.cursor()
        
        # 1. Users Table
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'operator',
            verified INTEGER DEFAULT 1
        )""")
        
        # 2. People Directory Table
        c.execute("""CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            extra TEXT,
            admin INTEGER DEFAULT 0
        )""")
        
        # 3. Incidents Table & Performance Indexes
        c.execute("""CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Open',
            camera_id INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0.0,
            clip_path TEXT,
            evidence_image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Create Covering Indexes for sub-millisecond query execution
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents (status);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents (created_at DESC);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_cam ON incidents (camera_id);")

        # 4. Settings Table
        c.execute("""CREATE TABLE IF NOT EXISTS settings (
            confidence_threshold REAL DEFAULT 0.5,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Migration column integrity checks
        ensure_column(c, "incidents", "evidence_image", "TEXT")
        ensure_column(c, "incidents", "clip_path", "TEXT")
        ensure_column(c, "incidents", "camera_id", "INTEGER DEFAULT 0")
        ensure_column(c, "incidents", "confidence", "REAL DEFAULT 0.0")

        # Seed default admin user if table empty
        c.execute("SELECT count(*) as cnt FROM users")
        u_row = c.fetchone()
        if not u_row or u_row["cnt"] == 0:
            from passlib.context import CryptContext
            pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
            default_admin_hash = pwd_ctx.hash("KavachG#Secured2026!CodeGambit")
            c.execute(
                "INSERT INTO users (id, name, email, password, role, verified) VALUES (?, ?, ?, ?, ?, ?)",
                (1, "Lead Security Architect", "codegambit.admin@kavachg.io", default_admin_hash, "admin", 1)
            )


