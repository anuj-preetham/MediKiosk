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
    assert data["problem_statement"] == "SIH26047 - Patient Case-Taking Software"

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

    # 3. Send chief complaint
    res_chat = client.post(f"/api/chat/{session_id}/message", json={
        "message": "Persistent burning stomach pain after meals",
        "step": "chief_complaint"
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

def test_ayush_assessment():
    res = client.post("/api/sessions/start", json={"language": "en"})
    session_id = res.json()["id"]

    # Submit AYUSH answers
    res_ayush = client.post(f"/api/ayush/{session_id}/submit", json={
        "answers": {
            "prakriti_body_frame": "vata",
            "prakriti_weather": "vata",
            "agni_digestion": "vishama_agni",
            "koshtha_bowel": "krura"
        }
    })
    assert res_ayush.status_code == 200
    data = res_ayush.json()
    assert "Vata" in data["prakriti_primary"]
    assert "Vishama Agni" in data["agni_status"]

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

def test_fhir_bundle_export():
    res = client.get("/api/doctor/queue")
    first_session_id = res.json()[0]["session_id"]
    
    res_fhir = client.get(f"/api/abdm/fhir-bundle/{first_session_id}")
    assert res_fhir.status_code == 200
    bundle = res_fhir.json()
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "document"
