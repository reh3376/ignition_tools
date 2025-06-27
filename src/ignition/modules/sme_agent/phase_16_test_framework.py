#!/usr/bin/env python3
"""Phase 16 Test Framework for Multi-Domain Architecture

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

import asyncio
import json
import logging
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Self
from unittest.mock import AsyncMock, MagicMock, patch

from dotenv import load_dotenv

from .agent_coordination_framework import (
    AgentCoordinationFramework,
    CoordinationStrategy,
    CoordinationMessage,
    AgentPerformanceMetrics,
    TaskStatus,
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
            context={"voltage": "480V", "phases": 3, "application": "motor_control"}
        )
    
    def test_domain_type_enum(self: Self) -> None:
        """Test DomainType enum values."""
        self.assertEqual(DomainType.ELECTRICAL.value, "electrical")
        self.assertEqual(DomainType.MECHANICAL.value, "mechanical")
        self.assertEqual(DomainType.CHEMICAL_PROCESS.value, "chemical_process")
    
    def test_agent_status_enum(self: Self) -> None:
        """Test AgentStatus enum values."""
        self.assertEqual(AgentStatus.INITIALIZING.value, "initializing")
        self.assertEqual(AgentStatus.ACTIVE.value, "active")
        self.assertEqual(AgentStatus.BUSY.value, "busy")
        self.assertEqual(AgentStatus.ERROR.value, "error")
        self.assertEqual(AgentStatus.OFFLINE.value, "offline")
    
    def test_agent_task_creation(self: Self) -> None:
        """Test AgentTask creation and validation."""
        # Test valid task creation
        task = AgentTask(
            query="Test query",
            domain=DomainType.ELECTRICAL,
            context={"test": "data"}
        )
        
        self.assertIsNotNone(task.task_id)
        self.assertEqual(task.query, "Test query")
        self.assertEqual(task.domain, DomainType.ELECTRICAL)
        self.assertEqual(task.context["test"], "data")
        self.assertEqual(task.status, "pending")
        self.assertIsInstance(task.created_at, datetime)
    
    def test_agent_task_to_dict(self: Self) -> None:
        """Test AgentTask dictionary conversion."""
        task_dict = self.test_task.to_dict()
        
        self.assertIn("task_id", task_dict)
        self.assertIn("query", task_dict)
        self.assertIn("domain", task_dict)
        self.assertIn("context", task_dict)
        self.assertIn("status", task_dict)
        self.assertIn("created_at", task_dict)
        
        self.assertEqual(task_dict["query"], self.test_task_query)
        self.assertEqual(task_dict["domain"], self.test_domain.value)


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
            context={"test": "context"}
        )
    
    def test_coordination_framework_initialization(self: Self) -> None:
        """Test coordination framework initialization."""
        self.assertEqual(
            self.coordination_framework.coordination_strategy,
            CoordinationStrategy.EXPERTISE_BASED
        )
        self.assertIsInstance(self.coordination_framework.registered_agents, dict)
        self.assertIsInstance(self.coordination_framework.domain_agents, dict)
        self.assertIsInstance(self.coordination_framework.task_queue, list)
        self.assertIsInstance(self.coordination_framework.active_tasks, dict)
    
    def test_environment_validation(self: Self) -> None:
        """Test Step 1: Environment Validation First."""
        validation_result = self.coordination_framework.validate_environment()
        
        self.assertIsInstance(validation_result, dict)
        self.assertIn("valid", validation_result)
        self.assertIn("errors", validation_result)
        self.assertIn("warnings", validation_result)
        self.assertIn("config", validation_result)
        
        # Should be valid with default environment
        self.assertTrue(validation_result["valid"])
    
    def test_input_validation(self: Self) -> None:
        """Test Step 2: Comprehensive Input Validation."""
        # Test valid task
        self.assertTrue(self.coordination_framework.validate_input(self.test_task))
        
        # Test invalid task - None
        self.assertFalse(self.coordination_framework.validate_input(None))
        
        # Test invalid task - empty query
        invalid_task = AgentTask(query="", domain=DomainType.ELECTRICAL, context={})
        self.assertFalse(self.coordination_framework.validate_input(invalid_task))
        
        # Test invalid task - too long query
        long_query_task = AgentTask(
            query="x" * 2001,
            domain=DomainType.ELECTRICAL,
            context={}
        )
        self.assertFalse(self.coordination_framework.validate_input(long_query_task))
    
    def test_error_handling(self: Self) -> None:
        """Test Step 3: Error Handling with User-Friendly Messages."""
        test_error = ValueError("Test error")
        error_response = self.coordination_framework.handle_error(test_error, "test context")
        
        self.assertIsInstance(error_response, dict)
        self.assertFalse(error_response["success"])
        self.assertIn("error", error_response)
        self.assertIn("suggestion", error_response)
        self.assertIn("timestamp", error_response)
        self.assertIn("coordination_strategy", error_response)
    
    def test_coordination_message_creation(self: Self) -> None:
        """Test coordination message creation."""
        message = CoordinationMessage(
            sender_agent="agent_1",
            receiver_agent="agent_2",
            message_type="task_assignment",
            content={"task_id": "test_123"},
            priority=1
        )
        
        self.assertIsNotNone(message.message_id)
        self.assertEqual(message.sender_agent, "agent_1")
        self.assertEqual(message.receiver_agent, "agent_2")
        self.assertEqual(message.message_type, "task_assignment")
        self.assertEqual(message.priority, 1)
        
        # Test dictionary conversion
        message_dict = message.to_dict()
        self.assertIn("message_id", message_dict)
        self.assertIn("timestamp", message_dict)
    
    def test_agent_performance_metrics(self: Self) -> None:
        """Test agent performance metrics."""
        metrics = AgentPerformanceMetrics(
            agent_id="test_agent",
            domain="electrical",
            total_tasks=10,
            successful_tasks=8,
            failed_tasks=2
        )
        
        self.assertEqual(metrics.success_rate(), 0.8)
        
        # Test metrics with no tasks
        empty_metrics = AgentPerformanceMetrics(
            agent_id="empty_agent",
            domain="mechanical"
        )
        self.assertEqual(empty_metrics.success_rate(), 0.0)
        
        # Test dictionary conversion
        metrics_dict = metrics.to_dict()
        self.assertIn("success_rate", metrics_dict)
        self.assertEqual(metrics_dict["success_rate"], 0.8)
    
    def test_coordination_status(self: Self) -> None:
        """Test coordination framework status reporting."""
        status = self.coordination_framework.get_coordination_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("coordination_strategy", status)
        self.assertIn("registered_agents", status)
        self.assertIn("active_agents", status)
        self.assertIn("task_queue_size", status)
        self.assertIn("active_tasks", status)
        self.assertIn("statistics", status)
        self.assertIn("agent_metrics", status)
        
        self.assertEqual(status["coordination_strategy"], "expertise_based")
        self.assertEqual(status["registered_agents"], 0)  # No agents registered yet


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
            context={"voltage_level": "13.8kV", "application": "distribution"}
        )
        
        self.motor_control_task = AgentTask(
            query="Configure VFD parameters for 100HP motor speed control",
            domain=DomainType.ELECTRICAL,
            context={"motor_hp": 100, "application": "speed_control"}
        )
        
        self.plc_task = AgentTask(
            query="Develop PLC ladder logic for automated conveyor system",
            domain=DomainType.ELECTRICAL,
            context={"system_type": "conveyor", "automation_level": "full"}
        )
    
    def test_electrical_agent_initialization(self: Self) -> None:
        """Test electrical engineering agent initialization."""
        self.assertEqual(self.electrical_agent.domain, DomainType.ELECTRICAL)
        self.assertEqual(self.electrical_agent.agent_id, "test_electrical_agent")
        self.assertEqual(self.electrical_agent.status, AgentStatus.ACTIVE)
        self.assertIsInstance(self.electrical_agent.expertise_areas, dict)
        
        # Check expertise areas
        expected_areas = [
            "power_systems", "motor_control", "plc_programming",
            "electrical_safety", "circuit_analysis", "instrumentation"
        ]
        for area in expected_areas:
            self.assertIn(area, self.electrical_agent.expertise_areas)
    
    def test_electrical_environment_validation(self: Self) -> None:
        """Test electrical agent environment validation."""
        validation_result = self.electrical_agent.validate_environment()
        
        self.assertIsInstance(validation_result, dict)
        self.assertIn("valid", validation_result)
        self.assertTrue(validation_result["valid"])
    
    def test_electrical_task_validation(self: Self) -> None:
        """Test electrical task validation and expertise matching."""
        # Test power systems task
        power_validation = self.electrical_agent.validate_electrical_task(self.power_systems_task)
        self.assertTrue(power_validation["valid"])
        self.assertIn("power", power_validation["keywords_found"])
        
        # Test motor control task
        motor_validation = self.electrical_agent.validate_electrical_task(self.motor_control_task)
        self.assertTrue(motor_validation["valid"])
        self.assertIn("motor", motor_validation["keywords_found"])
        
        # Test PLC task
        plc_validation = self.electrical_agent.validate_electrical_task(self.plc_task)
        self.assertTrue(plc_validation["valid"])
        self.assertIn("plc", plc_validation["keywords_found"])
        
        # Test general task with low confidence
        general_task = AgentTask(
            query="General electrical question",
            domain=DomainType.ELECTRICAL,
            context={}
        )
        general_validation = self.electrical_agent.validate_electrical_task(general_task)
        self.assertTrue(general_validation["valid"])
        self.assertLess(general_validation["confidence"], 0.3)
        self.assertGreater(len(general_validation["suggestions"]), 0)
    
    async def test_electrical_task_processing(self: Self) -> None:
        """Test electrical task processing for different expertise areas."""
        # Test power systems processing
        power_result = await self.electrical_agent.process_electrical_task(self.power_systems_task)
        self.assertTrue(power_result["success"])
        self.assertEqual(power_result["expertise_area"], "power_systems")
        self.assertIn("response", power_result)
        self.assertIn("recommendations", power_result["response"])
        
        # Test motor control processing
        motor_result = await self.electrical_agent.process_electrical_task(self.motor_control_task)
        self.assertTrue(motor_result["success"])
        self.assertEqual(motor_result["expertise_area"], "motor_control")
        self.assertIn("control_strategies", motor_result["response"])
        
        # Test PLC processing
        plc_result = await self.electrical_agent.process_electrical_task(self.plc_task)
        self.assertTrue(plc_result["success"])
        self.assertEqual(plc_result["expertise_area"], "plc_programming")
        self.assertIn("programming_guidelines", plc_result["response"])
    
    def test_electrical_agent_status(self: Self) -> None:
        """Test electrical agent status reporting."""
        status = self.electrical_agent.get_agent_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("agent_id", status)
        self.assertIn("domain", status)
        self.assertIn("status", status)
        self.assertIn("expertise_areas", status)
        self.assertIn("specialization", status)
        
        self.assertEqual(status["specialization"], "Electrical Engineering")
        self.assertEqual(status["domain"], "electrical")


class TestIntegrationScenarios(unittest.TestCase):
    """Test suite for integration scenarios.
    
    Following crawl_mcp.py methodology for integration testing.
    """
    
    def setUp(self: Self) -> None:
        """Set up integration test environment."""
        self.coordination_framework = AgentCoordinationFramework(
            coordination_strategy=CoordinationStrategy.EXPERTISE_BASED
        )
        self.electrical_agent = ElectricalEngineeringAgent("integration_electrical_agent")
    
    async def test_agent_registration_and_task_submission(self: Self) -> None:
        """Test complete agent registration and task submission workflow."""
        # Step 1: Register agent with coordination framework
        registration_success = await self.coordination_framework.register_agent(self.electrical_agent)
        self.assertTrue(registration_success)
        
        # Verify agent is registered
        self.assertIn(self.electrical_agent.agent_id, self.coordination_framework.registered_agents)
        self.assertIn(
            self.electrical_agent.agent_id,
            self.coordination_framework.domain_agents[DomainType.ELECTRICAL]
        )
        
        # Step 2: Submit task
        test_task = AgentTask(
            query="Design motor control circuit for 50HP pump application",
            domain=DomainType.ELECTRICAL,
            context={"motor_hp": 50, "application": "pump"}
        )
        
        submission_result = await self.coordination_framework.submit_task(test_task)
        self.assertTrue(submission_result["success"])
        self.assertIn("task_id", submission_result)
        
        # Step 3: Verify task assignment
        self.assertIn(test_task.task_id, self.coordination_framework.active_tasks)
        
        # Step 4: Check coordination status
        status = self.coordination_framework.get_coordination_status()
        self.assertEqual(status["registered_agents"], 1)
        self.assertEqual(status["active_agents"], 1)
    
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
            query="Motor control analysis",
            domain=DomainType.ELECTRICAL,
            context={}
        )
        
        mechanical_task = AgentTask(
            query="Mechanical system design",
            domain=DomainType.MECHANICAL,
            context={}
        )
        
        # Submit tasks
        electrical_result = await self.coordination_framework.submit_task(electrical_task)
        mechanical_result = await self.coordination_framework.submit_task(mechanical_task)
        
        self.assertTrue(electrical_result["success"])
        self.assertTrue(mechanical_result["success"])
        
        # Verify coordination status
        status = self.coordination_framework.get_coordination_status()
        self.assertEqual(status["registered_agents"], 2)
        self.assertEqual(status["active_agents"], 2)
    
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
        self.assertEqual(len(self.coordination_framework.task_queue), 0)
        self.assertEqual(len(self.coordination_framework.active_tasks), 0)
        self.assertEqual(len(self.coordination_framework.registered_agents), 0)
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
                context={"task_number": i}
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
        self.assertEqual(successful_tasks, 10)
        
        # Performance assertion (should process 10 tasks in reasonable time)
        self.assertLess(processing_time, 5.0)  # 5 seconds max
        
        # Log performance metrics
        logger.info(f"Processed {len(tasks)} tasks in {processing_time:.2f} seconds")
        logger.info(f"Average time per task: {processing_time / len(tasks):.3f} seconds")
    
    def test_memory_usage(self: Self) -> None:
        """Test memory usage with large number of tasks."""
        import psutil
        import gc
        
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
                context={"task_id": i, "data": "x" * 100}  # Some test data
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
        logger.info(f"After creating {large_task_count} tasks: {after_creation_memory:.2f} MB")
        logger.info(f"After cleanup: {after_cleanup_memory:.2f} MB")
        
        # Memory should not grow excessively
        memory_growth = after_creation_memory - initial_memory
        self.assertLess(memory_growth, 100)  # Should not use more than 100MB for 1000 tasks


def run_phase_16_tests() -> Dict[str, Any]:
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
            runner = unittest.TextTestRunner(verbosity=2, stream=open(os.devnull, 'w'))
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
            test_results["passed_tests"] += result.testsRun - len(result.failures) - len(result.errors)
            test_results["failed_tests"] += len(result.failures) + len(result.errors)
            
            # Record any errors
            for failure in result.failures:
                test_results["errors"].append(f"FAILURE: {failure[0]} - {failure[1]}")
            for error in result.errors:
                test_results["errors"].append(f"ERROR: {error[0]} - {error[1]}")
            
            logger.info(f"Suite {suite_name}: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
            
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
    "TestMultiDomainArchitecture",
    "TestAgentCoordinationFramework", 
    "TestElectricalEngineeringAgent",
    "TestIntegrationScenarios",
    "TestPerformanceAndScalability",
    "run_phase_16_tests",
] 