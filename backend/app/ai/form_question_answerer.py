import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from backend.app.config import settings
from backend.app.ai.gemini_client import gemini_client
from backend.app.ai.matcher import compute_dynamic_experience

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"

class FormQuestionAnswerer:
    """Answers job application form questions (both deterministic eligibility and
    open-ended behavioral/technical questions) with strict grounding in candidate profile.
    """

    def __init__(self):
        self.profile_answers = self._load_profile_answers()
        self.master_profile = self._load_master_profile()

    def _load_profile_answers(self) -> Dict[str, Any]:
        path = DATA_DIR / "questionnaire_answers.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading questionnaire_answers.json: {e}")
        return {}

    def _load_master_profile(self) -> Dict[str, Any]:
        path = DATA_DIR / "master_profile.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading master_profile.json: {e}")
        return {}

    def answer_question(
        self,
        question_text: str,
        job_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Answers an ATS form question deterministically or with Gemini RAG."""
        q_lower = question_text.lower().strip()
        job = job_context or {}
        company = job.get("company_name", "the company")
        title = job.get("job_title", "Software Engineer")

        # 1. Deterministic Fast-Paths
        # Notice Period
        if any(k in q_lower for k in ["notice period", "how soon can you start", "availability", "when can you join"]):
            if "day" in q_lower or "number" in q_lower:
                return "15"
            return self.profile_answers.get("notice_period", "Immediate / 15 days or less")

        # Current CTC / Compensation
        if any(k in q_lower for k in ["current ctc", "current salary", "present ctc", "current compensation"]):
            if "lpa" in q_lower or "numeric" in q_lower or "inr" in q_lower or "number" in q_lower:
                return "600000"
            return self.profile_answers.get("current_ctc", "6 LPA")

        # Expected CTC / Compensation
        if any(k in q_lower for k in ["expected ctc", "expected salary", "salary expectation", "compensation expectation"]):
            if "numeric" in q_lower or "number" in q_lower:
                return "1000000"
            return self.profile_answers.get("expected_ctc", "8 - 12 LPA")

        # Work Authorization / Citizenship
        if any(k in q_lower for k in ["authorized to work", "legally authorized", "right to work", "work permit", "citizen"]):
            return "Yes"

        # Visa Sponsorship
        if any(k in q_lower for k in ["sponsorship", "require visa", "require sponsorship", "need sponsorship"]):
            return "No"

        # Relocation / Travel
        if any(k in q_lower for k in ["willing to relocate", "relocation", "open to relocate"]):
            return "Yes"

        # Experience (Overall Years)
        if any(k in q_lower for k in ["total experience", "years of overall experience", "total years of"]):
            exp_data = compute_dynamic_experience()
            years = exp_data.get("years", 1)
            months = exp_data.get("months", 5)
            if "number" in q_lower or "digit" in q_lower:
                return f"{years}.{months}"
            return f"{years} year {months} months"

        # Experience with a specific skill (e.g. "How many years of experience with Python?")
        skills = self.profile_answers.get("primary_skills", [])
        for skill in skills:
            if skill.lower() in q_lower:
                if "how many years" in q_lower or "years of experience" in q_lower:
                    return "2"
                return f"Yes, 1-2 years of hands-on experience building production workflows with {skill}."

        # Demographic Standard Questions (EEO / Voluntary Disclosures)
        if "gender" in q_lower:
            return "Male"
        if "veteran" in q_lower:
            return "I am not a protected veteran"
        if "disability" in q_lower:
            return "No, I do not have a disability"

        # 2. Open-Ended Questions: Use Gemini RAG
        return self._generate_ai_answer(question_text, company, title)

    def _generate_ai_answer(self, question: str, company: str, title: str) -> str:
        """Generates a truthful, concise 2-3 sentence response using Gemini grounded in candidate profile."""
        system_instruction = (
            "You are an expert ATS application assistant for candidate Ayush Rao. "
            "Your task is to answer a job application question truthfully, concisely, and professionally. "
            "STRICT RULES:\n"
            "1. Answer must be 2 to 3 sentences maximum (under 75 words).\n"
            "2. Grounded strictly in candidate reality: Ayush is a Software Engineer 1 at MAQ Software working on AI/ML, Data Engineering, and Power Platform automation. Graduating B.Tech CSE from Lovely Professional University (2026).\n"
            "3. Key tools: Python, SQL, FastAPI, LangGraph, ChromaDB, Docker, Power BI, Copilot Studio, Snowflake.\n"
            "4. NEVER invent unverified achievements, metrics, or previous companies.\n"
            "5. Tone: Confident, articulate, humble, and directly addressing the prompt."
        )

        prompt = (
            f"Job Position: {title} at {company}\n"
            f"Application Question: {question}\n\n"
            f"Provide a natural, concise, first-person response suitable for pasting directly into the job application form:"
        )

        try:
            answer = gemini_client.generate_text(
                prompt=prompt,
                system_instruction=system_instruction
            )
            # Remove any wrapping quotes or markdown backticks
            cleaned = answer.strip().strip('"').strip("'")
            return cleaned
        except Exception as e:
            logger.warning(f"Gemini form answer generation failed: {e}. Using deterministic fallback.")
            # Deterministic fallback
            if "why" in question.lower() and ("company" in question.lower() or "join" in question.lower() or "role" in question.lower()):
                return (
                    f"I am excited by {company}'s focus on high-impact engineering and innovation. "
                    f"With my background in Python, FastAPI, and data-driven systems at MAQ Software, "
                    f"I am eager to contribute reliable code and scale solutions for the {title} team."
                )
            elif "project" in question.lower() or "problem" in question.lower():
                return (
                    "At MAQ Software, I developed an automated agentic workflow using LangChain and FastAPI "
                    "that streamlined enterprise reporting pipelines, reducing manual processing time while ensuring deterministic data validation."
                )
            else:
                return (
                    f"With hands-on experience in full-stack Python, SQL, and enterprise cloud tooling, "
                    f"I bring a disciplined engineering approach and look forward to contributing to the {title} role at {company}."
                )

form_question_answerer = FormQuestionAnswerer()
