import sys
import copy
import json
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.ai.gemini_client import gemini_client
from backend.app.ai.validator import resume_validator
from backend.app.vector_store.chroma_service import chroma_service

class ResumeTailor:
    def tailor_resume(self, job: Dict[str, Any], verified_profile: Dict[str, Any], user_id: int = 1) -> Dict[str, Any]:
        """Generates a truthful, job-tailored resume strictly grounded in the verified profile."""
        job_title = job.get("job_title", "Software Engineer")
        company = job.get("company_name", "Target Company")
        job_desc = job.get("description", "")[:2500]

        # Retrieve relevant profile items
        retrieved_items = chroma_service.query_profile_context(f"{job_title} {job_desc[:300]}", user_id=user_id, n_results=6)
        context_str = "\n".join([f"- {item['content']}" for item in retrieved_items])

        prompt = f"""You are an elite, ATS-optimization resume architect. 
Tailor the candidate's verified profile for this target job.

RULES FOR ZERO-HALLUCINATION / ABSOLUTE FACTUAL ACCURACY:
1. NEVER invent employers, job titles, or dates. The candidate worked at: MAQ Software (May 2025 - Present) and Grasim Industries (June 2024 - July 2024).
2. NEVER invent degrees, certifications, or colleges. The candidate attends Lovely Professional University (B.Tech CSE, 2022-2026).
3. Rephrase bullet points to emphasize impact and keywords that match the target job, but PRESERVE THE FACTUAL REALITY of what was actually built.
4. Craft an impactful 3-sentence professional summary directly addressing the target role '{job_title}' at '{company}'.

TARGET JOB:
Title: {job_title}
Company: {company}
Description:
{job_desc}

VERIFIED MASTER PROFILE DATA:
{json.dumps(verified_profile, indent=2)}

RELEVANT RETRIEVED HIGHLIGHTS:
{context_str}

OUTPUT FORMAT:
Return valid JSON representing the tailored resume structure:
{{
  "name": "{verified_profile.get('name', 'Ayush Rao')}",
  "headline": "{job_title}",
  "contact": {json.dumps(verified_profile.get('contact', {}))},
  "summary": "Tailored 3-sentence professional summary...",
  "experience": [
    {{
      "company": "MAQ Software",
      "role": "Software Engineer 1 – AI/ML, Data Engineering",
      "location": "Noida, India",
      "start_date": "May 2025",
      "end_date": "Present",
      "bullets": [
        "Tailored bullet point 1...",
        "Tailored bullet point 2...",
        "Tailored bullet point 3...",
        "Tailored bullet point 4..."
      ]
    }},
    {{
      "company": "Grasim Industries Limited (Aditya Birla Group)",
      "role": "IT Intern",
      "location": "Renukoot, India",
      "start_date": "June 2024",
      "end_date": "July 2024",
      "bullets": [
        "Tailored bullet point 1...",
        "Tailored bullet point 2..."
      ]
    }}
  ],
  "projects": [
    {{
      "title": "Executive Sponsorship Survey – Reporting Agent",
      "technologies": ["Copilot Studio", "Power Automate", "Power BI"],
      "dates": "April - June 2026",
      "bullets": [
        "Bullet 1...",
        "Bullet 2..."
      ]
    }},
    {{
      "title": "UrbanMart – Omnichannel Retail Intelligence Platform",
      "technologies": ["Snowflake", "SQL", "SnowSQL", "Cortex AI"],
      "dates": "August 2026",
      "bullets": [
        "Bullet 1...",
        "Bullet 2...",
        "Bullet 3..."
      ]
    }}
  ],
  "education": {json.dumps(verified_profile.get('education', []))},
  "skills": {json.dumps(verified_profile.get('skills', {}))},
  "certifications": {json.dumps(verified_profile.get('certifications', []))}
}}
"""
        tailored_data = None
        try:
            tailored_data = gemini_client.generate_json(
                prompt=prompt,
                system_instruction="You are a professional ATS resume tailor. Output strictly valid JSON."
            )
        except Exception as e:
            print(f"Gemini resume tailoring error: {e}. Falling back to master profile with custom summary.")
            tailored_data = copy.deepcopy(verified_profile)
            tailored_data["headline"] = job_title
            tailored_data["summary"] = f"Versatile Software Engineer with hands-on experience in AI/ML, multi-agent frameworks (LangGraph), SQL, and Snowflake, targeting the {job_title} position at {company}."

        # Validate tailored resume against ground truth
        validation_report = resume_validator.validate(tailored_data, verified_profile)
        
        # If any validation errors exist, revert unverified items
        if not validation_report["is_valid"]:
            print(f"Validation warnings/errors: {validation_report['errors']}")
            tailored_data["experience"] = verified_profile.get("experience", [])
            tailored_data["education"] = verified_profile.get("education", [])
            tailored_data["contact"] = verified_profile.get("contact", {})
            validation_report = resume_validator.validate(tailored_data, verified_profile)

        # Build diff summary
        diff_summary = {
            "target_role": job_title,
            "target_company": company,
            "summary_tailored": True,
            "validation_passed": validation_report["is_valid"]
        }

        return {
            "tailored_content": tailored_data,
            "validation_report": validation_report,
            "diff_summary": diff_summary
        }

resume_tailor = ResumeTailor()
