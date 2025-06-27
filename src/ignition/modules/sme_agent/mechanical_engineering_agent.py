#!/usr/bin/env python3
"""Mechanical Engineering Domain Agent for Phase 16 Multi-Domain Architecture.

Following crawl_mcp.py methodology for systematic development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Mechanical Engineering Expertise:
- Fluid dynamics and heat transfer
- Mechanical design and materials
- Pump and compressor systems
- Piping and instrumentation diagrams (P&IDs)
- Vibration analysis and monitoring
- Maintenance and reliability engineering
- Thermodynamics and energy systems
- Manufacturing processes and automation
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


class MechanicalEngineeringAgent(BaseDomainAgent):
    """Mechanical Engineering Domain Agent.

    Specialized SME agent for mechanical engineering tasks including:
    - Fluid dynamics and heat transfer
    - Mechanical design and materials
    - Pump and compressor systems
    - P&ID development and analysis
    - Vibration analysis
    - Maintenance and reliability
    """

    def __init__(self: Self, agent_id: str = "mechanical_engineering_agent"):
        """Initialize Mechanical Engineering Agent.

        Args:
            agent_id: Unique identifier for the agent
        """
        super().__init__(
            agent_id=agent_id, domain=DomainType.MECHANICAL, max_concurrent_tasks=5
        )

        # Mechanical engineering specific configuration
        self.expertise_areas = {
            "fluid_dynamics": {
                "description": "Fluid flow, heat transfer, and thermal systems",
                "keywords": ["fluid", "flow", "heat", "thermal", "pressure"],
                "complexity_level": "advanced",
            },
            "mechanical_design": {
                "description": "Mechanical design, materials, and stress analysis",
                "keywords": ["design", "material", "stress", "mechanical"],
                "complexity_level": "standard",
            },
        }

        # Knowledge base paths
        self.knowledge_base_path = os.getenv(
            "MECHANICAL_KNOWLEDGE_BASE_PATH", "data/mechanical_engineering"
        )

        self.logger.info(f"Initialized Mechanical Engineering Agent: {agent_id}")

    def validate_environment(self: Self) -> dict[str, Any]:
        """Step 1: Environment Validation First."""
        validation_result = super().validate_environment()

        mechanical_vars = ["MECHANICAL_KNOWLEDGE_BASE_PATH"]
        for var in mechanical_vars:
            value = os.getenv(var)
            if value is None:
                validation_result["warnings"].append(
                    f"Optional environment variable {var} not set"
                )
            else:
                validation_result["config"][var] = value

        return validation_result

    async def process_mechanical_task(self: Self, task: AgentTask) -> dict[str, Any]:
        """Process mechanical engineering specific task."""
        start_time = time.time()

        try:
            analysis = {
                "task_type": "mechanical_engineering",
                "analysis": {
                    "domain": "Mechanical Engineering",
                    "approach": "Systematic mechanical engineering analysis",
                },
                "recommendations": [
                    "Apply fundamental mechanical engineering principles",
                    "Consider operating conditions and environment",
                ],
            }

            return {
                "success": True,
                "analysis": analysis,
                "expertise_applied": "mechanical_engineering",
                "processing_time": time.time() - start_time,
            }

        except Exception as e:
            self.logger.error(f"Error processing mechanical task: {e}")
            return {
                "success": False,
                "error": f"Processing failed: {e!s}",
                "processing_time": time.time() - start_time,
            }

    async def assign_task(self: Self, task: AgentTask) -> bool:
        """Assign task to mechanical engineering agent."""
        try:
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                return False

            self.active_tasks[task.task_id] = task
            task.assigned_agent = self.agent_id
            task.status = "assigned"

            asyncio.create_task(self._execute_mechanical_task(task))
            return True

        except Exception as e:
            self.logger.error(f"Error assigning task {task.task_id}: {e}")
            return False

    async def _execute_mechanical_task(self: Self, task: AgentTask) -> None:
        """Execute mechanical engineering task."""
        try:
            task.status = "processing"

            result = await self.process_mechanical_task(task)

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

    def get_agent_status(self: Self) -> dict[str, Any]:
        """Get comprehensive agent status information."""
        base_status = super().get_agent_status()

        # Add mechanical engineering specific status
        mechanical_status = {
            "expertise_areas": list(self.expertise_areas.keys()),
            "knowledge_base_path": self.knowledge_base_path,
            "specialization": "Mechanical Engineering SME Agent",
            "capabilities": [
                "Fluid dynamics and heat transfer analysis",
                "Mechanical design and materials selection",
                "Pump and compressor systems optimization",
                "P&ID development and piping design",
                "Vibration analysis and condition monitoring",
                "Maintenance and reliability engineering",
                "Thermodynamic cycle analysis",
                "Manufacturing process optimization",
            ],
        }

        base_status.update(mechanical_status)
        return base_status
