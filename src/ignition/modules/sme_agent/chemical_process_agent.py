#!/usr/bin/env python3
"""Chemical Process Engineering Domain Agent for Phase 16 Multi-Domain Architecture.

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
import time
from datetime import datetime
from typing import Any, Self

from dotenv import load_dotenv

from .multi_domain_architecture import (
    AgentTask,
    BaseDomainAgent,
    DomainType,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ChemicalProcessAgent(BaseDomainAgent):
    """Chemical Process Engineering Domain Agent."""

    def __init__(self: Self, agent_id: str = "chemical_process_agent"):
        """Initialize Chemical Process Engineering Agent."""
        super().__init__(
            agent_id=agent_id,
            domain=DomainType.CHEMICAL_PROCESS,
            max_concurrent_tasks=5,
        )

        self.expertise_areas = {
            "distillation": {
                "description": "Distillation processes and column design",
                "keywords": [
                    "distillation",
                    "column",
                    "separation",
                    "reflux",
                    "reboiler",
                ],
                "complexity_level": "advanced",
            },
            "process_control": {
                "description": "Process control and automation systems",
                "keywords": ["control", "pid", "automation", "setpoint", "feedback"],
                "complexity_level": "standard",
            },
            "heat_exchangers": {
                "description": "Heat exchanger design and optimization",
                "keywords": ["heat", "exchanger", "thermal", "transfer", "efficiency"],
                "complexity_level": "standard",
            },
            "safety_systems": {
                "description": "Process safety and hazard analysis",
                "keywords": ["safety", "hazard", "risk", "protection", "emergency"],
                "complexity_level": "basic",
            },
        }

        self.knowledge_base_path = os.getenv(
            "CHEMICAL_KNOWLEDGE_BASE_PATH", "data/chemical_process"
        )
        self.logger.info(f"Initialized Chemical Process Agent: {agent_id}")

    def validate_environment(self: Self) -> dict[str, Any]:
        """Step 1: Environment Validation First."""
        validation_result = super().validate_environment()

        chemical_vars = ["CHEMICAL_KNOWLEDGE_BASE_PATH"]
        for var in chemical_vars:
            value = os.getenv(var)
            if value is None:
                validation_result["warnings"].append(
                    f"Optional environment variable {var} not set"
                )
            else:
                validation_result["config"][var] = value

        return validation_result

    async def process_chemical_task(self: Self, task: AgentTask) -> dict[str, Any]:
        """Process chemical process engineering specific task."""
        start_time = time.time()

        try:
            analysis = {
                "task_type": "chemical_process",
                "analysis": {
                    "domain": "Chemical Process Engineering",
                    "approach": "Systematic chemical process analysis",
                    "considerations": [
                        "Process safety and hazard analysis",
                        "Mass and energy balances",
                        "Separation processes optimization",
                        "Process control and automation",
                    ],
                },
                "recommendations": [
                    "Apply fundamental chemical engineering principles",
                    "Consider process safety and environmental impact",
                    "Optimize for efficiency and product quality",
                    "Implement robust process control systems",
                ],
            }

            return {
                "success": True,
                "analysis": analysis,
                "expertise_applied": "chemical_process",
                "processing_time": time.time() - start_time,
            }

        except Exception as e:
            self.logger.error(f"Error processing chemical task: {e}")
            return {
                "success": False,
                "error": f"Processing failed: {e!s}",
                "processing_time": time.time() - start_time,
            }

    async def assign_task(self: Self, task: AgentTask) -> bool:
        """Assign task to chemical process engineering agent."""
        try:
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                return False

            self.active_tasks[task.task_id] = task
            task.assigned_agent = self.agent_id
            task.status = "assigned"

            asyncio.create_task(self._execute_chemical_task(task))
            return True

        except Exception as e:
            self.logger.error(f"Error assigning task {task.task_id}: {e}")
            return False

    async def _execute_chemical_task(self: Self, task: AgentTask) -> None:
        """Execute chemical process engineering task."""
        try:
            task.status = "processing"

            result = await self.process_chemical_task(task)

            task.result = result
            task.status = "completed" if result.get("success", False) else "failed"
            task.completed_at = datetime.now()

            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

        except Exception as e:
            task.status = "failed"
            task.result = {"success": False, "error": str(e)}
            task.completed_at = datetime.now()

            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
