from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PatientCreate(BaseModel):
    full_name: str
    age: int
    gender: str
    phone_number: Optional[str] = None
    preferred_language: str = "en"
    abha_id: Optional[str] = None
    consent_granted: bool = True
    consent_audio_verified: bool = False

class PatientResponse(BaseModel):
    id: str
    full_name: str
    age: int
    gender: str
    phone_number: Optional[str]
    preferred_language: str
    abha_id: Optional[str]
    consent_granted: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    patient_id: Optional[str] = None
    patient_data: Optional[PatientCreate] = None
    language: str = "en"

class SessionResponse(BaseModel):
    id: str
    patient_id: str
    status: str
    triage_level: str
    red_flag_detected: Optional[str] = None
    language: str
    created_at: datetime
    patient: Optional[PatientResponse] = None

    class Config:
        from_attributes = True

class SessionDetailResponse(SessionResponse):
    chat_history: List[Dict[str, Any]] = []
    clinical_history: Optional[Dict[str, Any]] = None
    ayush_assessment: Optional[Dict[str, Any]] = None
    documents: List[Dict[str, Any]] = []
    physician_review: Optional[Dict[str, Any]] = None
