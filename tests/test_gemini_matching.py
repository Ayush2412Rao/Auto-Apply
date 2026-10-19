import pytest
from backend.app.ai.matcher import job_matcher

def test_hard_filters_exclusion():
    job = {
        "company_name": "BadCompany Inc",
        "job_title": "AI Engineer",
        "location": "Noida",
        "is_remote": False
    }
    preferences = {
        "excluded_companies": ["BadCompany"],
        "preferred_locations": ["Noida", "Remote"]
    }
    res = job_matcher.evaluate_hard_filters(job, preferences)
    assert res["eligible"] is False
    assert "excluded list" in res["reason"]

def test_hard_filters_location_pass():
    job = {
        "company_name": "GoodCompany Inc",
        "job_title": "AI Engineer",
        "location": "Noida, India",
        "is_remote": False
    }
    preferences = {
        "excluded_companies": [],
        "preferred_locations": ["Noida", "Remote"]
    }
    res = job_matcher.evaluate_hard_filters(job, preferences)
    assert res["eligible"] is True

def test_gemini_semantic_matching():
    job = {
        "company_name": "Elite AI Systems",
        "job_title": "AI & LangGraph Engineer",
        "location": "Noida, India",
        "description": "Looking for an engineer proficient in Python, LangGraph, and RAG architectures."
    }
    profile = {
        "name": "Ayush Rao",
        "headline": "Software Engineer – AI/ML & Data Engineering",
        "summary": "Hands-on experience in LangChain, LangGraph, Python, and SQL.",
        "skills": ["Python", "LangGraph", "FastAPI"]
    }
    preferences = {
        "min_match_score": 75,
        "preferred_locations": ["Noida", "Remote"],
        "excluded_companies": []
    }
    match = job_matcher.evaluate_job(job, profile, preferences, user_id=1)
    assert "match_score" in match
    assert match["match_score"] >= 70
    assert match["recommendation"] in ["proceed", "review"]
