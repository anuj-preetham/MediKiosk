import re
from typing import List, Dict, Any, Optional

class SafetyService:
    """
    Clinical Safety Engine:
    1. Drug-Allergy Cross-Reactivity Checker
    2. Drug-Drug Interaction Warnings
    3. Clinical Contraindication Analysis
    """

    # Allergy class mappings and common brand/generic names
    ALLERGY_CLASSES = {
        "penicillin": {
            "name": "Beta-Lactam / Penicillin Group",
            "trigger_keywords": ["penicillin", "penicillins", "amoxicillin", "ampicillin", "augmentin", "cloxacillin", "piperacillin", "piperacillin-tazobactam", "z菌素", "पेनिसिलिन"],
            "cross_reactivity": [
                "amoxicillin", "ampicillin", "augmentin", "moxikind", "clavum", "amoxyclav",
                "cloxacillin", "piperacillin", "tazobactam", "ampiclox", "penicillin-v",
                "benzylpenicillin", "cephalexin", "cefixime", "ceftriaxone", "cefuroxime"
            ],
            "severity": "CRITICAL_CONTRAINDICATION",
            "clinical_advice": "HIGH RISK: Patient has documented Penicillin allergy. Beta-lactam antibiotics may cause anaphylaxis or severe hypersensitivity. Consider non-beta-lactam alternatives (e.g. Macrolides, Fluoroquinolones, Doxycycline)."
        },
        "sulfa": {
            "name": "Sulfonamide Group",
            "trigger_keywords": ["sulfa", "sulfonamide", "sulfur", "सल्फा"],
            "cross_reactivity": [
                "bactrim", "septra", "cotrimoxazole", "sulfamethoxazole", "trimethoprim",
                "sulfasalazine", "silver sulfadiazine", "furosemide", "hydrochlorothiazide", "glimepiride"
            ],
            "severity": "WARNING",
            "clinical_advice": "WARNING: Patient reports Sulfa allergy. Cross-reaction with sulfonamide antimicrobials or high-risk diuretics may cause cutaneous eruptions or Steven-Johnson Syndrome."
        },
        "nsaid": {
            "name": "NSAID / Aspirin Group",
            "trigger_keywords": ["nsaid", "nsaids", "aspirin", "ibuprofen", "painkiller", "diclofenac", "दर्द निवारक"],
            "cross_reactivity": [
                "aspirin", "ibuprofen", "diclofenac", "naproxen", "ketorolac", "mefenamic",
                "aceclofenac", "etoricoxib", "indomethacin", "piroxicam", "combiflam", "voveran", "brufen"
            ],
            "severity": "WARNING",
            "clinical_advice": "WARNING: Patient reports NSAID sensitivity / bronchospasm or peptic ulceration risk. Avoid non-selective COX inhibitors. Consider Paracetamol or topical analgesics."
        },
        "paracetamol": {
            "name": "Acetaminophen / Paracetamol",
            "trigger_keywords": ["paracetamol", "pcm", "acetaminophen", "calpol", "crocin", "dolo", "पैरासिटामोल"],
            "cross_reactivity": ["paracetamol", "acetaminophen", "dolo", "crocin", "calpol", "pacimol", "pyregesic"],
            "severity": "CRITICAL_CONTRAINDICATION",
            "clinical_advice": "CRITICAL: Patient reports Paracetamol hypersensitivity or hepatic intolerance. Avoid all Paracetamol formulations."
        },
        "ciprofloxacin": {
            "name": "Fluoroquinolone Group",
            "trigger_keywords": ["cipro", "ciprofloxacin", "ofloxacin", "levofloxacin", "quinolone"],
            "cross_reactivity": ["ciprofloxacin", "ofloxacin", "levofloxacin", "norfloxacin", "moxifloxacin", "ciptox", "cifran", "zoxan"],
            "severity": "WARNING",
            "clinical_advice": "WARNING: Documented Fluoroquinolone allergy. Risk of tendonitis, QT prolongation, and severe rash."
        }
    }

    # High-risk drug-drug interactions
    DRUG_INTERACTIONS = [
        {
            "pair": ["warfarin", "aspirin"],
            "severity": "HIGH_RISK",
            "alert": "Major bleeding risk: Concurrent Warfarin and Aspirin significantly potentiates systemic hemorrhage.",
            "recommendation": "Monitor INR closely or adjust antiplatelet therapy."
        },
        {
            "pair": ["metformin", "contrast"],
            "severity": "MODERATE_RISK",
            "alert": "Risk of Contrast-Induced Nephropathy and Lactic Acidosis with Metformin.",
            "recommendation": "Hold Metformin for 48 hours before and after iodinated contrast imaging."
        },
        {
            "pair": ["ramipril", "spironolactone"],
            "severity": "MODERATE_RISK",
            "alert": "Risk of Severe Hyperkalemia with concurrent ACE inhibitor and Potassium-sparing diuretic.",
            "recommendation": "Check Serum Potassium and renal function within 1 week."
        }
    ]

    def check_drug_allergies(
        self,
        patient_allergies: List[str],
        medications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Cross-checks patient reported allergies against extracted medications.
        """
        safety_alerts = []
        if not patient_allergies or not medications:
            return safety_alerts

        cleaned_allergies = [a.lower().strip() for a in patient_allergies if a]

        # Identify which allergy classes are active for the patient
        active_classes = []
        for allergy in cleaned_allergies:
            for cls_key, cls_data in self.ALLERGY_CLASSES.items():
                if any(kw in allergy for kw in cls_data["trigger_keywords"]):
                    active_classes.append((cls_key, cls_data, allergy))

        # Check each prescribed medicine against active classes
        for med in medications:
            med_name = (med.get("name") or "").lower()
            if not med_name:
                continue

            for cls_key, cls_data, original_allergy in active_classes:
                is_match = any(re.search(r'\b' + re.escape(sub) + r'\b', med_name) or sub in med_name for sub in cls_data["cross_reactivity"])
                if is_match:
                    safety_alerts.append({
                        "type": "DRUG_ALLERGY_CONFLICT",
                        "severity": cls_data["severity"],
                        "medication": med.get("name"),
                        "allergy_trigger": original_allergy,
                        "allergy_class": cls_data["name"],
                        "clinical_advice": cls_data["clinical_advice"]
                    })

        return safety_alerts

    def check_drug_interactions(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Checks extracted medications for known interaction pairs.
        """
        interaction_alerts = []
        med_names = [(m.get("name") or "").lower() for m in medications if m.get("name")]
        
        for rule in self.DRUG_INTERACTIONS:
            p1, p2 = rule["pair"][0], rule["pair"][1]
            match_p1 = any(p1 in name for name in med_names)
            match_p2 = any(p2 in name for name in med_names)
            
            if match_p1 and match_p2:
                interaction_alerts.append({
                    "type": "DRUG_INTERACTION",
                    "severity": rule["severity"],
                    "drug_pair": rule["pair"],
                    "alert": rule["alert"],
                    "recommendation": rule["recommendation"]
                })

        return interaction_alerts

safety_service = SafetyService()
