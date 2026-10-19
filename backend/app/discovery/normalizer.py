import re
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

class JobNormalizer:
    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        if not text:
            return ""
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', ' ', text)
        clean = re.sub(r'\s+', ' ', clean)
        clean = re.sub(r'\s+([.,;:!?])', r'\1', clean).strip()
        return clean

    @staticmethod
    def generate_canonical_url(source: str, url: str, company: str, title: str) -> str:
        if url and url.startswith("http"):
            # Strip tracking query parameters
            clean_url = url.split("?")[0].split("#")[0].rstrip("/")
            return clean_url
        # Fallback to unique hash
        hash_seed = f"{source}:{company.lower().strip()}:{title.lower().strip()}"
        unique_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:16]
        return f"urn:job:{source}:{unique_hash}"

    @classmethod
    def normalize(cls, raw_job: Dict[str, Any], source: str = "apify") -> Dict[str, Any]:
        """Normalizes diverse scraper outputs into a standardized schema."""
        title = raw_job.get("title") or raw_job.get("job_title") or raw_job.get("positionName") or "Software Engineer"
        company = raw_job.get("company") or raw_job.get("company_name") or raw_job.get("companyName") or "Unknown"
        location = raw_job.get("location") or raw_job.get("formattedLocation") or raw_job.get("place") or "Remote"
        
        description = cls.clean_text(
            raw_job.get("description") or raw_job.get("job_description") or raw_job.get("text") or ""
        )
        
        url = raw_job.get("url") or raw_job.get("link") or raw_job.get("job_url") or raw_job.get("applyUrl") or ""
        canonical_url = cls.generate_canonical_url(source, url, company, title)
        
        is_remote = bool(
            "remote" in location.lower() or 
            raw_job.get("isRemote", False) or 
            raw_job.get("remote", False) or
            "work from home" in description[:500].lower()
        )

        salary_raw = str(raw_job.get("salary") or raw_job.get("salaryRange") or "")
        employment_type = str(raw_job.get("employmentType") or raw_job.get("jobType") or "full-time").lower()

        return {
            "source": source,
            "job_title": title.strip(),
            "company_name": company.strip(),
            "location": location.strip(),
            "is_remote": is_remote,
            "employment_type": employment_type,
            "description": description,
            "salary_raw": salary_raw if salary_raw else None,
            "canonical_url": canonical_url,
            "application_url": url or canonical_url,
            "raw_metadata": raw_job,
            "posting_date": datetime.utcnow()
        }

job_normalizer = JobNormalizer()
