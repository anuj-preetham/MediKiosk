from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.database import get_db
from app.models.session import IntakeSession
from app.services.fhir_service import fhir_service
from app.services.abdm_service import abdm_service

router = APIRouter()

@router.get("/scan-and-share/qr")
def get_scan_and_share_qr(counter_id: str = "OPD-COUNTER-01"):
    """
    Generate ABDM Scan & Share QR payload for patient counter self-check-in.
    """
    return abdm_service.generate_scan_and_share_qr(counter_id=counter_id)

@router.post("/scan-and-share/process")
def process_scan_and_share_checkin(payload: Dict[str, Any] = Body(...)):
    """
    Process scanned demographic data sent from patient's ABHA / Arogya Setu app.
    """
    return abdm_service.process_scan_and_share_payload(payload)

@router.post("/abha/send-otp")
def send_abha_verification_otp(payload: Dict[str, Any] = Body(...)):
    """
    Initiate ABHA OTP authentication.
    """
    abha_identifier = payload.get("abha_identifier", "9876543210")
    return abdm_service.send_abha_otp(abha_identifier)

@router.post("/abha/verify-otp")
def verify_abha_otp(payload: Dict[str, Any] = Body(...)):
    """
    Verify OTP for ABHA linking.
    """
    txn_id = payload.get("transaction_id", "")
    otp = payload.get("otp", "123456")
    return abdm_service.verify_abha_otp(txn_id, otp)

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

    bundle = fhir_service.generate_opd_clinical_bundle(
        session_id=session.id,
        patient_data=patient_dict,
        clinical_history=history_dict,
        doctor_review=None
    )
    return bundle

@router.post("/his/push/{session_id}")
def push_case_to_hospital_his(session_id: str, db: Session = Depends(get_db)):
    """
    Sync verified case and FHIR document to the Hospital Information System (HIS).
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    patient_dict = {
        "full_name": session.patient.full_name if session.patient else "Anonymous",
        "abha_id": session.patient.abha_id if session.patient else "91-9876543210@abdm",
        "phone_number": session.patient.phone_number if session.patient else ""
    }
    history_dict = {
        "chief_complaint": session.clinical_history.chief_complaint if session.clinical_history else "General OPD"
    }

    bundle = session.physician_review.fhir_bundle_json if (session.physician_review and session.physician_review.fhir_bundle_json) else fhir_service.generate_opd_clinical_bundle(
        session_id=session.id,
        patient_data=patient_dict,
        clinical_history=history_dict
    )

    result = abdm_service.push_to_hospital_his(
        session_id=session.id,
        patient_data=patient_dict,
        clinical_history=history_dict,
        fhir_bundle=bundle
    )
    return result
