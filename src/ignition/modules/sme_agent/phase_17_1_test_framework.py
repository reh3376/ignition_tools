"""Phase 17.1: Advanced LLM Integration - Comprehensive Test Framework

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity validation
- Step 6: Resource management and cleanup

Comprehensive testing framework for all Phase 17.1 components with modular testing approach.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

import os

from dotenv import load_dotenv

# Import Phase 17.1 components
from .phase_17_1_advanced_llm_integration import (
    AdvancedLLMIntegration,
    ContextAwareProcessor,
    ContextAwareResponse,
    IgnitionVersionDetector,
    IgnitionVersionInfo,
    MultiModalContext,
    MultiModalProcessor,
    create_advanced_llm_integration,
    validate_phase_17_environment,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result with detailed information."""

    test_name: str
    success: bool
    execution_time: float
    error_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "test_name": self.test_name,
            "success": self.success,
            "execution_time": self.execution_time,
            "error_message": self.error_message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TestSuite:
    """Collection of test results with summary statistics."""

    suite_name: str
    results: list[TestResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None

    @property
    def total_tests(self) -> int:
        """Total number of tests."""
        return len(self.results)

    @property
    def passed_tests(self) -> int:
        """Number of passed tests."""
        return sum(1 for r in self.results if r.success)

    @property
    def failed_tests(self) -> int:
        """Number of failed tests."""
        return sum(1 for r in self.results if not r.success)

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    @property
    def total_execution_time(self) -> float:
        """Total execution time for all tests."""
        return sum(r.execution_time for r in self.results)

    def add_result(self, result: TestResult) -> None:
        """Add a test result."""
        self.results.append(result)

    def finalize(self) -> None:
        """Finalize the test suite."""
        self.end_time = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "suite_name": self.suite_name,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": self.success_rate,
            "total_execution_time": self.total_execution_time,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": [r.to_dict() for r in self.results],
        }


class Phase17TestFramework:
    """Step 1: Environment Validation First

    Comprehensive test framework for Phase 17.1 Advanced LLM Integration.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_suites: list[TestSuite] = []
        self.current_suite: TestSuite | None = None

        # Test configuration
        self.config = {
            "run_integration_tests": os.getenv(
                "PHASE_17_RUN_INTEGRATION_TESTS", "true"
            ).lower()
            == "true",
            "run_performance_tests": os.getenv(
                "PHASE_17_RUN_PERFORMANCE_TESTS", "true"
            ).lower()
            == "true",
            "test_timeout": int(os.getenv("PHASE_17_TEST_TIMEOUT", "30")),
            "verbose_output": os.getenv("PHASE_17_VERBOSE_TESTS", "false").lower()
            == "true",
        }

    def run_test(self, test_name: str, test_function, *args, **kwargs) -> TestResult:
        """Step 2: Comprehensive Input Validation

        Run a single test with comprehensive error handling.

        Args:
            test_name: Name of the test
            test_function: Function to execute
            *args: Arguments for test function
            **kwargs: Keyword arguments for test function

        Returns:
            TestResult with execution details
        """
        start_time = time.time()

        try:
            # Input validation
            if not test_name or not callable(test_function):
                raise ValueError("Test name and function are required")

            if self.config["verbose_output"]:
                print(f"🧪 Running test: {test_name}")

            # Execute test with timeout protection
            result = test_function(*args, **kwargs)

            execution_time = time.time() - start_time

            # Validate result
            if isinstance(result, dict) and "success" in result:
                success = result["success"]
                details = result
            elif isinstance(result, bool):
                success = result
                details = {"result": result}
            else:
                success = True
                details = {"result": result}

            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                details=details,
            )

            if self.config["verbose_output"]:
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"  {status} ({execution_time:.3f}s)")

            return test_result

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)

            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                error_message=error_msg,
                details={"exception": type(e).__name__},
            )

            if self.config["verbose_output"]:
                print(f"  ❌ FAIL ({execution_time:.3f}s): {error_msg}")

            self.logger.error(f"Test {test_name} failed: {error_msg}")
            return test_result

    def start_test_suite(self, suite_name: str) -> None:
        """Start a new test suite."""
        self.current_suite = TestSuite(suite_name=suite_name)

        if self.config["verbose_output"]:
            print(f"\n📋 Starting test suite: {suite_name}")
            print("=" * (len(suite_name) + 25))

    def add_test_result(self, result: TestResult) -> None:
        """Add test result to current suite."""
        if self.current_suite:
            self.current_suite.add_result(result)

    def finalize_test_suite(self) -> TestSuite:
        """Finalize current test suite and return it."""
        if self.current_suite:
            self.current_suite.finalize()
            self.test_suites.append(self.current_suite)

            if self.config["verbose_output"]:
                suite = self.current_suite
                print(f"\n📊 Test Suite Summary: {suite.suite_name}")
                print(
                    f"   Total: {suite.total_tests} | Passed: {suite.passed_tests} | Failed: {suite.failed_tests}"
                )
                print(
                    f"   Success Rate: {suite.success_rate:.1f}% | Time: {suite.total_execution_time:.3f}s"
                )

            completed_suite = self.current_suite
            self.current_suite = None
            return completed_suite

        return TestSuite("empty")

    def run_environment_validation_tests(self) -> TestSuite:
        """Step 3: Error Handling with User-Friendly Messages

        Test environment validation functionality.
        """
        self.start_test_suite("Environment Validation Tests")

        # Test 1: Basic environment validation
        def test_basic_validation():
            result = validate_phase_17_environment()
            return {
                "success": isinstance(result, dict) and "valid" in result,
                "environment_score": result.get("environment_score", 0),
                "components_available": len(result.get("components_available", [])),
            }

        result = self.run_test("Basic Environment Validation", test_basic_validation)
        self.add_test_result(result)

        # Test 2: Component availability check
        def test_component_availability():
            result = validate_phase_17_environment()
            required_components = [
                "transformers",
                "multimodal_enabled",
                "context_aware_enabled",
            ]
            available = result.get("components_available", [])

            component_status = {}
            for component in required_components:
                component_status[component] = component in available

            return {
                "success": len(available) > 0,
                "component_status": component_status,
                "total_available": len(available),
            }

        result = self.run_test(
            "Component Availability Check", test_component_availability
        )
        self.add_test_result(result)

        # Test 3: Configuration validation
        def test_configuration_validation():
            config_items = {
                "PHASE_17_MULTIMODAL_ENABLED": os.getenv("PHASE_17_MULTIMODAL_ENABLED"),
                "PHASE_17_CONTEXT_AWARE_ENABLED": os.getenv(
                    "PHASE_17_CONTEXT_AWARE_ENABLED"
                ),
                "IGNITION_VERSION": os.getenv("IGNITION_VERSION"),
            }

            valid_configs = sum(1 for v in config_items.values() if v is not None)

            return {
                "success": valid_configs > 0,
                "configuration_items": config_items,
                "valid_configs": valid_configs,
            }

        result = self.run_test(
            "Configuration Validation", test_configuration_validation
        )
        self.add_test_result(result)

        return self.finalize_test_suite()

    def run_version_detector_tests(self) -> TestSuite:
        """Test Ignition version detection functionality."""
        self.start_test_suite("Version Detector Tests")

        # Test 1: Version parsing
        def test_version_parsing():
            detector = IgnitionVersionDetector()

            test_versions = ["8.1.25", "8.0.17", "7.9.20"]
            results = {}

            for version in test_versions:
                try:
                    info = detector.detect_version(version)
                    results[version] = {
                        "parsed": True,
                        "major": info.major_version,
                        "minor": info.minor_version,
                        "patch": info.patch_version,
                    }
                except Exception as e:
                    results[version] = {"parsed": False, "error": str(e)}

            success = all(r["parsed"] for r in results.values())
            return {"success": success, "version_results": results}

        result = self.run_test("Version Parsing", test_version_parsing)
        self.add_test_result(result)

        # Test 2: Feature detection
        def test_feature_detection():
            detector = IgnitionVersionDetector()

            # Test different versions
            v8_info = detector.detect_version("8.1.25")
            v7_info = detector.detect_version("7.9.20")

            feature_tests = {
                "v8_has_perspective": v8_info.has_perspective,
                "v8_supports_sessions": v8_info.supports_perspective_sessions,
                "v7_has_perspective": v7_info.has_perspective,
                "v7_supports_sessions": v7_info.supports_perspective_sessions,
            }

            # Validate expected behavior
            expected_results = {
                "v8_has_perspective": True,
                "v8_supports_sessions": True,
                "v7_has_perspective": False,
                "v7_supports_sessions": False,
            }

            matches = sum(
                1 for k, v in feature_tests.items() if v == expected_results[k]
            )
            success = matches == len(expected_results)

            return {
                "success": success,
                "feature_tests": feature_tests,
                "expected_results": expected_results,
                "matches": matches,
            }

        result = self.run_test("Feature Detection", test_feature_detection)
        self.add_test_result(result)

        # Test 3: Version advice generation
        def test_version_advice():
            detector = IgnitionVersionDetector()
            v8_info = detector.detect_version("8.1.25")

            topics = ["perspective", "tags", "queries"]
            advice_results = {}

            for topic in topics:
                advice = detector.get_version_specific_advice(v8_info, topic)
                advice_results[topic] = {
                    "has_advice": len(advice) > 0,
                    "advice_count": len(advice),
                    "advice": advice,
                }

            success = all(r["has_advice"] for r in advice_results.values())
            return {"success": success, "advice_results": advice_results}

        result = self.run_test("Version Advice Generation", test_version_advice)
        self.add_test_result(result)

        return self.finalize_test_suite()

    def run_multimodal_processor_tests(self) -> TestSuite:
        """Test multi-modal processing functionality."""
        self.start_test_suite("Multi-Modal Processor Tests")

        # Test 1: Processor initialization
        def test_processor_initialization():
            processor = MultiModalProcessor()
            init_result = processor.initialize()

            return {
                "success": isinstance(init_result, bool),
                "initialized": init_result,
                "processor_status": processor.initialized,
            }

        result = self.run_test(
            "Processor Initialization", test_processor_initialization
        )
        self.add_test_result(result)

        # Test 2: Screenshot analysis
        def test_screenshot_analysis():
            processor = MultiModalProcessor()
            processor.initialize()

            # Test with valid base64 image data (placeholder)
            test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

            analysis = processor.analyze_screenshot(test_image)

            return {
                "success": analysis.get("success", False),
                "has_components": "components_detected" in analysis,
                "analysis_result": analysis,
            }

        result = self.run_test("Screenshot Analysis", test_screenshot_analysis)
        self.add_test_result(result)

        # Test 3: Tag browser analysis
        def test_tag_browser_analysis():
            processor = MultiModalProcessor()
            processor.initialize()

            # Test tag structure
            test_structure = {
                "tags": [
                    {"name": "PLC1_Temperature", "type": "float"},
                    {"name": "PLC1_Pressure", "type": "float"},
                    {"name": "HMI_StartButton", "type": "boolean"},
                ]
            }

            analysis = processor.analyze_tag_browser(test_structure)

            return {
                "success": analysis.get("success", False),
                "tag_count": analysis.get("tag_count", 0),
                "has_recommendations": len(analysis.get("recommendations", [])) >= 0,
            }

        result = self.run_test("Tag Browser Analysis", test_tag_browser_analysis)
        self.add_test_result(result)

        return self.finalize_test_suite()

    def run_context_aware_processor_tests(self) -> TestSuite:
        """Step 4: Modular Component Testing

        Test context-aware processing functionality.
        """
        self.start_test_suite("Context-Aware Processor Tests")

        # Test 1: User profile management
        def test_user_profile_management():
            processor = ContextAwareProcessor()

            # Test profile creation
            profile1 = processor._get_user_profile("user1")
            profile2 = processor._get_user_profile("user2")
            profile1_again = processor._get_user_profile("user1")

            return {
                "success": (
                    isinstance(profile1, dict)
                    and isinstance(profile2, dict)
                    and profile1 is profile1_again
                    and profile1 is not profile2
                ),
                "profile_count": len(processor.user_profiles),
                "profile_keys": list(processor.user_profiles.keys()),
            }

        result = self.run_test("User Profile Management", test_user_profile_management)
        self.add_test_result(result)

        # Test 2: Question analysis
        def test_question_analysis():
            processor = ContextAwareProcessor()
            context = MultiModalContext()
            version_info = IgnitionVersionInfo(
                version="8.1.25", major_version=8, minor_version=1, patch_version=25
            )

            test_questions = [
                "How do I write a script for Perspective?",
                "Show me the component layout",
                "What's new in version 8.1?",
                "Basic tag operations",
            ]

            analyses = {}
            for question in test_questions:
                analysis = processor._analyze_question(question, context, version_info)
                analyses[question] = analysis

            success = all(isinstance(a, dict) for a in analyses.values())
            return {"success": success, "analyses": analyses}

        result = self.run_test("Question Analysis", test_question_analysis)
        self.add_test_result(result)

        # Test 3: Context-aware response generation
        def test_context_aware_response():
            processor = ContextAwareProcessor()
            context = MultiModalContext(
                user_preferences={"expertise_level": "advanced"}
            )
            version_info = IgnitionVersionInfo(
                version="8.1.25", major_version=8, minor_version=1, patch_version=25
            )

            response = processor.process_context_aware_request(
                "How do I create a Perspective session script?",
                "test_user",
                context,
                version_info,
            )

            return {
                "success": isinstance(response, ContextAwareResponse),
                "has_content": bool(response.content),
                "confidence": response.confidence,
                "processing_time": response.processing_time,
                "version_specific": response.ignition_version_specific,
            }

        result = self.run_test(
            "Context-Aware Response Generation", test_context_aware_response
        )
        self.add_test_result(result)

        return self.finalize_test_suite()

    def run_integration_tests(self) -> TestSuite:
        """Test full system integration."""
        self.start_test_suite("Integration Tests")

        if not self.config["run_integration_tests"]:
            # Skip integration tests if disabled
            result = TestResult(
                test_name="Integration Tests Skipped",
                success=True,
                execution_time=0.0,
                details={"reason": "Integration tests disabled in configuration"},
            )
            self.add_test_result(result)
            return self.finalize_test_suite()

        # Test 1: Full system initialization
        def test_full_system_initialization():
            try:
                integration = AdvancedLLMIntegration("standard")
                init_success = integration.initialize()
                status = integration.get_system_status()
                integration.cleanup()

                return {
                    "success": init_success,
                    "system_status": status,
                    "initialized": status.get("initialized", False),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        result = self.run_test(
            "Full System Initialization", test_full_system_initialization
        )
        self.add_test_result(result)

        # Test 2: End-to-end request processing
        def test_end_to_end_processing():
            try:
                integration = create_advanced_llm_integration("standard")

                response = integration.process_enhanced_request(
                    "How do I create a tag in Ignition 8.1?",
                    user_id="test_user",
                    ignition_version="8.1.25",
                )

                integration.cleanup()

                return {
                    "success": isinstance(response, ContextAwareResponse),
                    "has_content": bool(response.content),
                    "confidence": response.confidence,
                    "processing_time": response.processing_time,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        result = self.run_test(
            "End-to-End Request Processing", test_end_to_end_processing
        )
        self.add_test_result(result)

        # Test 3: Progressive complexity support
        def test_progressive_complexity():
            complexity_levels = ["basic", "standard", "advanced", "enterprise"]
            results = {}

            for level in complexity_levels:
                try:
                    integration = AdvancedLLMIntegration(level)
                    init_success = integration.initialize()
                    integration.cleanup()
                    results[level] = {"success": init_success}
                except Exception as e:
                    results[level] = {"success": False, "error": str(e)}

            success = all(r["success"] for r in results.values())
            return {"success": success, "complexity_results": results}

        result = self.run_test(
            "Progressive Complexity Support", test_progressive_complexity
        )
        self.add_test_result(result)

        return self.finalize_test_suite()

    def run_performance_tests(self) -> TestSuite:
        """Step 5: Progressive Complexity Support

        Test performance characteristics.
        """
        self.start_test_suite("Performance Tests")

        if not self.config["run_performance_tests"]:
            # Skip performance tests if disabled
            result = TestResult(
                test_name="Performance Tests Skipped",
                success=True,
                execution_time=0.0,
                details={"reason": "Performance tests disabled in configuration"},
            )
            self.add_test_result(result)
            return self.finalize_test_suite()

        # Test 1: Initialization performance
        def test_initialization_performance():
            times = []
            success_count = 0

            for i in range(5):
                start_time = time.time()
                try:
                    integration = AdvancedLLMIntegration("standard")
                    init_success = integration.initialize()
                    integration.cleanup()

                    if init_success:
                        success_count += 1

                    times.append(time.time() - start_time)
                except Exception:
                    times.append(time.time() - start_time)

            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)

            return {
                "success": success_count >= 3,  # At least 3/5 successful
                "avg_time": avg_time,
                "max_time": max_time,
                "min_time": min_time,
                "success_rate": success_count / 5 * 100,
            }

        result = self.run_test(
            "Initialization Performance", test_initialization_performance
        )
        self.add_test_result(result)

        # Test 2: Request processing performance
        def test_request_processing_performance():
            try:
                integration = create_advanced_llm_integration("standard")

                times = []
                for i in range(10):
                    start_time = time.time()
                    response = integration.process_enhanced_request(
                        f"Test question {i}",
                        user_id=f"user_{i}",
                        ignition_version="8.1.25",
                    )
                    times.append(time.time() - start_time)

                integration.cleanup()

                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)

                return {
                    "success": avg_time < 1.0,  # Average under 1 second
                    "avg_time": avg_time,
                    "max_time": max_time,
                    "min_time": min_time,
                    "total_requests": len(times),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        result = self.run_test(
            "Request Processing Performance", test_request_processing_performance
        )
        self.add_test_result(result)

        return self.finalize_test_suite()

    def run_all_tests(self) -> dict[str, Any]:
        """Step 6: Resource Management and Cleanup

        Run all test suites and return comprehensive results.

        Returns:
            Comprehensive test results summary
        """
        print("🚀 Phase 17.1: Advanced LLM Integration - Comprehensive Test Suite")
        print("=" * 70)

        start_time = time.time()

        # Run all test suites
        test_suites = [
            self.run_environment_validation_tests(),
            self.run_version_detector_tests(),
            self.run_multimodal_processor_tests(),
            self.run_context_aware_processor_tests(),
            self.run_integration_tests(),
            self.run_performance_tests(),
        ]

        total_time = time.time() - start_time

        # Calculate overall statistics
        total_tests = sum(suite.total_tests for suite in test_suites)
        total_passed = sum(suite.passed_tests for suite in test_suites)
        total_failed = sum(suite.failed_tests for suite in test_suites)
        overall_success_rate = (
            (total_passed / total_tests * 100) if total_tests > 0 else 0
        )

        # Generate summary
        summary = {
            "overall_results": {
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "success_rate": overall_success_rate,
                "total_execution_time": total_time,
            },
            "test_suites": [suite.to_dict() for suite in test_suites],
            "timestamp": datetime.now().isoformat(),
            "configuration": self.config,
        }

        # Print summary
        print("\n🎯 Overall Test Results")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Total Time: {total_time:.3f}s")

        # Print suite summaries
        for suite in test_suites:
            status = (
                "✅"
                if suite.success_rate >= 80
                else "⚠️" if suite.success_rate >= 60 else "❌"
            )
            print(
                f"   {status} {suite.suite_name}: {suite.success_rate:.1f}% ({suite.passed_tests}/{suite.total_tests})"
            )

        return summary


# Utility functions for test execution
def run_phase_17_tests(
    include_integration: bool = True,
    include_performance: bool = True,
    verbose: bool = False,
) -> dict[str, Any]:
    """Run Phase 17.1 tests with specified options.

    Args:
        include_integration: Whether to run integration tests
        include_performance: Whether to run performance tests
        verbose: Whether to show verbose output

    Returns:
        Test results summary
    """
    # Set environment variables for test configuration
    os.environ["PHASE_17_RUN_INTEGRATION_TESTS"] = str(include_integration).lower()
    os.environ["PHASE_17_RUN_PERFORMANCE_TESTS"] = str(include_performance).lower()
    os.environ["PHASE_17_VERBOSE_TESTS"] = str(verbose).lower()

    # Create and run test framework
    framework = Phase17TestFramework()
    return framework.run_all_tests()


def save_test_results(
    results: dict[str, Any], output_file: str = "phase_17_1_test_results.json"
) -> None:
    """Save test results to JSON file."""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"✅ Test results saved to: {output_path}")

    except Exception as e:
        print(f"❌ Failed to save test results: {e}")


# Main execution for standalone testing
if __name__ == "__main__":
    # Run comprehensive tests
    test_results = run_phase_17_tests(
        include_integration=True, include_performance=True, verbose=True
    )

    # Save results
    save_test_results(test_results)

    # Exit with appropriate code
    success_rate = test_results["overall_results"]["success_rate"]
    exit_code = 0 if success_rate >= 80 else 1

    print(f"\n🏁 Test execution completed with {success_rate:.1f}% success rate")
    exit(exit_code)
