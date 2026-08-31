import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class SessionStatus(str, enum.Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    TRIAGED_RED_FLAG = "triaged_red_flag"
    COMPLETED = "completed"
    REVIEWED = "reviewed"

class TriageLevel(str, enum.Enum):
    ROUTINE = "routine"
    PRIORITY = "priority"
    EMERGENCY_RED_FLAG = "emergency_red_flag"

class IntakeSession(Base):
    __tablename__ = "intake_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String(30), default=SessionStatus.INITIATED.value)
    triage_level = Column(String(30), default=TriageLevel.ROUTINE.value)
    
    # Red Flag details if detected
    red_flag_detected = Column(String(255), nullable=True)
    red_flag_timestamp = Column(DateTime, nullable=True)
    red_flag_action_taken = Column(String(255), nullable=True)
    
    language = Column(String(10), default="en")
    chat_history = Column(JSON, default=list)  # List of {sender: 'ai'|'user', message: str, timestamp: str}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="sessions")
    clinical_history = relationship("ClinicalHistory", back_populates="session", uselist=False, cascade="all, delete-orphan")
    documents = relationship("MedicalDocument", back_populates="session", cascade="all, delete-orphan")
    physician_review = relationship("PhysicianReview", back_populates="session", uselist=False, cascade="all, delete-orphan")
