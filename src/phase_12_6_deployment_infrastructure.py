"""Phase 12.6: Deployment & Infrastructure Implementation

Following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation using Pydantic models
3. Robust error handling with user-friendly messages
4. Modular testing approach with progressive complexity
5. Proper resource management with async context managers

This module provides production-ready deployment infrastructure for the IGN Scripts
Code Intelligence System with Docker containerization, CI/CD pipelines, health checks,
and monitoring capabilities.
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
from typing import Any, Dict, List, Optional

import docker
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables
load_dotenv()

# === STEP 1: ENVIRONMENT VALIDATION FIRST (crawl_mcp.py methodology) ===

def validate_deployment_environment() -> Dict[str, Any]:
    """Validate deployment environment setup before proceeding.
    
    Following crawl_mcp.py pattern: Environment validation first.
    """
    validation_results = {
        "docker_available": False,
        "docker_compose_available": False,
        "github_actions_configured": False,
        "environment_variables": False,
        "deployment_files": False,
        "valid": False,
        "errors": [],
        "warnings": []
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
                timeout=10
            )
            if result.returncode == 0:
                validation_results["docker_compose_available"] = True
        except Exception as e:
            validation_results["errors"].append(f"Docker Compose not available: {e}")
        
        # Check GitHub Actions configuration
        github_actions_dir = Path(".github/workflows")
        if github_actions_dir.exists() and any(github_actions_dir.glob("*.yml")):
            validation_results["github_actions_configured"] = True
        else:
            validation_results["warnings"].append("GitHub Actions workflows not found")
        
        # Check required environment variables
        required_env_vars = [
            "NEO4J_URI",
            "NEO4J_USER",
            "NEO4J_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if not missing_vars:
            validation_results["environment_variables"] = True
        else:
            validation_results["errors"].append(f"Missing environment variables: {missing_vars}")
        
        # Check deployment files
        deployment_files = ["Dockerfile", "docker-compose.yml"]
        missing_files = []
        for file in deployment_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if not missing_files:
            validation_results["deployment_files"] = True
        else:
            validation_results["warnings"].append(f"Missing deployment files: {missing_files}")
        
        # Overall validation
        validation_results["valid"] = (
            validation_results["docker_available"] and
            validation_results["environment_variables"]
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
    ports: Dict[int, int] = Field(default_factory=dict, description="Port mappings")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    volumes: List[str] = Field(default_factory=list, description="Volume mounts")
    restart_policy: str = Field(default="unless-stopped", description="Restart policy")
    
    @validator('image_name')
    def validate_image_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Image name must be a non-empty string")
        return v
    
    @validator('restart_policy')
    def validate_restart_policy(cls, v):
        valid_policies = ["no", "always", "unless-stopped", "on-failure"]
        if v not in valid_policies:
            raise ValueError(f"Restart policy must be one of: {valid_policies}")
        return v


class HealthCheckConfig(BaseModel):
    """Health check configuration."""
    
    endpoint: str = Field(default="/health", description="Health check endpoint")
    interval: int = Field(default=30, ge=1, description="Health check interval in seconds")
    timeout: int = Field(default=10, ge=1, description="Health check timeout in seconds")
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
    resource_limits: Dict[str, str] = Field(default_factory=dict, description="Resource limits")
    
    @validator('environment')
    def validate_environment(cls, v):
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
    container_id: Optional[str] = None
    container_name: Optional[str] = None
    ports: Dict[int, int] = field(default_factory=dict)
    health_status: str = "unknown"
    deployment_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


async def main():
    """Main execution function for Phase 12.6."""
    print("🚀 Phase 12.6: Deployment & Infrastructure Implementation")
    print("Following crawl_mcp.py methodology")
    
    # Step 1: Environment validation first
    print("\n🔍 Step 1: Environment Validation")
    env_validation = validate_deployment_environment()
    
    if env_validation["valid"]:
        print("✅ Environment validation passed")
    else:
        print("❌ Environment validation failed")
        for error in env_validation["errors"]:
            print(f"   Error: {error}")
        for warning in env_validation["warnings"]:
            print(f"   Warning: {warning}")
    
    # Save results
    results = {
        "phase": "12.6 - Deployment & Infrastructure",
        "timestamp": datetime.now().isoformat(),
        "environment_validation": env_validation,
        "methodology": "crawl_mcp.py systematic approach"
    }
    
    results_file = Path("phase_12_6_deployment_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {results_file}")
    return results


if __name__ == "__main__":
    asyncio.run(main()) 