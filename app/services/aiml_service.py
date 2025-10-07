import os
import requests
from typing import Dict, Any
from app.core.config import settings

async def call_aiml_api(context: Dict[str, Any]) -> Dict[str, Any]:
    """Call AI/ML API for market insights"""
    api_key = settings.AIML_API_KEY
    
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
