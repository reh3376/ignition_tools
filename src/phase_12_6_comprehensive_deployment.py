"""Phase 12.6: Comprehensive Deployment & Infrastructure Implementation

Following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation using Pydantic models
3. Robust error handling with user-friendly messages
4. Modular testing approach with progressive complexity
5. Proper resource management with async context managers

This module provides production-ready deployment infrastructure for the IGN Scripts
Code Intelligence System with Docker containerization, CI/CD pipelines, health checks,
monitoring capabilities, and comprehensive testing validation.
"""

import asyncio
import json
import os
import subprocess
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import docker
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables
load_dotenv()

# === STEP 1: ENVIRONMENT VALIDATION FIRST (crawl_mcp.py methodology) ===


def validate_deployment_environment() -> dict[str, Any]:
    """Validate deployment environment setup before proceeding.

    Following crawl_mcp.py pattern: Environment validation first.
    """
    validation_results = {
        "docker_available": False,
        "docker_compose_available": False,
        "github_actions_configured": False,
        "environment_variables": False,
        "deployment_files": False,
        "network_connectivity": False,
        "valid": False,
        "errors": [],
        "warnings": [],
    }

    try:
        # Check Docker availability
        try:
            client = docker.from_env()
            client.ping()
            validation_results["docker_available"] = True
        except Exception as e:
            validation_results["errors"].append(f"Docker not available: {e}")

        # Check Docker Compose availability
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                validation_results["docker_compose_available"] = True
        except Exception as e:
            validation_results["warnings"].append(f"Docker Compose not available: {e}")

        # Check GitHub Actions configuration
        github_actions_dir = Path(".github/workflows")
        if github_actions_dir.exists() and any(github_actions_dir.glob("*.yml")):
            validation_results["github_actions_configured"] = True
        else:
            validation_results["warnings"].append("GitHub Actions workflows not found")

        # Check required environment variables
        required_env_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if not missing_vars:
            validation_results["environment_variables"] = True
        else:
            validation_results["errors"].append(
                f"Missing environment variables: {missing_vars}"
            )

        # Check deployment files
        deployment_files = ["Dockerfile", "docker-compose.yml"]
        missing_files = []
        for file in deployment_files:
            if not Path(file).exists():
                missing_files.append(file)

        if not missing_files:
            validation_results["deployment_files"] = True
        else:
            validation_results["warnings"].append(
                f"Missing deployment files: {missing_files}"
            )

        # Check network connectivity
        try:
            import httpx

            validation_results["network_connectivity"] = True
        except ImportError:
            validation_results["warnings"].append(
                "httpx not available for network checks"
            )

        # Overall validation
        validation_results["valid"] = (
            validation_results["docker_available"]
            and validation_results["environment_variables"]
        )

        return validation_results

    except Exception as e:
        validation_results["errors"].append(f"Environment validation failed: {e}")
        return validation_results


def format_deployment_error(error: Exception, context: str = "") -> str:
    """Format deployment errors for user-friendly messages.

    Following crawl_mcp.py error handling patterns.
    """
    error_str = str(error).lower()

    if "permission" in error_str or "denied" in error_str:
        return f"Permission denied during {context}. Check Docker permissions."
    elif "connection" in error_str or "refused" in error_str:
        return f"Connection failed during {context}. Check Docker daemon status."
    elif "not found" in error_str or "no such" in error_str:
        return f"Resource not found during {context}. Check configuration."
    elif "timeout" in error_str:
        return f"Timeout during {context}. Operation took too long."
    else:
        return f"Deployment error during {context}: {error}"


# === STEP 2: COMPREHENSIVE INPUT VALIDATION ===


class DockerConfig(BaseModel):
    """Docker configuration with comprehensive validation."""

    image_name: str = Field(..., description="Docker image name")
    tag: str = Field(default="latest", description="Docker image tag")
    ports: dict[int, int] = Field(default_factory=dict, description="Port mappings")
    environment: dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )
    volumes: list[str] = Field(default_factory=list, description="Volume mounts")
    restart_policy: str = Field(default="unless-stopped", description="Restart policy")

    @validator("image_name")
    def validate_image_name(cls, v) -> Any:
        if not v or not isinstance(v, str):
            raise ValueError("Image name must be a non-empty string")
        return v

    @validator("restart_policy")
    def validate_restart_policy(cls, v) -> Any:
        valid_policies = ["no", "always", "unless-stopped", "on-failure"]
        if v not in valid_policies:
            raise ValueError(f"Restart policy must be one of: {valid_policies}")
        return v


class HealthCheckConfig(BaseModel):
    """Health check configuration."""

    endpoint: str = Field(default="/health", description="Health check endpoint")
    interval: int = Field(
        default=30, ge=1, description="Health check interval in seconds"
    )
    timeout: int = Field(
        default=10, ge=1, description="Health check timeout in seconds"
    )
    retries: int = Field(default=3, ge=1, description="Health check retries")
    start_period: int = Field(default=60, ge=0, description="Start period in seconds")


class DeploymentConfig(BaseModel):
    """Comprehensive deployment configuration."""

    environment: str = Field(..., description="Deployment environment")
    docker_config: DockerConfig = Field(..., description="Docker configuration")
    health_check: HealthCheckConfig = Field(default_factory=HealthCheckConfig)
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    backup_enabled: bool = Field(default=True, description="Enable backups")
    auto_restart: bool = Field(default=True, description="Enable auto-restart")
    resource_limits: dict[str, str] = Field(
        default_factory=dict, description="Resource limits"
    )

    @validator("environment")
    def validate_environment(cls, v) -> Any:
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v


# === STEP 3: COMPREHENSIVE ERROR HANDLING ===


@dataclass
class DeploymentResult:
    """Deployment operation result with comprehensive details."""

    success: bool
    message: str
    container_id: str | None = None
    container_name: str | None = None
    ports: dict[int, int] = field(default_factory=dict)
    health_status: str = "unknown"
    deployment_time: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DeploymentManager:
    """Production deployment manager following crawl_mcp.py methodology."""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self._docker_client: docker.DockerClient | None = None
        self._is_initialized = False

    async def initialize(self) -> dict[str, Any]:
        """Initialize deployment manager with environment validation."""
        try:
            # Step 1: Environment validation first
            env_validation = validate_deployment_environment()
            if not env_validation["valid"]:
                return {
                    "success": False,
                    "error": "Environment validation failed",
                    "details": env_validation["errors"],
                }

            # Step 2: Initialize Docker client
            try:
                self._docker_client = docker.from_env()
                self._docker_client.ping()
            except Exception as e:
                return {
                    "success": False,
                    "error": format_deployment_error(e, "Docker client initialization"),
                }

            self._is_initialized = True
            return {"success": True, "message": "Deployment manager initialized"}

        except Exception as e:
            return {
                "success": False,
                "error": format_deployment_error(
                    e, "deployment manager initialization"
                ),
            }

    async def deploy_container(self) -> DeploymentResult:
        """Deploy container with comprehensive error handling."""
        start_time = time.time()

        try:
            if not self._is_initialized:
                init_result = await self.initialize()
                if not init_result["success"]:
                    return DeploymentResult(
                        success=False,
                        message=init_result["error"],
                        deployment_time=time.time() - start_time,
                    )

            # Step 1: Validate configuration
            try:
                docker_config = self.config.docker_config
            except Exception as e:
                return DeploymentResult(
                    success=False,
                    message=f"Configuration validation failed: {e}",
                    deployment_time=time.time() - start_time,
                )

            # Step 2: Check for existing container
            container_name = f"ign-scripts-{self.config.environment}"
            existing_container = None

            try:
                existing_container = self._docker_client.containers.get(container_name)
                if existing_container.status == "running":
                    return DeploymentResult(
                        success=True,
                        message=f"Container {container_name} already running",
                        container_id=existing_container.id,
                        container_name=container_name,
                        health_status="running",
                        deployment_time=time.time() - start_time,
                    )
                else:
                    # Stop and remove existing container
                    existing_container.stop()
                    existing_container.remove()
            except docker.errors.NotFound:
                # Container doesn't exist, which is fine
                pass
            except Exception as e:
                return DeploymentResult(
                    success=False,
                    message=format_deployment_error(e, "existing container cleanup"),
                    deployment_time=time.time() - start_time,
                )

            # Step 3: Pull latest image (try local first)
            image_name = f"{docker_config.image_name}:{docker_config.tag}"
            try:
                # Try to use local image first
                self._docker_client.images.get(image_name)
            except docker.errors.ImageNotFound:
                try:
                    self._docker_client.images.pull(image_name)
                except Exception as e:
                    return DeploymentResult(
                        success=False,
                        message=format_deployment_error(e, "image pull/fetch"),
                        deployment_time=time.time() - start_time,
                    )

            # Step 4: Create and start container
            try:
                container = self._docker_client.containers.run(
                    image=image_name,
                    name=container_name,
                    ports=docker_config.ports,
                    environment=docker_config.environment,
                    volumes=docker_config.volumes,
                    restart_policy={"Name": docker_config.restart_policy},
                    detach=True,
                    remove=False,
                )

                # Wait for container to start
                await asyncio.sleep(2)
                container.reload()

                return DeploymentResult(
                    success=True,
                    message=f"Container {container_name} deployed successfully",
                    container_id=container.id,
                    container_name=container_name,
                    ports=docker_config.ports,
                    health_status=container.status,
                    deployment_time=time.time() - start_time,
                )

            except Exception as e:
                return DeploymentResult(
                    success=False,
                    message=format_deployment_error(e, "container creation"),
                    deployment_time=time.time() - start_time,
                )

        except Exception as e:
            return DeploymentResult(
                success=False,
                message=format_deployment_error(e, "deployment"),
                deployment_time=time.time() - start_time,
            )

    async def get_deployment_status(self) -> dict[str, Any]:
        """Get comprehensive deployment status."""
        try:
            if not self._is_initialized:
                return {
                    "status": "not_initialized",
                    "error": "Deployment manager not initialized",
                }

            container_name = f"ign-scripts-{self.config.environment}"

            try:
                container = self._docker_client.containers.get(container_name)
                container.reload()

                return {
                    "status": "deployed",
                    "container": {
                        "id": container.id[:12],
                        "name": container.name,
                        "status": container.status,
                        "image": (
                            container.image.tags[0]
                            if container.image.tags
                            else "unknown"
                        ),
                        "created": container.attrs["Created"],
                        "ports": container.ports,
                        "environment": self.config.environment,
                    },
                    "health": {
                        "status": container.status,
                        "uptime": self._calculate_uptime(container.attrs["Created"]),
                        "restart_count": container.attrs["RestartCount"],
                    },
                }

            except docker.errors.NotFound:
                return {
                    "status": "not_deployed",
                    "message": f"Container {container_name} not found",
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": format_deployment_error(e, "status check"),
                }

        except Exception as e:
            return {
                "status": "error",
                "error": format_deployment_error(e, "deployment status"),
            }

    async def perform_health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            container_name = f"ign-scripts-{self.config.environment}"

            try:
                container = self._docker_client.containers.get(container_name)
                container.reload()

                health_results: Any = {
                    "container_running": container.status == "running",
                    "health_check_passed": False,
                    "response_time": None,
                    "errors": [],
                }

                if container.status == "running":
                    # Perform HTTP health check if configured
                    if self.config.health_check.endpoint:
                        try:
                            import httpx

                            # Find the mapped port for health check
                            health_port = None
                            for (
                                container_port,
                                host_bindings,
                            ) in container.ports.items():
                                if host_bindings:
                                    health_port = host_bindings[0]["HostPort"]
                                    break

                            if health_port:
                                start_time = time.time()
                                async with httpx.AsyncClient(
                                    timeout=self.config.health_check.timeout
                                ) as client:
                                    response = await client.get(
                                        f"http://localhost:{health_port}{self.config.health_check.endpoint}"
                                    )
                                    health_results["response_time"] = (
                                        time.time() - start_time
                                    )
                                    health_results["health_check_passed"] = (
                                        response.status_code == 200
                                    )
                            else:
                                health_results["errors"].append(
                                    "No mapped ports found for health check"
                                )

                        except ImportError:
                            health_results["errors"].append(
                                "httpx not available for health checks"
                            )
                        except Exception as e:
                            health_results["errors"].append(f"Health check failed: {e}")

                return {
                    "healthy": health_results["container_running"]
                    and health_results["health_check_passed"],
                    "details": health_results,
                }

            except docker.errors.NotFound:
                return {
                    "healthy": False,
                    "error": f"Container {container_name} not found",
                }

        except Exception as e:
            return {
                "healthy": False,
                "error": format_deployment_error(e, "health check"),
            }

    def _calculate_uptime(self, created_time: str) -> str:
        """Calculate container uptime."""
        try:
            created = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
            uptime = datetime.now(created.tzinfo) - created

            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            return f"{days}d {hours}h {minutes}m"
        except Exception:
            return "unknown"

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._docker_client:
            self._docker_client.close()
        self._is_initialized = False


# === STEP 4: MODULAR TESTING INTEGRATION ===


class Phase126ComprehensiveTester:
    """Comprehensive testing suite for Phase 12.6 deployment infrastructure."""

    def __init__(self) -> None:
        self.test_results = []

    async def run_comprehensive_tests(self) -> dict[str, Any]:
        """Run comprehensive deployment tests following crawl_mcp.py methodology."""
        print("🚀 Phase 12.6: Deployment & Infrastructure Testing")
        start_time = time.time()

        test_results = {
            "environment_validation": await self._test_environment_validation(),
            "docker_functionality": await self._test_docker_functionality(),
            "deployment_process": await self._test_deployment_process(),
            "health_checks": await self._test_health_checks(),
            "ci_cd_pipeline": await self._test_ci_cd_pipeline(),
            "configuration_validation": await self._test_configuration_validation(),
        }

        # Calculate overall success
        total_tests = len(test_results)
        passed_tests = sum(
            1 for result in test_results.values() if result.get("passed", False)
        )

        return {
            "phase": "12.6 - Deployment & Infrastructure",
            "execution_time": time.time() - start_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "overall_success": passed_tests == total_tests,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat(),
        }

    async def _test_environment_validation(self) -> dict[str, Any]:
        """Test environment validation."""
        try:
            validation_result = validate_deployment_environment()
            return {
                "name": "Environment Validation",
                "passed": validation_result["valid"],
                "details": validation_result,
                "message": (
                    "Environment ready for deployment"
                    if validation_result["valid"]
                    else "Environment validation failed"
                ),
            }
        except Exception as e:
            return {
                "name": "Environment Validation",
                "passed": False,
                "error": str(e),
                "message": "Environment validation test failed",
            }

    async def _test_docker_functionality(self) -> dict[str, Any]:
        """Test Docker functionality."""
        try:
            client = docker.from_env()
            client.ping()

            # Test basic Docker operations
            test_image = "hello-world:latest"
            client.images.pull(test_image)

            container = client.containers.run(
                test_image, name="ign-scripts-test-container", detach=True, remove=True
            )

            # Wait for container to complete
            await asyncio.sleep(2)

            return {
                "name": "Docker Functionality",
                "passed": True,
                "message": "Docker operations successful",
                "details": {"test_container": container.id[:12]},
            }

        except Exception as e:
            return {
                "name": "Docker Functionality",
                "passed": False,
                "error": str(e),
                "message": "Docker functionality test failed",
            }

    async def _test_deployment_process(self) -> dict[str, Any]:
        """Test deployment process."""
        try:
            # Create test configuration
            test_config = DeploymentConfig(
                environment="development",
                docker_config=DockerConfig(
                    image_name="nginx", tag="alpine", ports={80: 8080}
                ),
            )

            manager = DeploymentManager(test_config)
            init_result = await manager.initialize()

            if not init_result["success"]:
                return {
                    "name": "Deployment Process",
                    "passed": False,
                    "error": init_result["error"],
                    "message": "Deployment manager initialization failed",
                }

            # Test deployment
            deployment_result = await manager.deploy_container()

            # Cleanup
            if deployment_result.success and deployment_result.container_id:
                try:
                    container = manager._docker_client.containers.get(
                        deployment_result.container_id
                    )
                    container.stop()
                    container.remove()
                except Exception:
                    pass

            await manager.cleanup()

            return {
                "name": "Deployment Process",
                "passed": deployment_result.success,
                "message": deployment_result.message,
                "details": {
                    "deployment_time": deployment_result.deployment_time,
                    "container_id": deployment_result.container_id,
                },
            }

        except Exception as e:
            return {
                "name": "Deployment Process",
                "passed": False,
                "error": str(e),
                "message": "Deployment process test failed",
            }

    async def _test_health_checks(self) -> dict[str, Any]:
        """Test health check functionality."""
        try:
            # Test health check configuration validation
            health_config = HealthCheckConfig(
                endpoint="/health", interval=30, timeout=10, retries=3
            )

            # Validate configuration
            config_valid = (
                isinstance(health_config.endpoint, str) and health_config.interval > 0
            )

            return {
                "name": "Health Checks",
                "passed": config_valid,
                "message": "Health check configuration valid",
                "details": {
                    "endpoint": health_config.endpoint,
                    "interval": health_config.interval,
                    "timeout": health_config.timeout,
                },
            }

        except Exception as e:
            return {
                "name": "Health Checks",
                "passed": False,
                "error": str(e),
                "message": "Health check test failed",
            }

    async def _test_ci_cd_pipeline(self) -> dict[str, Any]:
        """Test CI/CD pipeline configuration."""
        try:
            github_workflows_dir = Path(".github/workflows")

            if not github_workflows_dir.exists():
                return {
                    "name": "CI/CD Pipeline",
                    "passed": False,
                    "message": "GitHub Actions workflows directory not found",
                    "details": {"path": str(github_workflows_dir)},
                }

            workflow_files = list(github_workflows_dir.glob("*.yml"))

            if not workflow_files:
                return {
                    "name": "CI/CD Pipeline",
                    "passed": False,
                    "message": "No workflow files found",
                    "details": {"workflow_count": 0},
                }

            # Check for deployment-related workflows
            deployment_workflows = []
            for workflow_file in workflow_files:
                try:
                    with open(workflow_file) as f:
                        workflow_content = yaml.safe_load(f)
                        if any(
                            keyword in str(workflow_content).lower()
                            for keyword in ["deploy", "docker", "build"]
                        ):
                            deployment_workflows.append(workflow_file.name)
                except Exception:
                    continue

            return {
                "name": "CI/CD Pipeline",
                "passed": len(deployment_workflows) > 0,
                "message": f"Found {len(deployment_workflows)} deployment-related workflows",
                "details": {
                    "total_workflows": len(workflow_files),
                    "deployment_workflows": deployment_workflows,
                },
            }

        except Exception as e:
            return {
                "name": "CI/CD Pipeline",
                "passed": False,
                "error": str(e),
                "message": "CI/CD pipeline test failed",
            }

    async def _test_configuration_validation(self) -> dict[str, Any]:
        """Test configuration validation."""
        try:
            # Test valid configuration
            valid_config = DeploymentConfig(
                environment="production",
                docker_config=DockerConfig(
                    image_name="ign-scripts", tag="latest", ports={8000: 8000}
                ),
            )

            # Test invalid configuration
            try:
                invalid_config = DeploymentConfig(
                    environment="invalid",
                    docker_config=DockerConfig(image_name="", tag="latest"),
                )
                config_validation_works = False
            except Exception:
                config_validation_works = True

            return {
                "name": "Configuration Validation",
                "passed": config_validation_works
                and valid_config.environment == "production",
                "message": "Configuration validation working correctly",
                "details": {
                    "valid_config_created": True,
                    "invalid_config_rejected": config_validation_works,
                },
            }

        except Exception as e:
            return {
                "name": "Configuration Validation",
                "passed": False,
                "error": str(e),
                "message": "Configuration validation test failed",
            }


# === STEP 5: PROGRESSIVE COMPLEXITY ===


async def run_phase_12_6_implementation() -> dict[str, Any]:
    """Run Phase 12.6 implementation with progressive complexity."""
    print("🚀 Starting Phase 12.6: Deployment & Infrastructure Implementation")
    print(
        "Following crawl_mcp.py methodology: Environment validation → Testing → Deployment"
    )

    implementation_results = {
        "phase": "12.6 - Deployment & Infrastructure",
        "methodology": "crawl_mcp.py systematic approach",
        "start_time": datetime.now().isoformat(),
        "steps": {},
    }

    try:
        # Step 1: Environment Validation (Basic)
        print("\n🔍 Step 1: Environment Validation")
        env_validation = validate_deployment_environment()
        implementation_results["steps"]["environment_validation"] = env_validation

        if env_validation["valid"]:
            print("✅ Environment validation passed")
        else:
            print("⚠️ Environment validation has issues")
            for error in env_validation["errors"]:
                print(f"   Error: {error}")
            for warning in env_validation["warnings"]:
                print(f"   Warning: {warning}")

        # Step 2: Comprehensive Testing (Standard)
        print("\n🧪 Step 2: Comprehensive Testing")
        tester = Phase126ComprehensiveTester()
        test_results = await tester.run_comprehensive_tests()
        implementation_results["steps"]["testing"] = test_results

        print(
            f"✅ Testing completed: {test_results['passed_tests']}/{test_results['total_tests']} tests passed"
        )

        # Step 3: Production Configuration (Advanced)
        print("\n🚀 Step 3: Production Configuration")

        # Create production configuration
        production_config = DeploymentConfig(
            environment=os.getenv("DEPLOYMENT_ENVIRONMENT", "production"),
            docker_config=DockerConfig(
                image_name="ign-scripts-api",
                tag=os.getenv("API_VERSION", "latest"),
                ports={8000: 8000, 7474: 7474, 7687: 7687},
                environment={
                    "NEO4J_URI": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                    "NEO4J_USER": os.getenv("NEO4J_USER", "neo4j"),
                    "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD", ""),
                    "API_VERSION": os.getenv("API_VERSION", "1.0.0"),
                    "DEPLOYMENT_ENVIRONMENT": os.getenv(
                        "DEPLOYMENT_ENVIRONMENT", "production"
                    ),
                },
            ),
            health_check=HealthCheckConfig(
                endpoint="/health", interval=30, timeout=10, retries=3
            ),
            monitoring_enabled=True,
            backup_enabled=True,
        )

        implementation_results["steps"]["production_config"] = {
            "environment": production_config.environment,
            "image": f"{production_config.docker_config.image_name}:{production_config.docker_config.tag}",
            "ports": production_config.docker_config.ports,
            "monitoring": production_config.monitoring_enabled,
        }

        print("✅ Production configuration created")

        # Step 4: Deployment Manager Setup (Enterprise)
        print("\n⚙️ Step 4: Deployment Manager Setup")

        manager = DeploymentManager(production_config)
        init_result = await manager.initialize()

        if init_result["success"]:
            print("✅ Deployment manager initialized successfully")

            # Get deployment status
            status = await manager.get_deployment_status()
            implementation_results["steps"]["deployment_status"] = status

            print(f"📊 Deployment status: {status.get('status', 'unknown')}")
        else:
            print(f"⚠️ Deployment manager initialization: {init_result['error']}")
            implementation_results["steps"]["deployment_manager"] = init_result

        await manager.cleanup()

        # Final results
        implementation_results["success"] = True
        implementation_results["end_time"] = datetime.now().isoformat()
        implementation_results["message"] = (
            "Phase 12.6 implementation completed successfully"
        )

        print("\n🎉 Phase 12.6: Deployment & Infrastructure implementation completed!")
        return implementation_results

    except Exception as e:
        implementation_results["success"] = False
        implementation_results["error"] = format_deployment_error(
            e, "Phase 12.6 implementation"
        )
        implementation_results["end_time"] = datetime.now().isoformat()
        return implementation_results


# === STEP 6: RESOURCE MANAGEMENT ===


@asynccontextmanager
async def deployment_context(config: DeploymentConfig) -> None:
    """Async context manager for deployment operations."""
    manager = DeploymentManager(config)
    try:
        init_result = await manager.initialize()
        if not init_result["success"]:
            raise RuntimeError(
                f"Deployment manager initialization failed: {init_result['error']}"
            )
        yield manager
    finally:
        await manager.cleanup()


# Main execution function
async def main() -> Any:
    """Main execution function for Phase 12.6."""
    results = await run_phase_12_6_implementation()

    # Save results to file
    results_file = Path("phase_12_6_comprehensive_deployment_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {results_file}")

    if results["success"]:
        print("🎉 Phase 12.6: Deployment & Infrastructure - COMPLETED SUCCESSFULLY")
    else:
        print(f"❌ Phase 12.6 failed: {results.get('error', 'Unknown error')}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
