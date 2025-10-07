from typing import Dict, Any, List
from app.core.database import get_db

async def find_matches(offer: Dict[str, Any], price_analysis: Dict[str, Any], market_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find potential buyers for a fish catch offer
    
    Args:
        offer: Fish catch details (fish_type, quantity_kg, location, user_id)
        price_analysis: Price analysis from Mistral AI
        market_insights: Market insights from AI/ML API
    
    Returns:
        List of potential buyer matches with scores and details
    """
    try:
        conn = await get_db()
        
        # Get all users and filter for buyers
        all_users = await conn.fetch("SELECT * FROM users")
        buyers = [u for u in all_users if u.get("user_type") == "buyer"]
        
        # Build match scoring & results
        matches = []
        for buyer in buyers:
            # Simple heuristic: base score on Mistral confidence + random factor
            confidence = float(price_analysis.get("confidence_score", 0)) if price_analysis else 0.5
            score = int(min(max(30 + confidence * 60, 0), 100))
            
            matches.append({
                "buyer_id": buyer.get("id"),
                "buyer_contact": buyer.get("email"),
                "buyer_name": buyer.get("name", "Unknown"),
                "buyer_organization": buyer.get("organization", ""),
                "buyer_location": buyer.get("location", ""),
                "match_score": score,
                "estimated_price_per_kg": price_analysis.get("fair_price"),
                "estimated_total_value": round(price_analysis.get("fair_price", 0) * offer.get('quantity_kg', 0), 2),
                "reason": f"High demand for {offer.get('fish_type', 'fish')} in {offer.get('location', 'area')}",
                "note": "Simulated match (use buyer preferences in production)"
            })
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches[:10]  # Return top 10 matches
        
    except Exception as e:
        print(f"Matchmaking error: {e}")
        return []
