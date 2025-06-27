#!/usr/bin/env python3
"""Phase 16 Test Framework for Multi-Domain Architecture.

Following crawl_mcp.py methodology for systematic testing:
- Step 4: Modular component testing
- Environment validation testing
- Input validation testing
- Error handling testing
- Resource management testing
- Integration testing
- Performance testing

Test Coverage:
- Multi-domain architecture components
- Agent coordination framework
- Domain-specific agents (Electrical, Mechanical, Chemical)
- Communication protocols
- Task delegation and coordination
- Performance monitoring
- Scalability testing
"""

import logging
import os
import time
import unittest
from datetime import datetime
from typing import Any, Self
from unittest.mock import AsyncMock, MagicMock

from dotenv import load_dotenv

from .agent_coordination_framework import (
    AgentCoordinationFramework,
    AgentPerformanceMetrics,
    CoordinationMessage,
    CoordinationStrategy,
)
from .electrical_engineering_agent import ElectricalEngineeringAgent
from .multi_domain_architecture import (
    AgentStatus,
    AgentTask,
    BaseDomainAgent,
    DomainType,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TestMultiDomainArchitecture(unittest.TestCase):
    """Test suite for Multi-Domain Architecture components.

    Following crawl_mcp.py methodology for comprehensive testing.
    """

    def setUp(self: Self) -> None:
        """Set up test environment."""
        self.test_agent_id = "test_agent_001"
        self.test_domain = DomainType.ELECTRICAL
        self.test_task_query = "Analyze motor control system for 480V 3-phase motor"

        # Create test task
        self.test_task = AgentTask(
            query=self.test_task_query,
            domain=self.test_domain,
            context={"voltage": "480V", "phases": 3, "application": "motor_control"},
        )

    def test_domain_type_enum(self: Self) -> None:
        """Test DomainType enum values."""
        assert DomainType.ELECTRICAL.value == "electrical"
        assert DomainType.MECHANICAL.value == "mechanical"
        assert DomainType.CHEMICAL_PROCESS.value == "chemical_process"

    def test_agent_status_enum(self: Self) -> None:
        """Test AgentStatus enum values."""
        assert AgentStatus.INITIALIZING.value == "initializing"
        assert AgentStatus.ACTIVE.value == "active"
        assert AgentStatus.BUSY.value == "busy"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.OFFLINE.value == "offline"

    def test_agent_task_creation(self: Self) -> None:
        """Test AgentTask creation and validation."""
        # Test valid task creation
        task = AgentTask(
            query="Test query", domain=DomainType.ELECTRICAL, context={"test": "data"}
        )

        assert task.task_id is not None
        assert task.query == "Test query"
        assert task.domain == DomainType.ELECTRICAL
        assert task.context["test"] == "data"
        assert task.status == "pending"
        assert isinstance(task.created_at, datetime)

    def test_agent_task_to_dict(self: Self) -> None:
        """Test AgentTask dictionary conversion."""
        task_dict = self.test_task.to_dict()

        assert "task_id" in task_dict
        assert "query" in task_dict
        assert "domain" in task_dict
        assert "context" in task_dict
        assert "status" in task_dict
        assert "created_at" in task_dict

        assert task_dict["query"] == self.test_task_query
        assert task_dict["domain"] == self.test_domain.value


class TestAgentCoordinationFramework(unittest.TestCase):
    """Test suite for Agent Coordination Framework.

    Following crawl_mcp.py methodology for coordination testing.
    """

    def setUp(self: Self) -> None:
        """Set up test environment."""
        self.coordination_framework = AgentCoordinationFramework(
            coordination_strategy=CoordinationStrategy.EXPERTISE_BASED
        )

        # Create test task
        self.test_task = AgentTask(
            query="Test electrical engineering query",
            domain=DomainType.ELECTRICAL,
            context={"test": "context"},
        )

    def test_coordination_framework_initialization(self: Self) -> None:
        """Test coordination framework initialization."""
        assert (
            self.coordination_framework.coordination_strategy
            == CoordinationStrategy.EXPERTISE_BASED
        )
        assert isinstance(self.coordination_framework.registered_agents, dict)
        assert isinstance(self.coordination_framework.domain_agents, dict)
        assert isinstance(self.coordination_framework.task_queue, list)
        assert isinstance(self.coordination_framework.active_tasks, dict)

    def test_environment_validation(self: Self) -> None:
        """Test Step 1: Environment Validation First."""
        validation_result = self.coordination_framework.validate_environment()

        assert isinstance(validation_result, dict)
        assert "valid" in validation_result
        assert "errors" in validation_result
        assert "warnings" in validation_result
        assert "config" in validation_result

        # Should be valid with default environment
        assert validation_result["valid"]

    def test_input_validation(self: Self) -> None:
        """Test Step 2: Comprehensive Input Validation."""
        # Test valid task
        assert self.coordination_framework.validate_input(self.test_task)

        # Test invalid task - None
        assert not self.coordination_framework.validate_input(None)

        # Test invalid task - empty query
        invalid_task = AgentTask(query="", domain=DomainType.ELECTRICAL, context={})
        assert not self.coordination_framework.validate_input(invalid_task)

        # Test invalid task - too long query
        long_query_task = AgentTask(
            query="x" * 2001, domain=DomainType.ELECTRICAL, context={}
        )
        assert not self.coordination_framework.validate_input(long_query_task)

    def test_error_handling(self: Self) -> None:
        """Test Step 3: Error Handling with User-Friendly Messages."""
        test_error = ValueError("Test error")
        error_response = self.coordination_framework.handle_error(
            test_error, "test context"
        )

        assert isinstance(error_response, dict)
        assert not error_response["success"]
        assert "error" in error_response
        assert "suggestion" in error_response
        assert "timestamp" in error_response
        assert "coordination_strategy" in error_response

    def test_coordination_message_creation(self: Self) -> None:
        """Test coordination message creation."""
        message = CoordinationMessage(
            sender_agent="agent_1",
            receiver_agent="agent_2",
            message_type="task_assignment",
            content={"task_id": "test_123"},
            priority=1,
        )

        assert message.message_id is not None
        assert message.sender_agent == "agent_1"
        assert message.receiver_agent == "agent_2"
        assert message.message_type == "task_assignment"
        assert message.priority == 1

        # Test dictionary conversion
        message_dict = message.to_dict()
        assert "message_id" in message_dict
        assert "timestamp" in message_dict

    def test_agent_performance_metrics(self: Self) -> None:
        """Test agent performance metrics."""
        metrics = AgentPerformanceMetrics(
            agent_id="test_agent",
            domain="electrical",
            total_tasks=10,
            successful_tasks=8,
            failed_tasks=2,
        )

        assert metrics.success_rate() == 0.8

        # Test metrics with no tasks
        empty_metrics = AgentPerformanceMetrics(
            agent_id="empty_agent", domain="mechanical"
        )
        assert empty_metrics.success_rate() == 0.0

        # Test dictionary conversion
        metrics_dict = metrics.to_dict()
        assert "success_rate" in metrics_dict
        assert metrics_dict["success_rate"] == 0.8

    def test_coordination_status(self: Self) -> None:
        """Test coordination framework status reporting."""
        status = self.coordination_framework.get_coordination_status()

        assert isinstance(status, dict)
        assert "coordination_strategy" in status
        assert "registered_agents" in status
        assert "active_agents" in status
        assert "task_queue_size" in status
        assert "active_tasks" in status
        assert "statistics" in status
        assert "agent_metrics" in status

        assert status["coordination_strategy"] == "expertise_based"
        assert status["registered_agents"] == 0  # No agents registered yet


class TestElectricalEngineeringAgent(unittest.TestCase):
    """Test suite for Electrical Engineering Agent.

    Following crawl_mcp.py methodology for domain-specific testing.
    """

    def setUp(self: Self) -> None:
        """Set up test environment."""
        self.electrical_agent = ElectricalEngineeringAgent("test_electrical_agent")

        # Create test tasks for different expertise areas
        self.power_systems_task = AgentTask(
            query="Analyze power transformer ratings for 13.8kV distribution system",
            domain=DomainType.ELECTRICAL,
            context={"voltage_level": "13.8kV", "application": "distribution"},
        )

        self.motor_control_task = AgentTask(
            query="Configure VFD parameters for 100HP motor speed control",
            domain=DomainType.ELECTRICAL,
            context={"motor_hp": 100, "application": "speed_control"},
        )

        self.plc_task = AgentTask(
            query="Develop PLC ladder logic for automated conveyor system",
            domain=DomainType.ELECTRICAL,
            context={"system_type": "conveyor", "automation_level": "full"},
        )

    def test_electrical_agent_initialization(self: Self) -> None:
        """Test electrical engineering agent initialization."""
        assert self.electrical_agent.domain == DomainType.ELECTRICAL
        assert self.electrical_agent.agent_id == "test_electrical_agent"
        assert self.electrical_agent.status == AgentStatus.ACTIVE
        assert isinstance(self.electrical_agent.expertise_areas, dict)

        # Check expertise areas
        expected_areas = [
            "power_systems",
            "motor_control",
            "plc_programming",
            "electrical_safety",
            "circuit_analysis",
            "instrumentation",
        ]
        for area in expected_areas:
            assert area in self.electrical_agent.expertise_areas

    def test_electrical_environment_validation(self: Self) -> None:
        """Test electrical agent environment validation."""
        validation_result = self.electrical_agent.validate_environment()

        assert isinstance(validation_result, dict)
        assert "valid" in validation_result
        assert validation_result["valid"]

    def test_electrical_task_validation(self: Self) -> None:
        """Test electrical task validation and expertise matching."""
        # Test power systems task
        power_validation = self.electrical_agent.validate_electrical_task(
            self.power_systems_task
        )
        assert power_validation["valid"]
        assert "power" in power_validation["keywords_found"]

        # Test motor control task
        motor_validation = self.electrical_agent.validate_electrical_task(
            self.motor_control_task
        )
        assert motor_validation["valid"]
        assert "motor" in motor_validation["keywords_found"]

        # Test PLC task
        plc_validation = self.electrical_agent.validate_electrical_task(self.plc_task)
        assert plc_validation["valid"]
        assert "plc" in plc_validation["keywords_found"]

        # Test general task with low confidence
        general_task = AgentTask(
            query="General electrical question",
            domain=DomainType.ELECTRICAL,
            context={},
        )
        general_validation = self.electrical_agent.validate_electrical_task(
            general_task
        )
        assert general_validation["valid"]
        assert general_validation["confidence"] < 0.3
        assert len(general_validation["suggestions"]) > 0

    async def test_electrical_task_processing(self: Self) -> None:
        """Test electrical task processing for different expertise areas."""
        # Test power systems processing
        power_result = await self.electrical_agent.process_electrical_task(
            self.power_systems_task
        )
        assert power_result["success"]
        assert power_result["expertise_area"] == "power_systems"
        assert "response" in power_result
        assert "recommendations" in power_result["response"]

        # Test motor control processing
        motor_result = await self.electrical_agent.process_electrical_task(
            self.motor_control_task
        )
        assert motor_result["success"]
        assert motor_result["expertise_area"] == "motor_control"
        assert "control_strategies" in motor_result["response"]

        # Test PLC processing
        plc_result = await self.electrical_agent.process_electrical_task(self.plc_task)
        assert plc_result["success"]
        assert plc_result["expertise_area"] == "plc_programming"
        assert "programming_guidelines" in plc_result["response"]

    def test_electrical_agent_status(self: Self) -> None:
        """Test electrical agent status reporting."""
        status = self.electrical_agent.get_agent_status()

        assert isinstance(status, dict)
        assert "agent_id" in status
        assert "domain" in status
        assert "status" in status
        assert "expertise_areas" in status
        assert "specialization" in status

        assert status["specialization"] == "Electrical Engineering"
        assert status["domain"] == "electrical"


class TestIntegrationScenarios(unittest.TestCase):
    """Test suite for integration scenarios.

    Following crawl_mcp.py methodology for integration testing.
    """

    def setUp(self: Self) -> None:
        """Set up integration test environment."""
        self.coordination_framework = AgentCoordinationFramework(
            coordination_strategy=CoordinationStrategy.EXPERTISE_BASED
        )
        self.electrical_agent = ElectricalEngineeringAgent(
            "integration_electrical_agent"
        )

    async def test_agent_registration_and_task_submission(self: Self) -> None:
        """Test complete agent registration and task submission workflow."""
        # Step 1: Register agent with coordination framework
        registration_success = await self.coordination_framework.register_agent(
            self.electrical_agent
        )
        assert registration_success

        # Verify agent is registered
        assert (
            self.electrical_agent.agent_id
            in self.coordination_framework.registered_agents
        )
        assert (
            self.electrical_agent.agent_id
            in self.coordination_framework.domain_agents[DomainType.ELECTRICAL]
        )

        # Step 2: Submit task
        test_task = AgentTask(
            query="Design motor control circuit for 50HP pump application",
            domain=DomainType.ELECTRICAL,
            context={"motor_hp": 50, "application": "pump"},
        )

        submission_result = await self.coordination_framework.submit_task(test_task)
        assert submission_result["success"]
        assert "task_id" in submission_result

        # Step 3: Verify task assignment
        assert test_task.task_id in self.coordination_framework.active_tasks

        # Step 4: Check coordination status
        status = self.coordination_framework.get_coordination_status()
        assert status["registered_agents"] == 1
        assert status["active_agents"] == 1

    async def test_multiple_agent_coordination(self: Self) -> None:
        """Test coordination with multiple agents."""
        # Create additional agents (mock for now)
        mechanical_agent = MagicMock(spec=BaseDomainAgent)
        mechanical_agent.agent_id = "mechanical_agent"
        mechanical_agent.domain = DomainType.MECHANICAL
        mechanical_agent.status = AgentStatus.ACTIVE
        mechanical_agent.max_concurrent_tasks = 3
        mechanical_agent.active_tasks = {}
        mechanical_agent.assign_task = AsyncMock(return_value=True)

        # Register agents
        await self.coordination_framework.register_agent(self.electrical_agent)
        await self.coordination_framework.register_agent(mechanical_agent)

        # Submit tasks to different domains
        electrical_task = AgentTask(
            query="Motor control analysis", domain=DomainType.ELECTRICAL, context={}
        )

        mechanical_task = AgentTask(
            query="Mechanical system design", domain=DomainType.MECHANICAL, context={}
        )

        # Submit tasks
        electrical_result = await self.coordination_framework.submit_task(
            electrical_task
        )
        mechanical_result = await self.coordination_framework.submit_task(
            mechanical_task
        )

        assert electrical_result["success"]
        assert mechanical_result["success"]

        # Verify coordination status
        status = self.coordination_framework.get_coordination_status()
        assert status["registered_agents"] == 2
        assert status["active_agents"] == 2

    def test_resource_cleanup(self: Self) -> None:
        """Test Step 6: Resource Management and Cleanup."""
        # Add some test data
        self.coordination_framework.task_queue.append(
            AgentTask(query="Test task", domain=DomainType.ELECTRICAL, context={})
        )

        # Add mock agent
        mock_agent = MagicMock(spec=BaseDomainAgent)
        mock_agent.agent_id = "cleanup_test_agent"
        mock_agent.cleanup = MagicMock()
        self.coordination_framework.registered_agents["cleanup_test_agent"] = mock_agent

        # Perform cleanup
        self.coordination_framework.cleanup()

        # Verify cleanup
        assert len(self.coordination_framework.task_queue) == 0
        assert len(self.coordination_framework.active_tasks) == 0
        assert len(self.coordination_framework.registered_agents) == 0
        mock_agent.cleanup.assert_called_once()


class TestPerformanceAndScalability(unittest.TestCase):
    """Test suite for performance and scalability.

    Following crawl_mcp.py methodology for performance testing.
    """

    def setUp(self: Self) -> None:
        """Set up performance test environment."""
        self.coordination_framework = AgentCoordinationFramework()
        self.electrical_agent = ElectricalEngineeringAgent("performance_test_agent")

    async def test_task_processing_performance(self: Self) -> None:
        """Test task processing performance."""
        # Register agent
        await self.coordination_framework.register_agent(self.electrical_agent)

        # Create multiple tasks
        tasks = []
        for i in range(10):
            task = AgentTask(
                query=f"Motor control task {i}",
                domain=DomainType.ELECTRICAL,
                context={"task_number": i},
            )
            tasks.append(task)

        # Measure processing time
        start_time = time.time()

        results = []
        for task in tasks:
            result = await self.coordination_framework.submit_task(task)
            results.append(result)

        processing_time = time.time() - start_time

        # Verify all tasks were processed successfully
        successful_tasks = sum(1 for result in results if result["success"])
        assert successful_tasks == 10

        # Performance assertion (should process 10 tasks in reasonable time)
        assert processing_time < 5.0  # 5 seconds max

        # Log performance metrics
        logger.info(f"Processed {len(tasks)} tasks in {processing_time:.2f} seconds")
        logger.info(
            f"Average time per task: {processing_time / len(tasks):.3f} seconds"
        )

    def test_memory_usage(self: Self) -> None:
        """Test memory usage with large number of tasks."""
        import gc

        import psutil

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many tasks
        large_task_count = 1000
        tasks = []
        for i in range(large_task_count):
            task = AgentTask(
                query=f"Large scale test task {i}",
                domain=DomainType.ELECTRICAL,
                context={"task_id": i, "data": "x" * 100},  # Some test data
            )
            tasks.append(task)

        # Add tasks to queue
        self.coordination_framework.task_queue.extend(tasks)

        # Get memory usage after creating tasks
        after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Cleanup
        self.coordination_framework.cleanup()
        gc.collect()

        # Get memory usage after cleanup
        after_cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Log memory usage
        logger.info(f"Initial memory: {initial_memory:.2f} MB")
        logger.info(
            f"After creating {large_task_count} tasks: {after_creation_memory:.2f} MB"
        )
        logger.info(f"After cleanup: {after_cleanup_memory:.2f} MB")

        # Memory should not grow excessively
        memory_growth = after_creation_memory - initial_memory
        assert memory_growth < 100  # Should not use more than 100MB for 1000 tasks


def run_phase_16_tests() -> dict[str, Any]:
    """Run comprehensive Phase 16 test suite.

    Returns:
        Test results summary
    """
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_suites": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "errors": [],
        "performance_metrics": {},
    }

    # Define test suites
    test_suites = [
        TestMultiDomainArchitecture,
        TestAgentCoordinationFramework,
        TestElectricalEngineeringAgent,
        TestIntegrationScenarios,
        TestPerformanceAndScalability,
    ]

    for test_suite_class in test_suites:
        suite_name = test_suite_class.__name__
        logger.info(f"Running test suite: {suite_name}")

        try:
            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(test_suite_class)

            # Run tests
            runner = unittest.TextTestRunner(verbosity=2, stream=open(os.devnull, "w"))
            result = runner.run(suite)

            # Record results
            suite_result = {
                "suite_name": suite_name,
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "success": result.wasSuccessful(),
            }

            test_results["test_suites"].append(suite_result)
            test_results["total_tests"] += result.testsRun
            test_results["passed_tests"] += (
                result.testsRun - len(result.failures) - len(result.errors)
            )
            test_results["failed_tests"] += len(result.failures) + len(result.errors)

            # Record any errors
            for failure in result.failures:
                test_results["errors"].append(f"FAILURE: {failure[0]} - {failure[1]}")
            for error in result.errors:
                test_results["errors"].append(f"ERROR: {error[0]} - {error[1]}")

            logger.info(
                f"Suite {suite_name}: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors"
            )

        except Exception as e:
            logger.error(f"Failed to run test suite {suite_name}: {e}")
            test_results["errors"].append(f"Suite execution error: {suite_name} - {e}")

    # Calculate success rate
    if test_results["total_tests"] > 0:
        success_rate = test_results["passed_tests"] / test_results["total_tests"]
        test_results["success_rate"] = success_rate
    else:
        test_results["success_rate"] = 0.0

    return test_results


# Export test classes and runner
__all__ = [
    "TestAgentCoordinationFramework",
    "TestElectricalEngineeringAgent",
    "TestIntegrationScenarios",
    "TestMultiDomainArchitecture",
    "TestPerformanceAndScalability",
    "run_phase_16_tests",
]
