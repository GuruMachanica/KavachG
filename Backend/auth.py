from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import sqlite3
from database import get_db

router = APIRouter()

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    verified: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials.")
    c = db.cursor()
    c.execute("SELECT id, name, email, role FROM users WHERE id=?", (payload["id"],))
    user = c.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return {"id": user[0], "name": user[1], "email": user[2], "role": user[3]}


@router.post("/auth/register", response_model=UserOut)
def register(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT id FROM users WHERE email=?", (user.email,))
    if c.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered.")
    hashed_password = get_password_hash(user.password)
    c.execute(
        "INSERT INTO users (name, email, password, role, verified) VALUES (?, ?, ?, ?, ?)",
        (user.name, user.email, hashed_password, user.role, False)
    )
    db.commit()
    user_id = c.lastrowid
    return UserOut(id=user_id, name=user.name, email=user.email, role=user.role, verified=False)

@router.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT id, name, email, password, role, verified FROM users WHERE email=?", (form_data.username,))
    user = c.fetchone()
    if not user or not verify_password(form_data.password, user[3]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    access_token = create_access_token({"id": user[0], "email": user[2], "role": user[4]})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user[0], "name": user[1], "email": user[2], "role": user[4], "verified": user[5]}}
