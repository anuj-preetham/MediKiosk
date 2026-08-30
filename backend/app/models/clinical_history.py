import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database import Base

class ClinicalHistory(Base):
    __tablename__ = "clinical_histories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("intake_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    chief_complaint = Column(Text, nullable=True)
    
    # SOCRATES Structured HPI
    # { "site": "...", "onset": "...", "character": "...", "radiation": "...", "associated": "...", "timing": "...", "exacerbating_relieving": "...", "severity": "8/10" }
    socrates_hpi = Column(JSON, default=dict)
    
    past_medical_history = Column(JSON, default=list)       # ["Hypertension (5 yrs)", "Type 2 Diabetes"]
    past_surgical_history = Column(JSON, default=list)      # ["Appendectomy (2018)"]
    current_medications = Column(JSON, default=list)        # ["Metformin 500mg BD", "Amlodipine 5mg OD"]
    drug_allergies = Column(JSON, default=list)             # ["Penicillin (Rash)", "Sulfa drugs"]
    family_history = Column(JSON, default=list)             # ["Father: CAD", "Mother: Asthma"]
    personal_history = Column(JSON, default=dict)           # { "smoking": "no", "alcohol": "occasional", "sleep": "6h" }
    review_of_systems = Column(JSON, default=dict)          # { "cardio": "no palpitation", "respiratory": "mild cough" }
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    session = relationship("IntakeSession", back_populates="clinical_history")
