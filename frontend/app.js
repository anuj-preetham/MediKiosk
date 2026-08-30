/**
 * MediKiosk Frontend Application
 * Multi-portal Patient Kiosk & Physician Review System (SIH26047)
 */

const API_BASE = '/api';

const state = {
    portal: 'kiosk', // 'kiosk' | 'doctor'
    language: 'en', // 'en' | 'hi'
    audioGuidance: true,
    currentSessionId: null,
    currentPatient: null,
    kioskStep: 'consent', // 'consent' | 'chat' | 'ayush' | 'document' | 'complete'
    currentChatStep: 'chief_complaint',
    chatHistory: [],
    extractedSocrates: {},
    ayushAnswers: {},
    ayushResult: null,
    uploadedDocuments: [],
    doctorQueue: [],
    selectedDoctorSession: null,
    isRecording: false
};

// UI Translations
const i18n = {
    en: {
        welcomeTitle: "Welcome to MediKiosk",
        welcomeSubtitle: "Ministry of Ayush & AIIA Smart Clinical Intake Kiosk",
        consentTitle: "Patient Identity & ABDM Consent",
        consentDesc: "By continuing, you consent to secure recording of your clinical history, Ayurvedic assessment, and prior medical records for your consultation under DPDP Act 2023.",
        startBtn: "Start Touch / Voice Intake",
        quickStart: "Walk-in Patient (Quick Start)",
        abhaLabel: "ABHA ID / Mobile Number",
        speakingPrompt: "Listening to your voice...",
        micBtn: "Tap to Speak",
        sendBtn: "Send Response",
        orTouch: "Or choose a quick option below:",
        socratesStepLabels: {
            chief_complaint: "Chief Complaint",
            site: "Location / Site",
            onset: "Onset & Duration",
            character: "Pain Feeling",
            radiation: "Spread / Radiation",
            associated: "Other Symptoms",
            timing: "Time Pattern",
            exacerbating: "Relief Factors",
            severity: "Pain Severity"
        },
        ayushTitle: "AYUSH Dashavidha & Prakriti Assessment",
        ayushSubtitle: "Ayurvedic constitutional analysis and digestive fire evaluation",
        submitAyushBtn: "Calculate & Save Assessment",
        docTitle: "Medical Document Digitization (OCR)",
        docSubtitle: "Upload or scan previous prescriptions, lab reports, or discharge summaries",
        uploadBtn: "Scan / Upload Document",
        demoPrescriptionBtn: "Use Sample Hospital Prescription",
        summaryTitle: "Physician Clinical History Summary",
        verifyBtn: "Approve & Push to ABDM / HIS",
        fhirBtn: "View ABDM FHIR JSON",
        triageRoutine: "Routine",
        triagePriority: "Priority",
        triageEmergency: "Emergency Red Flag"
    },
    hi: {
        welcomeTitle: "मेडीकियोस्क में आपका स्वागत है",
        welcomeSubtitle: "आयुष मंत्रालय एवं अखिल भारतीय आयुर्वेद संस्थान (AIIA) डिजिटल केस-टेकिंग",
        consentTitle: "रोगी पहचान एवं डिजिटल सहमति (DPDP 2023)",
        consentDesc: "आगे बढ़कर आप अपने स्वास्थ्य इतिहास, आयुर्वेदिक प्रकृति और पुराने पर्चों को डॉक्टर परामर्श हेतु सुरक्षित रूप से रिकॉर्ड करने की सहमति देते हैं।",
        startBtn: "बोलकर या छूकर शुरू करें",
        quickStart: "सीधे शुरू करें (त्वरित प्रवेश)",
        abhaLabel: "आभा आईडी / मोबाइल नंबर",
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
        ayushTitle: "आयुर्वेदिक दशविध परीक्षा एवं प्रकृति मूल्यांकन",
        ayushSubtitle: "दोष प्रकृति, अग्नि एवं कोष्ठ का वैज्ञानिक मूल्यांकन",
        submitAyushBtn: "प्रकृति की गणना करें व सहेजें",
        docTitle: "चिकित्सा दस्तावेज़ डिजिटलीकरण (OCR)",
        docSubtitle: "पुराने पर्चे या लैब रिपोर्ट स्कैन / अपलोड करें",
        uploadBtn: "पर्चा अपलोड करें",
        demoPrescriptionBtn: "नमूना पर्चा लोड करें",
        summaryTitle: "चिकित्सक सारांश (Physician Summary)",
        verifyBtn: "सत्यापित करें एवं ABDM में भेजें",
        fhirBtn: "ABDM FHIR JSON देखें",
        triageRoutine: "सामान्य",
        triagePriority: "प्राथमिकता",
        triageEmergency: "आपातकालीन रेड फ्लैग"
    }
};

// Speech Synthesis
function speakPrompt(text) {
    if (!state.audioGuidance || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = state.language === 'hi' ? 'hi-IN' : 'en-IN';
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
        recognition.lang = state.language === 'hi' ? 'hi-IN' : 'en-IN';

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
        recognition.lang = state.language === 'hi' ? 'hi-IN' : 'en-IN';
        recognition.start();
    }
}

// Portal Switcher
function switchPortal(portal) {
    state.portal = portal;
    document.getElementById('nav-kiosk-btn').className = portal === 'kiosk' 
        ? "px-3 py-1.5 rounded-md text-xs font-semibold transition-all bg-white text-emerald-700 shadow-sm flex items-center space-x-1.5"
        : "px-3 py-1.5 rounded-md text-xs font-semibold transition-all text-slate-600 hover:text-slate-900 flex items-center space-x-1.5";
    
    document.getElementById('nav-doctor-btn').className = portal === 'doctor'
        ? "px-3 py-1.5 rounded-md text-xs font-semibold transition-all bg-white text-emerald-700 shadow-sm flex items-center space-x-1.5"
        : "px-3 py-1.5 rounded-md text-xs font-semibold transition-all text-slate-600 hover:text-slate-900 flex items-center space-x-1.5";

    if (portal === 'doctor') {
        loadDoctorQueue();
    } else {
        render();
    }
}

// Language Switcher
function toggleLanguage() {
    state.language = state.language === 'en' ? 'hi' : 'en';
    document.getElementById('current-lang-label').innerText = state.language === 'en' ? 'English' : 'हिन्दी';
    render();
}

function toggleAudioGuidance() {
    state.audioGuidance = !state.audioGuidance;
    const icon = document.getElementById('audio-icon');
    if (state.audioGuidance) {
        icon.className = "w-4 h-4 text-emerald-600";
        speakPrompt(state.language === 'hi' ? 'ध्वनि मार्गदर्शन चालू है।' : 'Audio guidance enabled.');
    } else {
        icon.className = "w-4 h-4 text-slate-400";
        if (window.speechSynthesis) window.speechSynthesis.cancel();
    }
}

// API Calls
async function startSession(fullName = "OPD Walk-in Patient", age = 45, gender = "Male", phone = "9876543210") {
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
                    preferred_language: state.language,
                    consent_granted: true,
                    consent_audio_verified: true
                }
            })
        });
        const data = await res.json();
        state.currentSessionId = data.id;
        state.currentPatient = data.patient;
        state.kioskStep = 'chat';
        await loadInitialChatQuestion();
    } catch (err) {
        console.error("Failed to start session:", err);
    }
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

async function sendChatMessage(message) {
    if (!message || !state.currentSessionId) return;

    // Add user message to history
    state.chatHistory.push({ sender: 'user', message: message });
    render();

    try {
        const res = await fetch(`${API_BASE}/chat/${state.currentSessionId}/message`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                step: state.currentChatStep
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
            state.kioskStep = 'ayush';
        }

        render();
        speakPrompt(data.ai_reply_audio_text);
    } catch (err) {
        console.error("Chat message failed:", err);
    }
}

async function submitAyushData() {
    try {
        const res = await fetch(`${API_BASE}/ayush/${state.currentSessionId}/submit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ answers: state.ayushAnswers })
        });
        const data = await res.json();
        state.ayushResult = data;
        state.kioskStep = 'document';
        render();
        speakPrompt(state.language === 'hi' ? 'आयुर्वेदिक प्रकृति की गणना हो गई है। अब पुराने पर्चे अपलोड करें।' : 'AYUSH assessment calculated. Now please upload previous medical documents.');
    } catch (err) {
        console.error("AYUSH submission failed:", err);
    }
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
        speakPrompt(state.language === 'hi' ? 'आपकी केस-टेकिंग पूरी हो गई है। डॉक्टर को भेज दिया गया है।' : 'Intake completed successfully and sent to doctor queue.');
    } catch (err) {
        console.error("Complete intake failed:", err);
    }
}

// Red Flag Handling
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
        if (queue.length > 0) {
            badge.innerText = queue.length;
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
                doctor_id: "DOC-AIIA-104",
                doctor_name: "Dr. Ananya Vaidya, MD (Ayurveda)",
                department: "Kayachikitsa & General OPD",
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
    alert("FHIR JSON copied to clipboard!");
}

// Render Main Template
function render() {
    const root = document.getElementById('app-root');
    const t = i18n[state.language];

    if (state.portal === 'doctor') {
        root.innerHTML = renderDoctorPortal(t);
        lucide.createIcons();
        return;
    }

    // Patient Kiosk Flows
    switch (state.kioskStep) {
        case 'consent':
            root.innerHTML = renderConsentView(t);
            break;
        case 'chat':
            root.innerHTML = renderChatView(t);
            break;
        case 'ayush':
            root.innerHTML = renderAyushView(t);
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

// 1. Consent View
function renderConsentView(t) {
    return `
    <div class="max-w-2xl mx-auto w-full bg-white rounded-3xl p-8 sm:p-10 shadow-xl border border-slate-100 animate-in fade-in duration-300">
        <div class="text-center mb-8">
            <div class="w-16 h-16 bg-emerald-100 text-emerald-700 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                <i data-lucide="heart-pulse" class="w-8 h-8"></i>
            </div>
            <h2 class="text-3xl font-extrabold text-slate-900 tracking-tight">${t.welcomeTitle}</h2>
            <p class="text-slate-500 font-medium mt-1">${t.welcomeSubtitle}</p>
        </div>

        <div class="bg-emerald-50/70 border border-emerald-200/80 rounded-2xl p-6 mb-8">
            <div class="flex items-start space-x-3.5">
                <div class="p-2 rounded-xl bg-emerald-600 text-white flex-shrink-0 mt-0.5">
                    <i data-lucide="shield-check" class="w-5 h-5"></i>
                </div>
                <div>
                    <h3 class="text-base font-bold text-emerald-950">${t.consentTitle}</h3>
                    <p class="text-sm text-emerald-800/90 mt-1 leading-relaxed">${t.consentDesc}</p>
                    <div class="flex items-center space-x-4 mt-3 text-xs font-semibold text-emerald-700">
                        <span class="flex items-center"><i data-lucide="lock" class="w-3.5 h-3.5 mr-1"></i> DPDP Act 2023</span>
                        <span class="flex items-center"><i data-lucide="file-check" class="w-3.5 h-3.5 mr-1"></i> ABDM / ABHA Ready</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="space-y-4">
            <button onclick="startSession()" class="touch-btn w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-lg flex items-center justify-center space-x-3 shadow-lg shadow-emerald-600/25 transition-all">
                <i data-lucide="mic" class="w-6 h-6"></i>
                <span>${t.startBtn}</span>
            </button>
            <button onclick="startSession('Sunita Devi', 62, 'Female', '9123456789')" class="touch-btn w-full py-3 px-6 rounded-2xl border border-rose-200 bg-rose-50/70 hover:bg-rose-100 text-rose-700 font-semibold text-sm flex items-center justify-center space-x-2 transition-all">
                <i data-lucide="alert-circle" class="w-4 h-4"></i>
                <span>Demo Emergency Case (Chest Pain Red Flag)</span>
            </button>
        </div>
    </div>
    `;
}

// 2. Chat View (SOCRATES Multimodal)
function renderChatView(t) {
    const options = state.currentChatOptions || [];
    const stepLabel = t.socratesStepLabels[state.currentChatStep] || state.currentChatStep;

    return `
    <div class="max-w-4xl mx-auto w-full flex flex-col h-[78vh] bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden animate-in fade-in">
        
        <!-- Chat Header & Stage Progress -->
        <div class="bg-slate-900 text-white p-4 px-6 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
                    <i data-lucide="message-square" class="w-5 h-5"></i>
                </div>
                <div>
                    <h3 class="text-sm font-bold text-white">Clinical Intake Interview</h3>
                    <p class="text-xs text-slate-400">SOCRATES Framework Step: <span class="text-emerald-400 font-semibold">${stepLabel}</span></p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button onclick="state.kioskStep = 'ayush'; render();" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-semibold text-slate-300">
                    Skip to AYUSH
                </button>
            </div>
        </div>

        <!-- Chat Transcript Area -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/50">
            ${state.chatHistory.map(msg => `
                <div class="flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}">
                    <div class="max-w-[80%] rounded-2xl p-4 shadow-sm text-sm ${msg.sender === 'user' ? 'bg-emerald-600 text-white rounded-br-none' : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none'}">
                        <div class="flex items-center space-x-2 mb-1">
                            <span class="text-[10px] uppercase font-bold tracking-wider ${msg.sender === 'user' ? 'text-emerald-200' : 'text-slate-400'}">${msg.sender === 'user' ? 'You (Patient)' : 'MediKiosk AI'}</span>
                        </div>
                        <p class="leading-relaxed font-medium">${msg.message}</p>
                    </div>
                </div>
            `).join('')}
        </div>

        <!-- Touch Quick Options & Voice Control Bar -->
        <div class="p-5 bg-white border-t border-slate-200 space-y-4">
            
            <!-- Quick Options -->
            ${options.length > 0 ? `
                <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5">${t.orTouch}</p>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        ${options.map(opt => `
                            <button onclick="sendChatMessage('${opt.value.replace(/'/g, "\\'")}')" class="touch-btn text-left p-3.5 px-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-emerald-50 hover:border-emerald-300 text-slate-800 hover:text-emerald-950 font-semibold text-sm flex items-center justify-between transition-all group">
                                <span>${opt.label}</span>
                                <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400 group-hover:text-emerald-600"></i>
                            </button>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Voice Mic & Text Input Row -->
            <div class="flex items-center space-x-3 pt-2">
                <button onclick="toggleVoiceInput()" class="touch-btn h-12 px-5 rounded-xl ${state.isRecording ? 'bg-rose-600 text-white animate-pulse' : 'bg-emerald-600 text-white hover:bg-emerald-700'} font-bold text-sm flex items-center space-x-2 shadow-md shadow-emerald-600/20 flex-shrink-0 transition-all">
                    <i data-lucide="${state.isRecording ? 'mic-off' : 'mic'}" class="w-5 h-5"></i>
                    <span>${state.isRecording ? t.speakingPrompt : t.micBtn}</span>
                </button>
                <div class="flex-1 relative">
                    <input id="chat-text-input" onkeypress="if(event.key==='Enter') sendChatMessage(this.value)" type="text" placeholder="${state.language === 'hi' ? 'यहाँ टाइप करें या माइक दबाएं...' : 'Type symptoms or use voice...'}" class="w-full h-12 px-4 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm">
                </div>
                <button onclick="sendChatMessage(document.getElementById('chat-text-input').value)" class="touch-btn h-12 px-4 rounded-xl bg-slate-900 text-white hover:bg-slate-800 flex items-center justify-center">
                    <i data-lucide="send" class="w-5 h-5"></i>
                </button>
            </div>
        </div>
    </div>
    `;
}

// 3. AYUSH Dashavidha Assessment View
function renderAyushView(t) {
    return `
    <div class="max-w-3xl mx-auto w-full bg-white rounded-3xl p-8 shadow-xl border border-slate-100 animate-in fade-in">
        <div class="text-center mb-8">
            <div class="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <i data-lucide="leaf" class="w-7 h-7"></i>
            </div>
            <h2 class="text-2xl font-extrabold text-slate-900">${t.ayushTitle}</h2>
            <p class="text-slate-500 text-sm font-medium mt-1">${t.ayushSubtitle}</p>
        </div>

        <div class="space-y-6">
            <!-- Question 1: Body Frame (Prakriti) -->
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                <label class="block text-sm font-bold text-slate-800 mb-3">1. Body Constitution & Frame (शरीर बनावट)</label>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <button onclick="selectAyush('prakriti_body_frame', 'vata', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Vata (वात):</b> Lean, slender frame, quick movements
                    </button>
                    <button onclick="selectAyush('prakriti_body_frame', 'pitta', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Pitta (पित्त):</b> Medium muscular build, athletic
                    </button>
                    <button onclick="selectAyush('prakriti_body_frame', 'kapha', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Kapha (कफ):</b> Broad, heavy build, steady
                    </button>
                </div>
            </div>

            <!-- Question 2: Appetite & Agni -->
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                <label class="block text-sm font-bold text-slate-800 mb-3">2. Appetite & Digestive Fire (अग्नि)</label>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button onclick="selectAyush('agni_digestion', 'vishama_agni', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Vishama Agni:</b> Irregular hunger, gas bloating
                    </button>
                    <button onclick="selectAyush('agni_digestion', 'tikshna_agni', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Tikshna Agni:</b> Intense hunger, hyperacidity
                    </button>
                    <button onclick="selectAyush('agni_digestion', 'manda_agni', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Manda Agni:</b> Sluggish digestion, heavy fullness
                    </button>
                    <button onclick="selectAyush('agni_digestion', 'sama_agni', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Sama Agni:</b> Normal, balanced digestion
                    </button>
                </div>
            </div>

            <!-- Question 3: Bowel Habits (Koshtha) -->
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                <label class="block text-sm font-bold text-slate-800 mb-3">3. Bowel Evacuation Pattern (कोष्ठ)</label>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <button onclick="selectAyush('koshtha_bowel', 'krura', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Krura:</b> Hard stools / constipation
                    </button>
                    <button onclick="selectAyush('koshtha_bowel', 'mridu', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Mridu:</b> Soft / loose stools easily
                    </button>
                    <button onclick="selectAyush('koshtha_bowel', 'madhyama', this)" class="ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left">
                        <b>Madhyama:</b> Regular smooth clearance
                    </button>
                </div>
            </div>
        </div>

        <div class="mt-8 flex space-x-4">
            <button onclick="submitAyushData()" class="touch-btn flex-1 py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base flex items-center justify-center space-x-2 shadow-lg shadow-emerald-600/25">
                <i data-lucide="sparkles" class="w-5 h-5"></i>
                <span>${t.submitAyushBtn}</span>
            </button>
        </div>
    </div>
    `;
}

function selectAyush(key, val, el) {
    state.ayushAnswers[key] = val;
    const siblings = el.parentElement.querySelectorAll('.ayush-opt');
    siblings.forEach(s => s.className = "ayush-opt p-3.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold hover:border-emerald-500 text-left");
    el.className = "ayush-opt p-3.5 rounded-xl border-2 border-emerald-600 bg-emerald-50 text-emerald-950 text-xs font-bold text-left";
}

// 4. Document OCR View
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
        <div class="border-2 border-dashed border-slate-300 hover:border-emerald-500 rounded-3xl p-8 text-center bg-slate-50/60 transition-all cursor-pointer mb-6" onclick="document.getElementById('file-input').click()">
            <input id="file-input" type="file" accept="image/*,.pdf" class="hidden" onchange="handleFileUpload(event)">
            <div class="w-12 h-12 bg-white rounded-2xl shadow-sm text-emerald-600 flex items-center justify-center mx-auto mb-3">
                <i data-lucide="upload-cloud" class="w-6 h-6"></i>
            </div>
            <p class="text-sm font-bold text-slate-800">Click to upload prescription or lab report</p>
            <p class="text-xs text-slate-400 mt-1">Supports JPG, PNG, PDF (Multilingual & Handwritten OCR)</p>
        </div>

        <!-- Quick Demo Prescription Button -->
        <div class="mb-6">
            <button onclick="uploadDemoPrescription()" class="touch-btn w-full py-3 px-4 rounded-xl border border-emerald-200 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-bold text-xs flex items-center justify-center space-x-2">
                <i data-lucide="file-check" class="w-4 h-4"></i>
                <span>${t.demoPrescriptionBtn}</span>
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
                            <span class="text-xs text-slate-400">${doc.document_date || 'Today'}</span>
                        </div>
                        
                        <!-- Extracted Medicines -->
                        <div class="mt-3">
                            <span class="text-[11px] font-bold text-slate-600">Extracted Medications:</span>
                            <div class="flex flex-wrap gap-1.5 mt-1">
                                ${(doc.extracted_entities.medicines || []).map(m => `
                                    <span class="px-2 py-1 rounded-md bg-white border border-slate-200 text-xs font-medium text-slate-700">${m.name} (${m.dosage})</span>
                                `).join('')}
                            </div>
                        </div>

                        <!-- Abnormal Highlights -->
                        ${(doc.abnormal_flags || []).length > 0 ? `
                            <div class="mt-3 p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
                                <span class="font-bold flex items-center"><i data-lucide="alert-triangle" class="w-3.5 h-3.5 mr-1 text-amber-600"></i> Abnormal Lab Parameters Flagged:</span>
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
            <button onclick="finishKioskIntake()" class="touch-btn flex-1 py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base flex items-center justify-center space-x-2 shadow-lg shadow-emerald-600/25">
                <i data-lucide="check-circle" class="w-5 h-5"></i>
                <span>Complete Intake & Submit to Doctor</span>
            </button>
        </div>
    </div>
    `;
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) uploadDocument(file, file.name);
}

function uploadDemoPrescription() {
    const dummyBlob = new Blob(["DEMO PRESCRIPTION CONTENT"], { type: "text/plain" });
    uploadDocument(dummyBlob, "aiia_opd_prescription_sample.jpg", "prescription");
}

// 5. Complete View
function renderCompleteView(t) {
    return `
    <div class="max-w-xl mx-auto w-full bg-white rounded-3xl p-8 sm:p-10 shadow-xl border border-slate-100 text-center animate-in fade-in">
        <div class="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-md shadow-emerald-600/10">
            <i data-lucide="check" class="w-10 h-10"></i>
        </div>
        <span class="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-200">OPD Queue Token Generated</span>
        <h2 class="text-3xl font-extrabold text-slate-900 mt-3">Intake Completed Successfully</h2>
        <p class="text-slate-500 text-sm mt-2">Your clinical history, AYUSH assessment, and digitized records are now ready for the OPD physician.</p>

        <div class="bg-slate-50 rounded-2xl p-6 border border-slate-200 my-8 text-left space-y-2.5">
            <div class="flex justify-between text-xs">
                <span class="text-slate-500">Patient:</span>
                <span class="font-bold text-slate-800">${state.currentPatient?.full_name || 'Walk-in Patient'}</span>
            </div>
            <div class="flex justify-between text-xs">
                <span class="text-slate-500">ABHA ID:</span>
                <span class="font-mono font-bold text-emerald-700">${state.currentPatient?.abha_id || '91-9876543210@abdm'}</span>
            </div>
            <div class="flex justify-between text-xs">
                <span class="text-slate-500">OPD Room:</span>
                <span class="font-bold text-slate-800">Kayachikitsa OPD Room 4</span>
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

// 6. Doctor Portal View
function renderDoctorPortal(t) {
    const s = state.selectedDoctorSession;

    return `
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full h-[84vh]">
        
        <!-- Left: Live Patient OPD Queue (4 Cols) -->
        <div class="lg:col-span-4 bg-white rounded-3xl p-5 shadow-lg border border-slate-200 flex flex-col h-full overflow-hidden">
            <div class="flex items-center justify-between pb-4 border-b border-slate-100">
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

            <!-- Queue List -->
            <div class="flex-1 overflow-y-auto space-y-2.5 pt-3 pr-1">
                ${state.doctorQueue.map(item => `
                    <div onclick="selectDoctorSession('${item.session_id}')" class="p-3.5 rounded-2xl border transition-all cursor-pointer ${s && s.session_id === item.session_id ? 'border-emerald-600 bg-emerald-50/50 shadow-sm' : 'border-slate-200 bg-white hover:border-slate-300'}">
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
                            <span class="text-emerald-700">${item.prakriti || 'Vata-Pitta'}</span>
                            <span>${item.documents_count} docs</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Right: Structured Clinical Summary & Verification (8 Cols) -->
        <div class="lg:col-span-8 bg-white rounded-3xl p-6 shadow-lg border border-slate-200 flex flex-col h-full overflow-y-auto">
            ${s ? `
                <!-- Summary Header -->
                <div class="flex items-center justify-between pb-4 border-b border-slate-100">
                    <div>
                        <div class="flex items-center space-x-2">
                            <h2 class="text-xl font-extrabold text-slate-900">${s.patient_name}</h2>
                            <span class="text-xs text-slate-500 font-semibold">${s.patient_age} Y / ${s.patient_gender}</span>
                            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${s.triage_level === 'emergency_red_flag' ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'}">
                                ${s.triage_level.toUpperCase()}
                            </span>
                        </div>
                        <p class="text-xs text-slate-400 font-mono mt-0.5">ABHA: ${s.abha_id || '91-9876543210@abdm'}</p>
                    </div>

                    <div class="flex items-center space-x-2">
                        <button onclick="openFhirModal('${s.session_id}')" class="px-3 py-2 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-bold flex items-center space-x-1.5">
                            <i data-lucide="code" class="w-3.5 h-3.5 text-emerald-600"></i>
                            <span>${t.fhirBtn}</span>
                        </button>
                        <button onclick="verifyDoctorReview()" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-emerald-600/20">
                            <i data-lucide="check-check" class="w-4 h-4"></i>
                            <span>${t.verifyBtn}</span>
                        </button>
                    </div>
                </div>

                <!-- Red Flag Warning Banner -->
                ${s.red_flag_alert ? `
                    <div class="mt-4 p-4 rounded-2xl bg-rose-50 border-2 border-rose-500 text-rose-900 flex items-start space-x-3">
                        <i data-lucide="alert-triangle" class="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5"></i>
                        <div>
                            <h4 class="text-xs font-bold uppercase tracking-wider text-rose-700">Triage Escalation Warning</h4>
                            <p class="text-sm font-semibold mt-0.5">${s.red_flag_alert}</p>
                        </div>
                    </div>
                ` : ''}

                <!-- Structured Sections Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                    
                    <!-- 1. Chief Complaint & HPI -->
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center">
                            <i data-lucide="activity" class="w-3.5 h-3.5 mr-1 text-emerald-600"></i> Chief Complaint & SOCRATES HPI
                        </h4>
                        <p class="text-xs font-bold text-slate-900 mb-2">${s.chief_complaint || 'N/A'}</p>
                        <div class="space-y-1 text-xs text-slate-600">
                            ${Object.entries(s.socrates_hpi || {}).map(([k, v]) => `
                                <p>• <b>${k.replace('_', ' ').toUpperCase()}:</b> ${v}</p>
                            `).join('')}
                        </div>
                    </div>

                    <!-- 2. AYUSH Pariksha Assessment -->
                    <div class="bg-emerald-50/50 p-4 rounded-2xl border border-emerald-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-2 flex items-center">
                            <i data-lucide="leaf" class="w-3.5 h-3.5 mr-1 text-emerald-700"></i> AYUSH Dashavidha Pariksha
                        </h4>
                        <div class="space-y-1.5 text-xs text-emerald-950">
                            <p>• <b>Dominant Prakriti:</b> <span class="font-bold">${s.prakriti_dominant || 'Vata-Pitta'}</span></p>
                            <p>• <b>Agni Status:</b> ${s.agni_status || 'Vishama Agni'}</p>
                            <p>• <b>Koshtha:</b> ${s.koshtha_status || 'Krura Koshtha'}</p>
                            <p>• <b>Ahara-Vihara:</b> ${JSON.stringify(s.ahara_vihara_notes || {})}</p>
                        </div>
                    </div>

                    <!-- 3. Current Meds & Allergies -->
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center">
                            <i data-lucide="pill" class="w-3.5 h-3.5 mr-1 text-hospital-600"></i> Prior Medications & Allergies
                        </h4>
                        <div class="space-y-1 text-xs text-slate-700">
                            <p class="font-semibold text-rose-700">Allergies: ${(s.drug_allergies || []).join(', ') || 'NKDA'}</p>
                            <div class="mt-2 space-y-1">
                                ${(s.current_medications || []).map(m => `
                                    <p class="text-[11px]">• ${m.name || m} ${m.dosage ? `(${m.dosage})` : ''}</p>
                                `).join('')}
                            </div>
                        </div>
                    </div>

                    <!-- 4. Abnormal Lab Highlights -->
                    <div class="bg-amber-50/60 p-4 rounded-2xl border border-amber-200">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-amber-800 mb-2 flex items-center">
                            <i data-lucide="alert-circle" class="w-3.5 h-3.5 mr-1 text-amber-600"></i> Abnormal Lab Findings
                        </h4>
                        <div class="space-y-1.5 text-xs text-amber-950">
                            ${(s.abnormal_lab_highlights || []).map(h => `
                                <div class="p-1.5 bg-white/80 rounded-lg border border-amber-200">
                                    <span class="font-bold text-rose-700">${h.parameter}: ${h.value}</span>
                                    <span class="text-[11px] text-slate-500 ml-1">(${h.ref_range || 'Ref'})</span>
                                    <p class="text-[10px] text-amber-800">${h.clinical_note || ''}</p>
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

                <!-- 6. Doctor Clinical Notes & Prescription Plan Input -->
                <div class="mt-6 pt-4 border-t border-slate-200 space-y-3">
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-700">Doctor Clinical Notes & Ayurvedic Treatment Plan</label>
                    <textarea id="doctor-notes-input" rows="2" placeholder="Enter clinical assessment notes, Ayurvedic shaman/shodhana recommendations..." class="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-emerald-500">${s.physician_notes || ''}</textarea>
                    <input id="doctor-plan-input" type="text" placeholder="Prescription / Investigation advice (e.g. Continue Yograj Guggulu, repeat S. Uric Acid in 3 weeks)" class="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-emerald-500">
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

// Initial Launch
window.addEventListener('DOMContentLoaded', () => {
    initSpeechRecognition();
    render();
});
