import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.db.session import get_sync_db
from backend.app.models.application import ResumeVersion
from backend.app.models.job import DiscoveredJob
from backend.app.config import BASE_DIR

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.get("/")
def list_tailored_resumes(db: Session = Depends(get_sync_db)):
    versions = db.query(ResumeVersion).order_by(ResumeVersion.created_at.desc()).all()
    results = []
    for v in versions:
        job = db.query(DiscoveredJob).filter(DiscoveredJob.id == v.job_id).first()
        results.append({
            "id": v.id,
            "version_identifier": v.version_identifier,
            "job_id": v.job_id,
            "job_title": job.job_title if job else "N/A",
            "company_name": job.company_name if job else "N/A",
            "pdf_available": bool(v.pdf_path and os.path.exists(v.pdf_path)),
            "docx_available": bool(v.docx_path and os.path.exists(v.docx_path)),
            "validation_status": v.validation_status,
            "created_at": v.created_at.isoformat() if v.created_at else None
        })
    return results

@router.get("/master/pdf")
def get_master_pdf():
    pdf_path = BASE_DIR / "data" / "resumes" / "Ayush_Rao_Master_Resume.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Master PDF not found")
    return FileResponse(str(pdf_path), media_type="application/pdf", filename="Ayush_Rao_Resume.pdf")

@router.get("/master/docx")
def get_master_docx():
    docx_path = BASE_DIR / "data" / "resumes" / "Ayush_Rao_Master_Resume.docx"
    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="Master DOCX not found")
    return FileResponse(
        str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="Ayush_Rao_Resume.docx"
    )

@router.get("/{version_id}/pdf")
def download_tailored_pdf(version_id: int, db: Session = Depends(get_sync_db)):
    rv = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not rv or not rv.pdf_path or not os.path.exists(rv.pdf_path):
        raise HTTPException(status_code=404, detail="Tailored PDF file not found")
    return FileResponse(rv.pdf_path, media_type="application/pdf", filename=os.path.basename(rv.pdf_path))

@router.get("/{version_id}/docx")
def download_tailored_docx(version_id: int, db: Session = Depends(get_sync_db)):
    rv = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not rv or not rv.docx_path or not os.path.exists(rv.docx_path):
        raise HTTPException(status_code=404, detail="Tailored DOCX file not found")
    return FileResponse(
        rv.docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(rv.docx_path)
    )
