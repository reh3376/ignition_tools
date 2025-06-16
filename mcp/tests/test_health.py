"""Health check tests for MCP service."""


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "details" in data
    assert data["status"] == "healthy"


def test_health_check_content_type(client):
    """Test the health check endpoint content type."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"


def test_health_check_structure(client):
    """Test the health check response structure."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["details"], dict)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to MCP Service"
