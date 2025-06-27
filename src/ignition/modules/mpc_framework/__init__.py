"""Phase 14: MPC Framework & Production Control 🎛️.

This module implements a comprehensive Model Predictive Control (MPC) framework
with advanced production control capabilities for Ignition systems.

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Input validation using Pydantic models
- Step 3: Comprehensive error handling with user-friendly messages
- Step 4: Modular testing with progressive complexity
- Step 5: Progressive complexity deployment
- Step 6: Resource management with proper cleanup

Key Components:
- Production MPC Controller with real-time optimization
- Safety System Integration with emergency procedures
- Alarm Management System with escalation
- Performance Monitoring with analytics
- Advanced Control Strategies (PID, Cascade, Feedforward)
- Production Scheduling and Optimization

Author: IGN Scripts Development Team
Version: 14.0.0
Phase: 14 - MPC Framework & Production Control
"""

from .alarm_manager import (
    AlarmConfiguration,
    AlarmDefinition,
    AlarmPriority,
    AlarmState,
    NotificationMethod,
    NotificationRule,
    ProductionAlarmManager,
    format_alarm_error,
    validate_alarm_environment,
)
from .control_strategies import (
    ControlStrategy,
    ControlStrategyConfig,
    cleanup_control_strategies,
    create_default_strategy_config,
    format_control_strategies_error,
    get_available_strategies,
    validate_control_strategies_environment,
)
from .mpc_cli import MPCFrameworkCLI
from .mpc_controller import ProductionMPCController
from .performance_monitor import ProductionPerformanceMonitor
from .production_scheduler import ProductionScheduler
from .safety_system import ProductionSafetySystem

__all__ = [
    "ControlStrategy",
    "ControlStrategyConfig",
    "MPCFrameworkCLI",
    "ProductionAlarmManager",
    "ProductionMPCController",
    "ProductionPerformanceMonitor",
    "ProductionSafetySystem",
    "ProductionScheduler",
]

__version__ = "14.0.0"
__phase__ = "Phase 14: MPC Framework & Production Control"
