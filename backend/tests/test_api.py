# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_analyze_invalid_credentials():
    """Test that invalid credentials are handled gracefully"""
    response = client.post("/api/analyze", json={
        "aws_access_key": "INVALID",
        "aws_secret_key": "INVALID",
        "aws_region": "us-east-1"
    })
    assert response.status_code == 400

def test_analyze_missing_fields():
    """Test missing required fields"""
    response = client.post("/api/analyze", json={
        "aws_access_key": "AKIA..."
    })
    assert response.status_code == 422  # Validation error