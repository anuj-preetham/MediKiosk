import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import Base, engine
from app.api import api_router
from app.utils.seed_data import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medikiosk")

# Create tables immediately on module load
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing MediKiosk Database Schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Checking & seeding demo cases...")
    try:
        seed_database()
    except Exception as e:
        logger.warning(f"Seed database note: {e}")
    logger.info("MediKiosk Backend Started Successfully!")
    yield
    logger.info("MediKiosk Backend shutting down...")

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Multimodal Patient Intake & Clinical History Platform for SIH 2026 (SIH26047)",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount upload directory for document preview
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Mount frontend static assets
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def serve_home():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "problem_statement": "SIH26047 - Patient Case-Taking Software",
        "ministry": "Ministry of Ayush / AIIA",
        "status": "healthy",
        "docs_url": "/docs"
    }

@app.get("/api/info")
def root_info():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "problem_statement": "SIH26047 - Patient Case-Taking Software",
        "ministry": "Ministry of Ayush / AIIA",
        "status": "healthy",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "uploads_ready": os.path.exists(settings.UPLOAD_DIR)}
