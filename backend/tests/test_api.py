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

def test_fhir_bundle_export():
    res = client.get("/api/doctor/queue")
    first_session_id = res.json()[0]["session_id"]
    
    res_fhir = client.get(f"/api/abdm/fhir-bundle/{first_session_id}")
    assert res_fhir.status_code == 200
    bundle = res_fhir.json()
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "document"
