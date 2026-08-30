import os
import uuid
import shutil
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.config import settings
from app.models.session import IntakeSession
from app.models.document import MedicalDocument
from app.schemas.document_schema import DocumentResponse
from app.services.ocr_service import ocr_service

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_medical_document(
    session_id: str = Form(...),
    document_type: str = Form("prescription"), # prescription | lab_report | discharge_summary
    document_date: Optional[str] = Form(None),
    doctor_or_lab_name: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a prescription or lab report image/PDF, run OCR & entity extraction, and highlight abnormal values.
    """
    session = db.query(IntakeSession).filter(IntakeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save file
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    saved_filename = f"{file_id}_{file.filename or 'record.jpg'}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse date
    parsed_date = None
    if document_date:
        try:
            parsed_date = datetime.strptime(document_date, "%Y-%m-%d").date()
        except ValueError:
            parsed_date = date.today()
    else:
        parsed_date = date.today()

    # Extract entities and abnormal lab markers
    extracted_entities, abnormal_flags, ocr_raw_text = ocr_service.extract_document_entities(
        file_path=saved_path,
        doc_type=document_type,
        doc_date=parsed_date
    )

    # Create document record
    doc_record = MedicalDocument(
        id=file_id,
        session_id=session.id,
        file_name=file.filename or saved_filename,
        file_path=saved_path,
        document_type=document_type,
        document_date=parsed_date,
        doctor_or_lab_name=doctor_or_lab_name or "District Hospital OPD",
        ocr_raw_text=ocr_raw_text,
        extracted_entities=extracted_entities,
        abnormal_flags=abnormal_flags
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    return doc_record

@router.get("/{session_id}/list", response_model=List[DocumentResponse])
def list_session_documents(session_id: str, db: Session = Depends(get_db)):
    docs = db.query(MedicalDocument).filter(MedicalDocument.session_id == session_id).all()
    return docs
