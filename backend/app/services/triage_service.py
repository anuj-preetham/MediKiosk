import re
from typing import Tuple, Optional, Dict, Any

class TriageService:
    """
    Real-time Red Flag & Clinical Emergency Triage Detector
    Matches high-risk symptom patterns in both English and Hindi.
    """

    RED_FLAG_PATTERNS = [
        {
            "id": "cardiac_emergency",
            "title": "Suspected Acute Coronary Syndrome / Severe Cardiac Event",
            "hindi_title": "गंभीर हृदय आपात स्थिति की संभावना",
            "keywords": [
                r"chest pain", r"छाती में दर्द", r"सीने में दर्द", r"crushing pain",
                r"radiat.*arm", r"बांह में दर्द", r"radiat.*jaw", r"pressure in chest",
                r"sweating.*chest", r"घबराहट और सीने में दर्द"
            ],
            "secondary_triggers": [r"shortness of breath", r"breathless", r"सांस फूलना", r"सांस लेने में तकलीफ", r"sweating", r"पसीना"],
            "action_instructions": "IMMEDIATE ATTENTION: Direct patient to Emergency / Triage Room 1 for immediate ECG, vitals, and physician evaluation. Do not continue kiosk intake."
        },
        {
            "id": "stroke_neurological",
            "title": "Suspected Acute Stroke / Focal Neurological Deficit",
            "hindi_title": "संभावित स्ट्रोक / गंभीर न्यूरोलॉजिकल आपातकाल",
            "keywords": [
                r"facial droop", r"चेहरे का टेढ़ा होना", r"arm weakness", r"हाथ में कमजोरी",
                r"slurred speech", r"बोलने में कठिनाई", r"sudden paralysis", r"अचानक लकवा",
                r"loss of consciousness", r"बेहोश", r"unconscious", r"seizure", r"दौरा"
            ],
            "action_instructions": "EMERGENCY: Suspected FAST stroke signs. Alert nearest nursing officer and move patient to Acute Care."
        },
        {
            "id": "severe_respiratory",
            "title": "Acute Severe Respiratory Distress",
            "hindi_title": "गंभीर श्वसन संकट (सांस लेने में अत्यधिक तकलीफ)",
            "keywords": [
                r"cannot breathe", r"सांस नहीं आ रही", r"severe wheezing", r"gasping",
                r"lips turn.*blue", r"नीले होंठ", r"stridor", r"suffocat"
            ],
            "action_instructions": "URGENT: Initiate oxygen triage protocol and direct to ER triage."
        },
        {
            "id": "severe_hemorrhage_trauma",
            "title": "Severe Bleeding / Acute Hemorrhage",
            "hindi_title": "अत्यधिक रक्तस्राव / गंभीर चोट",
            "keywords": [
                r"uncontrolled bleed", r"खून बहना बंद नहीं", r"vomiting blood", r"खून की उल्टी",
                r"coughing blood", r"hemoptysis", r"black stool.*dizzy"
            ],
            "action_instructions": "EMERGENCY: Immediate pressure hemostasis and IV line setup by clinical nursing team."
        }
    ]

    def scan_for_red_flags(self, text: str, language: str = "en") -> Tuple[bool, Optional[Dict[str, Any]]]:
        if not text:
            return False, None
            
        lower_text = text.lower()

        for pattern in self.RED_FLAG_PATTERNS:
            # Check direct keywords
            matched_primary = any(re.search(kw, lower_text) for kw in pattern["keywords"])
            
            if matched_primary:
                title = pattern["hindi_title"] if language == "hi" else pattern["title"]
                return True, {
                    "pattern_id": pattern["id"],
                    "title": title,
                    "instructions": pattern["action_instructions"],
                    "severity": "CRITICAL_RED_FLAG",
                    "triage_level": "emergency_red_flag"
                }

        return False, None

    def detect_red_flags(self, text: str, current_step: str = "chief_complaint", language: str = "en") -> Optional[Dict[str, Any]]:
        is_flag, details = self.scan_for_red_flags(text, language)
        if is_flag and details:
            return {
                "alert_title": details["title"],
                "instructions": details["instructions"],
                "severity": details["severity"],
                "pattern_id": details["pattern_id"]
            }
        return None

triage_service = TriageService()

