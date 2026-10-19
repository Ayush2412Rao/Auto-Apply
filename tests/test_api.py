import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "gemini_model" in data

def test_profile_endpoint():
    response = client.get("/api/profile/")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert "experience" in data

def test_preferences_endpoint():
    response = client.get("/api/preferences/")
    assert response.status_code == 200
    data = response.json()
    assert "target_titles" in data
    assert "min_match_score" in data

def test_jobs_endpoint():
    response = client.get("/api/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_agent_stats_endpoint():
    response = client.get("/api/agent/stats")
    assert response.status_code == 200
    data = response.json()
    assert "jobs_discovered" in data
    assert "scheduler_status" in data
