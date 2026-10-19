import pytest
from backend.app.ai.validator import resume_validator

@pytest.fixture
def sample_profile():
    return {
        "name": "Ayush Rao",
        "contact": {
            "email": "ayushrao786420@gmail.com",
            "phone": "+91-7667880422"
        },
        "experience": [
            {
                "company": "MAQ Software",
                "role": "Software Engineer 1 – AI/ML, Data Engineering"
            },
            {
                "company": "Grasim Industries Limited (Aditya Birla Group)",
                "role": "IT Intern"
            }
        ],
        "education": [
            {
                "institution": "Lovely Professional University",
                "degree": "Bachelor of Technology"
            }
        ],
        "projects": [
            {
                "title": "Executive Sponsorship Survey – Reporting Agent"
            },
            {
                "title": "UrbanMart – Omnichannel Retail Intelligence Platform"
            }
        ]
    }

def test_valid_tailored_resume_passes(sample_profile):
    valid_tailored = {
        "name": "Ayush Rao",
        "contact": {
            "email": "ayushrao786420@gmail.com",
            "phone": "+91-7667880422"
        },
        "experience": [
            {"company": "MAQ Software", "role": "Software Engineer 1"},
            {"company": "Grasim Industries Limited", "role": "IT Intern"}
        ],
        "education": [
            {"institution": "Lovely Professional University", "degree": "B.Tech"}
        ],
        "projects": [
            {"title": "UrbanMart – Omnichannel Retail Intelligence Platform"}
        ]
    }
    report = resume_validator.validate(valid_tailored, sample_profile)
    assert report["is_valid"] is True
    assert len(report["errors"]) == 0
    assert report["verified_elements"]["companies_verified"] == 2

def test_hallucinated_employer_fails(sample_profile):
    hallucinated = {
        "name": "Ayush Rao",
        "contact": {
            "email": "ayushrao786420@gmail.com",
            "phone": "+91-7667880422"
        },
        "experience": [
            {"company": "Google LLC", "role": "Senior Staff AI Architect"},
            {"company": "MAQ Software", "role": "Software Engineer 1"}
        ],
        "education": sample_profile["education"],
        "projects": sample_profile["projects"]
    }
    report = resume_validator.validate(hallucinated, sample_profile)
    assert report["is_valid"] is False
    assert any("Unverified employer detected: 'Google LLC'" in e for e in report["errors"])
