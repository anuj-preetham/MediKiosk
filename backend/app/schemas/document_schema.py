from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class AbnormalFlagItem(BaseModel):
    parameter: str
    value: str
    ref_range: Optional[str] = None
    severity: str = "high" # "high" | "critical" | "borderline"
    clinical_note: Optional[str] = None

class DocumentEntityResponse(BaseModel):
    diagnoses: List[str] = []
    medicines: List[Dict[str, Any]] = []
    investigations: List[Dict[str, Any]] = []
    vital_signs: Dict[str, Any] = {}
    procedures: List[str] = []

class DocumentResponse(BaseModel):
    id: str
    session_id: str
    file_name: str
    file_path: str
    document_type: str
    document_date: Optional[date] = None
    doctor_or_lab_name: Optional[str] = None
    ocr_raw_text: Optional[str] = None
    extracted_entities: DocumentEntityResponse
    abnormal_flags: List[AbnormalFlagItem] = []
    created_at: datetime

    class Config:
        from_attributes = True
