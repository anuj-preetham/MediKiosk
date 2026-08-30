from typing import Dict, Any, List

class AyushService:
    """
    AYUSH Case-Taking Engine supporting Dashavidha Pariksha & Ahara-Vihara
    """

    QUESTIONS = {
        "prakriti_body_frame": {
            "en": {
                "question": "How would you describe your body build and weight tendency?",
                "audio": "How would you describe your body build and weight tendency?",
                "options": [
                    {"label": "Slim, difficult to gain weight (Vata)", "value": "vata", "icon": "wind"},
                    {"label": "Medium, muscular, athletic build (Pitta)", "value": "pitta", "icon": "flame"},
                    {"label": "Broad, heavy build, gains weight easily (Kapha)", "value": "kapha", "icon": "droplets"}
                ]
            },
            "hi": {
                "question": "आपकी शारीरिक बनावट और वजन की प्रवृत्ति कैसी है?",
                "audio": "आपकी शारीरिक बनावट और वजन की प्रवृत्ति कैसी है?",
                "options": [
                    {"label": "दुबला-पतला, वजन बढ़ना मुश्किल (वात)", "value": "vata", "icon": "wind"},
                    {"label": "मध्यम, गठीला शरीर (पित्त)", "value": "pitta", "icon": "flame"},
                    {"label": "भारी शरीर, आसानी से वजन बढ़ना (कफ)", "value": "kapha", "icon": "droplets"}
                ]
            }
        },
        "prakriti_weather": {
            "en": {
                "question": "Which climate or weather affects you most uncomfortably?",
                "audio": "Which climate or weather affects you most uncomfortably?",
                "options": [
                    {"label": "Cold, dry and windy weather (Vata)", "value": "vata", "icon": "snowflake"},
                    {"label": "Hot, humid sunny weather (Pitta)", "value": "pitta", "icon": "sun"},
                    {"label": "Damp, cloudy and cold weather (Kapha)", "value": "kapha", "icon": "cloud-rain"}
                ]
            },
            "hi": {
                "question": "कौन सा मौसम आपको सबसे अधिक असहज करता है?",
                "audio": "कौन सा मौसम आपको सबसे अधिक असहज करता है?",
                "options": [
                    {"label": "ठंड और सूखी हवा (वात)", "value": "vata", "icon": "snowflake"},
                    {"label": "तेज धूप और गर्मी (पित्त)", "value": "pitta", "icon": "sun"},
                    {"label": "गीला, उमस और बादलों वाला मौसम (कफ)", "value": "kapha", "icon": "cloud-rain"}
                ]
            }
        },
        "agni_digestion": {
            "en": {
                "question": "How is your appetite and digestion pattern (Agni)?",
                "audio": "How is your appetite and digestion pattern?",
                "options": [
                    {"label": "Irregular / Unpredictable hunger (Vishama Agni)", "value": "vishama_agni", "icon": "activity"},
                    {"label": "Intense / Frequent strong hunger with acidity (Tikshna Agni)", "value": "tikshna_agni", "icon": "flame"},
                    {"label": "Low appetite / Heavy stomach after small meal (Manda Agni)", "value": "manda_agni", "icon": "clock"},
                    {"label": "Normal, regular hunger with proper digestion (Sama Agni)", "value": "sama_agni", "icon": "check-circle"}
                ]
            },
            "hi": {
                "question": "आपकी भूख और पाचन क्रिया (अग्नि) कैसी है?",
                "audio": "आपकी भूख और पाचन क्रिया कैसी है?",
                "options": [
                    {"label": "अनियमित/अस्थिर भूख (विषमाग्नि)", "value": "vishama_agni", "icon": "activity"},
                    {"label": "तीव्र भूख और एसिडिटी/जलन (तीक्ष्णाग्नि)", "value": "tikshna_agni", "icon": "flame"},
                    {"label": "कम भूख/थोड़े खाने पर भी भारीपन (मंदाग्नि)", "value": "manda_agni", "icon": "clock"},
                    {"label": "संतुलित और नियमित भूख (समाग्नि)", "value": "sama_agni", "icon": "check-circle"}
                ]
            }
        },
        "koshtha_bowel": {
            "en": {
                "question": "How are your bowel movements (Koshtha)?",
                "audio": "How are your bowel movements?",
                "options": [
                    {"label": "Hard, dry stools / prone to constipation (Krura Koshtha)", "value": "krura", "icon": "shield-alert"},
                    {"label": "Soft / Loose stools / easily responds to milk (Mridu Koshtha)", "value": "mridu", "icon": "feather"},
                    {"label": "Regular, normal smooth daily clearance (Madhyama Koshtha)", "value": "madhyama", "icon": "check"}
                ]
            },
            "hi": {
                "question": "आपका पेट साफ होने की स्थिति (कोष्ठ) कैसी रहती है?",
                "audio": "आपका पेट साफ होने की स्थिति कैसी रहती है?",
                "options": [
                    {"label": "कड़ा मल / कब्ज की प्रवृत्ति (क्रूर कोष्ठ)", "value": "krura", "icon": "shield-alert"},
                    {"label": "नरम/ढीला मल, दूध पीने पर भी तुरंत दस्त (मृदु कोष्ठ)", "value": "mridu", "icon": "feather"},
                    {"label": "नियमित और सामान्य (मध्यम कोष्ठ)", "value": "madhyama", "icon": "check"}
                ]
            }
        },
        "ahara_vihara_diet": {
            "en": {
                "question": "What is your typical diet type and meal timing habit?",
                "audio": "What is your typical diet type and meal timing habit?",
                "options": [
                    {"label": "Vegetarian - Regular timings", "value": "veg_regular", "icon": "apple"},
                    {"label": "Vegetarian - Irregular / Late night meals", "value": "veg_irregular", "icon": "moon"},
                    {"label": "Mixed Diet (Non-Veg) - Regular", "value": "mixed_regular", "icon": "utensils"},
                    {"label": "Mixed Diet - Spicy / Fried / Irregular", "value": "mixed_spicy", "icon": "flame"}
                ]
            },
            "hi": {
                "question": "आपका सामान्य खान-पान और समय कैसा रहता है?",
                "audio": "आपका सामान्य खान-पान और समय कैसा रहता है?",
                "options": [
                    {"label": "शाकाहारी - नियमित समय", "value": "veg_regular", "icon": "apple"},
                    {"label": "शाकाहारी - देर रात / अनियमित", "value": "veg_irregular", "icon": "moon"},
                    {"label": "मिश्रित (मांसाहारी) - नियमित", "value": "mixed_regular", "icon": "utensils"},
                    {"label": "मिश्रित - अधिक मसालेदार/तला हुआ", "value": "mixed_spicy", "icon": "flame"}
                ]
            }
        }
    }

    def get_question(self, step_key: str, language: str = "en") -> Dict[str, Any]:
        lang = language if language in ["en", "hi"] else "en"
        data = self.QUESTIONS.get(step_key, self.QUESTIONS["prakriti_body_frame"])
        return data[lang]

    def calculate_assessment(self, answers: Dict[str, str]) -> Dict[str, Any]:
        vata_score = 0
        pitta_score = 0
        kapha_score = 0

        # Count scores
        for k, v in answers.items():
            if "vata" in v.lower():
                vata_score += 35
            if "pitta" in v.lower():
                pitta_score += 35
            if "kapha" in v.lower():
                kapha_score += 35

        # Normalize
        total = max(1, vata_score + pitta_score + kapha_score)
        v_pct = round((vata_score / total) * 100)
        p_pct = round((pitta_score / total) * 100)
        k_pct = 100 - v_pct - p_pct

        # Dominant Prakriti
        scores = {"Vata": v_pct, "Pitta": p_pct, "Kapha": k_pct}
        sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_doshas[0][1] - sorted_doshas[1][1] <= 15:
            dominant = f"{sorted_doshas[0][0]}-{sorted_doshas[1][0]} (Dvidoshaja)"
        else:
            dominant = f"{sorted_doshas[0][0]} (Ekadoshaja)"

        # Agni Status
        raw_agni = answers.get("agni_digestion", "sama_agni")
        agni_map = {
            "vishama_agni": "Vishama Agni (Irregular / Vata dominant)",
            "tikshna_agni": "Tikshna Agni (Intense / Hyperactive Pitta)",
            "manda_agni": "Manda Agni (Sluggish / Kapha dominant)",
            "sama_agni": "Sama Agni (Balanced Equilibrium)"
        }

        # Koshtha Status
        raw_koshtha = answers.get("koshtha_bowel", "madhyama")
        koshtha_map = {
            "krura": "Krura Koshtha (Hard / Vata dominant)",
            "mridu": "Mridu Koshtha (Soft / Pitta dominant)",
            "madhyama": "Madhyama Koshtha (Normal balanced)"
        }

        return {
            "prakriti_primary": dominant,
            "prakriti_scores": scores,
            "agni_status": agni_map.get(raw_agni, raw_agni),
            "koshtha_status": koshtha_map.get(raw_koshtha, raw_koshtha),
            "samhanana": "Madhyama (Medium Build)",
            "ahara_shakti": "Madhyama (Moderate Intake Capacity)",
            "vyayama_shakti": "Madhyama (Moderate Exercise Capacity)",
            "ahara_vihara": {
                "diet_pattern": answers.get("ahara_vihara_diet", "Vegetarian"),
                "lifestyle_factors": "Desk job, mild sleep irregularity"
            }
        }

ayush_service = AyushService()
