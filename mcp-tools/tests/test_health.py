import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"

def test_health_check_content_type():
    """Test the health check endpoint content type."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"

def test_health_check_structure():
    """Test the health check response structure."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["timestamp"], str)

def test_health_check_mcp_connection():
    """Test the MCP service connection check."""
    response = client.get("/health/mcp")
    assert response.status_code == 200
    data = response.json()
    assert "mcp_status" in data
    assert "connection_time" in data
    assert isinstance(data["connection_time"], float) 