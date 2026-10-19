import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.db.session import Base

class ResumeDocument(Base):
    __tablename__ = "resume_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    is_master = Column(Boolean, default=True)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    tailored_versions = relationship("ResumeVersion", back_populates="master_document", cascade="all, delete-orphan")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("discovered_jobs.id"), nullable=False)
    resume_document_id = Column(Integer, ForeignKey("resume_documents.id"), nullable=True)
    
    version_identifier = Column(String(100), unique=True, index=True, nullable=False)
    tailored_content = Column(JSON, nullable=False)
    pdf_path = Column(String(1000), nullable=True)
    docx_path = Column(String(1000), nullable=True)
    
    diff_summary = Column(JSON, default=dict)
    validation_status = Column(String(50), default="passed")
    validation_report = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    master_document = relationship("ResumeDocument", back_populates="tailored_versions")
    job = relationship("DiscoveredJob")
    application = relationship("JobApplication", back_populates="resume_version", uselist=False)


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("discovered_jobs.id"), nullable=False)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id"), nullable=True)
    
    status = Column(String(50), default="discovered", index=True, nullable=False)
    application_route = Column(String(50), default="portal")
    
    idempotency_key = Column(String(100), unique=True, index=True, nullable=False)
    submission_evidence = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    approved_by_user = Column(Boolean, default=False)
    approved_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    job = relationship("DiscoveredJob", back_populates="applications")
    resume_version = relationship("ResumeVersion", back_populates="application")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_uuid = Column(String(100), unique=True, index=True, nullable=False)
    trigger_type = Column(String(50), default="scheduled")
    status = Column(String(50), default="running", index=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    jobs_discovered = Column(Integer, default=0)
    jobs_matched = Column(Integer, default=0)
    resumes_tailored = Column(Integer, default=0)
    applications_submitted = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)
    
    events = relationship("AgentRunEvent", back_populates="run", cascade="all, delete-orphan")


class AgentRunEvent(Base):
    __tablename__ = "agent_run_events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    
    stage = Column(String(50), nullable=False)
    level = Column(String(20), default="info")
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("AgentRun", back_populates="events")


class NotificationRecord(Base):
    __tablename__ = "notification_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    notification_type = Column(String(50), nullable=False)
    channel = Column(String(20), default="email")
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)
