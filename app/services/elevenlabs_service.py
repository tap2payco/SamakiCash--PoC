import os
import uuid
import requests
from typing import Dict, Any
from app.core.config import settings

async def call_elevenlabs(price_data: Dict[str, Any], market_data: Dict[str, Any]) -> str:
    """Generate voice message using ElevenLabs"""
    api_key = settings.ELEVENLABS_API_KEY
    
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
