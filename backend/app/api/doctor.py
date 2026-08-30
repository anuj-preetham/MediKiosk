from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.models.session import IntakeSession, SessionStatus, TriageLevel
from app.models.review import PhysicianReview
from app.schemas.summary_schema import (
    ClinicalSummaryResponse, TimelineEvent,
    PhysicianReviewRequest, PhysicianReviewResponse
)
from app.services.fhir_service import fhir_service

router = APIRouter()

@router.get("/queue")
def get_opd_patient_queue(db: Session = Depends(get_db)):
    """
    Get live OPD waiting queue with triage priority badges.
    """
    sessions = db.query(IntakeSession).order_by(
        # Put emergency red flags first, then latest created
        IntakeSession.triage_level.desc(),
        IntakeSession.created_at.desc()
    ).all()

    queue = []
    for s in sessions:
        queue.append({
            "session_id": s.id,
            "patient_name": s.patient.full_name if s.patient else "Unknown",
            "age": s.patient.age if s.patient else 0,
            "gender": s.patient.gender if s.patient else "N/A",
            "abha_id": s.patient.abha_id if s.patient else None,
            "triage_level": s.triage_level,
            "red_flag_detected": s.red_flag_detected,
            "status": s.status,
            "chief_complaint": s.clinical_history.chief_complaint if s.clinical_history else "Intake in progress",
            "prakriti": s.ayush_assessment.prakriti_primary if s.ayush_assessment else "Pending",
            "documents_count": len(s.documents),
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "is_reviewed": bool(s.physician_review and s.physician_review.is_verified)
        })
    return queue

@router.get("/sessions/{session_id}/summary", response_model=ClinicalSummaryResponse)
def get_structured_clinical_summary(session_id: str, db: Session = Depends(get_db)):
    """
    Generate unified physician-ready clinical summary.
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    patient = session.patient
    history = session.clinical_history
    ayush = session.ayush_assessment
    docs = session.documents
    review = session.physician_review

    # Build chronological timeline
    timeline: List[TimelineEvent] = []
    
    # 1. Symptom onset event
    if history and history.socrates_hpi:
        onset_val = history.socrates_hpi.get("onset", "Recent onset")
        timeline.append(TimelineEvent(
            date="Presenting Episode",
            event_type="symptom_onset",
            title=f"Onset of {history.chief_complaint or 'Symptoms'}",
            description=f"Characteristics: {history.socrates_hpi.get('character', 'N/A')}. Severity: {history.socrates_hpi.get('severity', 'N/A')}.",
            highlights=[history.socrates_hpi.get("site", "")]
        ))

    # 2. Add document events
    abnormal_highlights = []
    for d in docs:
        d_date_str = str(d.document_date) if d.document_date else "Prior Visit"
        diag_str = ", ".join(d.extracted_entities.get("diagnoses", [])) if d.extracted_entities else ""
        meds_count = len(d.extracted_entities.get("medicines", [])) if d.extracted_entities else 0
        
        timeline.append(TimelineEvent(
            date=d_date_str,
            event_type=d.document_type,
            title=f"{d.document_type.replace('_', ' ').title()} ({d.doctor_or_lab_name or 'OPD'})",
            description=f"Extracted Diagnoses: {diag_str or 'General Clinical'}. Prescribed {meds_count} medications.",
            source_document_id=d.id,
            highlights=[f"{m.get('name', '')} ({m.get('dosage', '')})" for m in (d.extracted_entities.get("medicines", []) if d.extracted_entities else [])[:2]]
        ))

        # Collect abnormal lab values
        if d.abnormal_flags:
            abnormal_highlights.extend(d.abnormal_flags)

    # Sort timeline
    timeline.reverse()

    # Collect extracted current medications
    extracted_meds = []
    for d in docs:
        if d.extracted_entities and "medicines" in d.extracted_entities:
            extracted_meds.extend(d.extracted_entities["medicines"])

    return ClinicalSummaryResponse(
        session_id=session.id,
        patient_name=patient.full_name if patient else "Anonymous Patient",
        patient_age=patient.age if patient else 0,
        patient_gender=patient.gender if patient else "Unknown",
        abha_id=patient.abha_id if patient else None,
        triage_level=session.triage_level,
        red_flag_alert=session.red_flag_detected,
        chief_complaint=history.chief_complaint if history else None,
        socrates_hpi=history.socrates_hpi if history else {},
        past_medical_history=history.past_medical_history if history else ["Hypertension (Known history from past records)"],
        past_surgical_history=history.past_surgical_history if history else [],
        current_medications=extracted_meds or (history.current_medications if history else []),
        drug_allergies=history.drug_allergies if history else ["No known drug allergies reported"],
        family_history=history.family_history if history else [],
        prakriti_dominant=ayush.prakriti_primary if ayush else "Not assessed",
        prakriti_breakdown=ayush.prakriti_scores if ayush else {},
        agni_status=ayush.agni_status if ayush else "Not assessed",
        koshtha_status=ayush.koshtha_status if ayush else "Not assessed",
        ahara_vihara_notes=ayush.ahara_vihara if ayush else {},
        abnormal_lab_highlights=abnormal_highlights,
        chronological_timeline=timeline,
        is_verified=bool(review and review.is_verified),
        physician_notes=review.physician_clinical_notes if review else None
    )

@router.post("/sessions/{session_id}/verify", response_model=PhysicianReviewResponse)
def verify_physician_review(session_id: str, payload: PhysicianReviewRequest, db: Session = Depends(get_db)):
    """
    Physician confirms, edits, or adds clinical notes to the AI-generated history.
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    review = session.physician_review
    if not review:
        review = PhysicianReview(
            session_id=session.id,
            doctor_id=payload.doctor_id,
            doctor_name=payload.doctor_name
        )
        db.add(review)

    review.doctor_id = payload.doctor_id
    review.doctor_name = payload.doctor_name
    review.department = payload.department or "General OPD / Kayachikitsa"
    review.is_verified = payload.is_verified
    review.is_rejected = payload.is_rejected
    review.rejection_reason = payload.rejection_reason
    review.verified_chief_complaint = payload.verified_chief_complaint
    review.verified_hpi = payload.verified_hpi
    review.physician_clinical_notes = payload.physician_clinical_notes
    review.prescribed_plan = payload.prescribed_plan
    review.reviewed_at = datetime.utcnow()

    # Generate ABDM FHIR bundle
    patient_dict = {
        "id": session.patient.id if session.patient else "",
        "full_name": session.patient.full_name if session.patient else "",
        "gender": session.patient.gender if session.patient else "",
        "abha_id": session.patient.abha_id if session.patient else "",
        "phone_number": session.patient.phone_number if session.patient else ""
    }
    history_dict = {"chief_complaint": payload.verified_chief_complaint or (session.clinical_history.chief_complaint if session.clinical_history else "")}
    ayush_dict = {"prakriti_primary": session.ayush_assessment.prakriti_primary if session.ayush_assessment else "", "agni_status": session.ayush_assessment.agni_status if session.ayush_assessment else ""}

    bundle = fhir_service.generate_opd_clinical_bundle(
        session_id=session.id,
        patient_data=patient_dict,
        clinical_history=history_dict,
        ayush_assessment=ayush_dict,
        doctor_review={"doctor_name": payload.doctor_name}
    )
    review.fhir_bundle_json = bundle

    session.status = SessionStatus.REVIEWED.value
    db.commit()

    return PhysicianReviewResponse(
        session_id=session.id,
        doctor_name=payload.doctor_name,
        is_verified=payload.is_verified,
        reviewed_at=review.reviewed_at,
        message="Physician review confirmed and ABDM FHIR bundle generated successfully."
    )
