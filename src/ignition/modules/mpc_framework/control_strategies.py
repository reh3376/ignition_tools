"""
Control Strategies Module for MPC Framework

This module provides advanced control strategies and algorithms for the MPC Framework.
Following crawl_mcp.py methodology for robust, production-ready implementation.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ControlStrategy(Enum):
    """Available control strategies."""
    PID = "PID"
    MPC = "MPC"
    ADAPTIVE = "ADAPTIVE"
    ROBUST = "ROBUST"
    FEEDFORWARD = "FEEDFORWARD"


@dataclass
class ControlStrategyConfig:
    """Configuration for control strategies."""
    strategy_type: str
    parameters: Dict[str, Any]
    enabled: bool = True


def validate_control_strategies_environment() -> Dict[str, Any]:
    """Validate control strategies environment following crawl_mcp.py Step 1."""
    logger.info("🔍 Step 1: Environment Validation - Control Strategies")
    
    errors = []
    warnings = []
    
    try:
        # Check basic imports
        import numpy as np
        import scipy.signal
        logger.info("✅ NumPy and SciPy available for control algorithms")
    except ImportError as e:
        errors.append(f"Missing required packages: {e}")
    
    # Check system resources
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        if available_gb < 1.0:
            warnings.append(f"Low memory available: {available_gb:.1f} GB")
        else:
            logger.info(f"✅ System memory: {available_gb:.1f} GB available")
    except ImportError:
        warnings.append("psutil not available for memory monitoring")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "components": ["control_strategies"],
    }


def get_available_strategies() -> List[str]:
    """Get list of available control strategies."""
    return [strategy.value for strategy in ControlStrategy]


def create_default_strategy_config(strategy: str) -> ControlStrategyConfig:
    """Create default configuration for a control strategy."""
    if strategy == "PID":
        return ControlStrategyConfig(
            strategy_type="PID",
            parameters={
                "Kp": 1.0,
                "Ki": 0.1,
                "Kd": 0.01,
                "setpoint": 0.0,
            }
        )
    elif strategy == "MPC":
        return ControlStrategyConfig(
            strategy_type="MPC",
            parameters={
                "prediction_horizon": 10,
                "control_horizon": 3,
                "Q": [[1.0]],
                "R": [[0.1]],
            }
        )
    else:
        return ControlStrategyConfig(
            strategy_type=strategy,
            parameters={}
        )


def format_control_strategies_error(error: Exception, context: str = "") -> str:
    """Format control strategies errors following crawl_mcp.py Step 3."""
    error_str = str(error).lower()
    
    if "import" in error_str:
        return f"Control strategies import error in {context}: Check package installation"
    elif "configuration" in error_str:
        return f"Control strategies configuration error in {context}: {error!s}"
    else:
        return f"Control strategies error in {context}: {error!s}"


# Step 6: Resource Management (crawl_mcp.py methodology)
async def cleanup_control_strategies() -> None:
    """Clean up control strategies resources."""
    try:
        logger.info("✅ Control strategies cleanup completed")
    except Exception as e:
        logger.error(f"❌ Control strategies cleanup error: {e}")


if __name__ == "__main__":
    # Test the module
    result = validate_control_strategies_environment()
    print(f"Control Strategies Environment Validation: {result}")
    
    strategies = get_available_strategies()
    print(f"Available Strategies: {strategies}") 