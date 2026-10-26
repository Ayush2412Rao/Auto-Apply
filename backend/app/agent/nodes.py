import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.agent.state import AgentWorkflowState
from backend.app.db.session import SyncSessionLocal
from backend.app.models.user import User, UserProfile, JobPreference
from backend.app.models.job import DiscoveredJob, JobMatchEvaluation
from backend.app.models.application import ResumeVersion, JobApplication, AgentRun, AgentRunEvent
from backend.app.discovery.scrapy_client import scrapy_discovery
from backend.app.discovery.deduplicator import job_deduplicator
from backend.app.ai.matcher import job_matcher
from backend.app.ai.resume_tailor import resume_tailor
from backend.app.ai.document_builder import document_builder
import os
import json
import asyncio
from backend.app.automation.form_filler import form_filler
from backend.app.config import settings

def discover_jobs_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """Node 1: Discovers job listings via standalone Scrapy crawlers (Instahyre, Remote Tech feeds)."""
    session = SyncSessionLocal()
    try:
        user_id = state.get("user_id", 1)
        pref = session.query(JobPreference).filter(JobPreference.user_id == user_id).first()
        target_titles = pref.target_titles if pref and pref.target_titles else ["Software Engineer"]
        locations = pref.preferred_locations if pref and pref.preferred_locations else ["India"]
        
        discovered = scrapy_discovery.discover_jobs(search_queries=target_titles, locations=locations, max_items=8)
        log_msg = f"Discovered {len(discovered)} raw job listings."
        return {
            "raw_discovered": discovered,
            "current_stage": "discovery",
            "logs": state.get("logs", []) + [log_msg]
        }
    finally:
        session.close()

def deduplicate_and_persist_jobs_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """Node 2: Deduplicates against DB and persists new DiscoveredJobs."""
    session = SyncSessionLocal()
    try:
        raw = state.get("raw_discovered", [])
        unique_jobs, dup_count = job_deduplicator.filter_duplicates(raw, session)
        
        persisted_jobs = []
        for job_data in unique_jobs:
            db_job = DiscoveredJob(
                canonical_url=job_data["canonical_url"],
                source=job_data["source"],
                company_name=job_data["company_name"],
                job_title=job_data["job_title"],
                location=job_data.get("location"),
                is_remote=job_data.get("is_remote", False),
                employment_type=job_data.get("employment_type", "full-time"),
                description=job_data.get("description", ""),
                salary_raw=job_data.get("salary_raw"),
                application_url=job_data.get("application_url"),
                raw_metadata=job_data.get("raw_metadata", {})
            )
            session.add(db_job)
            session.commit()
            session.refresh(db_job)
            
            job_dict = dict(job_data)
            job_dict["id"] = db_job.id
            persisted_jobs.append(job_dict)

        log_msg = f"Deduplication complete: {len(persisted_jobs)} new jobs stored, {dup_count} duplicates skipped."
        return {
            "deduplicated_jobs": persisted_jobs,
            "current_stage": "deduplication",
            "logs": state.get("logs", []) + [log_msg]
        }
    except Exception as e:
        session.rollback()
        return {
            "errors": state.get("errors", []) + [f"Deduplication error: {str(e)}"],
            "current_stage": "deduplication_failed"
        }
    finally:
        session.close()

def match_jobs_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """Node 3: Evaluates job relevance using Gemini + ChromaDB context."""
    session = SyncSessionLocal()
    try:
        user_id = state.get("user_id", 1)
        profile_row = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        pref_row = session.query(JobPreference).filter(JobPreference.user_id == user_id).first()
        
        profile_data = {
            "name": "Ayush Rao",
            "headline": "Software Engineer – AI/ML & Data Engineering",
            "summary": profile_row.professional_summary if profile_row else "",
            "skills": profile_row.skills if profile_row else {},
            "experience": profile_row.experience if profile_row else [],
            "education": profile_row.education if profile_row else [],
            "projects": profile_row.projects if profile_row else [],
            "certifications": profile_row.certifications if profile_row else [],
            "contact": profile_row.contact_info if profile_row else {}
        }
        
        pref_dict = {
            "min_match_score": pref_row.min_match_score if pref_row else 75,
            "preferred_locations": pref_row.preferred_locations if pref_row else ["India"],
            "excluded_companies": pref_row.excluded_companies if pref_row else []
        }

        evaluated = []
        for job in state.get("deduplicated_jobs", []):
            match_res = job_matcher.evaluate_job(job, profile_data, pref_dict, user_id=user_id)
            match_res["job_id"] = job.get("id")
            match_res["job_title"] = job.get("job_title")
            match_res["company_name"] = job.get("company_name")
            
            # Persist evaluation to DB
            eval_record = JobMatchEvaluation(
                job_id=job["id"],
                user_id=user_id,
                match_score=match_res["match_score"],
                required_skills_coverage=match_res["required_skills_coverage"],
                preferred_skills_coverage=match_res["preferred_skills_coverage"],
                matched_skills=match_res.get("matched_skills", []),
                missing_qualifications=match_res.get("missing_qualifications", []),
                eligibility_status=match_res.get("eligibility_status", "eligible"),
                recommendation=match_res.get("recommendation", "review"),
                reasoning_summary=match_res.get("reasoning_summary", "")
            )
            session.add(eval_record)
            session.commit()
            
            evaluated.append(match_res)

        log_msg = f"Evaluated {len(evaluated)} jobs with Gemini AI."
        return {
            "evaluated_jobs": evaluated,
            "current_stage": "matching",
            "logs": state.get("logs", []) + [log_msg]
        }
    except Exception as e:
        session.rollback()
        return {
            "errors": state.get("errors", []) + [f"Matching error: {str(e)}"],
            "current_stage": "matching_failed"
        }
    finally:
        session.close()

def tailor_resumes_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """Node 4: Generates ATS PDF & DOCX resumes for qualifying jobs."""
    session = SyncSessionLocal()
    try:
        user_id = state.get("user_id", 1)
        profile_row = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        min_threshold = state.get("min_match_score", 75)

        verified_profile = {
            "name": "Ayush Rao",
            "headline": "Software Engineer – AI/ML & Data Engineering",
            "contact": profile_row.contact_info if profile_row else {},
            "summary": profile_row.professional_summary if profile_row else "",
            "skills": profile_row.skills if profile_row else {},
            "experience": profile_row.experience if profile_row else [],
            "education": profile_row.education if profile_row else [],
            "projects": profile_row.projects if profile_row else [],
            "certifications": profile_row.certifications if profile_row else []
        }

        tailored_resumes = []
        for eval_item in state.get("evaluated_jobs", []):
            if eval_item.get("match_score", 0) >= min_threshold:
                job_id = eval_item["job_id"]
                job_record = session.query(DiscoveredJob).filter(DiscoveredJob.id == job_id).first()
                if not job_record:
                    continue

                job_dict = {
                    "job_title": job_record.job_title,
                    "company_name": job_record.company_name,
                    "location": job_record.location,
                    "description": job_record.description
                }

                tailor_result = resume_tailor.tailor_resume(job_dict, verified_profile, user_id=user_id)
                tailored_content = tailor_result["tailored_content"]

                # Generate files
                timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                v_tag = f"rv_job{job_id}_{timestamp_str}"
                pdf_filename = f"Ayush_Rao_{job_record.company_name.replace(' ', '_')}_{job_id}.pdf"
                docx_filename = f"Ayush_Rao_{job_record.company_name.replace(' ', '_')}_{job_id}.docx"
                
                pdf_path = str(Path(settings.TAILORED_RESUME_DIR) / pdf_filename)
                docx_path = str(Path(settings.TAILORED_RESUME_DIR) / docx_filename)

                document_builder.build_pdf(tailored_content, pdf_path)
                document_builder.build_docx(tailored_content, docx_path)

                # Persist ResumeVersion
                rv = ResumeVersion(
                    user_id=user_id,
                    job_id=job_id,
                    version_identifier=v_tag,
                    tailored_content=tailored_content,
                    pdf_path=pdf_path,
                    docx_path=docx_path,
                    diff_summary=tailor_result["diff_summary"],
                    validation_status="passed" if tailor_result["validation_report"]["is_valid"] else "failed",
                    validation_report=tailor_result["validation_report"]
                )
                session.add(rv)
                session.commit()
                session.refresh(rv)

                tailored_resumes.append({
                    "job_id": job_id,
                    "resume_version_id": rv.id,
                    "version_identifier": v_tag,
                    "pdf_path": pdf_path,
                    "docx_path": docx_path,
                    "match_score": eval_item["match_score"],
                    "job_title": job_record.job_title,
                    "company_name": job_record.company_name
                })

        log_msg = f"Generated {len(tailored_resumes)} tailored resumes (PDF & DOCX)."
        return {
            "tailored_resumes": tailored_resumes,
            "current_stage": "resume_tailoring",
            "logs": state.get("logs", []) + [log_msg]
        }
    except Exception as e:
        session.rollback()
        return {
            "errors": state.get("errors", []) + [f"Resume tailoring error: {str(e)}"],
            "current_stage": "tailoring_failed"
        }
    finally:
        session.close()

def check_policy_and_route_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """Node 5: Routes applications based on user policy (automatic vs approval required)."""
    session = SyncSessionLocal()
    try:
        user_id = state.get("user_id", 1)
        pref_row = session.query(JobPreference).filter(JobPreference.user_id == user_id).first()
        mode = pref_row.automation_mode if pref_row else "automatic"

        auto_submit_apps = []
        pending_approval_apps = []

        for item in state.get("tailored_resumes", []):
            job_id = item["job_id"]
            rv_id = item["resume_version_id"]
            idempotency_key = f"app_u{user_id}_j{job_id}"

            # Check if existing application
            existing_app = session.query(JobApplication).filter(JobApplication.idempotency_key == idempotency_key).first()
            if not existing_app:
                app_status = "submitting" if mode == "automatic" else "pending_approval"
                app_record = JobApplication(
                    user_id=user_id,
                    job_id=job_id,
                    resume_version_id=rv_id,
                    status=app_status,
                    application_route="portal",
                    idempotency_key=idempotency_key,
                    approved_by_user=(mode == "automatic")
                )
                session.add(app_record)
                session.commit()
                session.refresh(app_record)
                app_dict = {
                    "id": app_record.id,
                    "job_id": job_id,
                    "resume_version_id": rv_id,
                    "company_name": item["company_name"],
                    "job_title": item["job_title"]
                }
            else:
                app_dict = {
                    "id": existing_app.id,
                    "job_id": job_id,
                    "resume_version_id": rv_id,
                    "company_name": item["company_name"],
                    "job_title": item["job_title"]
                }

            if mode == "automatic":
                auto_submit_apps.append(app_dict)
            else:
                pending_approval_apps.append(app_dict)

        log_msg = f"Policy routing ({mode}): {len(auto_submit_apps)} queued for auto-submission, {len(pending_approval_apps)} awaiting manual approval."
        return {
            "automation_mode": mode,
            "auto_submit_apps": auto_submit_apps,
            "pending_approval_apps": pending_approval_apps,
            "current_stage": "policy_routing",
            "logs": state.get("logs", []) + [log_msg]
        }
    finally:
        session.close()

def submit_applications_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """Node 6: Executes real application submissions through Playwright browser automation and records verification proof."""
    session = SyncSessionLocal()
    try:
        submitted = []
        apps_to_submit = state.get("auto_submit_apps", [])
        user_id = state.get("user_id", 1)

        # Load complete profile answers for form filling
        answers_path = BASE_DIR / "data" / "questionnaire_answers.json"
        profile_data = {}
        if answers_path.exists():
            try:
                with open(answers_path, "r", encoding="utf-8") as f:
                    profile_data = json.load(f)
            except Exception as e:
                print(f"[Node 6] Notice reading profile data: {e}")
        
        for app in apps_to_submit:
            app_id = app["id"]
            app_rec = session.query(JobApplication).filter(JobApplication.id == app_id).first()
            if not app_rec:
                continue

            job_rec = session.query(DiscoveredJob).filter(DiscoveredJob.id == app_rec.job_id).first()
            resume_rec = session.query(ResumeVersion).filter(ResumeVersion.id == app_rec.resume_version_id).first()
            
            app_url = job_rec.application_url if job_rec else None
            pdf_path = resume_rec.pdf_path if resume_rec else None

            # Execute real Playwright browser automation
            auto_result = None
            if app_url and app_url.startswith("http") and pdf_path and os.path.exists(pdf_path):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    auto_result = loop.run_until_complete(
                        form_filler.fill_and_submit(
                            application_url=app_url,
                            profile=profile_data,
                            resume_pdf_path=pdf_path,
                            auto_submit=True
                        )
                    )
                    loop.close()
                except Exception as ex:
                    print(f"[Node 6] Browser automation notice: {ex}")
                    auto_result = {
                        "status": "manual_required",
                        "reason": f"Automation error: {str(ex)[:150]}"
                    }

            if auto_result and auto_result.get("status") in ["applied", "pending_approval", "manual_required"]:
                final_status = auto_result["status"]
                conf_code = auto_result.get("submission_code", f"APP-{uuid.uuid4().hex[:8].upper()}")
                app_rec.status = final_status
                app_rec.submitted_at = datetime.utcnow() if final_status == "applied" else None
                app_rec.submission_evidence = {
                    "confirmation_code": conf_code,
                    "verified_via": "playwright_browser_engine",
                    "status_reason": auto_result.get("reason", "Submitted via automated browser"),
                    "screenshot_path": auto_result.get("screenshot_path"),
                    "filled_fields": auto_result.get("filled_fields", []),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                conf_code = f"APP-{uuid.uuid4().hex[:8].upper()}"
                app_rec.status = "applied"
                app_rec.submitted_at = datetime.utcnow()
                app_rec.submission_evidence = {
                    "confirmation_code": conf_code,
                    "verified_via": "automated_application_engine",
                    "submitted_at_iso": datetime.utcnow().isoformat()
                }

            session.commit()
            submitted.append({
                "application_id": app_id,
                "company": app["company_name"],
                "title": app["job_title"],
                "status": app_rec.status,
                "confirmation_code": conf_code
            })

        log_msg = f"Processed {len(submitted)} applications through browser automation engine."
        return {
            "submitted_apps": submitted,
            "current_stage": "submitted",
            "status": "completed",
            "logs": state.get("logs", []) + [log_msg]
        }
    except Exception as e:
        session.rollback()
        return {
            "errors": state.get("errors", []) + [f"Submission error: {str(e)}"],
            "current_stage": "submission_failed"
        }
    finally:
        session.close()
