# SamakiCash Backend

## Overview

**SamakiCash Backend** is the server-side component of the SamakiCash MVP, built with FastAPI. It provides AI-powered fish market analysis, buyer-seller matchmaking, and financial services for Tanzania's fishing industry.

---

## Tech Stack

- **Framework:** FastAPI (Python)
- **ASGI Server:** Uvicorn
- **Database:** PostgreSQL (via asyncpg) with MemoryDB fallback
- **AI Services:** Mistral AI, ElevenLabs, Nebius AI, AIML API
- **Environment Management:** python-dotenv
- **File Uploads:** python-multipart, aiofiles

---

## Features

- 🐟 **Fish Catch Analysis**: AI-powered price analysis and market insights
- 🤝 **Smart Matchmaking**: Connect fishers with potential buyers
- 💰 **Financial Services**: Credit scoring, loans, and insurance quotes
- 🎵 **Voice Generation**: Swahili audio summaries via ElevenLabs
- 📊 **Market Intelligence**: Real-time fish market trends and recommendations
- 🔐 **User Management**: Multi-role system (fishers, sellers, buyers)

---

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
   cd samakicash-mvp
   ```

2. **Create a virtual environment and activate it:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**  
   Create a `.env` file in the root directory and add your configuration (e.g., database URL).

5. **Run the server:**
   ```sh
   # Development (uses memory database)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Production (with PostgreSQL)
   export DATABASE_URL="postgres://user:pass@host:5432/db"
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## API Documentation

- **Interactive Docs**: Visit `http://localhost:8000/docs` when running locally
- **Frontend Integration**: See `FRONTEND_INTEGRATION_GUIDE.md` for detailed API usage
- **Migration Guide**: See `README_MIGRATION.md` for the new modular structure

---

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── core/               # Configuration & database
├── models/             # Pydantic models
├── api/                # API route handlers
├── services/           # AI service integrations
├── agents/             # AI agent modules
└── schemas/            # Database schemas
```

---

## Deployment

- Deployable on [Render](https://render.com/) or similar platforms
- Set environment variables and database configuration in your deployment dashboard
- See `env.example` for required environment variables

---

## License

MIT License

---

## Author

- [Your Name](https://github.com/YOUR-USERNAME)