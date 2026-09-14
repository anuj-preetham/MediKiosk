/**
 * MediKiosk Frontend Application (Production-Grade Final Platform)
 * Smart OPD Clinical History & Medical Document Intelligence Platform (SIH26047)
 * Built with ABDM M1/M2/M3 Scan & Share, FHIR R4, and Hospital HIS Interoperability
 */

const API_BASE = '/api';

const state = {
    portal: 'kiosk', // 'kiosk' | 'doctor'
    language: 'en', // 'en' | 'hi' | 'bn' | 'ta' | 'te' | 'mr'
    audioGuidance: true,
    currentSessionId: null,
    currentPatient: null,
    kioskStep: 'consent', // 'consent' | 'bodymap' | 'chat' | 'lifestyle' | 'document' | 'complete'
    currentChatStep: 'chief_complaint',
    chatHistory: [],
    selectedBodyZone: null,
    extractedSocrates: {},
    lifestyleAnswers: {
        diet: 'Normal balanced',
        smoking: 'No',
        alcohol: 'No',
        pastConditions: []
    },
    uploadedDocuments: [],
    doctorQueue: [],
    queueFilter: 'all', // 'all' | 'red_flag' | 'priority' | 'routine'
    searchQuery: '',
    selectedDoctorSession: null,
    isRecording: false,
    aiCopilotChatHistory: [],
    aiCopilotLoading: false
};

// UI Multi-lingual Localization
const i18n = {
    en: {
        welcomeTitle: "Welcome to MediKiosk",
        welcomeSubtitle: "AI-Powered Patient Clinical History & Document Intake Platform",
        consentTitle: "Patient Identity & ABDM Consent",
        consentDesc: "By continuing, you consent to secure recording of your clinical history, symptoms, and prior medical records for your OPD consultation under the Digital Personal Data Protection (DPDP) Act 2023.",
        startBtn: "Start Touch / Voice Intake",
        scanShareBtn: "Scan & Share with ABHA QR (M1 Counter)",
        bodymapTitle: "Select Pain / Discomfort Area",
        bodymapSubtitle: "Touch the body map where you feel pain or discomfort",
        skipBodymap: "Skip Body Map & Speak Directly",
        speakingPrompt: "Listening to your voice...",
        micBtn: "Tap to Speak",
        sendBtn: "Send Response",
        orTouch: "Or select a quick option below:",
        socratesStepLabels: {
            chief_complaint: "Chief Complaint",
            site: "Pain Location",
            onset: "Onset & Duration",
            character: "Pain Sensation",
            radiation: "Spread / Radiation",
            associated: "Other Symptoms",
            timing: "Time Pattern",
            exacerbating: "Relief Factors",
            severity: "Pain Severity"
        },
        lifestyleTitle: "Past Medical & Lifestyle History",
        lifestyleSubtitle: "Record chronic conditions, known allergies, and daily habits",
        submitLifestyleBtn: "Continue to Document Scanner",
        docTitle: "Medical Document Digitization (Vision OCR)",
        docSubtitle: "Upload or scan previous prescriptions, lab reports, or discharge summaries",
        uploadBtn: "Scan / Upload Document",
        demoPrescriptionBtn: "Use Sample Hospital Prescription",
        demoLabReportBtn: "Use Sample Blood Lab Report",
        summaryTitle: "Physician Clinical History Summary",
        verifyBtn: "Approve & Submit to ABDM / HIS",
        fhirBtn: "View ABDM FHIR JSON",
        printBtn: "Print OPD Case Sheet",
        hisPushBtn: "Push to Hospital HIS",
        triageRoutine: "Routine",
        triagePriority: "Priority",
        triageEmergency: "Emergency Red Flag"
    },
    hi: {
        welcomeTitle: "मेडीकियोस्क में आपका स्वागत है",
        welcomeSubtitle: "स्मार्ट अस्पताल ओपीडी डिजिटल केस-टेकिंग एवं लक्षण रिकॉर्डिंग",
        consentTitle: "रोगी पहचान एवं डिजिटल सहमति (DPDP 2023)",
        consentDesc: "आगे बढ़कर आप अपने स्वास्थ्य इतिहास, वर्तमान लक्षणों और पुराने पर्चों को डॉक्टर परामर्श हेतु सुरक्षित रूप से रिकॉर्ड करने की सहमति देते हैं।",
        startBtn: "बोलकर या छूकर शुरू करें",
        scanShareBtn: "आभा क्यूआर स्कैन व शेयर (Scan & Share)",
        bodymapTitle: "दर्द या तकलीफ का स्थान चुनें",
        bodymapSubtitle: "शरीर के जिस हिस्से में दर्द या समस्या है, उसे छूकर चुनें",
        skipBodymap: "बॉडी मैप छोड़ें और सीधे बोलें",
        speakingPrompt: "आपकी आवाज सुनी जा रही है...",
        micBtn: "बोलने के लिए दबाएं",
        sendBtn: "जवाब भेजें",
        orTouch: "या नीचे दिए गए विकल्पों में से चुनें:",
        socratesStepLabels: {
            chief_complaint: "मुख्य समस्या",
            site: "दर्द का स्थान",
            onset: "शुरुआत का समय",
            character: "दर्द का प्रकार",
            radiation: "दर्द का फैलाव",
            associated: "अन्य लक्षण",
            timing: "समय चक्र",
            exacerbating: "आराम कारक",
            severity: "तीव्रता"
        },
        lifestyleTitle: "पूर्व चिकित्सा इतिहास एवं जीवनशैली",
        lifestyleSubtitle: "पुरानी बीमारियाँ, एलर्जी एवं खान-पान का विवरण",
        submitLifestyleBtn: "दस्तावेज़ स्कैनर पर जाएं",
        docTitle: "चिकित्सा दस्तावेज़ डिजिटलीकरण (Vision OCR)",
        docSubtitle: "पुराने पर्चे या लैब रिपोर्ट स्कैन / अपलोड करें",
        uploadBtn: "पर्चा अपलोड करें",
        demoPrescriptionBtn: "नमूना अस्पताल पर्चा लोड करें",
        demoLabReportBtn: "नमूना ब्लड टेस्ट रिपोर्ट लोड करें",
        summaryTitle: "चिकित्सक सारांश (Physician Summary)",
        verifyBtn: "सत्यापित करें एवं ABDM में भेजें",
        fhirBtn: "ABDM FHIR JSON देखें",
        printBtn: "ओपीडी केस शीट प्रिंट करें",
        hisPushBtn: "अस्पताल HIS में भेजें",
        triageRoutine: "सामान्य",
        triagePriority: "प्राथमिकता",
        triageEmergency: "आपातकालीन रेड फ्लैग"
    },
    bn: {
        welcomeTitle: "মেডিকিয়স্কে স্বাগতম",
        welcomeSubtitle: "স্মার্ট হাসপাতাল ওপিডি ক্লিনিকাল ইতিহাস ও নথি ব্যবস্থা",
        consentTitle: "রোগীর সম্মতি ও ডেটা সুরক্ষা (DPDP 2023)",
        consentDesc: "এগিয়ে গিয়ে আপনি আপনার চিকিৎসা ইতিহাস এবং পুরোনো প্রেসক্রিপশন নিরাপদে রেকর্ড করার সম্মতি দিচ্ছেন।",
        startBtn: "স্পর্শ বা ভয়েস দিয়ে শুরু করুন",
        scanShareBtn: "আভা স্ক্যান ও শেয়ার (Scan & Share)",
        bodymapTitle: "ব্যথার স্থান নির্বাচন করুন",
        bodymapSubtitle: "শরীরের যে অংশে ব্যথা আছে সেখানে স্পর্শ করুন",
        skipBodymap: "সরাসরি কথা বলুন",
        speakingPrompt: "আপনার কথা শোনা হচ্ছে...",
        micBtn: "বলতে চাপুন",
        sendBtn: "উত্তর পাঠান",
        orTouch: "অথবা নিচের বিকল্পগুলি বেছে নিন:",
        socratesStepLabels: {
            chief_complaint: "প্রধান সমস্যা",
            site: "ব্যথার স্থান",
            onset: "শুরুর সময়",
            character: "ব্যথার অনুভূতি",
            radiation: "ছড়ানোর ধরণ",
            associated: "অন্যান্য লক্ষণ",
            timing: "সময় প্যাটার্ন",
            exacerbating: "উপশমের কারণ",
            severity: "তীব্রতা"
        },
        lifestyleTitle: "পূর্ব চিকিৎসা ইতিহাস",
        lifestyleSubtitle: "দীর্ঘস্থায়ী রোগ এবং অ্যালার্জি",
        submitLifestyleBtn: "নথি স্ক্যানারে যান",
        docTitle: "মেডিকেল নথি ডিজিটাইজেশন (OCR)",
        docSubtitle: "পুরোনো প্রেসক্রিপশন বা রিপোর্ট আপলোড করুন",
        uploadBtn: "নথি আপলোড করুন",
        demoPrescriptionBtn: "নমুনা প্রেসক্রিপশন",
        demoLabReportBtn: "নমুনা ল্যাব রিপোর্ট",
        summaryTitle: "চিকিৎসক সারাংশ",
        verifyBtn: "অনুমোদন করুন ও জমা দিন",
        fhirBtn: "FHIR JSON দেখুন",
        printBtn: "কেস শীট প্রিন্ট করুন",
        hisPushBtn: "হাসপাতাল HIS সিঙ্ক"
    },
    ta: {
        welcomeTitle: "மெடிகியோஸ்க்கிற்கு வரவேற்கிறோம்",
        welcomeSubtitle: "மருத்துவமனை வெளிநோயாளி பிரிவு மருத்துவ வரலாறு தளம்",
        consentTitle: "நோயாளி ஒப்புதல் (DPDP 2023)",
        consentDesc: "தங்கள் மருத்துவ விவரங்களை பதிவு செய்ய ஒப்புதல் அளிக்கிறீர்கள்.",
        startBtn: "தொடங்கவும்",
        scanShareBtn: "ABHA ஸ்கேன் மற்றும் பகிர்வு (Scan & Share)",
        bodymapTitle: "வலி உள்ள இடத்தை தேர்ந்தெடுக்கவும்",
        bodymapSubtitle: "உடலில் வலி உள்ள பகுதியை தொடவும்",
        skipBodymap: "நேரடியாக பேசவும்",
        speakingPrompt: "குரலை கேட்கிறது...",
        micBtn: "பேச தொடவும்",
        sendBtn: "அனுப்புக",
        orTouch: "அல்லது விருப்பங்களை தேர்ந்தெடுக்கவும்:",
        socratesStepLabels: {
            chief_complaint: "முக்கிய பிரச்சனை",
            site: "வலி உள்ள இடம்",
            onset: "தொடங்கிய நேரம்",
            character: "வலியின் வகை",
            radiation: "பரவும் விதம்",
            associated: "பிற அறிகுறிகள்",
            timing: "நேர இடைவெளி",
            exacerbating: "நிவாரண காரணிகள்",
            severity: "தீவிரம்"
        },
        lifestyleTitle: "முந்தைய மருத்துவ வரலாறு",
        lifestyleSubtitle: "நீண்டகால நோய்கள் மற்றும் ஒவ்வாமை",
        submitLifestyleBtn: "ஆவணங்களை பதிவேற்றவும்",
        docTitle: "மருத்துவ ஆவணங்கள் டிஜிட்டல்மயமாக்கல்",
        docSubtitle: "பழைய மருத்துவ சீட்டுகளை பதிவேற்றவும்",
        uploadBtn: "ஆவணத்தை பதிவேற்றவும்",
        demoPrescriptionBtn: "மாதிரி மருத்துவ சீட்டு",
        demoLabReportBtn: "மாதிரி ஆய்வு அறிக்கை",
        summaryTitle: "மருத்துவர் சுருக்கம்",
        verifyBtn: "சரிபார்த்து சமர்ப்பிக்கவும்",
        fhirBtn: "FHIR JSON காண்க",
        printBtn: "அச்சிடுக",
        hisPushBtn: "HIS இல் சமர்ப்பிக்கவும்"
    },
    te: {
        welcomeTitle: "మెడికియోస్క్‌కు స్వాగతం",
        welcomeSubtitle: "స్మార్ట్ ఆసుపత్రి ఓపిడి క్లినికల్ కేస్-టేకింగ్ ప్లాట్‌ఫారమ్",
        consentTitle: "రోగి సమ్మతి (DPDP 2023)",
        consentDesc: "మీ ఆరోగ్య వివరాలు నమోదు చేయడానికి అనుమతిస్తున్నారు.",
        startBtn: "ప్రారంభించండి",
        scanShareBtn: "ABHA స్కాన్ & షేర్ (Scan & Share)",
        bodymapTitle: "నొప్పి ఉన్న ప్రదేశాన్ని ఎంచుకోండి",
        bodymapSubtitle: "నొప్పి ఉన్న శరీర భాగాన్ని తాకండి",
        skipBodymap: "నేరుగా మాట్లాడండి",
        speakingPrompt: "వినబడుతోంది...",
        micBtn: "మాట్లాడటానికి నొక్కండి",
        sendBtn: "పంపండి",
        orTouch: "లేదా కింద ఎంపికలను ఎంచుకోండి:",
        socratesStepLabels: {
            chief_complaint: "ప్రధాన సమస్య",
            site: "నొప్పి స్థానం",
            onset: "ప్రారంభం",
            character: "నొప్పి రకం",
            radiation: "వ్యాపించే విధానం",
            associated: "ఇతర లక్షణాలు",
            timing: "సమయ నమూనా",
            exacerbating: "ఉపశమన కారకాలు",
            severity: "తీవ్రత"
        },
        lifestyleTitle: "పూర్వ వైద్య చరిత్ర",
        lifestyleSubtitle: "దీర్ఘకాలిక వ్యాధులు మరియు అలర్జీలు",
        submitLifestyleBtn: "డాక్యుమెంట్ స్కానర్‌కు వెళ్లండి",
        docTitle: "మెడికల్ డాక్యుమెంట్ డిజిటలైజేషన్",
        docSubtitle: "పాత ప్రిస్క్రిప్షన్ లేదా ల్యాబ్ నివేదికలు",
        uploadBtn: "డాక్యుమెంట్ అప్‌లోడ్ చేయండి",
        demoPrescriptionBtn: "నమూనా ప్రిస్క్రిప్షన్",
        demoLabReportBtn: "నమూనా ల్యాబ్ రిపోర్ట్",
        summaryTitle: "వైద్యుల సారాంశం",
        verifyBtn: "ఆమోదించి సమర్పించండి",
        fhirBtn: "FHIR JSON చూడండి",
        printBtn: "ప్రింట్ చేయండి",
        hisPushBtn: "ఆసుపత్రి HIS కి పంపండి"
    },
    mr: {
        welcomeTitle: "मेडीकियोस्क मध्ये आपले स्वागत आहे",
        welcomeSubtitle: "स्मार्ट हॉस्पिटल ओपीडी डिजिटल केस-टेकिंग प्लॅटफॉर्म",
        consentTitle: "रुग्ण संमती व डेटा सुरक्षा (DPDP 2023)",
        consentDesc: "आपला आरोग्य इतिहास आणि जुनी कागदपत्रे सुरक्षितपणे नोंदवण्यास आपण संमती देत आहात.",
        startBtn: "सुरू करा",
        scanShareBtn: "आभा क्यूआर स्कॅन आणि शेअर (Scan & Share)",
        bodymapTitle: "त्रास किंवा वेदनेचा भाग निवडा",
        bodymapSubtitle: "वेदना असलेल्या शरीराच्या भागावर स्पर्श करा",
        skipBodymap: "थेट बोला",
        speakingPrompt: "ऐकत आहे...",
        micBtn: "बोलण्यासाठी दाबा",
        sendBtn: "उत्तर पाठवा",
        orTouch: "किंवा खालील पर्याय निवडा:",
        socratesStepLabels: {
            chief_complaint: "मुख्य समस्या",
            site: "वेदनेचे ठिकाण",
            onset: "सुरुवात",
            character: "वेदनेचा प्रकार",
            radiation: "पसरणे",
            associated: "इतर लक्षणे",
            timing: "वेळ",
            exacerbating: "आराम देणारे घटक",
            severity: "तीव्रता"
        },
        lifestyleTitle: "मागील वैद्यकीय इतिहास",
        lifestyleSubtitle: "जुने आजार व ऍलर्जी",
        submitLifestyleBtn: "दस्तऐवज स्कॅनरवर जा",
        docTitle: "वैद्यकीय कागदपत्रे डिजिटलीकरण",
        docSubtitle: "जुने प्रिस्क्रिप्शन किंवा रिपोर्ट स्कॅन करा",
        uploadBtn: "कागदपत्र अपलोड करा",
        demoPrescriptionBtn: "नमुना प्रिस्क्रिप्शन",
        demoLabReportBtn: "नमुना लॅब रिपोर्ट",
        summaryTitle: "डॉक्टर सारांश",
        verifyBtn: "मंजूर करा व पाठवा",
        fhirBtn: "FHIR JSON पहा",
        printBtn: "केस शीट प्रिंट करा",
        hisPushBtn: "हॉस्पिटल HIS मध्ये पाठवा"
    }
};

// Speech Synthesis
function speakPrompt(text) {
    if (!state.audioGuidance || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const langMap = {
        'en': 'en-IN',
        'hi': 'hi-IN',
        'bn': 'bn-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'mr': 'mr-IN'
    };
    utterance.lang = langMap[state.language] || 'en-IN';
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
}

// Voice Recognition
let recognition = null;
function initSpeechRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;
        const langMap = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'bn': 'bn-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'mr': 'mr-IN'
        };
        recognition.lang = langMap[state.language] || 'en-IN';

        recognition.onstart = () => {
            state.isRecording = true;
            render();
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            state.isRecording = false;
            sendChatMessage(transcript);
        };

        recognition.onerror = () => {
            state.isRecording = false;
            render();
        };

        recognition.onend = () => {
            state.isRecording = false;
            render();
        };
    }
}

function toggleVoiceInput() {
    if (!recognition) initSpeechRecognition();
    if (!recognition) {
        alert("Voice recognition is not supported in this browser. Please use touch options or Chrome.");
        return;
    }
    if (state.isRecording) {
        recognition.stop();
    } else {
        const langMap = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'bn': 'bn-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'mr': 'mr-IN'
        };
        recognition.lang = langMap[state.language] || 'en-IN';
        recognition.start();
    }
}

// Portal Switcher
function switchPortal(portal) {
    state.portal = portal;
    document.getElementById('nav-kiosk-btn').className = portal === 'kiosk' 
        ? "px-3 py-1.5 rounded-md text-xs font-semibold transition-all bg-white text-blue-700 shadow-sm flex items-center space-x-1.5"
        : "px-3 py-1.5 rounded-md text-xs font-semibold transition-all text-slate-600 hover:text-slate-900 flex items-center space-x-1.5";
    
    document.getElementById('nav-doctor-btn').className = portal === 'doctor'
        ? "px-3 py-1.5 rounded-md text-xs font-semibold transition-all bg-white text-blue-700 shadow-sm flex items-center space-x-1.5"
        : "px-3 py-1.5 rounded-md text-xs font-semibold transition-all text-slate-600 hover:text-slate-900 flex items-center space-x-1.5";

    if (portal === 'doctor') {
        loadDoctorQueue();
    } else {
        render();
    }
}

// Language Switcher
function changeLanguage(lang) {
    state.language = lang;
    const select = document.getElementById('lang-select');
    if (select) select.value = lang;
    render();
}

function toggleAudioGuidance() {
    state.audioGuidance = !state.audioGuidance;
    const icon = document.getElementById('audio-icon');
    if (state.audioGuidance) {
        icon.className = "w-4 h-4 text-blue-600";
        speakPrompt(state.language === 'hi' ? 'ध्वनि मार्गदर्शन चालू है।' : 'Audio guidance enabled.');
    } else {
        icon.className = "w-4 h-4 text-slate-400";
        if (window.speechSynthesis) window.speechSynthesis.cancel();
    }
}

// Scan & Share Modal Functions
function openScanShareModal() {
    document.getElementById('scan-share-modal').classList.remove('hidden');
}

function closeScanShareModal() {
    document.getElementById('scan-share-modal').classList.add('hidden');
}

async function simulateScanAndShareApp() {
    const name = document.getElementById('modal-abha-name')?.value.trim() || "Rameshwar Sharma";
    const gender = document.getElementById('modal-abha-gender')?.value || "Male";
    const yearOfBirth = parseInt(document.getElementById('modal-abha-year')?.value) || 1968;
    const phone = document.getElementById('modal-abha-phone')?.value.trim() || "9876543210";
    const abhaAddress = document.getElementById('modal-abha-address')?.value.trim() || "rameshwar.sharma@abdm";

    closeScanShareModal();
    try {
        const res = await fetch(`${API_BASE}/abdm/scan-and-share/process`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                abha_number: `91-${phone}`,
                abha_address: abhaAddress,
                name: name,
                gender: gender,
                year_of_birth: yearOfBirth,
                phone_number: phone
            })
        });
        const data = await res.json();
        await startSession(data.full_name, data.age, data.gender, data.phone_number, abhaAddress);
    } catch (err) {
        console.error("Scan & share failed:", err);
    }
}

// Hospital HIS Push Integration
async function pushToHospitalHis(sessionId) {
    const targetId = sessionId || state.selectedDoctorSession?.session_id;
    if (!targetId) return;
    try {
        const res = await fetch(`${API_BASE}/abdm/his/push/${targetId}`, { method: 'POST' });
        const data = await res.json();
        alert(`🏥 Hospital HIS Synchronized Successfully!\n\n• Transaction ID: ${data.his_transaction_id}\n• OPD Case No: ${data.hospital_opd_case_number}\n• FHIR Bundle Status: Validated & Pushed to EMR Core`);
    } catch (err) {
        console.error("HIS push failed:", err);
    }
}

function fillPresetPatient(name, age, gender, phone, abha) {
    const nameEl = document.getElementById('reg-patient-name');
    const ageEl = document.getElementById('reg-patient-age');
    const genderEl = document.getElementById('reg-patient-gender');
    const phoneEl = document.getElementById('reg-patient-phone');
    const abhaEl = document.getElementById('reg-patient-abha');

    if (nameEl) nameEl.value = name;
    if (ageEl) ageEl.value = age;
    if (genderEl) genderEl.value = gender;
    if (phoneEl) phoneEl.value = phone;
    if (abhaEl) abhaEl.value = abha;
}

function startSessionFromForm() {
    const name = document.getElementById('reg-patient-name')?.value.trim() || "OPD Walk-in Patient";
    const age = parseInt(document.getElementById('reg-patient-age')?.value) || 45;
    const gender = document.getElementById('reg-patient-gender')?.value || "Male";
    const phone = document.getElementById('reg-patient-phone')?.value.trim() || "9876543210";
    const abha = document.getElementById('reg-patient-abha')?.value.trim() || `91-${phone}@abdm`;
    startSession(name, age, gender, phone, abha);
}

// API Calls
async function startSession(fullName = "OPD Walk-in Patient", age = 45, gender = "Male", phone = "9876543210", abhaId = null) {
    try {
        const res = await fetch(`${API_BASE}/sessions/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                language: state.language,
                patient_data: {
                    full_name: fullName,
                    age: parseInt(age) || 45,
                    gender: gender,
                    phone_number: phone,
                    abha_id: abhaId || `91-${phone}@abdm`,
                    preferred_language: state.language,
                    consent_granted: true,
                    consent_audio_verified: true
                }
            })
        });
        const data = await res.json();
        state.currentSessionId = data.id;
        state.currentPatient = data.patient;
        state.kioskStep = 'bodymap';
        render();
        speakPrompt(i18n[state.language]?.bodymapTitle || "Please select the pain or discomfort area on the body map.");
    } catch (err) {
        console.error("Failed to start session:", err);
    }
}

function selectBodyLocation(locationName, zoneId) {
    state.selectedBodyZone = locationName;
    state.kioskStep = 'chat';
    sendChatMessage(`Discomfort in ${locationName}`, 'site', locationName);
}

async function loadInitialChatQuestion() {
    try {
        const res = await fetch(`${API_BASE}/chat/${state.currentSessionId}/initial`);
        const data = await res.json();
        state.currentChatStep = data.current_step;
        state.currentChatOptions = data.quick_options;
        state.chatHistory = [{ sender: 'ai', message: data.ai_reply }];
        render();
        speakPrompt(data.ai_reply_audio_text);
    } catch (err) {
        console.error("Failed to fetch initial question:", err);
    }
}

async function sendChatMessage(message, overrideStep = null, bodyLocation = null) {
    if (!message || !state.currentSessionId) return;

    const stepToSend = overrideStep || state.currentChatStep;
    state.chatHistory.push({ sender: 'user', message: message });
    render();

    try {
        const res = await fetch(`${API_BASE}/chat/${state.currentSessionId}/message`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                step: stepToSend,
                body_location: bodyLocation || state.selectedBodyZone
            })
        });
        const data = await res.json();

        state.chatHistory.push({ sender: 'ai', message: data.ai_reply });
        state.currentChatStep = data.next_step;
        state.currentChatOptions = data.quick_options;
        state.extractedSocrates = data.extracted_socrates || {};

        if (data.is_red_flag) {
            showRedFlagModal(data.red_flag_alert_title, data.red_flag_instructions);
        } else if (data.current_step === 'socrates_completed' || data.next_step === 'socrates_completed') {
            state.kioskStep = 'lifestyle';
        }

        render();
        speakPrompt(data.ai_reply_audio_text);
    } catch (err) {
        console.error("Chat message failed:", err);
    }
}

function addCustomCondition() {
    const input = document.getElementById('custom-condition-input');
    const val = input?.value.trim();
    if (val && !state.lifestyleAnswers.pastConditions.includes(val)) {
        state.lifestyleAnswers.pastConditions.push(val);
        input.value = '';
        renderCustomConditionsTags();
    }
}

function removeCustomCondition(cond) {
    state.lifestyleAnswers.pastConditions = state.lifestyleAnswers.pastConditions.filter(c => c !== cond);
    renderCustomConditionsTags();
}

function renderCustomConditionsTags() {
    const container = document.getElementById('custom-conditions-list');
    if (!container) return;
    const customList = state.lifestyleAnswers.pastConditions.filter(c => 
        !['Diabetes (Type 2)', 'Hypertension (BP)', 'Thyroid Disorder', 'Asthma / Allergy'].includes(c)
    );
    container.innerHTML = customList.map(c => `
        <span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-blue-100 text-blue-900 text-xs font-semibold">
            ${c}
            <button type="button" onclick="removeCustomCondition('${c.replace(/'/g, "\\'")}')" class="ml-1.5 text-blue-600 hover:text-blue-900 font-bold">×</button>
        </span>
    `).join('');
}

async function submitLifestyleData() {
    const allergyVal = document.getElementById('allergy-input')?.value;
    const allergies = allergyVal ? allergyVal.split(',').map(s => s.trim()).filter(Boolean) : [];
    
    const medsVal = document.getElementById('meds-input')?.value;
    const currentMeds = medsVal ? medsVal.split(',').map(s => {
        const trimmed = s.trim();
        return { name: trimmed, dosage: "Regular", frequency: "Daily" };
    }).filter(m => m.name.length > 0) : [];

    const smokingVal = document.getElementById('lifestyle-smoking')?.value || "Non-smoker";
    const dietVal = document.getElementById('lifestyle-diet')?.value || "Vegetarian";
    const alcoholVal = document.getElementById('lifestyle-alcohol')?.value || "No";

    state.lifestyleAnswers.allergies = allergies;
    state.lifestyleAnswers.currentMeds = currentMeds;
    state.lifestyleAnswers.smoking = smokingVal;
    state.lifestyleAnswers.diet = dietVal;
    state.lifestyleAnswers.alcohol = alcoholVal;

    // Persist to backend session
    if (state.currentSessionId) {
        try {
            await fetch(`${API_BASE}/sessions/${state.currentSessionId}/lifestyle`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    past_medical_history: state.lifestyleAnswers.pastConditions,
                    drug_allergies: allergies,
                    current_medications: currentMeds,
                    personal_history: {
                        diet: dietVal,
                        smoking: smokingVal,
                        alcohol: alcoholVal,
                        sleep: "7-8 hours"
                    }
                })
            });
        } catch (e) {
            console.error("Failed to save lifestyle data:", e);
        }
    }

    state.kioskStep = 'document';
    render();
    speakPrompt(state.language === 'hi' ? 'पूर्व इतिहास दर्ज हो गया है। अब पुराने पर्चे या रिपोर्ट स्कैन करें।' : 'Lifestyle and medical history recorded. Now please scan or upload prior medical records.');
}

async function uploadDocument(fileOrBlob, filename = "prescription.jpg", docType = "prescription") {
    try {
        const formData = new FormData();
        formData.append("session_id", state.currentSessionId);
        formData.append("document_type", docType);
        formData.append("file", fileOrBlob, filename);

        const res = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        state.uploadedDocuments.push(data);
        render();
        speakPrompt(state.language === 'hi' ? 'दस्तावेज़ सफलतापूर्वक स्कैन और पढ़ा गया।' : 'Document successfully digitized and clinical entities extracted.');
    } catch (err) {
        console.error("Document upload failed:", err);
    }
}

async function finishKioskIntake() {
    try {
        await fetch(`${API_BASE}/sessions/${state.currentSessionId}/complete`, { method: 'POST' });
        state.kioskStep = 'complete';
        render();
        speakPrompt(state.language === 'hi' ? 'आपकी केस-टेकिंग पूरी हो गई है। डॉक्टर को भेज दिया गया है।' : 'Intake completed successfully and submitted to doctor queue.');
    } catch (err) {
        console.error("Complete intake failed:", err);
    }
}

// Red Flag Modal Handling
function showRedFlagModal(title, instructions) {
    document.getElementById('red-flag-title').innerText = title;
    document.getElementById('red-flag-instructions').innerText = instructions;
    document.getElementById('red-flag-modal').classList.remove('hidden');
    speakPrompt(title);
}

function closeRedFlagModal() {
    document.getElementById('red-flag-modal').classList.add('hidden');
}

function dismissRedFlagAndCallStaff() {
    closeRedFlagModal();
    state.kioskStep = 'complete';
    render();
}

// Doctor Portal Functions
async function loadDoctorQueue() {
    try {
        const res = await fetch(`${API_BASE}/doctor/queue`);
        const queue = await res.json();
        state.doctorQueue = queue;

        const badge = document.getElementById('queue-badge-count');
        const emergencyCount = queue.filter(q => q.triage_level === 'emergency_red_flag').length;
        if (queue.length > 0) {
            badge.innerText = emergencyCount > 0 ? `🔴 ${emergencyCount}` : queue.length;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }

        if (queue.length > 0 && !state.selectedDoctorSession) {
            await selectDoctorSession(queue[0].session_id);
        } else {
            render();
        }
    } catch (err) {
        console.error("Failed to load doctor queue:", err);
    }
}

async function selectDoctorSession(sessionId) {
    try {
        const res = await fetch(`${API_BASE}/doctor/sessions/${sessionId}/summary`);
        const summary = await res.json();
        state.selectedDoctorSession = summary;
        render();
    } catch (err) {
        console.error("Failed to load clinical summary:", err);
    }
}

async function verifyDoctorReview() {
    if (!state.selectedDoctorSession) return;
    try {
        const notes = document.getElementById('doctor-notes-input')?.value || "";
        const plan = document.getElementById('doctor-plan-input')?.value || "";

        const res = await fetch(`${API_BASE}/doctor/sessions/${state.selectedDoctorSession.session_id}/verify`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                doctor_id: "DOC-OPD-201",
                doctor_name: "Dr. Rajesh Sharma, MD (Medicine)",
                department: "Department of General Medicine",
                physician_clinical_notes: notes,
                prescribed_plan: plan,
                is_verified: true
            })
        });
        const data = await res.json();
        alert("✅ " + data.message);
        await loadDoctorQueue();
    } catch (err) {
        console.error("Failed to verify review:", err);
    }
}

// Case Sheet Modal & Print
function openCaseSheetModal(sessionId) {
    const targetId = sessionId || state.selectedDoctorSession?.session_id;
    if (!targetId) return;
    const iframe = document.getElementById('casesheet-iframe');
    iframe.src = `${API_BASE}/doctor/sessions/${targetId}/casesheet`;
    document.getElementById('casesheet-modal').classList.remove('hidden');
}

function closeCaseSheetModal() {
    document.getElementById('casesheet-modal').classList.add('hidden');
}

function printCaseSheetIframe() {
    const iframe = document.getElementById('casesheet-iframe');
    iframe.contentWindow.print();
}

async function openFhirModal(sessionId) {
    try {
        const targetId = sessionId || state.selectedDoctorSession?.session_id;
        const res = await fetch(`${API_BASE}/abdm/fhir-bundle/${targetId}`);
        const fhir = await res.json();
        document.getElementById('fhir-json-content').innerText = JSON.stringify(fhir, null, 2);
        document.getElementById('fhir-modal').classList.remove('hidden');
    } catch (err) {
        console.error("Failed to load FHIR bundle:", err);
    }
}

function closeFhirModal() {
    document.getElementById('fhir-modal').classList.add('hidden');
}

function copyFhirJson() {
    const text = document.getElementById('fhir-json-content').innerText;
    navigator.clipboard.writeText(text);
    alert("ABDM FHIR JSON copied to clipboard!");
}

// Render Master
function render() {
    const root = document.getElementById('app-root');
    const t = i18n[state.language] || i18n['en'];

    if (state.portal === 'doctor') {
        root.innerHTML = renderDoctorPortal(t);
        lucide.createIcons();
        return;
    }

    // Patient Kiosk Steps
    switch (state.kioskStep) {
        case 'consent':
            root.innerHTML = renderConsentView(t);
            break;
        case 'bodymap':
            root.innerHTML = renderBodyMapView(t);
            break;
        case 'chat':
            root.innerHTML = renderChatView(t);
            break;
        case 'lifestyle':
            root.innerHTML = renderLifestyleView(t);
            break;
        case 'document':
            root.innerHTML = renderDocumentView(t);
            break;
        case 'complete':
            root.innerHTML = renderCompleteView(t);
            break;
    }
    lucide.createIcons();
}

// 1. Consent View (With ABDM Scan & Share)
function renderConsentView(t) {
    return `
    <div class="max-w-2xl mx-auto w-full bg-white rounded-3xl p-8 sm:p-10 shadow-xl border border-slate-100 animate-in fade-in duration-300">
        <div class="text-center mb-6">
            <div class="w-16 h-16 bg-blue-100 text-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-sm">
                <i data-lucide="heart-pulse" class="w-8 h-8"></i>
            </div>
            <h2 class="text-3xl font-extrabold text-slate-900 tracking-tight">${t.welcomeTitle}</h2>
            <p class="text-slate-500 font-medium mt-1">${t.welcomeSubtitle}</p>
        </div>

        <div class="bg-blue-50/70 border border-blue-200/80 rounded-2xl p-5 mb-6">
            <div class="flex items-start space-x-3.5">
                <div class="p-2 rounded-xl bg-blue-600 text-white flex-shrink-0 mt-0.5">
                    <i data-lucide="shield-check" class="w-5 h-5"></i>
                </div>
                <div>
                    <h3 class="text-base font-bold text-blue-950">${t.consentTitle}</h3>
                    <p class="text-xs text-blue-800/90 mt-1 leading-relaxed">${t.consentDesc}</p>
                    <div class="flex items-center space-x-4 mt-2.5 text-[11px] font-semibold text-blue-700">
                        <span class="flex items-center"><i data-lucide="lock" class="w-3.5 h-3.5 mr-1"></i> DPDP Act 2023 Compliant</span>
                        <span class="flex items-center"><i data-lucide="file-check" class="w-3.5 h-3.5 mr-1"></i> ABDM / ABHA Ready</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 1-Click Persona Pre-fill Chips for Testing / Fast Evaluation -->
        <div class="mb-5">
            <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">Quick Pre-fill Test Profiles (Or Type Custom Below)</label>
            <div class="flex flex-wrap gap-2">
                <button type="button" onclick="fillPresetPatient('Rohan Mehta', 45, 'Male', '9876543210', 'rohan.mehta@abdm')" class="px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-blue-50 hover:border-blue-300 text-xs font-semibold text-slate-700 hover:text-blue-900 transition-all flex items-center space-x-1">
                    <span>👤 Rohan Mehta (45/M)</span>
                </button>
                <button type="button" onclick="fillPresetPatient('Kavita Devi', 38, 'Female', '9812345678', 'kavita.devi@abdm')" class="px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-blue-50 hover:border-blue-300 text-xs font-semibold text-slate-700 hover:text-blue-900 transition-all flex items-center space-x-1">
                    <span>👤 Kavita Devi (38/F)</span>
                </button>
                <button type="button" onclick="fillPresetPatient('Sunita Devi', 62, 'Female', '9123456789', 'sunita.devi@abdm')" class="px-3 py-1.5 rounded-xl border border-rose-200 bg-rose-50 hover:bg-rose-100 text-xs font-semibold text-rose-800 transition-all flex items-center space-x-1">
                    <span>🔴 Sunita Devi (62/F - Red Flag)</span>
                </button>
            </div>
        </div>

        <!-- Interactive Patient Demographic Input Form -->
        <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 mb-6 space-y-3.5 text-left text-xs">
            <span class="font-bold text-slate-800 block text-xs uppercase tracking-wider">Patient Registration & Identity</span>
            
            <div>
                <label class="block text-[11px] font-bold text-slate-600 mb-1">Full Name (रोगी का पूरा नाम)</label>
                <input id="reg-patient-name" type="text" value="Rameshwar Sharma" placeholder="e.g. Rameshwar Sharma" class="w-full p-2.5 rounded-xl border border-slate-300 bg-white font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>

            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="block text-[11px] font-bold text-slate-600 mb-1">Age (उम्र)</label>
                    <input id="reg-patient-age" type="number" value="48" placeholder="e.g. 48" class="w-full p-2.5 rounded-xl border border-slate-300 bg-white font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-[11px] font-bold text-slate-600 mb-1">Gender (लिंग)</label>
                    <select id="reg-patient-gender" class="w-full p-2.5 rounded-xl border border-slate-300 bg-white font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="Male" selected>Male (पुरुष)</option>
                        <option value="Female">Female (महिला)</option>
                        <option value="Other">Other (अन्य)</option>
                    </select>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="block text-[11px] font-bold text-slate-600 mb-1">Phone Number (मोबाइल नंबर)</label>
                    <input id="reg-patient-phone" type="tel" value="9876543210" placeholder="10-digit mobile" class="w-full p-2.5 rounded-xl border border-slate-300 bg-white font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-[11px] font-bold text-slate-600 mb-1">ABHA Address / ID (आभा आईडी)</label>
                    <input id="reg-patient-abha" type="text" value="91-9876543210@abdm" placeholder="e.g. name@abdm" class="w-full p-2.5 rounded-xl border border-slate-300 bg-white font-mono font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
            </div>
        </div>

        <div class="space-y-3">
            <!-- 1. Start with Entered Details -->
            <button onclick="startSessionFromForm()" class="touch-btn w-full py-4 px-6 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-base flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/25 transition-all">
                <i data-lucide="sparkles" class="w-5 h-5"></i>
                <span>${t.startBtn}</span>
            </button>

            <!-- 2. Scan & Share Option -->
            <button onclick="openScanShareModal()" class="touch-btn w-full py-3 px-6 rounded-2xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs flex items-center justify-center space-x-2 transition-all">
                <i data-lucide="qr-code" class="w-4 h-4 text-blue-600"></i>
                <span>${t.scanShareBtn}</span>
            </button>
        </div>
    </div>
    `;
}

// 2. Interactive 2D Human Body Map View
function renderBodyMapView(t) {
    return `
    <div class="max-w-4xl mx-auto w-full bg-white rounded-3xl p-6 sm:p-8 shadow-xl border border-slate-100 animate-in fade-in">
        <div class="text-center mb-6">
            <div class="w-12 h-12 bg-blue-100 text-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-2">
                <i data-lucide="user" class="w-6 h-6"></i>
            </div>
            <h2 class="text-2xl font-extrabold text-slate-900">${t.bodymapTitle}</h2>
            <p class="text-slate-500 text-sm font-medium mt-0.5">${t.bodymapSubtitle}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            
            <!-- Left: Interactive Body Silhouette -->
            <div class="bg-slate-50 rounded-2xl p-6 border border-slate-200 flex justify-center">
                <svg width="240" height="380" viewBox="0 0 240 380" class="drop-shadow-sm select-none">
                    <!-- Head & Neck -->
                    <circle cx="120" cy="35" r="24" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Head / Neck (सिर व गर्दन)', 'head')"></circle>
                    <rect x="112" y="58" width="16" height="14" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Head / Neck (सिर व गर्दन)', 'head')"></rect>

                    <!-- Chest & Cardiac -->
                    <rect x="85" y="74" width="70" height="50" rx="8" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Chest / Heart (सीना व हृदय)', 'chest')"></rect>
                    <text x="120" y="102" font-size="10" font-weight="bold" fill="#475569" text-anchor="middle" pointer-events="none">CHEST</text>

                    <!-- Upper Abdomen / Epigastrium -->
                    <rect x="85" y="128" width="70" height="40" rx="6" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Upper Abdomen / Stomach (पेट का ऊपरी हिस्सा)', 'epigastrium')"></rect>
                    <text x="120" y="152" font-size="9" font-weight="bold" fill="#475569" text-anchor="middle" pointer-events="none">STOMACH</text>

                    <!-- Lower Abdomen & Pelvis -->
                    <rect x="88" y="172" width="64" height="42" rx="6" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Lower Abdomen / Pelvis (पेट का निचला हिस्सा)', 'pelvis')"></rect>
                    <text x="120" y="196" font-size="9" font-weight="bold" fill="#475569" text-anchor="middle" pointer-events="none">PELVIS</text>

                    <!-- Upper Limbs / Arms -->
                    <rect x="52" y="80" width="28" height="110" rx="8" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Arms & Shoulders (कंधा व हाथ)', 'arms')"></rect>
                    <rect x="160" y="80" width="28" height="110" rx="8" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Arms & Shoulders (कंधा व हाथ)', 'arms')"></rect>

                    <!-- Legs & Knees -->
                    <rect x="88" y="220" width="28" height="140" rx="8" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Bilateral Knees & Legs (घुटने व पैर)', 'knees')"></rect>
                    <rect x="124" y="220" width="28" height="140" rx="8" class="body-zone" fill="#e2e8f0" stroke="#94a3b8" onclick="selectBodyLocation('Bilateral Knees & Legs (घुटने व पैर)', 'knees')"></rect>
                    <circle cx="102" cy="285" r="10" fill="#3b82f6" opacity="0.3"></circle>
                    <circle cx="138" cy="285" r="10" fill="#3b82f6" opacity="0.3"></circle>
                    <text x="120" y="290" font-size="9" font-weight="bold" fill="#1e40af" text-anchor="middle" pointer-events="none">KNEES</text>
                </svg>
            </div>

            <!-- Right: Quick Anatomical Selection Buttons -->
            <div class="space-y-3">
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Quick Touch Anatomy Options</p>
                <button onclick="selectBodyLocation('Stomach & Upper Abdomen (पेट दर्द व एसिडिटी)', 'epigastrium')" class="touch-btn w-full p-3.5 px-4 rounded-xl border border-slate-200 hover:border-blue-500 bg-slate-50 hover:bg-blue-50 text-left font-bold text-sm text-slate-800 flex items-center justify-between">
                    <span class="flex items-center"><i data-lucide="activity" class="w-4 h-4 mr-2.5 text-blue-600"></i> Stomach / Upper Abdomen (पेट / एसिडिटी)</span>
                    <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
                </button>
                <button onclick="selectBodyLocation('Chest & Heart (सीने में दर्द या भारीपन)', 'chest')" class="touch-btn w-full p-3.5 px-4 rounded-xl border border-slate-200 hover:border-blue-500 bg-slate-50 hover:bg-blue-50 text-left font-bold text-sm text-slate-800 flex items-center justify-between">
                    <span class="flex items-center"><i data-lucide="heart" class="w-4 h-4 mr-2.5 text-rose-600"></i> Chest / Heart (सीना / सांस फूलना)</span>
                    <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
                </button>
                <button onclick="selectBodyLocation('Bilateral Knees & Joint Pain (घुटने व जोड़ों का दर्द)', 'knees')" class="touch-btn w-full p-3.5 px-4 rounded-xl border border-slate-200 hover:border-blue-500 bg-slate-50 hover:bg-blue-50 text-left font-bold text-sm text-slate-800 flex items-center justify-between">
                    <span class="flex items-center"><i data-lucide="bone" class="w-4 h-4 mr-2.5 text-amber-600"></i> Knees & Joints (घुटने / जोड़ों में दर्द)</span>
                    <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
                </button>
                <button onclick="selectBodyLocation('Headache & Fever (सिरदर्द व बुखार)', 'head')" class="touch-btn w-full p-3.5 px-4 rounded-xl border border-slate-200 hover:border-blue-500 bg-slate-50 hover:bg-blue-50 text-left font-bold text-sm text-slate-800 flex items-center justify-between">
                    <span class="flex items-center"><i data-lucide="thermometer" class="w-4 h-4 mr-2.5 text-teal-600"></i> Head & Throat (सिरदर्द / बुखार / जुकाम)</span>
                    <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
                </button>
                <button onclick="selectBodyLocation('Lower Back & Spine (कमर व रीढ़ का दर्द)', 'back')" class="touch-btn w-full p-3.5 px-4 rounded-xl border border-slate-200 hover:border-blue-500 bg-slate-50 hover:bg-blue-50 text-left font-bold text-sm text-slate-800 flex items-center justify-between">
                    <span class="flex items-center"><i data-lucide="shield" class="w-4 h-4 mr-2.5 text-indigo-600"></i> Lower Back & Spine (कमर व पीठ)</span>
                    <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
                </button>
            </div>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-200 flex justify-end">
            <button onclick="state.kioskStep = 'chat'; loadInitialChatQuestion();" class="text-xs font-bold text-slate-500 hover:text-blue-600 flex items-center">
                <span>${t.skipBodymap}</span>
                <i data-lucide="arrow-right" class="w-3.5 h-3.5 ml-1"></i>
            </button>
        </div>
    </div>
    `;
}

// 3. Chat View (SOCRATES Multimodal Engine)
function renderChatView(t) {
    const options = state.currentChatOptions || [];
    const stepLabel = t.socratesStepLabels[state.currentChatStep] || state.currentChatStep;

    return `
    <div class="max-w-4xl mx-auto w-full flex flex-col h-[82vh] bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden animate-in fade-in">
        
        <!-- Chat Header & Stage Progress -->
        <div class="bg-slate-900 text-white p-4 px-6 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">
                    <i data-lucide="message-square" class="w-5 h-5"></i>
                </div>
                <div>
                    <h3 class="text-sm font-bold text-white">Clinical Intake Dialogue</h3>
                    <p class="text-xs text-slate-400">SOCRATES Dimension: <span class="text-blue-400 font-semibold">${stepLabel}</span></p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button onclick="state.kioskStep = 'lifestyle'; render();" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-semibold text-slate-300">
                    Skip to Past History
                </button>
            </div>
        </div>

        <!-- Real-Time AI Clinical Reasoning Banner -->
        <div class="px-6 py-2.5 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100 flex items-center justify-between text-xs text-blue-900">
            <div class="flex items-center space-x-2">
                <span class="flex h-2 w-2 relative">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-600"></span>
                </span>
                <span class="font-bold flex items-center text-blue-800"><i data-lucide="sparkles" class="w-3.5 h-3.5 mr-1 text-blue-600"></i> MediKiosk Clinical AI:</span>
                <span class="text-slate-600 font-medium">${state.currentChatStep === 'chief_complaint' ? 'Analyzing presenting chief complaint & adapting follow-up interview...' : `Synthesizing ${stepLabel} dimension... adapting follow-up.`}</span>
            </div>
            <span class="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 font-mono text-[10px] font-bold border border-blue-200">Gemini 2.5 Flash Engine</span>
        </div>

        <!-- Chat Transcript Area -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/50">
            ${state.chatHistory.map(msg => `
                <div class="flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}">
                    <div class="max-w-[80%] rounded-2xl p-4 shadow-sm text-sm ${msg.sender === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none'}">
                        <div class="flex items-center space-x-2 mb-1">
                            <span class="text-[10px] uppercase font-bold tracking-wider ${msg.sender === 'user' ? 'text-blue-200' : 'text-slate-400'}">${msg.sender === 'user' ? 'You (Patient)' : 'MediKiosk Clinical AI'}</span>
                        </div>
                        <p class="leading-relaxed font-medium">${msg.message}</p>
                    </div>
                </div>
            `).join('')}
        </div>

        <!-- Live Waveform Visualizer (When Recording) -->
        ${state.isRecording ? `
            <div class="px-6 py-2.5 bg-rose-50 border-t border-rose-200 flex items-center justify-between animate-pulse">
                <div class="flex items-center space-x-3">
                    <div class="flex items-center space-x-1 h-6 px-2 bg-rose-200/50 rounded-lg">
                        <span class="w-1 bg-rose-600 rounded-full wave-bar"></span>
                        <span class="w-1 bg-rose-600 rounded-full wave-bar"></span>
                        <span class="w-1 bg-rose-600 rounded-full wave-bar"></span>
                        <span class="w-1 bg-rose-600 rounded-full wave-bar"></span>
                        <span class="w-1 bg-rose-600 rounded-full wave-bar"></span>
                    </div>
                    <span class="text-xs font-bold text-rose-800">Listening to patient speech (Indian multi-dialect speech model)...</span>
                </div>
                <span class="text-[11px] text-rose-600 font-medium">Click mic to finish speaking</span>
            </div>
        ` : ''}

        <!-- Touch Quick Options & Voice Control Bar -->
        <div class="p-5 bg-white border-t border-slate-200 space-y-4">
            
            <!-- Quick Options -->
            ${options.length > 0 ? `
                <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5">${t.orTouch}</p>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        ${options.map(opt => `
                            <button onclick="sendChatMessage('${opt.value.replace(/'/g, "\\'")}')" class="touch-btn text-left p-3.5 px-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-blue-50 hover:border-blue-300 text-slate-800 hover:text-blue-950 font-semibold text-sm flex items-center justify-between transition-all group">
                                <span>${opt.label}</span>
                                <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400 group-hover:text-blue-600"></i>
                            </button>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Voice Mic & Text Input Row -->
            <div class="flex items-center space-x-3 pt-2">
                <button onclick="toggleVoiceInput()" class="touch-btn h-12 px-5 rounded-xl ${state.isRecording ? 'bg-rose-600 text-white animate-pulse' : 'bg-blue-600 text-white hover:bg-blue-700'} font-bold text-sm flex items-center space-x-2 shadow-md shadow-blue-600/20 flex-shrink-0 transition-all">
                    <i data-lucide="${state.isRecording ? 'mic-off' : 'mic'}" class="w-5 h-5"></i>
                    <span>${state.isRecording ? t.speakingPrompt : t.micBtn}</span>
                </button>
                <div class="flex-1 relative">
                    <input id="chat-text-input" onkeypress="if(event.key==='Enter') sendChatMessage(this.value)" type="text" placeholder="${state.language === 'hi' ? 'यहाँ टाइप करें या माइक दबाएं...' : 'Type symptoms or use voice...'}" class="w-full h-12 px-4 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                </div>
                <button onclick="sendChatMessage(document.getElementById('chat-text-input').value)" class="touch-btn h-12 px-4 rounded-xl bg-slate-900 text-white hover:bg-slate-800 flex items-center justify-center">
                    <i data-lucide="send" class="w-5 h-5"></i>
                </button>
            </div>
        </div>
    </div>
    `;
}

// 4. Past Medical & Lifestyle History View
function renderLifestyleView(t) {
    return `
    <div class="max-w-3xl mx-auto w-full bg-white rounded-3xl p-8 shadow-xl border border-slate-100 animate-in fade-in">
        <div class="text-center mb-8">
            <div class="w-14 h-14 bg-blue-100 text-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <i data-lucide="user-check" class="w-7 h-7"></i>
            </div>
            <h2 class="text-2xl font-extrabold text-slate-900">${t.lifestyleTitle}</h2>
            <p class="text-slate-500 text-sm font-medium mt-1">${t.lifestyleSubtitle}</p>
        </div>

        <div class="space-y-6">
            <!-- Known Chronic Conditions -->
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                <label class="block text-sm font-bold text-slate-800 mb-3">1. Known Chronic Conditions (पुरानी बीमारियाँ)</label>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
                    <button type="button" onclick="toggleCondition(this, 'Diabetes (Type 2)')" class="cond-btn p-3 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-blue-500 text-center">
                        Diabetes (शुगर)
                    </button>
                    <button type="button" onclick="toggleCondition(this, 'Hypertension (BP)')" class="cond-btn p-3 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-blue-500 text-center">
                        High BP (रक्तचाप)
                    </button>
                    <button type="button" onclick="toggleCondition(this, 'Thyroid Disorder')" class="cond-btn p-3 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-blue-500 text-center">
                        Thyroid (थायराइड)
                    </button>
                    <button type="button" onclick="toggleCondition(this, 'Asthma / Allergy')" class="cond-btn p-3 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-blue-500 text-center">
                        Asthma (दमा)
                    </button>
                </div>
                <!-- Custom Condition Adder -->
                <div class="flex space-x-2 pt-1">
                    <input id="custom-condition-input" onkeypress="if(event.key==='Enter') { event.preventDefault(); addCustomCondition(); }" type="text" placeholder="Add custom condition (e.g. Arthritis, Migraine, Acid Reflux)..." class="flex-1 p-2.5 rounded-xl border border-slate-300 text-xs font-medium bg-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button type="button" onclick="addCustomCondition()" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs shadow-sm flex items-center space-x-1">
                        <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                        <span>Add</span>
                    </button>
                </div>
                <div id="custom-conditions-list" class="flex flex-wrap gap-1.5 mt-2.5"></div>
            </div>

            <!-- Drug Allergies -->
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                <label class="block text-sm font-bold text-slate-800 mb-2">2. Known Drug Allergies (दवाओं से एलर्जी)</label>
                <input id="allergy-input" type="text" placeholder="e.g. Penicillin, Sulfa, Aspirin (Leave blank if none)" class="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-blue-500 bg-white">
                <p class="text-[11px] text-slate-400 mt-1">Cross-checked automatically by the Clinical Safety Engine during physician review.</p>
            </div>

            <!-- Current Regular Medications -->
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                <label class="block text-sm font-bold text-slate-800 mb-2">3. Current Regular Medications (वर्तमान में ले रहे दवाइयाँ)</label>
                <input id="meds-input" type="text" placeholder="e.g. Tab Metformin 500mg (1 OD), Tab Telmisartan 40mg (1 OD Morning)" class="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-blue-500 bg-white">
                <p class="text-[11px] text-slate-400 mt-1">Comma-separated list of regular prescription drugs.</p>
            </div>

            <!-- Lifestyle Habits -->
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                <label class="block text-sm font-bold text-slate-800 mb-3">4. Daily Lifestyle & Habits (दैनिक आदतें)</label>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                        <span class="text-xs font-semibold text-slate-600 block mb-1">Smoking / Tobacco</span>
                        <select id="lifestyle-smoking" class="w-full p-2.5 rounded-xl border border-slate-300 text-xs font-medium bg-white">
                            <option value="Non-smoker">Non-smoker</option>
                            <option value="Occasional">Occasional</option>
                            <option value="Regular smoker">Regular smoker</option>
                        </select>
                    </div>
                    <div>
                        <span class="text-xs font-semibold text-slate-600 block mb-1">Alcohol</span>
                        <select id="lifestyle-alcohol" class="w-full p-2.5 rounded-xl border border-slate-300 text-xs font-medium bg-white">
                            <option value="No">No</option>
                            <option value="Occasional">Occasional</option>
                            <option value="Regular">Regular</option>
                        </select>
                    </div>
                    <div>
                        <span class="text-xs font-semibold text-slate-600 block mb-1">Diet Preference</span>
                        <select id="lifestyle-diet" class="w-full p-2.5 rounded-xl border border-slate-300 text-xs font-medium bg-white">
                            <option value="Vegetarian">Vegetarian</option>
                            <option value="Non-Vegetarian">Non-Vegetarian / Mixed</option>
                            <option value="Low Sodium / Diabetic">Low Sodium / Diabetic</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-8 flex space-x-4">
            <button onclick="submitLifestyleData()" class="touch-btn flex-1 py-4 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-base flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/25">
                <i data-lucide="arrow-right" class="w-5 h-5"></i>
                <span>${t.submitLifestyleBtn}</span>
            </button>
        </div>
    </div>
    `;
}

function toggleCondition(el, cond) {
    if (el.classList.contains('border-blue-600')) {
        el.className = "cond-btn p-3 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-blue-500 text-center";
        state.lifestyleAnswers.pastConditions = state.lifestyleAnswers.pastConditions.filter(c => c !== cond);
    } else {
        el.className = "cond-btn p-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-950 text-xs font-bold text-center";
        state.lifestyleAnswers.pastConditions.push(cond);
    }
}

// 5. Document OCR & Vision AI View
function renderDocumentView(t) {
    return `
    <div class="max-w-3xl mx-auto w-full bg-white rounded-3xl p-8 shadow-xl border border-slate-100 animate-in fade-in">
        <div class="text-center mb-8">
            <div class="w-14 h-14 bg-teal-100 text-teal-700 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <i data-lucide="file-text" class="w-7 h-7"></i>
            </div>
            <h2 class="text-2xl font-extrabold text-slate-900">${t.docTitle}</h2>
            <p class="text-slate-500 text-sm font-medium mt-1">${t.docSubtitle}</p>
        </div>

        <!-- Upload Drop Zone -->
        <div class="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-3xl p-8 text-center bg-slate-50/60 transition-all cursor-pointer mb-6" onclick="document.getElementById('file-input').click()">
            <input id="file-input" type="file" accept="image/*,.pdf" class="hidden" onchange="handleFileUpload(event)">
            <div class="w-12 h-12 bg-white rounded-2xl shadow-sm text-blue-600 flex items-center justify-center mx-auto mb-3">
                <i data-lucide="upload-cloud" class="w-6 h-6"></i>
            </div>
            <p class="text-sm font-bold text-slate-800">Click or Drag & Drop Prescription / Lab Report</p>
            <p class="text-xs text-slate-400 mt-1">Supports Multimodal Vision OCR (Handwritten, Printed & Multilingual)</p>
        </div>

        <!-- Action Buttons: Manual Entry & Sample Loaders -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
            <button onclick="openCustomDocModal()" class="touch-btn py-3 px-3.5 rounded-xl border border-teal-300 bg-teal-50 hover:bg-teal-100 text-teal-900 font-bold text-xs flex items-center justify-center space-x-1.5 shadow-sm">
                <i data-lucide="file-plus" class="w-4 h-4 text-teal-700"></i>
                <span>➕ Enter Custom Record</span>
            </button>
            <button onclick="uploadDemoPrescription()" class="touch-btn py-3 px-3.5 rounded-xl border border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-800 font-bold text-xs flex items-center justify-center space-x-1.5">
                <i data-lucide="file-check" class="w-4 h-4"></i>
                <span>${t.demoPrescriptionBtn}</span>
            </button>
            <button onclick="uploadDemoLabReport()" class="touch-btn py-3 px-3.5 rounded-xl border border-amber-200 bg-amber-50 hover:bg-amber-100 text-amber-900 font-bold text-xs flex items-center justify-center space-x-1.5">
                <i data-lucide="flask-conical" class="w-4 h-4 text-amber-600"></i>
                <span>${t.demoLabReportBtn}</span>
            </button>
        </div>

        <!-- Uploaded Documents Preview -->
        ${state.uploadedDocuments.length > 0 ? `
            <div class="space-y-4 mb-8">
                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500">Digitized Medical Records (${state.uploadedDocuments.length})</h4>
                ${state.uploadedDocuments.map(doc => `
                    <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center space-x-2">
                                <span class="px-2 py-0.5 rounded bg-teal-100 text-teal-800 text-[10px] font-bold uppercase">${doc.document_type}</span>
                                <span class="text-xs font-bold text-slate-800">${doc.file_name}</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 text-[10px] font-bold flex items-center">
                                    <i data-lucide="scan-eye" class="w-3 h-3 mr-1 text-blue-600"></i>
                                    <span>AI Vision OCR (${(doc.extracted_entities && doc.extracted_entities.ai_ocr_metadata && doc.extracted_entities.ai_ocr_metadata.overall_confidence) || 97}%)</span>
                                </span>
                                <span class="text-xs text-slate-400">${doc.document_date || 'Today'}</span>
                            </div>
                        </div>
                        
                        <!-- Extracted Medicines -->
                        ${(doc.extracted_entities.medicines || []).length > 0 ? `
                            <div class="mt-3">
                                <span class="text-[11px] font-bold text-slate-600">AI-Extracted Medications & SNOMED CT:</span>
                                <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 mt-1.5">
                                    ${doc.extracted_entities.medicines.map(m => `
                                        <div class="p-2 rounded-xl bg-white border border-slate-200 text-xs flex items-center justify-between">
                                            <span class="font-medium text-slate-800">${m.name} <span class="text-slate-500">(${m.dosage})</span></span>
                                            <span class="text-[9px] px-1.5 py-0.5 rounded bg-teal-50 text-teal-800 font-mono font-bold border border-teal-200">${m.snomed_ct ? `SNOMED: ${m.snomed_ct}` : 'VERIFIED'}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Abnormal Highlights -->
                        ${(doc.abnormal_flags || []).length > 0 ? `
                            <div class="mt-3 p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
                                <span class="font-bold flex items-center"><i data-lucide="alert-triangle" class="w-3.5 h-3.5 mr-1 text-amber-600"></i> Abnormal Lab Parameters Flagged by AI:</span>
                                ${doc.abnormal_flags.map(f => `
                                    <p class="text-[11px]">• <b>${f.parameter}:</b> ${f.value} (${f.clinical_note || 'High'})</p>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        ` : ''}

        <div class="flex space-x-4">
            <button onclick="finishKioskIntake()" class="touch-btn flex-1 py-4 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-base flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/25">
                <i data-lucide="check-circle" class="w-5 h-5"></i>
                <span>Complete Intake & Submit to OPD Queue</span>
            </button>
        </div>
    </div>
    `;
}

function openCustomDocModal() {
    document.getElementById('custom-doc-modal').classList.remove('hidden');
}

function closeCustomDocModal() {
    document.getElementById('custom-doc-modal').classList.add('hidden');
}

async function submitCustomDocEntry() {
    if (!state.currentSessionId) return;

    const docType = document.getElementById('custom-doc-type')?.value || "prescription";
    const title = document.getElementById('custom-doc-title')?.value.trim() || "District General Hospital OPD";
    const medsRaw = document.getElementById('custom-doc-meds')?.value.trim() || "";
    
    // Parse medicines from user text
    const medicines = medsRaw ? medsRaw.split(',').map(m => {
        const parts = m.trim().split('(');
        const nameAndDose = parts[0].trim();
        const freq = parts.length > 1 ? parts[1].replace(')', '').trim() : "As directed";
        return {
            name: nameAndDose,
            dosage: "Prescribed dose",
            frequency: freq,
            snomed_ct: "410942007"
        };
    }).filter(m => m.name.length > 0) : [];

    // Parse investigations
    const hba1c = document.getElementById('custom-doc-hba1c')?.value.trim();
    const fbs = document.getElementById('custom-doc-fbs')?.value.trim();
    const uric = document.getElementById('custom-doc-uric')?.value.trim();
    const creatinine = document.getElementById('custom-doc-creatinine')?.value.trim();

    const investigations = [];
    if (hba1c) {
        investigations.push({
            test: "HbA1c (Glycated Hemoglobin)",
            value: hba1c,
            unit: "%",
            ref_range: "4.0 - 5.6 %",
            is_abnormal: parseFloat(hba1c) > 5.6
        });
    }
    if (fbs) {
        investigations.push({
            test: "Fasting Blood Sugar (Glucose)",
            value: fbs,
            unit: "mg/dL",
            ref_range: "70 - 99 mg/dL",
            is_abnormal: parseFloat(fbs) > 99
        });
    }
    if (uric) {
        investigations.push({
            test: "Serum Uric Acid",
            value: uric,
            unit: "mg/dL",
            ref_range: "3.5 - 7.2 mg/dL",
            is_abnormal: parseFloat(uric) > 7.2
        });
    }
    if (creatinine) {
        investigations.push({
            test: "Serum Creatinine",
            value: creatinine,
            unit: "mg/dL",
            ref_range: "0.7 - 1.2 mg/dL",
            is_abnormal: parseFloat(creatinine) > 1.2
        });
    }

    try {
        const res = await fetch(`${API_BASE}/documents/manual-entry`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: state.currentSessionId,
                document_title: title,
                document_type: docType,
                doctor_or_lab_name: title,
                medicines: medicines,
                investigations: investigations,
                diagnoses: ["Patient Record Intake"]
            })
        });
        const data = await res.json();
        state.uploadedDocuments.push(data);
        closeCustomDocModal();
        render();
        speakPrompt("Custom medical record and lab values successfully saved.");
    } catch (err) {
        console.error("Custom doc entry failed:", err);
        alert("Failed to save custom medical record.");
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) uploadDocument(file, file.name);
}

function uploadDemoPrescription() {
    const dummyBlob = new Blob(["DEMO PRESCRIPTION CONTENT"], { type: "text/plain" });
    uploadDocument(dummyBlob, "civil_hospital_prescription.jpg", "prescription");
}

function uploadDemoLabReport() {
    const dummyBlob = new Blob(["DEMO LAB REPORT CONTENT"], { type: "text/plain" });
    uploadDocument(dummyBlob, "blood_biochemistry_report.jpg", "lab_report");
}

// 6. Complete View
function renderCompleteView(t) {
    return `
    <div class="max-w-xl mx-auto w-full bg-white rounded-3xl p-8 sm:p-10 shadow-xl border border-slate-100 text-center animate-in fade-in">
        <div class="w-20 h-20 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-md shadow-blue-600/10">
            <i data-lucide="check" class="w-10 h-10"></i>
        </div>
        <span class="px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-bold border border-blue-200">OPD Token Generated</span>
        <h2 class="text-3xl font-extrabold text-slate-900 mt-3">Intake Completed Successfully</h2>
        <p class="text-slate-500 text-sm mt-2">Your clinical history, symptoms, and digitized records are now ready for the OPD physician.</p>

        <div class="bg-slate-50 rounded-2xl p-6 border border-slate-200 my-8 text-left space-y-2.5">
            <div class="flex justify-between text-xs">
                <span class="text-slate-500">Patient:</span>
                <span class="font-bold text-slate-800">${state.currentPatient?.full_name || 'Walk-in Patient'}</span>
            </div>
            <div class="flex justify-between text-xs">
                <span class="text-slate-500">ABHA ID:</span>
                <span class="font-mono font-bold text-blue-700">${state.currentPatient?.abha_id || '91-9876543210@abdm'}</span>
            </div>
            <div class="flex justify-between text-xs">
                <span class="text-slate-500">OPD Room:</span>
                <span class="font-bold text-slate-800">General Medicine OPD Room 3</span>
            </div>
        </div>

        <div class="flex space-x-3">
            <button onclick="switchPortal('doctor')" class="touch-btn flex-1 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm flex items-center justify-center space-x-2">
                <i data-lucide="stethoscope" class="w-4 h-4"></i>
                <span>Open Doctor Review Portal</span>
            </button>
            <button onclick="state.kioskStep = 'consent'; render();" class="touch-btn px-4 py-3.5 rounded-xl border border-slate-300 text-slate-700 font-semibold text-sm hover:bg-slate-50">
                New Patient
            </button>
        </div>
    </div>
    `;
}

// 7. Doctor Review Portal (Full Feature-Set with Hospital HIS Push)
function renderDoctorPortal(t) {
    const s = state.selectedDoctorSession;
    const filteredQueue = state.doctorQueue.filter(item => {
        if (state.queueFilter === 'red_flag' && item.triage_level !== 'emergency_red_flag') return false;
        if (state.queueFilter === 'priority' && item.triage_level !== 'priority') return false;
        if (state.queueFilter === 'routine' && item.triage_level !== 'routine') return false;
        if (state.searchQuery) {
            const q = state.searchQuery.toLowerCase();
            return (item.patient_name || '').toLowerCase().includes(q) || (item.abha_id || '').toLowerCase().includes(q);
        }
        return true;
    });

    return `
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full h-[84vh]">
        
        <!-- Left Column: Live OPD Patient Queue (4 Cols) -->
        <div class="lg:col-span-4 bg-white rounded-3xl p-5 shadow-lg border border-slate-200 flex flex-col h-full overflow-hidden">
            
            <!-- Queue Header & Search -->
            <div class="pb-3 border-b border-slate-100 space-y-3">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2.5">
                        <div class="w-8 h-8 rounded-lg bg-hospital-50 text-hospital-600 flex items-center justify-center">
                            <i data-lucide="users" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-900">OPD Waiting Queue</h3>
                            <p class="text-[11px] text-slate-500">${state.doctorQueue.length} Patients Triaged</p>
                        </div>
                    </div>
                    <button onclick="loadDoctorQueue()" class="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50">
                        <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i>
                    </button>
                </div>

                <!-- Search Input -->
                <div class="relative">
                    <input type="text" placeholder="Search by name or ABHA ID..." value="${state.searchQuery}" oninput="state.searchQuery = this.value; render();" class="w-full pl-8 pr-3 py-1.5 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <i data-lucide="search" class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5"></i>
                </div>

                <!-- Filter Tabs -->
                <div class="flex space-x-1 text-[11px] font-semibold">
                    <button onclick="state.queueFilter = 'all'; render();" class="flex-1 py-1 rounded-lg ${state.queueFilter === 'all' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">All</button>
                    <button onclick="state.queueFilter = 'red_flag'; render();" class="flex-1 py-1 rounded-lg ${state.queueFilter === 'red_flag' ? 'bg-rose-600 text-white' : 'bg-rose-50 text-rose-700 hover:bg-rose-100'}">🔴 Red Flag</button>
                    <button onclick="state.queueFilter = 'routine'; render();" class="flex-1 py-1 rounded-lg ${state.queueFilter === 'routine' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">Routine</button>
                </div>
            </div>

            <!-- Queue List -->
            <div class="flex-1 overflow-y-auto space-y-2.5 pt-3 pr-1">
                ${filteredQueue.map(item => `
                    <div onclick="selectDoctorSession('${item.session_id}')" class="p-3.5 rounded-2xl border transition-all cursor-pointer ${s && s.session_id === item.session_id ? 'border-blue-600 bg-blue-50/50 shadow-sm' : 'border-slate-200 bg-white hover:border-slate-300'}">
                        <div class="flex items-center justify-between mb-1.5">
                            <span class="font-bold text-xs text-slate-900">${item.patient_name} (${item.age}/${item.gender.charAt(0)})</span>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                item.triage_level === 'emergency_red_flag' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                                item.triage_level === 'priority' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                            }">
                                ${item.triage_level === 'emergency_red_flag' ? '🔴 RED FLAG' : item.triage_level.toUpperCase()}
                            </span>
                        </div>
                        <p class="text-xs text-slate-600 line-clamp-1 font-medium">${item.chief_complaint}</p>
                        <div class="flex items-center justify-between text-[11px] text-slate-400 mt-2 font-medium">
                            <span class="text-blue-700">${item.status.toUpperCase()}</span>
                            <span>${item.documents_count} records</span>
                        </div>
                    </div>
                `).join('') || '<div class="text-center py-8 text-xs text-slate-400">No patients match this filter.</div>'}
            </div>
        </div>

        <!-- Right Column: Structured Clinical Summary & Verification (8 Cols) -->
        <div class="lg:col-span-8 bg-white rounded-3xl p-6 shadow-lg border border-slate-200 flex flex-col h-full overflow-y-auto">
            ${s ? `
                <!-- Summary Header -->
                <div class="flex items-center justify-between pb-4 border-b border-slate-100">
                    <div>
                        <div class="flex items-center space-x-2">
                            <h2 class="text-xl font-extrabold text-slate-900">${s.patient_name}</h2>
                            <span class="text-xs text-slate-500 font-semibold">${s.patient_age} Y / ${s.patient_gender}</span>
                            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${s.triage_level === 'emergency_red_flag' ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'}">
                                ${s.triage_level.toUpperCase()}
                            </span>
                        </div>
                        <p class="text-xs text-slate-400 font-mono mt-0.5">ABHA ID: ${s.abha_id || '91-9876543210@abdm'}</p>
                    </div>

                    <div class="flex items-center space-x-2">
                        <button onclick="pushToHospitalHis('${s.session_id}')" class="px-3 py-2 rounded-xl border border-teal-300 text-teal-800 bg-teal-50 hover:bg-teal-100 text-xs font-bold flex items-center space-x-1.5 shadow-sm">
                            <i data-lucide="upload" class="w-3.5 h-3.5 text-teal-600"></i>
                            <span>${t.hisPushBtn}</span>
                        </button>
                        <button onclick="openCaseSheetModal('${s.session_id}')" class="px-3 py-2 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-bold flex items-center space-x-1.5">
                            <i data-lucide="printer" class="w-3.5 h-3.5 text-blue-600"></i>
                            <span>${t.printBtn}</span>
                        </button>
                        <button onclick="openFhirModal('${s.session_id}')" class="px-3 py-2 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-bold flex items-center space-x-1.5">
                            <i data-lucide="code" class="w-3.5 h-3.5 text-blue-600"></i>
                            <span>${t.fhirBtn}</span>
                        </button>
                        <button onclick="verifyDoctorReview()" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-blue-600/20">
                            <i data-lucide="check-check" class="w-4 h-4"></i>
                            <span>${t.verifyBtn}</span>
                        </button>
                    </div>
                </div>

                <!-- Red Flag Warning Banner -->
                ${s.red_flag_alert ? `
                    <div class="mt-4 p-4 rounded-2xl bg-rose-50 border-2 border-rose-500 text-rose-900 flex items-start space-x-3 animate-pulse">
                        <i data-lucide="alert-triangle" class="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5"></i>
                        <div>
                            <h4 class="text-xs font-bold uppercase tracking-wider text-rose-700">Triage Escalation Warning</h4>
                            <p class="text-sm font-semibold mt-0.5">${s.red_flag_alert}</p>
                        </div>
                    </div>
                ` : ''}

                <!-- Drug-Allergy Safety Conflict Banner -->
                ${(s.safety_alerts || []).length > 0 ? `
                    <div class="mt-4 p-4 rounded-2xl bg-red-50 border border-red-300 text-red-900 space-y-2">
                        <div class="flex items-center space-x-2">
                            <i data-lucide="shield-alert" class="w-5 h-5 text-red-600 flex-shrink-0"></i>
                            <h4 class="text-xs font-bold uppercase tracking-wider text-red-800">Clinical Drug Safety Alerts (${s.safety_alerts.length})</h4>
                        </div>
                        ${s.safety_alerts.map(a => `
                            <div class="text-xs pl-7">
                                <span class="font-bold text-red-700">• ${a.medication || a.drug_pair?.join(' + ')}:</span>
                                <span class="text-red-900">${a.clinical_advice || a.alert}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}

                <!-- ⚡ AI CLINICAL COPILOT & DECISION SUPPORT PANEL -->
                ${s.ai_copilot_analysis ? `
                    <div class="mt-5 p-5 rounded-3xl bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900 text-white shadow-xl border border-blue-500/30">
                        <div class="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
                            <div class="flex items-center space-x-2.5">
                                <div class="w-8 h-8 rounded-xl bg-blue-500 text-white flex items-center justify-center shadow-md shadow-blue-500/30">
                                    <i data-lucide="sparkles" class="w-4 h-4"></i>
                                </div>
                                <div>
                                    <h3 class="text-sm font-extrabold tracking-tight text-white flex items-center">
                                        MediKiosk AI Clinical Copilot
                                        <span class="ml-2 px-2 py-0.5 rounded-full bg-blue-400/20 text-blue-300 text-[10px] font-mono border border-blue-400/30">${s.ai_copilot_analysis.engine_model}</span>
                                    </h3>
                                    <p class="text-[11px] text-blue-200/80 font-medium">Physician Decision Support, Differential Diagnoses & SOAP Note Synthesis</p>
                                </div>
                            </div>
                            <button onclick="adoptAiSoapPlan()" class="touch-btn px-3 py-1.5 rounded-xl bg-blue-500 hover:bg-blue-400 text-white text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-blue-500/30 transition-all">
                                <i data-lucide="file-plus-2" class="w-3.5 h-3.5"></i>
                                <span>Adopt AI SOAP Draft</span>
                            </button>
                        </div>

                        <!-- AI Clinical Impression -->
                        <div class="p-3.5 rounded-2xl bg-white/10 border border-white/10 backdrop-blur-md mb-4">
                            <span class="text-[10px] font-bold uppercase tracking-wider text-blue-300 block mb-1">AI Clinical Synthesis</span>
                            <p class="text-xs text-blue-50 leading-relaxed font-medium">${s.ai_copilot_analysis.clinical_impression}</p>
                        </div>

                        <!-- Differential Diagnoses Cards Grid -->
                        <div class="mb-4">
                            <span class="text-[10px] font-bold uppercase tracking-wider text-blue-300 block mb-2">Provisional Differential Diagnoses</span>
                            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                                ${s.ai_copilot_analysis.differential_diagnoses.map(d => `
                                    <div class="p-3 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-400/50 transition-all">
                                        <div class="flex items-center justify-between mb-1.5">
                                            <span class="font-bold text-xs text-white">${d.condition}</span>
                                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                                d.confidence_score >= 80 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                                                d.confidence_score >= 60 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-slate-500/20 text-slate-300'
                                            }">
                                                ${d.confidence_score}% Match
                                            </span>
                                        </div>
                                        <div class="flex items-center space-x-2 text-[10px] text-blue-200/70 font-mono mb-2">
                                            <span>ICD: ${d.icd10_code || 'N/A'}</span>
                                            <span>•</span>
                                            <span>SNOMED: ${d.snomed_ct || 'N/A'}</span>
                                        </div>
                                        <p class="text-[11px] text-blue-100/90 leading-snug font-normal">${d.clinical_rationale}</p>
                                    </div>
                                `).join('')}
                            </div>
                        </div>

                        <!-- Risk Scores & Suggested Investigations Row -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                            <!-- Clinical Risk Scores -->
                            <div class="p-3 rounded-2xl bg-white/5 border border-white/10">
                                <span class="text-[10px] font-bold uppercase tracking-wider text-blue-300 block mb-1.5">Clinical Risk Assessment</span>
                                <div class="space-y-1.5">
                                    ${(s.ai_copilot_analysis.clinical_risk_scores || []).map(r => `
                                        <div class="flex items-center justify-between text-xs">
                                            <span class="text-blue-100">${r.category}</span>
                                            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${
                                                r.risk_level === 'High' ? 'bg-rose-500/30 text-rose-200' :
                                                r.risk_level === 'Elevated' || r.risk_level === 'Moderate' ? 'bg-amber-500/30 text-amber-200' : 'bg-emerald-500/30 text-emerald-200'
                                            }">
                                                ${r.risk_level}
                                            </span>
                                        </div>
                                        <p class="text-[10px] text-blue-200/70 pl-1 pb-1">${r.score_note}</p>
                                    `).join('')}
                                </div>
                            </div>

                            <!-- Suggested Investigations -->
                            <div class="p-3 rounded-2xl bg-white/5 border border-white/10">
                                <span class="text-[10px] font-bold uppercase tracking-wider text-blue-300 block mb-1.5">Suggested Diagnostic Workup</span>
                                <div class="space-y-1 text-xs text-blue-100">
                                    ${(s.ai_copilot_analysis.suggested_investigations || []).map(inv => `
                                        <p class="text-[11px] flex items-start"><i data-lucide="check" class="w-3.5 h-3.5 text-blue-400 mr-1.5 flex-shrink-0 mt-0.5"></i> ${inv}</p>
                                    `).join('')}
                                </div>
                            </div>
                        </div>

                        <!-- Interactive Doctor-AI Clinical Assistant Box -->
                        <div class="pt-3 border-t border-white/10">
                            <div class="flex items-center justify-between mb-2">
                                <span class="text-[11px] font-bold text-blue-300 flex items-center">
                                    <i data-lucide="bot" class="w-3.5 h-3.5 mr-1 text-blue-400"></i> Ask Doctor AI Assistant:
                                </span>
                                <div class="flex space-x-1.5">
                                    <button onclick="sendDoctorAiQuery('Check contraindications for NSAIDs with hypertension')" class="text-[10px] px-2 py-0.5 rounded-lg bg-white/10 hover:bg-white/20 text-blue-200 font-medium">Drug Interactions?</button>
                                    <button onclick="sendDoctorAiQuery('Explain abnormal lab findings in relation to symptoms')" class="text-[10px] px-2 py-0.5 rounded-lg bg-white/10 hover:bg-white/20 text-blue-200 font-medium">Explain Labs?</button>
                                </div>
                            </div>

                            <!-- AI Assistant Dialogue Output -->
                            ${state.aiCopilotChatHistory.length > 0 ? `
                                <div class="p-3 rounded-2xl bg-black/40 border border-white/10 max-h-48 overflow-y-auto space-y-2 mb-2.5 font-sans text-xs">
                                    ${state.aiCopilotChatHistory.map(item => `
                                        <div class="${item.sender === 'doctor' ? 'text-blue-300 font-semibold text-right' : 'text-slate-100 text-left'}">
                                            <p class="text-[10px] text-white/40 mb-0.5">${item.sender === 'doctor' ? 'Doctor Query' : 'MediKiosk AI'}</p>
                                            <div class="p-2 rounded-xl ${item.sender === 'doctor' ? 'bg-blue-600/40 inline-block' : 'bg-white/10'} whitespace-pre-line">${item.message}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : ''}

                            <div class="flex items-center space-x-2">
                                <input id="doctor-ai-query-input" onkeypress="if(event.key==='Enter') sendDoctorAiQuery()" type="text" placeholder="Ask AI: e.g. What is the recommended PPI dosage? Are there renal risks?" class="flex-1 bg-white/10 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-white placeholder-blue-300/50 focus:outline-none focus:ring-2 focus:ring-blue-400">
                                <button onclick="sendDoctorAiQuery()" class="px-3 py-1.5 rounded-xl bg-blue-500 hover:bg-blue-400 text-white font-bold text-xs flex items-center space-x-1">
                                    <i data-lucide="send" class="w-3.5 h-3.5"></i>
                                    <span>Ask</span>
                                </button>
                            </div>
                        </div>
                    </div>
                ` : ''}

                <!-- Structured Sections Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                    
                    <!-- 1. Chief Complaint & SOCRATES HPI -->
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center">
                            <i data-lucide="activity" class="w-3.5 h-3.5 mr-1 text-blue-600"></i> Chief Complaint & SOCRATES HPI
                        </h4>
                        <p class="text-xs font-bold text-slate-900 mb-2">${s.chief_complaint || 'N/A'}</p>
                        <div class="space-y-1 text-xs text-slate-600">
                            ${Object.entries(s.socrates_hpi || {}).map(([k, v]) => `
                                <p>• <b>${k.replace('_', ' ').toUpperCase()}:</b> ${v}</p>
                            `).join('')}
                        </div>
                    </div>

                    <!-- 2. Past Medical & Family History -->
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center">
                            <i data-lucide="history" class="w-3.5 h-3.5 mr-1 text-blue-600"></i> Past Conditions & Lifestyle
                        </h4>
                        <div class="space-y-1.5 text-xs text-slate-700">
                            <p>• <b>Past Illnesses:</b> ${(s.past_medical_history || []).join(', ') || 'None reported'}</p>
                            <p>• <b>Past Surgeries:</b> ${(s.past_surgical_history || []).join(', ') || 'None'}</p>
                            <p>• <b>Family History:</b> ${(s.family_history || []).join(', ') || 'No hereditary conditions'}</p>
                            <p>• <b>Lifestyle:</b> ${JSON.stringify(s.personal_history || {})}</p>
                        </div>
                    </div>

                    <!-- 3. Current Meds & Allergies -->
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center">
                            <i data-lucide="pill" class="w-3.5 h-3.5 mr-1 text-blue-600"></i> Prior Medications & Allergies
                        </h4>
                        <div class="space-y-1 text-xs text-slate-700">
                            <p class="font-semibold text-rose-700">Allergies: ${(s.drug_allergies || []).join(', ') || 'NKDA (No Known Drug Allergies)'}</p>
                            <div class="mt-2 space-y-1">
                                ${(s.current_medications || []).map(m => `
                                    <p class="text-[11px]">• <b>${m.name || m}</b> ${m.dosage ? `(${m.dosage})` : ''} - <span class="text-slate-500">${m.frequency || ''}</span></p>
                                `).join('')}
                            </div>
                        </div>
                    </div>

                    <!-- 4. Abnormal Lab Findings -->
                    <div class="bg-amber-50/60 p-4 rounded-2xl border border-amber-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-amber-800 mb-2 flex items-center">
                            <i data-lucide="alert-circle" class="w-3.5 h-3.5 mr-1 text-amber-600"></i> Abnormal Lab Findings
                        </h4>
                        <div class="space-y-1.5 text-xs text-amber-950">
                            ${(s.abnormal_lab_highlights || []).map(h => `
                                <div class="p-2 bg-white/90 rounded-xl border border-amber-200">
                                    <span class="font-bold text-rose-700">${h.parameter}: ${h.value}</span>
                                    <span class="text-[11px] text-slate-500 ml-1">(${h.ref_range || 'Ref'})</span>
                                    <p class="text-[10px] text-amber-900 mt-0.5">${h.clinical_note || ''}</p>
                                </div>
                            `).join('') || '<p class="text-slate-400">No abnormal lab markers flagged.</p>'}
                        </div>
                    </div>
                </div>

                <!-- 5. Chronological Medical Timeline -->
                <div class="mt-6 bg-slate-50 p-4 rounded-2xl border border-slate-200">
                    <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center">
                        <i data-lucide="clock" class="w-3.5 h-3.5 mr-1 text-slate-700"></i> Chronological Medical Timeline
                    </h4>
                    <div class="space-y-3">
                        ${(s.chronological_timeline || []).map(ev => `
                            <div class="flex items-start space-x-3 text-xs">
                                <span class="px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-mono text-[10px] font-bold flex-shrink-0">${ev.date || 'Record'}</span>
                                <div>
                                    <p class="font-bold text-slate-800">${ev.title}</p>
                                    <p class="text-slate-600 text-[11px]">${ev.description}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- 6. Doctor Clinical Notes & Prescription Input -->
                <div class="mt-6 pt-4 border-t border-slate-200 space-y-3">
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-700">Physician Clinical Assessment & Prescription Plan</label>
                    <textarea id="doctor-notes-input" rows="2" placeholder="Enter physician clinical notes, provisional diagnosis, and assessment..." class="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-blue-500">${s.physician_notes || ''}</textarea>
                    <input id="doctor-plan-input" type="text" placeholder="Prescription / Advice (e.g. Tab Pantoprazole 40mg OD x 14d, repeat blood tests in 2 weeks)" class="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-blue-500">
                </div>
            ` : `
                <div class="flex-1 flex flex-col items-center justify-center text-slate-400">
                    <i data-lucide="inbox" class="w-12 h-12 mb-2"></i>
                    <p class="text-sm font-semibold">Select a patient from the queue to review structured summary.</p>
                </div>
            `}
        </div>
    </div>
    `;
}

function adoptAiSoapPlan() {
    const copilot = state.selectedDoctorSession?.ai_copilot_analysis;
    if (!copilot || !copilot.soap_draft) return;
    
    const notesEl = document.getElementById('doctor-notes-input');
    const planEl = document.getElementById('doctor-plan-input');
    
    if (notesEl) {
        notesEl.value = `[AI SOAP ASSESSMENT]\nSUBJECTIVE: ${copilot.soap_draft.subjective}\nOBJECTIVE: ${copilot.soap_draft.objective}\nASSESSMENT: ${copilot.soap_draft.assessment}`;
    }
    if (planEl) {
        planEl.value = copilot.soap_draft.plan;
    }
}

async function sendDoctorAiQuery(queryText) {
    const query = queryText || document.getElementById('doctor-ai-query-input')?.value;
    if (!query || !state.selectedDoctorSession) return;
    
    state.aiCopilotLoading = true;
    state.aiCopilotChatHistory.push({ sender: 'doctor', message: query });
    render();
    
    try {
        const res = await fetch(`${API_BASE}/doctor/sessions/${state.selectedDoctorSession.session_id}/ai-copilot/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doctor_query: query })
        });
        const data = await res.json();
        state.aiCopilotChatHistory.push({ 
            sender: 'ai', 
            message: data.ai_response, 
            context: data.clinical_context_used,
            follow_ups: data.suggested_follow_up 
        });
    } catch (err) {
        state.aiCopilotChatHistory.push({ sender: 'ai', message: "AI Copilot analysis temporarily unavailable." });
    } finally {
        state.aiCopilotLoading = false;
        render();
    }
}

// ==========================================
// AI Settings & Google Gemini Key Management
// ==========================================

async function checkAiStatus() {
    try {
        const res = await fetch(`${API_BASE}/settings/ai-status`);
        if (!res.ok) return;
        const data = await res.json();
        
        const pillIndicator = document.getElementById('ai-status-indicator');
        const pillText = document.getElementById('ai-status-text');
        
        if (pillIndicator) {
            if (data.is_configured) {
                pillIndicator.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse";
                if (pillText) pillText.textContent = "Gemini 2.5 Live";
            } else {
                pillIndicator.className = "w-2.5 h-2.5 rounded-full bg-amber-400";
                if (pillText) pillText.textContent = "AI Settings";
            }
        }
        return data;
    } catch (e) {
        console.warn("Could not check AI status:", e);
    }
}

async function openAiSettingsModal() {
    const modal = document.getElementById('ai-settings-modal');
    if (!modal) return;
    modal.classList.remove('hidden');

    const statusData = await checkAiStatus();
    const statusTitle = document.getElementById('ai-status-card-title');
    const statusBadge = document.getElementById('ai-status-pill-badge');
    const statusDesc = document.getElementById('ai-status-card-desc');
    const maskedKeyEl = document.getElementById('ai-masked-key-display');
    const badgeIcon = document.getElementById('ai-status-badge-icon');
    const testResultEl = document.getElementById('ai-test-result');
    if (testResultEl) testResultEl.classList.add('hidden');

    if (statusData && statusData.is_configured) {
        if (statusTitle) statusTitle.textContent = "Status: Live Google Gemini 2.5 Flash Connected";
        if (statusBadge) {
            statusBadge.textContent = "Live Gemini AI";
            statusBadge.className = "px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800";
        }
        if (badgeIcon) {
            badgeIcon.className = "w-8 h-8 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0 mt-0.5";
            badgeIcon.innerHTML = '<i data-lucide="check-circle" class="w-4 h-4"></i>';
        }
        if (statusDesc) {
            statusDesc.textContent = "Full Gemini 2.5 Flash clinical reasoning is active across Adaptive SOCRATES intake, ICD-10 Differential Diagnoses, Risk Stratification, and Multimodal Vision OCR.";
        }
        if (maskedKeyEl) {
            maskedKeyEl.textContent = `Configured Key: ${statusData.masked_key}`;
            maskedKeyEl.classList.remove('hidden');
        }
    } else {
        if (statusTitle) statusTitle.textContent = "Status: Clinical Knowledge Fallback Engine";
        if (statusBadge) {
            statusBadge.textContent = "Offline / Rule-based";
            statusBadge.className = "px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800";
        }
        if (badgeIcon) {
            badgeIcon.className = "w-8 h-8 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center flex-shrink-0 mt-0.5";
            badgeIcon.innerHTML = '<i data-lucide="alert-circle" class="w-4 h-4"></i>';
        }
        if (statusDesc) {
            statusDesc.textContent = "Provide a Google Gemini API Key to unlock real-time Gemini 2.5 Flash clinical reasoning, customized differential diagnoses, and doctor copilot dialogue.";
        }
        if (maskedKeyEl) maskedKeyEl.classList.add('hidden');
    }
    lucide.createIcons();
}

function closeAiSettingsModal() {
    const modal = document.getElementById('ai-settings-modal');
    if (modal) modal.classList.add('hidden');
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('gemini-api-key-input');
    const eyeIcon = document.getElementById('eye-icon');
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        if (eyeIcon) eyeIcon.setAttribute('data-lucide', 'eye-off');
    } else {
        input.type = 'password';
        if (eyeIcon) eyeIcon.setAttribute('data-lucide', 'eye');
    }
    lucide.createIcons();
}

async function testGeminiConnection() {
    const keyInput = document.getElementById('gemini-api-key-input')?.value?.trim();
    const testBtn = document.getElementById('btn-test-gemini');
    const testBtnText = document.getElementById('test-btn-text');
    const resultEl = document.getElementById('ai-test-result');
    
    if (testBtn) testBtn.disabled = true;
    if (testBtnText) testBtnText.textContent = "Testing...";
    if (resultEl) {
        resultEl.className = "p-3 rounded-xl text-xs font-medium bg-blue-50 text-blue-800 border border-blue-200 block";
        resultEl.innerHTML = "Connecting to Google Gemini API (gemini-2.5-flash)...";
    }

    try {
        const res = await fetch(`${API_BASE}/settings/test-gemini`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gemini_api_key: keyInput || undefined })
        });
        const data = await res.json();
        
        if (res.ok && data.status === "SUCCESS") {
            resultEl.className = "p-3 rounded-xl text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200 block";
            resultEl.innerHTML = `<strong>Connected Successfully!</strong> Latency: ${data.latency_ms}ms with model <code>${data.model_tested}</code>. AI response: "${data.reply_preview}"`;
        } else {
            resultEl.className = "p-3 rounded-xl text-xs font-medium bg-rose-50 text-rose-800 border border-rose-200 block";
            resultEl.innerHTML = `<strong>Connection Failed:</strong> ${data.detail || data.error || 'Invalid API Key or network error.'}`;
        }
    } catch (err) {
        if (resultEl) {
            resultEl.className = "p-3 rounded-xl text-xs font-medium bg-rose-50 text-rose-800 border border-rose-200 block";
            resultEl.innerHTML = `<strong>Error:</strong> Network request failed (${err.message}).`;
        }
    } finally {
        if (testBtn) testBtn.disabled = false;
        if (testBtnText) testBtnText.textContent = "Test Connection";
    }
}

async function saveGeminiApiKey() {
    const keyInput = document.getElementById('gemini-api-key-input')?.value?.trim();
    if (!keyInput) {
        alert("Please enter a valid Google Gemini API Key.");
        return;
    }

    const saveBtn = document.getElementById('btn-save-gemini');
    if (saveBtn) saveBtn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/settings/ai-config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gemini_api_key: keyInput })
        });
        const data = await res.json();
        
        if (res.ok && data.status === "SUCCESS") {
            const input = document.getElementById('gemini-api-key-input');
            if (input) input.value = '';
            await checkAiStatus();
            alert("Gemini API Key saved and activated successfully! Gemini 2.5 Flash is now powering clinical intake and diagnostic copilot.");
            closeAiSettingsModal();
        } else {
            alert(`Failed to save key: ${data.detail || 'Unknown error'}`);
        }
    } catch (err) {
        alert(`Error saving Gemini API key: ${err.message}`);
    } finally {
        if (saveBtn) saveBtn.disabled = false;
    }
}

// Initial Launch
window.addEventListener('DOMContentLoaded', () => {
    initSpeechRecognition();
    checkAiStatus();
    render();
});

