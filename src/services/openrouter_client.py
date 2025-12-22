"""Client for OpenRouter.ai API (Google Gemini 2.0 Flash Lite for speech-to-text)."""
import base64
import httpx
from typing import Optional
from src.config import settings


async def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
    """
    Transcribe audio to text using OpenRouter.ai with Google Gemini 2.0 Flash Lite.
    
    Args:
        audio_bytes: Raw audio file bytes
        mime_type: MIME type of the audio (e.g., audio/webm, audio/wav, audio/mpeg)
    
    Returns:
        Transcribed text string
    
    Raises:
        ValueError: If API key is not configured
        httpx.HTTPError: If API request fails
    """
    if not settings.openrouter_api_key:
        raise ValueError("OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.")
    
    # Convert audio to base64
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    # Create data URI
    data_uri = f"data:{mime_type};base64,{audio_base64}"
    
    # Prepare request payload
    # OpenRouter uses OpenAI-compatible format
    # For Gemini models with audio, we use the multimodal content format
    # Gemini accepts audio in the same format as images (data URI in content array)
    payload = {
        "model": "google/gemini-2.0-flash-lite-001",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe this audio to text. Return only the transcribed text without any additional commentary."
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": data_uri
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,  # Lower temperature for more accurate transcription
        "max_tokens": 1000
    }
    
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://image-stand.local",  # Optional but recommended
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        
        if response.status_code != 200:
            error_text = response.text
            try:
                error_json = response.json()
                error_msg = error_json.get("error", {}).get("message", error_text)
            except:
                error_msg = error_text
            raise httpx.HTTPError(
                f"OpenRouter API error (HTTP {response.status_code}): {error_msg}",
                request=response.request,
                response=response,
            )
        
        data = response.json()
        
        # Extract transcription from response
        # OpenRouter returns OpenAI-compatible format
        if "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")
            return content.strip()
        else:
            raise ValueError(f"Unexpected response format: {data}")

