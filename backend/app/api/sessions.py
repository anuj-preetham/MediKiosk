import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.patient import Patient
from app.models.session import IntakeSession, SessionStatus, TriageLevel
from app.models.clinical_history import ClinicalHistory
from app.models.review import PhysicianReview
from app.schemas.session_schema import (
    PatientCreate, PatientResponse,
    SessionCreate, SessionResponse,
    SessionDetailResponse
)

router = APIRouter()

@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def start_intake_session(payload: SessionCreate, db: Session = Depends(get_db)):
    """
    Initialize a new patient intake session with consent and preferred language.
    """
    now = datetime.now(timezone.utc)
    patient = None
    if payload.patient_id:
        patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
    elif payload.patient_data:
        p_data = payload.patient_data
        patient = Patient(
            id=str(uuid.uuid4()),
            abha_id=p_data.abha_id or f"91-{p_data.phone_number or '9876543210'}@abdm",
            full_name=p_data.full_name,
            age=p_data.age,
            gender=p_data.gender,
            phone_number=p_data.phone_number,
            preferred_language=payload.language or p_data.preferred_language,
            consent_granted=p_data.consent_granted,
            consent_audio_verified=p_data.consent_audio_verified,
            consent_timestamp=now
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    else:
        # Default walk-in anonymous patient profile for quick kiosk start
        patient = Patient(
            id=str(uuid.uuid4()),
            abha_id="91-9876543210@abdm",
            full_name="OPD Walk-in Patient",
            age=35,
            gender="Male",
            preferred_language=payload.language,
            consent_granted=True,
            consent_audio_verified=True,
            consent_timestamp=now
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # Create Intake Session
    session = IntakeSession(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        status=SessionStatus.IN_PROGRESS.value,
        triage_level=TriageLevel.ROUTINE.value,
        language=payload.language,
        chat_history=[]
    )
    db.add(session)

    # Initialize associated record shells
    clinical_history = ClinicalHistory(
        id=str(uuid.uuid4()),
        session_id=session.id,
        socrates_hpi={},
        past_medical_history=[],
        past_surgical_history=[],
        current_medications=[],
        drug_allergies=[],
        family_history=[],
        personal_history={"diet": "Normal balanced", "smoking": "No", "alcohol": "No", "sleep": "7-8 hours"},
        review_of_systems={}
    )
    db.add(clinical_history)

    db.commit()
    db.refresh(session)
    return session

@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session_details(session_id: str, db: Session = Depends(get_db)):
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "patient_id": session.patient_id,
        "status": session.status,
        "triage_level": session.triage_level,
        "red_flag_detected": session.red_flag_detected,
        "language": session.language,
        "created_at": session.created_at,
        "patient": session.patient,
        "chat_history": session.chat_history or [],
        "clinical_history": {
            "chief_complaint": session.clinical_history.chief_complaint if session.clinical_history else None,
            "socrates_hpi": session.clinical_history.socrates_hpi if session.clinical_history else {},
            "past_medical_history": session.clinical_history.past_medical_history if session.clinical_history else [],
            "past_surgical_history": session.clinical_history.past_surgical_history if session.clinical_history else [],
            "current_medications": session.clinical_history.current_medications if session.clinical_history else [],
            "drug_allergies": session.clinical_history.drug_allergies if session.clinical_history else [],
            "family_history": session.clinical_history.family_history if session.clinical_history else [],
            "personal_history": session.clinical_history.personal_history if session.clinical_history else {}
        } if session.clinical_history else None,
        "documents": [
            {
                "id": doc.id,
                "file_name": doc.file_name,
                "document_type": doc.document_type,
                "document_date": str(doc.document_date) if doc.document_date else None,
                "extracted_entities": doc.extracted_entities or {},
                "abnormal_flags": doc.abnormal_flags or []
            }
            for doc in session.documents
        ]
    }

@router.post("/{session_id}/complete")
def complete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != SessionStatus.TRIAGED_RED_FLAG.value:
        session.status = SessionStatus.COMPLETED.value
    db.commit()
    return {"message": "Intake completed successfully and submitted to physician OPD queue."}
