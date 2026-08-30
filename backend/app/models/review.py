import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class PhysicianReview(Base):
    __tablename__ = "physician_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("intake_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    doctor_id = Column(String(50), nullable=False)
    doctor_name = Column(String(150), nullable=False)
    department = Column(String(100), default="General OPD / Kayachikitsa")
    
    # Review Status
    is_verified = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    rejection_reason = Column(String(255), nullable=True)
    
    # Editable summary fields verified by doctor
    verified_chief_complaint = Column(Text, nullable=True)
    verified_hpi = Column(Text, nullable=True)
    verified_past_history = Column(JSON, default=list)
    verified_ayush_notes = Column(Text, nullable=True)
    
    physician_clinical_notes = Column(Text, nullable=True)
    prescribed_plan = Column(Text, nullable=True)
    
    # Interoperability: ABDM FHIR R4 Bundle JSON
    fhir_bundle_json = Column(JSON, nullable=True)
    abdm_care_context_ref = Column(String(100), nullable=True)
    
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("IntakeSession", back_populates="physician_review")
