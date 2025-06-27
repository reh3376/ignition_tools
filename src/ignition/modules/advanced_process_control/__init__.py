"""Phase 15: Advanced Process Control Suite Module.

This module implements comprehensive Advanced Process Control (APC) capabilities
with automated tuning, real-time analytics, and multi-loop coordination.

Following crawl_mcp.py methodology:
- Step 1: Environment validation with comprehensive checks
- Step 2: Input validation using Pydantic models
- Step 3: Comprehensive error handling with user-friendly messages
- Step 4: Modular testing with progressive complexity
- Step 5: Progressive complexity with safety guarantees
- Step 6: Resource management with async context managers

Author: IGN Scripts Development Team
Version: 15.0.0
"""

import logging
import os
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Module version
__version__ = "15.0.0"

# Environment validation flag
_environment_validated = False


def validate_environment() -> dict[str, Any]:
    """Validate Phase 15 Advanced Process Control environment.

    Returns:
        dict: Environment validation results
    """
    global _environment_validated

    results = {"valid": True, "issues": [], "dependencies": {}, "configuration": {}}

    try:
        # Check required dependencies
        dependencies = {
            "numpy": ">=1.21.0",
            "scipy": ">=1.7.0",
            "pandas": ">=1.3.0",
            "scikit-learn": ">=1.0.0",
            "asyncua": ">=1.0.0",
        }

        for dep, version in dependencies.items():
            try:
                __import__(dep)
                results["dependencies"][dep] = "✅ Available"
            except ImportError:
                results["valid"] = False
                results["issues"].append(f"Missing dependency: {dep} {version}")
                results["dependencies"][dep] = "❌ Missing"

        # Check environment variables
        required_env_vars = [
            "MPC_CONTROLLER_ENABLED",
            "APC_AUTO_TUNING_ENABLED",
            "APC_MULTI_LOOP_COORDINATION",
            "APC_ANALYTICS_ENABLED",
        ]

        for var in required_env_vars:
            value = os.getenv(var)
            if value:
                results["configuration"][var] = f"✅ {value}"
            else:
                results["configuration"][var] = "⚠️ Not set (using defaults)"

        # Check for MPC framework integration
        try:
            from src.ignition.modules.mpc_framework import mpc_controller

            results["mpc_integration"] = "✅ MPC Framework available"
        except ImportError:
            results["valid"] = False
            results["issues"].append(
                "MPC Framework not available - required for Phase 15"
            )
            results["mpc_integration"] = "❌ MPC Framework missing"

        if results["valid"]:
            _environment_validated = True
            logger.info("✅ Phase 15 Advanced Process Control environment validated")
        else:
            logger.warning(f"⚠️ Environment validation issues: {results['issues']}")

    except Exception as e:
        results["valid"] = False
        results["issues"].append(f"Environment validation error: {e!s}")
        logger.error(f"❌ Environment validation failed: {e}")

    return results


# Lazy import of main components to avoid import errors
def get_auto_tuning_system():
    """Get the automated tuning system."""
    if not _environment_validated:
        validate_environment()

    from .automated_tuning_system import AutomatedTuningSystem

    return AutomatedTuningSystem


def get_multi_loop_coordinator():
    """Get the multi-loop coordination system."""
    if not _environment_validated:
        validate_environment()

    from .multi_loop_coordinator import MultiLoopCoordinator

    return MultiLoopCoordinator


def get_analytics_engine():
    """Get the real-time analytics engine."""
    if not _environment_validated:
        validate_environment()

    from .analytics_engine import AnalyticsEngine

    return AnalyticsEngine


# Export main classes
__all__ = [
    "__version__",
    "get_analytics_engine",
    "get_auto_tuning_system",
    "get_multi_loop_coordinator",
    "validate_environment",
]
