from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.database import get_db
from app.models.session import IntakeSession
from app.models.ayush import AyushAssessment
from app.services.ayush_service import ayush_service

router = APIRouter()

class AyushSubmitRequest(BaseModel):
    answers: Dict[str, str] # e.g. {"prakriti_body_frame": "pitta", "prakriti_weather": "vata", "agni_digestion": "tikshna_agni", ...}

@router.get("/questions")
def get_all_ayush_questions(language: str = "en"):
    lang = language if language in ["en", "hi"] else "en"
    questions = {}
    for k, v in ayush_service.QUESTIONS.items():
        questions[k] = v[lang]
    return questions

@router.post("/{session_id}/submit")
def submit_ayush_assessment(session_id: str, payload: AyushSubmitRequest, db: Session = Depends(get_db)):
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    assessment_record = session.ayush_assessment
    if not assessment_record:
        assessment_record = AyushAssessment(session_id=session.id)
        db.add(assessment_record)

    # Compute AYUSH parameters
    calc = ayush_service.calculate_assessment(payload.answers)
    
    assessment_record.prakriti_primary = calc["prakriti_primary"]
    assessment_record.prakriti_scores = calc["prakriti_scores"]
    assessment_record.agni_status = calc["agni_status"]
    assessment_record.koshtha_status = calc["koshtha_status"]
    assessment_record.samhanana = calc["samhanana"]
    assessment_record.ahara_shakti = calc["ahara_shakti"]
    assessment_record.vyayama_shakti = calc["vyayama_shakti"]
    assessment_record.ahara_vihara = calc["ahara_vihara"]

    db.commit()
    db.refresh(assessment_record)

    return {
        "message": "AYUSH assessment saved successfully",
        "prakriti_primary": assessment_record.prakriti_primary,
        "prakriti_scores": assessment_record.prakriti_scores,
        "agni_status": assessment_record.agni_status,
        "koshtha_status": assessment_record.koshtha_status,
        "ahara_vihara": assessment_record.ahara_vihara
    }
