from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.session import IntakeSession
from app.services.fhir_service import fhir_service

router = APIRouter()

@router.get("/fhir-bundle/{session_id}")
def get_fhir_bundle(session_id: str, db: Session = Depends(get_db)):
    """
    Export ABDM-compliant FHIR R4 Bundle for electronic health record interoperability.
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.physician_review and session.physician_review.fhir_bundle_json:
        return session.physician_review.fhir_bundle_json

    # Dynamically generate bundle if not yet confirmed
    patient_dict = {
        "id": session.patient.id if session.patient else "",
        "full_name": session.patient.full_name if session.patient else "Anonymous",
        "gender": session.patient.gender if session.patient else "unknown",
        "abha_id": session.patient.abha_id if session.patient else "",
        "phone_number": session.patient.phone_number if session.patient else ""
    }
    history_dict = {"chief_complaint": session.clinical_history.chief_complaint if session.clinical_history else ""}
    ayush_dict = {"prakriti_primary": session.ayush_assessment.prakriti_primary if session.ayush_assessment else "", "agni_status": session.ayush_assessment.agni_status if session.ayush_assessment else ""}

    bundle = fhir_service.generate_opd_clinical_bundle(
        session_id=session.id,
        patient_data=patient_dict,
        clinical_history=history_dict,
        ayush_assessment=ayush_dict,
        doctor_review=None
    )
    return bundle
