"""Logging Operations Module for Task 6.

Provides logging utility functions including:
- Logger level management
- Logging configuration
- Diagnostic level management

Functions: 12 functions
Contexts: Gateway
"""

from typing import Any


def get_logging_operations_functions() -> list[dict[str, Any]]:
    """Get logging operations functions.

    Returns:
        List[Dict[str, Any]]: List of logging operation function definitions
    """
    return [
        {
            "name": "system.util.getLoggerLevel",
            "description": "Get current logging level for specified logger",
            "parameters": [
                {
                    "name": "loggerName",
                    "type": "str",
                    "description": "Name of logger to query",
                    "required": True,
                },
                {
                    "name": "context",
                    "type": "str",
                    "description": "Context scope for logger",
                    "required": False,
                    "default": "system",
                },
            ],
            "returns": {
                "type": "str",
                "description": "Current logging level (TRACE, DEBUG, INFO, WARN, ERROR)",
            },
            "scope": ["Gateway"],
            "category": "Logging Operations",
            "patterns": [
                "logging_configuration",
                "system_monitoring",
                "diagnostic_level_management",
            ],
        },
        {
            "name": "system.util.setLoggerLevel",
            "description": "Set logging level for specified logger",
            "parameters": [
                {
                    "name": "loggerName",
                    "type": "str",
                    "description": "Name of logger to configure",
                    "required": True,
                },
                {
                    "name": "level",
                    "type": "str",
                    "description": "Logging level to set",
                    "required": True,
                },
                {
                    "name": "persist",
                    "type": "bool",
                    "description": "Whether to persist logging changes",
                    "required": False,
                    "default": True,
                },
            ],
            "returns": {
                "type": "bool",
                "description": "True if logging level was successfully set",
            },
            "scope": ["Gateway"],
            "category": "Logging Operations",
            "patterns": [
                "logging_management",
                "diagnostic_configuration",
                "system_administration",
            ],
        },
        {
            "name": "system.util.configureLogging",
            "description": "Configure comprehensive logging settings",
            "parameters": [
                {
                    "name": "configuration",
                    "type": "dict",
                    "description": "Logging configuration dictionary",
                    "required": True,
                },
                {
                    "name": "resetToDefaults",
                    "type": "bool",
                    "description": "Reset to default configuration first",
                    "required": False,
                    "default": False,
                },
            ],
            "returns": {
                "type": "bool",
                "description": "True if logging was successfully configured",
            },
            "scope": ["Gateway"],
            "category": "Logging Operations",
            "patterns": [
                "logging_setup",
                "system_configuration",
                "diagnostic_management",
            ],
        },
    ]
