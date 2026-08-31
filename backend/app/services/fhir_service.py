import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

class FHIRService:
    """
    ABDM & FHIR R4 Interoperability Generator
    Constructs standardized FHIR R4 Document Bundles compliant with Ayushman Bharat Digital Mission (ABDM).
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
        patient_id = patient_data.get("id", str(uuid.uuid4()))
        timestamp_str = datetime.utcnow().isoformat() + "Z"

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
                "gender": patient_data.get("gender", "unknown").lower(),
                "telecom": [{"system": "phone", "value": patient_data.get("phone_number", "")}]
            }
        }

        # Composition (Standardized Clinical OPD Consultation Document)
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
                "section": [
                    {
                        "title": "Chief Complaint & History of Present Illness (SOCRATES)",
                        "code": {
                            "coding": [{"system": "http://loinc.org", "code": "10154-3", "display": "Chief Complaint HPI"}]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div><p><b>Chief Complaint:</b> {clinical_history.get('chief_complaint', 'N/A') if clinical_history else 'N/A'}</p></div>"
                        }
                    },
                    {
                        "title": "Past Medical & Drug History",
                        "code": {
                            "coding": [{"system": "http://loinc.org", "code": "11348-0", "display": "History of past illness"}]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div><p><b>Recorded Past Conditions & Prior Medications</b></p></div>"
                        }
                    }
                ]
            }
        }

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
            "entry": [
                composition_resource,
                patient_resource
            ]
        }

        return bundle

fhir_service = FHIRService()
