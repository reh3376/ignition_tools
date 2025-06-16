import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

@pytest.fixture
def sample_machine_data():
    """Fixture providing sample machine data for testing."""
    return {
        "machine_id": "TEST_MACHINE_001",
        "status": "running",
        "metrics": {
            "temperature": 75.5,
            "pressure": 2.1,
            "speed": 1000
        }
    }

def test_get_machine_status(sample_machine_data):
    """Test getting machine status."""
    # First create a machine status
    client.post(f"/machines/{sample_machine_data['machine_id']}/status", json=sample_machine_data)

    # Then get the status
    response = client.get(f"/machines/{sample_machine_data['machine_id']}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["machine_id"] == sample_machine_data["machine_id"]
    assert data["status"] == sample_machine_data["status"]
    assert "last_updated" in data
    assert data["metrics"] == sample_machine_data["metrics"]

def test_get_nonexistent_machine():
    """Test getting status for a nonexistent machine."""
    response = client.get("/machines/NONEXISTENT/status")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "message" in data

def test_update_machine_status(sample_machine_data):
    """Test updating machine status."""
    response = client.post(
        f"/machines/{sample_machine_data['machine_id']}/status",
        json=sample_machine_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["machine_id"] == sample_machine_data["machine_id"]
    assert data["status"] == sample_machine_data["status"]
    assert "last_updated" in data
    assert data["metrics"] == sample_machine_data["metrics"]

def test_update_machine_status_invalid_data():
    """Test updating machine status with invalid data."""
    invalid_data = {
        "status": "invalid_status",
        "metrics": {
            "temperature": "not_a_number"
        }
    }
    response = client.post("/machines/TEST_MACHINE_001/status", json=invalid_data)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "message" in data

def test_list_machines(sample_machine_data):
    """Test listing machines."""
    # Create a machine first
    client.post(f"/machines/{sample_machine_data['machine_id']}/status", json=sample_machine_data)

    # Then list machines
    response = client.get("/machines")
    assert response.status_code == 200
    data = response.json()
    assert "machines" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert len(data["machines"]) > 0
    assert data["machines"][0]["machine_id"] == sample_machine_data["machine_id"]

def test_list_machines_with_filters(sample_machine_data):
    """Test listing machines with filters."""
    # Create a machine first
    client.post(f"/machines/{sample_machine_data['machine_id']}/status", json=sample_machine_data)

    # List machines with status filter
    response = client.get("/machines?status=running")
    assert response.status_code == 200
    data = response.json()
    assert all(machine["status"] == "running" for machine in data["machines"])

def test_get_machine_metrics(sample_machine_data):
    """Test getting machine metrics."""
    # Create a machine first
    client.post(f"/machines/{sample_machine_data['machine_id']}/status", json=sample_machine_data)

    # Get metrics
    response = client.get(f"/machines/{sample_machine_data['machine_id']}/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "machine_id" in data
    assert "metrics" in data
    assert len(data["metrics"]) > 0
    assert "timestamp" in data["metrics"][0]
    assert "temperature" in data["metrics"][0]
    assert "pressure" in data["metrics"][0]
    assert "speed" in data["metrics"][0]
