"""Test configuration for MCP service tests."""

import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import pytest

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

# Add the MCP src directory to Python path
mcp_root = Path(__file__).parent.parent
sys.path.insert(0, str(mcp_root / "src"))

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
def sample_machine_data() -> dict[str, Any]:
    """Provide sample machine data for testing."""
    return {
        "machine_id": "TEST_MACHINE_001",
        "status": "running",
        "metrics": {"temperature": 75.5, "pressure": 2.1, "speed": 1000},
    }


@pytest.fixture
def sample_machine_list() -> list[dict[str, Any]]:
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
