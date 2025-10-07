import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings

# PostgreSQL imports
try:
    import asyncpg
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

class MemoryDB:
    """In-memory database for development and fallback"""
    def __init__(self):
        self.users = []
        self.catches = []
        self.loans = []
        self.insurance = []
    
    async def execute(self, query, *params):
        print(f"DB Query: {query}")
        print(f"Params: {params}")
        
        # Handle user inserts
        if "INSERT INTO users" in query:
            user_data = {
                "id": params[0],
                "email": params[1],
                "password_hash": params[2],
                "user_type": params[3],
                "created_at": params[4] if len(params) > 4 else datetime.now()
            }
            self.users.append(user_data)
            return True
            
        # Handle catch inserts
        elif "INSERT INTO catches" in query:
            catch_data = {
                "id": params[0],
                "user_id": params[1],
                "fish_type": params[2],
                "quantity_kg": params[3],
                "location": params[4],
                "price_analysis": json.loads(params[5]) if isinstance(params[5], str) else params[5],
                "created_at": params[6] if len(params) > 6 else datetime.now()
            }
            self.catches.append(catch_data)
            return True
            
        # Handle user queries
        elif "SELECT * FROM users" in query:
            if "email" in query and "password_hash" in query:
                email = params[0]
                password = params[1]
                for user in self.users:
                    if user['email'] == email and user['password_hash'] == password:
                        return [user]
                return []
            return self.users
            
        # Handle catch queries
        elif "SELECT * FROM catches" in query:
            if "user_id" in query:
                user_id = params[0]
                return [catch for catch in self.catches if catch['user_id'] == user_id]
            return self.catches
            
        return True
    
    async def fetchrow(self, query, *params):
        result = await self.execute(query, *params)
        return result[0] if result and len(result) > 0 else None
    
    async def fetch(self, query, *params):
        result = await self.execute(query, *params)
        return result if result else []
    
    async def fetchval(self, query, *params):
        result = await self.execute(query, *params)
        return len(result) if result else 0

class PostgreSQLDB:
    """PostgreSQL database connection"""
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def init_pool(self):
        """Initialize connection pool"""
        if not POSTGRES_AVAILABLE:
            raise ImportError("asyncpg not available. Install with: pip install asyncpg")
        
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def execute(self, query, *params):
        """Execute a query"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *params)
    
    async def fetchrow(self, query, *params):
        """Fetch a single row"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *params)
    
    async def fetch(self, query, *params):
        """Fetch multiple rows"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *params)
    
    async def fetchval(self, query, *params):
        """Fetch a single value"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *params)

# Global database instance
_db_instance = None

async def get_db():
    """Get database instance"""
    global _db_instance
    
    if _db_instance is None:
        if settings.USE_MEMORY_DB or not settings.DATABASE_URL:
            print("Using in-memory database")
            _db_instance = MemoryDB()
        else:
            print("Using PostgreSQL database")
            _db_instance = PostgreSQLDB(settings.DATABASE_URL)
            await _db_instance.init_pool()
    
    return _db_instance

async def init_db():
    """Initialize database"""
    db = await get_db()
    if isinstance(db, PostgreSQLDB):
        # Create tables if they don't exist
        await create_tables()
    return True

async def create_tables():
    """Create database tables"""
    db = await get_db()
    if isinstance(db, PostgreSQLDB):
        async with db.pool.acquire() as conn:
            # Create users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR PRIMARY KEY,
                    email VARCHAR UNIQUE NOT NULL,
                    password_hash VARCHAR NOT NULL,
                    user_type VARCHAR NOT NULL,
                    name VARCHAR,
                    phone VARCHAR,
                    organization VARCHAR,
                    location VARCHAR,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create catches table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS catches (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    fish_type VARCHAR NOT NULL,
                    quantity_kg DECIMAL NOT NULL,
                    location VARCHAR NOT NULL,
                    price_analysis JSONB,
                    image_analysis JSONB,
                    market_insights JSONB,
                    voice_filename VARCHAR,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create loans table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS loans (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    amount DECIMAL NOT NULL,
                    purpose VARCHAR,
                    status VARCHAR DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create insurance table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS insurance (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    coverage_type VARCHAR,
                    coverage_amount DECIMAL,
                    annual_premium DECIMAL,
                    status VARCHAR DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

async def close_db():
    """Close database connections"""
    global _db_instance
    if _db_instance and isinstance(_db_instance, PostgreSQLDB):
        await _db_instance.close_pool()
        _db_instance = None
