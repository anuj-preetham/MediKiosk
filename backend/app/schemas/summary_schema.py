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

class DifferentialDiagnosisItem(BaseModel):
    condition: str
    icd10_code: Optional[str] = None
    snomed_ct: Optional[str] = None
    confidence_score: int # e.g. 85 for 85%
    clinical_rationale: str
    urgency: str # "Routine" | "Priority" | "High"

class ClinicalRiskScore(BaseModel):
    category: str # e.g. "Cardiovascular", "GI Bleed", "Metabolic"
    risk_level: str # "Low" | "Moderate" | "Elevated" | "High"
    score_note: str

class SOAPDraft(BaseModel):
    subjective: str
    objective: str
    assessment: str
    plan: str

class AICopilotAnalysis(BaseModel):
    clinical_impression: str
    differential_diagnoses: List[DifferentialDiagnosisItem] = []
    clinical_risk_scores: List[ClinicalRiskScore] = []
    suggested_investigations: List[str] = []
    suggested_lifestyle_advice: List[str] = []
    soap_draft: SOAPDraft
    engine_model: str = "Gemini 2.5 Flash Clinical Engine"

class AICopilotQueryRequest(BaseModel):
    doctor_query: str

class AICopilotQueryResponse(BaseModel):
    query: str
    ai_response: str
    clinical_context_used: List[str] = []
    suggested_follow_up: List[str] = []
    engine_model: str = "Gemini 2.5 Flash Clinical Copilot"

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

    # 5. Clinical Safety & Cross-Checks
    safety_alerts: List[Dict[str, Any]] = []
    
    # 6. AI Clinical Copilot & Differential Diagnoses
    ai_copilot_analysis: Optional[AICopilotAnalysis] = None

    # 7. Review & Status
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
