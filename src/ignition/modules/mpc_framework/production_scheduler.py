"""Production Scheduler Module for MPC Framework.

This module provides production scheduling and optimization capabilities.
Following crawl_mcp.py methodology for robust, production-ready implementation.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ScheduleStatus(Enum):
    """Production schedule status."""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class SchedulePriority(Enum):
    """Schedule priority levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class ProductionTask:
    """Production task definition."""

    task_id: str
    name: str
    description: str
    priority: SchedulePriority
    estimated_duration: float  # hours
    required_resources: list[str]
    dependencies: list[str] = field(default_factory=list)
    status: ScheduleStatus = ScheduleStatus.PENDING
    scheduled_start: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None


@dataclass
class ProductionSchedule:
    """Production schedule definition."""

    schedule_id: str
    name: str
    tasks: list[ProductionTask]
    start_time: datetime
    end_time: datetime
    status: ScheduleStatus = ScheduleStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)


def validate_scheduler_environment() -> dict[str, Any]:
    """Validate production scheduler environment following crawl_mcp.py Step 1."""
    logger.info("🔍 Step 1: Environment Validation - Production Scheduler")

    errors = []
    warnings = []

    try:
        # Check basic imports
        import asyncio
        import datetime

        logger.info("✅ DateTime and AsyncIO available for scheduling")
    except ImportError as e:
        errors.append(f"Missing required packages: {e}")

    # Check system resources
    try:
        import psutil

        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        if available_gb < 0.5:
            warnings.append(f"Low memory available: {available_gb:.1f} GB")
        else:
            logger.info(f"✅ System memory: {available_gb:.1f} GB available")
    except ImportError:
        warnings.append("psutil not available for memory monitoring")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "components": ["production_scheduler"],
    }


@dataclass
class ProductionScheduler:
    """Production scheduler with comprehensive scheduling capabilities."""

    # Configuration
    scheduler_name: str = "Production Scheduler"
    max_concurrent_tasks: int = 10

    # Runtime state
    _initialized: bool = field(default=False, init=False)
    _active_schedules: dict[str, ProductionSchedule] = field(
        default_factory=dict, init=False
    )

    def __post_init__(self) -> None:
        """Initialize scheduler after creation."""
        logger.info("📅 Initializing Production Scheduler")

    async def initialize(self) -> dict[str, Any]:
        """Initialize production scheduler with comprehensive validation."""
        logger.info(
            "🔧 Step 1-6: Initializing Production Scheduler (crawl_mcp.py methodology)"
        )

        # Step 1: Environment validation first
        env_validation = validate_scheduler_environment()
        if not env_validation["valid"]:
            return {
                "success": False,
                "error": "Scheduler environment validation failed",
                "details": env_validation["errors"],
            }

        self._initialized = True
        logger.info("✅ Production Scheduler initialized successfully")

        return {
            "success": True,
            "message": "Production scheduler initialized successfully",
            "configuration": {
                "scheduler_name": self.scheduler_name,
                "max_concurrent_tasks": self.max_concurrent_tasks,
            },
        }

    def get_status(self) -> dict[str, Any]:
        """Get scheduler status."""
        return {
            "initialized": self._initialized,
            "active_schedules": len(self._active_schedules),
        }
