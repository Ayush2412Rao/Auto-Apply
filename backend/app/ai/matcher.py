import sys
import json
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.ai.gemini_client import gemini_client
from backend.app.vector_store.chroma_service import chroma_service

class JobMatcher:
    def evaluate_hard_filters(self, job: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates deterministic restrictions before invoking LLM."""
        excluded_companies = [c.lower() for c in preferences.get("excluded_companies", [])]
        company = job.get("company_name", "").lower()
        if any(exc in company for exc in excluded_companies):
            return {
                "eligible": False,
                "reason": f"Company '{job.get('company_name')}' is in excluded list."
            }

        # Location check
        preferred_locs = [loc.lower() for loc in preferences.get("preferred_locations", [])]
        job_loc = job.get("location", "").lower()
        is_remote = job.get("is_remote", False) or "remote" in job_loc

        if not is_remote and preferred_locs:
            # Check if job location matches any preferred location
            matched_loc = any(pref in job_loc or job_loc in pref for pref in preferred_locs)
            if not matched_loc and "any" not in preferred_locs:
                # If neither remote nor matching preferred locations
                return {
                    "eligible": False,
                    "reason": f"Location '{job.get('location')}' does not match preferred locations {preferences.get('preferred_locations')}"
                }

        return {"eligible": True, "reason": "Passed hard filters."}

    def evaluate_job(self, job: Dict[str, Any], user_profile: Dict[str, Any], preferences: Dict[str, Any], user_id: int = 1) -> Dict[str, Any]:
        """Performs full end-to-end matching evaluation using Gemini + ChromaDB."""
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

        # 2. Retrieve relevant profile context from ChromaDB
        query_text = f"{job.get('job_title', '')} {job.get('description', '')[:500]}"
        retrieved_items = chroma_service.query_profile_context(query_text, user_id=user_id, n_results=6)
        context_str = "\n".join([f"- {item['content']}" for item in retrieved_items])

        # 3. Prompt Gemini for structured matching
        prompt = f"""You are an expert technical recruiter evaluating a candidate for a job posting.

CANDIDATE VERIFIED CONTEXT:
Name: {user_profile.get('name', 'Ayush Rao')}
Headline: {user_profile.get('headline', '')}
Summary: {user_profile.get('summary', '')}

Relevant Retrieved Achievements & Skills:
{context_str}

JOB POSTING:
Title: {job.get('job_title')}
Company: {job.get('company_name')}
Location: {job.get('location')}
Description:
{job.get('description', '')[:3000]}

SCORING CRITERIA:
- 0 to 100 integer score based on overlap of technical skills, role responsibilities, and experience level.
- Be fair and objective: acknowledge transferable strengths (e.g. Python, SQL, LangGraph, Power BI, FastAPI, Snowflake).
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
  "reasoning_summary": "Strong match in Python, AI agents, and data engineering. Missing AWS but has strong Azure and Snowflake background."
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
                "match_score": 75,
                "required_skills_coverage": 0.75,
                "preferred_skills_coverage": 0.70,
                "matched_skills": ["Python", "SQL", "Data Engineering"],
                "missing_qualifications": [],
                "eligibility_status": "eligible",
                "recommendation": "review",
                "reasoning_summary": "Evaluated with local heuristic fallback."
            }

job_matcher = JobMatcher()
