# Roadmap — from one big `main.py` to a clean, agentic multi-file SamakiCash backend

Nice — I’ll act like your senior dev and give a **practical, prioritized plan** you can follow (or hand to another dev). It covers **what to change, why, and exactly how** to split the code, wire agents, test, secure and deploy so the system runs smoothly.

---

# 1 — Goals (what we get)

* Clear separation of concerns (auth, AI services, agents, DB, API routes).
* Easy to test, maintain and onboard new contributors.
* Agents (matchmaker, credit scorer, notifier, orchestrator) that can be developed/tested independently.
* Safer API (better error handling, timeouts, fallbacks) and production-ready deployment pipeline.

---

# 2 — High-level project layout (copy/paste-ready)

```
samakicash-backend/
├─ app/
│  ├─ __init__.py
│  ├─ main.py                # FastAPI app, middleware, router includes
│  ├─ config.py              # env loading, constants
│  ├─ db.py                  # DB wrapper (MemoryDB -> Postgres later)
│  ├─ models.py              # Pydantic models & enums
│  ├─ schemas.py             # SQLAlchemy / DB models (when using Postgres)
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ analyze.py
│  │  ├─ match.py
│  │  ├─ credit.py
│  │  └─ insurance.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ mistral.py
│  │  ├─ aiml_api.py
│  │  ├─ nebius.py
│  │  └─ elevenlabs_service.py
│  ├─ agents/
│  │  ├─ __init__.py
│  │  ├─ orchestrator.py     # orchestrates agent flows & background jobs
│  │  ├─ matchmaker.py
│  │  ├─ credit_scoring.py
│  │  └─ notifier.py
│  ├─ tasks/
│  │  └─ queue_worker.py     # optional worker for background queue
│  ├─ utils.py               # helpers (safe fetch, file management)
│  └─ tests/                 # unit & integration tests
├─ docker-compose.yml
├─ Dockerfile
├─ .env.example
├─ requirements.txt
└─ README.md
```

---

# 3 — Step-by-step migration plan (priority order)

## Step A — Create the scaffolding (1–2 hours)

* Create folders/files above.
* Move existing functions into `services/*` (Mistral, Nebius, ElevenLabs, AIML). Keep their logic intact for now.
* Move Pydantic models into `models.py`.
* Move MemoryDB into `db.py` and export `get_db()`.

**Why:** minimal change, easy to test route-by-route.

---

## Step B — Split endpoints into routers (1–2 hours)

* `api/auth.py` — register/login.
* `api/analyze.py` — `/analyze-catch`.
* `api/match.py` — `/match`.
* `api/credit.py` — `/credit-score`.
* Each router imports `get_db()` and `services.*`.

**Why:** clarity, auto-generated docs per router.

---

## Step C — Add an orchestrator & agents (2–4 hours)

* `agents/orchestrator.py` exposes `orchestrate_analysis(request)` used as a background task. It calls:

  * `agents.matchmaker.find_matches(...)`
  * `agents.credit_scoring.update_user_score(...)`
  * `agents.notifier.notify_matches(...)`
* Agents are pure Python modules with clear function inputs/outputs (dict in, dict out). Keep them sync/async as needed.

**Why:** moves business logic out of API handlers so endpoints remain thin.

---

## Step D — Background processing (2–4 hours)

Options:

* **Quick**: Use `BackgroundTasks` from FastAPI (sufficient for low-volume).
* **Scale**: Add a queue (Redis + RQ or Celery) and a worker `tasks/queue_worker.py`.

**Why:** avoid blocking API calls (AI calls and DB storage run async/background).

---

## Step E — DB layer & migrations (4–8 hours)

* Keep `MemoryDB` for dev. Add `schemas.py` with SQLAlchemy models and `db.py` to support both modes.
* Use `asyncpg` / `databases` or `SQLAlchemy 2.0 async` + `alembic` for migrations.

**Why:** persistence and querying at scale (users, catches, audits).

---

## Step F — Add API contracts & validation (1–2 hours)

* Standardize request/response models in `models.py` and return typed Pydantic responses in endpoints.
* Add explicit error responses and status codes.

**Why:** prevents frontend render issues (React error #31 came from uncontrolled object render).

---

## Step G — Testing, logging, monitoring (2–4 hours)

* Add unit tests for `services/*` (mock external APIs), integration tests for endpoints.
* Add logging (structured), and Sentry for error monitoring.
* Ensure Render logs are structured; add health checks.

---

## Step H — Security & hardening (2–4 hours)

* Use `python-dotenv` in dev, secrets manager in Render.
* Hash passwords with `bcrypt` (passlib).
* Add rate limiting (FastAPI limiter) for endpoints that call AI.
* Validate inputs strictly (Pydantic) and limit image sizes (uploads).

---

## Step I — CI / CD + Docker (2–4 hours)

* Add `Dockerfile` and `docker-compose.yml` for local staging (DB, Redis, worker).
* Add GitHub Actions: run tests, then deploy to Render/GitHub if tests pass.

---

# 4 — Agent design (what each agent does & interfaces)

### Matchmaker agent (`agents/matchmaker.py`)

* Input: `{fish_type, quantity_kg, location, price_analysis, user_profile?}`
* Output: `[{buyer_id, contact, score, reason, estimated_price, distance_km}]`
* Logic: filter `users` by `user_type == buyer`, location proximity, buyer preferences, reliability score, required quantity.

### Credit scoring agent (`agents/credit_scoring.py`)

* Input: `user_id` or user's transaction history
* Output: `{credit_score, score_components: {repayment, frequency, income}, eligible_amount}`
* Logic: simple rule-based + ML later (aggregates transaction history).

### Notifier agent (`agents/notifier.py`)

* Input: `recipient, channel (sms/whatsapp/email), message, metadata`
* Output: `{status, message_id}`
* Integrations: Twilio, Africa's Talking, or WhatsApp API. Use ElevenLabs for voice version.

### Orchestrator (`agents/orchestrator.py`)

* API: `async def orchestrate_analysis(request)`
* Steps:

  1. call matchmaker → get matches
  2. call notifier → send notifications
  3. call credit_scoring → update user score
  4. store results in DB

**Design:** keep agents independent & testable. Use events (publish/subscribe) if you later add a message bus.

---

# 5 — Example function signatures (pasteable)

```py
# services/mistral.py
async def call_mistral_ai(context: dict) -> dict: ...

# agents/matchmaker.py
def find_matches(offer: dict, buyers: list) -> list: ...

# agents/orchestrator.py
async def orchestrate_analysis(offer: dict) -> dict: ...
```

---

# 6 — Frontend contract recommendations (avoid future bugs)

* Every endpoint should return a stable JSON shape. Example `/api/analyze-catch`:

```json
{
  "status":"success",
  "price_analysis": { "fair_price": 5200, "currency":"TZS", "confidence_score":0.8 },
  "market_insights": { "market_trend":"growing", "recommendation":"sell morning" },
  "image_analysis": { ... },
  "analysis_summary": "10 kg tilapia in Mwanza. Suggested price 5200 TZS/kg",
  "voice_message_url": "/audio/abc.mp3"
}
```

* Frontend must render `analysis_summary` (string) for single-line display and use a safe component to render objects (or `JSON.stringify`) for details.

---

# 7 — Operational: env, secrets, and keys

* Keep keys out of code. Use `.env.example` and set real secrets in Render environment variables.
* Use a secret manager if you scale (Render secrets, AWS Secrets Manager).

---

# 8 — Testing checklist (before deploy)

* Unit tests for all `services/*` (mock API responses).
* Integration tests for `api/*` routers using `httpx.AsyncClient(app=app)` to hit endpoints.
* Manual tests: register buyer + register fisher, analyze-catch, then /match should return buyers.

---

# 9 — Deployment & scaling notes

* Start with Render (you already have it). Use one web service + one background worker (if using queue).
* Move heavy AI batch jobs to Nebius or dedicated worker with higher CPU/RAM.
* For audio files, use cloud storage (S3) instead of local disk on Render.

---

# 10 — Timeline estimate for a dev (conservative)

* Scaffolding + moving code to modules + quick smoke tests: **1 day**.
* Add orchestrator + basic agents + background tasks: **1–2 days**.
* DB migration and Postgres switch: **1–2 days**.
* Tests + CI/CD + deploy pipeline: **1 day**.
  (You can do a working modular demo in a day; production hardening takes longer.)

---

# 11 — Immediate next actions I recommend you run now

1. Create `app/` folder and copy your `main.py` logic into `services/*`, `api/*`, `models.py`, `db.py` as above.
2. Add a thin `main.py` that includes routers and runs the app.
3. Wire `agents/orchestrator` as a background task for `/analyze-catch`.
4. Update frontend to use `analysis_summary` for display and call `/api/match`.
5. Run local tests and register at least one buyer user; then trigger `/match`.

---

# 12 — Example git-friendly checklist (what to commit first)

* `app/main.py` (thin entry)
* `app/models.py` (pydantic)
* `app/db.py` (MemoryDB)
* `app/services/*` (mistral, nebius, aiml, elevenlabs)
* `app/api/*` (auth, analyze, match)
* `requirements.txt`, `.env.example`, `README.md`

Commit these, push, test on Render.

---

If you want I can do one of the following *right now* (pick one):

* Provide the **exact file contents** for the new `app/main.py`, `app/models.py`, `app/db.py`, `app/api/analyze.py` and `app/agents/orchestrator.py` (ready-to-paste).
* Create a **git patch/diff** that converts your current `main.py` into the modular layout.
* Generate the **worker + queue** skeleton (Redis + RQ) to run orchestrator tasks asynchronously.

Tell me which of those you want and I’ll produce the files/code instantly.





About postgres 

Perfect — going with **PostgreSQL** is a solid decision ✅.
It’s scalable, reliable, and integrates beautifully with **FastAPI** and **Render** (and even Supabase if you ever expand later).

Let’s go step-by-step so you understand both the **setup** and the **best structure** for your app.

---

## 🧩 1. Why PostgreSQL for SamakiCash

PostgreSQL gives you:

* **Reliability** — ACID-compliant and robust for financial/fish market data.
* **JSONB support** — great for flexible AI analysis results (price analysis, images, etc.).
* **Scalability** — handles your matchmaking and analytics workloads.
* **Easy integration** with Render and FastAPI using async libraries like `asyncpg` or `SQLAlchemy`.

---

## ⚙️ 2. Set up PostgreSQL on Render

You already have your backend on Render, so do this:

### ➤ Step 1: Create a PostgreSQL database

1. Go to your **Render dashboard**
2. Click **New + → PostgreSQL**
3. Choose **Free plan** (for now)
4. Wait until the database is provisioned.

You’ll get:

* **Database URL** (looks like this):
  `postgres://username:password@host:5432/dbname`
* Copy it — we’ll need it soon.

---

## 📁 3. Update Your Project Structure

Let’s move away from one giant `main.py` and make a **modular FastAPI app** with clean architecture.

```
samakicash-backend/
│
├── app/
│   ├── main.py               # entry point (FastAPI instance)
│   ├── core/
│   │   ├── config.py         # settings (Render environment vars)
│   │   └── database.py       # async connection setup
│   │
│   ├── models/
│   │   ├── user.py           # User model (with user_type)
│   │   ├── catch.py          # Fish catch, analysis, etc.
│   │   └── match.py          # Buyer/Seller matching model
│   │
│   ├── routes/
│   │   ├── auth.py           # signup/login routes
│   │   ├── catch.py          # analyze-catch endpoints
│   │   ├── match.py          # buyer/seller matchmaking
│   │   └── ai_agents.py      # calls to Mistral, ElevenLabs, Nebius, etc.
│   │
│   ├── services/
│   │   ├── ai_service.py     # AI integrations (Mistral, etc.)
│   │   ├── match_service.py  # matching logic
│   │   └── audio_service.py  # ElevenLabs voice logic
│   │
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── catch_schema.py
│   │   └── match_schema.py
│   │
│   ├── utils/
│   │   └── helpers.py
│   │
│   └── __init__.py
│
├── requirements.txt
├── .env
└── README.md
```

---

## 🧠 4. Database Configuration (database.py)

```python
# app/core/database.py
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)
```

If you want to use **SQLAlchemy** (recommended for scaling later):

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 🔑 5. Environment Variables (.env)

In Render’s **Environment settings**, add:

```
DATABASE_URL=postgres://user:password@hostname:5432/dbname
ELEVENLABS_API_KEY=your_key
MISTRAL_API_KEY=your_key
AIML_API_KEY=your_key
NEBIUS_API_KEY=your_key
```

Never hardcode keys — always load them via environment variables.

---

## 🧩 6. Add Your User Model (user.py)

```python
from sqlalchemy import Column, String, Enum
from app.core.database import Base
import enum

class UserType(enum.Enum):
    FISHER = "fisher"
    SELLER = "seller"
    BUYER = "buyer"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), default=UserType.FISHER)
    name = Column(String)
    phone = Column(String)
    organization = Column(String)
    location = Column(String)
```

---

## ⚙️ 7. Migrations (optional but professional)

Use **Alembic** for migrations:

```bash
pip install alembic
alembic init migrations
```

Then configure it to point to your async DB URL and run:

```bash
alembic revision --autogenerate -m "create users and catches"
alembic upgrade head
```

---

## 🔁 8. Linking Everything in main.py

```python
from fastapi import FastAPI
from app.routes import auth, catch, match

app = FastAPI(title="SamakiCash API")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(catch.router, prefix="/api/catch", tags=["Catch Analysis"])
app.include_router(match.router, prefix="/api/match", tags=["Buyer-Seller Matching"])
```

---

## 🧠 9. Agents Layer (AI Integration)

You’ll have separate service files for:

* **ai_service.py** → Mistral, AIML, Nebius
* **audio_service.py** → ElevenLabs
* **match_service.py** → Smart logic to pair sellers and buyers based on location, price, quantity, etc.

---

## ✅ 10. Testing locally

After setting the `.env`:

```bash
uvicorn app.main:app --reload
```

Test via:

* `http://localhost:8000/docs`
* Postman or browser

---

Would you like me to generate the **initial folder with base files** (like models, schemas, and routes with the right imports and structure) — so you can copy-paste it directly into your Render backend and just add your credentials?
That would make this step 100× faster.
