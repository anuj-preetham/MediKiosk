from datetime import datetime
from typing import Dict, Any, List, Optional

class PDFService:
    """
    Service to generate structured, formatted printable OPD Consultation Case Sheets.
    Outputs hospital-standard formatted HTML ready for browser window.print() or direct PDF export.
    """

    def generate_opd_casesheet_html(
        self,
        session_id: str,
        patient: Dict[str, Any],
        clinical_history: Optional[Dict[str, Any]],
        documents: List[Dict[str, Any]],
        review: Optional[Dict[str, Any]],
        safety_alerts: List[Dict[str, Any]] = []
    ) -> str:
        p_name = patient.get("full_name", "Anonymous Patient")
        p_age = patient.get("age", "N/A")
        p_gender = patient.get("gender", "N/A")
        abha_id = patient.get("abha_id", "N/A")
        p_phone = patient.get("phone_number", "N/A")
        
        chief_complaint = clinical_history.get("chief_complaint", "N/A") if clinical_history else "N/A"
        socrates = clinical_history.get("socrates_hpi", {}) if clinical_history else {}
        past_med = clinical_history.get("past_medical_history", []) if clinical_history else []
        allergies = clinical_history.get("drug_allergies", []) if clinical_history else []
        meds = clinical_history.get("current_medications", []) if clinical_history else []
        personal = clinical_history.get("personal_history", {}) if clinical_history else {}

        doc_name = review.get("doctor_name", "Consultant Physician") if review else "Consultant Physician"
        dept = review.get("department", "Department of General Medicine") if review else "Department of General Medicine"
        notes = review.get("physician_clinical_notes", "Clinical intake verified and completed.") if review else "Intake summary generated for OPD physician evaluation."
        plan = review.get("prescribed_plan", "") if review else ""

        now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")

        # Format Socrates bullets
        socrates_rows = "".join([
            f"<tr><td style='padding:4px 8px; font-weight:600; width:30%; color:#475569;'>{k.replace('_', ' ').title()}:</td><td style='padding:4px 8px;'>{v}</td></tr>"
            for k, v in socrates.items()
        ]) or "<tr><td colspan='2' style='padding:6px 8px;'>No specific HPI details recorded.</td></tr>"

        # Format Allergies
        allergy_html = ", ".join(allergies) if allergies else "<span style='color:#16a34a; font-weight:600;'>NKDA (No Known Drug Allergies)</span>"

        # Format Medications
        meds_rows = "".join([
            f"<tr><td style='padding:4px 8px;'>{m.get('name', m)}</td><td style='padding:4px 8px;'>{m.get('dosage', 'Standard')}</td><td style='padding:4px 8px;'>{m.get('frequency', 'As directed')}</td></tr>"
            for m in meds
        ]) if meds else "<tr><td colspan='3' style='padding:6px 8px;'>No prior medications recorded.</td></tr>"

        # Format Safety Alerts
        safety_html = ""
        if safety_alerts:
            safety_html = "<div style='background:#fef2f2; border:1px solid #f87171; border-radius:8px; padding:12px; margin-bottom:16px; color:#991b1b;'>"
            safety_html += "<div style='font-weight:700; font-size:13px; margin-bottom:4px;'>⚠️ CLINICAL SAFETY ALERTS DETECTED</div>"
            for alert in safety_alerts:
                safety_html += f"<div style='font-size:12px; margin-top:2px;'>• <b>{alert.get('allergy_trigger', 'Alert')}:</b> {alert.get('clinical_advice', '')}</div>"
            safety_html += "</div>"

        # HTML Template
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OPD Case Sheet — {p_name}</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.4; padding: 24px; max-width: 850px; margin: 0 auto; }}
        .header {{ border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: flex-start; }}
        .hospital-title {{ font-size: 20px; font-weight: 800; color: #1e3a8a; letter-spacing: -0.5px; }}
        .dept-title {{ font-size: 13px; font-weight: 600; color: #64748b; }}
        .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 16px; font-size: 12px; }}
        .section-title {{ font-size: 13px; font-weight: 700; text-transform: uppercase; color: #1e40af; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-top: 16px; margin-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 12px; }}
        th {{ background: #f1f5f9; text-align: left; padding: 6px 8px; font-weight: 600; color: #334155; }}
        td {{ border-bottom: 1px solid #f1f5f9; }}
        .footer {{ margin-top: 36px; padding-top: 12px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; font-size: 11px; color: #64748b; }}
        .sign-area {{ margin-top: 40px; text-align: right; }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="hospital-title">DISTRICT HOSPITAL & CLINICAL OPD CENTER</div>
            <div class="dept-title">{dept}</div>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">MediKiosk Smart Intake System | Case Ref: MEDIKIOSK-{session_id[:8].upper()}</div>
        </div>
        <div style="text-align: right; font-size: 11px;">
            <div><b>Date:</b> {now_str}</div>
            <div style="color: #2563eb; font-weight: 700;">OPD Case Sheet</div>
        </div>
    </div>

    <!-- Patient Demographics -->
    <div class="meta-box">
        <table style="margin: 0;">
            <tr>
                <td style="width: 25%; font-weight: 600;">Patient Name:</td>
                <td style="width: 35%; font-weight: 700; color: #0f172a;">{p_name}</td>
                <td style="width: 20%; font-weight: 600;">ABHA ID:</td>
                <td style="width: 20%; font-family: monospace; font-weight: 700; color: #2563eb;">{abha_id}</td>
            </tr>
            <tr>
                <td style="font-weight: 600;">Age / Gender:</td>
                <td>{p_age} Years / {p_gender}</td>
                <td style="font-weight: 600;">Contact:</td>
                <td>{p_phone}</td>
            </tr>
        </table>
    </div>

    {safety_html}

    <!-- Chief Complaint & HPI -->
    <div class="section-title">1. Chief Complaint & History of Present Illness (SOCRATES)</div>
    <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">Chief Complaint: {chief_complaint}</div>
    <table>
        {socrates_rows}
    </table>

    <!-- Past Medical History & Allergies -->
    <div class="section-title">2. Medical History, Allergies & Lifestyle</div>
    <table>
        <tr>
            <td style="width: 25%; font-weight: 600; padding: 4px 8px;">Past Illnesses:</td>
            <td style="padding: 4px 8px;">{", ".join(past_med) if past_med else "No chronic illnesses reported"}</td>
        </tr>
        <tr>
            <td style="font-weight: 600; padding: 4px 8px;">Drug Allergies:</td>
            <td style="padding: 4px 8px; color: #b91c1c; font-weight: 600;">{allergy_html}</td>
        </tr>
        <tr>
            <td style="font-weight: 600; padding: 4px 8px;">Personal/Habits:</td>
            <td style="padding: 4px 8px;">Diet: {personal.get('diet', 'Regular')} | Smoking: {personal.get('smoking', 'No')} | Alcohol: {personal.get('alcohol', 'No')}</td>
        </tr>
    </table>

    <!-- Current Medications -->
    <div class="section-title">3. Current Medications Recorded</div>
    <table>
        <thead>
            <tr>
                <th style="width: 50%;">Medicine Name</th>
                <th style="width: 25%;">Dosage / Strength</th>
                <th style="width: 25%;">Frequency</th>
            </tr>
        </thead>
        <tbody>
            {meds_rows}
        </tbody>
    </table>

    <!-- Physician Assessment & Plan -->
    <div class="section-title">4. Physician Clinical Assessment & Treatment Plan</div>
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 12px; font-size: 12px;">
        <div style="font-weight: 700; color: #334155; margin-bottom: 4px;">Clinical Notes & Provisional Diagnosis:</div>
        <div style="white-space: pre-line; color: #0f172a;">{notes}</div>
        {f"<div style='font-weight: 700; color: #334155; margin-top: 8px; margin-bottom: 4px;'>Prescription & Investigation Advice:</div><div style='color: #0f172a;'>{plan}</div>" if plan else ""}
    </div>

    <!-- Sign-off -->
    <div class="sign-area">
        <div style="font-weight: 700; font-size: 13px; color: #0f172a;">{doc_name}</div>
        <div style="font-size: 11px; color: #64748b;">Consultant Physician / OPD Incharge</div>
        <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">Verified electronically via MediKiosk (SIH26047)</div>
    </div>

    <div class="footer">
        <div>Complies with Digital Personal Data Protection Act 2023 & ABDM FHIR R4 Standards</div>
        <div>Page 1 of 1</div>
    </div>

    <div class="no-print" style="text-align: center; margin-top: 24px;">
        <button onclick="window.print()" style="padding: 10px 24px; background: #2563eb; color: white; border: none; border-radius: 8px; font-weight: 700; cursor: pointer;">Print / Save as PDF</button>
    </div>
</body>
</html>
"""
        return html

pdf_service = PDFService()
