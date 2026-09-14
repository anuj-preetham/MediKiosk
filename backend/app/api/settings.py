import os
import time
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class AIConfigRequest(BaseModel):
    gemini_api_key: str
    model_name: Optional[str] = "gemini-2.5-flash"

class TestConnectionRequest(BaseModel):
    gemini_api_key: Optional[str] = None

@router.get("/ai-status")
def get_ai_status():
    """
    Get current AI configuration status, active model, and whether an API key is present.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "")
    has_key = bool(api_key and len(api_key.strip()) > 5)
    
    masked_key = ""
    if has_key:
        clean_key = api_key.strip()
        if len(clean_key) > 8:
            masked_key = f"{clean_key[:4]}...{clean_key[-4:]}"
        else:
            masked_key = "********"

    return {
        "status": "CONFIGURED" if has_key else "UNCONFIGURED",
        "is_configured": has_key,
        "has_api_key": has_key,
        "masked_key": masked_key,
        "active_model": "gemini-2.5-flash",
        "models_supported": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        "engine_mode": "Live Google Gemini 2.5 Flash" if has_key else "Offline Clinical Knowledge Engine (Deterministic Fallback)"
    }

@router.post("/ai-config")
def update_ai_config(payload: AIConfigRequest):
    """
    Update the active Gemini API key at runtime and save it to backend/.env.
    """
    key = payload.gemini_api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="Gemini API key cannot be empty.")

    # 1. Update runtime environment and settings
    os.environ["GEMINI_API_KEY"] = key
    settings.GEMINI_API_KEY = key

    # 2. Persist to backend/.env safely
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    try:
        env_lines = []
        key_found = False
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        env_lines.append(f"GEMINI_API_KEY={key}\n")
                        key_found = True
                    else:
                        env_lines.append(line)
        if not key_found:
            env_lines.append(f"GEMINI_API_KEY={key}\n")

        with open(env_path, "w") as f:
            f.writelines(env_lines)
    except Exception as e:
        logger.warning(f"Could not persist GEMINI_API_KEY to {env_path}: {e}")

    masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "********"
    return {
        "status": "SUCCESS",
        "is_configured": True,
        "has_api_key": True,
        "masked_key": masked,
        "message": "Gemini API key successfully configured and activated.",
        "active_model": "gemini-2.5-flash"
    }

@router.post("/test-gemini")
def test_gemini_connection(payload: TestConnectionRequest):
    """
    Test live connectivity and latency with Google Gemini API.
    """
    test_key = (payload.gemini_api_key or "").strip() or os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "")
    if not test_key:
        raise HTTPException(
            status_code=400,
            detail="No Gemini API Key provided to test. Please enter a key or configure it in Settings."
        )

    start_time = time.time()
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=test_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Respond in exactly 3 words: 'MediKiosk AI Connected'",
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=20
            )
        )
        latency_ms = int((time.time() - start_time) * 1000)
        reply_text = response.text.strip() if response.text else "Connected"

        return {
            "status": "CONNECTED",
            "model": "gemini-2.5-flash",
            "latency_ms": latency_ms,
            "response_sample": reply_text,
            "message": f"Successfully connected to Google Gemini 2.5 Flash ({latency_ms}ms latency)."
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Gemini test connection failed: {e}")
        return {
            "status": "ERROR",
            "model": "gemini-2.5-flash",
            "latency_ms": latency_ms,
            "error_detail": str(e),
            "message": f"Failed to connect to Gemini API: {str(e)}"
        }
