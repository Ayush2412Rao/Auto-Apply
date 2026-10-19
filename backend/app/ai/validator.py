import sys
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

class ResumeFactualValidator:
    """Enforces zero-hallucination factual consistency against candidate verified profile."""

    @staticmethod
    def validate(tailored_resume: Dict[str, Any], verified_profile: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        verified_elements: Dict[str, int] = {
            "companies_verified": 0,
            "degrees_verified": 0,
            "skills_verified": 0,
            "projects_verified": 0
        }

        # 1. Employer & Company Validation
        verified_companies = {
            exp.get("company", "").strip().lower()
            for exp in verified_profile.get("experience", [])
            if exp.get("company")
        }

        for exp in tailored_resume.get("experience", []):
            comp = exp.get("company", "").strip().lower()
            # Allow partial matching if company name has variations (e.g., 'MAQ Software' vs 'MAQ Software LLC')
            matched = any(comp in v_comp or v_comp in comp for v_comp in verified_companies)
            if not matched:
                errors.append(f"Unverified employer detected: '{exp.get('company')}'. Candidate never worked here.")
            else:
                verified_elements["companies_verified"] += 1

        # 2. Education & Degree Validation
        verified_institutions = {
            edu.get("institution", "").strip().lower()
            for edu in verified_profile.get("education", [])
            if edu.get("institution")
        }

        for edu in tailored_resume.get("education", []):
            inst = edu.get("institution", "").strip().lower()
            matched = any(inst in v_inst or v_inst in inst for v_inst in verified_institutions)
            if not matched:
                errors.append(f"Unverified institution detected: '{edu.get('institution')}'.")
            else:
                verified_elements["degrees_verified"] += 1

        # 3. Project Validation
        verified_projects = {
            proj.get("title", "").strip().lower()
            for proj in verified_profile.get("projects", [])
            if proj.get("title")
        }

        for proj in tailored_resume.get("projects", []):
            title = proj.get("title", "").strip().lower()
            matched = any(title in v_proj or v_proj in title for v_proj in verified_projects)
            if not matched:
                errors.append(f"Unverified project title detected: '{proj.get('title')}'.")
            else:
                verified_elements["projects_verified"] += 1

        # 4. Check that contact details were not altered
        verified_contact = verified_profile.get("contact", {})
        tailored_contact = tailored_resume.get("contact", {})
        if tailored_contact.get("email") and tailored_contact.get("email") != verified_contact.get("email"):
            errors.append(f"Email changed from verified email {verified_contact.get('email')}")
        if tailored_contact.get("phone") and tailored_contact.get("phone") != verified_contact.get("phone"):
            errors.append(f"Phone changed from verified phone {verified_contact.get('phone')}")

        is_valid = len(errors) == 0
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "verified_elements": verified_elements
        }

resume_validator = ResumeFactualValidator()
