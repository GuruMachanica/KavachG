import sqlite3
from passlib.context import CryptContext

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

def main():
    db_path = '../Database/factory.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    email = 'admin@kavachg.com'
    password = 'kavachG'
    name = 'Admin'
    role = 'admin'
    verified = True
    # Check if admin already exists
    c.execute("SELECT id FROM users WHERE email=?", (email,))
    if c.fetchone():
        print('Admin user already exists.')
        return
    hashed_password = get_password_hash(password)
    c.execute("INSERT INTO users (name, email, password, role, verified) VALUES (?, ?, ?, ?, ?)", (name, email, hashed_password, role, verified))
    conn.commit()
    print('Admin user created.')

if __name__ == "__main__":
    main()
