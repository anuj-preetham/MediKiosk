import os
import json
import logging
from typing import Dict, Any, List, Optional
from app.services.triage_service import triage_service
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """
    Advanced Clinical Dialogue & Dynamic SOCRATES Engine
    Powered by Gemini 2.5 Multimodal AI with structured clinical schemas and offline deterministic fallback.
    """

    SOCRATES_FLOW = [
        "chief_complaint",
        "site",
        "onset",
        "character",
        "radiation",
        "associated",
        "timing",
        "exacerbating",
        "severity"
    ]

    SOCRATES_QUESTIONS = {
        "chief_complaint": {
            "en": {
                "question": "Hello, welcome to MediKiosk. What brings you to the hospital today? You can speak into the microphone or select below.",
                "audio": "Welcome to MediKiosk. Please tell me your main health concern today.",
                "options": [
                    {"label": "Stomach Pain & Acidity", "value": "Stomach pain, acidity, and burning sensation", "icon": "activity"},
                    {"label": "Fever, Cough & Cold", "value": "Fever, cold, body ache, and cough for 3 days", "icon": "thermometer"},
                    {"label": "Joint Pain & Stiffness", "value": "Severe joint pain and morning stiffness in knees", "icon": "bone"},
                    {"label": "Chest Discomfort / Heaviness", "value": "Mild chest heaviness and breathlessness", "icon": "heart"},
                    {"label": "Skin Rash & Itching", "value": "Itchy red rash and patches on skin", "icon": "sparkles"}
                ]
            },
            "hi": {
                "question": "नमस्ते, मेडीकियोस्क में आपका स्वागत है। आज आप अस्पताल किस मुख्य समस्या के लिए आए हैं? आप माइक में बोल सकते हैं या नीचे विकल्प चुन सकते हैं।",
                "audio": "नमस्ते। कृपया आज की अपनी मुख्य स्वास्थ्य समस्या बताएं।",
                "options": [
                    {"label": "पेट दर्द और गैस / एसिडिटी", "value": "पेट में दर्द, जलन और एसिडिटी की समस्या", "icon": "activity"},
                    {"label": "बुखार, खांसी और जुकाम", "value": "3 दिन से बुखार, खांसी और बदन दर्द", "icon": "thermometer"},
                    {"label": "जोड़ों में दर्द व जकड़न", "value": "घुटनों और जोड़ों में तेज दर्द व अकड़न", "icon": "bone"},
                    {"label": "सीने में भारीपन व सांस फूलना", "value": "सीने में भारीपन और चलने पर सांस फूलना", "icon": "heart"},
                    {"label": "त्वचा पर खुजली और चकत्ते", "value": "त्वचा पर लाल चकत्ते और तेज खुजली", "icon": "sparkles"}
                ]
            }
        },
        "site": {
            "en": {
                "question": "Where exactly is the discomfort or pain located? You can also tap on the body map.",
                "audio": "Where exactly is the discomfort located?",
                "options": [
                    {"label": "Upper Abdomen (Epigastric)", "value": "Upper center abdomen below ribcage", "icon": "map-pin"},
                    {"label": "Retrosternal Chest", "value": "Center of the chest", "icon": "heart"},
                    {"label": "Lower Abdomen / Pelvic", "value": "Lower abdomen and pelvic region", "icon": "map-pin"},
                    {"label": "Both Knees / Large Joints", "value": "Bilateral knee joints and ankles", "icon": "bone"}
                ]
            },
            "hi": {
                "question": "तकलीफ या दर्द शरीर के किस हिस्से में हो रहा है? आप बॉडी मैप पर भी छू सकते हैं।",
                "audio": "दर्द शरीर के किस हिस्से में है?",
                "options": [
                    {"label": "पेट के ऊपरी हिस्से (सीने के नीचे)", "value": "पेट के ऊपरी मध्य भाग में", "icon": "map-pin"},
                    {"label": "सीने के मध्य भाग में", "value": "सीने के बीचों-बीच", "icon": "heart"},
                    {"label": "पेट के निचले हिस्से में", "value": "पेट के निचले हिस्से में", "icon": "map-pin"},
                    {"label": "दोनों घुटनों / जोड़ों में", "value": "दोनों घुटनों और जोड़ों में", "icon": "bone"}
                ]
            }
        },
        "onset": {
            "en": {
                "question": "When did this problem start, and how did it begin?",
                "audio": "When did it start and how did it begin?",
                "options": [
                    {"label": "Suddenly today (Acute)", "value": "Started suddenly today", "icon": "zap"},
                    {"label": "Gradually over 2-3 days", "value": "Developed gradually over 2 to 3 days", "icon": "clock"},
                    {"label": "Ongoing for 2-4 weeks", "value": "Present for 2 to 4 weeks", "icon": "calendar"},
                    {"label": "Chronic (More than 3 months)", "value": "Chronic issue for over 3 months", "icon": "repeat"}
                ]
            },
            "hi": {
                "question": "यह समस्या कब शुरू हुई और कैसे शुरू हुई?",
                "audio": "यह समस्या कब शुरू हुई?",
                "options": [
                    {"label": "अचानक आज ही शुरू हुआ (तीव्र)", "value": "आज अचानक शुरू हुआ", "icon": "zap"},
                    {"label": "धीरे-धीरे 2-3 दिनों में बढ़ा", "value": "2-3 दिनों से धीरे-धीरे बढ़ रहा है", "icon": "clock"},
                    {"label": "2 से 4 हफ्तों से चल रहा है", "value": "2 से 4 हफ्तों से है", "icon": "calendar"},
                    {"label": "पुराना (3 महीने से ज्यादा)", "value": "3 महीने से अधिक पुराना है", "icon": "repeat"}
                ]
            }
        },
        "character": {
            "en": {
                "question": "How would you describe the feeling of the pain or discomfort?",
                "audio": "How does the pain feel?",
                "options": [
                    {"label": "Burning sensation / Acid reflux", "value": "Burning / Sour eructations", "icon": "flame"},
                    {"label": "Dull ache / Heaviness", "value": "Constant dull ache and heaviness", "icon": "shield"},
                    {"label": "Sharp / Cramping spasmodic pain", "value": "Sharp cramping spasms", "icon": "activity"},
                    {"label": "Throbbing / Pulsating", "value": "Throbbing pulsating discomfort", "icon": "heart"}
                ]
            },
            "hi": {
                "question": "दर्द या तकलीफ का अहसास कैसा है?",
                "audio": "दर्द का अहसास कैसा है?",
                "options": [
                    {"label": "जलन / खट्टी डकारें", "value": "पेट में जलन और खट्टी डकार", "icon": "flame"},
                    {"label": "हल्का भारीपन व मंद दर्द", "value": "लगातार मंद दर्द और भारीपन", "icon": "shield"},
                    {"label": "तीखा मरोड़ / ऐंठन भरा दर्द", "value": "तेज ऐंठन और मरोड़", "icon": "activity"},
                    {"label": "टीस / धड़कन जैसा दर्द", "value": "टीस मारने वाला दर्द", "icon": "heart"}
                ]
            }
        },
        "radiation": {
            "en": {
                "question": "Does the discomfort spread or travel to any other area (like back, neck, or arms)?",
                "audio": "Does the discomfort spread anywhere else?",
                "options": [
                    {"label": "No, stays in one spot", "value": "Localized, no radiation", "icon": "crosshair"},
                    {"label": "Spreads to middle of back", "value": "Radiates straight to the back", "icon": "arrow-right"},
                    {"label": "Radiates up to throat / chest", "value": "Radiates upward to chest and throat", "icon": "arrow-up"},
                    {"label": "Down the legs / arms", "value": "Radiates down the extremities", "icon": "arrow-down"}
                ]
            },
            "hi": {
                "question": "क्या यह दर्द कहीं और फैलता है (जैसे पीठ, गले या हाथों-पैरों में)?",
                "audio": "क्या यह दर्द कहीं और फैलता है?",
                "options": [
                    {"label": "नहीं, एक ही जगह रहता है", "value": "एक ही जगह सीमित है", "icon": "crosshair"},
                    {"label": "पीठ के पीछे की तरफ फैलता है", "value": "पीठ की ओर फैलता है", "icon": "arrow-right"},
                    {"label": "ऊपर सीने और गले तक आता है", "value": "सीने व गले की तरफ जलन फैलती है", "icon": "arrow-up"},
                    {"label": "हाथों या पैरों की तरफ", "value": "हाथ-पैरों की ओर फैलता है", "icon": "arrow-down"}
                ]
            }
        },
        "associated": {
            "en": {
                "question": "Are there any other associated symptoms you have noticed?",
                "audio": "Are there any other associated symptoms?",
                "options": [
                    {"label": "Nausea, bloating & loss of appetite", "value": "Nausea, gas bloating, decreased appetite", "icon": "frown"},
                    {"label": "Fever, chills & body weakness", "value": "Mild fever, chills, fatigue", "icon": "thermometer"},
                    {"label": "Morning stiffness & swelling", "value": "Joint stiffness in morning, mild swelling", "icon": "bone"},
                    {"label": "None of these", "value": "No other associated symptoms", "icon": "check"}
                ]
            },
            "hi": {
                "question": "क्या इसके साथ अन्य कोई लक्षण भी महसूस हो रहे हैं?",
                "audio": "क्या कोई अन्य लक्षण भी हैं?",
                "options": [
                    {"label": "जी मिचलाना, पेट फूलना व भूख न लगना", "value": "जी मिचलाना, गैस और भूख में कमी", "icon": "frown"},
                    {"label": "हल्का बुखार, ठंड लगना व थकान", "value": "हल्का बुखार और कमजोरी", "icon": "thermometer"},
                    {"label": "सुबह जोड़ों में अकड़न व हल्की सूजन", "value": "सुबह जोड़ों में अकड़न और सूजन", "icon": "bone"},
                    {"label": "इनमें से कोई नहीं", "value": "कोई अन्य लक्षण नहीं", "icon": "check"}
                ]
            }
        },
        "timing": {
            "en": {
                "question": "Is the discomfort continuous throughout the day or does it come and go?",
                "audio": "Does it come and go, or is it continuous?",
                "options": [
                    {"label": "Worse after meals / exertion", "value": "Aggravated after food or exertion", "icon": "utensils"},
                    {"label": "Worse on empty stomach / early morning", "value": "More severe on empty stomach", "icon": "sun"},
                    {"label": "Continuous all day long", "value": "Constant without break", "icon": "clock"},
                    {"label": "Comes in intermittent waves", "value": "Intermittent episodic waves", "icon": "activity"}
                ]
            },
            "hi": {
                "question": "क्या तकलीफ पूरे दिन लगातार रहती है या किसी खास समय बढ़ती है?",
                "audio": "क्या तकलीफ किसी खास समय बढ़ती है?",
                "options": [
                    {"label": "खाना खाने या परिश्रम के बाद बढ़ती है", "value": "खाने या मेहनत के बाद तकलीफ बढ़ती है", "icon": "utensils"},
                    {"label": "खाली पेट या सुबह अधिक होती है", "value": "खाली पेट ज्यादा जलन होती है", "icon": "sun"},
                    {"label": "पूरे दिन लगातार बनी रहती है", "value": "पूरे दिन निरंतर रहती है", "icon": "clock"},
                    {"label": "रुक-रुक कर लहरों की तरह आती है", "value": "रुक-रुक कर आती है", "icon": "activity"}
                ]
            }
        },
        "exacerbating": {
            "en": {
                "question": "Does anything specific make it feel better or worse?",
                "audio": "What makes it better or worse?",
                "options": [
                    {"label": "Antacids or food give temporary relief", "value": "Relieved by antacids/food", "icon": "check-circle"},
                    {"label": "Rest helps; movement/walking makes it worse", "value": "Relieved with rest; aggravated with exertion", "icon": "pause"},
                    {"label": "Warm compression relieves", "value": "Relieved by warm water / heat application", "icon": "flame"},
                    {"label": "Nothing brings clear relief", "value": "No specific relieving factor", "icon": "help-circle"}
                ]
            },
            "hi": {
                "question": "क्या किसी चीज से आराम मिलता है या तकलीफ बढ़ जाती है?",
                "audio": "किस चीज से आराम या तकलीफ बढ़ती है?",
                "options": [
                    {"label": "दवा या भोजन से आराम मिलता है", "value": "दवा/दूध से आराम मिलता है", "icon": "check-circle"},
                    {"label": "आराम करने से घटता है; चलने पर बढ़ता है", "value": "आराम से राहत; चलने-फिरने से दर्द बढ़ता है", "icon": "pause"},
                    {"label": "गर्म पानी / सिकाई से आराम मिलता है", "value": "गर्म सिकाई से आराम", "icon": "flame"},
                    {"label": "किसी चीज से विशेष आराम नहीं", "value": "कोई स्पष्ट राहत नहीं", "icon": "help-circle"}
                ]
            }
        },
        "severity": {
            "en": {
                "question": "On a scale of 1 to 10 (where 1 is very mild and 10 is unbearable), how severe is it right now?",
                "audio": "On a scale of 1 to 10, how severe is it?",
                "options": [
                    {"label": "Mild (1 to 3 / 10)", "value": "Mild (2-3/10) - Noticeable but manageable", "icon": "smile"},
                    {"label": "Moderate (4 to 6 / 10)", "value": "Moderate (5/10) - Interferes with daily work", "icon": "meh"},
                    {"label": "Severe (7 to 8 / 10)", "value": "Severe (7-8/10) - Significant distress", "icon": "frown"},
                    {"label": "Very Severe (9 to 10 / 10)", "value": "Very Severe (9-10/10) - Extreme pain", "icon": "alert-octagon"}
                ]
            },
            "hi": {
                "question": "1 से 10 के पैमाने पर (जहाँ 1 हल्का और 10 असहनीय है), अभी दर्द कितना तीव्र है?",
                "audio": "1 से 10 के पैमाने पर दर्द कितना तीव्र है?",
                "options": [
                    {"label": "हल्का (1 से 3 / 10)", "value": "हल्का (2-3/10)", "icon": "smile"},
                    {"label": "मध्यम (4 से 6 / 10)", "value": "मध्यम (5/10) - कामकाज प्रभावित", "icon": "meh"},
                    {"label": "तेज दर्द (7 से 8 / 10)", "value": "तेज दर्द (7-8/10)", "icon": "frown"},
                    {"label": "अत्यधिक असहनीय (9 से 10 / 10)", "value": "अत्यधिक असहनीय (9-10/10)", "icon": "alert-octagon"}
                ]
            }
        }
    }

    def _call_gemini_adaptive_turn(
        self,
        current_step: str,
        user_message: str,
        language: str,
        socrates_history: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Dynamically query Gemini 2.5 Flash for contextual clinical reasoning and follow-up options.
        """
        api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            return None

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = f"""
You are MediKiosk AI, an empathetic, highly structured clinical intake assistant in an Indian hospital OPD.
Language: {language} (en or hi).
Current SOCRATES Step: {current_step}
Patient Input: "{user_message}"
History Collected So Far: {json.dumps(socrates_history, ensure_ascii=False)}

Generate a patient-friendly response for the next clinical intake step.
Respond strictly in JSON format matching this schema:
{{
  "next_step": "site|onset|character|radiation|associated|timing|exacerbating|severity|socrates_completed",
  "question": "string (the next question to ask the patient)",
  "audio_text": "short audio summary sentence for voice readout",
  "quick_options": [
     {{"label": "Option text", "value": "Detailed clinical value", "icon": "activity|heart|map-pin|clock|flame"}}
  ]
}}
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            if response.text:
                return json.loads(response.text)
        except Exception as e:
            logger.warning(f"Gemini API dynamic call skipped or failed ({e}), falling back to deterministic engine.")
            return None

    def process_turn(
        self,
        current_step: str,
        user_message: str,
        language: str = "en",
        extracted_socrates: Optional[Dict[str, Any]] = None,
        body_location: Optional[str] = None
    ) -> Dict[str, Any]:
        lang = language if language in ["en", "hi"] else "en"
        socrates_data = extracted_socrates or {}

        # 1. Real-time Red-Flag Check
        is_red_flag, flag_info = triage_service.scan_for_red_flags(user_message, language=lang)
        if is_red_flag:
            return {
                "ai_reply": f"⚠️ ALERT: {flag_info['title']}. {flag_info['instructions']}",
                "ai_reply_audio_text": flag_info["title"],
                "language": lang,
                "current_step": current_step,
                "next_step": "red_flag_triaged",
                "quick_options": [],
                "is_red_flag": True,
                "red_flag_alert_title": flag_info["title"],
                "red_flag_instructions": flag_info["instructions"],
                "extracted_socrates": socrates_data,
                "progress_percentage": 100
            }

        # 2. Update extracted SOCRATES entity
        socrates_data[current_step] = user_message
        if body_location and "body_site" not in socrates_data:
            socrates_data["body_site"] = body_location

        # 3. Try dynamic Gemini response first
        gemini_result = self._call_gemini_adaptive_turn(current_step, user_message, lang, socrates_data)
        if gemini_result and "question" in gemini_result:
            next_step = gemini_result.get("next_step", "socrates_completed")
            idx_for_prog = self.SOCRATES_FLOW.index(next_step) if next_step in self.SOCRATES_FLOW else len(self.SOCRATES_FLOW)
            return {
                "ai_reply": gemini_result["question"],
                "ai_reply_audio_text": gemini_result.get("audio_text", gemini_result["question"]),
                "language": lang,
                "current_step": next_step,
                "next_step": next_step,
                "quick_options": gemini_result.get("quick_options", []),
                "is_red_flag": False,
                "extracted_socrates": socrates_data,
                "progress_percentage": int((idx_for_prog / len(self.SOCRATES_FLOW)) * 100)
            }

        # 4. Deterministic Clinical sequence fallback
        try:
            current_idx = self.SOCRATES_FLOW.index(current_step)
            if current_idx < len(self.SOCRATES_FLOW) - 1:
                next_step = self.SOCRATES_FLOW[current_idx + 1]
            else:
                next_step = "socrates_completed"
        except ValueError:
            next_step = "site"

        # Calculate progress
        idx_for_progress = self.SOCRATES_FLOW.index(next_step) if next_step in self.SOCRATES_FLOW else len(self.SOCRATES_FLOW)
        progress_pct = int((idx_for_progress / len(self.SOCRATES_FLOW)) * 100)

        # Fetch question
        if next_step != "socrates_completed":
            question_info = self.SOCRATES_QUESTIONS[next_step][lang]
            reply_text = question_info["question"]
            audio_text = question_info["audio"]
            options = question_info["options"]
        else:
            if lang == "hi":
                reply_text = "धन्यवाद। आपकी मुख्य समस्या और लक्षणों का विवरण दर्ज कर लिया गया है। अब आप अपनी जीवनशैली का विवरण दे सकते हैं या पुराने पर्चे/रिपोर्ट स्कैन कर सकते हैं।"
                audio_text = "धन्यवाद। आपकी मुख्य समस्या का विवरण दर्ज हो गया है।"
            else:
                reply_text = "Thank you. Your clinical symptoms and history of present illness have been recorded. You can now record your medical/lifestyle history or upload prior medical records."
                audio_text = "Thank you. Your clinical history has been recorded."
            options = [
                {"label": "Review Lifestyle & Medical History" if lang == "en" else "जीवनशैली एवं पूर्व इतिहास जोड़ें", "value": "start_lifestyle", "icon": "user-check"},
                {"label": "Upload Past Prescriptions / Reports" if lang == "en" else "पुराने पर्चे/रिपोर्ट स्कैन करें", "value": "upload_docs", "icon": "file-text"}
            ]

        return {
            "ai_reply": reply_text,
            "ai_reply_audio_text": audio_text,
            "language": lang,
            "current_step": next_step,
            "next_step": next_step,
            "quick_options": options,
            "is_red_flag": False,
            "extracted_socrates": socrates_data,
            "progress_percentage": progress_pct
        }

ai_service = AIService()
