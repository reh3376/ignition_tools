#!/usr/bin/env python3
"""Agent Coordination Framework for Phase 16 Multi-Domain Architecture

Following crawl_mcp.py methodology for systematic development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Multi-Agent System Features:
- Agent communication protocols
- Task delegation and coordination
- Conflict resolution mechanisms
- Load balancing across agents
- Performance monitoring and optimization
- Scalability and fault tolerance
"""

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Self

from dotenv import load_dotenv

from .multi_domain_architecture import (
    AgentStatus,
    AgentTask,
    BaseDomainAgent,
    DomainType,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class CoordinationStrategy(Enum):
    """Task coordination strategies."""
    
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    EXPERTISE_BASED = "expertise_based"
    PRIORITY_BASED = "priority_based"


class TaskStatus(Enum):
    """Task status in coordination system."""
    
    QUEUED = "queued"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CoordinationMessage:
    """Message for agent communication."""
    
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_agent: str = ""
    receiver_agent: str = ""
    message_type: str = "info"
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0
    
    def to_dict(self: Self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_agent": self.sender_agent,
            "receiver_agent": self.receiver_agent,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
        }


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for agents."""
    
    agent_id: str
    domain: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_processing_time: float = 0.0
    current_load: int = 0
    availability: float = 1.0
    last_activity: datetime = field(default_factory=datetime.now)
    
    def success_rate(self: Self) -> float:
        """Calculate success rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks
    
    def to_dict(self: Self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "average_processing_time": self.average_processing_time,
            "current_load": self.current_load,
            "availability": self.availability,
            "success_rate": self.success_rate(),
            "last_activity": self.last_activity.isoformat(),
        }


class AgentCoordinationFramework:
    """Multi-Agent Coordination Framework for SME Agents.
    
    Following crawl_mcp.py methodology for systematic implementation.
    """
    
    def __init__(self: Self, coordination_strategy: CoordinationStrategy = CoordinationStrategy.EXPERTISE_BASED):
        """Initialize Agent Coordination Framework.
        
        Args:
            coordination_strategy: Strategy for task coordination
        """
        # Step 1: Environment Validation First
        self.logger = logging.getLogger(__name__)
        self.coordination_strategy = coordination_strategy
        self.initialized = False
        
        # Agent management
        self.registered_agents: Dict[str, BaseDomainAgent] = {}
        self.domain_agents: Dict[DomainType, List[str]] = {
            DomainType.ELECTRICAL: [],
            DomainType.MECHANICAL: [],
            DomainType.CHEMICAL_PROCESS: [],
        }
        
        # Task management
        self.task_queue: List[AgentTask] = []
        self.active_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: List[AgentTask] = []
        self.failed_tasks: List[AgentTask] = []
        
        # Communication system
        self.message_queue: List[CoordinationMessage] = []
        self.communication_log: List[CoordinationMessage] = []
        
        # Performance monitoring
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        
        # Configuration
        self.max_queue_size = int(os.getenv("SME_AGENT_MAX_QUEUE_SIZE", "100"))
        self.task_timeout = int(os.getenv("SME_AGENT_TASK_TIMEOUT", "300"))
        self.heartbeat_interval = int(os.getenv("SME_AGENT_HEARTBEAT_INTERVAL", "30"))
        
        # Statistics
        self.coordination_stats = {
            "total_tasks_coordinated": 0,
            "successful_coordinations": 0,
            "failed_coordinations": 0,
            "average_coordination_time": 0.0,
            "active_agents": 0,
            "last_coordination": datetime.now(),
        }
        
        self.logger.info(f"Initialized Agent Coordination Framework with {coordination_strategy.value} strategy")
    
    def validate_environment(self: Self) -> Dict[str, Any]:
        """Step 1: Environment Validation First."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "config": {},
        }
        
        # Check required environment variables
        required_vars = [
            "SME_AGENT_MAX_QUEUE_SIZE",
            "SME_AGENT_TASK_TIMEOUT",
            "SME_AGENT_HEARTBEAT_INTERVAL",
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                validation_result["warnings"].append(f"Optional environment variable {var} not set, using default")
            else:
                validation_result["config"][var] = value
        
        # Validate configuration values
        try:
            if int(os.getenv("SME_AGENT_MAX_QUEUE_SIZE", "100")) <= 0:
                validation_result["errors"].append("SME_AGENT_MAX_QUEUE_SIZE must be positive")
                validation_result["valid"] = False
        except ValueError:
            validation_result["errors"].append("SME_AGENT_MAX_QUEUE_SIZE must be a valid integer")
            validation_result["valid"] = False
        
        return validation_result
    
    def validate_input(self: Self, task: AgentTask) -> bool:
        """Step 2: Comprehensive Input Validation.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        if not isinstance(task, AgentTask):
            self.logger.error("Task must be an AgentTask instance")
            return False
        
        if not task.query or not isinstance(task.query, str):
            self.logger.error("Task query must be a non-empty string")
            return False
        
        if task.query.strip() == "":
            self.logger.error("Task query cannot be empty or whitespace only")
            return False
        
        if len(task.query) > 2000:
            self.logger.error("Task query too long (max 2000 characters)")
            return False
        
        if not isinstance(task.domain, DomainType):
            self.logger.error("Task domain must be a valid DomainType")
            return False
        
        if not isinstance(task.context, dict):
            self.logger.error("Task context must be a dictionary")
            return False
        
        return True
    
    def handle_error(self: Self, error: Exception, context: str) -> Dict[str, Any]:
        """Step 3: Error Handling with User-Friendly Messages.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            
        Returns:
            User-friendly error response
        """
        error_message = f"Coordination framework error: {context}"
        self.logger.error(f"{error_message}: {error!s}")
        
        # Update statistics
        self.coordination_stats["failed_coordinations"] += 1
        
        # Create user-friendly error response
        return {
            "success": False,
            "error": error_message,
            "suggestion": "Please check task format and try again",
            "timestamp": datetime.now().isoformat(),
            "coordination_strategy": self.coordination_strategy.value,
        }
    
    async def register_agent(self: Self, agent: BaseDomainAgent) -> bool:
        """Register a domain-specific agent with the coordination framework.
        
        Args:
            agent: Domain agent to register
            
        Returns:
            True if registration successful
        """
        try:
            # Validate agent
            if not isinstance(agent, BaseDomainAgent):
                self.logger.error("Agent must be a BaseDomainAgent instance")
                return False
            
            if agent.agent_id in self.registered_agents:
                self.logger.warning(f"Agent {agent.agent_id} already registered")
                return False
            
            # Register agent
            self.registered_agents[agent.agent_id] = agent
            self.domain_agents[agent.domain].append(agent.agent_id)
            
            # Initialize performance metrics
            self.agent_metrics[agent.agent_id] = AgentPerformanceMetrics(
                agent_id=agent.agent_id,
                domain=agent.domain.value,
            )
            
            # Update statistics
            self.coordination_stats["active_agents"] = len(self.registered_agents)
            
            self.logger.info(f"Registered agent {agent.agent_id} for domain {agent.domain.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent: {e}")
            return False
    
    async def submit_task(self: Self, task: AgentTask) -> Dict[str, Any]:
        """Submit task for coordination and processing.
        
        Args:
            task: Task to submit
            
        Returns:
            Task submission result
        """
        start_time = time.time()
        
        try:
            # Step 2: Comprehensive Input Validation
            if not self.validate_input(task):
                return self.handle_error(
                    ValueError("Invalid task format"),
                    "task validation"
                )
            
            # Check queue capacity
            if len(self.task_queue) >= self.max_queue_size:
                return self.handle_error(
                    RuntimeError("Task queue at maximum capacity"),
                    "queue management"
                )
            
            # Add task to queue
            task.status = TaskStatus.QUEUED.value
            self.task_queue.append(task)
            
            # Attempt immediate assignment
            assignment_result = await self._assign_task_to_agent(task)
            
            # Update statistics
            self.coordination_stats["total_tasks_coordinated"] += 1
            self.coordination_stats["last_coordination"] = datetime.now()
            
            coordination_time = time.time() - start_time
            
            return {
                "success": True,
                "task_id": task.task_id,
                "status": task.status,
                "assigned_agent": task.assigned_agent,
                "coordination_time": coordination_time,
                "queue_position": len(self.task_queue) if not assignment_result else 0,
            }
            
        except Exception as e:
            return self.handle_error(e, "task submission")
    
    async def _assign_task_to_agent(self: Self, task: AgentTask) -> bool:
        """Assign task to appropriate agent based on coordination strategy.
        
        Args:
            task: Task to assign
            
        Returns:
            True if task assigned successfully
        """
        try:
            # Get available agents for domain
            available_agents = self._get_available_agents(task.domain)
            
            if not available_agents:
                self.logger.warning(f"No available agents for domain {task.domain.value}")
                return False
            
            # Select agent based on coordination strategy
            selected_agent = self._select_agent(available_agents, task)
            
            if not selected_agent:
                self.logger.warning("No suitable agent selected")
                return False
            
            # Assign task to agent
            assignment_success = await selected_agent.assign_task(task)
            
            if assignment_success:
                # Remove from queue and add to active tasks
                if task in self.task_queue:
                    self.task_queue.remove(task)
                self.active_tasks[task.task_id] = task
                
                # Update agent metrics
                if selected_agent.agent_id in self.agent_metrics:
                    metrics = self.agent_metrics[selected_agent.agent_id]
                    metrics.current_load += 1
                    metrics.last_activity = datetime.now()
                
                self.logger.info(f"Task {task.task_id} assigned to agent {selected_agent.agent_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to assign task: {e}")
            return False
    
    def _get_available_agents(self: Self, domain: DomainType) -> List[BaseDomainAgent]:
        """Get available agents for specified domain.
        
        Args:
            domain: Domain type
            
        Returns:
            List of available agents
        """
        available_agents = []
        
        for agent_id in self.domain_agents.get(domain, []):
            agent = self.registered_agents.get(agent_id)
            if agent and agent.status == AgentStatus.ACTIVE:
                # Check if agent has capacity
                if len(agent.active_tasks) < agent.max_concurrent_tasks:
                    available_agents.append(agent)
        
        return available_agents
    
    def _select_agent(self: Self, available_agents: List[BaseDomainAgent], task: AgentTask) -> Optional[BaseDomainAgent]:
        """Select best agent based on coordination strategy.
        
        Args:
            available_agents: List of available agents
            task: Task to assign
            
        Returns:
            Selected agent or None
        """
        if not available_agents:
            return None
        
        if self.coordination_strategy == CoordinationStrategy.ROUND_ROBIN:
            return self._select_round_robin(available_agents)
        elif self.coordination_strategy == CoordinationStrategy.LOAD_BALANCED:
            return self._select_load_balanced(available_agents)
        elif self.coordination_strategy == CoordinationStrategy.EXPERTISE_BASED:
            return self._select_expertise_based(available_agents, task)
        else:
            # Default to first available
            return available_agents[0]
    
    def _select_round_robin(self: Self, available_agents: List[BaseDomainAgent]) -> BaseDomainAgent:
        """Select agent using round-robin strategy."""
        # Simple round-robin based on total tasks
        min_tasks = float('inf')
        selected_agent = available_agents[0]
        
        for agent in available_agents:
            metrics = self.agent_metrics.get(agent.agent_id)
            if metrics and metrics.total_tasks < min_tasks:
                min_tasks = metrics.total_tasks
                selected_agent = agent
        
        return selected_agent
    
    def _select_load_balanced(self: Self, available_agents: List[BaseDomainAgent]) -> BaseDomainAgent:
        """Select agent using load balancing strategy."""
        # Select agent with lowest current load
        min_load = float('inf')
        selected_agent = available_agents[0]
        
        for agent in available_agents:
            current_load = len(agent.active_tasks)
            if current_load < min_load:
                min_load = current_load
                selected_agent = agent
        
        return selected_agent
    
    def _select_expertise_based(self: Self, available_agents: List[BaseDomainAgent], task: AgentTask) -> BaseDomainAgent:
        """Select agent based on expertise and performance."""
        # Select agent with highest success rate and availability
        best_score = -1
        selected_agent = available_agents[0]
        
        for agent in available_agents:
            metrics = self.agent_metrics.get(agent.agent_id)
            if metrics:
                # Calculate score based on success rate and availability
                score = metrics.success_rate() * metrics.availability
                if score > best_score:
                    best_score = score
                    selected_agent = agent
        
        return selected_agent
    
    async def process_task_queue(self: Self) -> Dict[str, Any]:
        """Process pending tasks in queue.
        
        Returns:
            Processing results
        """
        try:
            processed_tasks = 0
            failed_assignments = 0
            
            # Process tasks in queue
            tasks_to_process = self.task_queue.copy()
            
            for task in tasks_to_process:
                assignment_result = await self._assign_task_to_agent(task)
                if assignment_result:
                    processed_tasks += 1
                else:
                    failed_assignments += 1
            
            return {
                "success": True,
                "processed_tasks": processed_tasks,
                "failed_assignments": failed_assignments,
                "remaining_queue_size": len(self.task_queue),
                "active_tasks": len(self.active_tasks),
            }
            
        except Exception as e:
            return self.handle_error(e, "queue processing")
    
    def get_coordination_status(self: Self) -> Dict[str, Any]:
        """Get coordination framework status."""
        return {
            "coordination_strategy": self.coordination_strategy.value,
            "registered_agents": len(self.registered_agents),
            "active_agents": sum(1 for agent in self.registered_agents.values() 
                               if agent.status == AgentStatus.ACTIVE),
            "task_queue_size": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "statistics": self.coordination_stats.copy(),
            "agent_metrics": {agent_id: metrics.to_dict() 
                            for agent_id, metrics in self.agent_metrics.items()},
        }
    
    def cleanup(self: Self) -> None:
        """Step 6: Resource Management and Cleanup."""
        try:
            # Cancel all active tasks
            for task_id, task in self.active_tasks.items():
                task.status = TaskStatus.CANCELLED.value
                self.logger.info(f"Cancelled task {task_id}")
            
            # Cleanup all registered agents
            for agent_id, agent in self.registered_agents.items():
                agent.cleanup()
                self.logger.info(f"Cleaned up agent {agent_id}")
            
            # Clear all data structures
            self.task_queue.clear()
            self.active_tasks.clear()
            self.registered_agents.clear()
            self.domain_agents = {domain: [] for domain in DomainType}
            self.agent_metrics.clear()
            
            self.logger.info("Agent Coordination Framework cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Export classes
__all__ = [
    "CoordinationStrategy",
    "TaskStatus",
    "CoordinationMessage",
    "AgentPerformanceMetrics",
    "AgentCoordinationFramework",
] 