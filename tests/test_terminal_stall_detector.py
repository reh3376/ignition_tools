"""Comprehensive Test Suite for Terminal Stall Detection System.

Following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation using Pydantic models
3. Robust error handling with user-friendly messages
4. Modular testing approach with progressive complexity
5. Proper resource management with cleanup
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.terminal_stall_detector import (
    CommandState, RecoveryAction, StallDetectorConfig, MonitoredCommandRequest,
    CommandExecution, TerminalStallDetector, execute_with_stall_detection,
    format_stall_error
)


class TestConfig(BaseModel):
    """Test configuration."""
    
    test_timeout: int = Field(default=60, ge=10, le=300, description="Test timeout in seconds")
    temp_dir: Optional[str] = Field(default=None, description="Temporary directory for tests")
    cleanup_after_tests: bool = Field(default=True, description="Clean up after tests")
    verbose_output: bool = Field(default=True, description="Enable verbose test output")


class StallDetectorTestSuite:
    """Comprehensive test suite for terminal stall detection system."""
    
    def __init__(self, test_config: Optional[TestConfig] = None):
        """Initialize test suite.
        
        Args:
            test_config: Test configuration
        """
        self.test_config = test_config or TestConfig()
        self.detector: Optional[TerminalStallDetector] = None
        self.temp_dir: Optional[Path] = None
        self.test_results: Dict[str, Any] = {}
        
    def validate_test_environment(self) -> Dict[str, Any]:
        """Validate test environment following crawl_mcp.py methodology.
        
        Returns:
            Environment validation results
        """
        validation_results = {
            "python_version_ok": False,
            "required_modules_available": False,
            "temp_dir_writable": False,
            "basic_commands_work": False,
            "async_support_available": False,
            "signal_handling_available": False
        }
        
        try:
            # Python version check
            validation_results["python_version_ok"] = sys.version_info >= (3, 8)
            
            # Required modules check
            try:
                import subprocess
                import threading
                import signal
                import asyncio
                from pydantic import BaseModel
                validation_results["required_modules_available"] = True
            except ImportError:
                pass
            
            # Async support check
            try:
                import asyncio
                validation_results["async_support_available"] = True
            except ImportError:
                pass
            
            # Signal handling check
            try:
                import signal
                validation_results["signal_handling_available"] = hasattr(signal, 'SIGINT')
            except ImportError:
                pass
            
            # Create temporary directory for tests
            try:
                self.temp_dir = Path(tempfile.mkdtemp(prefix="stall_detector_test_"))
                test_file = self.temp_dir / "test_write.txt"
                test_file.write_text("test")
                test_file.unlink()
                validation_results["temp_dir_writable"] = True
            except Exception:
                pass
            
            # Test basic command execution
            try:
                import subprocess
                result = subprocess.run(["echo", "test"], capture_output=True, text=True, timeout=5)
                validation_results["basic_commands_work"] = result.returncode == 0
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
                "python_version_ok", "required_modules_available", "temp_dir_writable",
                "basic_commands_work", "async_support_available"
            ]
            
            missing_components = [
                comp for comp in required_components 
                if not env_validation.get(comp, False)
            ]
            
            if missing_components:
                raise RuntimeError(f"Missing required test components: {missing_components}")
            
            # Initialize detector with test configuration
            test_config = StallDetectorConfig(
                check_interval=0.5,  # Faster for testing
                stall_timeout=10,    # Shorter for testing
                output_timeout=5,    # Shorter for testing
                max_recovery_attempts=2,  # Fewer for testing
                max_concurrent=3,
                enable_auto_recovery=True
            )
            
            self.detector = TerminalStallDetector(test_config)
            
            # Start monitoring
            if not self.detector.start_monitoring():
                raise RuntimeError("Failed to start monitoring")
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Test suite setup failed: {e}")
    
    async def teardown_test_suite(self):
        """Clean up test suite resources."""
        try:
            # Stop monitoring
            if self.detector:
                self.detector.stop_monitoring()
            
            # Clean up temp directory
            if self.temp_dir and self.temp_dir.exists() and self.test_config.cleanup_after_tests:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")
    
    async def test_environment_validation(self) -> Dict[str, Any]:
        """Test environment validation."""
        test_name = "environment_validation"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Test detector environment validation
            env_validation = self.detector.validate_environment()
            test_result["details"]["detector_validation"] = env_validation
            
            # Test our test environment validation
            test_env_validation = self.validate_test_environment()
            test_result["details"]["test_env_validation"] = test_env_validation
            
            # Check if all required components are available
            required_ok = all([
                env_validation.get("python_version_ok", False),
                env_validation.get("subprocess_available", False),
                env_validation.get("threading_available", False),
                env_validation.get("basic_commands_work", False)
            ])
            
            if required_ok:
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append("Required environment components not available")
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Environment validation failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def test_basic_command_execution(self) -> Dict[str, Any]:
        """Test basic command execution without stalls."""
        test_name = "basic_command_execution"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Test simple echo command
            result = await execute_with_stall_detection(["echo", "Hello, World!"])
            
            test_result["details"]["echo_test"] = {
                "state": result.state.value,
                "return_code": result.return_code,
                "stdout_lines": result.stdout_lines,
                "stderr_lines": result.stderr_lines,
                "duration": result.get_duration(),
                "recovery_attempts": result.recovery_attempts
            }
            
            # Validate results
            if (result.state == CommandState.COMPLETED and 
                result.return_code == 0 and 
                len(result.stdout_lines) > 0 and
                "Hello, World!" in " ".join(result.stdout_lines)):
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append("Echo command did not execute correctly")
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Basic command execution failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def test_timeout_detection(self) -> Dict[str, Any]:
        """Test timeout detection and recovery."""
        test_name = "timeout_detection"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Test command that should timeout
            result = await execute_with_stall_detection(
                ["sleep", "10"],
                timeout=3,
                auto_recover=True
            )
            
            test_result["details"]["timeout_test"] = {
                "state": result.state.value,
                "return_code": result.return_code,
                "duration": result.get_duration(),
                "recovery_attempts": result.recovery_attempts,
                "recovery_history": result.recovery_history,
                "errors": result.errors,
                "warnings": result.warnings
            }
            
            # Validate timeout was detected and handled
            if (result.state in [CommandState.TIMEOUT, CommandState.RECOVERED] and
                result.recovery_attempts > 0):
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append(f"Expected timeout/recovery, got state: {result.state}")
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Timeout detection test failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def test_stall_detection(self) -> Dict[str, Any]:
        """Test stall detection for commands with no output."""
        test_name = "stall_detection"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Create a script that runs but produces no output
            if self.temp_dir:
                script_path = self.temp_dir / "stall_test.py"
                script_content = '''
import time
import sys

# Run for a while without producing output
time.sleep(15)
print("Finally done!")
'''
                script_path.write_text(script_content)
                
                # Test stall detection
                result = await execute_with_stall_detection(
                    [sys.executable, str(script_path)],
                    timeout=12,
                    auto_recover=True
                )
                
                test_result["details"]["stall_test"] = {
                    "state": result.state.value,
                    "return_code": result.return_code,
                    "duration": result.get_duration(),
                    "time_since_output": result.time_since_output(),
                    "recovery_attempts": result.recovery_attempts,
                    "recovery_history": result.recovery_history,
                    "warnings": result.warnings
                }
                
                # Validate stall was detected
                if (result.state in [CommandState.STALLED, CommandState.TIMEOUT, CommandState.RECOVERED] or
                    len(result.warnings) > 0):
                    test_result["status"] = "passed"
                else:
                    test_result["status"] = "failed"
                    test_result["errors"].append("Stall was not detected")
            else:
                test_result["status"] = "skipped"
                test_result["errors"].append("No temp directory available for stall test")
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Stall detection test failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def test_recovery_mechanisms(self) -> Dict[str, Any]:
        """Test various recovery mechanisms."""
        test_name = "recovery_mechanisms"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Test different recovery actions
            recovery_tests = []
            
            # Test TERMINATE recovery
            try:
                result = await execute_with_stall_detection(
                    ["sleep", "20"],
                    timeout=3,
                    auto_recover=True
                )
                recovery_tests.append({
                    "recovery_type": "terminate",
                    "state": result.state.value,
                    "recovery_attempts": result.recovery_attempts,
                    "recovery_history": result.recovery_history
                })
            except Exception as e:
                recovery_tests.append({
                    "recovery_type": "terminate",
                    "error": str(e)
                })
            
            test_result["details"]["recovery_tests"] = recovery_tests
            
            # Check if any recovery was attempted
            recovery_attempted = any(
                test.get("recovery_attempts", 0) > 0 
                for test in recovery_tests
            )
            
            if recovery_attempted:
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append("No recovery mechanisms were tested successfully")
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Recovery mechanisms test failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def test_concurrent_monitoring(self) -> Dict[str, Any]:
        """Test concurrent command monitoring."""
        test_name = "concurrent_monitoring"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Execute multiple commands concurrently
            commands = [
                ["echo", f"Command {i}"]
                for i in range(3)
            ]
            
            # Execute all commands concurrently
            tasks = [execute_with_stall_detection(cmd) for cmd in commands]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            test_result["details"]["concurrent_test"] = {
                "total_commands": len(results),
                "successful_results": len([r for r in results if isinstance(r, CommandExecution) and r.state == CommandState.COMPLETED]),
                "failed_results": len([r for r in results if isinstance(r, Exception)]),
                "results": []
            }
            
            for i, result in enumerate(results):
                if isinstance(result, CommandExecution):
                    test_result["details"]["concurrent_test"]["results"].append({
                        "command_index": i,
                        "state": result.state.value,
                        "return_code": result.return_code,
                        "duration": result.get_duration(),
                        "stdout_lines": len(result.stdout_lines)
                    })
                else:
                    test_result["details"]["concurrent_test"]["results"].append({
                        "command_index": i,
                        "error": str(result)
                    })
            
            # Validate concurrent execution
            successful_count = test_result["details"]["concurrent_test"]["successful_results"]
            if successful_count >= 2:  # At least 2 out of 3 should succeed
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append(f"Only {successful_count} out of {len(commands)} commands succeeded")
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Concurrent monitoring test failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid commands."""
        test_name = "error_handling"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Test invalid command - should be handled gracefully
            try:
                result = await execute_with_stall_detection(["nonexistent_command_12345"])
                
                test_result["details"]["invalid_command_test"] = {
                    "state": result.state.value,
                    "return_code": result.return_code,
                    "stderr_lines": result.stderr_lines,
                    "errors": result.errors,
                    "duration": result.get_duration()
                }
                
                # Validate error was handled properly
                if result.state == CommandState.FAILED and result.return_code != 0:
                    test_result["status"] = "passed"
                else:
                    test_result["status"] = "failed"
                    test_result["errors"].append(f"Expected failure, got state: {result.state}")
                    
            except Exception as cmd_error:
                # If command execution throws an exception, that's also valid error handling
                test_result["details"]["invalid_command_test"] = {
                    "exception_handled": True,
                    "exception_type": type(cmd_error).__name__,
                    "exception_message": str(cmd_error)
                }
                test_result["status"] = "passed"  # Exception handling is valid
            
            # Test error formatting
            test_error = Exception("Command not found")
            formatted_error = format_stall_error(test_error)
            test_result["details"]["error_formatting"] = {
                "original_error": str(test_error),
                "formatted_error": formatted_error
            }
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Error handling test failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def test_statistics_collection(self) -> Dict[str, Any]:
        """Test statistics collection."""
        test_name = "statistics_collection"
        test_result = {
            "name": test_name,
            "status": "pending",
            "details": {},
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Get initial statistics
            initial_stats = self.detector.get_statistics()
            
            # Execute a few commands using the same detector instance
            await self.detector.execute_monitored_command(
                MonitoredCommandRequest(command=["echo", "stats test 1"])
            )
            await self.detector.execute_monitored_command(
                MonitoredCommandRequest(command=["echo", "stats test 2"])
            )
            
            # Try a command that will fail
            try:
                await self.detector.execute_monitored_command(
                    MonitoredCommandRequest(command=["nonexistent_command"])
                )
            except:
                pass  # Expected to fail
            
            # Get final statistics
            final_stats = self.detector.get_statistics()
            
            test_result["details"]["statistics_test"] = {
                "initial_stats": initial_stats,
                "final_stats": final_stats,
                "commands_executed": final_stats["total_commands"] - initial_stats["total_commands"],
                "uptime_increase": final_stats["uptime_seconds"] - initial_stats["uptime_seconds"]
            }
            
            # Validate statistics were updated
            if final_stats["total_commands"] > initial_stats["total_commands"]:
                test_result["status"] = "passed"
            else:
                test_result["status"] = "failed"
                test_result["errors"].append("Statistics were not updated correctly")
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(f"Statistics collection test failed: {e}")
        
        finally:
            test_result["duration"] = time.time() - start_time
        
        return test_result
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite following crawl_mcp.py methodology.
        
        Returns:
            Complete test results
        """
        print("🧪 Starting Terminal Stall Detector Comprehensive Test Suite")
        
        # Setup test suite
        try:
            await self.setup_test_suite()
            print("✅ Test suite setup completed")
        except Exception as e:
            return {
                "setup_failed": True,
                "error": str(e),
                "timestamp": time.time()
            }
        
        # Define test sequence (progressive complexity)
        test_sequence = [
            ("Environment Validation", self.test_environment_validation),
            ("Basic Command Execution", self.test_basic_command_execution),
            ("Error Handling", self.test_error_handling),
            ("Timeout Detection", self.test_timeout_detection),
            ("Stall Detection", self.test_stall_detection),
            ("Recovery Mechanisms", self.test_recovery_mechanisms),
            ("Concurrent Monitoring", self.test_concurrent_monitoring),
            ("Statistics Collection", self.test_statistics_collection)
        ]
        
        # Execute tests
        test_results = {
            "suite_name": "Terminal Stall Detector Comprehensive Tests",
            "start_time": time.time(),
            "tests": [],
            "summary": {
                "total_tests": len(test_sequence),
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "total_duration": 0.0
            }
        }
        
        for test_name, test_func in test_sequence:
            print(f"🔍 Running: {test_name}")
            
            try:
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
                
                test_results["summary"]["total_duration"] += test_result.get("duration", 0.0)
                
            except Exception as e:
                error_result = {
                    "name": test_name,
                    "status": "failed",
                    "details": {},
                    "errors": [f"Test execution exception: {e}"],
                    "duration": 0.0
                }
                test_results["tests"].append(error_result)
                test_results["summary"]["failed_tests"] += 1
                print(f"❌ {test_name}: EXCEPTION - {e}")
        
        # Cleanup
        await self.teardown_test_suite()
        
        # Final summary
        test_results["end_time"] = time.time()
        test_results["total_execution_time"] = test_results["end_time"] - test_results["start_time"]
        
        success_rate = (test_results["summary"]["passed_tests"] / 
                       test_results["summary"]["total_tests"]) * 100
        
        print(f"\n📊 Test Suite Complete:")
        print(f"   Total Tests: {test_results['summary']['total_tests']}")
        print(f"   Passed: {test_results['summary']['passed_tests']}")
        print(f"   Failed: {test_results['summary']['failed_tests']}")
        print(f"   Skipped: {test_results['summary']['skipped_tests']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Duration: {test_results['total_execution_time']:.2f}s")
        
        return test_results


async def run_stall_detector_tests():
    """Run terminal stall detector tests."""
    test_suite = StallDetectorTestSuite()
    results = await test_suite.run_comprehensive_tests()
    
    # Save results
    results_file = Path("terminal_stall_detector_test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    """Run the test suite."""
    asyncio.run(run_stall_detector_tests())
