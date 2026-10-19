import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.app.db.session import get_sync_db
from backend.app.models.user import JobPreference, QuestionnaireAnswer
from backend.app.config import BASE_DIR

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.get("/")
def get_preferences(db: Session = Depends(get_sync_db)):
    pref = db.query(JobPreference).first()
    if not pref:
        pref_file = BASE_DIR / "data" / "preferences.json"
        if pref_file.exists():
            with open(pref_file, "r", encoding="utf-8") as f:
                return json.load(f)
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    return {
        "target_titles": pref.target_titles,
        "preferred_locations": pref.preferred_locations,
        "remote_preference": pref.remote_preference,
        "min_match_score": pref.min_match_score,
        "max_applications_per_hour": pref.max_applications_per_hour,
        "max_applications_per_day": pref.max_applications_per_day,
        "automation_mode": pref.automation_mode,
        "notice_period_days": pref.notice_period_days,
        "work_authorization": pref.work_authorization,
        "excluded_companies": pref.excluded_companies
    }

@router.post("/")
def update_preferences(data: dict = Body(...), db: Session = Depends(get_sync_db)):
    pref = db.query(JobPreference).first()
    if pref:
        if "min_match_score" in data: pref.min_match_score = data["min_match_score"]
        if "automation_mode" in data: pref.automation_mode = data["automation_mode"]
        if "target_titles" in data: pref.target_titles = data["target_titles"]
        if "preferred_locations" in data: pref.preferred_locations = data["preferred_locations"]
        db.commit()
    return {"status": "success", "message": "Preferences updated"}

@router.get("/questionnaire")
def get_questionnaire_answers(db: Session = Depends(get_sync_db)):
    answers = db.query(QuestionnaireAnswer).all()
    return [
        {
            "id": a.id,
            "key": a.question_key,
            "question": a.question_text,
            "answer": a.answer_value,
            "status": a.status
        }
        for a in answers
    ]
