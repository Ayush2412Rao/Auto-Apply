import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_sync_db
from backend.app.models.user import User, UserProfile
from backend.app.config import BASE_DIR

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/")
def get_user_profile(db: Session = Depends(get_sync_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        profile_file = BASE_DIR / "data" / "master_profile.json"
        if profile_file.exists():
            with open(profile_file, "r", encoding="utf-8") as f:
                return json.load(f)
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": profile.id,
        "contact": profile.contact_info,
        "summary": profile.professional_summary,
        "skills": profile.skills,
        "experience": profile.experience,
        "education": profile.education,
        "projects": profile.projects,
        "certifications": profile.certifications,
        "is_verified": profile.is_verified
    }
