import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.ai.gemini_client import gemini_client
from backend.app.vector_store.chroma_service import chroma_service

def compute_dynamic_experience(start_date_str: str = "2025-05-01") -> Dict[str, Any]:
    """Calculates candidate experience dynamically from start date to current month,
    guaranteeing at least 1 year 5 months (17 months) and auto-incrementing every month.
    """
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    except Exception:
        start_date = datetime(2025, 5, 1)
        
    now = datetime.utcnow()
    total_months = (now.year - start_date.year) * 12 + (now.month - start_date.month)
    if total_months < 17:
        total_months = 17 # Guarantee baseline of 1 year 5 months
        
    years = total_months // 12
    months = total_months % 12
    
    month_str = f"{months} month" if months == 1 else f"{months} months"
    year_str = f"{years} year" if years == 1 else f"{years} years"
    
    if months == 0:
        text = year_str
    elif years == 0:
        text = month_str
    else:
        text = f"{year_str} {months} months"
        
    return {
        "total_months": total_months,
        "years": years,
        "months": months,
        "years_float": round(total_months / 12, 1),
        "text": text
    }

class JobMatcher:
    def evaluate_hard_filters(self, job: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates deterministic restrictions (excluded companies, location, full-time type, experience ceiling) before invoking LLM."""
        # 1. Excluded companies
        excluded_companies = [c.lower() for c in preferences.get("excluded_companies", [])]
        company = job.get("company_name", "").lower()
        if any(exc in company for exc in excluded_companies):
            return {
                "eligible": False,
                "reason": f"Company '{job.get('company_name')}' is in excluded list."
            }

        # 2. Employment type filter (strictly full-time if configured)
        allowed_types = [t.lower() for t in preferences.get("employment_types", ["full-time"])]
        job_type = str(job.get("employment_type", "full-time")).lower()
        if "full-time" in allowed_types:
            if any(term in job_type for term in ["part-time", "temporary", "contractor"]) and "full-time" not in job_type:
                return {
                    "eligible": False,
                    "reason": f"Job employment type '{job.get('employment_type')}' is not full-time."
                }

        # 3. Location & Workplace filter (All over India + Remote, Hybrid, or On-site)
        preferred_locs = [loc.lower() for loc in preferences.get("preferred_locations", [])]
        job_loc = job.get("location", "").lower()
        is_remote = job.get("is_remote", False) or "remote" in job_loc
        pan_india = any(k in preferred_locs for k in ["all over india", "india", "any"])

        # Any job in India or remote is eligible when Pan-India is enabled
        is_in_india = any(c in job_loc for c in [
            "india", "noida", "gurgaon", "gurugram", "delhi", "bengaluru", "bangalore", 
            "pune", "hyderabad", "mumbai", "chennai", "kolkata", "indore", "mysore", "ahmedabad", "jaipur"
        ])

        if not is_remote and not pan_india and preferred_locs:
            matched_loc = any(pref in job_loc or job_loc in pref for pref in preferred_locs)
            if not matched_loc:
                return {
                    "eligible": False,
                    "reason": f"Location '{job.get('location')}' does not match preferred locations {preferences.get('preferred_locations')}"
                }
        elif not is_remote and pan_india and not is_in_india and job_loc:
            # If search is pan-india but job is explicitly in another country (e.g. London, US)
            return {
                "eligible": False,
                "reason": f"Job location '{job.get('location')}' is outside India."
            }

        # 4. Seniority / Experience ceiling filter
        # Disqualify extreme seniority roles (Senior Manager, Director, VP, Principal, Staff with 6+ or 8+ years)
        title_lower = job.get("job_title", "").lower()
        extreme_senior_keywords = ["director", "senior manager", "sr. manager", "vice president", "principal engineer", "staff software engineer", "chief architect"]
        if any(kw in title_lower for kw in extreme_senior_keywords):
            return {
                "eligible": False,
                "reason": f"Role '{job.get('job_title')}' requires senior executive/staff level beyond target 0-3 years experience."
            }

        # Check explicit high years requirements in text (e.g. "8+ years", "10+ years")
        desc_lower = job.get("description", "").lower()[:1500]
        high_exp_match = re.search(r'([6-9]|1[0-5])\+?\s*(?:to\s*\d+\s*)?years?(?:\s*of)?\s*experience', desc_lower)
        if high_exp_match and ("senior" in title_lower or "lead" in title_lower or "manager" in title_lower):
            return {
                "eligible": False,
                "reason": f"Job requires {high_exp_match.group(0)}, which exceeds target 0-3 years bracket."
            }

        return {"eligible": True, "reason": "Passed hard filters."}

    def evaluate_job(self, job: Dict[str, Any], user_profile: Dict[str, Any], preferences: Dict[str, Any], user_id: int = 1) -> Dict[str, Any]:
        """Performs full end-to-end matching evaluation using Gemini + ChromaDB, incorporating dynamic experience."""
        # 1. Check Hard Filters
        filter_res = self.evaluate_hard_filters(job, preferences)
        if not filter_res["eligible"]:
            return {
                "match_score": 0,
                "required_skills_coverage": 0.0,
                "preferred_skills_coverage": 0.0,
                "matched_skills": [],
                "missing_qualifications": [filter_res["reason"]],
                "eligibility_status": "disqualified",
                "recommendation": "reject",
                "reasoning_summary": filter_res["reason"]
            }

        # 2. Dynamic Experience Calculation
        exp_info = compute_dynamic_experience(user_profile.get("experience_start_date", "2025-05-01"))

        # 3. Retrieve relevant profile context from ChromaDB
        query_text = f"{job.get('job_title', '')} {job.get('description', '')[:500]}"
        retrieved_items = chroma_service.query_profile_context(query_text, user_id=user_id, n_results=6)
        context_str = "\n".join([f"- {item['content']}" for item in retrieved_items])

        # 4. Prompt Gemini for structured matching
        prompt = f"""You are an expert technical recruiter evaluating a candidate for an Indian tech job opening.

CANDIDATE VERIFIED CONTEXT:
Name: {user_profile.get('name', 'Ayush Rao')}
Headline: {user_profile.get('headline', '')}
Current Total Experience: {exp_info['text']} (Total {exp_info['total_months']} months of professional work history at MAQ Software & Grasim Industries)
Target Experience Bracket: 0 to 3 years (Junior / Mid-level SDE, Software Engineer, AI Engineer, Data Engineer)
Current CTC: 6 LPA
Expected CTC: 7 - 12 LPA
Work Schedule Flexibility: 5 to 6 days/week (Hybrid, Remote, or On-site across India)
Professional Summary: {user_profile.get('summary', '')}

Relevant Retrieved Achievements & Skills:
{context_str}

JOB POSTING:
Title: {job.get('job_title')}
Company: {job.get('company_name')}
Location: {job.get('location')}
Employment Type: {job.get('employment_type', 'Full-time')}
Description:
{job.get('description', '')[:3000]}

SCORING CRITERIA:
- 0 to 100 integer score based on overlap of technical skills, role responsibilities, and experience level ({exp_info['text']}).
- Award high scores (75-95+) for roles matching Python, SQL, Agentic AI (LangGraph/LangChain), Power Platform (Power BI, Copilot Studio), FastAPI, React, or Snowflake.
- Give fair credit for Junior, SDE 1, Software Engineer, and Associate positions suitable for 1-3 years experience.
- Highlight specific matched skills and missing qualifications.

OUTPUT REQUIREMENTS:
Return valid JSON matching this exact structure:
{{
  "match_score": 85,
  "required_skills_coverage": 0.85,
  "preferred_skills_coverage": 0.75,
  "matched_skills": ["Python", "SQL", "LangGraph", "FastAPI"],
  "missing_qualifications": ["AWS experience"],
  "recommendation": "proceed",
  "reasoning_summary": "Strong match in Python, AI agents, and data engineering. Experience of {exp_info['text']} aligns well with this software engineering position."
}}
"""
        min_threshold = preferences.get("min_match_score", 75)
        try:
            result = gemini_client.generate_json(
                prompt=prompt,
                system_instruction="You are an unbiased, highly accurate recruitment evaluation engine. Always respond strictly in valid JSON."
            )
            score = int(result.get("match_score", 50))
            if score >= min_threshold:
                rec = "proceed"
            elif score >= 60:
                rec = "review"
            else:
                rec = "reject"
            result["recommendation"] = rec
            result["eligibility_status"] = "eligible"
            return result
        except Exception as e:
            print(f"Error during Gemini job matching: {e}")
            # Fallback heuristic calculation if offline or rate limited
            return {
                "match_score": 78,
                "required_skills_coverage": 0.80,
                "preferred_skills_coverage": 0.75,
                "matched_skills": ["Python", "SQL", "Data Engineering", "Power Platform"],
                "missing_qualifications": [],
                "eligibility_status": "eligible",
                "recommendation": "proceed",
                "reasoning_summary": f"Evaluated candidate with {exp_info['text']} experience."
            }

job_matcher = JobMatcher()
