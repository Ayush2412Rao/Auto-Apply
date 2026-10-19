import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("JobPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    questionnaire_answers = relationship("QuestionnaireAnswer", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("ResumeDocument", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    contact_info = Column(JSON, default=dict)
    professional_summary = Column(Text, nullable=True)
    skills = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    raw_parsed_text = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    target_titles = Column(JSON, default=lambda: ["Software Engineer", "AI Engineer", "Data Engineer"])
    preferred_industries = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=lambda: ["Remote", "Noida", "Gurgaon", "Delhi", "Bengaluru", "Pune", "Hyderabad"])
    remote_preference = Column(String(50), default="hybrid_or_remote")
    min_salary = Column(Integer, default=0)
    salary_currency = Column(String(10), default="INR")
    employment_types = Column(JSON, default=lambda: ["full-time"])
    
    preferred_companies = Column(JSON, default=list)
    excluded_companies = Column(JSON, default=list)
    
    job_posting_age_days = Column(Integer, default=7)
    min_match_score = Column(Integer, default=75)
    max_applications_per_hour = Column(Integer, default=5)
    max_applications_per_day = Column(Integer, default=25)

    automation_mode = Column(String(50), default="automatic")
    work_authorization = Column(String(100), default="Authorized to work in India (Citizen)")
    requires_sponsorship = Column(Boolean, default=False)
    notice_period_days = Column(Integer, default=15)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    question_key = Column(String(100), index=True, nullable=False)
    question_text = Column(String(500), nullable=False)
    answer_value = Column(Text, nullable=False)
    status = Column(String(50), default="verified")
    category = Column(String(50), default="general")
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="questionnaire_answers")
