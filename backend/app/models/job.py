import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.db.session import Base

class DiscoveredJob(Base):
    __tablename__ = "discovered_jobs"

    id = Column(Integer, primary_key=True, index=True)
    canonical_url = Column(String(1000), unique=True, index=True, nullable=False)
    source = Column(String(100), index=True, nullable=False)
    
    company_name = Column(String(255), index=True, nullable=False)
    job_title = Column(String(255), index=True, nullable=False)
    location = Column(String(255), nullable=True)
    is_remote = Column(Boolean, default=False)
    employment_type = Column(String(50), default="full-time")
    
    description = Column(Text, nullable=False)
    salary_raw = Column(String(255), nullable=True)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="INR")
    
    posting_date = Column(DateTime, nullable=True)
    application_url = Column(String(1000), nullable=True)
    raw_metadata = Column(JSON, default=dict)
    
    first_discovered_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    evaluations = relationship("JobMatchEvaluation", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")


class JobMatchEvaluation(Base):
    __tablename__ = "job_match_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("discovered_jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    match_score = Column(Integer, nullable=False)
    required_skills_coverage = Column(Float, default=0.0)
    preferred_skills_coverage = Column(Float, default=0.0)
    
    matched_skills = Column(JSON, default=list)
    missing_qualifications = Column(JSON, default=list)
    eligibility_status = Column(String(50), default="eligible")
    recommendation = Column(String(50), default="review")
    reasoning_summary = Column(Text, nullable=True)
    
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("DiscoveredJob", back_populates="evaluations")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("job_id", "user_id", name="uq_job_user_evaluation"),
    )
