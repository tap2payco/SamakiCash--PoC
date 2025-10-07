# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import requests
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from elevenlabs.client import ElevenLabs
import base64
from enum import Enum
from pydantic import Field

# Load environment variables
load_dotenv()

app = FastAPI(title="SamakiCash API", version="1.0.0")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://samakicash-pwa.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory database simulation
class MemoryDB:
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

# Global in-memory database
memory_db = MemoryDB()

async def get_db():
    return memory_db

async def init_db():
    print("Using in-memory database for demo")
    return True

@app.on_event("startup")
async def startup_event():
    await init_db()

# Pydantic models & User types
class UserType(str, Enum):
    FISHER = "fisher"
    SELLER = "seller"   # seller = dagaa vendor / landing site seller
    BUYER = "buyer"     # buyer = wholesaler / hotel / processor / trader

class UserCreate(BaseModel):
    email: str
    password: str
    user_type: UserType = Field(default=UserType.FISHER)
    name: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None  # useful for buyers
    location: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class FishCatchRequest(BaseModel):
    fish_type: str
    quantity_kg: float
    location: str
    user_id: str
    image_data: Optional[str] = None

class LoanApplication(BaseModel):
    user_id: str
    amount: float
    purpose: str = "fishing_equipment"

class InsuranceQuoteRequest(BaseModel):
    user_id: str
    coverage_type: str = "equipment"
    coverage_amount: float = 1000000

# API Key validation
def validate_api_key(api_key: str, service: str):
    if not api_key or not api_key.startswith("sk-"):
        print(f"Warning: Invalid {service} API key format")
    return True

# Mistral AI Integration
async def call_mistral_ai(context: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv('MISTRAL_API_KEY')
    validate_api_key(api_key, "Mistral AI")
    
    prompt = f"""
    As an expert fish market analyst in Tanzania, analyze this fishing catch:
    Fish Type: {context.get('fish_type', 'unknown')}
    Quantity: {context.get('quantity_kg', 0)} kg
    Location: {context.get('location', 'unknown')}
    
    Provide a fair market price per kg in TZS with detailed reasoning.
    Return JSON with: fair_price, currency, reasoning, confidence_score
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistral-large-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return json.loads(result['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Mistral AI error: {e}")
        return {
            "fair_price": 5200,
            "currency": "TZS",
            "reasoning": "High demand in Mwanza market",
            "confidence_score": 0.8
        }

# AI/ML API Integration
async def call_aiml_api(context: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv('AIML_API_KEY')
    validate_api_key(api_key, "AI/ML API")
    
    prompt = f"""
    Provide market insights for fish trading in Tanzania:
    Fish: {context.get('fish_type')}
    Location: {context.get('location')}
    
    Include: demand trends, competitor prices, recommendations.
    Format as JSON with: market_trend, competitor_analysis, recommendation
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://api.aimlapi.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"AI/ML API error: {e}")
        return {
            "market_trend": "Growing demand",
            "competitor_analysis": "Average price: 4000-6000 TZS/kg",
            "recommendation": "Sell in morning for best prices"
        }

# Nebius AI Integration
async def call_nebius_ai(image_data: Optional[str] = None) -> Dict[str, Any]:
    api_key = os.getenv('NEBIUS_API_KEY')
    validate_api_key(api_key, "Nebius AI")
    
    if not image_data:
        return {"analysis": "No image provided"}
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "nebius-vision-v1",
            "image": image_data,
            "encoding": "base64",
            "tasks": ["quality_assessment"]
        }
        
        response = requests.post(
            "https://api.nebius.ai/v1/vision/analyze",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Nebius AI error: {e}")
        return {
            "quality_assessment": "good",
            "freshness": "fresh",
            "confidence": 0.7
        }

# ElevenLabs Integration - Updated and Fixed
async def call_elevenlabs(price_data: Dict[str, Any], market_data: Dict[str, Any]) -> str:
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    # If no API key or invalid format, skip gracefully
    if not api_key or not api_key.startswith("sk-"):
        print("ElevenLabs API key not configured or invalid - skipping voice generation")
        return "voice_generation_skipped"
    
    try:
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        # Create a clear, concise message in Swahili
        message = f"""
        Habari! SamakiCash hapa. 
        Bei ya soko ya {price_data.get('fish_type', 'samaki')} ni TZS {price_data.get('fair_price', 0)} kwa kilo.
        Sababu: {price_data.get('reasoning', 'mahitaji ya soko')}.
        Ushauri: {market_data.get('recommendation', 'nunua kwa bei nzuri')}.
        Asante na kwa heri!
        """
        
        # Clean up the message
        message = " ".join(message.split())  # Remove extra whitespace
        
        # Get available voices
        voices_response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers=headers,
            timeout=30
        )
        
        if voices_response.status_code != 200:
            print(f"Voice fetch failed: {voices_response.status_code} - {voices_response.text}")
            return "voice_generation_failed"
        
        voices = voices_response.json().get('voices', [])
        if not voices:
            print("No voices available in ElevenLabs account")
            return "voice_generation_failed"
        
        # Try to find a suitable voice (prefer multilingual voices)
        voice_id = None
        for voice in voices:
            if voice.get('name') == 'Bella' or 'multilingual' in voice.get('description', '').lower():
                voice_id = voice.get('voice_id')
                break
        
        # Fallback to first available voice
        if not voice_id and voices:
            voice_id = voices[0]['voice_id']
        
        if not voice_id:
            print("No valid voice ID found")
            return "voice_generation_failed"
        
        print(f"Using voice ID: {voice_id}")
        
        # Generate speech
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            json={
                "text": message,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            },
            headers=headers,
            timeout=45
        )
        
        if response.status_code == 200:
            filename = f"price_alert_{uuid.uuid4().hex[:8]}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Voice message saved as: {filename}")
            return filename
        else:
            print(f"Speech generation failed: {response.status_code} - {response.text}")
            return "voice_generation_failed"
            
    except requests.exceptions.Timeout:
        print("ElevenLabs API timeout - voice generation took too long")
        return "voice_generation_timeout"
    except requests.exceptions.ConnectionError:
        print("ElevenLabs connection error - check internet connection")
        return "voice_connection_error"
    except Exception as e:
        print(f"ElevenLabs unexpected error: {str(e)}")
        return "voice_generation_failed"

# Store catch record
async def store_catch_record(request: FishCatchRequest, price_analysis: Dict, market_insights: Dict, image_analysis: Dict, voice_filename: str):
    try:
        conn = await get_db()
        catch_id = str(uuid.uuid4())
        
        await conn.execute(
            """INSERT INTO catches (id, user_id, fish_type, quantity_kg, location, price_analysis, created_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7)""",
            catch_id, request.user_id, request.fish_type, request.quantity_kg, 
            request.location, json.dumps(price_analysis), datetime.now()
        )
    except Exception as e:
        print(f"Database storage error: {e}")

# API Endpoints
@app.post("/api/auth/register")
async def register(user: UserCreate):
    try:
        # Basic duplicate check (in-memory)
        conn = await get_db()
        existing = await conn.fetch("SELECT * FROM users WHERE email = $1", user.email)
        if existing:
            return {"status": "error", "message": "User with that email already exists"}

        user_id = str(uuid.uuid4())

        await conn.execute(
            "INSERT INTO users (id, email, password_hash, user_type, created_at) VALUES ($1, $2, $3, $4, $5)",
            user_id, user.email, user.password, user.user_type.value, datetime.now()
        )

        # Optionally store extended profile in separate table / fields - for demo we keep simple
        return {"status": "success", "user_id": user_id, "user_type": user.user_type.value}
    except Exception as e:
        print("Registration error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
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

from fastapi import HTTPException

@app.post("/api/analyze-catch")
async def analyze_catch(request: FishCatchRequest, background_tasks: BackgroundTasks):
    """
    Analyze a fisher's catch:
    - call Mistral for price analysis
    - call an AI/ML API for market insights
    - optionally call Nebius for image analysis
    - optionally generate a voice file via ElevenLabs
    - store the record in background
    Returns a safe, renderable analysis_summary plus detailed JSON pieces.
    """
    try:
        # -----------------------
        # 1) Price analysis (Mistral)
        # -----------------------
        try:
            price_analysis = await call_mistral_ai(request.dict())
            if not isinstance(price_analysis, dict):
                raise ValueError("Mistral returned unexpected format")
        except Exception as e:
            print(f"[analyze_catch] Mistral AI failed: {e}")
            price_analysis = {
                "fair_price": 0,
                "currency": "TZS",
                "reasoning": "fallback price due to AI error",
                "confidence_score": 0.0
            }

        # -----------------------
        # 2) Market insights (AI/ML API)
        # -----------------------
        try:
            market_insights = await call_aiml_api(request.dict())
            # if the integration returns a raw string or unexpected object, normalize
            if isinstance(market_insights, dict):
                market_trend = market_insights.get("market_trend") or market_insights.get("market_trend_major", "stable")
            else:
                market_trend = str(market_insights)
                market_insights = {"market_trend": market_trend}
        except Exception as e:
            print(f"[analyze_catch] AI/ML API failed: {e}")
            market_insights = {"market_trend": "stable", "recommendation": "Sell in the morning for best price"}

        # -----------------------
        # 3) Image analysis (Nebius) - optional
        # -----------------------
        try:
            image_analysis = await call_nebius_ai(request.image_data) if request.image_data else {"analysis": "no image provided"}
            if not isinstance(image_analysis, dict):
                image_analysis = {"analysis": str(image_analysis)}
        except Exception as e:
            print(f"[analyze_catch] Nebius AI failed: {e}")
            image_analysis = {"analysis": "image analysis failed", "confidence": 0.0}

        # -----------------------
        # 4) Voice generation (ElevenLabs) - optional
        # -----------------------
        try:
            voice_filename = await call_elevenlabs(price_analysis, market_insights)
            # standardize failure markers
            if not voice_filename or voice_filename in ("voice_generation_failed", "voice_generation_timeout", "voice_generation_skipped", "voice_connection_error"):
                voice_filename = None
        except Exception as e:
            print(f"[analyze_catch] ElevenLabs failed: {e}")
            voice_filename = None

        # -----------------------
        # 5) Build a safe, human-friendly summary
        # -----------------------
        try:
            suggested_price = price_analysis.get("fair_price", "N/A")
            currency = price_analysis.get("currency", "TZS")
            market_trend_text = market_insights.get("market_trend") if isinstance(market_insights, dict) else str(market_insights)
            summary = (
                f"{request.quantity_kg} kg of {request.fish_type} in {request.location}. "
                f"Suggested price: {suggested_price} {currency}/kg. "
                f"Market trend: {market_trend_text}."
            )
        except Exception as e:
            print(f"[analyze_catch] Summary build failed: {e}")
            summary = f"{request.quantity_kg} kg of {request.fish_type} in {request.location}. Price unavailable."

        # -----------------------
        # 6) Store in DB (background)
        # -----------------------
        try:
            background_tasks.add_task(store_catch_record, request, price_analysis, market_insights, image_analysis, voice_filename)
        except Exception as e:
            # storing should not block the response; log for later debugging
            print(f"[analyze_catch] Failed to queue DB store: {e}")

        # -----------------------
        # 7) Return a consistent payload (safe to render)
        # -----------------------
        response_payload = {
            "status": "success",
            "price_analysis": price_analysis,
            "market_insights": market_insights,
            "image_analysis": image_analysis,
            "voice_message_url": f"/audio/{voice_filename}" if voice_filename else None,
            "analysis_summary": summary,
            "recommendation": f"Suggested price: TZS {suggested_price} per kg" if suggested_price != "N/A" else "No price recommendation"
        }

        return response_payload

    except Exception as e:
        # If something truly unexpected happens, return a 500 with error info
        print(f"[analyze_catch] Fatal error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/credit-score")
async def get_credit_score(user_id: str):
    try:
        conn = await get_db()
        catches = await conn.fetch("SELECT * FROM catches WHERE user_id = $1", user_id)
        
        score = 650 + (len(catches) * 10)
        score = min(score, 850)
        
        return {
            "user_id": user_id,
            "credit_score": score,
            "loan_eligible": score > 600,
            "max_loan_amount": score * 1000,
            "catch_count": len(catches)
        }
    except Exception as e:
        return {
            "user_id": user_id,
            "credit_score": 700,
            "loan_eligible": True,
            "max_loan_amount": 700000,
            "catch_count": 5
        }

@app.post("/api/insurance-quote")
async def get_insurance_quote(request: InsuranceQuoteRequest):
    try:
        premium = request.coverage_amount * 0.05
        
        return {
            "user_id": request.user_id,
            "coverage_type": request.coverage_type,
            "coverage_amount": request.coverage_amount,
            "annual_premium": premium,
            "message": "Comprehensive coverage"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

class MatchRequest(BaseModel):
    fish_type: str
    quantity_kg: float
    location: str
    user_id: Optional[str] = None

@app.post("/api/match")
async def make_match(request: MatchRequest):
    """
    Simple matchmaking: uses price/demand analysis then returns candidate buyers.
    To match real buyers you must register buyer accounts (user_type='buyer').
    """
    try:
        conn = await get_db()

        # 1) Get price + market insights using AI services
        price_analysis = await call_mistral_ai(request.dict())
        market_insights = await call_aiml_api(request.dict())

        # 2) Find buyers from the in-memory DB
        all_users = await conn.fetch("SELECT * FROM users")
        buyers = [u for u in all_users if u.get("user_type") == "buyer"]

        # 3) Build simple match scoring & result
        matches = []
        for b in buyers:
            # Simple heuristic: base score on Mistral confidence + random factor
            confidence = float(price_analysis.get("confidence_score", 0)) if price_analysis else 0.5
            score = int(min(max(30 + confidence * 60, 0), 100))
            matches.append({
                "buyer_id": b.get("id"),
                "buyer_contact": b.get("email"),
                "match_score": score,
                "estimated_price_per_kg": price_analysis.get("fair_price"),
                "estimated_total_value": round(price_analysis.get("fair_price", 0) * request.quantity_kg, 2),
                "note": "Simulated match (use buyer preferences in production)"
            })

        # 4) Provide a short string summary (safe to render directly in UI)
        summary = (
            f"{request.quantity_kg} kg of {request.fish_type} at {request.location}. "
            f"Suggested price: {price_analysis.get('fair_price', 'N/A')} {price_analysis.get('currency','TZS')}/kg. "
            f"Market trend: {market_insights.get('market_trend', market_insights.get('market_trend', 'stable'))}."
        )

        return {
            "status": "success",
            "matches": matches,
            "price_analysis": price_analysis,
            "market_insights": market_insights,
            "analysis_summary": summary
        }

    except Exception as e:
        print("Matchmaking error:", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    if os.path.exists(filename) and not filename.startswith("error:"):
        return FileResponse(filename)
    return {"status": "error", "message": "Audio file not found"}

@app.get("/")
async def root():
    return {"message": "SamakiCash API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/users/buyers")
async def list_buyers():
    conn = await get_db()
    users = await conn.fetch("SELECT * FROM users")
    buyers = [u for u in users if u.get("user_type") == UserType.BUYER.value]
    return {"count": len(buyers), "buyers": buyers}

@app.get("/api/users/sellers")
async def list_sellers():
    conn = await get_db()
    users = await conn.fetch("SELECT * FROM users")
    sellers = [u for u in users if u.get("user_type") in (UserType.SELLER.value, UserType.FISHER.value)]
    return {"count": len(sellers), "sellers": sellers}

# Debug endpoints
@app.get("/api/debug/elevenlabs")
async def debug_elevenlabs():
    """Debug endpoint to check ElevenLabs configuration"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
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
    conn = await get_db()
    users = await conn.fetch("SELECT * FROM users")
    return {"users": users}

@app.get("/api/debug/catches")
async def debug_catches():
    conn = await get_db()
    catches = await conn.fetch("SELECT * FROM catches")
    return {"catches": catches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)