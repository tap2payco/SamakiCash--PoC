import json
import uuid
from datetime import datetime
from typing import Dict, Any
from app.core.database import get_db
from app.services import call_mistral_ai, call_aiml_api, call_nebius_ai, call_elevenlabs
from app.agents.matchmaker import find_matches
from app.agents.credit_scoring import calculate_credit_score
from app.agents.notifier import send_notification

async def orchestrate_analysis(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrate the complete analysis workflow:
    1. Call AI services for analysis
    2. Find potential matches
    3. Update credit score
    4. Send notifications
    5. Store results
    """
    try:
        # 1. Price analysis (Mistral)
        try:
            price_analysis = await call_mistral_ai(request)
            if not isinstance(price_analysis, dict):
                raise ValueError("Mistral returned unexpected format")
        except Exception as e:
            print(f"[orchestrator] Mistral AI failed: {e}")
            price_analysis = {
                "fair_price": 0,
                "currency": "TZS",
                "reasoning": "fallback price due to AI error",
                "confidence_score": 0.0
            }

        # 2. Market insights (AI/ML API)
        try:
            market_insights = await call_aiml_api(request)
            if isinstance(market_insights, dict):
                market_trend = market_insights.get("market_trend") or market_insights.get("market_trend_major", "stable")
            else:
                market_trend = str(market_insights)
                market_insights = {"market_trend": market_trend}
        except Exception as e:
            print(f"[orchestrator] AI/ML API failed: {e}")
            market_insights = {"market_trend": "stable", "recommendation": "Sell in the morning for best price"}

        # 3. Image analysis (Nebius) - optional
        try:
            image_analysis = await call_nebius_ai(request.get('image_data')) if request.get('image_data') else {"analysis": "no image provided"}
            if not isinstance(image_analysis, dict):
                image_analysis = {"analysis": str(image_analysis)}
        except Exception as e:
            print(f"[orchestrator] Nebius AI failed: {e}")
            image_analysis = {"analysis": "image analysis failed", "confidence": 0.0}

        # 4. Voice generation (ElevenLabs) - optional
        try:
            voice_filename = await call_elevenlabs(price_analysis, market_insights)
            if not voice_filename or voice_filename in ("voice_generation_failed", "voice_generation_timeout", "voice_generation_skipped", "voice_connection_error"):
                voice_filename = None
        except Exception as e:
            print(f"[orchestrator] ElevenLabs failed: {e}")
            voice_filename = None

        # 5. Find matches
        try:
            matches = await find_matches(request, price_analysis, market_insights)
        except Exception as e:
            print(f"[orchestrator] Matchmaking failed: {e}")
            matches = []

        # 6. Update credit score
        try:
            credit_info = await calculate_credit_score(request.get('user_id'))
        except Exception as e:
            print(f"[orchestrator] Credit scoring failed: {e}")
            credit_info = {"credit_score": 700, "loan_eligible": True}

        # 7. Store catch record
        try:
            await store_catch_record(request, price_analysis, market_insights, image_analysis, voice_filename)
        except Exception as e:
            print(f"[orchestrator] Database storage failed: {e}")

        # 8. Send notifications (if matches found)
        if matches:
            try:
                await send_notification(request.get('user_id'), matches, price_analysis)
            except Exception as e:
                print(f"[orchestrator] Notification failed: {e}")

        # 9. Build summary
        try:
            suggested_price = price_analysis.get("fair_price", "N/A")
            currency = price_analysis.get("currency", "TZS")
            market_trend_text = market_insights.get("market_trend") if isinstance(market_insights, dict) else str(market_insights)
            summary = (
                f"{request.get('quantity_kg', 0)} kg of {request.get('fish_type', 'fish')} in {request.get('location', 'unknown')}. "
                f"Suggested price: {suggested_price} {currency}/kg. "
                f"Market trend: {market_trend_text}."
            )
        except Exception as e:
            print(f"[orchestrator] Summary build failed: {e}")
            summary = f"{request.get('quantity_kg', 0)} kg of {request.get('fish_type', 'fish')} in {request.get('location', 'unknown')}. Price unavailable."

        return {
            "status": "success",
            "price_analysis": price_analysis,
            "market_insights": market_insights,
            "image_analysis": image_analysis,
            "voice_message_url": f"/audio/{voice_filename}" if voice_filename else None,
            "analysis_summary": summary,
            "matches": matches,
            "credit_info": credit_info,
            "recommendation": f"Suggested price: TZS {suggested_price} per kg" if suggested_price != "N/A" else "No price recommendation"
        }

    except Exception as e:
        print(f"[orchestrator] Fatal error: {e}")
        return {
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        }

async def store_catch_record(request: Dict[str, Any], price_analysis: Dict, market_insights: Dict, image_analysis: Dict, voice_filename: str):
    """Store catch record in database"""
    try:
        conn = await get_db()
        catch_id = str(uuid.uuid4())
        
        await conn.execute(
            """INSERT INTO catches (id, user_id, fish_type, quantity_kg, location, price_analysis, created_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7)""",
            catch_id, request.get('user_id'), request.get('fish_type'), request.get('quantity_kg'), 
            request.get('location'), json.dumps(price_analysis), datetime.now()
        )
    except Exception as e:
        print(f"Database storage error: {e}")
