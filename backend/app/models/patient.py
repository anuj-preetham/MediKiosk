import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    abha_id = Column(String(50), nullable=True, index=True)
    full_name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    phone_number = Column(String(20), nullable=True)
    preferred_language = Column(String(10), default="en")
    
    # Consent parameters
    consent_granted = Column(Boolean, default=True)
    consent_timestamp = Column(DateTime, default=datetime.utcnow)
    consent_audio_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("IntakeSession", back_populates="patient", cascade="all, delete-orphan")
