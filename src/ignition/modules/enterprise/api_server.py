"""Phase 10: Enterprise Integration & Deployment - FastAPI Server.

This module provides REST API endpoints for testing, monitoring, and managing
the Phase 10 enterprise modules using FastAPI and uvicorn following crawl_mcp.py methodology.

Features:
- Environment validation endpoints
- Module deployment endpoints
- Health check and monitoring endpoints
- Auto-generated API documentation
- Progressive complexity testing endpoints

Methodology:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling and User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity Support
6. Resource Management and Cleanup

Usage:
    # Start the API server
    python -m uvicorn src.ignition.modules.enterprise.api_server:app --reload --port 8000

    # Access API documentation
    http://localhost:8000/docs
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .analytics_platform import AdvancedAnalyticsPlatformModule
from .cloud_integration import CloudIntegrationModule

# Import Phase 10 modules
from .enterprise_architecture import EnterpriseArchitectureModule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Phase 10: Enterprise Integration & Deployment API",
    description="REST API for testing and managing Phase 10 enterprise modules",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests/responses
class ValidationResponse(BaseModel):
    """Response model for environment validation."""

    overall_valid: bool
    validation_score: float
    valid_components: int
    total_components: int
    details: dict[str, Any]
    recommendations: list[str] = []


class DeploymentRequest(BaseModel):
    """Request model for module deployment."""

    complexity_level: str = Field(
        default="basic",
        description="Deployment complexity level",
        pattern="^(basic|standard|advanced|enterprise)$",
    )
    dry_run: bool = Field(default=False, description="Perform dry run without actual deployment")


class DeploymentResponse(BaseModel):
    """Response model for deployment operations."""

    success: bool
    complexity_level: str
    message: str
    steps_completed: list[dict[str, Any]] = []
    error: str | None = None
    recommendations: list[str] = []


class HealthCheckResponse(BaseModel):
    """Response model for health checks."""

    status: str
    timestamp: str
    modules: dict[str, str]
    environment_score: float
    uptime: str


class TestRequest(BaseModel):
    """Request model for comprehensive testing."""

    complexity_level: str = Field(
        default="basic",
        description="Test complexity level",
        pattern="^(basic|standard|advanced|enterprise)$",
    )
    include_deployment: bool = Field(default=False, description="Include deployment testing")


# Global module instances (initialized on startup)
architecture_module: EnterpriseArchitectureModule | None = None
cloud_module: CloudIntegrationModule | None = None
analytics_module: AdvancedAnalyticsPlatformModule | None = None
startup_time = datetime.now()


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize modules on startup following crawl_mcp.py methodology."""
    global architecture_module, cloud_module, analytics_module

    logger.info("🚀 Phase 10 Enterprise API: Starting up...")

    try:
        # Step 1: Environment Variable Validation First
        logger.info("Initializing enterprise modules...")

        architecture_module = EnterpriseArchitectureModule()
        cloud_module = CloudIntegrationModule()
        analytics_module = AdvancedAnalyticsPlatformModule()

        logger.info("✅ Phase 10 Enterprise API: All modules initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize enterprise modules: {e}")
        # Continue startup even if modules fail to initialize
        logger.warning("API will start with limited functionality")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up resources on shutdown."""
    logger.info("🧹 Phase 10 Enterprise API: Shutting down...")

    # Step 6: Resource Management and Cleanup
    if architecture_module:
        architecture_module.cleanup_resources()
    if cloud_module:
        cloud_module.cleanup_resources()
    if analytics_module:
        analytics_module.cleanup_resources()

    logger.info("✅ Phase 10 Enterprise API: Shutdown completed")


# Health and Status Endpoints


@app.get("/", response_model=dict[str, Any])
async def root() -> None:
    """Root endpoint with API information."""
    return {
        "message": "Phase 10: Enterprise Integration & Deployment API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "validation": "/api/v1/validation",
            "deployment": "/api/v1/deployment",
            "testing": "/api/v1/testing",
            "monitoring": "/api/v1/monitoring",
        },
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> None:
    """Health check endpoint for monitoring.

    Following crawl_mcp.py methodology for comprehensive status reporting.
    """
    try:
        # Calculate uptime
        uptime = datetime.now() - startup_time
        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m"

        # Check module status
        modules_status = {}
        environment_scores = []

        if architecture_module:
            arch_status = architecture_module.get_status()
            env_validation = arch_status["environment_validation"]
            modules_status["enterprise_architecture"] = "healthy" if env_validation["overall_valid"] else "degraded"
            environment_scores.append(env_validation["validation_score"])
        else:
            modules_status["enterprise_architecture"] = "unavailable"

        if cloud_module:
            cloud_status = cloud_module.get_status()
            cloud_validation = cloud_status["environment_validation"]
            modules_status["cloud_integration"] = "healthy" if cloud_validation["overall_valid"] else "degraded"
            environment_scores.append(cloud_validation["validation_score"])
        else:
            modules_status["cloud_integration"] = "unavailable"

        if analytics_module:
            analytics_status = analytics_module.get_status()
            analytics_validation = analytics_status["environment_validation"]
            modules_status["analytics_platform"] = "healthy" if analytics_validation["overall_valid"] else "degraded"
            environment_scores.append(analytics_validation["validation_score"])
        else:
            modules_status["analytics_platform"] = "unavailable"

        # Calculate overall environment score
        avg_environment_score = sum(environment_scores) / len(environment_scores) if environment_scores else 0.0

        # Determine overall status
        healthy_modules = sum(1 for status in modules_status.values() if status == "healthy")
        total_modules = len(modules_status)

        if healthy_modules == total_modules:
            overall_status = "healthy"
        elif healthy_modules > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            modules=modules_status,
            environment_score=avg_environment_score,
            uptime=uptime_str,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e!s}")


# Environment Validation Endpoints


@app.get("/api/v1/validation/all", response_model=ValidationResponse)
async def validate_all_environments() -> None:
    """Validate all enterprise module environments.

    Following crawl_mcp.py methodology: Step 1 - Environment Variable Validation First
    """
    try:
        validation_results = {}
        valid_count = 0
        total_count = 0
        all_recommendations = []

        # Validate Enterprise Architecture
        if architecture_module:
            arch_validation = architecture_module.validate_environment()
            validation_results["enterprise_architecture"] = arch_validation
            if arch_validation["overall_valid"]:
                valid_count += 1
            total_count += 1

        # Validate Cloud Integration
        if cloud_module:
            cloud_validation = cloud_module.validate_environment()
            validation_results["cloud_integration"] = cloud_validation
            if cloud_validation["overall_valid"]:
                valid_count += 1
            total_count += 1

        # Validate Analytics Platform
        if analytics_module:
            analytics_validation = analytics_module.validate_environment()
            validation_results["analytics_platform"] = analytics_validation
            if analytics_validation["overall_valid"]:
                valid_count += 1
            total_count += 1

        # Calculate overall metrics
        overall_valid = valid_count == total_count
        validation_score = (valid_count / total_count * 100) if total_count > 0 else 0.0

        # Collect recommendations
        if not overall_valid:
            all_recommendations = [
                "Fix environment variables for failed modules",
                "Check .env file configuration",
                "Verify all required environment variables are set",
                "Run individual module validation for detailed information",
            ]

        return ValidationResponse(
            overall_valid=overall_valid,
            validation_score=validation_score,
            valid_components=valid_count,
            total_components=total_count,
            details=validation_results,
            recommendations=all_recommendations,
        )

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {e!s}")


@app.get("/api/v1/validation/architecture", response_model=dict[str, Any])
async def validate_architecture_environment() -> None:
    """Validate enterprise architecture environment."""
    if not architecture_module:
        raise HTTPException(status_code=503, detail="Enterprise Architecture module not available")

    try:
        return architecture_module.validate_environment()
    except Exception as e:
        logger.error(f"Architecture validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Architecture validation failed: {e!s}")


@app.get("/api/v1/validation/cloud", response_model=dict[str, Any])
async def validate_cloud_environment() -> None:
    """Validate cloud integration environment."""
    if not cloud_module:
        raise HTTPException(status_code=503, detail="Cloud Integration module not available")

    try:
        return cloud_module.validate_environment()
    except Exception as e:
        logger.error(f"Cloud validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cloud validation failed: {e!s}")


@app.get("/api/v1/validation/analytics", response_model=dict[str, Any])
async def validate_analytics_environment() -> None:
    """Validate analytics platform environment."""
    if not analytics_module:
        raise HTTPException(status_code=503, detail="Analytics Platform module not available")

    try:
        return analytics_module.validate_environment()
    except Exception as e:
        logger.error(f"Analytics validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics validation failed: {e!s}")


# Deployment Endpoints


@app.post("/api/v1/deployment/architecture", response_model=DeploymentResponse)
async def deploy_architecture(request: DeploymentRequest, background_tasks: BackgroundTasks) -> None:
    """Deploy enterprise architecture with progressive complexity.

    Following crawl_mcp.py methodology: Step 5 - Progressive Complexity Support
    """
    if not architecture_module:
        raise HTTPException(status_code=503, detail="Enterprise Architecture module not available")

    try:
        if request.dry_run:
            # Simulate deployment for dry run
            return DeploymentResponse(
                success=True,
                complexity_level=request.complexity_level,
                message=f"Dry run completed for {request.complexity_level} complexity",
                steps_completed=[
                    {
                        "step": "dry_run",
                        "success": True,
                        "message": "Simulation completed",
                    }
                ],
            )

        # Perform actual deployment
        result = architecture_module.deploy_architecture(request.complexity_level)

        # Schedule cleanup in background
        background_tasks.add_task(cleanup_after_delay, "architecture", 300)  # 5 minutes

        return DeploymentResponse(
            success=result["success"],
            complexity_level=result["complexity_level"],
            message=result["message"],
            steps_completed=result.get("steps_completed", []),
            error=result.get("error"),
            recommendations=result.get("recommendations", []),
        )

    except Exception as e:
        logger.error(f"Architecture deployment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {e!s}")


@app.post("/api/v1/deployment/cloud", response_model=DeploymentResponse)
async def deploy_cloud(request: DeploymentRequest, background_tasks: BackgroundTasks) -> None:
    """Deploy cloud infrastructure with progressive complexity."""
    if not cloud_module:
        raise HTTPException(status_code=503, detail="Cloud Integration module not available")

    try:
        if request.dry_run:
            return DeploymentResponse(
                success=True,
                complexity_level=request.complexity_level,
                message=f"Cloud dry run completed for {request.complexity_level} complexity",
                steps_completed=[
                    {
                        "step": "dry_run",
                        "success": True,
                        "message": "Cloud simulation completed",
                    }
                ],
            )

        result = cloud_module.deploy_cloud_infrastructure(request.complexity_level)

        background_tasks.add_task(cleanup_after_delay, "cloud", 300)

        return DeploymentResponse(
            success=result["success"],
            complexity_level=result["complexity_level"],
            message=result["message"],
            steps_completed=result.get("steps_completed", []),
            error=result.get("error"),
            recommendations=result.get("recommendations", []),
        )

    except Exception as e:
        logger.error(f"Cloud deployment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cloud deployment failed: {e!s}")


@app.post("/api/v1/deployment/analytics", response_model=DeploymentResponse)
async def deploy_analytics(request: DeploymentRequest, background_tasks: BackgroundTasks) -> None:
    """Deploy analytics platform with progressive complexity."""
    if not analytics_module:
        raise HTTPException(status_code=503, detail="Analytics Platform module not available")

    try:
        if request.dry_run:
            return DeploymentResponse(
                success=True,
                complexity_level=request.complexity_level,
                message=f"Analytics dry run completed for {request.complexity_level} complexity",
                steps_completed=[
                    {
                        "step": "dry_run",
                        "success": True,
                        "message": "Analytics simulation completed",
                    }
                ],
            )

        result = analytics_module.deploy_analytics_platform(request.complexity_level)

        background_tasks.add_task(cleanup_after_delay, "analytics", 300)

        return DeploymentResponse(
            success=result["success"],
            complexity_level=result["complexity_level"],
            message=result["message"],
            steps_completed=result.get("steps_completed", []),
            error=result.get("error"),
            recommendations=result.get("recommendations", []),
        )

    except Exception as e:
        logger.error(f"Analytics deployment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics deployment failed: {e!s}")


# Testing Endpoints


@app.post("/api/v1/testing/comprehensive", response_model=dict[str, Any])
async def run_comprehensive_tests(request: TestRequest) -> None:
    """Run comprehensive tests on all enterprise modules.

    Following crawl_mcp.py methodology: Step 4 - Modular Component Testing
    """
    try:
        test_results = {}
        passed_tests = 0
        total_tests = 0

        # Test Enterprise Architecture
        if architecture_module:
            arch_validation = architecture_module.validate_environment()
            test_results["enterprise_architecture"] = {
                "environment_validation": arch_validation,
                "status": "passed" if arch_validation["overall_valid"] else "failed",
            }

            if request.include_deployment:
                arch_deployment = architecture_module.deploy_architecture(request.complexity_level)
                test_results["enterprise_architecture"]["deployment"] = arch_deployment
                test_results["enterprise_architecture"]["status"] = (
                    "passed" if (arch_validation["overall_valid"] and arch_deployment["success"]) else "failed"
                )

            if test_results["enterprise_architecture"]["status"] == "passed":
                passed_tests += 1
            total_tests += 1

        # Test Cloud Integration
        if cloud_module:
            cloud_validation = cloud_module.validate_environment()
            test_results["cloud_integration"] = {
                "environment_validation": cloud_validation,
                "status": "passed" if cloud_validation["overall_valid"] else "failed",
            }

            if request.include_deployment:
                cloud_deployment = cloud_module.deploy_cloud_infrastructure(request.complexity_level)
                test_results["cloud_integration"]["deployment"] = cloud_deployment
                test_results["cloud_integration"]["status"] = (
                    "passed" if (cloud_validation["overall_valid"] and cloud_deployment["success"]) else "failed"
                )

            if test_results["cloud_integration"]["status"] == "passed":
                passed_tests += 1
            total_tests += 1

        # Test Analytics Platform
        if analytics_module:
            analytics_validation = analytics_module.validate_environment()
            test_results["analytics_platform"] = {
                "environment_validation": analytics_validation,
                "status": ("passed" if analytics_validation["overall_valid"] else "failed"),
            }

            if request.include_deployment:
                analytics_deployment = analytics_module.deploy_analytics_platform(request.complexity_level)
                test_results["analytics_platform"]["deployment"] = analytics_deployment
                test_results["analytics_platform"]["status"] = (
                    "passed"
                    if (analytics_validation["overall_valid"] and analytics_deployment["success"])
                    else "failed"
                )

            if test_results["analytics_platform"]["status"] == "passed":
                passed_tests += 1
            total_tests += 1

        # Calculate success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0

        return {
            "test_results": test_results,
            "summary": {
                "complexity_level": request.complexity_level,
                "include_deployment": request.include_deployment,
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Comprehensive testing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Testing failed: {e!s}")


# Monitoring Endpoints


@app.get("/api/v1/monitoring/status", response_model=dict[str, Any])
async def get_module_status() -> None:
    """Get detailed status of all enterprise modules."""
    try:
        status = {}

        if architecture_module:
            status["enterprise_architecture"] = architecture_module.get_status()

        if cloud_module:
            status["cloud_integration"] = cloud_module.get_status()

        if analytics_module:
            status["analytics_platform"] = analytics_module.get_status()

        return {
            "timestamp": datetime.now().isoformat(),
            "modules": status,
            "api_version": "1.0.0",
            "uptime": str(datetime.now() - startup_time),
        }

    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {e!s}")


# Background task for cleanup
async def cleanup_after_delay(module_name: str, delay_seconds: int) -> None:
    """Clean up module resources after a delay."""
    await asyncio.sleep(delay_seconds)
    logger.info(f"🧹 Cleaning up {module_name} module resources after {delay_seconds} seconds")

    if module_name == "architecture" and architecture_module:
        architecture_module.cleanup_resources()
    elif module_name == "cloud" and cloud_module:
        cloud_module.cleanup_resources()
    elif module_name == "analytics" and analytics_module:
        analytics_module.cleanup_resources()


# CLI command to start the server
def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    """Start the Phase 10 Enterprise API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    logger.info(f"🚀 Starting Phase 10 Enterprise API server on {host}:{port}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/docs")
    logger.info(f"🔍 Health Check: http://{host}:{port}/health")

    uvicorn.run(
        "src.ignition.modules.enterprise.api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    start_server()
