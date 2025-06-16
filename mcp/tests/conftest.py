"""Test configuration for MCP service tests."""

import sys
from pathlib import Path

import pytest

# Add the MCP src directory to Python path
mcp_root = Path(__file__).parent.parent
sys.path.insert(0, str(mcp_root / "src"))

try:
    from fastapi.testclient import TestClient

    from main import app

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None
    app = None


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    return TestClient(app)


@pytest.fixture
def sample_machine_data():
    """Provide sample machine data for testing."""
    return {
        "machine_id": "TEST_MACHINE_001",
        "status": "running",
        "metrics": {"temperature": 75.5, "pressure": 2.1, "speed": 1000},
    }


@pytest.fixture
def sample_machine_list():
    """Provide a list of sample machines for testing."""
    return [
        {
            "machine_id": "TEST_MACHINE_001",
            "status": "running",
            "metrics": {"temperature": 75.5, "pressure": 2.1, "speed": 1000},
        },
        {
            "machine_id": "TEST_MACHINE_002",
            "status": "idle",
            "metrics": {"temperature": 25.0, "pressure": 1.0, "speed": 0},
        },
    ]
