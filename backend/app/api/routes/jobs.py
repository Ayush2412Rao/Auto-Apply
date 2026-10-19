from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_sync_db
from backend.app.models.job import DiscoveredJob, JobMatchEvaluation

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/")
def list_jobs(
    search: str = Query(None),
    min_score: int = Query(None),
    db: Session = Depends(get_sync_db)
):
    query = db.query(DiscoveredJob)
    if search:
        query = query.filter(
            (DiscoveredJob.job_title.ilike(f"%{search}%")) |
            (DiscoveredJob.company_name.ilike(f"%{search}%")) |
            (DiscoveredJob.location.ilike(f"%{search}%"))
        )
    jobs = query.order_by(DiscoveredJob.first_discovered_at.desc()).all()
    
    results = []
    for j in jobs:
        evaluation = db.query(JobMatchEvaluation).filter(JobMatchEvaluation.job_id == j.id).first()
        match_score = evaluation.match_score if evaluation else None
        
        if min_score is not None and (match_score is None or match_score < min_score):
            continue

        results.append({
            "id": j.id,
            "title": j.job_title,
            "company": j.company_name,
            "location": j.location,
            "is_remote": j.is_remote,
            "employment_type": j.employment_type,
            "source": j.source,
            "application_url": j.application_url,
            "description": j.description,
            "discovered_at": j.first_discovered_at.isoformat() if j.first_discovered_at else None,
            "match_score": match_score,
            "recommendation": evaluation.recommendation if evaluation else None,
            "reasoning": evaluation.reasoning_summary if evaluation else None,
            "matched_skills": evaluation.matched_skills if evaluation else [],
            "missing_qualifications": evaluation.missing_qualifications if evaluation else []
        })
    return results

@router.get("/{job_id}")
def get_job_detail(job_id: int, db: Session = Depends(get_sync_db)):
    job = db.query(DiscoveredJob).filter(DiscoveredJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    evaluation = db.query(JobMatchEvaluation).filter(JobMatchEvaluation.job_id == job.id).first()
    return {
        "id": job.id,
        "title": job.job_title,
        "company": job.company_name,
        "location": job.location,
        "description": job.description,
        "is_remote": job.is_remote,
        "source": job.source,
        "application_url": job.application_url,
        "evaluation": {
            "match_score": evaluation.match_score if evaluation else None,
            "recommendation": evaluation.recommendation if evaluation else None,
            "reasoning": evaluation.reasoning_summary if evaluation else None,
            "matched_skills": evaluation.matched_skills if evaluation else [],
            "missing_qualifications": evaluation.missing_qualifications if evaluation else []
        } if evaluation else None
    }
