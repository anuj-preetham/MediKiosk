import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import (
    Patient, IntakeSession, ClinicalHistory,
    AyushAssessment, MedicalDocument, PhysicianReview
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if data already exists
    if db.query(Patient).count() > 0:
        print("Database already contains seed records. Skipping seeding.")
        db.close()
        return

    print("Seeding demo patients, intake sessions, and documents...")

    # Case 1: Routine Ayurvedic Joint Pain & Dyspepsia
    p1 = Patient(
        id=str(uuid.uuid4()),
        abha_id="91-9876543210@abdm",
        full_name="Rameshwar Sharma",
        age=56,
        gender="Male",
        phone_number="+91 98765 43210",
        preferred_language="hi",
        consent_granted=True,
        consent_audio_verified=True,
        consent_timestamp=datetime.utcnow() - timedelta(hours=2)
    )
    db.add(p1)
    db.flush()

    s1 = IntakeSession(
        id=str(uuid.uuid4()),
        patient_id=p1.id,
        status="completed",
        triage_level="routine",
        language="hi",
        created_at=datetime.utcnow() - timedelta(minutes=45)
    )
    db.add(s1)
    db.flush()

    h1 = ClinicalHistory(
        id=str(uuid.uuid4()),
        session_id=s1.id,
        chief_complaint="घुटनों में तेज दर्द व अकड़न और खट्टी डकारें (Bilateral Knee Pain & Acidity)",
        socrates_hpi={
            "site": "Both knee joints & upper abdomen",
            "onset": "Gradual worsening over 6 months",
            "character": "Dull throbbing ache in knees; burning in chest after meals",
            "radiation": "Pain radiates down both calves",
            "associated": "Morning stiffness for 30 minutes, mild knee crepitus, flatulence",
            "timing": "Knee pain worse in cold weather; acidity worse after dinner",
            "exacerbating_relieving": "Relieved by hot water fermentation and rest; aggravated by climbing stairs",
            "severity": "6/10 (Moderate)"
        },
        past_medical_history=["Hypertension (3 years on Amlodipine)", "Mild Hyperlipidemia"],
        past_surgical_history=[],
        current_medications=[
            {"name": "Tab. Amlodipine 5mg", "dosage": "1 OD", "frequency": "Morning"}
        ],
        drug_allergies=["Sulfa drugs (Skin pruritus)"],
        family_history=["Mother had osteoarthritis"]
    )
    db.add(h1)

    a1 = AyushAssessment(
        id=str(uuid.uuid4()),
        session_id=s1.id,
        prakriti_primary="Vata-Pitta (Dvidoshaja)",
        prakriti_scores={"Vata": 50, "Pitta": 35, "Kapha": 15},
        agni_status="Vishama Agni (Irregular Appetite & Digestion)",
        koshtha_status="Krura Koshtha (Constipation tendency)",
        samhanana="Madhyama (Medium Build)",
        ahara_shakti="Madhyama (Moderate)",
        vyayama_shakti="Avara (Poor tolerance due to joint pain)",
        ahara_vihara={
            "diet": "Vegetarian",
            "habit": "Irregular meal timings, high intake of curd at night",
            "sleep": "6 hours, disturbed due to knee discomfort"
        }
    )
    db.add(a1)

    d1 = MedicalDocument(
        id=str(uuid.uuid4()),
        session_id=s1.id,
        file_name="prescription_aiia_previous.jpg",
        file_path="uploads/demo_prescription.jpg",
        document_type="prescription",
        document_date=date.today() - timedelta(days=60),
        doctor_or_lab_name="AIIA Kayachikitsa OPD",
        ocr_raw_text="AIIA OPD Rx: Tab. Yograj Guggulu 2 BD, Syp. Dashamoolarishta 15ml BD, Cap. Pantoprazole 40mg OD",
        extracted_entities={
            "diagnoses": ["Janu Sandhigata Vata (Osteoarthritis)", "Amlapitta (Hyperacidity)"],
            "medicines": [
                {"name": "Tab. Yograj Guggulu 500mg", "dosage": "2 tabs", "frequency": "Twice Daily", "duration": "1 month"},
                {"name": "Syp. Dashamoolarishta", "dosage": "15ml", "frequency": "Twice Daily after meals", "duration": "1 month"},
                {"name": "Cap. Pantoprazole 40mg", "dosage": "1 cap", "frequency": "Once Daily (Morning AC)", "duration": "14 days"}
            ],
            "investigations": [
                {"test": "Serum Uric Acid", "value": "7.8", "unit": "mg/dL", "ref_range": "3.5 - 7.0", "is_abnormal": True},
                {"test": "HbA1c", "value": "7.2", "unit": "%", "ref_range": "4.0 - 5.6", "is_abnormal": True}
            ]
        },
        abnormal_flags=[
            {"parameter": "Serum Uric Acid", "value": "7.8 mg/dL", "ref_range": "3.5 - 7.0", "severity": "high", "clinical_note": "Hyperuricemia (Risk of secondary gouty arthropathy)"},
            {"parameter": "HbA1c", "value": "7.2 %", "ref_range": "4.0 - 5.6", "severity": "high", "clinical_note": "Elevated HbA1c (Indicative of suboptimally controlled blood sugar)"}
        ]
    )
    db.add(d1)

    # Case 2: Red Flag Emergency Triage
    p2 = Patient(
        id=str(uuid.uuid4()),
        abha_id="91-9123456789@abdm",
        full_name="Sunita Devi",
        age=62,
        gender="Female",
        phone_number="+91 91234 56789",
        preferred_language="en",
        consent_granted=True,
        consent_audio_verified=True,
        consent_timestamp=datetime.utcnow() - timedelta(minutes=15)
    )
    db.add(p2)
    db.flush()

    s2 = IntakeSession(
        id=str(uuid.uuid4()),
        patient_id=p2.id,
        status="triaged_red_flag",
        triage_level="emergency_red_flag",
        red_flag_detected="Suspected Acute Coronary Syndrome / Severe Cardiac Event",
        red_flag_timestamp=datetime.utcnow() - timedelta(minutes=10),
        red_flag_action_taken="IMMEDIATE ATTENTION: Direct patient to Emergency / Triage Room 1 for immediate ECG, vitals, and physician evaluation.",
        language="en",
        created_at=datetime.utcnow() - timedelta(minutes=15)
    )
    db.add(s2)
    db.flush()

    h2 = ClinicalHistory(
        id=str(uuid.uuid4()),
        session_id=s2.id,
        chief_complaint="Severe crushing chest pain with breathlessness and left arm radiation for 45 minutes",
        socrates_hpi={
            "site": "Retrosternal chest radiating to left arm and jaw",
            "onset": "Acute sudden onset 45 minutes ago",
            "character": "Heavy crushing tightness",
            "radiation": "Left arm and left side of neck",
            "associated": "Profuse cold sweating, acute breathlessness, dizziness",
            "timing": "Continuous, worsening with minimal effort",
            "exacerbating_relieving": "No relief with rest",
            "severity": "9/10 (Emergency)"
        },
        past_medical_history=["Type 2 Diabetes Mellitus (10 years)", "Dyslipidemia"],
        current_medications=[{"name": "Tab. Metformin 1000mg", "dosage": "1 BD", "frequency": "Twice Daily"}],
        drug_allergies=[]
    )
    db.add(h2)

    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
