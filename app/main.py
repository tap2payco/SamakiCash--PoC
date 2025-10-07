from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime
import os
import requests

from app.core.config import settings
from app.core.database import init_db, close_db, get_db
from app.api import auth, analyze, match, credit, users
from app.models import UserType

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SamakiCash - AI-powered fish market platform for Tanzania"
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="/api", tags=["Catch Analysis"])
app.include_router(match.router, prefix="/api", tags=["Matchmaking"])
app.include_router(credit.router, prefix="/api", tags=["Financial Services"])
app.include_router(users.router, prefix="/api", tags=["Users"])

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started successfully!")
    print(f"📊 Using {'PostgreSQL' if not settings.USE_MEMORY_DB else 'in-memory'} database")
    # Seed test users if none exist
    try:
        conn = await get_db()
        existing = await conn.fetch("SELECT * FROM users")
        if not existing:
            import uuid
            from datetime import datetime
            password = "Piuspe@9702"
            # Fisher
            await conn.execute(
                "INSERT INTO users (id, email, phone, password_hash, user_type, name, organization, location, created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
                str(uuid.uuid4()), "elespius1.0@gmail.com", "+255700000001", password, UserType.FISHER.value, "Fisher User", None, "Mwanza", datetime.now()
            )
            # Seller
            await conn.execute(
                "INSERT INTO users (id, email, phone, password_hash, user_type, name, organization, location, created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
                str(uuid.uuid4()), "elespius1.0@gmail.com", "+255700000002", password, UserType.SELLER.value, "Seller User", "Landing Site", "Dar es Salaam", datetime.now()
            )
            # Buyer
            await conn.execute(
                "INSERT INTO users (id, email, phone, password_hash, user_type, name, organization, location, created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
                str(uuid.uuid4()), "elespius1.0@gmail.com", "+255700000003", password, UserType.BUYER.value, "Buyer User", "Lake Hotel", "Mwanza", datetime.now()
            )
            # Superuser
            await conn.execute(
                "INSERT INTO users (id, email, phone, password_hash, user_type, name, organization, location, created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
                str(uuid.uuid4()), "superuser@samakicash.com", "+255700000000", password, UserType.SUPERUSER.value, "Super Admin", "SamakiCash", "HQ", datetime.now()
            )
            print("👤 Seeded 4 test users (fisher, seller, buyer, superuser)")
    except Exception as e:
        print(f"Seeding users failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await close_db()
    print("👋 SamakiCash API shutdown complete")

# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{settings.APP_NAME} is running!",
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "PostgreSQL" if not settings.USE_MEMORY_DB else "in-memory"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": settings.APP_VERSION
    }

# Audio file serving
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio files"""
    if os.path.exists(filename) and not filename.startswith("error:"):
        return FileResponse(filename)
    return {"status": "error", "message": "Audio file not found"}

# User management endpoints
@app.get("/api/users/buyers")
async def list_buyers():
    """List all buyer users"""
    from app.core.database import get_db
    from app.models import UserType
    
    conn = await get_db()
    users = await conn.fetch("SELECT * FROM users")
    buyers = [u for u in users if u.get("user_type") == UserType.BUYER.value]
    return {"count": len(buyers), "buyers": buyers}

@app.get("/api/users/sellers")
async def list_sellers():
    """List all seller users"""
    from app.core.database import get_db
    from app.models import UserType
    
    conn = await get_db()
    users = await conn.fetch("SELECT * FROM users")
    sellers = [u for u in users if u.get("user_type") in (UserType.SELLER.value, UserType.FISHER.value)]
    return {"count": len(sellers), "sellers": sellers}

# Debug endpoints
@app.get("/api/debug/elevenlabs")
async def debug_elevenlabs():
    """Debug endpoint to check ElevenLabs configuration"""
    api_key = settings.ELEVENLABS_API_KEY
    
    try:
        headers = {"xi-api-key": api_key} if api_key else {}
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=10)
        
        return {
            "has_api_key": bool(api_key),
            "api_key_valid": api_key and api_key.startswith("sk-"),
            "api_connection": response.status_code == 200,
            "voices_available": len(response.json().get('voices', [])) if response.status_code == 200 else 0,
            "message": "Check your ELEVENLABS_API_KEY in .env file" if not api_key else "API key found"
        }
    except Exception as e:
        return {
            "has_api_key": bool(api_key),
            "api_key_valid": api_key and api_key.startswith("sk-"),
            "api_connection": False,
            "error": str(e)
        }

@app.get("/api/debug/users")
async def debug_users():
    """Debug endpoint to list all users"""
    from app.core.database import get_db
    
    conn = await get_db()
    users = await conn.fetch("SELECT * FROM users")
    return {"users": users}

@app.get("/api/debug/catches")
async def debug_catches():
    """Debug endpoint to list all catches"""
    from app.core.database import get_db
    
    conn = await get_db()
    catches = await conn.fetch("SELECT * FROM catches")
    return {"catches": catches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
