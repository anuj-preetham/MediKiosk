from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.models.session import IntakeSession, SessionStatus, TriageLevel
from app.models.review import PhysicianReview
from app.schemas.summary_schema import (
    ClinicalSummaryResponse, TimelineEvent,
    PhysicianReviewRequest, PhysicianReviewResponse,
    AICopilotAnalysis, AICopilotQueryRequest, AICopilotQueryResponse
)
from app.services.fhir_service import fhir_service
from app.services.safety_service import safety_service
from app.services.pdf_service import pdf_service
from app.services.ai_service import ai_service

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
            "documents_count": len(s.documents),
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "is_reviewed": bool(s.physician_review and s.physician_review.is_verified)
        })
    return queue

@router.get("/sessions/{session_id}/summary", response_model=ClinicalSummaryResponse)
def get_structured_clinical_summary(session_id: str, db: Session = Depends(get_db)):
    """
    Generate unified physician-ready clinical summary with safety alerts and chronological timeline.
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    patient = session.patient
    history = session.clinical_history
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
    extracted_meds = []

    for d in docs:
        d_date_str = str(d.document_date) if d.document_date else "Prior Visit"
        diag_str = ", ".join(d.extracted_entities.get("diagnoses", [])) if d.extracted_entities else ""
        meds_in_doc = (d.extracted_entities.get("medicines", []) if d.extracted_entities else [])
        extracted_meds.extend(meds_in_doc)
        
        timeline.append(TimelineEvent(
            date=d_date_str,
            event_type=d.document_type,
            title=f"{d.document_type.replace('_', ' ').title()} ({d.doctor_or_lab_name or 'District Hospital'})",
            description=f"Extracted Diagnoses: {diag_str or 'General Clinical'}. Prescribed {len(meds_in_doc)} medications.",
            source_document_id=d.id,
            highlights=[f"{m.get('name', '')} ({m.get('dosage', '')})" for m in meds_in_doc[:2]]
        ))

        # Collect abnormal lab values
        if d.abnormal_flags:
            abnormal_highlights.extend(d.abnormal_flags)

    # Sort timeline
    timeline.reverse()

    # Combine medications
    all_meds = extracted_meds or (history.current_medications if history else [])

    # 3. Clinical Safety Cross-Checks (Drug-Allergy & Drug-Drug)
    patient_allergies = history.drug_allergies if history else []
    safety_alerts = safety_service.check_drug_allergies(patient_allergies, all_meds)
    safety_alerts.extend(safety_service.check_drug_interactions(all_meds))

    # 4. Generate AI Clinical Copilot & Differential Diagnoses
    copilot_input = {
        "patient_name": patient.full_name if patient else "Patient",
        "patient_age": patient.age if patient else 45,
        "patient_gender": patient.gender if patient else "M",
        "chief_complaint": history.chief_complaint if history else None,
        "socrates_hpi": history.socrates_hpi if history else {},
        "past_medical_history": history.past_medical_history if history else [],
        "current_medications": all_meds,
        "drug_allergies": patient_allergies,
        "abnormal_lab_highlights": abnormal_highlights,
        "triage_level": session.triage_level
    }
    ai_copilot_data = ai_service.generate_ai_clinical_copilot(copilot_input)

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
        past_medical_history=history.past_medical_history if history else ["Hypertension (3 years)"],
        past_surgical_history=history.past_surgical_history if history else [],
        current_medications=all_meds,
        drug_allergies=patient_allergies or ["No known drug allergies reported"],
        family_history=history.family_history if history else [],
        personal_history=history.personal_history if history else {"diet": "Regular", "sleep": "Normal"},
        review_of_systems=history.review_of_systems if history else {},
        abnormal_lab_highlights=abnormal_highlights,
        chronological_timeline=timeline,
        safety_alerts=safety_alerts,
        ai_copilot_analysis=ai_copilot_data,
        is_verified=bool(review and review.is_verified),
        physician_notes=review.physician_clinical_notes if review else None
    )

@router.post("/sessions/{session_id}/ai-copilot/query", response_model=AICopilotQueryResponse)
def query_ai_copilot(session_id: str, payload: AICopilotQueryRequest, db: Session = Depends(get_db)):
    """
    Interactive Doctor AI Clinical Assistant query tool for specific patient cases.
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    patient = session.patient
    history = session.clinical_history
    docs = session.documents

    extracted_meds = []
    abnormal_highlights = []
    for d in docs:
        if d.extracted_entities:
            extracted_meds.extend(d.extracted_entities.get("medicines", []))
        if d.abnormal_flags:
            abnormal_highlights.extend(d.abnormal_flags)

    all_meds = extracted_meds or (history.current_medications if history else [])
    
    context_dict = {
        "patient_name": patient.full_name if patient else "Patient",
        "patient_age": patient.age if patient else 45,
        "patient_gender": patient.gender if patient else "M",
        "chief_complaint": history.chief_complaint if history else None,
        "socrates_hpi": history.socrates_hpi if history else {},
        "past_medical_history": history.past_medical_history if history else [],
        "current_medications": all_meds,
        "drug_allergies": history.drug_allergies if history else [],
        "abnormal_lab_highlights": abnormal_highlights,
        "triage_level": session.triage_level
    }

    result = ai_service.answer_physician_query(context_dict, payload.doctor_query)
    return AICopilotQueryResponse(**result)

@router.get("/sessions/{session_id}/casesheet", response_class=HTMLResponse)
def get_printable_opd_casesheet(session_id: str, db: Session = Depends(get_db)):
    """
    Generate professional printable OPD Case Sheet HTML ready for print / PDF export.
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    patient = {
        "full_name": session.patient.full_name if session.patient else "Anonymous",
        "age": session.patient.age if session.patient else 0,
        "gender": session.patient.gender if session.patient else "N/A",
        "abha_id": session.patient.abha_id if session.patient else "N/A",
        "phone_number": session.patient.phone_number if session.patient else "N/A"
    }

    history = {
        "chief_complaint": session.clinical_history.chief_complaint if session.clinical_history else None,
        "socrates_hpi": session.clinical_history.socrates_hpi if session.clinical_history else {},
        "past_medical_history": session.clinical_history.past_medical_history if session.clinical_history else [],
        "drug_allergies": session.clinical_history.drug_allergies if session.clinical_history else [],
        "current_medications": session.clinical_history.current_medications if session.clinical_history else [],
        "personal_history": session.clinical_history.personal_history if session.clinical_history else {}
    }

    docs_list = [
        {"id": d.id, "file_name": d.file_name, "document_type": d.document_type}
        for d in session.documents
    ]

    review_data = {
        "doctor_name": session.physician_review.doctor_name if session.physician_review else "Dr. Rajesh Sharma, MD",
        "department": session.physician_review.department if session.physician_review else "General Medicine OPD",
        "physician_clinical_notes": session.physician_review.physician_clinical_notes if session.physician_review else "Clinical intake verified.",
        "prescribed_plan": session.physician_review.prescribed_plan if session.physician_review else ""
    } if session.physician_review else None

    # Safety alerts
    all_meds = history["current_medications"]
    safety_alerts = safety_service.check_drug_allergies(history["drug_allergies"], all_meds)

    html_content = pdf_service.generate_opd_casesheet_html(
        session_id=session.id,
        patient=patient,
        clinical_history=history,
        documents=docs_list,
        review=review_data,
        safety_alerts=safety_alerts
    )
    return HTMLResponse(content=html_content)

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
    review.department = payload.department or "General Medicine / OPD"
    review.is_verified = payload.is_verified
    review.is_rejected = payload.is_rejected
    review.rejection_reason = payload.rejection_reason
    review.verified_chief_complaint = payload.verified_chief_complaint
    review.verified_hpi = payload.verified_hpi
    review.physician_clinical_notes = payload.physician_clinical_notes
    review.prescribed_plan = payload.prescribed_plan
    review.reviewed_at = datetime.now(timezone.utc)

    # Generate ABDM FHIR bundle
    patient_dict = {
        "id": session.patient.id if session.patient else "",
        "full_name": session.patient.full_name if session.patient else "",
        "gender": session.patient.gender if session.patient else "",
        "abha_id": session.patient.abha_id if session.patient else "",
        "phone_number": session.patient.phone_number if session.patient else ""
    }
    history_dict = {"chief_complaint": payload.verified_chief_complaint or (session.clinical_history.chief_complaint if session.clinical_history else "")}

    bundle = fhir_service.generate_opd_clinical_bundle(
        session_id=session.id,
        patient_data=patient_dict,
        clinical_history=history_dict,
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
