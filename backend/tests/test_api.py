import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, engine
from app.utils.seed_data import seed_database
from app.main import app

# Ensure database tables and seed data exist
Base.metadata.create_all(bind=engine)
seed_database()

client = TestClient(app)

def test_health_check():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "MediKiosk" in data["app"]

def test_start_session_and_socrates():
    # 1. Start Session
    res = client.post("/api/sessions/start", json={
        "language": "en",
        "patient_data": {
            "full_name": "Vikram Singh",
            "age": 42,
            "gender": "Male",
            "phone_number": "9811122233",
            "preferred_language": "en",
            "consent_granted": True,
            "consent_audio_verified": True
        }
    })
    assert res.status_code == 201
    session_id = res.json()["id"]

    # 2. Get initial question
    res_init = client.get(f"/api/chat/{session_id}/initial")
    assert res_init.status_code == 200
    assert "welcome to medikiosk" in res_init.json()["ai_reply"].lower()

    # 3. Send chief complaint with body location
    res_chat = client.post(f"/api/chat/{session_id}/message", json={
        "message": "Persistent burning stomach pain after meals",
        "step": "chief_complaint",
        "body_location": "Upper Abdomen"
    })
    assert res_chat.status_code == 200
    assert res_chat.json()["current_step"] == "site"
    assert res_chat.json()["is_red_flag"] == False

def test_red_flag_detection():
    # Start session
    res = client.post("/api/sessions/start", json={"language": "en"})
    session_id = res.json()["id"]

    # Trigger emergency chest pain red flag
    res_flag = client.post(f"/api/chat/{session_id}/message", json={
        "message": "Sudden severe crushing chest pain radiating to left arm with breathlessness",
        "step": "chief_complaint"
    })
    assert res_flag.status_code == 200
    data = res_flag.json()
    assert data["is_red_flag"] == True
    assert "Suspected Acute Coronary Syndrome" in data["red_flag_alert_title"]

def test_doctor_queue_and_summary():
    res = client.get("/api/doctor/queue")
    assert res.status_code == 200
    queue = res.json()
    assert len(queue) >= 1
    
    first_session_id = queue[0]["session_id"]
    res_summary = client.get(f"/api/doctor/sessions/{first_session_id}/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert "chief_complaint" in summary
    assert "chronological_timeline" in summary
    assert "abnormal_lab_highlights" in summary
    assert "safety_alerts" in summary

def test_drug_allergy_safety_cross_check():
    # Start session with Penicillin allergy
    res = client.post("/api/sessions/start", json={
        "language": "en",
        "patient_data": {
            "full_name": "Anita Verma",
            "age": 38,
            "gender": "Female",
            "phone_number": "9812345678",
            "preferred_language": "en",
            "consent_granted": True,
            "consent_audio_verified": True
        }
    })
    session_id = res.json()["id"]

    # Set allergy in clinical history
    from app.database import SessionLocal
    from app.models.clinical_history import ClinicalHistory
    db = SessionLocal()
    hist = db.query(ClinicalHistory).filter(ClinicalHistory.session_id == session_id).first()
    hist.drug_allergies = ["Penicillin hypersensitivity / Anaphylaxis"]
    hist.current_medications = [{"name": "Tab. Amoxicillin 500mg", "dosage": "1 TDS", "frequency": "TDS"}]
    db.commit()
    db.close()

    # Get summary and check safety alerts
    res_summary = client.get(f"/api/doctor/sessions/{session_id}/summary")
    assert res_summary.status_code == 200
    alerts = res_summary.json()["safety_alerts"]
    assert len(alerts) >= 1
    assert "Amoxicillin" in alerts[0]["medication"] or "Beta-Lactam" in alerts[0]["allergy_class"]

def test_printable_opd_casesheet_html():
    res = client.get("/api/doctor/queue")
    first_session_id = res.json()[0]["session_id"]
    
    res_sheet = client.get(f"/api/doctor/sessions/{first_session_id}/casesheet")
    assert res_sheet.status_code == 200
    assert "text/html" in res_sheet.headers["content-type"]
    assert "OPD Case Sheet" in res_sheet.text

def test_abdm_scan_and_share_qr_and_process():
    # 1. Get QR Code Payload
    res_qr = client.get("/api/abdm/scan-and-share/qr")
    assert res_qr.status_code == 200
    data_qr = res_qr.json()
    assert "abdm://scan-share" in data_qr["qr_data"]
    assert data_qr["counter_id"] == "OPD-COUNTER-01"

    # 2. Process Scan & Share Profile Handshake
    res_process = client.post("/api/abdm/scan-and-share/process", json={
        "name": "Rameshwar Sharma",
        "gender": "Male",
        "year_of_birth": 1968,
        "phone_number": "9876543210"
    })
    assert res_process.status_code == 200
    data_proc = res_process.json()
    assert data_proc["status"] == "SUCCESS"
    assert "OPD-TKN-" in data_proc["token_number"]
    assert data_proc["full_name"] == "Rameshwar Sharma"

def test_abdm_otp_flow():
    # 1. Send OTP
    res_send = client.post("/api/abdm/abha/send-otp", json={"abha_identifier": "9876543210"})
    assert res_send.status_code == 200
    txn_id = res_send.json()["transaction_id"]

    # 2. Verify OTP
    res_verify = client.post("/api/abdm/abha/verify-otp", json={"transaction_id": txn_id, "otp": "123456"})
    assert res_verify.status_code == 200
    assert res_verify.json()["status"] == "VERIFIED"
    assert "vikram.singh@abdm" in res_verify.json()["abha_address"]

def test_hospital_his_push():
    res_queue = client.get("/api/doctor/queue")
    session_id = res_queue.json()[0]["session_id"]

    res_his = client.post(f"/api/abdm/his/push/{session_id}")
    assert res_his.status_code == 200
    data = res_his.json()
    assert data["status"] == "SYNCED_TO_HIS"
    assert "HIS-TX-" in data["his_transaction_id"]
    assert "OPD-2026-" in data["hospital_opd_case_number"]

def test_fhir_bundle_export():
    res = client.get("/api/doctor/queue")
    first_session_id = res.json()[0]["session_id"]
    
    res_fhir = client.get(f"/api/abdm/fhir-bundle/{first_session_id}")
    assert res_fhir.status_code == 200
    bundle = res_fhir.json()
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "document"

def test_ai_copilot_analysis_and_doctor_query():
    res_queue = client.get("/api/doctor/queue")
    first_session_id = res_queue.json()[0]["session_id"]

    # 1. Verify AI Copilot analysis in summary
    res_summary = client.get(f"/api/doctor/sessions/{first_session_id}/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert "ai_copilot_analysis" in summary
    copilot = summary["ai_copilot_analysis"]
    assert copilot is not None
    assert "clinical_impression" in copilot
    assert len(copilot["differential_diagnoses"]) >= 1
    assert "confidence_score" in copilot["differential_diagnoses"][0]
    assert "soap_draft" in copilot

    # 2. Test interactive Doctor AI assistant query
    res_query = client.post(f"/api/doctor/sessions/{first_session_id}/ai-copilot/query", json={
        "doctor_query": "What are the contraindications for prescribing NSAIDs in this patient?"
    })
    assert res_query.status_code == 200
    q_data = res_query.json()
    assert "ai_response" in q_data
    assert len(q_data["clinical_context_used"]) >= 1
    assert "suggested_follow_up" in q_data

def test_document_ocr_confidence_metadata():
    from app.services.ocr_service import ocr_service
    extracted, flags, raw = ocr_service.extract_document_entities("dummy_path.jpg", doc_type="prescription")
    assert len(extracted["medicines"]) >= 1
    assert "confidence" in extracted["medicines"][0]
    assert "snomed_ct" in extracted["medicines"][0]
    assert "ai_ocr_metadata" in extracted

def test_custom_patient_registration_and_lifestyle_update():
    # 1. Start intake session with dynamic user-entered profile
    res = client.post("/api/sessions/start", json={
        "language": "hi",
        "patient_data": {
            "full_name": "Devendra Joshi",
            "age": 54,
            "gender": "Male",
            "phone_number": "9123498765",
            "abha_id": "devendra.joshi@abdm",
            "preferred_language": "hi",
            "consent_granted": True,
            "consent_audio_verified": True
        }
    })
    assert res.status_code == 201
    session_data = res.json()
    session_id = session_data["id"]
    patient = session_data["patient"]
    assert patient["full_name"] == "Devendra Joshi"
    assert patient["age"] == 54
    assert patient["gender"] == "Male"
    assert patient["abha_id"] == "devendra.joshi@abdm"

    # 2. Update lifestyle and chronic history
    res_life = client.post(f"/api/sessions/{session_id}/lifestyle", json={
        "past_medical_history": ["Diabetes (Type 2)", "Hypertension (BP)", "Gout / Hyperuricemia"],
        "drug_allergies": ["Sulfa drugs", "Aspirin"],
        "current_medications": [{"name": "Tab Telmisartan 40mg", "dosage": "40mg", "frequency": "1 OD Morning"}],
        "personal_history": {
            "diet": "Low Sodium / Diabetic",
            "smoking": "Non-smoker",
            "alcohol": "No",
            "sleep": "7-8 hours"
        }
    })
    assert res_life.status_code == 200
    assert res_life.json()["status"] == "SUCCESS"

    # 3. Verify session details contain persisted lifestyle data
    res_detail = client.get(f"/api/sessions/{session_id}")
    assert res_detail.status_code == 200
    clin_hist = res_detail.json()["clinical_history"]
    assert "Gout / Hyperuricemia" in clin_hist["past_medical_history"]
    assert "Sulfa drugs" in clin_hist["drug_allergies"]
    assert len(clin_hist["current_medications"]) == 1

def test_manual_document_entry_and_abnormal_lab_screening():
    # Start session
    res = client.post("/api/sessions/start", json={"language": "en"})
    session_id = res.json()["id"]

    # Submit manual document with custom medicines and abnormal lab values
    res_manual = client.post("/api/documents/manual-entry", json={
        "session_id": session_id,
        "document_title": "City Diagnostic Biochemistry Panel",
        "document_type": "lab_report",
        "doctor_or_lab_name": "City Diagnostics Center",
        "medicines": [
            {"name": "Cap Pantoprazole 40mg", "dosage": "40mg", "frequency": "1 OD", "snomed_ct": "410942007"}
        ],
        "investigations": [
            {
                "test": "HbA1c (Glycated Hemoglobin)",
                "value": "8.4",
                "unit": "%",
                "ref_range": "4.0 - 5.6 %",
                "is_abnormal": True
            },
            {
                "test": "Serum Uric Acid",
                "value": "8.2",
                "unit": "mg/dL",
                "ref_range": "3.5 - 7.2 mg/dL",
                "is_abnormal": True
            },
            {
                "test": "Serum Creatinine",
                "value": "0.9",
                "unit": "mg/dL",
                "ref_range": "0.7 - 1.2 mg/dL",
                "is_abnormal": False
            }
        ],
        "diagnoses": ["Hyperglycemia", "Hyperuricemia"]
    })
    assert res_manual.status_code == 200
    doc_data = res_manual.json()
    assert doc_data["file_name"] == "City Diagnostic Biochemistry Panel"
    assert doc_data["document_type"] == "lab_report"
    
    # Check abnormal flags computed
    flags = doc_data["abnormal_flags"]
    assert len(flags) >= 2
    flag_params = [f["parameter"] for f in flags]
    assert "HbA1c (Glycated Hemoglobin)" in flag_params
    assert "Serum Uric Acid" in flag_params

    # Verify summary reflects the abnormal lab findings
    res_summary = client.get(f"/api/doctor/sessions/{session_id}/summary")
    assert res_summary.status_code == 200
    highlights = res_summary.json()["abnormal_lab_highlights"]
    highlight_params = [h["parameter"] for h in highlights]
    assert any("HbA1c" in p for p in highlight_params)
    assert any("Uric Acid" in p for p in highlight_params)


