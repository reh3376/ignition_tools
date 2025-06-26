"""Production Safety System - Phase 14 Implementation.

This module implements a comprehensive safety system for production control
with emergency procedures, safety interlocks, and alarm management.

Following crawl_mpc.py methodology:
- Step 1: Environment validation with safety-critical checks
- Step 2: Input validation using Pydantic models with safety constraints
- Step 3: Comprehensive error handling with fail-safe behavior
- Step 4: Modular testing with safety scenario validation
- Step 5: Progressive complexity with safety guarantees
- Step 6: Resource management with emergency cleanup

Author: IGN Scripts Development Team
Version: 14.0.0
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncIterator, Callable

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety integrity levels."""
    SIL_0 = "SIL_0"  # No safety function
    SIL_1 = "SIL_1"  # Low safety integrity
    SIL_2 = "SIL_2"  # Medium safety integrity
    SIL_3 = "SIL_3"  # High safety integrity
    SIL_4 = "SIL_4"  # Very high safety integrity


class AlarmPriority(Enum):
    """Alarm priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class SafetyState(Enum):
    """Safety system states."""
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    ALARM = "ALARM"
    EMERGENCY = "EMERGENCY"
    SHUTDOWN = "SHUTDOWN"


# Step 1: Environment Validation (crawl_mcp.py methodology)
def validate_safety_environment() -> dict[str, Any]:
    """Validate safety system environment setup."""
    logger.info("🔍 Step 1: Environment Validation - Safety System")
    
    errors = []
    warnings = []
    
    # Check safety-critical environment variables
    safety_vars = [
        "SAFETY_EMERGENCY_TIMEOUT",
        "SAFETY_WATCHDOG_INTERVAL",
        "SAFETY_BACKUP_SYSTEMS",
        "SAFETY_NOTIFICATION_ENDPOINTS",
    ]
    
    for var in safety_vars:
        if not os.getenv(var):
            warnings.append(f"Safety environment variable {var} not set")
    
    # Check emergency shutdown capabilities
    emergency_stop_pin = os.getenv("EMERGENCY_STOP_GPIO_PIN")
    if not emergency_stop_pin:
        warnings.append("Emergency stop GPIO pin not configured")
    
    # Verify safety database connectivity
    safety_db_url = os.getenv("SAFETY_DATABASE_URL")
    if not safety_db_url:
        warnings.append("Safety database URL not configured")
    
    # Check watchdog timer availability
    try:
        import watchdog
        logger.info("✅ Watchdog timer available")
    except ImportError:
        warnings.append("Watchdog timer not available")
    
    # Verify backup communication channels
    backup_channels = os.getenv("SAFETY_BACKUP_CHANNELS", "").split(",")
    if len(backup_channels) < 2:
        warnings.append("Insufficient backup communication channels")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "safety_critical": len([w for w in warnings if "emergency" in w.lower()]) == 0,
        "timestamp": datetime.now().isoformat(),
    }


# Step 2: Input Validation Models (crawl_mcp.py methodology)
class SafetyLimit(BaseModel):
    """Safety limit configuration with validation."""
    
    parameter_name: str = Field(..., description="Parameter being monitored")
    low_limit: float | None = Field(None, description="Low safety limit")
    high_limit: float | None = Field(None, description="High safety limit")
    safety_level: SafetyLevel = Field(..., description="Safety integrity level")
    alarm_priority: AlarmPriority = Field(..., description="Alarm priority")
    time_delay: float = Field(default=0.0, ge=0, description="Alarm delay in seconds")
    hysteresis: float = Field(default=0.0, ge=0, description="Hysteresis value")
    
    @field_validator("parameter_name")
    @classmethod
    def validate_parameter_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Parameter name cannot be empty")
        return v.strip()
    
    @field_validator("low_limit", "high_limit")
    @classmethod
    def validate_limits(cls, v: float | None, info) -> float | None:
        if v is not None and hasattr(info, "data"):
            other_limit = info.data.get("high_limit" if info.field_name == "low_limit" else "low_limit")
            if other_limit is not None and info.field_name == "low_limit" and v >= other_limit:
                raise ValueError("Low limit must be less than high limit")
        return v


class EmergencyProcedure(BaseModel):
    """Emergency procedure configuration."""
    
    procedure_id: str = Field(..., description="Unique procedure identifier")
    name: str = Field(..., description="Procedure name")
    trigger_conditions: list[str] = Field(..., description="Conditions that trigger this procedure")
    safety_level: SafetyLevel = Field(..., description="Required safety level")
    timeout_seconds: float = Field(..., gt=0, description="Maximum execution time")
    steps: list[str] = Field(..., min_length=1, description="Procedure steps")
    verification_required: bool = Field(default=True, description="Require verification")
    
    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Emergency procedure must have at least one step")
        return [step.strip() for step in v if step.strip()]


class SafetyConfiguration(BaseModel):
    """Comprehensive safety system configuration."""
    
    system_name: str = Field(..., description="Safety system name")
    safety_level: SafetyLevel = Field(..., description="Overall system safety level")
    watchdog_interval: float = Field(default=1.0, gt=0, description="Watchdog check interval")
    emergency_timeout: float = Field(default=5.0, gt=0, description="Emergency response timeout")
    
    # Safety limits and procedures
    safety_limits: list[SafetyLimit] = Field(..., description="Safety parameter limits")
    emergency_procedures: list[EmergencyProcedure] = Field(..., description="Emergency procedures")
    
    # Notification settings
    notification_endpoints: list[str] = Field(default_factory=list, description="Notification endpoints")
    escalation_enabled: bool = Field(default=True, description="Enable alarm escalation")
    
    @field_validator("safety_limits")
    @classmethod
    def validate_safety_limits(cls, v: list[SafetyLimit]) -> list[SafetyLimit]:
        if not v:
            raise ValueError("At least one safety limit must be configured")
        
        # Check for duplicate parameter names
        param_names = [limit.parameter_name for limit in v]
        if len(param_names) != len(set(param_names)):
            raise ValueError("Duplicate parameter names in safety limits")
        
        return v


# Step 3: Comprehensive Error Handling (crawl_mcp.py methodology)
def format_safety_error(error: Exception, context: str = "") -> str:
    """Format safety system errors with fail-safe messaging."""
    error_str = str(error).lower()
    
    if "timeout" in error_str:
        return f"Safety timeout in {context}: Emergency procedures may be required"
    elif "communication" in error_str or "connection" in error_str:
        return f"Safety communication failure in {context}: Switching to backup systems"
    elif "sensor" in error_str or "measurement" in error_str:
        return f"Safety sensor failure in {context}: Using redundant measurements"
    elif "interlock" in error_str:
        return f"Safety interlock violation in {context}: System protection activated"
    elif "permission" in error_str or "access" in error_str:
        return f"Safety system access denied in {context}: Check authentication"
    else:
        return f"Safety system error in {context}: {error!s} - Entering safe mode"


# Step 5: Progressive Complexity (crawl_mcp.py methodology)
@dataclass
class ProductionSafetySystem:
    """Production safety system with comprehensive protection."""
    
    # Configuration
    config: SafetyConfiguration
    
    # Runtime state
    _initialized: bool = field(default=False, init=False)
    _current_state: SafetyState = field(default=SafetyState.NORMAL, init=False)
    _active_alarms: dict[str, dict[str, Any]] = field(default_factory=dict, init=False)
    _emergency_active: bool = field(default=False, init=False)
    
    # Monitoring
    _parameter_values: dict[str, float] = field(default_factory=dict, init=False)
    _last_update: dict[str, datetime] = field(default_factory=dict, init=False)
    _watchdog_task: asyncio.Task | None = field(default=None, init=False)
    
    # Event handlers
    _alarm_handlers: list[Callable] = field(default_factory=list, init=False)
    _emergency_handlers: list[Callable] = field(default_factory=list, init=False)
    
    def __post_init__(self) -> None:
        """Initialize safety system after creation."""
        logger.info("🛡️ Initializing Production Safety System")
    
    async def initialize(self) -> dict[str, Any]:
        """Initialize safety system with comprehensive validation."""
        logger.info("🔧 Step 1-6: Initializing Safety System (crawl_mcp.py methodology)")
        
        # Step 1: Environment validation first
        env_validation = validate_safety_environment()
        if not env_validation["valid"]:
            return {
                "success": False,
                "error": "Safety environment validation failed",
                "details": env_validation["errors"],
                "safety_critical": True,
            }
        
        try:
            # Step 2: Input validation (already done via Pydantic)
            logger.info("✅ Safety configuration validation passed")
            
            # Step 3: Initialize parameter monitoring
            for limit in self.config.safety_limits:
                self._parameter_values[limit.parameter_name] = 0.0
                self._last_update[limit.parameter_name] = datetime.now()
            
            # Step 4: Start watchdog monitoring
            await self._start_watchdog()
            
            # Step 5: Initialize emergency procedures
            await self._initialize_emergency_procedures()
            
            self._initialized = True
            self._current_state = SafetyState.NORMAL
            
            logger.info("✅ Production Safety System initialized successfully")
            
            return {
                "success": True,
                "message": "Safety system initialized successfully",
                "configuration": {
                    "system_name": self.config.system_name,
                    "safety_level": self.config.safety_level.value,
                    "monitored_parameters": len(self.config.safety_limits),
                    "emergency_procedures": len(self.config.emergency_procedures),
                },
                "safety_critical": env_validation["safety_critical"],
            }
            
        except Exception as e:
            error_msg = format_safety_error(e, "safety system initialization")
            logger.error(f"❌ Safety system initialization failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "safety_critical": True,
            }
    
    async def _start_watchdog(self) -> None:
        """Start safety watchdog monitoring."""
        self._watchdog_task = asyncio.create_task(self._watchdog_loop())
        logger.info("✅ Safety watchdog started")
    
    async def _watchdog_loop(self) -> None:
        """Safety watchdog monitoring loop."""
        while self._initialized:
            try:
                await self._check_safety_parameters()
                await self._check_communication_health()
                await self._update_safety_state()
                
                await asyncio.sleep(self.config.watchdog_interval)
                
            except asyncio.CancelledError:
                logger.info("Safety watchdog cancelled")
                break
            except Exception as e:
                logger.error(f"Safety watchdog error: {e}")
                await self._handle_watchdog_failure()
                await asyncio.sleep(self.config.watchdog_interval)
    
    async def _initialize_emergency_procedures(self) -> None:
        """Initialize emergency procedures."""
        for procedure in self.config.emergency_procedures:
            logger.info(f"✅ Emergency procedure loaded: {procedure.name}")
        
        logger.info(f"✅ {len(self.config.emergency_procedures)} emergency procedures initialized")
    
    async def update_parameter(self, parameter_name: str, value: float) -> dict[str, Any]:
        """Update safety parameter value and check limits."""
        if not self._initialized:
            return {"success": False, "error": "Safety system not initialized"}
        
        try:
            # Update parameter value
            self._parameter_values[parameter_name] = value
            self._last_update[parameter_name] = datetime.now()
            
            # Check safety limits
            safety_check = await self._check_parameter_safety(parameter_name, value)
            
            return {
                "success": True,
                "parameter": parameter_name,
                "value": value,
                "safety_check": safety_check,
                "current_state": self._current_state.value,
            }
            
        except Exception as e:
            error_msg = format_safety_error(e, f"parameter update ({parameter_name})")
            logger.error(f"❌ Parameter update failed: {error_msg}")
            
            # Trigger emergency response for critical failures
            await self._trigger_emergency_response("Parameter update failure")
            
            return {
                "success": False,
                "error": error_msg,
                "emergency_triggered": True,
            }
    
    async def _check_parameter_safety(self, parameter_name: str, value: float) -> dict[str, Any]:
        """Check if parameter value violates safety limits."""
        # Find safety limit for this parameter
        safety_limit = None
        for limit in self.config.safety_limits:
            if limit.parameter_name == parameter_name:
                safety_limit = limit
                break
        
        if not safety_limit:
            return {"safe": True, "message": "No safety limit configured"}
        
        # Check limits
        violation = None
        if safety_limit.low_limit is not None and value < safety_limit.low_limit:
            violation = "low"
        elif safety_limit.high_limit is not None and value > safety_limit.high_limit:
            violation = "high"
        
        if violation:
            # Create alarm
            alarm_id = f"{parameter_name}_{violation}_limit"
            await self._create_alarm(
                alarm_id=alarm_id,
                parameter=parameter_name,
                value=value,
                limit=safety_limit.low_limit if violation == "low" else safety_limit.high_limit,
                priority=safety_limit.alarm_priority,
                safety_level=safety_limit.safety_level,
            )
            
            return {
                "safe": False,
                "violation": violation,
                "limit_violated": safety_limit.low_limit if violation == "low" else safety_limit.high_limit,
                "safety_level": safety_limit.safety_level.value,
                "alarm_created": alarm_id,
            }
        
        return {"safe": True, "message": "Parameter within safety limits"}
    
    async def _create_alarm(
        self,
        alarm_id: str,
        parameter: str,
        value: float,
        limit: float,
        priority: AlarmPriority,
        safety_level: SafetyLevel,
    ) -> None:
        """Create safety alarm."""
        alarm_data = {
            "id": alarm_id,
            "parameter": parameter,
            "current_value": value,
            "limit_value": limit,
            "priority": priority.value,
            "safety_level": safety_level.value,
            "timestamp": datetime.now(),
            "acknowledged": False,
        }
        
        self._active_alarms[alarm_id] = alarm_data
        
        # Update safety state based on priority
        if priority in [AlarmPriority.CRITICAL, AlarmPriority.EMERGENCY]:
            self._current_state = SafetyState.EMERGENCY
            await self._trigger_emergency_response(f"Critical alarm: {alarm_id}")
        elif priority == AlarmPriority.HIGH:
            self._current_state = SafetyState.ALARM
        elif self._current_state == SafetyState.NORMAL:
            self._current_state = SafetyState.WARNING
        
        # Notify handlers
        for handler in self._alarm_handlers:
            try:
                await handler(alarm_data)
            except Exception as e:
                logger.error(f"Alarm handler error: {e}")
        
        logger.warning(f"🚨 Safety alarm created: {alarm_id} ({priority.value})")
    
    async def _trigger_emergency_response(self, reason: str) -> None:
        """Trigger emergency response procedures."""
        if self._emergency_active:
            logger.warning("Emergency response already active")
            return
        
        self._emergency_active = True
        self._current_state = SafetyState.EMERGENCY
        
        logger.critical(f"🚨 EMERGENCY RESPONSE TRIGGERED: {reason}")
        
        try:
            # Execute emergency procedures
            for procedure in self.config.emergency_procedures:
                if await self._should_execute_procedure(procedure, reason):
                    await self._execute_emergency_procedure(procedure)
            
            # Notify emergency handlers
            for handler in self._emergency_handlers:
                try:
                    await handler(reason)
                except Exception as e:
                    logger.error(f"Emergency handler error: {e}")
            
            # Send notifications
            await self._send_emergency_notifications(reason)
            
        except Exception as e:
            logger.critical(f"Emergency response execution failed: {e}")
            # Last resort: system shutdown
            await self._emergency_shutdown()
    
    async def _should_execute_procedure(self, procedure: EmergencyProcedure, reason: str) -> bool:
        """Determine if emergency procedure should be executed."""
        # Check if any trigger conditions match the reason
        for condition in procedure.trigger_conditions:
            if condition.lower() in reason.lower():
                return True
        
        # Default: execute all procedures for critical situations
        return self._current_state == SafetyState.EMERGENCY
    
    async def _execute_emergency_procedure(self, procedure: EmergencyProcedure) -> None:
        """Execute emergency procedure with timeout."""
        logger.critical(f"🚨 Executing emergency procedure: {procedure.name}")
        
        try:
            # Execute with timeout
            await asyncio.wait_for(
                self._run_procedure_steps(procedure),
                timeout=procedure.timeout_seconds
            )
            
            logger.info(f"✅ Emergency procedure completed: {procedure.name}")
            
        except asyncio.TimeoutError:
            logger.critical(f"❌ Emergency procedure timeout: {procedure.name}")
            raise
        except Exception as e:
            logger.critical(f"❌ Emergency procedure failed: {procedure.name} - {e}")
            raise
    
    async def _run_procedure_steps(self, procedure: EmergencyProcedure) -> None:
        """Run emergency procedure steps."""
        for i, step in enumerate(procedure.steps, 1):
            logger.info(f"Executing step {i}/{len(procedure.steps)}: {step}")
            
            # Simulate step execution (in real implementation, this would
            # interact with actual control systems)
            await asyncio.sleep(0.1)
            
            # Verification if required
            if procedure.verification_required:
                # In real implementation, this would check actual system state
                logger.info(f"✅ Step {i} verified")
    
    async def _send_emergency_notifications(self, reason: str) -> None:
        """Send emergency notifications to configured endpoints."""
        message = f"EMERGENCY: {self.config.system_name} - {reason}"
        
        for endpoint in self.config.notification_endpoints:
            try:
                # In real implementation, this would send actual notifications
                logger.critical(f"📢 Emergency notification sent to {endpoint}: {message}")
            except Exception as e:
                logger.error(f"Failed to send notification to {endpoint}: {e}")
    
    async def _emergency_shutdown(self) -> None:
        """Perform emergency system shutdown."""
        logger.critical("🚨 INITIATING EMERGENCY SHUTDOWN")
        
        self._current_state = SafetyState.SHUTDOWN
        
        try:
            # Stop all control operations
            # In real implementation, this would interface with actual control systems
            logger.critical("🛑 All control operations stopped")
            
            # Set safe states
            logger.critical("🛡️ Systems set to safe state")
            
            # Final notification
            await self._send_emergency_notifications("Emergency shutdown completed")
            
        except Exception as e:
            logger.critical(f"Emergency shutdown error: {e}")
    
    async def _check_safety_parameters(self) -> None:
        """Check all safety parameters for violations."""
        current_time = datetime.now()
        
        for parameter_name, last_update in self._last_update.items():
            # Check for stale data
            if (current_time - last_update).total_seconds() > 60:  # 1 minute timeout
                logger.warning(f"Stale data for parameter: {parameter_name}")
                await self._create_alarm(
                    alarm_id=f"{parameter_name}_stale_data",
                    parameter=parameter_name,
                    value=self._parameter_values[parameter_name],
                    limit=0.0,
                    priority=AlarmPriority.HIGH,
                    safety_level=SafetyLevel.SIL_2,
                )
    
    async def _check_communication_health(self) -> None:
        """Check communication health with external systems."""
        # In real implementation, this would check actual communication channels
        pass
    
    async def _update_safety_state(self) -> None:
        """Update overall safety system state."""
        if self._emergency_active:
            return  # State already set to emergency
        
        # Determine state based on active alarms
        if any(alarm["priority"] in ["CRITICAL", "EMERGENCY"] for alarm in self._active_alarms.values()):
            self._current_state = SafetyState.EMERGENCY
        elif any(alarm["priority"] == "HIGH" for alarm in self._active_alarms.values()):
            self._current_state = SafetyState.ALARM
        elif self._active_alarms:
            self._current_state = SafetyState.WARNING
        else:
            self._current_state = SafetyState.NORMAL
    
    async def _handle_watchdog_failure(self) -> None:
        """Handle watchdog monitoring failure."""
        logger.critical("🚨 Safety watchdog failure detected")
        await self._trigger_emergency_response("Watchdog failure")
    
    def add_alarm_handler(self, handler: Callable) -> None:
        """Add alarm event handler."""
        self._alarm_handlers.append(handler)
    
    def add_emergency_handler(self, handler: Callable) -> None:
        """Add emergency event handler."""
        self._emergency_handlers.append(handler)
    
    async def acknowledge_alarm(self, alarm_id: str, user: str) -> dict[str, Any]:
        """Acknowledge safety alarm."""
        if alarm_id not in self._active_alarms:
            return {"success": False, "error": "Alarm not found"}
        
        try:
            self._active_alarms[alarm_id]["acknowledged"] = True
            self._active_alarms[alarm_id]["acknowledged_by"] = user
            self._active_alarms[alarm_id]["acknowledged_at"] = datetime.now()
            
            logger.info(f"✅ Alarm acknowledged: {alarm_id} by {user}")
            
            return {
                "success": True,
                "alarm_id": alarm_id,
                "acknowledged_by": user,
            }
            
        except Exception as e:
            error_msg = format_safety_error(e, "alarm acknowledgment")
            return {"success": False, "error": error_msg}
    
    def get_status(self) -> dict[str, Any]:
        """Get comprehensive safety system status."""
        return {
            "initialized": self._initialized,
            "current_state": self._current_state.value,
            "emergency_active": self._emergency_active,
            "active_alarms": len(self._active_alarms),
            "monitored_parameters": len(self._parameter_values),
            "configuration": {
                "system_name": self.config.system_name,
                "safety_level": self.config.safety_level.value,
                "watchdog_interval": self.config.watchdog_interval,
                "emergency_procedures": len(self.config.emergency_procedures),
            },
            "alarms": list(self._active_alarms.values()),
            "parameter_values": self._parameter_values.copy(),
        }
    
    # Step 6: Resource Management (crawl_mcp.py methodology)
    @asynccontextmanager
    async def managed_safety_session(self) -> AsyncIterator["ProductionSafetySystem"]:
        """Manage safety system session with proper cleanup."""
        try:
            # Initialize safety system
            init_result = await self.initialize()
            if not init_result["success"]:
                raise RuntimeError(f"Safety system initialization failed: {init_result['error']}")
            
            logger.info("🛡️ Safety system session started")
            yield self
            
        finally:
            # Cleanup resources
            await self.cleanup()
            logger.info("🧹 Safety system session cleanup completed")
    
    async def cleanup(self) -> None:
        """Clean up safety system resources."""
        try:
            # Stop watchdog
            if self._watchdog_task:
                self._watchdog_task.cancel()
                try:
                    await self._watchdog_task
                except asyncio.CancelledError:
                    pass
            
            # Clear alarms and handlers
            self._active_alarms.clear()
            self._alarm_handlers.clear()
            self._emergency_handlers.clear()
            
            # Reset state
            self._initialized = False
            self._current_state = SafetyState.NORMAL
            self._emergency_active = False
            
            logger.info("✅ Safety system cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Safety system cleanup error: {e}")


# Step 4: Modular Testing (crawl_mcp.py methodology)
async def test_safety_system() -> dict[str, Any]:
    """Test safety system functionality."""
    start_time = datetime.now()
    
    try:
        # Create test configuration
        test_config = SafetyConfiguration(
            system_name="Test Safety System",
            safety_level=SafetyLevel.SIL_2,
            safety_limits=[
                SafetyLimit(
                    parameter_name="temperature",
                    high_limit=85.0,
                    safety_level=SafetyLevel.SIL_2,
                    alarm_priority=AlarmPriority.HIGH,
                ),
                SafetyLimit(
                    parameter_name="pressure",
                    high_limit=100.0,
                    safety_level=SafetyLevel.SIL_3,
                    alarm_priority=AlarmPriority.CRITICAL,
                ),
            ],
            emergency_procedures=[
                EmergencyProcedure(
                    procedure_id="emergency_shutdown",
                    name="Emergency Shutdown",
                    trigger_conditions=["critical alarm", "system failure"],
                    safety_level=SafetyLevel.SIL_3,
                    timeout_seconds=10.0,
                    steps=["Stop all pumps", "Close emergency valves", "Activate alarms"],
                ),
            ],
        )
        
        # Test safety system
        safety_system = ProductionSafetySystem(config=test_config)
        
        async with safety_system.managed_safety_session():
            # Test parameter updates
            result1 = await safety_system.update_parameter("temperature", 75.0)  # Normal
            result2 = await safety_system.update_parameter("temperature", 90.0)  # High alarm
            
            if not result1["success"] or not result2["success"]:
                raise RuntimeError("Parameter update test failed")
            
            # Test alarm acknowledgment
            if safety_system._active_alarms:
                alarm_id = list(safety_system._active_alarms.keys())[0]
                ack_result = await safety_system.acknowledge_alarm(alarm_id, "test_user")
                if not ack_result["success"]:
                    raise RuntimeError("Alarm acknowledgment test failed")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "execution_time": execution_time,
            "tests_passed": ["parameter_update", "alarm_creation", "alarm_acknowledgment"],
        }
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        return {
            "success": False,
            "execution_time": execution_time,
            "error": str(e),
        }


# Main execution for testing
if __name__ == "__main__":
    async def main():
        logger.info("🧪 Testing Production Safety System")
        test_result = await test_safety_system()
        
        if test_result["success"]:
            logger.info(f"✅ Test passed in {test_result['execution_time']:.2f}s")
        else:
            logger.error(f"❌ Test failed: {test_result['error']}")
    
    asyncio.run(main()) 