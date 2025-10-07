from fastapi import APIRouter
from typing import Dict, Any
from app.core.database import get_db

router = APIRouter()

@router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str) -> Dict[str, Any]:
    conn = await get_db()
    catches = await conn.fetch("SELECT * FROM catches WHERE user_id = $1", user_id)
    total_catches = len(catches)
    total_qty = sum(float(c.get("quantity_kg", 0)) for c in catches)
    prices = [float(c.get("price_analysis", {}).get("fair_price", 0)) for c in catches if isinstance(c.get("price_analysis"), dict)]
    avg_price = round(sum(prices) / len(prices), 2) if prices else 0
    return {
        "user_id": user_id,
        "total_catches": total_catches,
        "total_quantity_kg": total_qty,
        "average_price_per_kg": avg_price,
    }

@router.get("/users/{user_id}/catches")
async def get_user_catches(user_id: str) -> Dict[str, Any]:
    conn = await get_db()
    catches = await conn.fetch("SELECT * FROM catches WHERE user_id = $1", user_id)
    return {"user_id": user_id, "count": len(catches), "catches": catches}

@router.get("/users/{user_id}/transactions")
async def get_user_transactions(user_id: str) -> Dict[str, Any]:
    conn = await get_db()
    # MemoryDB fallback: returns empty unless transactions were added
    try:
        txs = await conn.fetch("SELECT * FROM transactions WHERE user_id = $1", user_id)
    except Exception:
        txs = []
    return {"user_id": user_id, "count": len(txs), "transactions": txs}

@router.get("/users/{user_id}/market-insights")
async def get_user_market_insights(user_id: str) -> Dict[str, Any]:
    # For now, summarize from catches' price_analysis
    conn = await get_db()
    catches = await conn.fetch("SELECT * FROM catches WHERE user_id = $1", user_id)
    fish_types = {}
    for c in catches:
        ft = c.get("fish_type")
        if ft:
            fish_types[ft] = fish_types.get(ft, 0) + 1
    top_fish = sorted(fish_types.items(), key=lambda x: x[1], reverse=True)
    return {
        "user_id": user_id,
        "top_fish_types": top_fish,
        "insight": "Increase supply during morning hours for better prices"
    }
