#!/usr/bin/env python3
"""Multi-Domain Architecture for SME Agent System - Phase 16.1.

Following crawl_mcp.py methodology for systematic development.
"""

import logging
import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Self

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """Engineering domain types for specialized SME agents."""

    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    CHEMICAL_PROCESS = "chemical_process"


class AgentStatus(Enum):
    """Agent status enumeration."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentTask:
    """Task for domain-specific agent processing."""

    query: str
    domain: DomainType
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    assigned_agent: str | None = None
    status: str = "pending"
    result: dict[str, Any] | None = None
    processing_time: float = 0.0
    completed_at: datetime | None = None

    def to_dict(self: Self) -> dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "query": self.query,
            "domain": self.domain.value,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "assigned_agent": self.assigned_agent,
            "status": self.status,
            "result": self.result,
            "processing_time": self.processing_time,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


class BaseDomainAgent(ABC):
    """Base class for domain-specific SME agents."""

    def __init__(
        self: Self, agent_id: str, domain: DomainType, max_concurrent_tasks: int = 5
    ):
        """Initialize domain-specific agent."""
        self.agent_id = agent_id
        self.domain = domain
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logging.getLogger(f"{__name__}.{self.agent_id}")
        self.status = AgentStatus.ACTIVE
        self.initialized = True

        # Task management
        self.active_tasks: dict[str, AgentTask] = {}
        self.completed_tasks: list[AgentTask] = []
        self.failed_tasks: list[AgentTask] = []

        self.logger.info(f"Initialized {domain.value} agent: {self.agent_id}")

    def validate_environment(self: Self) -> dict[str, Any]:
        """Validate agent environment."""
        return {
            "valid": True,
            "errors": [],
            "warnings": [],
            "config": {},
        }

    def handle_error(self: Self, error: Exception, context: str) -> dict[str, Any]:
        """Handle errors with user-friendly messages."""
        error_message = f"Agent {self.agent_id} error: {context}"
        self.logger.error(f"{error_message}: {error!s}")

        return {
            "success": False,
            "error": error_message,
            "suggestion": "Check agent configuration and try again",
            "timestamp": datetime.now().isoformat(),
        }

    async def assign_task(self: Self, task: AgentTask) -> bool:
        """Assign task to this agent."""
        try:
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                self.logger.warning(f"Agent {self.agent_id} at maximum capacity")
                return False

            task.assigned_agent = self.agent_id
            task.status = "assigned"
            self.active_tasks[task.task_id] = task

            self.logger.info(f"Task {task.task_id} assigned to agent {self.agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to assign task: {e}")
            return False

    def get_agent_status(self: Self) -> dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_id": self.agent_id,
            "domain": self.domain.value,
            "status": self.status.value,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
        }

    def cleanup(self: Self) -> None:
        """Cleanup agent resources."""
        try:
            # Cancel all active tasks
            for task_id, task in self.active_tasks.items():
                task.status = "cancelled"
                self.logger.info(f"Cancelled task {task_id}")

            self.active_tasks.clear()
            self.status = AgentStatus.OFFLINE

            self.logger.info(f"Agent {self.agent_id} cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Export classes
__all__ = [
    "AgentStatus",
    "AgentTask",
    "BaseDomainAgent",
    "DomainType",
]
