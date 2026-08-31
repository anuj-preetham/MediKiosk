# MediKiosk — AI-Powered Patient Clinical Intake & Document Intelligence Platform

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-blue.svg)](https://sih.gov.in/)
[![Problem Statement](https://img.shields.io/badge/Problem%20ID-SIH26047-green.svg)](https://sih.gov.in/)
[![Healthcare Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%7C%20PostgreSQL%20%7C%20FHIR-blue.svg)](#)

**MediKiosk** is an AI-powered clinical history intake and medical-document digitization platform built for hospital OPDs.

It empowers patients to independently record structured medical histories through natural spoken voice conversation and guided touchscreen interaction, digitizes previous paper prescriptions and lab reports, detects clinical red-flag emergencies in real time, and synthesizes structured, physician-ready summaries before consultation.

---

## 🌟 Key Features

1. **Multimodal Conversational Intake:** Adaptive voice + touch questioning in Hindi & English using the SOCRATES clinical framework (*Site, Onset, Character, Radiation, Associated symptoms, Timing, Exacerbating/relieving factors, Severity*).
2. **Medical Document Digitization & Timeline:** Multilingual OCR for handwritten & printed prescriptions, lab reports, and discharge summaries with automatic extraction of medicines, dosages, and abnormal lab parameter highlighting.
3. **Emergency Red-Flag Detection & Triage:** Real-time clinical pattern recognition to immediately alert medical staff on acute emergencies (e.g., suspected acute coronary syndrome, stroke signs, acute respiratory distress).
4. **Physician Review Dashboard:** Fast OPD waiting queue and clinical review interface for doctors to verify, edit, and approve structured AI-generated histories before clinical decision-making.
5. **Consent, Privacy & ABDM / FHIR Interoperability:** Consent-first data collection (DPDP Act 2023), ABHA linkage, and export of standardized NRCES / ABDM-compliant FHIR R4 Bundles.

---

## 🚀 Quickstart Guide

### 1. (Optional) Run PostgreSQL via Docker
```bash
docker compose up -d
```
*(If Docker is not running, MediKiosk automatically falls back to local SQLite session storage without crashing).*

### 2. Start the Server
```bash
./backend/.venv/bin/python backend/run.py
```
Open your browser at: **`http://localhost:8000`**

### 3. Run Automated Tests
```bash
./backend/.venv/bin/pytest backend/tests -v
```

---

## 📄 Compliance & Standards

Complies with the **Digital Personal Data Protection (DPDP) Act 2023** and **Ayushman Bharat Digital Mission (ABDM) FHIR R4** standards.
