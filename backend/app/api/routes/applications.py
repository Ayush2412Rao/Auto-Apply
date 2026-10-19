from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from backend.app.db.session import get_sync_db
from backend.app.models.application import JobApplication, ResumeVersion
from backend.app.models.job import DiscoveredJob, JobMatchEvaluation

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("/")
def list_applications(status: str = Query(None), db: Session = Depends(get_sync_db)):
    query = db.query(JobApplication)
    if status:
        query = query.filter(JobApplication.status == status)
    apps = query.order_by(JobApplication.updated_at.desc()).all()
    
    results = []
    for app in apps:
        job = db.query(DiscoveredJob).filter(DiscoveredJob.id == app.job_id).first()
        evaluation = db.query(JobMatchEvaluation).filter(JobMatchEvaluation.job_id == app.job_id).first()
        results.append({
            "id": app.id,
            "job_id": app.job_id,
            "resume_version_id": app.resume_version_id,
            "title": job.job_title if job else "N/A",
            "company": job.company_name if job else "N/A",
            "location": job.location if job else "N/A",
            "match_score": evaluation.match_score if evaluation else None,
            "status": app.status,
            "approved": app.approved_by_user,
            "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
            "evidence": app.submission_evidence,
            "error": app.error_message,
            "updated_at": app.updated_at.isoformat() if app.updated_at else None
        })
    return results

@router.post("/{app_id}/approve")
def approve_application(app_id: int, db: Session = Depends(get_sync_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.approved_by_user = True
    app.approved_at = datetime.utcnow()
    app.status = "applied"
    app.submitted_at = datetime.utcnow()
    app.submission_evidence = {
        "confirmation_code": f"MANUAL-APPROVAL-{app.id}",
        "verified_via": "user_dashboard_approval",
        "submitted_at_iso": datetime.utcnow().isoformat()
    }
    db.commit()
    return {"status": "success", "message": "Application approved and marked as submitted."}

@router.post("/{app_id}/reject")
def reject_application(app_id: int, db: Session = Depends(get_sync_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = "rejected_by_user"
    db.commit()
    return {"status": "success", "message": "Application rejected."}
