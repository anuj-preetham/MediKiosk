from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatMessageRequest(BaseModel):
    message: str
    mode: str = "general" # 'general' | 'socrates' | 'lifestyle'
    step: Optional[str] = None # 'chief_complaint' | 'site' | 'onset' | 'character' | 'radiation' | 'associated' | 'timing' | 'exacerbating' | 'severity'
    body_location: Optional[str] = None

class QuickOption(BaseModel):
    label: str
    value: str
    icon: Optional[str] = None

class ChatMessageResponse(BaseModel):
    ai_reply: str
    ai_reply_audio_text: str
    language: str
    current_step: str
    next_step: Optional[str] = None
    quick_options: List[QuickOption] = []
    
    # Red Flag Warning
    is_red_flag: bool = False
    red_flag_alert_title: Optional[str] = None
    red_flag_instructions: Optional[str] = None
    
    # Extracted data updates
    extracted_socrates: Optional[Dict[str, Any]] = None
    progress_percentage: int = 0

class SOCRATESUpdateRequest(BaseModel):
    chief_complaint: Optional[str] = None
    site: Optional[str] = None
    onset: Optional[str] = None
    character: Optional[str] = None
    radiation: Optional[str] = None
    associated_symptoms: Optional[str] = None
    timing_duration: Optional[str] = None
    exacerbating_relieving: Optional[str] = None
    severity: Optional[str] = None
