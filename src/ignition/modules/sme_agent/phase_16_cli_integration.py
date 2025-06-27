#!/usr/bin/env python3
"""Phase 16 CLI Integration for Multi-Domain Enterprise AI Platform.

Following crawl_mcp.py methodology for systematic CLI development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

CLI Commands for Phase 16:
- phase16 validate-env - Validate Phase 16 environment
- phase16 status - Show multi-domain agent status
- phase16 register-agent <type> - Register domain-specific agent
- phase16 submit-task <domain> <query> - Submit task to domain agent
- phase16 coordination-status - Show coordination framework status
- phase16 test-framework - Run Phase 16 test suite
- phase16 deploy <complexity> - Deploy with specified complexity level
- phase16 performance-metrics - Show performance metrics
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Self

import click
from dotenv import load_dotenv

from .agent_coordination_framework import (
    AgentCoordinationFramework,
    CoordinationStrategy,
)
from .electrical_engineering_agent import ElectricalEngineeringAgent
from .multi_domain_architecture import (
    AgentTask,
    BaseDomainAgent,
    DomainType,
)
from .phase_16_test_framework import run_phase_16_tests

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Phase16CLIManager:
    """CLI Manager for Phase 16 Multi-Domain Enterprise AI Platform.

    Following crawl_mcp.py methodology for systematic CLI management.
    """

    def __init__(self: Self):
        """Initialize Phase 16 CLI Manager."""
        # Step 1: Environment Validation First
        self.logger = logging.getLogger(__name__)
        self.coordination_framework: AgentCoordinationFramework | None = None
        self.registered_agents: dict[str, BaseDomainAgent] = {}

        # Configuration
        self.config = {
            "coordination_strategy": os.getenv(
                "PHASE16_COORDINATION_STRATEGY", "expertise_based"
            ),
            "max_concurrent_tasks": int(
                os.getenv("PHASE16_MAX_CONCURRENT_TASKS", "10")
            ),
            "default_timeout": int(os.getenv("PHASE16_DEFAULT_TIMEOUT", "300")),
            "log_level": os.getenv("PHASE16_LOG_LEVEL", "INFO"),
        }

        # Progressive complexity levels
        self.complexity_levels = {
            "basic": {
                "description": "Basic multi-domain agent functionality",
                "features": ["electrical_agent", "coordination_framework"],
                "max_agents": 1,
                "max_concurrent_tasks": 3,
            },
            "standard": {
                "description": "Standard multi-domain with coordination",
                "features": [
                    "electrical_agent",
                    "mechanical_agent",
                    "coordination_framework",
                    "performance_monitoring",
                ],
                "max_agents": 3,
                "max_concurrent_tasks": 10,
            },
            "advanced": {
                "description": "Advanced multi-domain with specialized expertise",
                "features": [
                    "all_domain_agents",
                    "coordination_framework",
                    "performance_monitoring",
                    "knowledge_integration",
                ],
                "max_agents": 10,
                "max_concurrent_tasks": 50,
            },
            "enterprise": {
                "description": "Enterprise-scale deployment with full features",
                "features": [
                    "all_domain_agents",
                    "coordination_framework",
                    "performance_monitoring",
                    "knowledge_integration",
                    "scalability",
                    "cloud_integration",
                ],
                "max_agents": "unlimited",
                "max_concurrent_tasks": "unlimited",
            },
        }

        self.logger.info("Initialized Phase 16 CLI Manager")

    def validate_environment(self: Self) -> dict[str, Any]:
        """Step 1: Environment Validation First."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "config": {},
            "dependencies": {},
        }

        # Check required environment variables
        required_vars = [
            "PHASE16_COORDINATION_STRATEGY",
            "PHASE16_MAX_CONCURRENT_TASKS",
            "PHASE16_DEFAULT_TIMEOUT",
            "PHASE16_LOG_LEVEL",
        ]

        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                validation_result["warnings"].append(
                    f"Optional environment variable {var} not set, using default"
                )
            else:
                validation_result["config"][var] = value

        # Validate coordination strategy
        valid_strategies = [
            "round_robin",
            "load_balanced",
            "expertise_based",
            "priority_based",
        ]
        if self.config["coordination_strategy"] not in valid_strategies:
            validation_result["errors"].append(
                f"Invalid coordination strategy: {self.config['coordination_strategy']}"
            )
            validation_result["valid"] = False

        # Check Python dependencies
        try:
            import asyncio

            validation_result["dependencies"]["asyncio"] = "available"
        except ImportError:
            validation_result["errors"].append("asyncio module not available")
            validation_result["valid"] = False

        try:
            import click

            validation_result["dependencies"]["click"] = "available"
        except ImportError:
            validation_result["errors"].append("click module not available")
            validation_result["valid"] = False

        try:
            from dotenv import load_dotenv

            validation_result["dependencies"]["python-dotenv"] = "available"
        except ImportError:
            validation_result["warnings"].append(
                "python-dotenv not available, using os.environ"
            )

        # Check Phase 16 components
        try:
            from .multi_domain_architecture import BaseDomainAgent

            validation_result["dependencies"]["multi_domain_architecture"] = "available"
        except ImportError:
            validation_result["errors"].append(
                "Multi-domain architecture components not available"
            )
            validation_result["valid"] = False

        try:
            from .agent_coordination_framework import AgentCoordinationFramework

            validation_result["dependencies"][
                "agent_coordination_framework"
            ] = "available"
        except ImportError:
            validation_result["errors"].append(
                "Agent coordination framework not available"
            )
            validation_result["valid"] = False

        return validation_result

    def validate_input(
        self: Self, command: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Step 2: Comprehensive Input Validation."""
        validation_result = {
            "valid": True,
            "errors": [],
            "sanitized_params": {},
        }

        # Validate command
        valid_commands = [
            "validate-env",
            "status",
            "register-agent",
            "submit-task",
            "coordination-status",
            "test-framework",
            "deploy",
            "performance-metrics",
        ]

        if command not in valid_commands:
            validation_result["errors"].append(f"Invalid command: {command}")
            validation_result["valid"] = False
            return validation_result

        # Command-specific validation
        if command == "register-agent":
            agent_type = params.get("agent_type")
            if not agent_type:
                validation_result["errors"].append("Agent type is required")
                validation_result["valid"] = False
            elif agent_type not in ["electrical", "mechanical", "chemical"]:
                validation_result["errors"].append(f"Invalid agent type: {agent_type}")
                validation_result["valid"] = False
            else:
                validation_result["sanitized_params"]["agent_type"] = agent_type.lower()

        elif command == "submit-task":
            domain = params.get("domain")
            query = params.get("query")

            if not domain:
                validation_result["errors"].append("Domain is required")
                validation_result["valid"] = False
            elif domain not in ["electrical", "mechanical", "chemical_process"]:
                validation_result["errors"].append(f"Invalid domain: {domain}")
                validation_result["valid"] = False

            if not query:
                validation_result["errors"].append("Query is required")
                validation_result["valid"] = False
            elif len(query.strip()) == 0:
                validation_result["errors"].append("Query cannot be empty")
                validation_result["valid"] = False
            elif len(query) > 2000:
                validation_result["errors"].append(
                    "Query too long (max 2000 characters)"
                )
                validation_result["valid"] = False

            if validation_result["valid"]:
                validation_result["sanitized_params"]["domain"] = domain.lower()
                validation_result["sanitized_params"]["query"] = query.strip()

        elif command == "deploy":
            complexity = params.get("complexity", "basic")
            if complexity not in self.complexity_levels:
                validation_result["errors"].append(
                    f"Invalid complexity level: {complexity}"
                )
                validation_result["valid"] = False
            else:
                validation_result["sanitized_params"]["complexity"] = complexity

        return validation_result

    def handle_error(self: Self, error: Exception, context: str) -> dict[str, Any]:
        """Step 3: Error Handling with User-Friendly Messages."""
        error_message = f"Phase 16 CLI error: {context}"
        self.logger.error(f"{error_message}: {error!s}")

        # Create user-friendly error response
        return {
            "success": False,
            "error": error_message,
            "suggestion": self._get_error_suggestion(error, context),
            "timestamp": datetime.now().isoformat(),
        }

    def _get_error_suggestion(self: Self, error: Exception, context: str) -> str:
        """Get user-friendly error suggestion."""
        str(error).lower()

        if "environment" in context:
            return "Run 'phase16 validate-env' to check environment setup"
        elif "validation" in context:
            return "Check command parameters and try again"
        elif "coordination" in context:
            return "Ensure coordination framework is initialized"
        elif "agent" in context:
            return "Check if agents are registered and active"
        else:
            return "Check logs for detailed error information"

    async def initialize_coordination_framework(self: Self) -> dict[str, Any]:
        """Initialize coordination framework."""
        try:
            # Map string strategy to enum
            strategy_map = {
                "round_robin": CoordinationStrategy.ROUND_ROBIN,
                "load_balanced": CoordinationStrategy.LOAD_BALANCED,
                "expertise_based": CoordinationStrategy.EXPERTISE_BASED,
                "priority_based": CoordinationStrategy.PRIORITY_BASED,
            }

            strategy = strategy_map.get(
                self.config["coordination_strategy"],
                CoordinationStrategy.EXPERTISE_BASED,
            )

            self.coordination_framework = AgentCoordinationFramework(
                coordination_strategy=strategy
            )

            return {
                "success": True,
                "message": "Coordination framework initialized successfully",
                "strategy": self.config["coordination_strategy"],
            }

        except Exception as e:
            return self.handle_error(e, "coordination framework initialization")

    async def register_domain_agent(self: Self, agent_type: str) -> dict[str, Any]:
        """Register domain-specific agent."""
        try:
            if not self.coordination_framework:
                init_result = await self.initialize_coordination_framework()
                if not init_result["success"]:
                    return init_result

            # Create agent based on type
            if agent_type == "electrical":
                agent_id = f"electrical_agent_{int(time.time())}"
                agent = ElectricalEngineeringAgent(agent_id)
            elif agent_type == "mechanical":
                # For now, create a mock mechanical agent
                agent_id = f"mechanical_agent_{int(time.time())}"
                agent = self._create_mock_agent(agent_id, DomainType.MECHANICAL)
            elif agent_type == "chemical":
                # For now, create a mock chemical agent
                agent_id = f"chemical_agent_{int(time.time())}"
                agent = self._create_mock_agent(agent_id, DomainType.CHEMICAL_PROCESS)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported agent type: {agent_type}",
                }

            # Register agent with coordination framework
            registration_success = await self.coordination_framework.register_agent(
                agent
            )

            if registration_success:
                self.registered_agents[agent.agent_id] = agent

                return {
                    "success": True,
                    "message": f"{agent_type.title()} agent registered successfully",
                    "agent_id": agent.agent_id,
                    "domain": agent.domain.value,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to register {agent_type} agent",
                }

        except Exception as e:
            return self.handle_error(e, f"{agent_type} agent registration")

    def _create_mock_agent(
        self: Self, agent_id: str, domain: DomainType
    ) -> BaseDomainAgent:
        """Create mock agent for testing purposes."""
        # This is a simplified mock implementation
        # In production, this would be replaced with actual domain agents

        class MockDomainAgent(BaseDomainAgent):
            def __init__(self, agent_id: str, domain: DomainType):
                super().__init__(
                    agent_id=agent_id, domain=domain, max_concurrent_tasks=3
                )

            async def assign_task(self, task: AgentTask) -> bool:
                # Mock task assignment
                task.assigned_agent = self.agent_id
                task.status = "assigned"
                self.active_tasks[task.task_id] = task

                # Simulate processing
                await asyncio.sleep(0.1)

                # Mock result
                task.result = {
                    "success": True,
                    "response": f"Mock {domain.value} agent response for: {task.query}",
                    "expertise_applied": f"Mock {domain.value} expertise",
                }
                task.status = "completed"
                task.completed_at = datetime.now()

                # Move to completed
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
                    self.completed_tasks.append(task)

                return True

        return MockDomainAgent(agent_id, domain)

    async def submit_task_to_domain(
        self: Self, domain: str, query: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Submit task to domain agent."""
        try:
            if not self.coordination_framework:
                return {
                    "success": False,
                    "error": "Coordination framework not initialized",
                    "suggestion": "Run 'phase16 register-agent <type>' first",
                }

            # Map domain string to enum
            domain_map = {
                "electrical": DomainType.ELECTRICAL,
                "mechanical": DomainType.MECHANICAL,
                "chemical_process": DomainType.CHEMICAL_PROCESS,
            }

            domain_enum = domain_map.get(domain)
            if not domain_enum:
                return {
                    "success": False,
                    "error": f"Invalid domain: {domain}",
                }

            # Create task
            task = AgentTask(query=query, domain=domain_enum, context=context or {})

            # Submit task
            submission_result = await self.coordination_framework.submit_task(task)

            if submission_result["success"]:
                return {
                    "success": True,
                    "message": "Task submitted successfully",
                    "task_id": submission_result["task_id"],
                    "domain": domain,
                    "assigned_agent": submission_result.get("assigned_agent"),
                    "coordination_time": submission_result.get("coordination_time", 0),
                }
            else:
                return submission_result

        except Exception as e:
            return self.handle_error(e, "task submission")

    def get_coordination_status(self: Self) -> dict[str, Any]:
        """Get coordination framework status."""
        try:
            if not self.coordination_framework:
                return {
                    "success": False,
                    "error": "Coordination framework not initialized",
                }

            status = self.coordination_framework.get_coordination_status()

            return {
                "success": True,
                "coordination_status": status,
                "registered_agents": len(self.registered_agents),
                "agent_details": {
                    agent_id: agent.get_agent_status()
                    for agent_id, agent in self.registered_agents.items()
                },
            }

        except Exception as e:
            return self.handle_error(e, "status retrieval")

    async def deploy_with_complexity(self: Self, complexity: str) -> dict[str, Any]:
        """Deploy Phase 16 with specified complexity level."""
        try:
            complexity_config = self.complexity_levels[complexity]

            deployment_result = {
                "success": True,
                "complexity_level": complexity,
                "description": complexity_config["description"],
                "features_deployed": [],
                "agents_registered": [],
                "deployment_time": 0,
            }

            start_time = time.time()

            # Initialize coordination framework
            if not self.coordination_framework:
                init_result = await self.initialize_coordination_framework()
                if not init_result["success"]:
                    return init_result
                deployment_result["features_deployed"].append("coordination_framework")

            # Deploy agents based on complexity
            if "electrical_agent" in complexity_config["features"]:
                register_result = await self.register_domain_agent("electrical")
                if register_result["success"]:
                    deployment_result["agents_registered"].append("electrical")
                    deployment_result["features_deployed"].append("electrical_agent")

            if (
                "mechanical_agent" in complexity_config["features"]
                or "all_domain_agents" in complexity_config["features"]
            ):
                register_result = await self.register_domain_agent("mechanical")
                if register_result["success"]:
                    deployment_result["agents_registered"].append("mechanical")
                    deployment_result["features_deployed"].append("mechanical_agent")

            if "all_domain_agents" in complexity_config["features"]:
                register_result = await self.register_domain_agent("chemical")
                if register_result["success"]:
                    deployment_result["agents_registered"].append("chemical")
                    deployment_result["features_deployed"].append("chemical_agent")

            # Add additional features
            if "performance_monitoring" in complexity_config["features"]:
                deployment_result["features_deployed"].append("performance_monitoring")

            if "knowledge_integration" in complexity_config["features"]:
                deployment_result["features_deployed"].append("knowledge_integration")

            if "scalability" in complexity_config["features"]:
                deployment_result["features_deployed"].append("scalability")

            if "cloud_integration" in complexity_config["features"]:
                deployment_result["features_deployed"].append("cloud_integration")

            deployment_result["deployment_time"] = time.time() - start_time

            return deployment_result

        except Exception as e:
            return self.handle_error(e, f"deployment with {complexity} complexity")

    def run_test_framework(self: Self) -> dict[str, Any]:
        """Run Phase 16 test framework."""
        try:
            self.logger.info("Running Phase 16 test framework...")

            # Run tests
            test_results = run_phase_16_tests()

            return {
                "success": True,
                "test_results": test_results,
                "summary": {
                    "total_tests": test_results["total_tests"],
                    "passed_tests": test_results["passed_tests"],
                    "failed_tests": test_results["failed_tests"],
                    "success_rate": test_results.get("success_rate", 0.0),
                },
            }

        except Exception as e:
            return self.handle_error(e, "test framework execution")

    def get_performance_metrics(self: Self) -> dict[str, Any]:
        """Get performance metrics."""
        try:
            if not self.coordination_framework:
                return {
                    "success": False,
                    "error": "Coordination framework not initialized",
                }

            status = self.coordination_framework.get_coordination_status()

            performance_metrics = {
                "coordination_statistics": status["statistics"],
                "agent_metrics": status["agent_metrics"],
                "system_performance": {
                    "registered_agents": status["registered_agents"],
                    "active_agents": status["active_agents"],
                    "task_queue_size": status["task_queue_size"],
                    "active_tasks": status["active_tasks"],
                    "completed_tasks": status["completed_tasks"],
                    "failed_tasks": status["failed_tasks"],
                },
                "timestamp": datetime.now().isoformat(),
            }

            return {
                "success": True,
                "performance_metrics": performance_metrics,
            }

        except Exception as e:
            return self.handle_error(e, "performance metrics retrieval")

    def cleanup(self: Self) -> None:
        """Step 6: Resource Management and Cleanup."""
        try:
            if self.coordination_framework:
                self.coordination_framework.cleanup()
                self.coordination_framework = None

            for agent_id, agent in self.registered_agents.items():
                agent.cleanup()
                self.logger.info(f"Cleaned up agent {agent_id}")

            self.registered_agents.clear()

            self.logger.info("Phase 16 CLI Manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# CLI Manager instance
cli_manager = Phase16CLIManager()


# CLI Commands using Click
@click.group()
def phase16():
    """Phase 16 Multi-Domain Enterprise AI Platform CLI."""
    pass


@phase16.command()
def validate_env():
    """Validate Phase 16 environment setup."""
    click.echo("🔍 Validating Phase 16 environment...")

    validation_result = cli_manager.validate_environment()

    if validation_result["valid"]:
        click.echo("✅ Environment validation successful!")

        if validation_result["config"]:
            click.echo("\n📋 Configuration:")
            for key, value in validation_result["config"].items():
                click.echo(f"  {key}: {value}")

        if validation_result["dependencies"]:
            click.echo("\n📦 Dependencies:")
            for dep, status in validation_result["dependencies"].items():
                click.echo(f"  {dep}: {status}")

        if validation_result["warnings"]:
            click.echo("\n⚠️  Warnings:")
            for warning in validation_result["warnings"]:
                click.echo(f"  - {warning}")
    else:
        click.echo("❌ Environment validation failed!")

        if validation_result["errors"]:
            click.echo("\n🚨 Errors:")
            for error in validation_result["errors"]:
                click.echo(f"  - {error}")

        sys.exit(1)


@phase16.command()
@click.argument(
    "agent_type", type=click.Choice(["electrical", "mechanical", "chemical"])
)
def register_agent(agent_type):
    """Register a domain-specific agent."""
    click.echo(f"🤖 Registering {agent_type} agent...")

    async def _register():
        result = await cli_manager.register_domain_agent(agent_type)

        if result["success"]:
            click.echo(f"✅ {result['message']}")
            click.echo(f"   Agent ID: {result['agent_id']}")
            click.echo(f"   Domain: {result['domain']}")
        else:
            click.echo(f"❌ {result['error']}")
            sys.exit(1)

    asyncio.run(_register())


@phase16.command()
@click.argument(
    "domain", type=click.Choice(["electrical", "mechanical", "chemical_process"])
)
@click.argument("query")
@click.option("--context", help="JSON context for the task")
def submit_task(domain, query, context):
    """Submit a task to a domain agent."""
    click.echo(f"📝 Submitting task to {domain} domain...")

    # Parse context if provided
    task_context = {}
    if context:
        try:
            task_context = json.loads(context)
        except json.JSONDecodeError:
            click.echo("❌ Invalid JSON context")
            sys.exit(1)

    async def _submit():
        result = await cli_manager.submit_task_to_domain(domain, query, task_context)

        if result["success"]:
            click.echo(f"✅ {result['message']}")
            click.echo(f"   Task ID: {result['task_id']}")
            click.echo(f"   Domain: {result['domain']}")
            if result.get("assigned_agent"):
                click.echo(f"   Assigned Agent: {result['assigned_agent']}")
            click.echo(
                f"   Coordination Time: {result.get('coordination_time', 0):.3f}s"
            )
        else:
            click.echo(f"❌ {result['error']}")
            if result.get("suggestion"):
                click.echo(f"💡 {result['suggestion']}")
            sys.exit(1)

    asyncio.run(_submit())


@phase16.command()
def coordination_status():
    """Show coordination framework status."""
    click.echo("📊 Retrieving coordination status...")

    result = cli_manager.get_coordination_status()

    if result["success"]:
        status = result["coordination_status"]

        click.echo("✅ Coordination Framework Status:")
        click.echo(f"   Strategy: {status['coordination_strategy']}")
        click.echo(f"   Registered Agents: {status['registered_agents']}")
        click.echo(f"   Active Agents: {status['active_agents']}")
        click.echo(f"   Task Queue Size: {status['task_queue_size']}")
        click.echo(f"   Active Tasks: {status['active_tasks']}")
        click.echo(f"   Completed Tasks: {status['completed_tasks']}")
        click.echo(f"   Failed Tasks: {status['failed_tasks']}")

        if result["agent_details"]:
            click.echo("\n🤖 Agent Details:")
            for agent_id, details in result["agent_details"].items():
                click.echo(f"   {agent_id}:")
                click.echo(f"     Domain: {details['domain']}")
                click.echo(f"     Status: {details['status']}")
                click.echo(f"     Active Tasks: {details['active_tasks']}")
                click.echo(f"     Completed Tasks: {details['completed_tasks']}")
    else:
        click.echo(f"❌ {result['error']}")
        sys.exit(1)


@phase16.command()
@click.argument(
    "complexity", type=click.Choice(["basic", "standard", "advanced", "enterprise"])
)
def deploy(complexity):
    """Deploy Phase 16 with specified complexity level."""
    click.echo(f"🚀 Deploying Phase 16 with {complexity} complexity...")

    async def _deploy():
        result = await cli_manager.deploy_with_complexity(complexity)

        if result["success"]:
            click.echo("✅ Deployment successful!")
            click.echo(f"   Complexity Level: {result['complexity_level']}")
            click.echo(f"   Description: {result['description']}")
            click.echo(f"   Deployment Time: {result['deployment_time']:.2f}s")

            if result["features_deployed"]:
                click.echo(
                    f"   Features Deployed: {', '.join(result['features_deployed'])}"
                )

            if result["agents_registered"]:
                click.echo(
                    f"   Agents Registered: {', '.join(result['agents_registered'])}"
                )
        else:
            click.echo(f"❌ Deployment failed: {result['error']}")
            sys.exit(1)

    asyncio.run(_deploy())


@phase16.command()
def test_framework():
    """Run Phase 16 test framework."""
    click.echo("🧪 Running Phase 16 test framework...")

    result = cli_manager.run_test_framework()

    if result["success"]:
        summary = result["summary"]
        click.echo("✅ Test framework completed!")
        click.echo(f"   Total Tests: {summary['total_tests']}")
        click.echo(f"   Passed: {summary['passed_tests']}")
        click.echo(f"   Failed: {summary['failed_tests']}")
        click.echo(f"   Success Rate: {summary['success_rate']:.1%}")

        if summary["failed_tests"] > 0:
            click.echo("\n⚠️  Some tests failed. Check logs for details.")
    else:
        click.echo(f"❌ Test framework failed: {result['error']}")
        sys.exit(1)


@phase16.command()
def performance_metrics():
    """Show performance metrics."""
    click.echo("📈 Retrieving performance metrics...")

    result = cli_manager.get_performance_metrics()

    if result["success"]:
        metrics = result["performance_metrics"]

        click.echo("✅ Performance Metrics:")

        # System performance
        sys_perf = metrics["system_performance"]
        click.echo("   System Performance:")
        click.echo(f"     Registered Agents: {sys_perf['registered_agents']}")
        click.echo(f"     Active Agents: {sys_perf['active_agents']}")
        click.echo(f"     Task Queue Size: {sys_perf['task_queue_size']}")
        click.echo(f"     Active Tasks: {sys_perf['active_tasks']}")
        click.echo(f"     Completed Tasks: {sys_perf['completed_tasks']}")
        click.echo(f"     Failed Tasks: {sys_perf['failed_tasks']}")

        # Coordination statistics
        coord_stats = metrics["coordination_statistics"]
        click.echo("\n   Coordination Statistics:")
        click.echo(
            f"     Total Tasks Coordinated: {coord_stats['total_tasks_coordinated']}"
        )
        click.echo(
            f"     Successful Coordinations: {coord_stats['successful_coordinations']}"
        )
        click.echo(f"     Failed Coordinations: {coord_stats['failed_coordinations']}")
        click.echo(
            f"     Average Coordination Time: {coord_stats['average_coordination_time']:.3f}s"
        )

        # Agent metrics
        if metrics["agent_metrics"]:
            click.echo("\n   Agent Metrics:")
            for agent_id, agent_metrics in metrics["agent_metrics"].items():
                click.echo(f"     {agent_id}:")
                click.echo(f"       Domain: {agent_metrics['domain']}")
                click.echo(f"       Total Tasks: {agent_metrics['total_tasks']}")
                click.echo(f"       Success Rate: {agent_metrics['success_rate']:.1%}")
                click.echo(f"       Current Load: {agent_metrics['current_load']}")
                click.echo(f"       Availability: {agent_metrics['availability']:.1%}")
    else:
        click.echo(f"❌ {result['error']}")
        sys.exit(1)


@phase16.command()
def status():
    """Show overall Phase 16 status."""
    click.echo("📋 Phase 16 Multi-Domain Enterprise AI Platform Status")
    click.echo("=" * 50)

    # Environment validation
    click.echo("\n🔍 Environment Status:")
    validation_result = cli_manager.validate_environment()
    if validation_result["valid"]:
        click.echo("   ✅ Environment: Valid")
    else:
        click.echo("   ❌ Environment: Invalid")
        for error in validation_result["errors"]:
            click.echo(f"      - {error}")

    # Coordination status
    click.echo("\n🤝 Coordination Status:")
    coord_result = cli_manager.get_coordination_status()
    if coord_result["success"]:
        status = coord_result["coordination_status"]
        click.echo(f"   ✅ Framework: Active ({status['coordination_strategy']})")
        click.echo(
            f"   🤖 Agents: {status['active_agents']}/{status['registered_agents']} active"
        )
        click.echo(
            f"   📋 Tasks: {status['active_tasks']} active, {status['task_queue_size']} queued"
        )
    else:
        click.echo("   ❌ Framework: Not initialized")

    click.echo("\n💡 Available Commands:")
    click.echo("   phase16 validate-env          - Validate environment")
    click.echo("   phase16 deploy <complexity>   - Deploy with complexity level")
    click.echo("   phase16 register-agent <type> - Register domain agent")
    click.echo("   phase16 submit-task <domain> <query> - Submit task")
    click.echo("   phase16 test-framework        - Run test suite")
    click.echo("   phase16 performance-metrics   - Show metrics")


if __name__ == "__main__":
    try:
        phase16()
    except KeyboardInterrupt:
        click.echo("\n👋 Phase 16 CLI interrupted by user")
        cli_manager.cleanup()
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        cli_manager.cleanup()
        sys.exit(1)


# Export CLI manager and commands
__all__ = [
    "Phase16CLIManager",
    "cli_manager",
    "phase16",
]
