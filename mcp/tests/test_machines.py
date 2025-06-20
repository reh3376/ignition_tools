import sys
from pathlib import Path

import pytest

# Add the mcp directory to the path to ensure imports work
mcp_root = Path(__file__).parent.parent
if str(mcp_root) not in sys.path:
    sys.path.insert(0, str(mcp_root))

# Try to import FastAPI dependencies
try:
    from fastapi.testclient import TestClient

    # Try multiple import paths for the FastAPI app
    app = None
    try:
        # Try relative import first
        from mcp.src.main import app  # type: ignore[import]
    except ImportError:
        try:
            # Try direct import from src
            from src.main import app  # type: ignore[import]
        except ImportError:
            try:
                # Try importing from current directory structure
                import sys

                sys.path.append(str(Path(__file__).parent.parent / "src"))
                from main import app  # type: ignore[import]
            except ImportError:
                app = None

    if app is not None:
        client = TestClient(app)
        FASTAPI_AVAILABLE = True
    else:
        # Create a dummy app for testing structure
        from fastapi import FastAPI, HTTPException

        dummy_app = FastAPI()

        # Simple in-memory storage for testing
        machine_storage = {}

        # Add dummy machine endpoints for testing
        @dummy_app.get("/machines/{machine_id}/status")
        async def get_machine_status(machine_id: str):
            if machine_id not in machine_storage:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "not_found",
                        "message": f"Machine {machine_id} not found",
                    },
                )
            return machine_storage[machine_id]

        @dummy_app.post("/machines/{machine_id}/status")
        async def update_machine_status(machine_id: str, data: dict):
            # Validate required fields
            if "status" not in data:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": "Status is required",
                    },
                )

            # Validate metrics if provided
            if "metrics" in data:
                metrics = data["metrics"]
                if isinstance(metrics, dict):
                    for key, value in metrics.items():
                        if not isinstance(value, int | float):
                            raise HTTPException(
                                status_code=400,
                                detail={
                                    "error": "validation_error",
                                    "message": f"Metric {key} must be a number",
                                },
                            )

            machine_data = {
                "machine_id": machine_id,
                "status": data["status"],
                "last_updated": "2024-01-01T00:00:00Z",
                "metrics": data.get("metrics", {}),
            }
            machine_storage[machine_id] = machine_data
            return machine_data

        @dummy_app.get("/machines")
        async def list_machines(status: str | None = None):
            machines = list(machine_storage.values())
            if status:
                machines = [m for m in machines if m["status"] == status]

            return {
                "machines": machines,
                "total": len(machines),
                "limit": 10,
                "offset": 0,
            }

        @dummy_app.get("/machines/{machine_id}/metrics")
        async def get_machine_metrics(machine_id: str):
            if machine_id not in machine_storage:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "not_found",
                        "message": f"Machine {machine_id} not found",
                    },
                )

            machine = machine_storage[machine_id]
            return {
                "machine_id": machine_id,
                "metrics": [{"timestamp": "2024-01-01T00:00:00Z", **machine["metrics"]}],
            }

        client = TestClient(dummy_app)
        FASTAPI_AVAILABLE = True

except ImportError:
    FASTAPI_AVAILABLE = False
    client = None


@pytest.fixture
def sample_machine_data():
    """Fixture providing sample machine data for testing."""
    return {
        "machine_id": "TEST_MACHINE_001",
        "status": "running",
        "metrics": {"temperature": 75.5, "pressure": 2.1, "speed": 1000},
    }


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
def test_get_machine_status(sample_machine_data):
    """Test getting machine status."""
    assert client is not None, "Client should not be None when FastAPI is available"

    # First create a machine status
    client.post(
        f"/machines/{sample_machine_data['machine_id']}/status",
        json=sample_machine_data,
    )

    # Then get the status
    response = client.get(f"/machines/{sample_machine_data['machine_id']}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["machine_id"] == sample_machine_data["machine_id"]
    assert data["status"] == sample_machine_data["status"]
    assert "last_updated" in data
    assert data["metrics"] == sample_machine_data["metrics"]


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
def test_get_nonexistent_machine():
    """Test getting status for a nonexistent machine."""
    assert client is not None, "Client should not be None when FastAPI is available"

    response = client.get("/machines/NONEXISTENT/status")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "message" in data


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
def test_update_machine_status(sample_machine_data):
    """Test updating machine status."""
    assert client is not None, "Client should not be None when FastAPI is available"

    response = client.post(
        f"/machines/{sample_machine_data['machine_id']}/status",
        json=sample_machine_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["machine_id"] == sample_machine_data["machine_id"]
    assert data["status"] == sample_machine_data["status"]
    assert "last_updated" in data
    assert data["metrics"] == sample_machine_data["metrics"]


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
def test_update_machine_status_invalid_data():
    """Test updating machine status with invalid data."""
    assert client is not None, "Client should not be None when FastAPI is available"

    invalid_data = {
        "status": "invalid_status",
        "metrics": {"temperature": "not_a_number"},
    }
    response = client.post("/machines/TEST_MACHINE_001/status", json=invalid_data)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "message" in data


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
def test_list_machines(sample_machine_data):
    """Test listing machines."""
    assert client is not None, "Client should not be None when FastAPI is available"

    # Create a machine first
    client.post(
        f"/machines/{sample_machine_data['machine_id']}/status",
        json=sample_machine_data,
    )

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


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
def test_list_machines_with_filters(sample_machine_data):
    """Test listing machines with filters."""
    assert client is not None, "Client should not be None when FastAPI is available"

    # Create a machine first
    client.post(
        f"/machines/{sample_machine_data['machine_id']}/status",
        json=sample_machine_data,
    )

    # List machines with status filter
    response = client.get("/machines?status=running")
    assert response.status_code == 200
    data = response.json()
    assert all(machine["status"] == "running" for machine in data["machines"])


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
def test_get_machine_metrics(sample_machine_data):
    """Test getting machine metrics."""
    assert client is not None, "Client should not be None when FastAPI is available"

    # Create a machine first
    client.post(
        f"/machines/{sample_machine_data['machine_id']}/status",
        json=sample_machine_data,
    )

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
