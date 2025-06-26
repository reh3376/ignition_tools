"""Terminal Command Monitoring and Auto-Recovery System.

This module provides comprehensive monitoring and auto-recovery capabilities for terminal commands,
following the crawl_mcp.py methodology with:
1. Environment validation first
2. Comprehensive input validation using Pydantic models
3. Robust error handling with user-friendly messages
4. Modular testing approach with progressive complexity
5. Proper resource management with cleanup
6. Real-time monitoring and automatic recovery mechanisms
"""

import asyncio
import json
import os
import signal
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import psutil
from pydantic import BaseModel, Field, validator

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class CommandState(str, Enum):
    """Command execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"
    KILLED = "killed"
    RECOVERED = "recovered"


class RecoveryAction(str, Enum):
    """Recovery action types."""
    RETRY = "retry"
    KILL_AND_RESTART = "kill_and_restart"
    ESCALATE = "escalate"
    SKIP = "skip"
    ADAPTIVE_TIMEOUT = "adaptive_timeout"


class MonitoringConfig(BaseModel):
    """Configuration for terminal monitoring."""
    
    # Basic monitoring settings
    check_interval: float = Field(default=1.0, ge=0.1, le=10.0, description="Monitoring check interval in seconds")
    default_timeout: int = Field(default=30, ge=1, le=3600, description="Default command timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    
    # Stall detection settings
    stall_detection_window: int = Field(default=10, ge=5, le=60, description="Window for stall detection in seconds")
    cpu_threshold: float = Field(default=5.0, ge=0.0, le=100.0, description="CPU usage threshold for stall detection")
    memory_threshold: float = Field(default=90.0, ge=50.0, le=100.0, description="Memory usage threshold")
    
    # Recovery settings
    enable_auto_recovery: bool = Field(default=True, description="Enable automatic recovery mechanisms")
    escalation_timeout: int = Field(default=120, ge=30, le=600, description="Timeout before escalating to manual intervention")
    adaptive_timeout_factor: float = Field(default=1.5, ge=1.0, le=3.0, description="Factor for adaptive timeout adjustment")
    
    # Resource management
    max_concurrent_commands: int = Field(default=5, ge=1, le=20, description="Maximum concurrent commands")
    cleanup_interval: int = Field(default=300, ge=60, le=3600, description="Cleanup interval in seconds")
    
    @validator('check_interval')
    def validate_check_interval(cls, v):
        if v <= 0:
            raise ValueError("Check interval must be positive")
        return v


class CommandRequest(BaseModel):
    """Command execution request model."""
    
    command: Union[str, List[str]] = Field(..., description="Command to execute")
    args: Optional[List[str]] = Field(default=None, description="Command arguments")
    cwd: Optional[str] = Field(default=None, description="Working directory")
    env: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    timeout: Optional[int] = Field(default=None, ge=1, le=3600, description="Command timeout in seconds")
    shell: bool = Field(default=False, description="Execute in shell")
    capture_output: bool = Field(default=True, description="Capture stdout/stderr")
    
    # Recovery settings
    max_retries: Optional[int] = Field(default=None, ge=0, le=10, description="Override max retries")
    critical: bool = Field(default=False, description="Mark as critical command")
    recovery_actions: Optional[List[RecoveryAction]] = Field(default=None, description="Custom recovery actions")
    
    @validator('command')
    def validate_command(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Command cannot be empty")
        elif isinstance(v, list):
            if not v or not v[0].strip():
                raise ValueError("Command list cannot be empty")
        return v


@dataclass
class CommandMetrics:
    """Metrics for command execution."""
    
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    io_read: int = 0
    io_write: int = 0
    peak_memory: float = 0.0
    average_cpu: float = 0.0
    
    def add_sample(self, cpu: float, memory: float, io_read: int = 0, io_write: int = 0):
        """Add a monitoring sample."""
        self.cpu_usage.append(cpu)
        self.memory_usage.append(memory)
        self.io_read = max(self.io_read, io_read)
        self.io_write = max(self.io_write, io_write)
        self.peak_memory = max(self.peak_memory, memory)
        
        # Update average CPU
        if self.cpu_usage:
            self.average_cpu = sum(self.cpu_usage) / len(self.cpu_usage)
    
    def is_stalled(self, window_seconds: int = 10, cpu_threshold: float = 5.0) -> bool:
        """Check if command appears stalled."""
        if len(self.cpu_usage) < window_seconds:
            return False
        
        recent_samples = self.cpu_usage[-window_seconds:]
        avg_recent_cpu = sum(recent_samples) / len(recent_samples)
        
        return avg_recent_cpu < cpu_threshold
    
    def get_duration(self) -> float:
        """Get command duration."""
        end = self.end_time or time.time()
        return end - self.start_time


@dataclass
class CommandExecution:
    """Represents a command execution instance."""
    
    id: str
    request: CommandRequest
    state: CommandState = CommandState.PENDING
    process: Optional[subprocess.Popen] = None
    metrics: CommandMetrics = field(default_factory=CommandMetrics)
    
    # Results
    return_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    
    # Recovery tracking
    retry_count: int = 0
    recovery_attempts: List[str] = field(default_factory=list)
    last_recovery_time: Optional[float] = None
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class TerminalMonitor:
    """Comprehensive terminal command monitoring and auto-recovery system."""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """Initialize terminal monitor.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config or MonitoringConfig()
        self.executions: Dict[str, CommandExecution] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "recovered_commands": 0,
            "timeout_commands": 0,
            "stalled_commands": 0,
            "average_execution_time": 0.0,
            "uptime_start": time.time()
        }
        
        # Recovery handlers
        self.recovery_handlers: Dict[RecoveryAction, Callable] = {
            RecoveryAction.RETRY: self._handle_retry_recovery,
            RecoveryAction.KILL_AND_RESTART: self._handle_kill_restart_recovery,
            RecoveryAction.ESCALATE: self._handle_escalation_recovery,
            RecoveryAction.SKIP: self._handle_skip_recovery,
            RecoveryAction.ADAPTIVE_TIMEOUT: self._handle_adaptive_timeout_recovery
        }
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment setup following crawl_mcp.py methodology.
        
        Returns:
            Environment validation results
        """
        validation_results = {
            "python_available": False,
            "subprocess_available": False,
            "psutil_available": False,
            "threading_available": False,
            "signal_handling_available": False,
            "filesystem_writable": False,
            "memory_sufficient": False,
            "cpu_monitoring_available": False
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
                import threading
                validation_results["threading_available"] = True
            except ImportError:
                pass
            
            try:
                import signal
                validation_results["signal_handling_available"] = True
            except ImportError:
                pass
            
            # System resources check
            try:
                # Memory check (at least 1GB available)
                memory = psutil.virtual_memory()
                validation_results["memory_sufficient"] = memory.available > 1024 * 1024 * 1024
            except:
                pass
            
            # CPU monitoring check
            try:
                psutil.cpu_percent(interval=0.1)
                validation_results["cpu_monitoring_available"] = True
            except:
                pass
            
            # Filesystem write check
            try:
                test_file = Path("/tmp/terminal_monitor_test")
                test_file.write_text("test")
                test_file.unlink()
                validation_results["filesystem_writable"] = True
            except:
                pass
        
        except Exception as e:
            validation_results["validation_error"] = str(e)
        
        return validation_results
    
    def start_monitoring(self) -> bool:
        """Start the monitoring system.
        
        Returns:
            True if started successfully
        """
        try:
            # Environment validation first (crawl_mcp.py principle)
            env_validation = self.validate_environment()
            required_components = [
                "python_available", "subprocess_available", "psutil_available", 
                "threading_available", "memory_sufficient"
            ]
            
            missing_components = [
                comp for comp in required_components 
                if not env_validation.get(comp, False)
            ]
            
            if missing_components:
                raise RuntimeError(f"Missing required components: {missing_components}")
            
            if self.monitoring_active:
                return True
            
            self.monitoring_active = True
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="TerminalMonitor"
            )
            self.monitor_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True,
                name="TerminalCleanup"
            )
            self.cleanup_thread.start()
            
            return True
            
        except Exception as e:
            self.monitoring_active = False
            raise RuntimeError(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False
        
        # Wait for threads to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        # Kill any remaining processes
        for execution in self.executions.values():
            if execution.process and execution.process.poll() is None:
                try:
                    execution.process.terminate()
                    execution.process.wait(timeout=5)
                except:
                    try:
                        execution.process.kill()
                    except:
                        pass
    
    async def execute_command(self, request: CommandRequest) -> CommandExecution:
        """Execute a command with monitoring and auto-recovery.
        
        Args:
            request: Command execution request
            
        Returns:
            Command execution result
        """
        # Input validation (crawl_mcp.py principle)
        try:
            request = CommandRequest.parse_obj(request.dict()) if not isinstance(request, CommandRequest) else request
        except Exception as e:
            raise ValueError(f"Invalid command request: {e}")
        
        # Check concurrent command limit
        active_commands = sum(1 for exec in self.executions.values() 
                             if exec.state == CommandState.RUNNING)
        
        if active_commands >= self.config.max_concurrent_commands:
            raise RuntimeError(f"Maximum concurrent commands limit reached ({self.config.max_concurrent_commands})")
        
        # Create execution instance
        execution_id = f"cmd_{int(time.time() * 1000)}_{len(self.executions)}"
        execution = CommandExecution(id=execution_id, request=request)
        self.executions[execution_id] = execution
        
        try:
            # Start command execution
            await self._start_command_execution(execution)
            
            # Wait for completion with monitoring
            await self._wait_for_completion(execution)
            
            # Update statistics
            self._update_statistics(execution)
            
            return execution
            
        except Exception as e:
            execution.state = CommandState.FAILED
            execution.errors.append(f"Execution failed: {e}")
            self._update_statistics(execution)
            raise
    
    async def _start_command_execution(self, execution: CommandExecution):
        """Start command execution."""
        request = execution.request
        
        try:
            # Prepare command
            if isinstance(request.command, str):
                if request.args:
                    cmd = [request.command] + request.args
                else:
                    cmd = request.command if request.shell else [request.command]
            else:
                cmd = request.command + (request.args or [])
            
            # Prepare environment
            env = os.environ.copy()
            if request.env:
                env.update(request.env)
            
            # Start process
            execution.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE if request.capture_output else None,
                stderr=subprocess.PIPE if request.capture_output else None,
                cwd=request.cwd,
                env=env,
                shell=request.shell,
                text=True
            )
            
            execution.state = CommandState.RUNNING
            execution.metrics.start_time = time.time()
            
            self.stats["total_commands"] += 1
            
        except Exception as e:
            execution.state = CommandState.FAILED
            execution.errors.append(f"Failed to start command: {e}")
            raise
    
    async def _wait_for_completion(self, execution: CommandExecution):
        """Wait for command completion with monitoring."""
        timeout = execution.request.timeout or self.config.default_timeout
        start_time = time.time()
        
        while execution.process and execution.process.poll() is None:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                await self._handle_timeout(execution)
                break
            
            # Check for stall
            if self._is_command_stalled(execution):
                await self._handle_stall(execution)
                break
            
            await asyncio.sleep(self.config.check_interval)
        
        # Collect final results
        if execution.process:
            try:
                stdout, stderr = execution.process.communicate(timeout=5)
                execution.stdout = stdout or ""
                execution.stderr = stderr or ""
                execution.return_code = execution.process.returncode
                execution.metrics.end_time = time.time()
                
                if execution.return_code == 0:
                    execution.state = CommandState.COMPLETED
                else:
                    execution.state = CommandState.FAILED
                    
            except subprocess.TimeoutExpired:
                execution.state = CommandState.TIMEOUT
                execution.errors.append("Failed to collect command output")
    
    def _is_command_stalled(self, execution: CommandExecution) -> bool:
        """Check if command is stalled."""
        if not execution.process:
            return False
        
        try:
            # Get process info
            process = psutil.Process(execution.process.pid)
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Add metrics sample
            execution.metrics.add_sample(
                cpu=cpu_percent,
                memory=memory_percent,
                io_read=memory_info.rss,
                io_write=memory_info.vms
            )
            
            # Check for stall
            return execution.metrics.is_stalled(
                window_seconds=self.config.stall_detection_window,
                cpu_threshold=self.config.cpu_threshold
            )
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    async def _handle_timeout(self, execution: CommandExecution):
        """Handle command timeout."""
        execution.state = CommandState.TIMEOUT
        execution.errors.append(f"Command timed out after {execution.request.timeout or self.config.default_timeout} seconds")
        
        if self.config.enable_auto_recovery:
            await self._attempt_recovery(execution, "timeout")
    
    async def _handle_stall(self, execution: CommandExecution):
        """Handle command stall."""
        execution.warnings.append(f"Command appears stalled (low CPU activity)")
        self.stats["stalled_commands"] += 1
        
        if self.config.enable_auto_recovery:
            await self._attempt_recovery(execution, "stall")
    
    async def _attempt_recovery(self, execution: CommandExecution, reason: str):
        """Attempt to recover a failed/stalled command."""
        if not self.config.enable_auto_recovery:
            return
        
        max_retries = execution.request.max_retries or self.config.max_retries
        if execution.retry_count >= max_retries:
            execution.state = CommandState.FAILED
            execution.errors.append(f"Maximum recovery attempts reached ({max_retries})")
            return
        
        # Determine recovery actions
        recovery_actions = execution.request.recovery_actions or [
            RecoveryAction.RETRY,
            RecoveryAction.ADAPTIVE_TIMEOUT,
            RecoveryAction.KILL_AND_RESTART,
            RecoveryAction.ESCALATE
        ]
        
        for action in recovery_actions:
            if execution.retry_count < max_retries:
                try:
                    success = await self.recovery_handlers[action](execution, reason)
                    if success:
                        execution.state = CommandState.RECOVERED
                        self.stats["recovered_commands"] += 1
                        break
                except Exception as e:
                    execution.errors.append(f"Recovery action {action} failed: {e}")
        
        execution.retry_count += 1
        execution.last_recovery_time = time.time()
        execution.recovery_attempts.append(f"{reason}:{action}")
    
    async def _handle_retry_recovery(self, execution: CommandExecution, reason: str) -> bool:
        """Handle retry recovery action."""
        try:
            # Kill current process if running
            if execution.process and execution.process.poll() is None:
                execution.process.terminate()
                try:
                    execution.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    execution.process.kill()
            
            # Reset execution state
            execution.state = CommandState.PENDING
            execution.process = None
            execution.metrics = CommandMetrics()
            
            # Restart execution
            await self._start_command_execution(execution)
            await self._wait_for_completion(execution)
            
            return execution.state == CommandState.COMPLETED
            
        except Exception:
            return False
    
    async def _handle_kill_restart_recovery(self, execution: CommandExecution, reason: str) -> bool:
        """Handle kill and restart recovery action."""
        try:
            # Force kill process and all children
            if execution.process:
                try:
                    parent = psutil.Process(execution.process.pid)
                    children = parent.children(recursive=True)
                    
                    # Kill children first
                    for child in children:
                        try:
                            child.kill()
                        except:
                            pass
                    
                    # Kill parent
                    parent.kill()
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Wait a bit before restart
            await asyncio.sleep(2)
            
            # Restart with same approach as retry
            return await self._handle_retry_recovery(execution, reason)
            
        except Exception:
            return False
    
    async def _handle_adaptive_timeout_recovery(self, execution: CommandExecution, reason: str) -> bool:
        """Handle adaptive timeout recovery action."""
        try:
            # Increase timeout by factor
            current_timeout = execution.request.timeout or self.config.default_timeout
            new_timeout = int(current_timeout * self.config.adaptive_timeout_factor)
            
            # Update request timeout
            execution.request.timeout = new_timeout
            execution.warnings.append(f"Increased timeout to {new_timeout} seconds")
            
            # Retry with new timeout
            return await self._handle_retry_recovery(execution, reason)
            
        except Exception:
            return False
    
    async def _handle_escalation_recovery(self, execution: CommandExecution, reason: str) -> bool:
        """Handle escalation recovery action."""
        execution.errors.append(f"Command escalated for manual intervention: {reason}")
        execution.state = CommandState.FAILED
        
        # Log critical issue
        print(f"🚨 CRITICAL: Command {execution.id} requires manual intervention")
        print(f"   Reason: {reason}")
        print(f"   Command: {execution.request.command}")
        print(f"   Retries: {execution.retry_count}")
        
        return False
    
    async def _handle_skip_recovery(self, execution: CommandExecution, reason: str) -> bool:
        """Handle skip recovery action."""
        execution.warnings.append(f"Command skipped due to {reason}")
        execution.state = CommandState.COMPLETED
        execution.return_code = -1
        return True
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                for execution in list(self.executions.values()):
                    if execution.state == CommandState.RUNNING and execution.process:
                        # Update metrics
                        try:
                            if execution.process.poll() is None:
                                self._update_execution_metrics(execution)
                        except:
                            pass
                
                time.sleep(self.config.check_interval)
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(self.config.check_interval)
    
    def _cleanup_loop(self):
        """Cleanup loop for completed executions."""
        while self.monitoring_active:
            try:
                current_time = time.time()
                cleanup_threshold = current_time - self.config.cleanup_interval
                
                # Remove old completed executions
                to_remove = []
                for exec_id, execution in self.executions.items():
                    if (execution.state in [CommandState.COMPLETED, CommandState.FAILED, CommandState.TIMEOUT] 
                        and execution.metrics.end_time 
                        and execution.metrics.end_time < cleanup_threshold):
                        to_remove.append(exec_id)
                
                for exec_id in to_remove:
                    del self.executions[exec_id]
                
                time.sleep(self.config.cleanup_interval)
                
            except Exception as e:
                print(f"Cleanup loop error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _update_execution_metrics(self, execution: CommandExecution):
        """Update execution metrics."""
        if not execution.process:
            return
        
        try:
            process = psutil.Process(execution.process.pid)
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            execution.metrics.add_sample(
                cpu=cpu_percent,
                memory=memory_percent,
                io_read=memory_info.rss,
                io_write=memory_info.vms
            )
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    def _update_statistics(self, execution: CommandExecution):
        """Update system statistics."""
        if execution.state == CommandState.COMPLETED:
            self.stats["successful_commands"] += 1
        elif execution.state == CommandState.FAILED:
            self.stats["failed_commands"] += 1
        elif execution.state == CommandState.TIMEOUT:
            self.stats["timeout_commands"] += 1
        
        # Update average execution time
        if execution.metrics.end_time:
            duration = execution.metrics.get_duration()
            total_time = self.stats["average_execution_time"] * (self.stats["total_commands"] - 1)
            self.stats["average_execution_time"] = (total_time + duration) / self.stats["total_commands"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        uptime = time.time() - self.stats["uptime_start"]
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "active_executions": len([e for e in self.executions.values() if e.state == CommandState.RUNNING]),
            "total_executions": len(self.executions),
            "success_rate": (self.stats["successful_commands"] / max(1, self.stats["total_commands"])) * 100,
            "recovery_rate": (self.stats["recovered_commands"] / max(1, self.stats["failed_commands"] + self.stats["timeout_commands"])) * 100
        }
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific execution."""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return {
            "id": execution.id,
            "state": execution.state.value,
            "command": execution.request.command,
            "duration": execution.metrics.get_duration(),
            "return_code": execution.return_code,
            "retry_count": execution.retry_count,
            "errors": execution.errors,
            "warnings": execution.warnings,
            "metrics": {
                "peak_memory": execution.metrics.peak_memory,
                "average_cpu": execution.metrics.average_cpu,
                "samples_count": len(execution.metrics.cpu_usage)
            }
        }
    
    @asynccontextmanager
    async def managed_execution(self, request: CommandRequest):
        """Context manager for managed command execution."""
        execution = None
        try:
            execution = await self.execute_command(request)
            yield execution
        finally:
            if execution and execution.process and execution.process.poll() is None:
                try:
                    execution.process.terminate()
                    execution.process.wait(timeout=5)
                except:
                    try:
                        execution.process.kill()
                    except:
                        pass


# Global monitor instance
_global_monitor: Optional[TerminalMonitor] = None


def get_terminal_monitor(config: Optional[MonitoringConfig] = None) -> TerminalMonitor:
    """Get global terminal monitor instance."""
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = TerminalMonitor(config)
    
    return _global_monitor


def format_terminal_error(error: Exception) -> str:
    """Format terminal errors for user-friendly messages (crawl_mcp.py principle)."""
    error_str = str(error).lower()
    
    if "timeout" in error_str or "timeoutexpired" in error_str:
        return "Command timed out. Consider increasing timeout or checking for hanging processes."
    elif "permission" in error_str or "access denied" in error_str:
        return "Permission denied. Check file permissions or run with appropriate privileges."
    elif "no such file" in error_str or "command not found" in error_str:
        return "Command or file not found. Verify the command exists and is in PATH."
    elif "connection" in error_str:
        return "Connection error. Check network connectivity and target availability."
    elif "memory" in error_str or "out of memory" in error_str:
        return "Insufficient memory. Close other applications or increase available memory."
    elif "disk" in error_str or "space" in error_str:
        return "Disk space error. Free up disk space and try again."
    else:
        return f"Terminal error: {error!s}"


if __name__ == "__main__":
    """Test the terminal monitoring system."""
    import asyncio
    
    async def test_monitoring():
        """Test monitoring functionality."""
        print("🧪 Testing Terminal Monitoring System")
        
        # Test environment validation
        monitor = TerminalMonitor()
        env_validation = monitor.validate_environment()
        print(f"Environment validation: {env_validation}")
        
        # Start monitoring
        monitor.start_monitoring()
        print("✅ Monitoring started")
        
        # Test simple command
        try:
            result = await execute_monitored_command(["echo", "Hello, World!"])
            print(f"✅ Simple command result: {result.state}, output: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ Simple command failed: {e}")
        
        # Test timeout command
        try:
            result = await execute_monitored_command(["sleep", "5"], timeout=2)
            print(f"⏰ Timeout command result: {result.state}")
        except Exception as e:
            print(f"❌ Timeout command failed: {e}")
        
        # Get statistics
        stats = monitor.get_statistics()
        print(f"📊 Statistics: {stats}")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("🛑 Monitoring stopped")
    
    asyncio.run(test_monitoring()) 