import sqlite3
import os
from dotenv import load_dotenv
from database import init_db, DB_PATH
from core.security import password_manager

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def get_password_hash(password):
    return password_manager.hash(password)



def main():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    email = os.getenv("ADMIN_EMAIL", "admin@vajranetra.com")

    password = os.getenv("ADMIN_PASSWORD", "admin123456")
    if not password:
        password = "admin_secure_password_2026"
    name = "Admin"
    role = "admin"
    verified = True

    # Check if admin already exists
    c.execute("SELECT id FROM users WHERE email=?", (email,))
    if c.fetchone():
        print(f"Admin user ({email}) already exists.")
        return

    hashed_password = get_password_hash(password)
    c.execute(
        (
            "INSERT INTO users (name, email, password, role, verified) "
            "VALUES (?, ?, ?, ?, ?)"
        ),
        (name, email, hashed_password, role, verified),
    )
    conn.commit()
    print(f"Admin user ({email}) created successfully.")


if __name__ == "__main__":
    main()

