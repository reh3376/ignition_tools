"""Terminal Stall Detection and Auto-Recovery System.

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
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class CommandState(str, Enum):
    """Command execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STALLED = "stalled"
    TIMEOUT = "timeout"
    FAILED = "failed"
    RECOVERED = "recovered"


class RecoveryAction(str, Enum):
    """Recovery actions for stalled commands."""
    INTERRUPT = "interrupt"
    TERMINATE = "terminate"
    KILL = "kill"
    RESTART = "restart"
    EXTEND_TIMEOUT = "extend_timeout"
    ESCALATE = "escalate"


class StallDetectorConfig(BaseModel):
    """Configuration for stall detection."""
    
    # Detection settings
    check_interval: float = Field(default=2.0, ge=0.5, le=10.0, description="Check interval in seconds")
    stall_timeout: int = Field(default=30, ge=5, le=300, description="Seconds before considering stalled")
    output_timeout: int = Field(default=15, ge=5, le=120, description="Seconds without output before stall")
    
    # Recovery settings
    max_recovery_attempts: int = Field(default=3, ge=1, le=10, description="Maximum recovery attempts")
    recovery_delay: float = Field(default=1.0, ge=0.1, le=5.0, description="Delay between recovery attempts")
    timeout_multiplier: float = Field(default=1.5, ge=1.0, le=3.0, description="Timeout extension multiplier")
    
    # System settings
    max_concurrent: int = Field(default=5, ge=1, le=20, description="Maximum concurrent monitored commands")
    enable_auto_recovery: bool = Field(default=True, description="Enable automatic recovery")
    
    @validator('check_interval')
    def validate_check_interval(cls, v):
        if v <= 0:
            raise ValueError("Check interval must be positive")
        return v


class MonitoredCommandRequest(BaseModel):
    """Request to monitor a command for stalls."""
    
    command: Union[str, List[str]] = Field(..., description="Command to execute and monitor")
    timeout: Optional[int] = Field(default=None, ge=1, le=3600, description="Command timeout in seconds")
    cwd: Optional[str] = Field(default=None, description="Working directory")
    env: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    shell: bool = Field(default=False, description="Execute in shell")
    
    # Recovery settings
    recovery_actions: List[RecoveryAction] = Field(
        default=[RecoveryAction.INTERRUPT, RecoveryAction.TERMINATE, RecoveryAction.KILL],
        description="Recovery actions to try in order"
    )
    critical: bool = Field(default=False, description="Mark as critical command")
    auto_recover: bool = Field(default=True, description="Enable auto-recovery for this command")
    
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
class CommandExecution:
    """Represents a command execution being monitored."""
    
    id: str
    request: MonitoredCommandRequest
    process: Optional[subprocess.Popen] = None
    state: CommandState = CommandState.PENDING
    
    # Timing
    start_time: float = field(default_factory=time.time)
    last_output_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Output
    stdout_lines: List[str] = field(default_factory=list)
    stderr_lines: List[str] = field(default_factory=list)
    return_code: Optional[int] = None
    
    # Recovery tracking
    recovery_attempts: int = 0
    recovery_history: List[str] = field(default_factory=list)
    last_recovery_time: Optional[float] = None
    
    # Status tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def get_duration(self) -> float:
        """Get execution duration."""
        end = self.end_time or time.time()
        return end - self.start_time
    
    def time_since_output(self) -> float:
        """Get time since last output."""
        return time.time() - self.last_output_time
    
    def add_stdout(self, line: str):
        """Add stdout line and update timing."""
        self.stdout_lines.append(line)
        self.last_output_time = time.time()
    
    def add_stderr(self, line: str):
        """Add stderr line and update timing."""
        self.stderr_lines.append(line)
        self.last_output_time = time.time()


class TerminalStallDetector:
    """Terminal stall detection and auto-recovery system."""
    
    def __init__(self, config: Optional[StallDetectorConfig] = None):
        """Initialize stall detector.
        
        Args:
            config: Detector configuration
        """
        self.config = config or StallDetectorConfig()
        self.executions: Dict[str, CommandExecution] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.stats = {
            "total_commands": 0,
            "completed_commands": 0,
            "failed_commands": 0,
            "stalled_commands": 0,
            "recovered_commands": 0,
            "timeout_commands": 0,
            "start_time": time.time()
        }
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment setup following crawl_mcp.py methodology.
        
        Returns:
            Environment validation results
        """
        validation_results = {
            "python_version_ok": False,
            "subprocess_available": False,
            "threading_available": False,
            "signal_handling_available": False,
            "system_resources_ok": False,
            "basic_commands_work": False
        }
        
        try:
            # Python version check
            validation_results["python_version_ok"] = sys.version_info >= (3, 8)
            
            # Module availability checks
            try:
                import subprocess
                validation_results["subprocess_available"] = True
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
                import psutil
                memory = psutil.virtual_memory()
                validation_results["system_resources_ok"] = memory.available > 128 * 1024 * 1024  # 128MB
            except ImportError:
                # Fallback without psutil
                validation_results["system_resources_ok"] = True
            
            # Test basic command execution
            try:
                result = subprocess.run(["echo", "test"], capture_output=True, text=True, timeout=5)
                validation_results["basic_commands_work"] = result.returncode == 0
            except Exception:
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
                "python_version_ok", "subprocess_available", "threading_available",
                "signal_handling_available", "basic_commands_work"
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
                name="StallDetector"
            )
            self.monitor_thread.start()
            
            return True
            
        except Exception as e:
            self.monitoring_active = False
            raise RuntimeError(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False
        
        # Wait for thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Terminate any running processes
        for execution in self.executions.values():
            if execution.process and execution.process.poll() is None:
                try:
                    execution.process.terminate()
                    execution.process.wait(timeout=3)
                except:
                    try:
                        execution.process.kill()
                    except:
                        pass
    
    async def execute_monitored_command(self, request: MonitoredCommandRequest) -> CommandExecution:
        """Execute a command with stall monitoring.
        
        Args:
            request: Command monitoring request
            
        Returns:
            Command execution result
        """
        # Input validation (crawl_mcp.py principle)
        try:
            if not isinstance(request, MonitoredCommandRequest):
                request = MonitoredCommandRequest.parse_obj(request)
        except Exception as e:
            raise ValueError(f"Invalid command request: {e}")
        
        # Check concurrent limit
        active_count = sum(1 for e in self.executions.values() 
                          if e.state in [CommandState.RUNNING, CommandState.PENDING])
        
        if active_count >= self.config.max_concurrent:
            raise RuntimeError(f"Maximum concurrent commands limit reached ({self.config.max_concurrent})")
        
        # Create execution
        execution_id = f"cmd_{int(time.time() * 1000)}_{len(self.executions)}"
        execution = CommandExecution(id=execution_id, request=request)
        self.executions[execution_id] = execution
        
        try:
            # Start the command
            await self._start_command(execution)
            
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
    
    async def _start_command(self, execution: CommandExecution):
        """Start a command execution."""
        request = execution.request
        
        try:
            # Prepare command
            if isinstance(request.command, str):
                cmd = request.command
                shell = request.shell or True
            else:
                cmd = request.command
                shell = request.shell
            
            # Prepare environment
            env = os.environ.copy()
            if request.env:
                env.update(request.env)
            
            # Start process
            try:
                execution.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=request.cwd,
                    env=env,
                    shell=shell,
                    text=True,
                    bufsize=1,  # Line buffered
                    universal_newlines=True
                )
            except FileNotFoundError as e:
                # Handle command not found gracefully
                execution.state = CommandState.FAILED
                execution.errors.append(f"Command not found: {e}")
                execution.return_code = 127  # Standard "command not found" exit code
                execution.end_time = time.time()
                return  # Exit early, don't try to monitor a non-existent process
            
            execution.state = CommandState.RUNNING
            execution.start_time = time.time()
            execution.last_output_time = time.time()
            
            self.stats["total_commands"] += 1
            
        except Exception as e:
            execution.state = CommandState.FAILED
            execution.errors.append(f"Failed to start command: {e}")
            raise
    
    async def _wait_for_completion(self, execution: CommandExecution):
        """Wait for command completion with monitoring."""
        timeout = execution.request.timeout
        
        while execution.process and execution.process.poll() is None:
            # Check timeout
            if timeout and execution.get_duration() > timeout:
                execution.state = CommandState.TIMEOUT
                execution.errors.append(f"Command timed out after {timeout}s")
                
                if execution.request.auto_recover and self.config.enable_auto_recovery:
                    await self._attempt_recovery(execution, "timeout")
                break
            
            # Check for stall (no output)
            if execution.time_since_output() > self.config.output_timeout:
                if execution.state != CommandState.STALLED:
                    execution.state = CommandState.STALLED
                    execution.warnings.append(f"Command stalled - no output for {self.config.output_timeout}s")
                    self.stats["stalled_commands"] += 1
                    
                    if execution.request.auto_recover and self.config.enable_auto_recovery:
                        await self._attempt_recovery(execution, "stall")
            
            # Check for overall stall (total time)
            if execution.get_duration() > self.config.stall_timeout:
                if execution.state == CommandState.RUNNING:
                    execution.state = CommandState.STALLED
                    execution.warnings.append(f"Command stalled - running for {self.config.stall_timeout}s")
                    self.stats["stalled_commands"] += 1
                    
                    if execution.request.auto_recover and self.config.enable_auto_recovery:
                        await self._attempt_recovery(execution, "long_running")
            
            await asyncio.sleep(self.config.check_interval)
        
        # Collect final results
        if execution.process:
            try:
                stdout, stderr = execution.process.communicate(timeout=5)
                if stdout:
                    execution.stdout_lines.extend(stdout.splitlines())
                if stderr:
                    execution.stderr_lines.extend(stderr.splitlines())
                
                execution.return_code = execution.process.returncode
                execution.end_time = time.time()
                
                if execution.state not in [CommandState.STALLED, CommandState.TIMEOUT, CommandState.RECOVERED]:
                    if execution.return_code == 0:
                        execution.state = CommandState.COMPLETED
                    else:
                        execution.state = CommandState.FAILED
                        
            except subprocess.TimeoutExpired:
                execution.errors.append("Failed to collect command output")
    
    async def _attempt_recovery(self, execution: CommandExecution, reason: str):
        """Attempt to recover a stalled command."""
        if execution.recovery_attempts >= self.config.max_recovery_attempts:
            execution.errors.append(f"Maximum recovery attempts reached ({self.config.max_recovery_attempts})")
            return
        
        execution.recovery_attempts += 1
        execution.last_recovery_time = time.time()
        
        for action in execution.request.recovery_actions:
            try:
                success = await self._execute_recovery_action(execution, action, reason)
                execution.recovery_history.append(f"{action.value}:{reason}:{'success' if success else 'failed'}")
                
                if success:
                    execution.state = CommandState.RECOVERED
                    self.stats["recovered_commands"] += 1
                    execution.warnings.append(f"Recovered using {action.value} for {reason}")
                    return
                
                # Wait between recovery attempts
                await asyncio.sleep(self.config.recovery_delay)
                
            except Exception as e:
                execution.recovery_history.append(f"{action.value}:{reason}:error:{e}")
        
        # All recovery attempts failed
        execution.errors.append(f"All recovery attempts failed for {reason}")
    
    async def _execute_recovery_action(self, execution: CommandExecution, action: RecoveryAction, reason: str) -> bool:
        """Execute a specific recovery action.
        
        Args:
            execution: Command execution to recover
            action: Recovery action to perform
            reason: Reason for recovery
            
        Returns:
            True if recovery was successful
        """
        if not execution.process:
            return False
        
        try:
            if action == RecoveryAction.INTERRUPT:
                # Send SIGINT (Ctrl+C equivalent)
                if hasattr(signal, 'SIGINT'):
                    execution.process.send_signal(signal.SIGINT)
                    await asyncio.sleep(2)
                    return execution.process.poll() is not None
                return False
            
            elif action == RecoveryAction.TERMINATE:
                # Send SIGTERM
                execution.process.terminate()
                try:
                    execution.process.wait(timeout=5)
                    return True
                except subprocess.TimeoutExpired:
                    return False
            
            elif action == RecoveryAction.KILL:
                # Send SIGKILL
                execution.process.kill()
                try:
                    execution.process.wait(timeout=3)
                    return True
                except subprocess.TimeoutExpired:
                    return False
            
            elif action == RecoveryAction.RESTART:
                # Kill current process and restart
                execution.process.kill()
                await asyncio.sleep(1)
                
                # Restart the command
                await self._start_command(execution)
                return execution.process is not None
            
            elif action == RecoveryAction.EXTEND_TIMEOUT:
                # Extend timeout
                if execution.request.timeout:
                    old_timeout = execution.request.timeout
                    execution.request.timeout = int(old_timeout * self.config.timeout_multiplier)
                    execution.warnings.append(f"Extended timeout from {old_timeout}s to {execution.request.timeout}s")
                    return True
                return False
            
            elif action == RecoveryAction.ESCALATE:
                # Escalate for manual intervention
                execution.errors.append(f"Command escalated for manual intervention: {reason}")
                print(f"🚨 ESCALATION REQUIRED: Command {execution.id}")
                print(f"   Command: {execution.request.command}")
                print(f"   Reason: {reason}")
                print(f"   Duration: {execution.get_duration():.1f}s")
                print(f"   Recovery attempts: {execution.recovery_attempts}")
                return False
        
        except Exception as e:
            execution.errors.append(f"Recovery action {action.value} failed: {e}")
            return False
        
        return False
    
    def _monitoring_loop(self):
        """Main monitoring loop (runs in separate thread)."""
        while self.monitoring_active:
            try:
                # Check all active executions
                for execution in list(self.executions.values()):
                    if execution.state in [CommandState.RUNNING, CommandState.STALLED]:
                        self._check_execution_output(execution)
                
                time.sleep(self.config.check_interval)
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(self.config.check_interval)
    
    def _check_execution_output(self, execution: CommandExecution):
        """Check for new output from a running command."""
        if not execution.process:
            return
        
        try:
            # Non-blocking read from stdout
            if execution.process.stdout and execution.process.stdout.readable():
                line = execution.process.stdout.readline()
                if line:
                    execution.add_stdout(line.rstrip())
            
            # Non-blocking read from stderr
            if execution.process.stderr and execution.process.stderr.readable():
                line = execution.process.stderr.readline()
                if line:
                    execution.add_stderr(line.rstrip())
        
        except Exception:
            # Ignore read errors (process might be finishing)
            pass
    
    def _update_statistics(self, execution: CommandExecution):
        """Update system statistics."""
        if execution.state == CommandState.COMPLETED:
            self.stats["completed_commands"] += 1
        elif execution.state == CommandState.FAILED:
            self.stats["failed_commands"] += 1
        elif execution.state == CommandState.TIMEOUT:
            self.stats["timeout_commands"] += 1
        elif execution.state == CommandState.RECOVERED:
            self.stats["recovered_commands"] += 1
        elif execution.state == CommandState.STALLED:
            self.stats["stalled_commands"] += 1
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific execution."""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return {
            "id": execution.id,
            "state": execution.state.value,
            "command": execution.request.command,
            "duration": execution.get_duration(),
            "time_since_output": execution.time_since_output(),
            "return_code": execution.return_code,
            "recovery_attempts": execution.recovery_attempts,
            "recovery_history": execution.recovery_history,
            "stdout_lines": len(execution.stdout_lines),
            "stderr_lines": len(execution.stderr_lines),
            "errors": execution.errors,
            "warnings": execution.warnings
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        uptime = time.time() - self.stats["start_time"]
        active_executions = len([e for e in self.executions.values() 
                                if e.state in [CommandState.RUNNING, CommandState.STALLED]])
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "active_executions": active_executions,
            "total_executions": len(self.executions),
            "success_rate": (self.stats["completed_commands"] / max(1, self.stats["total_commands"])) * 100,
            "recovery_rate": (self.stats["recovered_commands"] / max(1, self.stats["stalled_commands"])) * 100
        }


# Global detector instance
_global_detector: Optional[TerminalStallDetector] = None


def get_stall_detector(config: Optional[StallDetectorConfig] = None) -> TerminalStallDetector:
    """Get global stall detector instance."""
    global _global_detector
    
    if _global_detector is None:
        _global_detector = TerminalStallDetector(config)
        try:
            _global_detector.start_monitoring()
        except Exception as e:
            print(f"Warning: Failed to start stall detection: {e}")
    
    return _global_detector


async def execute_with_stall_detection(
    command: Union[str, List[str]],
    timeout: Optional[int] = None,
    cwd: Optional[str] = None,
    auto_recover: bool = True,
    critical: bool = False
) -> CommandExecution:
    """Execute a command with stall detection and auto-recovery.
    
    Args:
        command: Command to execute
        timeout: Command timeout in seconds
        cwd: Working directory
        auto_recover: Enable auto-recovery
        critical: Mark as critical command
        
    Returns:
        Command execution result
    """
    detector = get_stall_detector()
    
    request = MonitoredCommandRequest(
        command=command,
        timeout=timeout,
        cwd=cwd,
        auto_recover=auto_recover,
        critical=critical
    )
    
    return await detector.execute_monitored_command(request)


def format_stall_error(error: Exception) -> str:
    """Format stall detection errors for user-friendly messages."""
    error_str = str(error).lower()
    
    if "timeout" in error_str:
        return "Command timed out. It may be hanging or taking longer than expected."
    elif "stalled" in error_str:
        return "Command appears to be stalled. No output received for extended period."
    elif "permission" in error_str or "access denied" in error_str:
        return "Permission denied. Check file permissions or run with appropriate privileges."
    elif "no such file" in error_str or "command not found" in error_str:
        return "Command not found. Verify the command exists and is in PATH."
    elif "resource" in error_str or "memory" in error_str:
        return "Insufficient system resources. Close other applications and try again."
    else:
        return f"Stall detection error: {error!s}"


if __name__ == "__main__":
    """Test the stall detection system."""
    
    async def test_stall_detection():
        """Test stall detection functionality."""
        print("🧪 Testing Terminal Stall Detection System")
        
        # Create detector
        detector = TerminalStallDetector()
        
        # Test environment validation
        env_validation = detector.validate_environment()
        print(f"Environment validation: {env_validation}")
        
        # Start monitoring
        detector.start_monitoring()
        print("✅ Monitoring started")
        
        # Test normal command
        try:
            result = await execute_with_stall_detection(["echo", "Hello, World!"])
            print(f"✅ Normal command: {result.state} - {' '.join(result.stdout_lines)}")
        except Exception as e:
            print(f"❌ Normal command failed: {e}")
        
        # Test timeout command
        try:
            result = await execute_with_stall_detection(["sleep", "5"], timeout=2)
            print(f"⏰ Timeout command: {result.state} - Recovery attempts: {result.recovery_attempts}")
        except Exception as e:
            print(f"❌ Timeout command failed: {e}")
        
        # Get statistics
        stats = detector.get_statistics()
        print(f"📊 Statistics: {stats}")
        
        # Stop monitoring
        detector.stop_monitoring()
        print("🛑 Monitoring stopped")
    
    asyncio.run(test_stall_detection())
