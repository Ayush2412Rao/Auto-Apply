import email
from email.header import decode_header
import imaplib
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db.session import SyncSessionLocal
from backend.app.models.application import JobApplication
from backend.app.models.job import DiscoveredJob

logger = logging.getLogger(__name__)

class RecruiterEmailScanner:
    """Connects to candidate email via IMAP to scan recruiter notifications,
    interviews, test links, and status changes to automatically synchronize the Kanban board.
    """

    def __init__(self):
        self.host = settings.IMAP_HOST or "imap.gmail.com"
        self.port = settings.IMAP_PORT or 993
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASS

    def is_configured(self) -> bool:
        return bool(self.user and self.password and self.user.strip() and self.password.strip())

    def _clean_header(self, raw_header: Optional[str]) -> str:
        if not raw_header:
            return ""
        decoded_parts = decode_header(raw_header)
        text_parts = []
        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                try:
                    text_parts.append(content.decode(encoding or "utf-8", errors="ignore"))
                except Exception:
                    text_parts.append(content.decode("utf-8", errors="ignore"))
            else:
                text_parts.append(str(content))
        return " ".join(text_parts).strip()

    def _extract_body_text(self, msg) -> str:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                    except Exception:
                        pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
            except Exception:
                pass
        return re.sub(r"\s+", " ", body).strip()

    def _classify_email(self, subject: str, body: str) -> Optional[str]:
        text = f"{subject} {body}".lower()

        # 1. Offer
        if any(p in text for p in ["offer letter", "pleased to offer", "congratulations on the offer", "job offer"]):
            return "offer"

        # 2. Interview Invitation
        if any(p in text for p in [
            "invitation to interview", "schedule an interview", "schedule a call", 
            "phone screen", "meet the team", "calendly.com", "zoom.us", 
            "teams.microsoft", "google meet", "round 1", "technical round"
        ]):
            return "interview_scheduled"

        # 3. Assessment / Coding Challenge
        if any(p in text for p in [
            "coding test", "hackerrank", "codility", "technical assessment", 
            "online test link", "take-home challenge", "assessment link", "test invitation"
        ]):
            return "assessment_received"

        # 4. Rejection
        if any(p in text for p in [
            "unfortunately", "not moving forward", "pursue other candidates", 
            "regret to inform", "decided not to proceed", "other applicants whose qualifications"
        ]):
            return "rejected"

        # 5. Under Review / Confirmation
        if any(p in text for p in [
            "thank you for applying", "application received", "we received your application", 
            "we have received your application", "application submitted", "reviewing your application",
            "candidate profile created"
        ]):
            return "under_review"

        return None

    def scan_inbox(self, max_emails: int = 40) -> Dict[str, Any]:
        """Connects via IMAP, inspects recent emails for recruiter updates,
        matches with applications in database, and transitions Kanban statuses.
        """
        if not self.is_configured():
            return {
                "status": "unconfigured",
                "message": "Email scanner is not configured. Please set SMTP_USER and SMTP_PASS in your .env file to enable automatic inbox sync.",
                "scanned_count": 0,
                "updates_applied": []
            }

        mail = None
        try:
            logger.info(f"[EmailScanner] Connecting to {self.host}:{self.port}...")
            mail = imaplib.IMAP4_SSL(self.host, self.port)
            mail.login(self.user, self.password)
            mail.select("INBOX", readonly=True)

            # Search emails within the last 30 days
            since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE "{since_date}")')
            if status != "OK" or not messages[0]:
                return {
                    "status": "success",
                    "message": "Inbox scanned successfully. No new recruitment emails found in the last 30 days.",
                    "scanned_count": 0,
                    "updates_applied": []
                }

            email_ids = messages[0].split()
            # Inspect the most recent max_emails
            recent_ids = email_ids[-max_emails:]
            recent_ids.reverse()

            updates = []
            db: Session = SyncSessionLocal()

            try:
                # Load current applications
                applications = db.query(JobApplication).all()
                app_lookup = []
                for app in applications:
                    job = db.query(DiscoveredJob).filter(DiscoveredJob.id == app.job_id).first()
                    if job and job.company_name:
                        app_lookup.append({
                            "app": app,
                            "job": job,
                            "company_norm": job.company_name.lower().strip()
                        })

                scanned_count = 0
                for eid in recent_ids:
                    scanned_count += 1
                    res, msg_data = mail.fetch(eid, "(RFC822)")
                    if res != "OK" or not msg_data:
                        continue

                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    subject = self._clean_header(msg.get("Subject"))
                    from_header = self._clean_header(msg.get("From"))
                    date_header = msg.get("Date") or datetime.utcnow().isoformat()
                    body_snippet = self._extract_body_text(msg)[:600]

                    detected_status = self._classify_email(subject, body_snippet)
                    if not detected_status:
                        continue

                    # Match with candidate applications
                    from_lower = from_header.lower()
                    subject_lower = subject.lower()
                    body_lower = body_snippet.lower()

                    for item in app_lookup:
                        company = item["company_norm"]
                        # Check company name appearance in sender or subject or body
                        if company in from_lower or company in subject_lower or company in body_lower:
                            app = item["app"]
                            job = item["job"]

                            # Status hierarchy: do not regress interview to under_review
                            hierarchy = {
                                "pending_approval": 0,
                                "applied": 1,
                                "under_review": 2,
                                "assessment_received": 3,
                                "interview_scheduled": 4,
                                "rejected": 5,
                                "offer": 6
                            }

                            current_rank = hierarchy.get(app.status, 1)
                            new_rank = hierarchy.get(detected_status, 1)

                            # Apply update if higher rank or explicit decision
                            if detected_status in ["rejected", "offer"] or new_rank >= current_rank:
                                old_status = app.status
                                app.status = detected_status
                                
                                evidence = app.submission_evidence or {}
                                email_history = evidence.get("recruiter_emails", [])
                                email_history.append({
                                    "sender": from_header[:120],
                                    "subject": subject[:150],
                                    "date": str(date_header),
                                    "status": detected_status,
                                    "snippet": body_snippet[:180]
                                })
                                evidence["recruiter_emails"] = email_history
                                evidence["last_email_sync"] = datetime.utcnow().isoformat()
                                app.submission_evidence = evidence
                                app.updated_at = datetime.utcnow()

                                updates.append({
                                    "application_id": app.id,
                                    "company": job.company_name,
                                    "job_title": job.job_title,
                                    "previous_status": old_status,
                                    "new_status": detected_status,
                                    "subject": subject[:80]
                                })

                db.commit()

            finally:
                db.close()

            return {
                "status": "success",
                "message": f"Scanned {scanned_count} recent emails. Found {len(updates)} application status updates.",
                "scanned_count": scanned_count,
                "updates_applied": updates
            }

        except Exception as e:
            logger.error(f"[EmailScanner] Error scanning emails: {e}")
            return {
                "status": "error",
                "message": f"Failed to sync recruiter emails: {str(e)}",
                "scanned_count": 0,
                "updates_applied": []
            }
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except Exception:
                    pass

email_scanner = RecruiterEmailScanner()
