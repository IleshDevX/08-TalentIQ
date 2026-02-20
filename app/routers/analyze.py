"""
TalentIQ — Analyze Router
POST /analyze  — full analysis pipeline (file + optional target_role & jd_text)
GET  /roles    — list all available roles for the UI dropdown
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.services.analysis_service import AnalysisService
from app.core import vector_store

router = APIRouter()

# Single service instance — engines are initialised once
analysis_service = AnalysisService()


@router.get("/roles", tags=["Roles"])
async def list_roles():
    """Return every available target role (for the Streamlit dropdown)."""
    roles_db = vector_store.get_roles_db()
    result = []
    for name, info in roles_db.items():
        result.append({
            "role_name": info.get("role_name", name),
            "category": info.get("category", ""),
            "domain": info.get("domain", ""),
            "level": info.get("level", ""),
        })
    result.sort(key=lambda r: (r["category"], r["role_name"]))
    return {"roles": result, "total": len(result)}


@router.post("/analyze", tags=["Analysis"])
async def analyze_resume(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None),
    jd_text: Optional[str] = Form(None),
):
    """
    Upload a resume and receive the full TalentIQ intelligence report.

    - **file**: PDF or DOCX resume
    - **target_role**: (optional) role to evaluate against — if omitted, the
      best semantic match is used automatically.
    - **jd_text**: (optional) job description to compare — if omitted, the
      default JD for the resolved role is loaded from the database.
    """
    try:
        report = await analysis_service.process(
            file,
            target_role=target_role,
            jd_text=jd_text,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if "error" in report and len(report) == 1:
        raise HTTPException(status_code=400, detail=report["error"])

    return report
