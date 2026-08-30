from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models.session import IntakeSession, SessionStatus, TriageLevel
from app.models.clinical_history import ClinicalHistory
from app.schemas.chat_schema import ChatMessageRequest, ChatMessageResponse
from app.services.ai_service import ai_service

router = APIRouter()

@router.get("/{session_id}/initial", response_model=ChatMessageResponse)
def get_initial_question(session_id: str, db: Session = Depends(get_db)):
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    lang = session.language or "en"
    q_data = ai_service.SOCRATES_QUESTIONS["chief_complaint"][lang]
    
    return {
        "ai_reply": q_data["question"],
        "ai_reply_audio_text": q_data["audio"],
        "language": lang,
        "current_step": "chief_complaint",
        "next_step": "site",
        "quick_options": q_data["options"],
        "is_red_flag": False,
        "extracted_socrates": {},
        "progress_percentage": 10
    }

@router.post("/{session_id}/message", response_model=ChatMessageResponse)
def send_chat_turn(session_id: str, payload: ChatMessageRequest, db: Session = Depends(get_db)):
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history_record = session.clinical_history
    if not history_record:
        history_record = ClinicalHistory(session_id=session.id)
        db.add(history_record)
        db.commit()
        db.refresh(history_record)

    current_socrates = dict(history_record.socrates_hpi or {})
    current_step = payload.step or "chief_complaint"
    
    # Process turn with AI & Red-Flag Service
    result = ai_service.process_turn(
        current_step=current_step,
        user_message=payload.message,
        language=session.language or "en",
        extracted_socrates=current_socrates
    )

    # Save to chat history
    chat_list = list(session.chat_history or [])
    chat_list.append({"sender": "user", "message": payload.message, "timestamp": datetime.utcnow().isoformat()})
    chat_list.append({"sender": "ai", "message": result["ai_reply"], "timestamp": datetime.utcnow().isoformat()})
    session.chat_history = chat_list

    # If Red Flag detected, escalate session immediately
    if result["is_red_flag"]:
        session.status = SessionStatus.TRIAGED_RED_FLAG.value
        session.triage_level = TriageLevel.EMERGENCY_RED_FLAG.value
        session.red_flag_detected = result["red_flag_alert_title"]
        session.red_flag_timestamp = datetime.utcnow()
        session.red_flag_action_taken = result["red_flag_instructions"]
    else:
        # Update chief complaint and SOCRATES data
        if current_step == "chief_complaint":
            history_record.chief_complaint = payload.message
        
        history_record.socrates_hpi = result["extracted_socrates"]

    db.commit()
    return result
