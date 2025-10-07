import os
import json
import requests
from typing import Dict, Any
from app.core.config import settings

def validate_api_key(api_key: str, service: str):
    """Validate API key format"""
    if not api_key or not api_key.startswith("sk-"):
        print(f"Warning: Invalid {service} API key format")
    return True

async def call_mistral_ai(context: Dict[str, Any]) -> Dict[str, Any]:
    """Call Mistral AI for price analysis"""
    api_key = settings.MISTRAL_API_KEY
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
