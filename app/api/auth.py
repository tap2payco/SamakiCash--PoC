from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
from app.models import UserCreate, LoginRequest
from app.core.database import get_db

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    """Register a new user"""
    try:
        # Basic duplicate check
        conn = await get_db()
        existing = await conn.fetch("SELECT * FROM users WHERE email = $1", user.email)
        if existing:
            return {"status": "error", "message": "User with that email already exists"}

        user_id = str(uuid.uuid4())

        await conn.execute(
            "INSERT INTO users (id, email, password_hash, user_type, created_at) VALUES ($1, $2, $3, $4, $5)",
            user_id, user.email, user.password, user.user_type.value, datetime.now()
        )

        return {"status": "success", "user_id": user_id, "user_type": user.user_type.value}
    except Exception as e:
        print("Registration error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(credentials: LoginRequest):
    """Login user"""
    try:
        conn = await get_db()
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND password_hash = $2",
            credentials.email, credentials.password
        )
        
        if user:
            return {
                "user_id": user['id'],
                "user_type": user['user_type'],
                "message": "Login successful"
            }
        else:
            return {"status": "error", "message": "Invalid credentials"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
