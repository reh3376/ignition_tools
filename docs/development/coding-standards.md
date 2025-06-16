# Jython/Ignition Coding Standards

This document outlines coding standards and best practices for developing Jython scripts for Ignition SCADA systems using the IGN Scripts toolkit.

## Table of Contents

1. [Overview](#overview)
2. [Jython Language Standards](#jython-language-standards)
3. [Ignition Context Considerations](#ignition-context-considerations)
4. [Script Structure and Organization](#script-structure-and-organization)
5. [Error Handling and Logging](#error-handling-and-logging)
6. [Performance Guidelines](#performance-guidelines)
7. [Security Best Practices](#security-best-practices)
8. [Testing Standards](#testing-standards)
9. [Documentation Requirements](#documentation-requirements)
10. [Code Examples](#code-examples)

## Overview

### Target Environment

- **Jython Version**: 2.7 (Python 2.7 syntax with Java integration)
- **Ignition Version**: 8.1+ (primary), 8.0 (limited support)
- **Java Runtime**: OpenJDK 11+ (as used by Ignition)
- **Execution Contexts**: Gateway, Vision Client, Perspective Session

### Key Principles

1. **Compatibility**: Code must work in Jython 2.7 environment
2. **Context Awareness**: Consider the Ignition execution context
3. **Error Resilience**: Handle errors gracefully without breaking systems
4. **Performance**: Minimize resource usage and execution time
5. **Security**: Follow security best practices for industrial systems
6. **Maintainability**: Write clear, documented, and testable code

## Jython Language Standards

### Python 2.7 Syntax Compliance

Since Jython 2.7 is based on Python 2.7, follow Python 2.7 syntax:

```python
# Good - Python 2.7 compatible
print "Hello, World!"
raw_input("Enter value: ")
xrange(10)

# Bad - Python 3 syntax not supported
print("Hello, World!")  # Works but not required
input("Enter value:")   # Not available
range(10)              # Less efficient than xrange
```

### Import Statements

Organize imports in the following order:

```python
# 1. Java standard library imports
from java.lang import System
from java.util import Date, ArrayList
from javax.swing import JOptionPane

# 2. Ignition system function imports
from system.tag import readBlocking, writeBlocking
from system.db import runNamedQuery
from system.gui import messageBox

# 3. Custom module imports (if applicable)
from shared.utilities import format_timestamp
```

### Variable Naming Conventions

```python
# Use snake_case for variables and functions
tag_path = "[PLC]Production/Line1/Speed"
current_timestamp = system.date.now()

# Use UPPER_CASE for constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_MS = 5000

# Use descriptive names for Ignition-specific variables
gateway_context = system.util.getContext()
vision_window = system.nav.getCurrentWindow()
```

### Function Definitions

```python
def read_tag_value(tag_path, default_value=None):
    """
    Read a tag value with error handling and default fallback.
    
    Args:
        tag_path (str): The tag path to read
        default_value: Value to return if read fails
        
    Returns:
        The tag value or default_value if read fails
        
    Example:
        speed = read_tag_value("[PLC]Production/Line1/Speed", 0.0)
    """
    try:
        quality_value = system.tag.readBlocking([tag_path])[0]
        if quality_value.quality.isGood():
            return quality_value.value
        else:
            logger = system.util.getLogger("TagReader")
            logger.warn("Poor quality for tag: %s, Quality: %s" % 
                       (tag_path, quality_value.quality))
            return default_value
    except Exception, e:
        logger = system.util.getLogger("TagReader")
        logger.error("Failed to read tag %s: %s" % (tag_path, str(e)))
        return default_value
```

## Ignition Context Considerations

### Gateway Context Scripts

Gateway scripts run on the Ignition Gateway and have access to system resources:

```python
# Gateway startup script example
def gateway_startup():
    """Initialize gateway-level resources on startup."""
    logger = system.util.getLogger("GatewayStartup")
    logger.info("Starting gateway initialization...")
    
    try:
        # Initialize database connections
        system.db.runUpdateQuery(
            "UPDATE system_status SET status = 'starting' WHERE id = 1"
        )
        
        # Set up initial tag values
        tag_writes = [
            ("[Gateway]System/StartupTime", system.date.now()),
            ("[Gateway]System/Status", "Running")
        ]
        system.tag.writeBlocking(
            [write[0] for write in tag_writes],
            [write[1] for write in tag_writes]
        )
        
        logger.info("Gateway initialization completed successfully")
        
    except Exception, e:
        logger.error("Gateway startup failed: %s" % str(e))
        # Don't re-raise - gateway should continue to start
```

### Vision Client Context

Vision client scripts run in the Vision module with access to Swing components:

```python
# Vision component event handler
def button_actionPerformed(event):
    """Handle button click in Vision client."""
    component = event.source
    window = system.nav.getCurrentWindow()
    
    try:
        # Get user input with validation
        user_input = system.gui.inputBox(
            "Enter production speed (0-100):",
            "Speed Input"
        )
        
        if user_input is not None:
            speed_value = float(user_input)
            
            # Validate input range
            if 0 <= speed_value <= 100:
                # Write to tag
                system.tag.writeBlocking(
                    ["[PLC]Production/Line1/SetSpeed"],
                    [speed_value]
                )
                
                # Update component display
                window.getComponentForPath("Root Container.SpeedLabel").text = \
                    "Speed: %.1f %%" % speed_value
                    
                # Show confirmation
                system.gui.messageBox("Speed updated successfully!")
            else:
                system.gui.errorBox("Speed must be between 0 and 100")
                
    except ValueError:
        system.gui.errorBox("Please enter a valid number")
    except Exception, e:
        logger = system.util.getLogger("VisionUI")
        logger.error("Speed update failed: %s" % str(e))
        system.gui.errorBox("Failed to update speed: %s" % str(e))
```

### Perspective Session Context

Perspective scripts run in web-based sessions with different capabilities:

```python
# Perspective view script
def update_dashboard_data(view):
    """Update dashboard data for Perspective session."""
    logger = system.util.getLogger("PerspectiveDashboard")
    
    try:
        # Read multiple tags efficiently
        tag_paths = [
            "[PLC]Production/Line1/Speed",
            "[PLC]Production/Line1/Temperature",
            "[PLC]Production/Line1/Pressure"
        ]
        
        tag_values = system.tag.readBlocking(tag_paths)
        
        # Build data structure for Perspective
        dashboard_data = {
            "timestamp": system.date.now(),
            "metrics": {}
        }
        
        for i, tag_path in enumerate(tag_paths):
            tag_name = tag_path.split("/")[-1]  # Extract tag name
            quality_value = tag_values[i]
            
            dashboard_data["metrics"][tag_name] = {
                "value": quality_value.value if quality_value.quality.isGood() else None,
                "quality": str(quality_value.quality),
                "timestamp": quality_value.timestamp
            }
        
        # Update view parameters
        view.custom.dashboard_data = dashboard_data
        
        logger.debug("Dashboard data updated successfully")
        
    except Exception, e:
        logger.error("Dashboard update failed: %s" % str(e))
        # Set error state in view
        view.custom.error_message = "Data update failed: %s" % str(e)
```

## Script Structure and Organization

### Script Header Template

```python
"""
Script: Production Line Speed Control
Context: Vision Client - Button Event Handler
Author: Manufacturing Engineering
Created: 2025-01-28
Version: 1.0.0

Description:
    Handles user input for production line speed control with validation
    and error handling. Updates both PLC tags and UI display.

Dependencies:
    - Tags: [PLC]Production/Line1/SetSpeed, [PLC]Production/Line1/ActualSpeed
    - Components: Root Container.SpeedLabel, Root Container.StatusLabel
    
Security Considerations:
    - Validates input range to prevent equipment damage
    - Logs all speed changes for audit trail
"""

# Import required modules at the top
from system.tag import readBlocking, writeBlocking
from system.gui import messageBox, errorBox, inputBox
from system.util import getLogger

# Constants
MIN_SPEED = 0.0
MAX_SPEED = 100.0
SPEED_TAG_PATH = "[PLC]Production/Line1/SetSpeed"
```

### Function Organization

```python
# Utility functions first
def validate_speed_input(speed_str):
    """Validate and convert speed input string to float."""
    try:
        speed = float(speed_str)
        if MIN_SPEED <= speed <= MAX_SPEED:
            return speed, None  # Valid speed, no error
        else:
            return None, "Speed must be between %.1f and %.1f" % (MIN_SPEED, MAX_SPEED)
    except (ValueError, TypeError):
        return None, "Please enter a valid number"

def update_speed_display(window, speed_value):
    """Update the speed display in the UI."""
    try:
        speed_label = window.getComponentForPath("Root Container.SpeedLabel")
        speed_label.text = "Speed: %.1f %%" % speed_value
        return True
    except Exception, e:
        logger = getLogger("SpeedControl")
        logger.error("Failed to update display: %s" % str(e))
        return False

# Main event handler
def button_actionPerformed(event):
    """Main button event handler - entry point."""
    # Implementation here
    pass
```

## Error Handling and Logging

### Exception Handling Patterns

```python
# Pattern 1: Graceful degradation
def read_tag_with_fallback(tag_path, fallback_value):
    """Read tag with fallback to default value on failure."""
    try:
        result = system.tag.readBlocking([tag_path])[0]
        if result.quality.isGood():
            return result.value
        else:
            # Log warning but continue
            logger = system.util.getLogger("TagReader")
            logger.warn("Poor quality for %s: %s" % (tag_path, result.quality))
            return fallback_value
    except Exception, e:
        # Log error but don't crash
        logger = system.util.getLogger("TagReader")
        logger.error("Tag read failed for %s: %s" % (tag_path, str(e)))
        return fallback_value

# Pattern 2: Critical error handling
def write_critical_tag(tag_path, value):
    """Write to critical tag with proper error handling."""
    logger = system.util.getLogger("CriticalWrite")
    
    try:
        # Attempt the write
        result = system.tag.writeBlocking([tag_path], [value])
        
        # Check if write was successful
        if len(result) > 0 and not result[0].quality.isGood():
            error_msg = "Write failed - Poor quality: %s" % result[0].quality
            logger.error(error_msg)
            raise Exception(error_msg)
            
        logger.info("Successfully wrote %s to %s" % (value, tag_path))
        return True
        
    except Exception, e:
        logger.error("Critical tag write failed: %s" % str(e))
        # For critical operations, re-raise the exception
        raise
```

### Logging Best Practices

```python
# Configure logger at module level
logger = system.util.getLogger("ProductionControl")

def process_production_data():
    """Process production data with comprehensive logging."""
    logger.info("Starting production data processing")
    
    try:
        # Log important milestones
        logger.debug("Reading production tags...")
        tag_values = read_production_tags()
        
        logger.debug("Validating data quality...")
        validated_data = validate_production_data(tag_values)
        
        logger.info("Processing %d data points" % len(validated_data))
        results = calculate_kpis(validated_data)
        
        logger.info("Production data processing completed successfully")
        return results
        
    except ValidationError, e:
        logger.warn("Data validation failed: %s" % str(e))
        return None
    except Exception, e:
        logger.error("Production data processing failed: %s" % str(e))
        raise  # Re-raise for critical processes

# Log levels usage:
# DEBUG: Detailed diagnostic information
# INFO: General information about normal operation
# WARN: Something unexpected happened but system continues
# ERROR: Serious problem that prevented operation from completing
```

## Performance Guidelines

### Tag Reading Optimization

```python
# Good - Batch read multiple tags
def read_multiple_tags_efficient(tag_paths):
    """Efficiently read multiple tags in a single call."""
    return system.tag.readBlocking(tag_paths)

# Bad - Individual tag reads in loop
def read_multiple_tags_inefficient(tag_paths):
    """Inefficient approach - avoid this pattern."""
    results = []
    for tag_path in tag_paths:
        result = system.tag.readBlocking([tag_path])[0]
        results.append(result)
    return results
```

### Database Query Optimization

```python
# Good - Use parameterized queries
def get_production_data(line_id, start_date, end_date):
    """Get production data using parameterized query."""
    return system.db.runQuery(
        "SELECT * FROM production_data WHERE line_id = ? AND timestamp BETWEEN ? AND ?",
        [line_id, start_date, end_date]
    )

# Good - Use named queries for complex operations
def get_production_summary(line_id):
    """Get production summary using named query."""
    return system.db.runNamedQuery(
        "Production/GetLineSummary",
        {"lineId": line_id}
    )
```

### Memory Management

```python
# Good - Clean up resources
def process_large_dataset(data_source):
    """Process large dataset with proper resource management."""
    dataset = None
    try:
        dataset = system.db.runQuery(data_source)
        
        # Process data in chunks to avoid memory issues
        chunk_size = 1000
        results = []
        
        for i in xrange(0, dataset.rowCount, chunk_size):
            chunk = []
            for row in xrange(i, min(i + chunk_size, dataset.rowCount)):
                chunk.append(dataset.getValueAt(row, "value"))
            
            # Process chunk
            processed_chunk = process_data_chunk(chunk)
            results.extend(processed_chunk)
            
        return results
        
    finally:
        # Ensure dataset is cleaned up
        if dataset is not None:
            dataset = None
```

## Security Best Practices

### Input Validation

```python
def validate_user_input(user_input, input_type="string"):
    """Validate user input to prevent injection attacks."""
    if user_input is None:
        return False, "Input cannot be empty"
    
    # Convert to string and check length
    input_str = str(user_input).strip()
    if len(input_str) == 0:
        return False, "Input cannot be empty"
    
    if len(input_str) > 1000:  # Reasonable limit
        return False, "Input too long"
    
    if input_type == "numeric":
        try:
            float(input_str)
        except ValueError:
            return False, "Input must be numeric"
    
    elif input_type == "tag_path":
        # Basic tag path validation
        if not (input_str.startswith("[") and "]" in input_str):
            return False, "Invalid tag path format"
    
    return True, None
```

### Secure Database Operations

```python
def safe_database_query(query_name, parameters):
    """Execute database query safely with parameter validation."""
    logger = system.util.getLogger("DatabaseSecurity")
    
    # Validate parameters
    if not isinstance(parameters, dict):
        logger.error("Parameters must be a dictionary")
        return None
    
    # Log query execution (without sensitive data)
    logger.info("Executing query: %s" % query_name)
    
    try:
        # Use named queries to prevent SQL injection
        result = system.db.runNamedQuery(query_name, parameters)
        logger.debug("Query executed successfully, returned %d rows" % result.rowCount)
        return result
        
    except Exception, e:
        logger.error("Query execution failed: %s" % str(e))
        return None
```

## Testing Standards

### Unit Test Structure

Since Jython testing is limited, focus on testable logic:

```python
# testable_logic.py - Separate business logic for testing
def calculate_efficiency(actual_output, target_output):
    """Calculate production efficiency percentage."""
    if target_output <= 0:
        raise ValueError("Target output must be positive")
    
    if actual_output < 0:
        raise ValueError("Actual output cannot be negative")
    
    efficiency = (float(actual_output) / target_output) * 100.0
    return min(efficiency, 100.0)  # Cap at 100%

def validate_temperature_range(temperature, min_temp, max_temp):
    """Validate temperature is within acceptable range."""
    if not isinstance(temperature, (int, float)):
        return False, "Temperature must be numeric"
    
    if temperature < min_temp:
        return False, "Temperature too low"
    
    if temperature > max_temp:
        return False, "Temperature too high"
    
    return True, None

# integration_script.py - Ignition integration
def update_efficiency_display(event):
    """Update efficiency display - integrates with testable logic."""
    try:
        # Read values from tags
        actual = system.tag.readBlocking(["[PLC]Production/ActualOutput"])[0].value
        target = system.tag.readBlocking(["[PLC]Production/TargetOutput"])[0].value
        
        # Use testable function
        efficiency = calculate_efficiency(actual, target)
        
        # Update display
        component = event.source.parent.getComponent("EfficiencyLabel")
        component.text = "Efficiency: %.1f%%" % efficiency
        
    except Exception, e:
        system.gui.errorBox("Efficiency calculation failed: %s" % str(e))
```

## Documentation Requirements

### Script Documentation Template

```python
"""
==============================================================================
IGNITION SCRIPT DOCUMENTATION
==============================================================================

Script Name: Production Line Control System
Script Type: Gateway Timer Script
Execution Context: Gateway
Schedule: Fixed Rate - Every 30 seconds

==============================================================================
PURPOSE
==============================================================================
Monitors production line status and automatically adjusts control parameters
based on current conditions. Implements safety interlocks and alarm handling.

==============================================================================
DEPENDENCIES
==============================================================================

Tags:
- [PLC]Production/Line1/Status (Read) - Line operational status
- [PLC]Production/Line1/Speed (Read/Write) - Current and setpoint speed
- [PLC]Production/Line1/Temperature (Read) - Process temperature
- [Safety]EmergencyStop (Read) - Emergency stop status

Named Queries:
- Production/LogSpeedChange - Log speed adjustments
- Alarms/CreateAlarm - Create alarm records

Components: None (Gateway script)

==============================================================================
CONFIGURATION
==============================================================================

Constants (modify as needed):
- MAX_SPEED: 100.0 (Maximum allowed speed)
- MIN_SPEED: 0.0 (Minimum allowed speed)
- TEMP_LIMIT: 85.0 (Temperature alarm threshold)
- SPEED_INCREMENT: 5.0 (Speed adjustment increment)

==============================================================================
OPERATION
==============================================================================

Normal Operation:
1. Reads current line status and parameters
2. Checks safety conditions (emergency stop, temperature)
3. Adjusts speed based on temperature conditions
4. Logs any changes to database
5. Updates alarm status as needed

Error Conditions:
- Emergency stop activated: Sets speed to 0, creates alarm
- High temperature: Reduces speed, creates warning
- Communication failure: Maintains last known good state

==============================================================================
MAINTENANCE
==============================================================================

Version History:
- v1.0.0 (2025-01-28): Initial implementation
- v1.1.0 (TBD): Add predictive temperature control

Known Issues:
- None currently

Scheduled Reviews:
- Quarterly review of temperature thresholds
- Annual review of safety logic

==============================================================================
"""

# Constants - modify these values as needed for your system
MAX_SPEED = 100.0
MIN_SPEED = 0.0
TEMP_LIMIT = 85.0
SPEED_INCREMENT = 5.0

# Rest of script implementation...
```

## Code Examples

### Complete Script Examples

#### Gateway Startup Script

```python
"""
Gateway startup script for production system initialization.
Context: Gateway Startup Event
"""

def gateway_startup():
    """Initialize production system on gateway startup."""
    logger = system.util.getLogger("ProductionStartup")
    logger.info("=== Production System Startup ===")
    
    try:
        # 1. Initialize system status tags
        startup_tags = [
            ("[Gateway]System/StartupTime", system.date.now()),
            ("[Gateway]System/Status", "Initializing"),
            ("[Gateway]System/Version", "1.0.0")
        ]
        
        tag_paths = [tag[0] for tag in startup_tags]
        tag_values = [tag[1] for tag in startup_tags]
        
        system.tag.writeBlocking(tag_paths, tag_values)
        logger.info("System tags initialized")
        
        # 2. Verify database connectivity
        test_query = system.db.runQuery("SELECT 1 as test")
        if test_query.rowCount > 0:
            logger.info("Database connectivity verified")
        else:
            raise Exception("Database test query failed")
        
        # 3. Initialize production lines
        initialize_production_lines()
        
        # 4. Set final status
        system.tag.writeBlocking(
            ["[Gateway]System/Status"],
            ["Running"]
        )
        
        logger.info("=== Production System Startup Complete ===")
        
    except Exception, e:
        logger.error("Startup failed: %s" % str(e))
        system.tag.writeBlocking(
            ["[Gateway]System/Status"],
            ["Startup Failed"]
        )

def initialize_production_lines():
    """Initialize all production lines to default state."""
    logger = system.util.getLogger("ProductionStartup")
    
    # Get list of production lines from database
    lines_query = system.db.runNamedQuery("Production/GetActiveLines", {})
    
    for row in range(lines_query.rowCount):
        line_id = lines_query.getValueAt(row, "line_id")
        line_name = lines_query.getValueAt(row, "line_name")
        
        try:
            # Initialize each line
            init_tags = [
                ("[PLC]Production/%s/Status" % line_name, "Stopped"),
                ("[PLC]Production/%s/Speed" % line_name, 0.0),
                ("[PLC]Production/%s/LastStartup" % line_name, system.date.now())
            ]
            
            tag_paths = [tag[0] for tag in init_tags]
            tag_values = [tag[1] for tag in init_tags]
            
            system.tag.writeBlocking(tag_paths, tag_values)
            
            logger.info("Initialized production line: %s" % line_name)
            
        except Exception, e:
            logger.error("Failed to initialize line %s: %s" % (line_name, str(e)))

# Execute startup
gateway_startup()
```

This comprehensive coding standards document provides the foundation for consistent, reliable Jython script development in Ignition environments. Following these standards will ensure scripts are maintainable, secure, and perform well in production systems.

---

*Last updated: 2025-01-28* 