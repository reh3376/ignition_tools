"""Test configuration for MCP Tools service tests."""

import sys
from pathlib import Path
from typing import Any

import pytest

# Add the MCP Tools src directory to Python path
mcp_tools_root = Path(__file__).parent.parent
sys.path.insert(0, str(mcp_tools_root / "src"))

try:
    from fastapi.testclient import TestClient

    from main import app  # type: ignore[attr-defined]

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None
    app = None


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    if not FASTAPI_AVAILABLE or app is None:
        pytest.skip("FastAPI not available or app is None")

    return TestClient(app)  # type: ignore[misc]


@pytest.fixture
def mock_mcp_service() -> dict[str, Any]:
    """Mock MCP service responses."""
    return {
        "health": {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2024-03-17T12:00:00Z",
        },
        "machine_status": {
            "machine_id": "TEST_MACHINE_001",
            "status": "running",
            "last_updated": "2024-03-17T12:00:00Z",
            "metrics": {"temperature": 75.5, "pressure": 2.1, "speed": 1000},
        },
    }


@pytest.fixture
def sample_test_data() -> dict[str, Any]:
    """Provide sample test data for testing."""
    return {
        "test_id": "TEST_001",
        "name": "Performance Test",
        "description": "Test machine performance under load",
        "parameters": {
            "duration": 300,
            "load_level": "high",
            "metrics": ["temperature", "pressure", "speed"],
        },
    }
