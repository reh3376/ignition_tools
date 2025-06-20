"""MCP Tools Main Application.

This module provides the main FastAPI application for the MCP Tools service,
including health checks, authentication, and development tools functionality.
"""

import os
from datetime import datetime
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="MCP Tools Service",
    description="Machine Control Program Tools Service for IGN Scripts",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return 400 status code."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": "Invalid request data",
            "details": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):  # noqa: ARG001
    """Handle HTTP exceptions and return error response at top level."""
    # If the detail is a dict with error/message, return it directly
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    # Otherwise, use the default FastAPI behavior
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# In-memory storage for tests and results
tests_storage: dict[str, dict[str, Any]] = {}
results_storage: dict[str, dict[str, Any]] = {}


# Data Models
class TestParameters(BaseModel):
    """Test parameters model."""

    duration: int = Field(..., description="Test duration in seconds")
    load_level: str = Field(..., description="Load level for the test")
    metrics: list[str] = Field(..., description="Metrics to collect")


class TestCreate(BaseModel):
    """Test creation model."""

    test_id: str = Field(..., description="Unique test identifier")
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    parameters: TestParameters = Field(..., description="Test parameters")


class TestResponse(BaseModel):
    """Test response model."""

    test_id: str
    name: str
    description: str
    parameters: TestParameters
    created_at: datetime
    status: str = "created"


class TestListResponse(BaseModel):
    """Test list response model."""

    tests: list[TestResponse]
    total: int


class TestRunRequest(BaseModel):
    """Test run request model."""

    type: str | None = "standard"


class PerformanceMetrics(BaseModel):
    """Performance metrics model."""

    response_times: list[float]
    throughput: float
    avg_response_time: float
    max_response_time: float
    min_response_time: float


class TestResults(BaseModel):
    """Test results model."""

    metrics: dict[str, Any]
    summary: dict[str, Any]
    performance_metrics: PerformanceMetrics | None = None


class TestRunResponse(BaseModel):
    """Test run response model."""

    test_id: str
    status: str
    start_time: datetime
    end_time: datetime
    results: TestResults
    performance_metrics: PerformanceMetrics | None = None


class TestResultsResponse(BaseModel):
    """Test results response model."""

    test_id: str
    results: TestResults


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    message: str


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    details: dict[str, Any]


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse: Health status information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        details={
            "service": "mcp-tools",
            "environment": os.getenv("ENVIRONMENT", "development"),
        },
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Dict[str, str]: Welcome message
    """
    return {"message": "Welcome to MCP Tools Service"}


@app.post("/api/tests", response_model=TestResponse)
async def create_test(test_data: TestCreate) -> TestResponse:
    """Create a new API test.

    Args:
        test_data: Test creation data

    Returns:
        TestResponse: Created test information

    Raises:
        HTTPException: If test_id already exists or validation fails
    """
    try:
        # Validate parameters
        if (
            not isinstance(test_data.parameters.duration, int)
            or test_data.parameters.duration <= 0
        ):
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="validation_error",
                    message="Duration must be a positive integer",
                ).model_dump(),
            )

        if test_data.test_id in tests_storage:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="duplicate_test_id",
                    message=f"Test with ID {test_data.test_id} already exists",
                ).model_dump(),
            )

        # Create test
        created_at = datetime.now()
        test_response = TestResponse(
            test_id=test_data.test_id,
            name=test_data.name,
            description=test_data.description,
            parameters=test_data.parameters,
            created_at=created_at,
            status="created",
        )

        # Store test
        tests_storage[test_data.test_id] = test_response.model_dump()

        return test_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error="creation_error", message=str(e)).model_dump(),
        ) from None


@app.get("/api/tests/{test_id}", response_model=TestResponse)
async def get_test(test_id: str) -> TestResponse:
    """Get a specific test by ID.

    Args:
        test_id: Test identifier

    Returns:
        TestResponse: Test information

    Raises:
        HTTPException: If test not found
    """
    if test_id not in tests_storage:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "test_not_found",
                "message": f"Test with ID {test_id} not found",
            },
        )

    test_data = tests_storage[test_id]
    return TestResponse(**test_data)


@app.get("/api/tests", response_model=TestListResponse)
async def list_tests() -> TestListResponse:
    """List all tests.

    Returns:
        TestListResponse: List of all tests
    """
    tests = [TestResponse(**test_data) for test_data in tests_storage.values()]
    return TestListResponse(tests=tests, total=len(tests))


@app.post("/api/tests/{test_id}/run", response_model=TestRunResponse)
async def run_test(
    test_id: str, run_request: TestRunRequest | None = None
) -> TestRunResponse:
    """Run a specific test.

    Args:
        test_id: Test identifier
        run_request: Optional run configuration

    Returns:
        TestRunResponse: Test execution results

    Raises:
        HTTPException: If test not found
    """
    if test_id not in tests_storage:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "test_not_found",
                "message": f"Test with ID {test_id} not found",
            },
        )

    start_time = datetime.now()

    # Simulate test execution
    import time

    time.sleep(0.01)  # Brief simulation

    end_time = datetime.now()

    # Generate mock results
    results = TestResults(
        metrics={
            "temperature": 75.5,
            "pressure": 2.1,
            "speed": 1000,
            "success_rate": 98.5,
        },
        summary={
            "total_operations": 100,
            "successful_operations": 98,
            "failed_operations": 2,
            "execution_time": (end_time - start_time).total_seconds(),
        },
    )

    # Add performance metrics if it's a performance test
    performance_metrics = None
    if run_request and run_request.type == "performance":
        performance_metrics = PerformanceMetrics(
            response_times=[0.1, 0.12, 0.09, 0.11, 0.13],
            throughput=850.0,
            avg_response_time=0.11,
            max_response_time=0.13,
            min_response_time=0.09,
        )
        results.performance_metrics = performance_metrics

    # Store results
    result_data = {
        "test_id": test_id,
        "results": results.model_dump(),
        "start_time": start_time,
        "end_time": end_time,
        "status": "completed",
    }
    results_storage[test_id] = result_data

    # Update test status
    tests_storage[test_id]["status"] = "completed"

    response = TestRunResponse(
        test_id=test_id,
        status="completed",
        start_time=start_time,
        end_time=end_time,
        results=results,
    )

    if performance_metrics:
        response.performance_metrics = performance_metrics

    return response


@app.get("/api/tests/{test_id}/results", response_model=TestResultsResponse)
async def get_test_results(test_id: str) -> TestResultsResponse:
    """Get results for a specific test.

    Args:
        test_id: Test identifier

    Returns:
        TestResultsResponse: Test results

    Raises:
        HTTPException: If test or results not found
    """
    if test_id not in tests_storage:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "test_not_found",
                "message": f"Test with ID {test_id} not found",
            },
        )

    if test_id not in results_storage:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "results_not_found",
                "message": f"Results for test {test_id} not found. Test may not have been run yet.",
            },
        )

    result_data = results_storage[test_id]
    results = TestResults(**result_data["results"])

    return TestResultsResponse(test_id=test_id, results=results)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8082, reload=True)
