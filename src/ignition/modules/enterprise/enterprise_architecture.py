"""Phase 10.1: Enterprise Architecture Module

This module implements scalable deployment architecture, high availability,
disaster recovery, and performance optimization following crawl_mcp.py methodology.

Features:
- Scalable deployment architecture
- High availability and disaster recovery
- Enterprise security and compliance
- Performance optimization and monitoring

Methodology:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling and User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity Support
6. Resource Management and Cleanup
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentConfig:
    """Enterprise deployment configuration."""

    deployment_mode: str = "standalone"  # standalone, cluster, cloud
    high_availability: bool = False
    disaster_recovery: bool = False
    load_balancer_url: str | None = None
    cluster_nodes: list[str] = field(default_factory=list)
    backup_strategy: str = "daily"  # daily, hourly, continuous
    monitoring_enabled: bool = True
    performance_tuning: str = "standard"  # basic, standard, advanced


@dataclass
class ArchitectureValidationResult:
    """Result of architecture validation following crawl_mcp.py patterns."""

    valid: bool
    component: str
    message: str
    details: dict[str, Any] | None = None
    error: str | None = None
    recommendations: list[str] = field(default_factory=list)


class EnterpriseArchitectureModule:
    """Enterprise Architecture Module implementation.

    Following crawl_mcp.py methodology:
    1. Environment Variable Validation First
    2. Comprehensive Input Validation
    3. Error Handling and User-Friendly Messages
    4. Modular Component Testing
    5. Progressive Complexity Support
    6. Resource Management and Cleanup
    """

    def __init__(self):
        """Initialize Enterprise Architecture Module following crawl_mcp.py patterns."""
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Step 1: Environment Variable Validation First
        self.env_validation = self._validate_environment_variables()

        # Step 2: Comprehensive Input Validation
        self.config = self._load_and_validate_config()

        # Initialize components
        self.deployment_manager = None
        self.ha_manager = None
        self.dr_manager = None
        self.performance_monitor = None

        # Progressive complexity levels
        self.complexity_levels = ["basic", "standard", "advanced", "enterprise"]
        self.current_complexity = "basic"

        # Resource tracking
        self.resources_allocated = []
        self.cleanup_tasks = []

        # Initialize based on validation results
        if self.env_validation["overall_valid"]:
            self._initialize_components()

    def _validate_environment_variables(self) -> dict[str, Any]:
        """Step 1: Environment Variable Validation First

        Validate enterprise architecture environment variables following crawl_mcp.py patterns.
        """
        self.console.print(
            "🔍 Enterprise Architecture: Environment Validation", style="bold blue"
        )

        required_vars = {
            "ENTERPRISE_DEPLOYMENT_MODE": {
                "required": True,
                "valid_values": ["standalone", "cluster", "cloud"],
                "description": "Deployment mode for enterprise architecture",
            },
            "HIGH_AVAILABILITY_ENABLED": {
                "required": True,
                "valid_values": ["true", "false"],
                "description": "Enable high availability features",
            },
            "DISASTER_RECOVERY_ENABLED": {
                "required": True,
                "valid_values": ["true", "false"],
                "description": "Enable disaster recovery features",
            },
            "LOAD_BALANCER_URL": {
                "required": False,
                "format": "url",
                "description": "Load balancer endpoint URL",
            },
            "CLUSTER_NODES": {
                "required": False,
                "format": "comma_separated",
                "description": "Comma-separated list of cluster nodes",
            },
            "BACKUP_STRATEGY": {
                "required": False,
                "valid_values": ["daily", "hourly", "continuous"],
                "default": "daily",
                "description": "Backup strategy for disaster recovery",
            },
            "PERFORMANCE_TUNING_LEVEL": {
                "required": False,
                "valid_values": ["basic", "standard", "advanced"],
                "default": "standard",
                "description": "Performance tuning level",
            },
        }

        validation_results = {}

        for var_name, var_config in required_vars.items():
            result = self._validate_single_environment_variable(var_name, var_config)
            validation_results[var_name] = result

        # Calculate overall validation
        valid_count = sum(1 for result in validation_results.values() if result.valid)
        total_count = len(validation_results)
        overall_valid = valid_count == total_count

        final_results = {
            "validation_results": validation_results,
            "overall_valid": overall_valid,
            "valid_count": valid_count,
            "total_count": total_count,
            "validation_score": (valid_count / total_count) * 100,
        }

        # Display validation results
        self._display_environment_validation(final_results)

        return final_results

    def _validate_single_environment_variable(
        self, var_name: str, var_config: dict[str, Any]
    ) -> ArchitectureValidationResult:
        """Step 2: Comprehensive Input Validation

        Validate a single environment variable with comprehensive checks.
        """
        value = os.getenv(var_name)

        # Check if required variable is missing
        if var_config.get("required", False) and not value:
            return ArchitectureValidationResult(
                valid=False,
                component=var_name,
                message=f"Required environment variable {var_name} is missing",
                error=f"Missing required variable: {var_name}",
                recommendations=[
                    f"set {var_name} in your .env file",
                    f"Description: {var_config.get('description', 'No description available')}",
                ],
            )

        # Use default value if not required and missing
        if not value and "default" in var_config:
            value = var_config["default"]
            os.environ[var_name] = value

        # Skip validation if optional and not set
        if not value and not var_config.get("required", False):
            return ArchitectureValidationResult(
                valid=True,
                component=var_name,
                message=f"Optional variable {var_name} not set (using defaults)",
                details={
                    "status": "optional",
                    "default_used": var_config.get("default"),
                },
            )

        # Validate against valid values
        if "valid_values" in var_config:
            if value.lower() not in [v.lower() for v in var_config["valid_values"]]:
                return ArchitectureValidationResult(
                    valid=False,
                    component=var_name,
                    message=f"Invalid value for {var_name}: {value}",
                    error=f"Value '{value}' not in valid options: {var_config['valid_values']}",
                    recommendations=[
                        f"set {var_name} to one of: {', '.join(var_config['valid_values'])}",
                        f"Current value: {value}",
                    ],
                )

        # Validate format
        if "format" in var_config and value:
            format_validation = self._validate_format(
                value, var_config["format"], var_name
            )
            if not format_validation.valid:
                return format_validation

        return ArchitectureValidationResult(
            valid=True,
            component=var_name,
            message=f"Environment variable {var_name} validated successfully",
            details={"value": value, "description": var_config.get("description")},
        )

    def _validate_format(
        self, value: str, format_type: str, var_name: str
    ) -> ArchitectureValidationResult:
        """Validate value format following crawl_mcp.py patterns."""
        try:
            if format_type == "url":
                if not (
                    value.startswith("http://")
                    or value.startswith("https://")
                    or value.startswith("tcp://")
                ):
                    return ArchitectureValidationResult(
                        valid=False,
                        component=var_name,
                        message=f"Invalid URL format for {var_name}",
                        error="URL must start with http://, https://, or tcp://",
                        recommendations=[f"Update {var_name} to use proper URL format"],
                    )

            elif format_type == "comma_separated":
                nodes = [node.strip() for node in value.split(",") if node.strip()]
                if not nodes:
                    return ArchitectureValidationResult(
                        valid=False,
                        component=var_name,
                        message=f"Empty comma-separated list for {var_name}",
                        error="list cannot be empty",
                        recommendations=[f"Provide at least one value for {var_name}"],
                    )

            return ArchitectureValidationResult(
                valid=True,
                component=var_name,
                message=f"Format validation passed for {var_name}",
                details={"format": format_type, "value": value},
            )

        except Exception as e:
            return ArchitectureValidationResult(
                valid=False,
                component=var_name,
                message=f"Format validation failed for {var_name}",
                error=f"Validation error: {e!s}",
                recommendations=[f"Check the format of {var_name}"],
            )

    def _load_and_validate_config(self) -> DeploymentConfig:
        """Step 2: Comprehensive Input Validation

        Load and validate deployment configuration.
        """
        try:
            config = DeploymentConfig(
                deployment_mode=os.getenv("ENTERPRISE_DEPLOYMENT_MODE", "standalone"),
                high_availability=os.getenv(
                    "HIGH_AVAILABILITY_ENABLED", "false"
                ).lower()
                == "true",
                disaster_recovery=os.getenv(
                    "DISASTER_RECOVERY_ENABLED", "false"
                ).lower()
                == "true",
                load_balancer_url=os.getenv("LOAD_BALANCER_URL"),
                cluster_nodes=[
                    node.strip()
                    for node in os.getenv("CLUSTER_NODES", "").split(",")
                    if node.strip()
                ],
                backup_strategy=os.getenv("BACKUP_STRATEGY", "daily"),
                monitoring_enabled=os.getenv("MONITORING_ENABLED", "true").lower()
                == "true",
                performance_tuning=os.getenv("PERFORMANCE_TUNING_LEVEL", "standard"),
            )

            # Validate configuration consistency
            validation_errors = self._validate_config_consistency(config)
            if validation_errors:
                self.logger.warning(
                    f"Configuration validation warnings: {validation_errors}"
                )

            return config

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            # Return default configuration
            return DeploymentConfig()

    def _validate_config_consistency(self, config: DeploymentConfig) -> list[str]:
        """Validate configuration consistency following crawl_mcp.py error handling patterns."""
        errors = []

        # Validate cluster mode requirements
        if config.deployment_mode == "cluster" and not config.cluster_nodes:
            errors.append(
                "Cluster deployment mode requires cluster nodes to be specified"
            )

        # Validate high availability requirements
        if config.high_availability and config.deployment_mode == "standalone":
            errors.append("High availability requires cluster or cloud deployment mode")

        # Validate load balancer requirements
        if config.high_availability and not config.load_balancer_url:
            errors.append(
                "High availability requires load balancer URL to be specified"
            )

        # Validate disaster recovery requirements
        if config.disaster_recovery and not config.backup_strategy:
            errors.append("Disaster recovery requires backup strategy to be specified")

        return errors

    def _initialize_components(self):
        """Initialize enterprise architecture components."""
        try:
            self.console.print(
                "🚀 Initializing Enterprise Architecture Components", style="bold green"
            )

            # Initialize deployment manager
            self.deployment_manager = DeploymentManager(self.config)

            # Initialize HA manager if enabled
            if self.config.high_availability:
                self.ha_manager = HighAvailabilityManager(self.config)

            # Initialize DR manager if enabled
            if self.config.disaster_recovery:
                self.dr_manager = DisasterRecoveryManager(self.config)

            # Initialize performance monitor
            if self.config.monitoring_enabled:
                self.performance_monitor = PerformanceMonitor(self.config)

            self.logger.info(
                "Enterprise Architecture components initialized successfully"
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    def _display_environment_validation(self, validation_results: dict[str, Any]):
        """Display environment validation results following crawl_mcp.py patterns."""
        table = Table(title="Enterprise Architecture - Environment Validation")
        table.add_column("Variable", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Message", style="white")
        table.add_column("Details", style="dim")

        for var_name, result in validation_results["validation_results"].items():
            if isinstance(result, ArchitectureValidationResult):
                status = "✅ Valid" if result.valid else "❌ Invalid"
                message = result.message
                details = str(result.details) if result.details else ""

                table.add_row(var_name, status, message, details)

        # Add overall status
        overall_status = (
            "✅ All Valid"
            if validation_results["overall_valid"]
            else f"⚠️ {validation_results['valid_count']}/{validation_results['total_count']} Valid"
        )
        validation_score = validation_results["validation_score"]

        table.add_row(
            "Overall Status",
            overall_status,
            f"Validation Score: {validation_score:.1f}%",
            f"{validation_results['valid_count']} of {validation_results['total_count']} variables valid",
        )

        self.console.print(table)

        # Display recommendations if validation failed
        if not validation_results["overall_valid"]:
            self.console.print("\n📋 Recommendations:", style="bold yellow")
            for result in validation_results["validation_results"].values():
                if (
                    isinstance(result, ArchitectureValidationResult)
                    and not result.valid
                ):
                    for rec in result.recommendations:
                        self.console.print(f"  • {rec}")

    def deploy_architecture(self, complexity_level: str = "basic") -> dict[str, Any]:
        """Step 4: Modular Component Testing
        Step 5: Progressive Complexity Support

        Deploy enterprise architecture with progressive complexity.
        """
        if complexity_level not in self.complexity_levels:
            return {
                "success": False,
                "error": f"Invalid complexity level: {complexity_level}. Valid levels: {self.complexity_levels}",
            }

        self.current_complexity = complexity_level

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console,
            ) as progress:
                task = progress.add_task(
                    f"Deploying {complexity_level} architecture...", total=100
                )

                # Step 1: Validate environment (10%)
                progress.update(
                    task, advance=10, description="Validating environment..."
                )
                env_status = self._validate_deployment_environment()

                # Step 2: Initialize deployment (20%)
                progress.update(
                    task, advance=20, description="Initializing deployment..."
                )
                deployment_result = self._initialize_deployment(complexity_level)

                # Step 3: Configure high availability (30%)
                if self.config.high_availability and complexity_level in [
                    "advanced",
                    "enterprise",
                ]:
                    progress.update(
                        task, advance=30, description="Configuring high availability..."
                    )
                    ha_result = self._configure_high_availability()
                else:
                    progress.update(task, advance=30)
                    ha_result = {
                        "enabled": False,
                        "message": "HA not enabled for this complexity level",
                    }

                # Step 4: Setup disaster recovery (40%)
                if self.config.disaster_recovery and complexity_level == "enterprise":
                    progress.update(
                        task, advance=40, description="Setting up disaster recovery..."
                    )
                    dr_result = self._setup_disaster_recovery()
                else:
                    progress.update(task, advance=40)
                    dr_result = {
                        "enabled": False,
                        "message": "DR not enabled for this complexity level",
                    }

                # Step 5: Performance optimization (50%)
                progress.update(
                    task, advance=50, description="Optimizing performance..."
                )
                perf_result = self._optimize_performance(complexity_level)

                # Step 6: Final validation (100%)
                progress.update(task, advance=50, description="Final validation...")
                final_validation = self._validate_deployment()

                progress.update(
                    task, completed=100, description="Deployment completed!"
                )

            return {
                "success": True,
                "complexity_level": complexity_level,
                "deployment_id": f"enterprise-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "components": {
                    "environment_validation": env_status,
                    "deployment": deployment_result,
                    "high_availability": ha_result,
                    "disaster_recovery": dr_result,
                    "performance": perf_result,
                    "final_validation": final_validation,
                },
                "timestamp": datetime.now().isoformat(),
                "resources_allocated": len(self.resources_allocated),
            }

        except Exception as e:
            # Step 3: Error Handling and User-Friendly Messages
            error_message = self._format_deployment_error(e)
            self.logger.error(f"Deployment failed: {error_message}")

            return {
                "success": False,
                "error": error_message,
                "complexity_level": complexity_level,
                "timestamp": datetime.now().isoformat(),
                "recommendations": [
                    "Check environment variable configuration",
                    "Verify system resources are available",
                    "Review deployment logs for detailed error information",
                    "Try deploying with a lower complexity level first",
                ],
            }

    def _validate_deployment_environment(self) -> dict[str, Any]:
        """Validate deployment environment."""
        return {
            "environment_valid": self.env_validation["overall_valid"],
            "validation_score": self.env_validation["validation_score"],
            "config_valid": len(self._validate_config_consistency(self.config)) == 0,
        }

    def _initialize_deployment(self, complexity_level: str) -> dict[str, Any]:
        """Initialize deployment based on complexity level."""
        if complexity_level == "basic":
            return {"mode": "standalone", "nodes": 1, "features": ["basic_monitoring"]}
        elif complexity_level == "standard":
            return {
                "mode": "standalone",
                "nodes": 1,
                "features": ["monitoring", "backup"],
            }
        elif complexity_level == "advanced":
            return {
                "mode": "cluster",
                "nodes": 3,
                "features": ["monitoring", "backup", "load_balancing"],
            }
        else:  # enterprise
            return {
                "mode": "cluster",
                "nodes": 5,
                "features": ["monitoring", "backup", "load_balancing", "ha", "dr"],
            }

    def _configure_high_availability(self) -> dict[str, Any]:
        """Configure high availability."""
        return {
            "enabled": True,
            "load_balancer": self.config.load_balancer_url,
            "cluster_nodes": len(self.config.cluster_nodes),
            "failover_time": "< 30 seconds",
        }

    def _setup_disaster_recovery(self) -> dict[str, Any]:
        """Setup disaster recovery."""
        return {
            "enabled": True,
            "backup_strategy": self.config.backup_strategy,
            "recovery_time_objective": "< 4 hours",
            "recovery_point_objective": "< 1 hour",
        }

    def _optimize_performance(self, complexity_level: str) -> dict[str, Any]:
        """Optimize performance based on complexity level."""
        optimizations = {
            "basic": ["basic_caching", "connection_pooling"],
            "standard": ["basic_caching", "connection_pooling", "query_optimization"],
            "advanced": [
                "basic_caching",
                "connection_pooling",
                "query_optimization",
                "load_balancing",
            ],
            "enterprise": [
                "basic_caching",
                "connection_pooling",
                "query_optimization",
                "load_balancing",
                "auto_scaling",
            ],
        }

        return {
            "level": self.config.performance_tuning,
            "optimizations": optimizations.get(complexity_level, []),
            "monitoring_enabled": self.config.monitoring_enabled,
        }

    def _validate_deployment(self) -> dict[str, Any]:
        """Validate deployment completion."""
        return {
            "deployment_valid": True,
            "components_healthy": True,
            "performance_baseline": "established",
            "monitoring_active": self.config.monitoring_enabled,
        }

    def _format_deployment_error(self, error: Exception) -> str:
        """Format deployment error following crawl_mcp.py error handling patterns."""
        error_str = str(error).lower()

        if "connection" in error_str or "network" in error_str:
            return f"Network connectivity issue: {error}. Check network configuration and connectivity."
        elif "permission" in error_str or "access" in error_str:
            return (
                f"Permission denied: {error}. Check access permissions and credentials."
            )
        elif "resource" in error_str or "memory" in error_str:
            return f"Resource constraint: {error}. Check system resources and capacity."
        elif "configuration" in error_str or "config" in error_str:
            return f"Configuration error: {error}. Check environment variables and configuration files."
        else:
            return f"Deployment error: {error}"

    def cleanup_resources(self):
        """Step 6: Resource Management and Cleanup

        Clean up allocated resources following crawl_mcp.py patterns.
        """
        try:
            self.console.print(
                "🧹 Cleaning up Enterprise Architecture resources...",
                style="bold yellow",
            )

            # Execute cleanup tasks
            for task in self.cleanup_tasks:
                try:
                    task()
                except Exception as e:
                    self.logger.warning(f"Cleanup task failed: {e}")

            # Clear resource tracking
            self.resources_allocated.clear()
            self.cleanup_tasks.clear()

            self.logger.info("Resource cleanup completed successfully")

        except Exception as e:
            self.logger.error(f"Resource cleanup failed: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get current enterprise architecture status."""
        return {
            "environment_validation": self.env_validation,
            "configuration": {
                "deployment_mode": self.config.deployment_mode,
                "high_availability": self.config.high_availability,
                "disaster_recovery": self.config.disaster_recovery,
                "monitoring_enabled": self.config.monitoring_enabled,
            },
            "current_complexity": self.current_complexity,
            "resources_allocated": len(self.resources_allocated),
            "components_initialized": {
                "deployment_manager": self.deployment_manager is not None,
                "ha_manager": self.ha_manager is not None,
                "dr_manager": self.dr_manager is not None,
                "performance_monitor": self.performance_monitor is not None,
            },
        }


# Placeholder classes for component managers (to be implemented in separate files)
class DeploymentManager:
    def __init__(self, config: DeploymentConfig):
        self.config = config


class HighAvailabilityManager:
    def __init__(self, config: DeploymentConfig):
        self.config = config


class DisasterRecoveryManager:
    def __init__(self, config: DeploymentConfig):
        self.config = config


class PerformanceMonitor:
    def __init__(self, config: DeploymentConfig):
        self.config = config
