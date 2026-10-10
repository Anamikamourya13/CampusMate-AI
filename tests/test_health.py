"""
Unit test for CampusMate AI Health Endpoint.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Verify that /api/health returns 200 OK and valid JSON metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["application"] == "CampusMate AI"
    assert "version" in data
    assert "ai_configured" in data
