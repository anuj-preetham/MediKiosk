import uuid
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import (
    Patient, IntakeSession, ClinicalHistory,
    MedicalDocument, PhysicianReview
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if data already exists
    if db.query(Patient).count() > 0:
        db.close()
        return

    print("Seeding demo patients, intake sessions, and documents...")
    now = datetime.now(timezone.utc)

    # Case 1: Routine OPD - Osteoarthritis & Acid Reflux
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
        consent_timestamp=now - timedelta(hours=2)
    )
    db.add(p1)
    db.flush()

    s1 = IntakeSession(
        id=str(uuid.uuid4()),
        patient_id=p1.id,
        status="completed",
        triage_level="routine",
        language="hi",
        created_at=now - timedelta(minutes=45)
    )
    db.add(s1)
    db.flush()

    h1 = ClinicalHistory(
        id=str(uuid.uuid4()),
        session_id=s1.id,
        chief_complaint="घुटनों में तेज दर्द व अकड़न और खट्टी डकारें (Bilateral Knee Pain & Gastroesophageal Reflux)",
        socrates_hpi={
            "site": "Both knee joints & upper epigastrium",
            "onset": "Gradual worsening over 6 months",
            "character": "Dull throbbing ache in knees; burning in chest after meals",
            "radiation": "Pain radiates down both calves",
            "associated": "Morning stiffness for 30 minutes, mild knee crepitus, flatulence",
            "timing": "Knee pain worse in cold weather; acidity worse after dinner",
            "exacerbating_relieving": "Relieved by rest and warm compression; aggravated by climbing stairs",
            "severity": "6/10 (Moderate)"
        },
        past_medical_history=["Essential Hypertension (3 years on Amlodipine)", "Mild Hyperlipidemia"],
        past_surgical_history=[],
        current_medications=[
            {"name": "Tab. Amlodipine 5mg", "dosage": "1 tab OD", "frequency": "Morning"}
        ],
        drug_allergies=["Sulfa drugs (Skin pruritus)"],
        family_history=["Mother had osteoarthritis, Father had hypertension"],
        personal_history={
            "diet": "Vegetarian, high tea intake",
            "physical_activity": "Sedentary desk job",
            "smoking": "Non-smoker",
            "alcohol": "Non-drinker",
            "sleep": "6 hours, occasionally disturbed"
        },
        review_of_systems={
            "musculoskeletal": "Bilateral knee joint stiffness and pain",
            "gastrointestinal": "Epigastric burning, acid reflux",
            "cardiovascular": "No palpitations or chest heaviness"
        }
    )
    db.add(h1)

    d1 = MedicalDocument(
        id=str(uuid.uuid4()),
        session_id=s1.id,
        file_name="prescription_district_hospital.jpg",
        file_path="uploads/demo_prescription.jpg",
        document_type="prescription",
        document_date=date.today() - timedelta(days=60),
        doctor_or_lab_name="District Civil Hospital Medicine OPD",
        ocr_raw_text="District Hospital OPD Rx: Tab. Pantoprazole 40mg OD, Tab. Paracetamol 650mg SOS, Tab. Calcium + Vit D3 OD",
        extracted_entities={
            "diagnoses": ["Bilateral Knee Osteoarthritis", "Gastroesophageal Reflux Disease (GERD)"],
            "medicines": [
                {"name": "Tab. Pantoprazole 40mg", "dosage": "1 tab", "frequency": "Once Daily (Morning AC)", "duration": "14 days"},
                {"name": "Tab. Paracetamol 650mg", "dosage": "1 tab", "frequency": "SOS (For severe knee pain)", "duration": "5 days"},
                {"name": "Tab. Calcium 500mg + Vitamin D3", "dosage": "1 tab", "frequency": "Once Daily (After food)", "duration": "1 month"}
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

    # Case 2: Red Flag Emergency Triage Case
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
        consent_timestamp=now - timedelta(minutes=15)
    )
    db.add(p2)
    db.flush()

    s2 = IntakeSession(
        id=str(uuid.uuid4()),
        patient_id=p2.id,
        status="triaged_red_flag",
        triage_level="emergency_red_flag",
        red_flag_detected="Suspected Acute Coronary Syndrome / Severe Cardiac Event",
        red_flag_timestamp=now - timedelta(minutes=10),
        red_flag_action_taken="IMMEDIATE ATTENTION: Direct patient to Emergency / Triage Room 1 for immediate ECG, vitals, and physician evaluation.",
        language="en",
        created_at=now - timedelta(minutes=15)
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
        current_medications=[{"name": "Tab. Metformin 1000mg", "dosage": "1 tab BD", "frequency": "Twice Daily"}],
        drug_allergies=[],
        personal_history={"diet": "Diabetic diet", "smoking": "No", "alcohol": "No"}
    )
    db.add(h2)

    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
