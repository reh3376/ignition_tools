#!/usr/bin/env python3
"""Base Specialized Agent for Phase 16.2 Industry-Specific SME Modules.

Following crawl_mcp.py methodology for systematic development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Self

from dotenv import load_dotenv

from src.ignition.modules.sme_agent.multi_domain_architecture import (
    AgentTask,
    BaseDomainAgent,
    DomainType,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BaseSpecializedAgent(BaseDomainAgent, ABC):
    """Base class for specialized industry-specific SME agents."""

    def __init__(
        self: Self,
        agent_id: str,
        domain: DomainType,
        industry_type: str,
        max_concurrent_tasks: int = 3,
    ):
        """Initialize Base Specialized Agent.

        Args:
            agent_id: Unique identifier for the agent
            domain: Domain type from DomainType enum
            industry_type: Specific industry specialization
            max_concurrent_tasks: Maximum concurrent tasks (default: 3 for specialized agents)
        """
        super().__init__(
            agent_id=agent_id, domain=domain, max_concurrent_tasks=max_concurrent_tasks
        )

        self.industry_type = industry_type
        self.specialized_knowledge_areas: dict[str, dict[str, Any]] = {}
        self.regulatory_frameworks: list[str] = []
        self.process_templates: dict[str, dict[str, Any]] = {}
        self.safety_protocols: dict[str, list[str]] = {}

        # Initialize specialized components
        self._initialize_specialized_knowledge()
        self._initialize_regulatory_frameworks()
        self._initialize_process_templates()
        self._initialize_safety_protocols()

        self.logger.info(
            f"Initialized Specialized Agent: {agent_id} for {industry_type}"
        )

    def validate_environment(self: Self) -> dict[str, Any]:
        """Step 1: Environment Validation First."""
        validation_result = super().validate_environment()

        # Add specialized environment validation
        specialized_vars = [
            f"{self.industry_type.upper()}_KNOWLEDGE_BASE_PATH",
            f"{self.industry_type.upper()}_REGULATORY_DB_PATH",
            f"{self.industry_type.upper()}_PROCESS_LIBRARY_PATH",
        ]

        for var in specialized_vars:
            value = os.getenv(var)
            if value is None:
                validation_result["warnings"].append(
                    f"Optional specialized variable {var} not set"
                )
            else:
                validation_result["config"][var] = value

        # Validate specialized knowledge areas
        validation_result["specialized_validation"] = {
            "industry_type": self.industry_type,
            "knowledge_areas_count": len(self.specialized_knowledge_areas),
            "regulatory_frameworks_count": len(self.regulatory_frameworks),
            "process_templates_count": len(self.process_templates),
            "safety_protocols_count": len(self.safety_protocols),
        }

        return validation_result

    @abstractmethod
    def _initialize_specialized_knowledge(self: Self) -> None:
        """Initialize industry-specific knowledge areas."""
        pass

    @abstractmethod
    def _initialize_regulatory_frameworks(self: Self) -> None:
        """Initialize regulatory compliance frameworks."""
        pass

    @abstractmethod
    def _initialize_process_templates(self: Self) -> None:
        """Initialize industry-specific process templates."""
        pass

    @abstractmethod
    def _initialize_safety_protocols(self: Self) -> None:
        """Initialize industry-specific safety protocols."""
        pass

    @abstractmethod
    async def process_specialized_task(self: Self, task: AgentTask) -> dict[str, Any]:
        """Process industry-specific task with specialized knowledge."""
        pass

    async def assign_task(self: Self, task: AgentTask) -> bool:
        """Assign task to specialized agent with enhanced validation."""
        try:
            # Step 2: Input validation
            if not task or not hasattr(task, "task_id"):
                self.logger.error("Invalid task provided to specialized agent")
                return False

            if len(self.active_tasks) >= self.max_concurrent_tasks:
                self.logger.warning(f"Specialized agent {self.agent_id} at capacity")
                return False

            # Validate task compatibility with specialization
            if not self._validate_task_compatibility(task):
                self.logger.warning(
                    f"Task {task.task_id} not compatible with {self.industry_type} specialization"
                )
                return False

            self.active_tasks[task.task_id] = task
            task.assigned_agent = self.agent_id
            task.status = "assigned"

            asyncio.create_task(self._execute_specialized_task(task))
            return True

        except Exception as e:
            self.logger.error(f"Error assigning specialized task {task.task_id}: {e}")
            return False

    def _validate_task_compatibility(self: Self, task: AgentTask) -> bool:
        """Validate if task is compatible with this specialized agent."""
        try:
            # Check if task description contains relevant keywords
            task_description = getattr(task, "description", "").lower()
            task_type = getattr(task, "task_type", "").lower()

            # Check against specialized knowledge areas
            for _knowledge_area, details in self.specialized_knowledge_areas.items():
                keywords = details.get("keywords", [])
                if any(
                    keyword.lower() in task_description or keyword.lower() in task_type
                    for keyword in keywords
                ):
                    return True

            # Check against industry type
            return bool(
                self.industry_type.lower() in task_description
                or self.industry_type.lower() in task_type
            )

        except Exception as e:
            self.logger.error(f"Error validating task compatibility: {e}")
            return False

    async def _execute_specialized_task(self: Self, task: AgentTask) -> None:
        """Execute specialized task with comprehensive error handling."""
        try:
            task.status = "processing"

            # Process with specialized knowledge
            result = await self.process_specialized_task(task)

            # Add specialized metadata
            result["specialization"] = {
                "industry_type": self.industry_type,
                "agent_id": self.agent_id,
                "knowledge_areas_applied": self._get_applied_knowledge_areas(task),
                "regulatory_considerations": self._get_regulatory_considerations(task),
                "safety_protocols_applied": self._get_safety_protocols_applied(task),
            }

            task.result = result
            task.status = "completed" if result.get("success", False) else "failed"
            task.completed_at = datetime.now()

            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

        except Exception as e:
            # Step 3: Comprehensive error handling
            task.status = "failed"
            task.result = {
                "success": False,
                "error": f"Specialized processing failed: {e!s}",
                "specialization": {
                    "industry_type": self.industry_type,
                    "agent_id": self.agent_id,
                },
            }
            task.completed_at = datetime.now()

            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

            self.logger.error(
                f"Specialized task execution failed for {task.task_id}: {e}"
            )

    def _get_applied_knowledge_areas(self: Self, task: AgentTask) -> list[str]:
        """Determine which knowledge areas were applied to the task."""
        applied_areas = []
        task_description = getattr(task, "description", "").lower()

        for area_name, details in self.specialized_knowledge_areas.items():
            keywords = details.get("keywords", [])
            if any(keyword.lower() in task_description for keyword in keywords):
                applied_areas.append(area_name)

        return applied_areas

    def _get_regulatory_considerations(self: Self, task: AgentTask) -> list[str]:
        """Determine relevant regulatory considerations for the task."""
        relevant_frameworks = []
        task_description = getattr(task, "description", "").lower()

        for framework in self.regulatory_frameworks:
            if any(
                keyword in task_description for keyword in framework.lower().split()
            ):
                relevant_frameworks.append(framework)

        return relevant_frameworks

    def _get_safety_protocols_applied(self: Self, task: AgentTask) -> list[str]:
        """Determine which safety protocols apply to the task."""
        applicable_protocols = []
        task_description = getattr(task, "description", "").lower()

        for protocol_category, protocols in self.safety_protocols.items():
            if any(
                keyword in task_description
                for keyword in protocol_category.lower().split()
            ):
                applicable_protocols.extend(protocols)

        return applicable_protocols

    def get_specialization_summary(self: Self) -> dict[str, Any]:
        """Get comprehensive summary of agent specialization."""
        return {
            "agent_id": self.agent_id,
            "industry_type": self.industry_type,
            "domain": self.domain.value,
            "knowledge_areas": list(self.specialized_knowledge_areas.keys()),
            "regulatory_frameworks": self.regulatory_frameworks,
            "process_templates": list(self.process_templates.keys()),
            "safety_protocols": list(self.safety_protocols.keys()),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "current_active_tasks": len(self.active_tasks),
        }
