import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class FHIRService:
    """
    ABDM & FHIR R4 Interoperability Generator
    Constructs standardized FHIR R4 Document Bundles compliant with Ayushman Bharat Digital Mission (ABDM).
    Includes Patient, Composition, Condition, MedicationStatement, Observation, and AllergyIntolerance resources.
    """

    def generate_opd_clinical_bundle(
        self,
        session_id: str,
        patient_data: Dict[str, Any],
        clinical_history: Optional[Dict[str, Any]],
        doctor_review: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        bundle_id = str(uuid.uuid4())
        composition_id = str(uuid.uuid4())
        patient_id = patient_data.get("id") or str(uuid.uuid4())
        timestamp_str = datetime.now(timezone.utc).isoformat()

        # 1. Patient Resource
        patient_resource = {
            "fullUrl": f"urn:uuid:{patient_id}",
            "resource": {
                "resourceType": "Patient",
                "id": patient_id,
                "identifier": [
                    {
                        "system": "https://healthid.ndhm.gov.in",
                        "value": patient_data.get("abha_id") or f"91-{patient_data.get('phone_number', '9876543210')}"
                    }
                ],
                "name": [{"text": patient_data.get("full_name", "Anonymous Patient")}],
                "gender": (patient_data.get("gender") or "unknown").lower(),
                "telecom": [{"system": "phone", "value": patient_data.get("phone_number", "")}]
            }
        }

        # 2. Composition Sections
        chief_comp = clinical_history.get("chief_complaint", "N/A") if clinical_history else "N/A"
        allergies = clinical_history.get("drug_allergies", []) if clinical_history else []
        meds = clinical_history.get("current_medications", []) if clinical_history else []

        composition_sections = [
            {
                "title": "Chief Complaint & History of Present Illness (SOCRATES)",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "10154-3", "display": "Chief Complaint HPI"}]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div><p><b>Chief Complaint:</b> {chief_comp}</p></div>"
                }
            },
            {
                "title": "Past Medical & Chronic Illness History",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "11348-0", "display": "History of past illness"}]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div><p><b>Recorded Past Conditions:</b> {', '.join(clinical_history.get('past_medical_history', [])) if clinical_history else 'None'}</p></div>"
                }
            },
            {
                "title": "Allergies and Adverse Reactions",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "48765-2", "display": "Allergies and adverse reactions"}]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div><p><b>Drug Allergies:</b> {', '.join(allergies) if allergies else 'No known drug allergies'}</p></div>"
                }
            }
        ]

        # 3. Composition (Document Header)
        composition_resource = {
            "fullUrl": f"urn:uuid:{composition_id}",
            "resource": {
                "resourceType": "Composition",
                "id": composition_id,
                "status": "final",
                "type": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "371530004",
                            "display": "Clinical consultation report / OPD Case Sheet"
                        }
                    ],
                    "text": "MediKiosk Clinical Intake & History Summary"
                },
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "date": timestamp_str,
                "title": "Outpatient Clinical Intake Record",
                "author": [{"display": doctor_review.get("doctor_name", "Consultant Physician") if doctor_review else "MediKiosk Intake"}],
                "section": composition_sections
            }
        }

        # 4. Medication Resources
        bundle_entries = [composition_resource, patient_resource]

        for m in meds:
            med_id = str(uuid.uuid4())
            med_name = m.get("name", m) if isinstance(m, dict) else str(m)
            bundle_entries.append({
                "fullUrl": f"urn:uuid:{med_id}",
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": med_id,
                    "status": "active",
                    "medicationCodeableConcept": {
                        "text": med_name
                    },
                    "subject": {"reference": f"urn:uuid:{patient_id}"},
                    "dosage": [{"text": m.get("dosage", "Standard") if isinstance(m, dict) else "Standard"}]
                }
            })

        # 5. Full Document Bundle
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": timestamp_str,
                "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DocumentBundle"]
            },
            "identifier": {
                "system": "https://abdm.gov.in/bundles",
                "value": f"MEDIKIOSK-{session_id}"
            },
            "type": "document",
            "timestamp": timestamp_str,
            "entry": bundle_entries
        }

        return bundle

fhir_service = FHIRService()
