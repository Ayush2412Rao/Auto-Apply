import re
import hashlib
from typing import Dict, Any, Optional, List
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
        """Normalizes diverse scraper outputs (Naukri, Google Jobs, LinkedIn, Indeed) into a standardized schema."""
        title = raw_job.get("title") or raw_job.get("job_title") or raw_job.get("positionName") or "Software Engineer"
        
        # Company name handling (supports string or nested dict from Naukri)
        raw_company = raw_job.get("company")
        if isinstance(raw_company, dict):
            company = raw_company.get("name") or "Unknown"
        else:
            company = raw_job.get("company_name") or raw_company or raw_job.get("companyName") or "Unknown"

        # Location handling (supports string or nested list from Naukri)
        raw_locations = raw_job.get("locations")
        if isinstance(raw_locations, list) and raw_locations:
            labels = [l.get("label") for l in raw_locations if isinstance(l, dict) and l.get("label")]
            location = ", ".join(labels) if labels else "India"
        else:
            location = raw_job.get("location") or raw_job.get("formattedLocation") or raw_job.get("place") or "India"

        # Description handling (supports string or nested dict with HTML from Naukri)
        raw_desc = raw_job.get("description")
        if isinstance(raw_desc, dict):
            desc_text = raw_desc.get("full") or raw_desc.get("short") or ""
        else:
            desc_text = raw_desc or raw_job.get("job_description") or raw_job.get("text") or ""
        description = cls.clean_text(desc_text)
        
        # In Google Jobs scraper, job_highlights has structured Qualifications / Responsibilities
        highlights = raw_job.get("job_highlights") or []
        if isinstance(highlights, list) and highlights:
            highlight_lines: List[str] = []
            for h in highlights:
                h_title = h.get("title", "")
                h_items = h.get("items", [])
                if h_title and h_items:
                    highlight_lines.append(f"\n{h_title}:")
                    for item in h_items:
                        highlight_lines.append(f"- {item}")
            if highlight_lines:
                description = description + "\n" + "\n".join(highlight_lines)

        # In Naukri scraper, skills has preferred and other arrays
        skills_obj = raw_job.get("skills")
        if isinstance(skills_obj, dict):
            pref = skills_obj.get("preferred") or []
            oth = skills_obj.get("other") or []
            skill_lines = []
            if pref:
                skill_lines.append(f"Key Technical Skills: {', '.join(pref)}")
            if oth:
                skill_lines.append(f"Additional Skills: {', '.join(oth)}")
            if skill_lines:
                description = description + "\n\n" + "\n".join(skill_lines)

        # URL extraction (Naukri has 'url' directly, Google Jobs has apply_options)
        url = raw_job.get("url") or raw_job.get("link") or raw_job.get("job_url") or raw_job.get("applyUrl") or ""
        apply_options = raw_job.get("apply_options") or []
        if not url and isinstance(apply_options, list) and apply_options:
            best_link = None
            for opt in apply_options:
                opt_title = (opt.get("title") or "").lower()
                opt_link = opt.get("link") or ""
                if not opt_link:
                    continue
                if any(k in opt_title for k in ["company", "direct", "greenhouse", "lever", "workday", "careers"]):
                    best_link = opt_link
                    break
            if not best_link:
                best_link = apply_options[0].get("link")
            if best_link:
                url = best_link

        if not url:
            url = raw_job.get("share_link") or ""

        # Determine posting source platform
        via = raw_job.get("via") or ""
        if "naukri" in url.lower() or "naukri" in source.lower():
            source_label = "naukri"
        elif via:
            source_label = f"google_jobs ({via})"
        else:
            source_label = source

        canonical_url = cls.generate_canonical_url(source_label, url, company, title)
        
        # Remote / WFH detection (Naukri wfhType: 2 = Remote, 3 = Hybrid, 0 = Office)
        wfh_type = str(raw_job.get("wfhType", ""))
        is_remote = bool(
            wfh_type == "2" or
            "remote" in location.lower() or 
            raw_job.get("isRemote", False) or 
            raw_job.get("remote", False) or
            "work from home" in description[:500].lower()
        )

        detected_ext = raw_job.get("detected_extensions") or {}
        schedule = detected_ext.get("schedule_type") if isinstance(detected_ext, dict) else None
        employment_type = str(schedule or raw_job.get("employmentType") or raw_job.get("jobType") or "full-time").lower()

        # Salary extraction (handles dict from Naukri or string)
        raw_sal = raw_job.get("salary")
        if isinstance(raw_sal, dict):
            salary_raw = raw_sal.get("label") or f"{raw_sal.get('minimum', '')} - {raw_sal.get('maximum', '')} {raw_sal.get('currency', 'INR')}"
        else:
            salary_raw = str(raw_sal or raw_job.get("salaryRange") or "")

        return {
            "source": source_label,
            "job_title": title.strip(),
            "company_name": company.strip(),
            "location": location.strip(),
            "is_remote": is_remote,
            "employment_type": employment_type,
            "description": description.strip(),
            "salary_raw": salary_raw if salary_raw else None,
            "canonical_url": canonical_url,
            "application_url": url or canonical_url,
            "raw_metadata": raw_job,
            "posting_date": datetime.utcnow()
        }

job_normalizer = JobNormalizer()
