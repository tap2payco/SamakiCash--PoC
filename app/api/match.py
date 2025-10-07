from fastapi import APIRouter
from app.models import MatchRequest
from app.agents.matchmaker import find_matches
from app.services import call_mistral_ai, call_aiml_api

router = APIRouter()

@router.post("/match")
async def make_match(request: MatchRequest):
    """
    Simple matchmaking: uses price/demand analysis then returns candidate buyers.
    To match real buyers you must register buyer accounts (user_type='buyer').
    """
    try:
        # 1) Get price + market insights using AI services
        price_analysis = await call_mistral_ai(request.dict())
        market_insights = await call_aiml_api(request.dict())

        # 2) Find matches using the matchmaker agent
        matches = await find_matches(request.dict(), price_analysis, market_insights)

        # 3) Provide a short string summary (safe to render directly in UI)
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
