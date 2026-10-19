import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.models.job import DiscoveredJob
from backend.app.models.application import JobApplication

class JobDeduplicator:
    @staticmethod
    def filter_duplicates(jobs: List[Dict[str, Any]], session: Session) -> Tuple[List[Dict[str, Any]], int]:
        """Filters out jobs that already exist in the database or have already been applied to."""
        if not jobs:
            return [], 0

        canonical_urls = [j["canonical_url"] for j in jobs]
        
        # Query existing canonical URLs in DB
        existing_jobs = session.query(DiscoveredJob.canonical_url).filter(
            DiscoveredJob.canonical_url.in_(canonical_urls)
        ).all()
        existing_url_set = {row[0] for row in existing_jobs}

        # Query existing applied URLs
        existing_apps = session.query(DiscoveredJob.canonical_url).join(
            JobApplication, JobApplication.job_id == DiscoveredJob.id
        ).filter(
            DiscoveredJob.canonical_url.in_(canonical_urls)
        ).all()
        applied_url_set = {row[0] for row in existing_apps}

        unique_jobs = []
        duplicate_count = 0

        seen_in_batch = set()
        for job in jobs:
            url = job["canonical_url"]
            if url in existing_url_set or url in applied_url_set or url in seen_in_batch:
                duplicate_count += 1
                continue
            seen_in_batch.add(url)
            unique_jobs.append(job)

        return unique_jobs, duplicate_count

job_deduplicator = JobDeduplicator()
