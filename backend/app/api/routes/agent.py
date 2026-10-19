from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.db.session import get_sync_db
from backend.app.models.application import AgentRun, AgentRunEvent, JobApplication
from backend.app.models.job import DiscoveredJob, JobMatchEvaluation
from backend.app.agent.graph import execute_pipeline

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/run-now")
def trigger_agent_run(background_tasks: BackgroundTasks):
    """Triggers the full LangGraph pipeline asynchronously in the background."""
    background_tasks.add_task(execute_pipeline, user_id=1, trigger_type="manual_dashboard")
    return {
        "status": "initiated",
        "message": "Agentic Auto-Apply workflow triggered in the background."
    }

@router.get("/runs")
def list_agent_runs(db: Session = Depends(get_sync_db)):
    runs = db.query(AgentRun).order_by(AgentRun.started_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "uuid": r.run_uuid,
            "trigger": r.trigger_type,
            "status": r.status,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "jobs_discovered": r.jobs_discovered,
            "jobs_matched": r.jobs_matched,
            "resumes_tailored": r.resumes_tailored,
            "applications_submitted": r.applications_submitted,
            "error": r.error_summary
        }
        for r in runs
    ]

@router.get("/runs/latest")
def get_latest_run(db: Session = Depends(get_sync_db)):
    latest = db.query(AgentRun).order_by(AgentRun.started_at.desc()).first()
    if not latest:
        return {"status": "no_runs", "message": "No agent runs recorded yet."}
    
    events = db.query(AgentRunEvent).filter(AgentRunEvent.run_id == latest.id).order_by(AgentRunEvent.timestamp.asc()).all()
    return {
        "id": latest.id,
        "uuid": latest.run_uuid,
        "status": latest.status,
        "trigger": latest.trigger_type,
        "started_at": latest.started_at.isoformat() if latest.started_at else None,
        "completed_at": latest.completed_at.isoformat() if latest.completed_at else None,
        "metrics": {
            "discovered": latest.jobs_discovered,
            "matched": latest.jobs_matched,
            "tailored": latest.resumes_tailored,
            "submitted": latest.applications_submitted
        },
        "logs": [e.message for e in events]
    }

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_sync_db)):
    total_jobs = db.query(DiscoveredJob).count()
    high_matches = db.query(JobMatchEvaluation).filter(JobMatchEvaluation.match_score >= 75).count()
    total_applied = db.query(JobApplication).filter(JobApplication.status == "applied").count()
    pending_approval = db.query(JobApplication).filter(JobApplication.status == "pending_approval").count()
    latest_run = db.query(AgentRun).order_by(AgentRun.started_at.desc()).first()

    return {
        "jobs_discovered": total_jobs,
        "high_matches": high_matches,
        "applications_submitted": total_applied,
        "pending_approval": pending_approval,
        "scheduler_status": "Active (Hourly)",
        "last_run_status": latest_run.status if latest_run else "Ready"
    }
