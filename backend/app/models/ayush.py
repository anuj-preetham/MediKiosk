import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class AyushAssessment(Base):
    __tablename__ = "ayush_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("intake_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Dashavidha Pariksha Key Parameters
    # 1. Prakriti (Dominant constitutional phenotype)
    prakriti_primary = Column(String(50), nullable=True)     # Vata, Pitta, Kapha, Vata-Pitta, Pitta-Kapha, etc.
    prakriti_scores = Column(JSON, default=dict)            # { "vata": 40, "pitta": 45, "kapha": 15 }
    
    # 2. Vikriti (Current state of dosha imbalance / morbidity)
    vikriti_dosha = Column(String(50), nullable=True)       # Pitta-Vata vitiation
    
    # 3. Agni (Digestive Fire: Sama, Vishama, Tikshna, Manda)
    agni_status = Column(String(50), nullable=True)
    
    # 4. Koshtha (Bowel Habit: Krura, Madhyama, Mridu)
    koshtha_status = Column(String(50), nullable=True)
    
    # 5. Sara (Tissue excellence: Tvak, Rakta, Mamsa, Meda, Asthi, Majja, Sukra, Sattva)
    sara_assessment = Column(String(100), nullable=True)
    
    # 6. Samhanana (Body build / compactness)
    samhanana = Column(String(50), nullable=True)           # Pravara (Good), Madhyama (Medium), Avara (Poor)
    
    # 7. Pramana (Anthropometric proportions)
    pramana = Column(String(50), nullable=True)
    
    # 8. Satmya (Habituation / Adaptability)
    satmya = Column(JSON, default=list)                     # Food/habit affinities
    
    # 9. Sattva (Mental temperament / fortitude: Pravara, Madhyama, Avara)
    sattva = Column(String(50), nullable=True)
    
    # 10. Ahara Shakti (Food intake & digestive capacity) & Vyayama Shakti (Work/Exercise tolerance)
    ahara_shakti = Column(String(50), nullable=True)        # High / Moderate / Low
    vyayama_shakti = Column(String(50), nullable=True)      # High / Moderate / Low
    vaya = Column(String(50), nullable=True)                # Balya, Madhyama, Vriddha
    
    # Ahara & Vihara (Dietary habits & Lifestyle/Daily routine)
    ahara_vihara = Column(JSON, default=dict)               # { "diet_type": "Vegetarian", "meal_regularity": "Irregular", "sleep_pattern": "Disturbed" }
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    session = relationship("IntakeSession", back_populates="ayush_assessment")
