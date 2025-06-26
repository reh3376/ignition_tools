"""Terminal Command Wrapper with Automatic Stall Detection.

This module provides a comprehensive wrapper for terminal command execution that
automatically integrates stall detection and recovery mechanisms following the
crawl_mcp.py methodology.
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, validator

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.terminal_stall_detector import (
    CommandState,
    MonitoredCommandRequest,
    StallDetectorConfig,
    TerminalStallDetector,
    get_stall_detector,
)


class TerminalWrapperConfig(BaseModel):
    """Configuration for terminal command wrapper."""

    enable_stall_detection: bool = Field(default=True, description="Enable automatic stall detection")
    default_timeout: int | None = Field(default=300, ge=10, le=3600, description="Default command timeout")
    auto_recover: bool = Field(default=True, description="Enable automatic recovery")
    max_recovery_attempts: int = Field(default=3, ge=1, le=10, description="Maximum recovery attempts")
    log_commands: bool = Field(default=True, description="Log command executions")


class TerminalCommandRequest(BaseModel):
    """Request for terminal command execution."""

    command: str | list[str] = Field(..., description="Command to execute")
    timeout: int | None = Field(default=None, description="Command timeout in seconds")
    cwd: str | None = Field(default=None, description="Working directory")
    env: dict[str, str] | None = Field(default=None, description="Environment variables")
    shell: bool | None = Field(default=None, description="Execute in shell")
    auto_recover: bool | None = Field(default=None, description="Override auto-recovery setting")
    critical: bool = Field(default=False, description="Mark as critical command")

    @validator("command")
    def validate_command(cls, v) -> Any:
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Command cannot be empty")
        elif isinstance(v, list) and (not v or not v[0].strip()):
            raise ValueError("Command list cannot be empty")
        return v


class TerminalExecutionResult(BaseModel):
    """Result of terminal command execution."""

    command: str | list[str]
    state: CommandState
    return_code: int | None
    duration: float
    stdout: str = ""
    stderr: str = ""
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    stall_detected: bool = False
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_attempts: int = 0
    errors: list[str] = []
    warnings: list[str] = []
    start_time: float
    end_time: float | None = None

    @property
    def success(self) -> bool:
        """Check if command executed successfully."""
        return self.state == CommandState.COMPLETED and self.return_code == 0

    @property
    def failed(self) -> bool:
        """Check if command failed."""
        return self.state in [CommandState.FAILED, CommandState.TIMEOUT] and not self.recovery_successful


class TerminalCommandWrapper:
    """Terminal command wrapper with automatic stall detection and recovery."""

    def __init__(self, config: TerminalWrapperConfig | None = None):
        """Initialize terminal command wrapper."""
        self.config = config or TerminalWrapperConfig()
        self.detector: TerminalStallDetector | None = None
        self.execution_history: list[TerminalExecutionResult] = []

        # Statistics
        self.stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "stalled_commands": 0,
            "recovered_commands": 0,
            "start_time": time.time(),
        }

    def validate_environment(self) -> dict[str, Any]:
        """Validate environment setup following crawl_mcp.py methodology."""
        validation_results = {
            "python_version_ok": False,
            "subprocess_available": False,
            "stall_detector_available": False,
            "basic_commands_work": False,
            "permissions_ok": False,
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

            # Stall detector availability
            try:
                detector = get_stall_detector()
                validation_results["stall_detector_available"] = detector is not None
            except Exception:
                pass

            # Test basic command execution
            try:
                result = subprocess.run(["echo", "test"], capture_output=True, text=True, timeout=5)
                validation_results["basic_commands_work"] = result.returncode == 0
            except Exception:
                pass

            # Permissions check
            try:
                proc = subprocess.Popen(["sleep", "0.1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.wait(timeout=1)
                validation_results["permissions_ok"] = True
            except Exception:
                pass

        except Exception as e:
            validation_results["validation_error"] = str(e)

        return validation_results

    def initialize(self) -> bool:
        """Initialize the wrapper with environment validation."""
        try:
            # Environment validation first (crawl_mcp.py principle)
            env_validation = self.validate_environment()

            required_components = [
                "python_version_ok",
                "subprocess_available",
                "basic_commands_work",
                "permissions_ok",
            ]

            missing_components = [comp for comp in required_components if not env_validation.get(comp, False)]

            if missing_components:
                raise RuntimeError(f"Missing required components: {missing_components}")

            # Initialize stall detector if enabled
            if self.config.enable_stall_detection:
                stall_config = StallDetectorConfig(
                    max_recovery_attempts=self.config.max_recovery_attempts,
                    enable_auto_recovery=self.config.auto_recover,
                )
                self.detector = get_stall_detector(stall_config)

                if not env_validation.get("stall_detector_available", False):
                    print("Warning: Stall detector not available, falling back to basic execution")
                    self.config.enable_stall_detection = False

            return True

        except Exception as e:
            raise RuntimeError(f"Wrapper initialization failed: {e}")

    async def execute_command(self, request: TerminalCommandRequest) -> TerminalExecutionResult:
        """Execute a terminal command with automatic stall detection."""
        # Input validation (crawl_mcp.py principle)
        try:
            if not isinstance(request, TerminalCommandRequest):
                request = TerminalCommandRequest.parse_obj(request)
        except Exception as e:
            raise ValueError(f"Invalid command request: {e}")

        # Initialize if not already done
        if self.detector is None and self.config.enable_stall_detection:
            self.initialize()

        start_time = time.time()

        try:
            # Use stall detection if available
            if self.config.enable_stall_detection and self.detector:
                result = await self._execute_with_stall_detection(request, start_time)
            else:
                result = await self._execute_basic(request, start_time)

            # Update statistics
            self._update_statistics(result)

            # Save to history
            self.execution_history.append(result)

            # Log command if enabled
            if self.config.log_commands:
                self._log_command_execution(result)

            return result

        except Exception as e:
            # Create error result
            error_result = TerminalExecutionResult(
                command=request.command,
                state=CommandState.FAILED,
                return_code=-1,
                duration=time.time() - start_time,
                start_time=start_time,
                end_time=time.time(),
                errors=[f"Command execution failed: {e}"],
            )

            self._update_statistics(error_result)
            return error_result

    async def _execute_with_stall_detection(
        self, request: TerminalCommandRequest, start_time: float
    ) -> TerminalExecutionResult:
        """Execute command with stall detection."""
        # Convert to monitored command request
        monitored_request = MonitoredCommandRequest(
            command=request.command,
            timeout=request.timeout or self.config.default_timeout,
            cwd=request.cwd,
            env=request.env,
            shell=request.shell or False,
            critical=request.critical,
            auto_recover=(request.auto_recover if request.auto_recover is not None else self.config.auto_recover),
        )

        # Execute with stall detection
        execution = await self.detector.execute_monitored_command(monitored_request)

        # Convert to wrapper result
        return TerminalExecutionResult(
            command=request.command,
            state=execution.state,
            return_code=execution.return_code,
            duration=execution.get_duration(),
            stdout="\n".join(execution.stdout_lines),
            stderr="\n".join(execution.stderr_lines),
            stdout_lines=execution.stdout_lines,
            stderr_lines=execution.stderr_lines,
            stall_detected=execution.state in [CommandState.STALLED, CommandState.TIMEOUT],
            recovery_attempted=execution.recovery_attempts > 0,
            recovery_successful=execution.state == CommandState.RECOVERED,
            recovery_attempts=execution.recovery_attempts,
            errors=execution.errors,
            warnings=execution.warnings,
            start_time=start_time,
            end_time=start_time + execution.get_duration(),
        )

    async def _execute_basic(self, request: TerminalCommandRequest, start_time: float) -> TerminalExecutionResult:
        """Execute command without stall detection (fallback)."""
        try:
            # Prepare command
            if isinstance(request.command, str):
                cmd = request.command
                shell = request.shell if request.shell is not None else True
            else:
                cmd = request.command
                shell = request.shell if request.shell is not None else False

            # Prepare environment
            env = os.environ.copy()
            if request.env:
                env.update(request.env)

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                cwd=request.cwd,
                env=env,
                shell=shell,
                text=True,
                timeout=request.timeout or self.config.default_timeout,
            )

            end_time = time.time()

            # Process output
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            stdout_lines = stdout.splitlines() if stdout else []
            stderr_lines = stderr.splitlines() if stderr else []

            return TerminalExecutionResult(
                command=request.command,
                state=(CommandState.COMPLETED if result.returncode == 0 else CommandState.FAILED),
                return_code=result.returncode,
                duration=end_time - start_time,
                stdout=stdout,
                stderr=stderr,
                stdout_lines=stdout_lines,
                stderr_lines=stderr_lines,
                start_time=start_time,
                end_time=end_time,
            )

        except subprocess.TimeoutExpired:
            return TerminalExecutionResult(
                command=request.command,
                state=CommandState.TIMEOUT,
                return_code=-1,
                duration=time.time() - start_time,
                start_time=start_time,
                end_time=time.time(),
                errors=["Command timed out"],
            )

        except FileNotFoundError as e:
            return TerminalExecutionResult(
                command=request.command,
                state=CommandState.FAILED,
                return_code=127,
                duration=time.time() - start_time,
                start_time=start_time,
                end_time=time.time(),
                errors=[f"Command not found: {e}"],
            )

        except Exception as e:
            return TerminalExecutionResult(
                command=request.command,
                state=CommandState.FAILED,
                return_code=-1,
                duration=time.time() - start_time,
                start_time=start_time,
                end_time=time.time(),
                errors=[f"Execution failed: {e}"],
            )

    def _update_statistics(self, result: TerminalExecutionResult) -> Any:
        """Update execution statistics."""
        self.stats["total_commands"] += 1

        if result.success:
            self.stats["successful_commands"] += 1
        elif result.failed:
            self.stats["failed_commands"] += 1

        if result.stall_detected:
            self.stats["stalled_commands"] += 1

        if result.recovery_successful:
            self.stats["recovered_commands"] += 1

    def _log_command_execution(self, result: TerminalExecutionResult) -> Any:
        """Log command execution."""
        status_emoji = "✅" if result.success else "❌" if result.failed else "⚠️"
        command_str = " ".join(result.command) if isinstance(result.command, list) else result.command

        print(f"{status_emoji} Command: {command_str}")
        print(f"   Duration: {result.duration:.2f}s")
        print(f"   State: {result.state.value}")
        print(f"   Return Code: {result.return_code}")

        if result.stall_detected:
            print(f"   🚨 Stall detected - Recovery {'successful' if result.recovery_successful else 'failed'}")

    def get_statistics(self) -> dict[str, Any]:
        """Get execution statistics."""
        uptime = time.time() - self.stats["start_time"]

        return {
            **self.stats,
            "uptime_seconds": uptime,
            "success_rate": (self.stats["successful_commands"] / max(1, self.stats["total_commands"])) * 100,
            "recovery_rate": (self.stats["recovered_commands"] / max(1, self.stats["stalled_commands"])) * 100,
            "execution_history_size": len(self.execution_history),
        }


# Global wrapper instance
_global_wrapper: TerminalCommandWrapper | None = None


def get_terminal_wrapper(
    config: TerminalWrapperConfig | None = None,
) -> TerminalCommandWrapper:
    """Get global terminal wrapper instance."""
    global _global_wrapper

    if _global_wrapper is None:
        _global_wrapper = TerminalCommandWrapper(config)
        try:
            _global_wrapper.initialize()
        except Exception as e:
            print(f"Warning: Failed to initialize terminal wrapper: {e}")

    return _global_wrapper


async def execute_terminal_command(
    command: str | list[str],
    timeout: int | None = None,
    cwd: str | None = None,
    auto_recover: bool = True,
    critical: bool = False,
) -> TerminalExecutionResult:
    """Execute a terminal command with automatic stall detection and recovery."""
    wrapper = get_terminal_wrapper()

    request = TerminalCommandRequest(
        command=command,
        timeout=timeout,
        cwd=cwd,
        auto_recover=auto_recover,
        critical=critical,
    )

    return await wrapper.execute_command(request)


def execute_terminal_command_sync(
    command: str | list[str],
    timeout: int | None = None,
    cwd: str | None = None,
    auto_recover: bool = True,
    critical: bool = False,
) -> TerminalExecutionResult:
    """Synchronous version of execute_terminal_command."""
    return asyncio.run(
        execute_terminal_command(
            command=command,
            timeout=timeout,
            cwd=cwd,
            auto_recover=auto_recover,
            critical=critical,
        )
    )


if __name__ == "__main__":
    """Test the terminal command wrapper."""

    async def test_wrapper() -> None:
        """Test wrapper functionality."""
        print("🧪 Testing Terminal Command Wrapper")

        # Create wrapper
        wrapper = TerminalCommandWrapper()
        wrapper.initialize()

        # Test basic command
        result = await wrapper.execute_command(TerminalCommandRequest(command=["echo", "Hello, World!"]))
        print(f"✅ Basic command: {result.state} - {result.stdout.strip()}")

        # Test timeout with recovery
        result = await wrapper.execute_command(
            TerminalCommandRequest(command=["sleep", "10"], timeout=3, auto_recover=True)
        )
        print(f"⏰ Timeout test: {result.state} - Recovery: {result.recovery_successful}")

        # Get statistics
        stats = wrapper.get_statistics()
        print(f"📊 Statistics: {stats}")

    asyncio.run(test_wrapper())
