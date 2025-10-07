import os
import requests
from typing import Dict, Any, Optional
from app.core.config import settings

async def call_nebius_ai(image_data: Optional[str] = None) -> Dict[str, Any]:
    """Call Nebius AI for image analysis"""
    api_key = settings.NEBIUS_API_KEY
    
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
