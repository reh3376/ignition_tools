import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture
def test_db(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(test_db):
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_mcp_service():
    """Mock MCP service responses."""
    return {
        "health": {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2024-03-17T12:00:00Z"
        },
        "machine_status": {
            "machine_id": "TEST_MACHINE_001",
            "status": "running",
            "last_updated": "2024-03-17T12:00:00Z",
            "metrics": {
                "temperature": 75.5,
                "pressure": 2.1,
                "speed": 1000
            }
        }
    }

@pytest.fixture
def sample_test_data():
    """Provide sample test data for testing."""
    return {
        "test_id": "TEST_001",
        "name": "Performance Test",
        "description": "Test machine performance under load",
        "parameters": {
            "duration": 300,
            "load_level": "high",
            "metrics": ["temperature", "pressure", "speed"]
        }
    }
