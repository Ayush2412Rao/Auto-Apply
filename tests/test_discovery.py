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
