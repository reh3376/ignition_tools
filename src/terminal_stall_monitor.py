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

import psutil
from pydantic import BaseModel, Field, validator

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class StallState(str, Enum):
    """Command stall states."""
    RUNNING = "running"
    STALLED = "stalled"
    RECOVERED = "recovered"
    TIMEOUT = "timeout"
    FAILED = "failed"
    COMPLETED = "completed"


class RecoveryStrategy(str, Enum):
    """Recovery strategies for stalled commands."""
    INTERRUPT = "interrupt"
    TERMINATE = "terminate"
    KILL = "kill"
    RESTART = "restart"
    TIMEOUT_EXTEND = "timeout_extend"
    ESCALATE = "escalate"


class StallMonitorConfig(BaseModel):
    """Configuration for stall monitoring."""
    
    # Detection settings
    check_interval: float = Field(default=2.0, ge=0.5, le=10.0, description="Check interval in seconds")
    stall_threshold: int = Field(default=15, ge=5, le=300, description="Seconds before considering stalled")
    cpu_threshold: float = Field(default=1.0, ge=0.0, le=50.0, description="CPU % threshold for stall detection")
    
    # Recovery settings
    max_recovery_attempts: int = Field(default=3, ge=1, le=10, description="Maximum recovery attempts")
    recovery_delay: float = Field(default=2.0, ge=0.5, le=10.0, description="Delay between recovery attempts")
    timeout_extension_factor: float = Field(default=2.0, ge=1.0, le=5.0, description="Factor to extend timeout")
    
    # Monitoring settings
    max_monitored_commands: int = Field(default=10, ge=1, le=50, description="Maximum commands to monitor")
    cleanup_interval: int = Field(default=60, ge=30, le=300, description="Cleanup interval in seconds")
    
    @validator('check_interval')
    def validate_check_interval(cls, v):
        if v <= 0:
            raise ValueError("Check interval must be positive")
        return v


class CommandMonitorRequest(BaseModel):
    """Request to monitor a command."""
    
    command: Union[str, List[str]] = Field(..., description="Command to monitor")
    timeout: Optional[int] = Field(default=None, ge=1, le=3600, description="Command timeout in seconds")
    cwd: Optional[str] = Field(default=None, description="Working directory")
    env: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    
    # Recovery settings
    recovery_strategies: List[RecoveryStrategy] = Field(
        default=[RecoveryStrategy.INTERRUPT, RecoveryStrategy.TERMINATE, RecoveryStrategy.KILL],
        description="Recovery strategies to try"
    )
    critical: bool = Field(default=False, description="Mark as critical command")
    auto_recover: bool = Field(default=True, description="Enable auto-recovery")
    
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
    """Metrics for a monitored command."""
    
    start_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    cpu_samples: List[float] = field(default_factory=list)
    memory_samples: List[float] = field(default_factory=list)
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    
    def add_sample(self, cpu_percent: float, memory_mb: float, io_read: int = 0, io_write: int = 0):
        """Add a monitoring sample."""
        self.cpu_samples.append(cpu_percent)
        self.memory_samples.append(memory_mb)
        self.io_read_bytes = max(self.io_read_bytes, io_read)
        self.io_write_bytes = max(self.io_write_bytes, io_write)
        
        # Update last activity if CPU is above threshold
        if cpu_percent > 0.5:  # Minimal activity threshold
            self.last_activity = time.time()
    
    def is_stalled(self, stall_threshold: int, cpu_threshold: float) -> bool:
        """Check if command appears stalled."""
        if not self.cpu_samples:
            return False
        
        # Check time since last activity
        time_since_activity = time.time() - self.last_activity
        if time_since_activity < stall_threshold:
            return False
        
        # Check recent CPU activity
        recent_samples = self.cpu_samples[-5:] if len(self.cpu_samples) >= 5 else self.cpu_samples
        avg_cpu = sum(recent_samples) / len(recent_samples) if recent_samples else 0
        
        return avg_cpu < cpu_threshold
    
    def get_duration(self) -> float:
        """Get total duration."""
        return time.time() - self.start_time


@dataclass
class MonitoredCommand:
    """Represents a monitored command."""
    
    id: str
    request: CommandMonitorRequest
    process: subprocess.Popen
    state: StallState = StallState.RUNNING
    metrics: CommandMetrics = field(default_factory=CommandMetrics)
    
    # Recovery tracking
    recovery_attempts: int = 0
    last_recovery_time: Optional[float] = None
    recovery_history: List[str] = field(default_factory=list)
    
    # Results
    return_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class TerminalStallMonitor:
    """Terminal stall detection and auto-recovery system."""
    
    def __init__(self, config: Optional[StallMonitorConfig] = None):
        """Initialize stall monitor.
        
        Args:
            config: Monitor configuration
        """
        self.config = config or StallMonitorConfig()
        self.monitored_commands: Dict[str, MonitoredCommand] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.stats = {
            "total_monitored": 0,
            "stalled_detected": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "timeouts": 0,
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
            "psutil_available": False,
            "threading_available": False,
            "signal_handling_available": False,
            "system_resources_ok": False,
            "permissions_ok": False
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
                import psutil
                validation_results["psutil_available"] = True
                
                # System resources check
                memory = psutil.virtual_memory()
                cpu_count = psutil.cpu_count()
                validation_results["system_resources_ok"] = (
                    memory.available > 256 * 1024 * 1024 and  # 256MB
                    cpu_count >= 1
                )
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
            
            # Permissions check
            try:
                # Test process creation
                test_proc = subprocess.Popen(["echo", "test"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                test_proc.wait(timeout=5)
                validation_results["permissions_ok"] = True
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
                "python_version_ok", "subprocess_available", "psutil_available",
                "threading_available", "system_resources_ok", "permissions_ok"
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
                name="StallMonitor"
            )
            self.monitor_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True,
                name="StallCleanup"
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
    
    def monitor_command(self, request: CommandMonitorRequest) -> str:
        """Start monitoring a command.
        
        Args:
            request: Command monitoring request
            
        Returns:
            Command ID for tracking
        """
        # Input validation (crawl_mcp.py principle)
        try:
            if not isinstance(request, CommandMonitorRequest):
                request = CommandMonitorRequest.parse_obj(request)
        except Exception as e:
            raise ValueError(f"Invalid monitoring request: {e}")
        
        # Check monitoring limit
        if len(self.monitored_commands) >= self.config.max_monitored_commands:
            raise RuntimeError(f"Maximum monitored commands limit reached ({self.config.max_monitored_commands})")
        
        # Start the command
        try:
            # Prepare command
            if isinstance(request.command, str):
                cmd = request.command
                shell = True
            else:
                cmd = request.command
                shell = False
            
            # Prepare environment
            env = os.environ.copy()
            if request.env:
                env.update(request.env)
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=request.cwd,
                env=env,
                shell=shell,
                text=True
            )
            
            # Create monitored command
            command_id = f"cmd_{int(time.time() * 1000)}_{process.pid}"
            monitored_cmd = MonitoredCommand(
                id=command_id,
                request=request,
                process=process
            )
            
            self.monitored_commands[command_id] = monitored_cmd
            self.stats["total_monitored"] += 1
            
            return command_id
            
        except Exception as e:
            raise RuntimeError(f"Failed to start monitoring command: {e}")
    
    def get_command_status(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a monitored command.
        
        Args:
            command_id: Command ID
            
        Returns:
            Command status or None if not found
        """
        cmd = self.monitored_commands.get(command_id)
        if not cmd:
            return None
        
        return {
            "id": cmd.id,
            "state": cmd.state.value,
            "duration": cmd.metrics.get_duration(),
            "return_code": cmd.return_code,
            "recovery_attempts": cmd.recovery_attempts,
            "errors": cmd.errors,
            "warnings": cmd.warnings,
            "metrics": {
                "avg_cpu": sum(cmd.metrics.cpu_samples) / len(cmd.metrics.cpu_samples) if cmd.metrics.cpu_samples else 0,
                "peak_memory": max(cmd.metrics.memory_samples) if cmd.metrics.memory_samples else 0,
                "samples_count": len(cmd.metrics.cpu_samples)
            }
        }
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                for cmd_id, cmd in list(self.monitored_commands.items()):
                    self._check_command_status(cmd)
                
                time.sleep(self.config.check_interval)
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(self.config.check_interval)
    
    def _check_command_status(self, cmd: MonitoredCommand):
        """Check status of a single command."""
        try:
            # Check if process is still running
            if cmd.process.poll() is not None:
                # Process has finished
                cmd.return_code = cmd.process.returncode
                
                # Collect output
                try:
                    stdout, stderr = cmd.process.communicate(timeout=1)
                    cmd.stdout = stdout or ""
                    cmd.stderr = stderr or ""
                except:
                    pass
                
                if cmd.return_code == 0:
                    cmd.state = StallState.COMPLETED
                else:
                    cmd.state = StallState.FAILED
                
                return
            
            # Process is still running - collect metrics
            try:
                process = psutil.Process(cmd.process.pid)
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                
                cmd.metrics.add_sample(
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    io_read=memory_info.rss,
                    io_write=memory_info.vms
                )
                
                # Check for stall
                if cmd.metrics.is_stalled(self.config.stall_threshold, self.config.cpu_threshold):
                    if cmd.state != StallState.STALLED:
                        cmd.state = StallState.STALLED
                        self.stats["stalled_detected"] += 1
                        cmd.warnings.append(f"Command stalled after {cmd.metrics.get_duration():.1f}s")
                        
                        # Attempt recovery if enabled
                        if cmd.request.auto_recover:
                            self._attempt_recovery(cmd)
                
                # Check for timeout
                if cmd.request.timeout and cmd.metrics.get_duration() > cmd.request.timeout:
                    cmd.state = StallState.TIMEOUT
                    self.stats["timeouts"] += 1
                    cmd.errors.append(f"Command timed out after {cmd.request.timeout}s")
                    
                    # Attempt recovery
                    if cmd.request.auto_recover:
                        self._attempt_recovery(cmd)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process no longer exists
                cmd.state = StallState.FAILED
                cmd.errors.append("Process disappeared unexpectedly")
        
        except Exception as e:
            cmd.errors.append(f"Status check error: {e}")
    
    def _attempt_recovery(self, cmd: MonitoredCommand):
        """Attempt to recover a stalled/timed-out command."""
        if cmd.recovery_attempts >= self.config.max_recovery_attempts:
            cmd.errors.append(f"Maximum recovery attempts reached ({self.config.max_recovery_attempts})")
            return
        
        cmd.recovery_attempts += 1
        cmd.last_recovery_time = time.time()
        
        # Try recovery strategies in order
        for strategy in cmd.request.recovery_strategies:
            try:
                success = self._execute_recovery_strategy(cmd, strategy)
                cmd.recovery_history.append(f"{strategy.value}:{'success' if success else 'failed'}")
                
                if success:
                    cmd.state = StallState.RECOVERED
                    self.stats["successful_recoveries"] += 1
                    cmd.warnings.append(f"Recovered using strategy: {strategy.value}")
                    return
                
            except Exception as e:
                cmd.recovery_history.append(f"{strategy.value}:error:{e}")
        
        # All recovery strategies failed
        self.stats["failed_recoveries"] += 1
        cmd.errors.append("All recovery strategies failed")
    
    def _execute_recovery_strategy(self, cmd: MonitoredCommand, strategy: RecoveryStrategy) -> bool:
        """Execute a specific recovery strategy.
        
        Args:
            cmd: Command to recover
            strategy: Recovery strategy to use
            
        Returns:
            True if recovery was successful
        """
        try:
            if strategy == RecoveryStrategy.INTERRUPT:
                # Send SIGINT (Ctrl+C)
                cmd.process.send_signal(signal.SIGINT)
                time.sleep(1)
                return cmd.process.poll() is not None
            
            elif strategy == RecoveryStrategy.TERMINATE:
                # Send SIGTERM
                cmd.process.terminate()
                try:
                    cmd.process.wait(timeout=5)
                    return True
                except subprocess.TimeoutExpired:
                    return False
            
            elif strategy == RecoveryStrategy.KILL:
                # Send SIGKILL
                cmd.process.kill()
                try:
                    cmd.process.wait(timeout=5)
                    return True
                except subprocess.TimeoutExpired:
                    return False
            
            elif strategy == RecoveryStrategy.RESTART:
                # Kill and restart the command
                cmd.process.kill()
                time.sleep(self.config.recovery_delay)
                
                # Start new process
                if isinstance(cmd.request.command, str):
                    new_cmd = cmd.request.command
                    shell = True
                else:
                    new_cmd = cmd.request.command
                    shell = False
                
                env = os.environ.copy()
                if cmd.request.env:
                    env.update(cmd.request.env)
                
                cmd.process = subprocess.Popen(
                    new_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cmd.request.cwd,
                    env=env,
                    shell=shell,
                    text=True
                )
                
                # Reset metrics
                cmd.metrics = CommandMetrics()
                return True
            
            elif strategy == RecoveryStrategy.TIMEOUT_EXTEND:
                # Extend timeout
                if cmd.request.timeout:
                    cmd.request.timeout = int(cmd.request.timeout * self.config.timeout_extension_factor)
                    cmd.warnings.append(f"Extended timeout to {cmd.request.timeout}s")
                    return True
                return False
            
            elif strategy == RecoveryStrategy.ESCALATE:
                # Mark for manual intervention
                cmd.errors.append("Command escalated for manual intervention")
                print(f"🚨 ESCALATION: Command {cmd.id} requires manual intervention")
                print(f"   Command: {cmd.request.command}")
                print(f"   Duration: {cmd.metrics.get_duration():.1f}s")
                print(f"   Recovery attempts: {cmd.recovery_attempts}")
                return False
        
        except Exception as e:
            cmd.errors.append(f"Recovery strategy {strategy.value} failed: {e}")
            return False
        
        return False
    
    def _cleanup_loop(self):
        """Cleanup completed commands."""
        while self.monitoring_active:
            try:
                current_time = time.time()
                cleanup_threshold = current_time - self.config.cleanup_interval
                
                # Remove completed commands older than threshold
                to_remove = []
                for cmd_id, cmd in self.monitored_commands.items():
                    if (cmd.state in [StallState.COMPLETED, StallState.FAILED] and
                        cmd.metrics.start_time < cleanup_threshold):
                        to_remove.append(cmd_id)
                
                for cmd_id in to_remove:
                    del self.monitored_commands[cmd_id]
                
                time.sleep(self.config.cleanup_interval)
                
            except Exception as e:
                print(f"Cleanup loop error: {e}")
                time.sleep(60)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        uptime = time.time() - self.stats["start_time"]
        active_commands = len([cmd for cmd in self.monitored_commands.values() 
                              if cmd.state == StallState.RUNNING])
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "active_commands": active_commands,
            "total_commands": len(self.monitored_commands),
            "recovery_success_rate": (
                self.stats["successful_recoveries"] / 
                max(1, self.stats["successful_recoveries"] + self.stats["failed_recoveries"])
            ) * 100
        }


# Global monitor instance
_global_stall_monitor: Optional[TerminalStallMonitor] = None


def get_stall_monitor(config: Optional[StallMonitorConfig] = None) -> TerminalStallMonitor:
    """Get global stall monitor instance."""
    global _global_stall_monitor
    
    if _global_stall_monitor is None:
        _global_stall_monitor = TerminalStallMonitor(config)
        try:
            _global_stall_monitor.start_monitoring()
        except Exception as e:
            print(f"Warning: Failed to start stall monitoring: {e}")
    
    return _global_stall_monitor


def format_stall_error(error: Exception) -> str:
    """Format stall monitoring errors for user-friendly messages."""
    error_str = str(error).lower()
    
    if "timeout" in error_str:
        return "Command monitoring timed out. The process may be hanging or taking longer than expected."
    elif "permission" in error_str or "access denied" in error_str:
        return "Permission denied while monitoring process. Check process permissions."
    elif "no such process" in error_str:
        return "Process disappeared during monitoring. It may have been killed externally."
    elif "resource" in error_str or "memory" in error_str:
        return "Insufficient system resources for monitoring. Close other applications."
    else:
        return f"Monitoring error: {error!s}"


if __name__ == "__main__":
    """Test the stall monitoring system."""
    import asyncio
    
    async def test_stall_monitoring():
        """Test stall monitoring functionality."""
        print("🧪 Testing Terminal Stall Monitoring System")
        
        # Create monitor
        monitor = TerminalStallMonitor()
        
        # Test environment validation
        env_validation = monitor.validate_environment()
        print(f"Environment validation: {env_validation}")
        
        # Start monitoring
        monitor.start_monitoring()
        print("✅ Monitoring started")
        
        # Test normal command
        try:
            cmd_id = monitor.monitor_command(
                CommandMonitorRequest(command=["echo", "Hello, World!"])
            )
            print(f"✅ Started monitoring command: {cmd_id}")
            
            # Wait for completion
            for _ in range(10):
                status = monitor.get_command_status(cmd_id)
                if status and status["state"] in ["completed", "failed"]:
                    print(f"✅ Command completed: {status}")
                    break
                await asyncio.sleep(1)
        
        except Exception as e:
            print(f"❌ Command monitoring failed: {e}")
        
        # Test stall detection with a long-running command
        try:
            stall_config = StallMonitorConfig(stall_threshold=5, cpu_threshold=1.0)
            stall_monitor = TerminalStallMonitor(stall_config)
            stall_monitor.start_monitoring()
            
            cmd_id = stall_monitor.monitor_command(
                CommandMonitorRequest(
                    command=["sleep", "10"],
                    timeout=8,
                    recovery_strategies=[RecoveryStrategy.TERMINATE]
                )
            )
            print(f"✅ Started stall test command: {cmd_id}")
            
            # Monitor for stall detection
            for i in range(15):
                status = stall_monitor.get_command_status(cmd_id)
                if status:
                    print(f"Status {i}: {status['state']} (duration: {status['duration']:.1f}s)")
                    if status["state"] in ["timeout", "recovered", "failed"]:
                        break
                await asyncio.sleep(1)
            
            stall_monitor.stop_monitoring()
        
        except Exception as e:
            print(f"❌ Stall test failed: {e}")
        
        # Get statistics
        stats = monitor.get_statistics()
        print(f"📊 Final statistics: {stats}")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("🛑 Monitoring stopped")
    
    asyncio.run(test_stall_monitoring()) 