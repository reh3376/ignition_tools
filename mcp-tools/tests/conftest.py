"""Test configuration for MCP Tools service tests."""

import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import pytest

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

# Add the MCP Tools src directory to Python path
mcp_tools_root = Path(__file__).parent.parent
sys.path.insert(0, str(mcp_tools_root / "src"))

# Type-safe imports with proper error handling
FASTAPI_AVAILABLE = False
TestClientClass: type["TestClient"] | None = None
app_instance: Optional["FastAPI"] = None

try:
    from fastapi.testclient import TestClient

    TestClientClass = TestClient

    # Import the main module and extract the app safely
    import main

    app_instance = getattr(main, "app", None)

    if app_instance is not None:
        FASTAPI_AVAILABLE = True
    else:
        raise ImportError("main module does not have 'app' attribute")

except ImportError:
    FASTAPI_AVAILABLE = False
    TestClientClass = None
    app_instance = None


@pytest.fixture
def client() -> Generator["TestClient", None, None]:
    """Create a test client for the FastAPI app."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    if TestClientClass is None:
        pytest.skip("TestClient class not imported")

    if app_instance is None:
        pytest.skip("FastAPI app instance not found")

    # At this point, type checker knows all components are available
    with TestClientClass(app_instance) as test_client:
        yield test_client


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
