from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """Test the main endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Klymate-AI API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"
    assert "features" in data
    assert "docs" in data

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Klymate-AI"
    assert "version" in data
    assert "environment" in data
