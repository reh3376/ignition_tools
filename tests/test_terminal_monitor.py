"""Comprehensive Test Suite for Terminal Monitoring System.

This test suite follows the crawl_mcp.py methodology with:
1. Environment validation first
2. Comprehensive input validation using Pydantic models
3. Robust error handling with user-friendly messages
4. Modular testing approach with progressive complexity
5. Proper resource management with cleanup
"""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.terminal_monitor import (
    CommandRequest,
    CommandState,
    MonitoringConfig,
    RecoveryAction,
    TerminalMonitor,
)


class TestEnvironment(BaseModel):
    """Test environment configuration."""

    test_timeout: int = Field(
        default=30, ge=1, le=300, description="Test timeout in seconds"
    )
    temp_dir: str | None = Field(
        default=None, description="Temporary directory for tests"
    )
    cleanup_after_tests: bool = Field(default=True, description="Clean up after tests")
    parallel_test_limit: int = Field(
        default=3, ge=1, le=10, description="Maximum parallel tests"
    )


class TerminalMonitorTestSuite:
    """Comprehensive test suite for terminal monitoring system."""

    def __init__(self, test_env: TestEnvironment | None = None):
        """Initialize test suite.

        Args:
            test_env: Test environment configuration
        """
        self.test_env = test_env or TestEnvironment()
        self.monitor: TerminalMonitor | None = None
        self.temp_dir: Path | None = None
        self.test_results: dict[str, Any] = {}

    def validate_test_environment(self) -> dict[str, Any]:
        """Validate test environment following crawl_mcp.py methodology.

        Returns:
            Environment validation results
        """
        validation_results = {
            "python_available": False,
            "subprocess_available": False,
            "psutil_available": False,
            "asyncio_available": False,
            "temp_dir_writable": False,
            "terminal_commands_available": False,
            "system_resources_sufficient": False,
        }

        try:
            # Python version check
            validation_results["python_available"] = sys.version_info >= (3, 8)

            # Core modules availability
            try:
                import subprocess

                validation_results["subprocess_available"] = True
            except ImportError:
                pass

            try:
                import psutil

                validation_results["psutil_available"] = True
            except ImportError:
                pass

            try:
                import asyncio

                validation_results["asyncio_available"] = True
            except ImportError:
                pass

            # Create temporary directory for tests
            try:
                self.temp_dir = Path(tempfile.mkdtemp(prefix="terminal_monitor_test_"))
                test_file = self.temp_dir / "test_write.txt"
                test_file.write_text("test")
                test_file.unlink()
                validation_results["temp_dir_writable"] = True
            except Exception:
                pass

            # Test basic terminal commands
            try:
                result = subprocess.run(
                    ["echo", "test"], capture_output=True, text=True, timeout=5
                )
                validation_results["terminal_commands_available"] = (
                    result.returncode == 0
                )
            except Exception:
                pass

            # System resources check
            try:
                import psutil

                memory = psutil.virtual_memory()
                cpu_count = psutil.cpu_count()
                validation_results["system_resources_sufficient"] = (
                    memory.available > 512 * 1024 * 1024 and cpu_count >= 1  # 512MB
                )
            except Exception:
                pass

        except Exception as e:
            validation_results["validation_error"] = str(e)

        return validation_results

    async def setup_test_suite(self) -> bool:
        """Set up test suite with environment validation.

        Returns:
            True if setup successful
        """
        try:
            # Environment validation first (crawl_mcp.py principle)
            env_validation = self.validate_test_environment()

            required_components = [
                "python_available",
                "subprocess_available",
                "psutil_available",
                "asyncio_available",
                "temp_dir_writable",
                "terminal_commands_available",
            ]

            missing_components = [
                comp
                for comp in required_components
                if not env_validation.get(comp, False)
            ]

            if missing_components:
                raise RuntimeError(
                    f"Missing required test components: {missing_components}"
                )

            # Initialize monitor with test configuration
            test_config = MonitoringConfig(
                check_interval=0.5,  # Faster for testing
                default_timeout=10,  # Shorter for testing
                max_retries=2,  # Fewer retries for testing
                max_concurrent_commands=3,
                cleanup_interval=60,
            )

            self.monitor = TerminalMonitor(test_config)

            # Start monitoring
            if not self.monitor.start_monitoring():
                raise RuntimeError("Failed to start monitoring")

            return True

        except Exception as e:
            raise RuntimeError(f"Test suite setup failed: {e}")

    async def teardown_test_suite(self):
        """Clean up test suite resources."""
        try:
            # Stop monitoring
            if self.monitor:
                self.monitor.stop_monitoring()

            # Clean up temp directory
            if (
                self.temp_dir
                and self.temp_dir.exists()
                and self.test_env.cleanup_after_tests
            ):
                import shutil

                shutil.rmtree(self.temp_dir, ignore_errors=True)

        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")

    async def test_basic_command_execution(self) -> dict[str, Any]:
        """Test basic command execution functionality."""
        test_name = "basic_command_execution"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0,
        }

        start_time = time.time()

        try:
            # Test simple echo command
            request = CommandRequest(command=["echo", "Hello, World!"])
            execution = await self.monitor.execute_command(request)

            test_result["details"]["echo_test"] = {
                "state": execution.state.value,
                "return_code": execution.return_code,
                "stdout": execution.stdout.strip(),
                "stderr": execution.stderr.strip(),
                "duration": execution.metrics.get_duration(),
            }

            # Validate results
            if (
                execution.state == CommandState.COMPLETED
                and execution.return_code == 0
                and "Hello, World!" in execution.stdout
            ):
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append("Echo command did not execute correctly")

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Test execution failed: {e}")

        finally:
            test_result["duration"] = time.time() - start_time

        return test_result

    async def test_timeout_handling(self) -> dict[str, Any]:
        """Test command timeout handling."""
        test_name = "timeout_handling"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0,
        }

        start_time = time.time()

        try:
            # Test command that should timeout
            request = CommandRequest(
                command=["sleep", "10"],
                timeout=2,
                max_retries=0,  # Disable retries for this test
            )
            execution = await self.monitor.execute_command(request)

            test_result["details"]["timeout_test"] = {
                "state": execution.state.value,
                "return_code": execution.return_code,
                "duration": execution.metrics.get_duration(),
                "errors": execution.errors,
                "warnings": execution.warnings,
            }

            # Validate timeout was handled
            if execution.state == CommandState.TIMEOUT:
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append(
                    f"Expected timeout, got state: {execution.state}"
                )

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Test execution failed: {e}")

        finally:
            test_result["duration"] = time.time() - start_time

        return test_result

    async def test_error_handling(self) -> dict[str, Any]:
        """Test error handling for invalid commands."""
        test_name = "error_handling"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0,
        }

        start_time = time.time()

        try:
            # Test invalid command
            request = CommandRequest(command=["nonexistent_command_12345"])
            execution = await self.monitor.execute_command(request)

            test_result["details"]["invalid_command_test"] = {
                "state": execution.state.value,
                "return_code": execution.return_code,
                "stderr": execution.stderr,
                "errors": execution.errors,
            }

            # Validate error was handled
            if execution.state == CommandState.FAILED and execution.return_code != 0:
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append(
                    f"Expected failure, got state: {execution.state}"
                )

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Test execution failed: {e}")

        finally:
            test_result["duration"] = time.time() - start_time

        return test_result

    async def test_concurrent_execution(self) -> dict[str, Any]:
        """Test concurrent command execution."""
        test_name = "concurrent_execution"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0,
        }

        start_time = time.time()

        try:
            # Create multiple concurrent commands
            commands = [
                CommandRequest(command=["echo", f"Command {i}"]) for i in range(3)
            ]

            # Execute concurrently
            tasks = [self.monitor.execute_command(cmd) for cmd in commands]
            executions = await asyncio.gather(*tasks)

            test_result["details"]["concurrent_test"] = {
                "total_commands": len(executions),
                "successful_commands": sum(
                    1 for e in executions if e.state == CommandState.COMPLETED
                ),
                "failed_commands": sum(
                    1 for e in executions if e.state == CommandState.FAILED
                ),
                "executions": [
                    {
                        "state": e.state.value,
                        "return_code": e.return_code,
                        "stdout": e.stdout.strip(),
                        "duration": e.metrics.get_duration(),
                    }
                    for e in executions
                ],
            }

            # Validate all commands succeeded
            if all(e.state == CommandState.COMPLETED for e in executions):
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append(
                    "Not all concurrent commands completed successfully"
                )

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Test execution failed: {e}")

        finally:
            test_result["duration"] = time.time() - start_time

        return test_result

    async def test_recovery_mechanisms(self) -> dict[str, Any]:
        """Test auto-recovery mechanisms."""
        test_name = "recovery_mechanisms"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0,
        }

        start_time = time.time()

        try:
            # Test retry recovery with a command that fails initially
            # Create a script that fails first time, succeeds second time
            if self.temp_dir:
                script_path = self.temp_dir / "retry_test.py"
                script_content = """
import sys
import os

flag_file = "/tmp/retry_test_flag"
if os.path.exists(flag_file):
    print("Success on retry!")
    os.remove(flag_file)
    sys.exit(0)
else:
    with open(flag_file, "w") as f:
        f.write("failed")
    print("First attempt failed", file=sys.stderr)
    sys.exit(1)
"""
                script_path.write_text(script_content)

                request = CommandRequest(
                    command=[sys.executable, str(script_path)],
                    max_retries=2,
                    recovery_actions=[RecoveryAction.RETRY],
                )

                execution = await self.monitor.execute_command(request)

                test_result["details"]["retry_recovery_test"] = {
                    "state": execution.state.value,
                    "return_code": execution.return_code,
                    "retry_count": execution.retry_count,
                    "recovery_attempts": execution.recovery_attempts,
                    "stdout": execution.stdout.strip(),
                    "stderr": execution.stderr.strip(),
                }

                # Validate recovery worked
                if (
                    execution.state in [CommandState.COMPLETED, CommandState.RECOVERED]
                    and execution.retry_count > 0
                ):
                    test_result["status"] = "passed"
                else:
                    test_result["status"] = "failed"
                    test_result["errors"].append(
                        "Recovery mechanism did not work as expected"
                    )
            else:
                test_result["status"] = "skipped"
                test_result["errors"].append(
                    "No temp directory available for recovery test"
                )

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Test execution failed: {e}")

        finally:
            test_result["duration"] = time.time() - start_time

        return test_result

    async def test_monitoring_statistics(self) -> dict[str, Any]:
        """Test monitoring statistics collection."""
        test_name = "monitoring_statistics"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0,
        }

        start_time = time.time()

        try:
            # Get initial statistics
            initial_stats = self.monitor.get_statistics()

            # Execute a few commands
            commands = [
                CommandRequest(command=["echo", "stats test 1"]),
                CommandRequest(command=["echo", "stats test 2"]),
                CommandRequest(command=["nonexistent_command"]),  # This should fail
            ]

            for cmd in commands:
                try:
                    await self.monitor.execute_command(cmd)
                except:
                    pass  # Expected for invalid command

            # Get final statistics
            final_stats = self.monitor.get_statistics()

            test_result["details"]["statistics_test"] = {
                "initial_stats": initial_stats,
                "final_stats": final_stats,
                "commands_executed": final_stats["total_commands"]
                - initial_stats["total_commands"],
                "success_rate": final_stats["success_rate"],
            }

            # Validate statistics were updated
            if final_stats["total_commands"] > initial_stats["total_commands"]:
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append("Statistics were not updated correctly")

        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Test execution failed: {e}")

        finally:
            test_result["duration"] = time.time() - start_time

        return test_result

    async def run_comprehensive_tests(self) -> dict[str, Any]:
        """Run comprehensive test suite following crawl_mcp.py methodology.

        Returns:
            Complete test results
        """
        print("🧪 Starting Terminal Monitor Comprehensive Test Suite")

        # Setup test suite
        try:
            await self.setup_test_suite()
            print("✅ Test suite setup completed")
        except Exception as e:
            return {"setup_failed": True, "error": str(e), "timestamp": time.time()}

        # Define test sequence (progressive complexity)
        test_sequence = [
            ("Environment Validation", self.validate_test_environment),
            ("Basic Command Execution", self.test_basic_command_execution),
            ("Error Handling", self.test_error_handling),
            ("Timeout Handling", self.test_timeout_handling),
            ("Concurrent Execution", self.test_concurrent_execution),
            ("Recovery Mechanisms", self.test_recovery_mechanisms),
            ("Monitoring Statistics", self.test_monitoring_statistics),
        ]

        # Execute tests
        test_results = {
            "suite_name": "Terminal Monitor Comprehensive Tests",
            "start_time": time.time(),
            "tests": [],
            "summary": {
                "total_tests": len(test_sequence),
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "total_duration": 0.0,
            },
        }

        for test_name, test_func in test_sequence:
            print(f"🔍 Running: {test_name}")

            try:
                if test_name == "Environment Validation":
                    # Special handling for environment validation
                    result = test_func()
                    test_result = {
                        "name": test_name,
                        "status": "passed" if all(result.values()) else "failed",
                        "details": result,
                        "errors": [],
                        "duration": 0.0,
                    }
                else:
                    test_result = await test_func()

                test_results["tests"].append(test_result)

                # Update summary
                if test_result["status"] == "passed":
                    test_results["summary"]["passed_tests"] += 1
                    print(f"✅ {test_name}: PASSED")
                elif test_result["status"] == "failed":
                    test_results["summary"]["failed_tests"] += 1
                    print(f"❌ {test_name}: FAILED")
                    if test_result["errors"]:
                        for error in test_result["errors"]:
                            print(f"   Error: {error}")
                else:
                    test_results["summary"]["skipped_tests"] += 1
                    print(f"⏭️  {test_name}: SKIPPED")

                test_results["summary"]["total_duration"] += test_result.get(
                    "duration", 0.0
                )

            except Exception as e:
                error_result = {
                    "name": test_name,
                    "status": "failed",
                    "details": {},
                    "errors": [f"Test execution exception: {e}"],
                    "duration": 0.0,
                }
                test_results["tests"].append(error_result)
                test_results["summary"]["failed_tests"] += 1
                print(f"❌ {test_name}: EXCEPTION - {e}")

        # Cleanup
        await self.teardown_test_suite()

        # Final summary
        test_results["end_time"] = time.time()
        test_results["total_execution_time"] = (
            test_results["end_time"] - test_results["start_time"]
        )

        success_rate = (
            test_results["summary"]["passed_tests"]
            / test_results["summary"]["total_tests"]
        ) * 100

        print("\n📊 Test Suite Complete:")
        print(f"   Total Tests: {test_results['summary']['total_tests']}")
        print(f"   Passed: {test_results['summary']['passed_tests']}")
        print(f"   Failed: {test_results['summary']['failed_tests']}")
        print(f"   Skipped: {test_results['summary']['skipped_tests']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Duration: {test_results['total_execution_time']:.2f}s")

        return test_results


async def run_terminal_monitor_tests():
    """Run terminal monitor tests."""
    test_suite = TerminalMonitorTestSuite()
    results = await test_suite.run_comprehensive_tests()

    # Save results
    results_file = Path("terminal_monitor_test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {results_file}")

    return results


if __name__ == "__main__":
    """Run the test suite."""
    asyncio.run(run_terminal_monitor_tests())
