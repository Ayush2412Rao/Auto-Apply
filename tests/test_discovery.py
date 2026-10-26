import pytest
from backend.app.discovery.normalizer import job_normalizer
from backend.app.discovery.deduplicator import job_deduplicator
from backend.app.db.session import SyncSessionLocal
from backend.app.models.job import DiscoveredJob

def test_normalization_schema():
    raw_job = {
        "title": " Senior AI Engineer ",
        "company": "Tech Corp",
        "location": "Noida, India",
        "description": "<p>We are looking for an <b>AI Engineer</b>.</p>",
        "url": "https://linkedin.com/jobs/view/123456?ref=tracking_param",
        "isRemote": False
    }
    norm = job_normalizer.normalize(raw_job, source="linkedin")
    assert norm["job_title"] == "Senior AI Engineer"
    assert norm["company_name"] == "Tech Corp"
    assert "We are looking for an AI Engineer." in norm["description"]
    assert norm["canonical_url"] == "https://linkedin.com/jobs/view/123456"
    assert norm["source"] == "linkedin"

def test_glassdoor_normalization():
    glassdoor_raw = {
        "job_id": "1010298094310",
        "job_title": "Engineer - Java Full Stack Developer",
        "company_name": "Cardinal Health, Inc.",
        "job_location": {
            "city": "bengaluru",
            "state": "Karnataka",
            "country": "India"
        },
        "job_description": "<p>We are seeking a <b>Java Full Stack Developer</b>.</p>",
        "job_salary": {
            "currency": "INR",
            "currency_symbol": "₹",
            "pay_period": "annual",
            "min": 400000,
            "max": 800000
        },
        "job_apply_url": "https://www.glassdoor.co.in/partner/jobListing.htm?jl=1010298094310",
        "job_type_labels": ["Full-time"]
    }
    norm = job_normalizer.normalize(glassdoor_raw, source="glassdoor")
    assert norm["job_title"] == "Engineer - Java Full Stack Developer"
    assert norm["company_name"] == "Cardinal Health, Inc."
    assert "Bengaluru, Karnataka, India" in norm["location"]
    assert "₹400000 - ₹800000 INR / annual" in norm["salary_raw"]
    assert norm["canonical_url"] == "https://www.glassdoor.co.in/partner/jobListing.htm"
    assert norm["source"] == "glassdoor"
    assert norm["employment_type"] == "full-time"

def test_deduplication():
    session = SyncSessionLocal()
    try:
        jobs = [
            {
                "canonical_url": "https://example.com/unique-job-1",
                "company_name": "Unique Co 1",
                "job_title": "Developer"
            },
            {
                "canonical_url": "https://example.com/unique-job-1",
                "company_name": "Unique Co 1",
                "job_title": "Developer"
            }
        ]
        unique, dups = job_deduplicator.filter_duplicates(jobs, session)
        assert len(unique) <= 1
        assert dups >= 1
    finally:
        session.close()

def test_scrapy_job_discovery():
    from backend.app.discovery.scrapy_client import scrapy_discovery
    jobs = scrapy_discovery.get_sample_live_jobs()
    assert len(jobs) >= 2
    for j in jobs:
        assert "job_title" in j
        assert "company_name" in j
        assert "canonical_url" in j
        assert j["canonical_url"].startswith("http") or j["canonical_url"].startswith("urn:job:")

