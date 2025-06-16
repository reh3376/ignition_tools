import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_create_api_test(sample_test_data):
    """Test creating a new API test."""
    response = client.post("/api/tests", json=sample_test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["test_id"] == sample_test_data["test_id"]
    assert data["name"] == sample_test_data["name"]
    assert data["description"] == sample_test_data["description"]
    assert data["parameters"] == sample_test_data["parameters"]

def test_get_api_test(sample_test_data):
    """Test retrieving an API test."""
    # First create a test
    client.post("/api/tests", json=sample_test_data)

    # Then get it
    response = client.get(f"/api/tests/{sample_test_data['test_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["test_id"] == sample_test_data["test_id"]
    assert data["name"] == sample_test_data["name"]

def test_list_api_tests(sample_test_data):
    """Test listing API tests."""
    # Create a test first
    client.post("/api/tests", json=sample_test_data)

    # Then list tests
    response = client.get("/api/tests")
    assert response.status_code == 200
    data = response.json()
    assert "tests" in data
    assert "total" in data
    assert len(data["tests"]) > 0
    assert data["tests"][0]["test_id"] == sample_test_data["test_id"]

def test_run_api_test(sample_test_data, mock_mcp_service):
    """Test running an API test."""
    # Create a test first
    client.post("/api/tests", json=sample_test_data)
    # Use mock service for isolated testing
    assert mock_mcp_service is not None

    # Run the test
    response = client.post(f"/api/tests/{sample_test_data['test_id']}/run")
    assert response.status_code == 200
    data = response.json()
    assert "test_id" in data
    assert "status" in data
    assert "start_time" in data
    assert "end_time" in data
    assert "results" in data

def test_get_test_results(sample_test_data):
    """Test getting test results."""
    # Create and run a test first
    client.post("/api/tests", json=sample_test_data)
    client.post(f"/api/tests/{sample_test_data['test_id']}/run")

    # Get results
    response = client.get(f"/api/tests/{sample_test_data['test_id']}/results")
    assert response.status_code == 200
    data = response.json()
    assert "test_id" in data
    assert "results" in data
    assert "metrics" in data["results"]
    assert "summary" in data["results"]

def test_invalid_test_creation():
    """Test creating a test with invalid data."""
    invalid_data = {
        "test_id": "TEST_001",
        "name": "Invalid Test",
        "parameters": {
            "duration": "not_a_number"
        }
    }
    response = client.post("/api/tests", json=invalid_data)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "message" in data

def test_nonexistent_test():
    """Test accessing a nonexistent test."""
    response = client.get("/api/tests/NONEXISTENT")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "message" in data

@pytest.mark.performance
def test_performance_test_execution(sample_test_data):
    """Test executing a performance test."""
    # Create a test first
    client.post("/api/tests", json=sample_test_data)

    # Run performance test
    response = client.post(
        f"/api/tests/{sample_test_data['test_id']}/run",
        json={"type": "performance"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "test_id" in data
    assert "status" in data
    assert "performance_metrics" in data
    assert "response_times" in data["performance_metrics"]
    assert "throughput" in data["performance_metrics"]
