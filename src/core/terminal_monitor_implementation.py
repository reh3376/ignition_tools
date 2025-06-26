"""Complete Terminal Command Monitoring and Auto-Recovery Implementation.

This module provides the full implementation of terminal command monitoring,
following the crawl_mcp.py methodology.
"""

import asyncio
import os
import subprocess
import threading
import time
from contextlib import asynccontextmanager, suppress
from typing import Any

import psutil

# Import the base classes
from .terminal_monitor import (
    CommandExecution,
    CommandMetrics,
    CommandRequest,
    CommandState,
    MonitoringConfig,
    RecoveryAction,
    TerminalMonitor,
)


class EnhancedTerminalMonitor(TerminalMonitor):
    """Enhanced terminal monitor with complete implementation."""

    def start_monitoring(self) -> bool:
        """Start the monitoring system.

        Returns:
            True if started successfully
        """
        try:
            # Environment validation first (crawl_mcp.py principle)
            env_validation = self.validate_environment()
            required_components = [
                "python_available",
                "subprocess_available",
                "psutil_available",
                "memory_sufficient",
            ]

            missing_components = [comp for comp in required_components if not env_validation.get(comp, False)]

            if missing_components:
                raise RuntimeError(f"Missing required components: {missing_components}")

            if self.monitoring_active:
                return True

            self.monitoring_active = True

            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True, name="TerminalMonitor")
            self.monitor_thread.start()

            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True, name="TerminalCleanup")
            self.cleanup_thread.start()

            return True

        except Exception as e:
            self.monitoring_active = False
            raise RuntimeError(f"Failed to start monitoring: {e}")

    def stop_monitoring(self) -> None:
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
                    with suppress(Exception):
                        execution.process.kill()

    async def execute_command(self, request: CommandRequest) -> CommandExecution:
        """Execute a command with monitoring and auto-recovery.

        Args:
            request: Command execution request

        Returns:
            Command execution result
        """
        # Input validation (crawl_mcp.py principle)
        try:
            if not isinstance(request, CommandRequest):
                request = CommandRequest.parse_obj(request)
        except Exception as e:
            raise ValueError(f"Invalid command request: {e}")

        # Check concurrent command limit
        active_commands = sum(1 for exec in self.executions.values() if exec.state == CommandState.RUNNING)

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

    async def _start_command_execution(self, execution: CommandExecution) -> None:
        """Start command execution."""
        request = execution.request

        try:
            # Prepare command
            if isinstance(request.command, str):
                if request.args:
                    cmd = [request.command, *request.args]
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
                text=True,
            )

            execution.state = CommandState.RUNNING
            execution.metrics.start_time = time.time()

            self.stats["total_commands"] += 1

        except Exception as e:
            execution.state = CommandState.FAILED
            execution.errors.append(f"Failed to start command: {e}")
            raise

    async def _wait_for_completion(self, execution: CommandExecution) -> bool:
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
                io_write=memory_info.vms,
            )

            # Check for stall
            return execution.metrics.is_stalled(
                window_seconds=self.config.stall_detection_window,
                cpu_threshold=self.config.cpu_threshold,
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    async def _handle_timeout(self, execution: CommandExecution) -> None:
        """Handle command timeout."""
        execution.state = CommandState.TIMEOUT
        execution.errors.append(
            f"Command timed out after {execution.request.timeout or self.config.default_timeout} seconds"
        )

        if self.config.enable_auto_recovery:
            await self._attempt_recovery(execution, "timeout")

    async def _handle_stall(self, execution: CommandExecution) -> None:
        """Handle command stall."""
        execution.warnings.append("Command appears stalled (low CPU activity)")
        self.stats["stalled_commands"] += 1

        if self.config.enable_auto_recovery:
            await self._attempt_recovery(execution, "stall")

    async def _attempt_recovery(self, execution: CommandExecution, reason: str) -> None:
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
            RecoveryAction.ESCALATE,
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
                        with suppress(Exception):
                            child.kill()

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

    def _monitoring_loop(self) -> Any:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                time.time()

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

    def _cleanup_loop(self) -> Any:
        """Cleanup loop for completed executions."""
        while self.monitoring_active:
            try:
                current_time = time.time()
                cleanup_threshold = current_time - self.config.cleanup_interval

                # Remove old completed executions
                to_remove = []
                for exec_id, execution in self.executions.items():
                    if (
                        execution.state
                        in [
                            CommandState.COMPLETED,
                            CommandState.FAILED,
                            CommandState.TIMEOUT,
                        ]
                        and execution.metrics.end_time
                        and execution.metrics.end_time < cleanup_threshold
                    ):
                        to_remove.append(exec_id)

                for exec_id in to_remove:
                    del self.executions[exec_id]

                time.sleep(self.config.cleanup_interval)

            except Exception as e:
                print(f"Cleanup loop error: {e}")
                time.sleep(60)  # Wait longer on error

    def _update_execution_metrics(self, execution: CommandExecution) -> Any:
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
                io_write=memory_info.vms,
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _update_statistics(self, execution: CommandExecution) -> Any:
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

    def get_statistics(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        uptime = time.time() - self.stats["uptime_start"]

        return {
            **self.stats,
            "uptime_seconds": uptime,
            "active_executions": len([e for e in self.executions.values() if e.state == CommandState.RUNNING]),
            "total_executions": len(self.executions),
            "success_rate": (self.stats["successful_commands"] / max(1, self.stats["total_commands"])) * 100,
            "recovery_rate": (
                self.stats["recovered_commands"]
                / max(1, self.stats["failed_commands"] + self.stats["timeout_commands"])
            )
            * 100,
        }

    def get_execution_status(self, execution_id: str) -> dict[str, Any] | None:
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
                "samples_count": len(execution.metrics.cpu_usage),
            },
        }

    @asynccontextmanager
    async def managed_execution(self, request: CommandRequest) -> None:
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
                    with suppress(Exception):
                        execution.process.kill()


# Global enhanced monitor instance
_global_enhanced_monitor: EnhancedTerminalMonitor | None = None


def get_enhanced_terminal_monitor(
    config: MonitoringConfig | None = None,
) -> EnhancedTerminalMonitor:
    """Get global enhanced terminal monitor instance."""
    global _global_enhanced_monitor

    if _global_enhanced_monitor is None:
        _global_enhanced_monitor = EnhancedTerminalMonitor(config)
        # Auto-start monitoring
        try:
            _global_enhanced_monitor.start_monitoring()
        except Exception as e:
            print(f"Warning: Failed to start terminal monitoring: {e}")

    return _global_enhanced_monitor


# Convenience functions
async def execute_monitored_command(
    command: str | list[str],
    timeout: int | None = None,
    cwd: str | None = None,
    max_retries: int | None = None,
    critical: bool = False,
) -> CommandExecution:
    """Execute a command with monitoring and auto-recovery.

    Args:
        command: Command to execute
        timeout: Command timeout in seconds
        cwd: Working directory
        max_retries: Maximum retry attempts
        critical: Mark as critical command

    Returns:
        Command execution result
    """
    monitor = get_enhanced_terminal_monitor()

    request = CommandRequest(
        command=command,
        timeout=timeout,
        cwd=cwd,
        max_retries=max_retries,
        critical=critical,
    )

    return await monitor.execute_command(request)


def execute_monitored_command_sync(
    command: str | list[str],
    timeout: int | None = None,
    cwd: str | None = None,
    max_retries: int | None = None,
    critical: bool = False,
) -> CommandExecution:
    """Synchronous wrapper for execute_monitored_command."""
    return asyncio.run(
        execute_monitored_command(
            command=command,
            timeout=timeout,
            cwd=cwd,
            max_retries=max_retries,
            critical=critical,
        )
    )
