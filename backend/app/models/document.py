import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Date
from sqlalchemy.orm import relationship
from app.database import Base

class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("intake_sessions.id", ondelete="CASCADE"), nullable=False)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    document_type = Column(String(50), nullable=False) # prescription, lab_report, discharge_summary, investigation
    
    document_date = Column(Date, nullable=True)
    doctor_or_lab_name = Column(String(200), nullable=True)
    
    ocr_raw_text = Column(Text, nullable=True)
    
    # Structured extracted entities:
    # {
    #   "diagnoses": ["Essential Hypertension", "Gastritis"],
    #   "medicines": [{"name": "Pantoprazole", "dosage": "40mg", "frequency": "OD", "duration": "14 days"}],
    #   "investigations": [{"test": "HbA1c", "value": "8.2", "unit": "%", "ref_range": "4.0-5.6", "is_abnormal": true}],
    #   "vital_signs": {"bp": "140/90", "pulse": "78"}
    # }
    extracted_entities = Column(JSON, default=dict)
    
    # Abnormal highlights for instant physician review
    # [{"parameter": "HbA1c", "value": "8.2%", "severity": "high", "note": "Elevated - Poor glycemic control"}]
    abnormal_flags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("IntakeSession", back_populates="documents")
