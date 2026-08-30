# SIH 2026: Problem Statement & Project Specification

## 1. Hackathon & Problem Details
- **Hackathon:** Smart India Hackathon 2026
- **Problem Statement ID:** SIH26047
- **Title:** Patient Case-Taking Software
- **Category:** Software
- **Domain / Theme:** Smart Automation / Healthcare / AYUSH
- **Organization / Ministry:** Ministry of Ayush
- **Associated Institution:** All India Institute of Ayurveda (AIIA)
- **Working Project Name:** MediKiosk
- **Project Type:** AI-powered patient-facing clinical history and medical-document intake platform

## 2. Problem Overview & Core Challenge

### Official Problem
Indian hospitals, particularly high-volume government OPDs, face severe clinical history-taking and documentation bottlenecks. Doctors may have only a few minutes per patient while being expected to collect a complete medical history, review previous records, examine the patient, diagnose, counsel, and prescribe.

AYUSH settings add further complexity because Ayurvedic case-taking requires detailed assessment such as Prakriti, Vikriti, Agni, Koshtha, Ahara-Vihara, Nidana, Samprapti, and Dashavidha Pariksha. Manually capturing this information within OPD time constraints is difficult.

Patients also commonly carry paper prescriptions, laboratory reports, discharge summaries, and other medical documents from multiple providers. These documents may be handwritten, multilingual, unstructured, and chronologically disordered. Existing hospital registration systems generally capture demographic/appointment information rather than detailed clinical history, while generic scanners do not extract and structure clinical information.

The problem statement calls for a purpose-built patient-facing software platform that allows patients to independently record comprehensive medical history through natural spoken conversation and guided touchscreen interaction, digitize existing medical documents, and produce a structured physician-ready summary before the consultation.

The solution should integrate with hospital information systems and the Ayushman Bharat Digital Mission (ABDM), using ABHA and FHIR-based interoperability where applicable.

### Core Problem to Solve
Reduce the amount of physician time spent manually collecting and organizing patient history and prior medical records without replacing physician judgment.

The system should:
1. Collect structured clinical history through voice and touch.
2. Adapt questioning based on the patient's responses.
3. Support AYUSH-specific history-taking.
4. Digitize and structure prior medical documents.
5. Build a chronological medical timeline.
6. Generate a concise, physician-readable clinical summary.
7. Detect potential red flags and route them for immediate human attention.
8. Preserve patient consent, privacy, and physician control.
9. Support integration with HIS/EMR and ABDM/FHIR infrastructure.

## 3. Key Objectives & Expected Solution

### Objective 1 — Conversational Multimodal History Taking
- Conduct a structured clinical interview using natural voice conversation.
- Provide touch-based alternatives for every important question.
- Support multilingual and multi-accent input.
- Use adaptive questioning rather than a rigid questionnaire.
- Structure information into:
  - Chief complaint
  - History of present illness (HPI)
  - Past medical history
  - Past surgical history
  - Drug history
  - Allergy history
  - Family history
  - Personal history
  - Review of systems
  - Prior investigations
- Use appropriate clinical questioning frameworks such as SOCRATES where relevant.

### Objective 2 — AYUSH Case-Taking
- Provide an AYUSH-specific history mode.
- Support Dashavidha Pariksha parameters including:
  - Prakriti
  - Vikriti
  - Sara
  - Samhanana
  - Pramana
  - Satmya
  - Sattva
  - Ahara Shakti
  - Vyayama Shakti
  - Vaya
- Capture Ahara-Vihara and other relevant AYUSH history information.
- Do not invent clinical conclusions or autonomous diagnoses.

### Objective 3 — Medical Document Digitization
- Accept prescriptions, laboratory reports, discharge summaries, and similar documents.
- Perform OCR on printed and handwritten documents where feasible.
- Support multilingual documents.
- Extract structured entities such as:
  - Diagnoses
  - Medicines
  - Dosages
  - Investigation values
  - Reference ranges
  - Procedures/surgeries
- Organize documents chronologically.
- Highlight abnormal laboratory values and other clinically relevant information for physician review.

### Objective 4 — Physician-Ready Summary
Generate a concise structured summary combining:
- Conversational history
- Extracted information from prior documents
- Relevant investigations
- Medication/allergy information
- Timeline information

The physician must be able to review, edit, confirm, reject, or correct the generated summary.

**Critical principle:** AI output is decision support and documentation assistance, not an autonomous diagnosis or substitute for a physician.

### Objective 5 — Red-Flag Detection & Triage
- Detect predefined emergency/high-risk symptom patterns.
- Examples include acute chest pain with dyspnoea and stroke-like symptoms.
- Escalate detected red flags to appropriate human/triage staff.
- Never allow the AI to independently make emergency treatment decisions.

### Objective 6 — Accessibility
- Design for elderly, low-literacy, first-time, and non-technical users.
- Use simple icon-driven interfaces.
- Provide audio prompts and confirmations.
- Support local-language interaction.
- Minimize typing requirements.
- The patient should be able to complete the workflow with minimal or no staff assistance.

### Objective 7 — Consent, Privacy & ABDM
- Use consent-first data collection.
- Support granular and revocable consent.
- Explain consent through audio for users with low literacy.
- Authenticate/link patients using ABHA where applicable.
- Support ABDM/FHIR-compatible integration.
- Protect sensitive health information during processing and storage.
- Clear temporary session data after submission where appropriate.
- Follow the Digital Personal Data Protection Act 2023 and applicable ABDM requirements.

## 4. Target Users & Personas

### Primary Users
- Patients visiting high-volume government hospital OPDs.
- Elderly patients.
- Low-literacy patients.
- First-time hospital visitors.
- Patients who are uncomfortable with conventional digital forms.
- Patients carrying physical medical records.
- AYUSH patients requiring detailed case-taking.

### Secondary Users
- Physicians.
- AYUSH physicians.
- OPD/triage staff.
- Nurses and clinical assistants.
- Hospital registration/front-desk staff.
- Hospital administrators.
- Health information/EMR personnel.

### Tertiary / Integration Stakeholders
- Hospital HIS/EMR systems.
- ABDM ecosystem.
- ABHA/Personal Health Record infrastructure.
- Government/AYUSH healthcare institutions.

## 5. Architectural & Technical Constraints

### Target Platform
- Patient-facing web application / kiosk-style interface.
- Physician-facing clinical summary/dashboard.
- Backend API and persistent database.
- AI services for conversational processing, speech, document OCR/extraction, and summarization.
- Designed so the patient workflow can run on a shared hospital terminal/kiosk rather than requiring the patient to own a smartphone.

### Core Functional Architecture
The system should conceptually follow:

**Patient → Identity & Consent → Voice/Touch History → Clinical Structuring → Document Upload/OCR → Entity Extraction → Timeline → Summary Generation → Physician Review → HIS/ABDM Integration**

### AI Constraints
- Prefer constrained, structured clinical workflows over unrestricted chatbot behavior.
- Maintain a defined clinical history ontology/schema.
- Validate structured outputs before persistence.
- Preserve source information where possible so physicians can verify AI-extracted data.
- Do not present generated content as confirmed medical fact when it is uncertain.
- AI-generated summaries must remain editable and physician-verifiable.
- Red-flag detection should trigger human review rather than autonomous action.

### Language & Accessibility Constraints
- Hindi and English are required target languages.
- Architecture should allow expansion to major Indian regional languages.
- Voice recognition must account for Indian accents and noisy environments.
- Touch interaction must remain available as a fallback to speech.
- Audio guidance should be available for low-literacy users.

### Medical Document Constraints
- Documents may be:
  - Printed
  - Handwritten
  - Scanned
  - Multilingual
  - Poor quality
  - Chronologically unordered
- OCR/extraction must tolerate imperfect documents.
- Extracted data should be treated as provisional until verified where accuracy is uncertain.

### Security & Privacy Constraints
- Health data is sensitive and must be handled accordingly.
- Implement authentication and authorization.
- Enforce least-privilege access.
- Use secure transport and appropriate data protection.
- Implement explicit consent before collecting/sharing patient data.
- Avoid unnecessary retention of temporary kiosk-session information.
- Maintain an audit trail for important clinical-data operations where appropriate.
- Do not expose patient information in logs, debug output, client-side storage, or public URLs.

### Integration Constraints
- Design APIs and data models so HIS/EMR integration can be added cleanly.
- Use FHIR-compatible representations for relevant clinical data where practical.
- ABDM integration should be modular rather than tightly coupling the entire application to external infrastructure.
- External integrations may be mocked during the hackathon demo if live government/HIS access is unavailable.

### Demo / Showcase Requirements
The hackathon prototype should demonstrate an end-to-end workflow using controlled/mock data where external integrations are unavailable:

1. Patient identification/login.
2. Language selection.
3. Consent.
4. Voice/touch clinical interview.
5. Adaptive follow-up questions.
6. AYUSH case-taking where applicable.
7. Red-flag detection demonstration.
8. Upload/scan prior medical documents.
9. OCR and clinical entity extraction.
10. Chronological medical timeline.
11. AI-generated structured clinical summary.
12. Physician review/edit/confirmation.
13. Mock or demonstrable HIS/ABDM/FHIR submission.
14. Proper session termination and data handling.

### Non-Goals / Boundaries
- The system is not an autonomous doctor.
- It must not independently diagnose patients.
- It must not prescribe medication autonomously.
- It must not replace physician review.
- AI suggestions must remain explainable/verifiable enough for clinical users.
- Hackathon mock integrations must not be represented as live government integrations.

## 6. Product Modules

### Module A — Conversational Multimodal History Engine
Voice + touch clinical interview, adaptive questioning, multilingual support, AYUSH mode, and red-flag detection.

### Module B — Medical Document Digitization & Intelligence
Document upload/scanning, OCR, clinical entity extraction, timeline construction, abnormal-value highlighting, and document review.

### Module C — Structured History Summary Generator
Combines patient responses and document-derived information into a standardized physician-ready summary.

### Module D — Consent, Privacy & ABDM Integration
Identity, consent management, secure processing, FHIR/ABDM integration, HIS/EMR routing, and session cleanup.

### Module E — Physician Review Interface
Displays the generated summary and source information so the physician can verify, edit, accept, or reject AI-generated content.

## 7. End-to-End Patient Journey

1. **Identify:** Patient identifies themselves using the supported identity flow and selects a language.
2. **Consent:** Patient receives an accessible explanation and explicitly grants consent.
3. **Converse:** AI conducts the adaptive clinical history interview through voice and/or touch.
4. **Triage:** Red-flag symptoms are detected and escalated to human staff.
5. **Scan:** Patient uploads/scans previous prescriptions, reports, and discharge documents.
6. **Extract:** OCR and AI structure the document contents.
7. **Timeline:** Previous records are organized chronologically.
8. **Summarize:** The system creates a standardized clinical history summary.
9. **Route:** Relevant information is made available to the hospital/HIS/ABDM integration layer.
10. **Consult:** Physician reviews and edits the generated history before using it for clinical decision-making.

## 8. Permanent Development Context for AI Coding Agents

When modifying or extending this project:

- Treat the SIH26047 problem statement as the product's primary source of truth.
- Preserve the patient-first and physician-in-control design.
- Do not turn the application into a generic chatbot or generic hospital-management system.
- Prioritize the clinical intake → document intelligence → physician summary pipeline.
- Keep AI functionality modular and replaceable.
- Keep external ABDM/HIS integrations behind clear service/API boundaries.
- Prefer structured schemas and typed interfaces over free-form AI output.
- Validate AI-generated structured data before saving it.
- Never silently discard clinically relevant source information.
- Do not introduce features that imply autonomous diagnosis or treatment.
- Maintain accessibility for users with low digital literacy.
- Assume noisy audio, imperfect documents, and incomplete patient responses.
- Design the demo path so the complete workflow works with deterministic/mock data even when external APIs or AI services are unavailable.
- Keep secrets, patient data, tokens, and credentials out of source control and logs.
