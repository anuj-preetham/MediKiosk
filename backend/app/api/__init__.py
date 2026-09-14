from fastapi import APIRouter
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.doctor import router as doctor_router
from app.api.abdm import router as abdm_router
from app.api.settings import router as settings_router

api_router = APIRouter()
api_router.include_router(sessions_router, prefix="/sessions", tags=["Intake Sessions"])
api_router.include_router(chat_router, prefix="/chat", tags=["Clinical Dialogue"])
api_router.include_router(documents_router, prefix="/documents", tags=["Document Intelligence & OCR"])
api_router.include_router(doctor_router, prefix="/doctor", tags=["Physician Review"])
api_router.include_router(abdm_router, prefix="/abdm", tags=["ABDM & FHIR"])
api_router.include_router(settings_router, prefix="/settings", tags=["AI & System Settings"])

