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
def sample_machine_data():
    """Provide sample machine data for testing."""
    return {
        "machine_id": "TEST_MACHINE_001",
        "status": "running",
        "metrics": {
            "temperature": 75.5,
            "pressure": 2.1,
            "speed": 1000
        }
    }

@pytest.fixture
def sample_machine_list():
    """Provide a list of sample machines for testing."""
    return [
        {
            "machine_id": "TEST_MACHINE_001",
            "status": "running",
            "metrics": {
                "temperature": 75.5,
                "pressure": 2.1,
                "speed": 1000
            }
        },
        {
            "machine_id": "TEST_MACHINE_002",
            "status": "idle",
            "metrics": {
                "temperature": 25.0,
                "pressure": 1.0,
                "speed": 0
            }
        }
    ]
