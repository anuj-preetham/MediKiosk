from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TimelineEvent(BaseModel):
    date: Optional[str] = None
    event_type: str # "prescription", "lab_report", "symptom_onset", "procedure"
    title: str
    description: str
    source_document_id: Optional[str] = None
    highlights: List[str] = []

class ClinicalSummaryResponse(BaseModel):
    session_id: str
    patient_name: str
    patient_age: int
    patient_gender: str
    abha_id: Optional[str] = None
    triage_level: str
    red_flag_alert: Optional[str] = None
    
    # 1. Chief Complaint & HPI
    chief_complaint: Optional[str] = None
    socrates_hpi: Dict[str, Any] = {}
    
    # 2. Medical & Drug History
    past_medical_history: List[str] = []
    past_surgical_history: List[str] = []
    current_medications: List[Dict[str, Any]] = []
    drug_allergies: List[str] = []
    family_history: List[str] = []
    
    # 3. Personal History & Review of Systems
    personal_history: Dict[str, Any] = {}
    review_of_systems: Dict[str, Any] = {}
    
    # 4. Document Intelligence & Timeline
    abnormal_lab_highlights: List[Dict[str, Any]] = []
    chronological_timeline: List[TimelineEvent] = []
    
    # 5. Review & Status
    is_verified: bool = False
    physician_notes: Optional[str] = None

class PhysicianReviewRequest(BaseModel):
    doctor_id: str
    doctor_name: str
    department: Optional[str] = "General Medicine / OPD"
    verified_chief_complaint: Optional[str] = None
    verified_hpi: Optional[str] = None
    verified_past_history: Optional[List[str]] = None
    physician_clinical_notes: Optional[str] = None
    prescribed_plan: Optional[str] = None
    is_verified: bool = True
    is_rejected: bool = False
    rejection_reason: Optional[str] = None

class PhysicianReviewResponse(BaseModel):
    session_id: str
    doctor_name: str
    is_verified: bool
    reviewed_at: Optional[datetime] = None
    message: str

class FHIRBundleResponse(BaseModel):
    resourceType: str = "Bundle"
    type: str = "document"
    id: str
    timestamp: str
    entry: List[Dict[str, Any]] = []
