"""
TalentIQ — Resume Upload Router
Handles PDF/DOCX resume file uploads.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

from app.config import settings
from app.engines.file_processing_engine import FileProcessingEngine

router = APIRouter()

UPLOAD_FOLDER = os.path.join(settings.BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_engine = FileProcessingEngine()


@router.post("/upload", tags=["Upload"])
async def upload_resume(file: UploadFile = File(...)):
    # Validate extension
    filename = file.filename or "resume"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text using File Processing Engine
    extracted_text = file_engine.extract_text(file_path)

    return {
        "file_path": file_path,
        "extracted_text": extracted_text,
        "char_count": len(extracted_text),
    }
