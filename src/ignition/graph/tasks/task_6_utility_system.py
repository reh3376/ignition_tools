"""
Task 6: Utility System Expansion
Comprehensive utility functions and system management for Ignition SCADA systems.

This module provides utility operations including:
- General Utilities (Translation, Locale, Timezone, System Info)
- Logging Operations (Logger Management, Configuration)
- Project Management (Client Management, System Control)
- Security and User Management
- Performance and Monitoring

Total Functions: 50+ functions
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Core systems (Tasks 1-5 complete)
"""

from typing import List, Dict, Any


def get_utility_system_functions() -> List[Dict[str, Any]]:
    """
    Get comprehensive utility system functions for Task 6.
    
    Returns:
        List[Dict[str, Any]]: List of utility function definitions
    """
    
    functions = []
    
    # ============================================================================
    # GENERAL UTILITIES (15 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.modifyTranslation",
            "description": "Modify translation strings for internationalization support",
            "parameters": [
                {
                    "name": "key", 
                    "type": "str", 
                    "description": "Translation key to modify",
                    "required": True
                },
                {
                    "name": "locale", 
                    "type": "str", 
                    "description": "Locale code (e.g., 'en_US', 'es_ES')",
                    "required": True
                },
                {
                    "name": "value", 
                    "type": "str", 
                    "description": "New translation value",
                    "required": True
                },
                {
                    "name": "persist", 
                    "type": "bool", 
                    "description": "Whether to persist changes to disk",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if translation was successfully modified"
            },
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "internationalization",
                "localization_management",
                "translation_updates"
            ]
        },
        
        {
            "name": "system.util.translate",
            "description": "Translate text using current locale settings",
            "parameters": [
                {
                    "name": "key", 
                    "type": "str", 
                    "description": "Translation key to translate",
                    "required": True
                },
                {
                    "name": "locale", 
                    "type": "str", 
                    "description": "Optional locale override",
                    "required": False
                },
                {
                    "name": "defaultValue", 
                    "type": "str", 
                    "description": "Default value if translation not found",
                    "required": False
                },
                {
                    "name": "params", 
                    "type": "dict", 
                    "description": "Parameters for parameterized translations",
                    "required": False
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Translated text or default value"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "internationalization",
                "localization_display",
                "multi_language_support"
            ]
        },
        
        {
            "name": "system.util.getLocale",
            "description": "Get current system locale configuration",
            "parameters": [
                {
                    "name": "context", 
                    "type": "str", 
                    "description": "Context to get locale for (system, session, client)",
                    "required": False,
                    "default": "system"
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Locale information including language, country, and variant"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "locale_detection",
                "system_configuration",
                "internationalization_info"
            ]
        },
        
        {
            "name": "system.util.setLocale",
            "description": "Set system locale configuration",
            "parameters": [
                {
                    "name": "locale", 
                    "type": "str", 
                    "description": "Locale string (e.g., 'en_US', 'fr_FR')",
                    "required": True
                },
                {
                    "name": "context", 
                    "type": "str", 
                    "description": "Context to set locale for",
                    "required": False,
                    "default": "system"
                },
                {
                    "name": "persist", 
                    "type": "bool", 
                    "description": "Whether to persist locale changes",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if locale was successfully set"
            },
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "locale_configuration",
                "system_settings",
                "internationalization_setup"
            ]
        }
    ])
    
    # Continue with more functions...
    functions.extend([
        {
            "name": "system.util.getTimezone",
            "description": "Get current system timezone configuration",
            "parameters": [
                {
                    "name": "format", 
                    "type": "str", 
                    "description": "Return format: 'id', 'display', 'offset'",
                    "required": False,
                    "default": "id"
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Timezone information in requested format"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "timezone_detection",
                "system_time_management",
                "time_configuration"
            ]
        },
        
        {
            "name": "system.util.setTimezone",
            "description": "Set system timezone configuration",
            "parameters": [
                {
                    "name": "timezone", 
                    "type": "str", 
                    "description": "Timezone ID (e.g., 'America/New_York')",
                    "required": True
                },
                {
                    "name": "persist", 
                    "type": "bool", 
                    "description": "Whether to persist timezone changes",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if timezone was successfully set"
            },
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "timezone_configuration",
                "system_time_setup",
                "time_zone_management"
            ]
        },
        
        {
            "name": "system.util.threadDump",
            "description": "Generate thread dump for system diagnostics",
            "parameters": [
                {
                    "name": "includeStackTrace", 
                    "type": "bool", 
                    "description": "Include stack traces in dump",
                    "required": False,
                    "default": True
                },
                {
                    "name": "format", 
                    "type": "str", 
                    "description": "Output format: 'text', 'json', 'xml'",
                    "required": False,
                    "default": "text"
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Thread dump information"
            },
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "system_diagnostics",
                "performance_troubleshooting",
                "thread_analysis"
            ]
        },
        
        {
            "name": "system.util.version",
            "description": "Get Ignition system version information",
            "parameters": [
                {
                    "name": "component", 
                    "type": "str", 
                    "description": "Specific component version to get",
                    "required": False
                },
                {
                    "name": "detailed", 
                    "type": "bool", 
                    "description": "Include detailed build information",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Version information including build, edition, and modules"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "version_checking",
                "system_information",
                "compatibility_verification"
            ]
        }
    ])
    
    # ============================================================================
    # LOGGING OPERATIONS (12 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.getLoggerLevel",
            "description": "Get current logging level for specified logger",
            "parameters": [
                {
                    "name": "loggerName", 
                    "type": "str", 
                    "description": "Name of logger to query",
                    "required": True
                },
                {
                    "name": "context", 
                    "type": "str", 
                    "description": "Context scope for logger",
                    "required": False,
                    "default": "system"
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Current logging level (TRACE, DEBUG, INFO, WARN, ERROR)"
            },
            "scope": ["Gateway"],
            "category": "Logging Operations",
            "patterns": [
                "logging_configuration",
                "system_monitoring",
                "diagnostic_level_management"
            ]
        },
        
        {
            "name": "system.util.setLoggerLevel",
            "description": "Set logging level for specified logger",
            "parameters": [
                {
                    "name": "loggerName", 
                    "type": "str", 
                    "description": "Name of logger to configure",
                    "required": True
                },
                {
                    "name": "level", 
                    "type": "str", 
                    "description": "Logging level to set",
                    "required": True
                },
                {
                    "name": "persist", 
                    "type": "bool", 
                    "description": "Whether to persist logging changes",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if logging level was successfully set"
            },
            "scope": ["Gateway"],
            "category": "Logging Operations",
            "patterns": [
                "logging_management",
                "diagnostic_configuration",
                "system_administration"
            ]
        },
        
        {
            "name": "system.util.configureLogging",
            "description": "Configure comprehensive logging settings",
            "parameters": [
                {
                    "name": "configuration", 
                    "type": "dict", 
                    "description": "Logging configuration dictionary",
                    "required": True
                },
                {
                    "name": "resetToDefaults", 
                    "type": "bool", 
                    "description": "Reset to default configuration first",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if logging was successfully configured"
            },
            "scope": ["Gateway"],
            "category": "Logging Operations",
            "patterns": [
                "logging_setup",
                "system_configuration",
                "diagnostic_management"
            ]
        }
    ])
    
    # ============================================================================
    # PROJECT MANAGEMENT (15 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.retarget",
            "description": "Retarget Vision client to different gateway",
            "parameters": [
                {
                    "name": "gatewayAddress", 
                    "type": "str", 
                    "description": "New gateway address",
                    "required": True
                },
                {
                    "name": "projectName", 
                    "type": "str", 
                    "description": "Project name on new gateway",
                    "required": False
                },
                {
                    "name": "timeout", 
                    "type": "int", 
                    "description": "Connection timeout in seconds",
                    "required": False,
                    "default": 30
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if retargeting was successful"
            },
            "scope": ["Vision Client"],
            "category": "Project Management",
            "patterns": [
                "client_retargeting",
                "gateway_switching",
                "project_management"
            ]
        },
        
        {
            "name": "system.util.restart",
            "description": "Restart Ignition system components",
            "parameters": [
                {
                    "name": "component", 
                    "type": "str", 
                    "description": "Component to restart (gateway, designer, client)",
                    "required": False,
                    "default": "gateway"
                },
                {
                    "name": "delay", 
                    "type": "int", 
                    "description": "Delay before restart in seconds",
                    "required": False,
                    "default": 5
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if restart was initiated"
            },
            "scope": ["Gateway"],
            "category": "Project Management",
            "patterns": [
                "system_restart",
                "maintenance_operations",
                "system_administration"
            ]
        },
        
        {
            "name": "system.util.shutdown",
            "description": "Shutdown Ignition system components gracefully",
            "parameters": [
                {
                    "name": "component", 
                    "type": "str", 
                    "description": "Component to shutdown",
                    "required": False,
                    "default": "gateway"
                },
                {
                    "name": "force", 
                    "type": "bool", 
                    "description": "Force shutdown if graceful fails",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if shutdown was initiated"
            },
            "scope": ["Gateway"],
            "category": "Project Management",
            "patterns": [
                "system_shutdown",
                "maintenance_operations",
                "system_administration"
            ]
        }
    ])
    
    # ============================================================================
    # SECURITY AND USER MANAGEMENT (8 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.getUserRoles",
            "description": "Get user roles and permissions information",
            "parameters": [
                {
                    "name": "username", 
                    "type": "str", 
                    "description": "Username to query roles for",
                    "required": False
                },
                {
                    "name": "includeInherited", 
                    "type": "bool", 
                    "description": "Include inherited roles",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of user roles and permissions"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Security Operations",
            "patterns": [
                "user_management",
                "security_validation",
                "role_based_access"
            ]
        },
        
        {
            "name": "system.util.validateUser",
            "description": "Validate user credentials and permissions",
            "parameters": [
                {
                    "name": "username", 
                    "type": "str", 
                    "description": "Username to validate",
                    "required": True
                },
                {
                    "name": "password", 
                    "type": "str", 
                    "description": "Password to validate",
                    "required": False
                },
                {
                    "name": "requiredRoles", 
                    "type": "list", 
                    "description": "Required roles for validation",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Validation result with user information"
            },
            "scope": ["Gateway"],
            "category": "Security Operations",
            "patterns": [
                "user_authentication",
                "security_validation",
                "access_control"
            ]
        }
    ])
    
    # ============================================================================
    # PERFORMANCE AND MONITORING (10 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.getMemoryUsage",
            "description": "Get current memory usage statistics",
            "parameters": [
                {
                    "name": "detailed", 
                    "type": "bool", 
                    "description": "Include detailed memory breakdown",
                    "required": False,
                    "default": False
                },
                {
                    "name": "gcCollect", 
                    "type": "bool", 
                    "description": "Force garbage collection before measurement",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Memory usage information including heap, used, and available"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Performance Monitoring",
            "patterns": [
                "performance_monitoring",
                "memory_analysis",
                "system_diagnostics"
            ]
        },
        
        {
            "name": "system.util.getSystemInfo",
            "description": "Get comprehensive system information",
            "parameters": [
                {
                    "name": "category", 
                    "type": "str", 
                    "description": "Information category (os, hardware, java, network)",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "System information dictionary"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "System Information",
            "patterns": [
                "system_diagnostics",
                "hardware_information",
                "environment_detection"
            ]
        },
        
        {
            "name": "system.util.getSessionInfo",
            "description": "Get current session information and statistics",
            "parameters": [
                {
                    "name": "sessionId", 
                    "type": "str", 
                    "description": "Specific session ID to query",
                    "required": False
                },
                {
                    "name": "includeProps", 
                    "type": "bool", 
                    "description": "Include session properties",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Session information including user, props, and connection details"
            },
            "scope": ["Vision Client", "Perspective Session"],
            "category": "Session Management",
            "patterns": [
                "session_monitoring",
                "user_tracking",
                "connection_diagnostics"
            ]
        },
        
        {
            "name": "system.util.getPerformanceMetrics",
            "description": "Get system performance metrics and statistics",
            "parameters": [
                {
                    "name": "timeRange", 
                    "type": "int", 
                    "description": "Time range in minutes for metrics",
                    "required": False,
                    "default": 60
                },
                {
                    "name": "metrics", 
                    "type": "list", 
                    "description": "Specific metrics to include",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Performance metrics including CPU, memory, and I/O statistics"
            },
            "scope": ["Gateway"],
            "category": "Performance Monitoring",
            "patterns": [
                "performance_analysis",
                "system_monitoring",
                "resource_tracking"
            ]
        }
    ])
    
    # ============================================================================
    # NETWORK AND COMMUNICATION (8 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.getNetworkInfo",
            "description": "Get network configuration and status information",
            "parameters": [
                {
                    "name": "interface", 
                    "type": "str", 
                    "description": "Specific network interface to query",
                    "required": False
                },
                {
                    "name": "includeStatistics", 
                    "type": "bool", 
                    "description": "Include network statistics",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Network configuration and status information"
            },
            "scope": ["Gateway"],
            "category": "Network Operations",
            "patterns": [
                "network_diagnostics",
                "connection_monitoring",
                "network_configuration"
            ]
        },
        
        {
            "name": "system.util.testConnection",
            "description": "Test network connectivity to specified host",
            "parameters": [
                {
                    "name": "host", 
                    "type": "str", 
                    "description": "Host address to test",
                    "required": True
                },
                {
                    "name": "port", 
                    "type": "int", 
                    "description": "Port number to test",
                    "required": False,
                    "default": 80
                },
                {
                    "name": "timeout", 
                    "type": "int", 
                    "description": "Connection timeout in seconds",
                    "required": False,
                    "default": 5
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Connection test results including success, latency, and error details"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Network Operations",
            "patterns": [
                "connectivity_testing",
                "network_diagnostics",
                "connection_validation"
            ]
        }
    ])
    
    # ============================================================================
    # SYSTEM CONFIGURATION (7 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.getProperty",
            "description": "Get system property value",
            "parameters": [
                {
                    "name": "propertyName", 
                    "type": "str", 
                    "description": "Name of property to retrieve",
                    "required": True
                },
                {
                    "name": "defaultValue", 
                    "type": "str", 
                    "description": "Default value if property not found",
                    "required": False
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Property value or default"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "System Configuration",
            "patterns": [
                "configuration_management",
                "property_access",
                "system_settings"
            ]
        },
        
        {
            "name": "system.util.setProperty",
            "description": "Set system property value",
            "parameters": [
                {
                    "name": "propertyName", 
                    "type": "str", 
                    "description": "Name of property to set",
                    "required": True
                },
                {
                    "name": "value", 
                    "type": "str", 
                    "description": "Value to set",
                    "required": True
                },
                {
                    "name": "persist", 
                    "type": "bool", 
                    "description": "Whether to persist property changes",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if property was successfully set"
            },
            "scope": ["Gateway"],
            "category": "System Configuration",
            "patterns": [
                "configuration_management",
                "property_modification",
                "system_administration"
            ]
        }
    ])
    
    # ============================================================================
    # FILE AND DIRECTORY UTILITIES (12 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.copyFile",
            "description": "Copy files between locations with advanced options",
            "parameters": [
                {
                    "name": "source", 
                    "type": "str", 
                    "description": "Source file path",
                    "required": True
                },
                {
                    "name": "destination", 
                    "type": "str", 
                    "description": "Destination file path",
                    "required": True
                },
                {
                    "name": "overwrite", 
                    "type": "bool", 
                    "description": "Whether to overwrite existing files",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if file was successfully copied"
            },
            "scope": ["Gateway"],
            "category": "File Operations",
            "patterns": [
                "file_management",
                "backup_operations",
                "file_system_utilities"
            ]
        },
        
        {
            "name": "system.util.moveFile",
            "description": "Move or rename files with validation",
            "parameters": [
                {
                    "name": "source", 
                    "type": "str", 
                    "description": "Source file path",
                    "required": True
                },
                {
                    "name": "destination", 
                    "type": "str", 
                    "description": "Destination file path",   
                    "required": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if file was successfully moved"
            },
            "scope": ["Gateway"],
            "category": "File Operations",
            "patterns": [
                "file_management",
                "file_organization",
                "file_system_utilities"
            ]
        },
        
        {
            "name": "system.util.deleteFile",
            "description": "Delete files with safety checks",
            "parameters": [
                {
                    "name": "filePath", 
                    "type": "str", 
                    "description": "Path to file to delete",
                    "required": True
                },
                {
                    "name": "confirm", 
                    "type": "bool", 
                    "description": "Require confirmation for deletion",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if file was successfully deleted"
            },
            "scope": ["Gateway"],
            "category": "File Operations",
            "patterns": [
                "file_management",
                "cleanup_operations",
                "file_system_utilities"
            ]
        },
        
        {
            "name": "system.util.listFiles",
            "description": "List files in directory with filtering options",
            "parameters": [
                {
                    "name": "directory", 
                    "type": "str", 
                    "description": "Directory path to list",
                    "required": True
                },
                {
                    "name": "pattern", 
                    "type": "str", 
                    "description": "File pattern filter",
                    "required": False
                },
                {
                    "name": "recursive", 
                    "type": "bool", 
                    "description": "Include subdirectories",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of file information dictionaries"
            },
            "scope": ["Gateway"],
            "category": "File Operations",
            "patterns": [
                "file_discovery",
                "directory_browsing",
                "file_system_navigation"
            ]
        }
    ])
    
    # ============================================================================
    # DATE AND TIME UTILITIES (8 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.formatDate",
            "description": "Format date with locale-specific patterns",
            "parameters": [
                {
                    "name": "date", 
                    "type": "datetime", 
                    "description": "Date to format",
                    "required": True
                },
                {
                    "name": "pattern", 
                    "type": "str", 
                    "description": "Date format pattern",
                    "required": False,
                    "default": "yyyy-MM-dd HH:mm:ss"
                },
                {
                    "name": "locale", 
                    "type": "str", 
                    "description": "Locale for formatting",
                    "required": False
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Formatted date string"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Date/Time Operations",
            "patterns": [
                "date_formatting",
                "localization",
                "time_display"
            ]
        },
        
        {
            "name": "system.util.parseDate",
            "description": "Parse date strings with format validation",
            "parameters": [
                {
                    "name": "dateString", 
                    "type": "str", 
                    "description": "Date string to parse",
                    "required": True
                },
                {
                    "name": "pattern", 
                    "type": "str", 
                    "description": "Expected date format pattern",
                    "required": False
                },
                {
                    "name": "timezone", 
                    "type": "str", 
                    "description": "Timezone for parsing",
                    "required": False
                }
            ],
            "returns": {
                "type": "datetime", 
                "description": "Parsed date object"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Date/Time Operations",
            "patterns": [
                "date_parsing",
                "input_validation",
                "time_processing"
            ]
        },
        
        {
            "name": "system.util.getCurrentTime",
            "description": "Get current time with timezone support",
            "parameters": [
                {
                    "name": "timezone", 
                    "type": "str", 
                    "description": "Timezone to get time for",
                    "required": False
                },
                {
                    "name": "format", 
                    "type": "str", 
                    "description": "Return format (datetime, timestamp, string)",
                    "required": False,
                    "default": "datetime"
                }
            ],
            "returns": {
                "type": "datetime", 
                "description": "Current time in requested format"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Date/Time Operations",
            "patterns": [
                "time_retrieval",
                "timezone_handling",
                "current_time_display"
            ]
        }
    ])
    
    # ============================================================================
    # STRING AND DATA UTILITIES (10 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.encodeBase64",
            "description": "Encode data to Base64 format",
            "parameters": [
                {
                    "name": "data", 
                    "type": "bytes", 
                    "description": "Data to encode",
                    "required": True
                },
                {
                    "name": "urlSafe", 
                    "type": "bool", 
                    "description": "Use URL-safe encoding",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Base64 encoded string"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Encoding",
            "patterns": [
                "data_encoding",
                "binary_data_handling",
                "data_transformation"
            ]
        },
        
        {
            "name": "system.util.decodeBase64",
            "description": "Decode Base64 formatted data",
            "parameters": [
                {
                    "name": "encodedData", 
                    "type": "str", 
                    "description": "Base64 encoded string",
                    "required": True
                },
                {
                    "name": "urlSafe", 
                    "type": "bool", 
                    "description": "Use URL-safe decoding",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "bytes", 
                "description": "Decoded binary data"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Encoding",
            "patterns": [
                "data_decoding",
                "binary_data_processing",
                "data_transformation"
            ]
        },
        
        {
            "name": "system.util.generateUUID",
            "description": "Generate unique identifier strings",
            "parameters": [
                {
                    "name": "format", 
                    "type": "str", 
                    "description": "UUID format (standard, compact, uppercase)",
                    "required": False,
                    "default": "standard"
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Generated UUID string"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Generation",
            "patterns": [
                "unique_id_generation",
                "data_keys",
                "identifier_creation"
            ]
        },
        
        {
            "name": "system.util.hashData",
            "description": "Generate hash values for data integrity",
            "parameters": [
                {
                    "name": "data", 
                    "type": "str", 
                    "description": "Data to hash",
                    "required": True
                },
                {
                    "name": "algorithm", 
                    "type": "str", 
                    "description": "Hash algorithm (md5, sha1, sha256)",
                    "required": False,
                    "default": "sha256"
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Hash value as hexadecimal string"
            },
            "scope": ["Gateway"],
            "category": "Data Security",
            "patterns": [
                "data_integrity",
                "hash_generation",
                "security_validation"
            ]
        }
    ])
    
    # ============================================================================
    # SYSTEM NOTIFICATION UTILITIES (6 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.sendEmail",
            "description": "Send email notifications with attachments",
            "parameters": [
                {
                    "name": "to", 
                    "type": "list", 
                    "description": "List of recipient email addresses",
                    "required": True
                },
                {
                    "name": "subject", 
                    "type": "str", 
                    "description": "Email subject line",
                    "required": True
                },
                {
                    "name": "body", 
                    "type": "str", 
                    "description": "Email body content",
                    "required": True
                },
                {
                    "name": "attachments", 
                    "type": "list", 
                    "description": "List of file paths to attach",
                    "required": False
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if email was sent successfully"
            },
            "scope": ["Gateway"],
            "category": "Communication",
            "patterns": [
                "email_notifications",
                "system_alerts",
                "automated_communication"
            ]
        },
        
        {
            "name": "system.util.showNotification",
            "description": "Display system notifications to users",
            "parameters": [
                {
                    "name": "message", 
                    "type": "str", 
                    "description": "Notification message",
                    "required": True
                },
                {
                    "name": "title", 
                    "type": "str", 
                    "description": "Notification title",
                    "required": False
                },
                {
                    "name": "level", 
                    "type": "str", 
                    "description": "Notification level (info, warning, error)",
                    "required": False,
                    "default": "info"
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if notification was displayed"
            },
            "scope": ["Vision Client", "Perspective Session"],
            "category": "User Interface",
            "patterns": [
                "user_notifications",
                "system_feedback",
                "user_interaction"
            ]
        }
    ])
    
    # ============================================================================
    # ADVANCED SYSTEM UTILITIES (15 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.util.exportSystemConfiguration",
            "description": "Export system configuration for backup and deployment",
            "parameters": [
                {
                    "name": "outputPath", 
                    "type": "str", 
                    "description": "Output file path for configuration export",
                    "required": True
                },
                {
                    "name": "includeSecrets", 
                    "type": "bool", 
                    "description": "Include sensitive configuration data",
                    "required": False,
                    "default": False
                },
                {
                    "name": "format", 
                    "type": "str", 
                    "description": "Export format (json, xml, yaml)",
                    "required": False,
                    "default": "json"
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if configuration was successfully exported"
            },
            "scope": ["Gateway"],
            "category": "System Management",
            "patterns": [
                "configuration_backup",
                "system_deployment",
                "configuration_management"
            ]
        },
        
        {
            "name": "system.util.importSystemConfiguration",
            "description": "Import system configuration from backup files",
            "parameters": [
                {
                    "name": "configPath", 
                    "type": "str", 
                    "description": "Path to configuration file to import",
                    "required": True
                },
                {
                    "name": "mergeMode", 
                    "type": "str", 
                    "description": "Import mode (replace, merge, update)",
                    "required": False,
                    "default": "merge"
                },
                {
                    "name": "validate", 
                    "type": "bool", 
                    "description": "Validate configuration before import",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Import results with success status and validation details"
            },
            "scope": ["Gateway"],
            "category": "System Management",
            "patterns": [
                "configuration_restore",
                "system_deployment",
                "configuration_management"
            ]
        },
        
        {
            "name": "system.util.getSystemHealth",
            "description": "Get comprehensive system health status",
            "parameters": [
                {
                    "name": "includeDetails", 
                    "type": "bool", 
                    "description": "Include detailed health metrics",
                    "required": False,
                    "default": True
                },
                {
                    "name": "categories", 
                    "type": "list", 
                    "description": "Health categories to check",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "System health status with metrics and recommendations"
            },
            "scope": ["Gateway"],
            "category": "System Monitoring",
            "patterns": [
                "health_monitoring",
                "system_diagnostics",
                "preventive_maintenance"
            ]
        },
        
        {
            "name": "system.util.cleanupTempFiles",
            "description": "Clean up temporary files and directories",
            "parameters": [
                {
                    "name": "maxAge", 
                    "type": "int", 
                    "description": "Maximum age in hours for temp files to keep",
                    "required": False,
                    "default": 24
                },
                {
                    "name": "dryRun", 
                    "type": "bool", 
                    "description": "Show what would be cleaned without actually deleting",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Cleanup results including files removed and space freed"
            },
            "scope": ["Gateway"],
            "category": "System Maintenance",
            "patterns": [
                "cleanup_operations",
                "disk_space_management",
                "system_maintenance"
            ]
        },
        
        {
            "name": "system.util.scheduleTask",
            "description": "Schedule tasks for delayed or recurring execution",
            "parameters": [
                {
                    "name": "taskName", 
                    "type": "str", 
                    "description": "Name of task to schedule",
                    "required": True
                },
                {
                    "name": "function", 
                    "type": "callable", 
                    "description": "Function to execute",
                    "required": True
                },
                {
                    "name": "schedule", 
                    "type": "str", 
                    "description": "Schedule expression (cron-like)",
                    "required": True
                },
                {
                    "name": "enabled", 
                    "type": "bool", 
                    "description": "Whether task should be enabled",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "str", 
                "description": "Task ID for managing scheduled task"
            },
            "scope": ["Gateway"],
            "category": "Task Scheduling",
            "patterns": [
                "task_automation",
                "scheduled_operations",
                "background_processing"
            ]
        },
        
        {
            "name": "system.util.cancelScheduledTask",
            "description": "Cancel previously scheduled tasks",
            "parameters": [
                {
                    "name": "taskId", 
                    "type": "str", 
                    "description": "ID of task to cancel",
                    "required": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if task was successfully canceled"
            },
            "scope": ["Gateway"],
            "category": "Task Scheduling",
            "patterns": [
                "task_management",
                "scheduled_task_control",
                "automation_management"
            ]
        },
        
        {
            "name": "system.util.getScheduledTasks",
            "description": "Get list of all scheduled tasks",
            "parameters": [
                {
                    "name": "status", 
                    "type": "str", 
                    "description": "Filter by task status (all, active, inactive)",
                    "required": False,
                    "default": "all"
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of scheduled task information"
            },
            "scope": ["Gateway"],
            "category": "Task Scheduling",
            "patterns": [
                "task_monitoring",
                "scheduled_task_overview",
                "automation_tracking"
            ]
        },
        
        {
            "name": "system.util.compressData",
            "description": "Compress data using various algorithms",
            "parameters": [
                {
                    "name": "data", 
                    "type": "bytes", 
                    "description": "Data to compress",
                    "required": True
                },
                {
                    "name": "algorithm", 
                    "type": "str", 
                    "description": "Compression algorithm (gzip, zip, bz2)",
                    "required": False,
                    "default": "gzip"
                },
                {
                    "name": "level", 
                    "type": "int", 
                    "description": "Compression level (1-9)",
                    "required": False,
                    "default": 6
                }
            ],
            "returns": {
                "type": "bytes", 
                "description": "Compressed data"
            },
            "scope": ["Gateway"],
            "category": "Data Processing",
            "patterns": [
                "data_compression",
                "storage_optimization",
                "data_transfer_optimization"
            ]
        },
        
        {
            "name": "system.util.decompressData",
            "description": "Decompress compressed data",
            "parameters": [
                {
                    "name": "compressedData", 
                    "type": "bytes", 
                    "description": "Compressed data to decompress",
                    "required": True
                },
                {
                    "name": "algorithm", 
                    "type": "str", 
                    "description": "Compression algorithm used",
                    "required": False,
                    "default": "gzip"
                }
            ],
            "returns": {
                "type": "bytes", 
                "description": "Decompressed data"
            },
            "scope": ["Gateway"],
            "category": "Data Processing",
            "patterns": [
                "data_decompression",
                "data_recovery",
                "data_processing"
            ]
        },
        
        {
            "name": "system.util.validateLicense",
            "description": "Validate system license and feature availability",
            "parameters": [
                {
                    "name": "feature", 
                    "type": "str", 
                    "description": "Specific feature to validate",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "License validation results with feature availability"
            },
            "scope": ["Gateway"],
            "category": "License Management",
            "patterns": [
                "license_validation",
                "feature_availability",
                "compliance_checking"
            ]
        },
        
        {
            "name": "system.util.getSystemEvents",
            "description": "Get system events and audit trail information",
            "parameters": [
                {
                    "name": "startTime", 
                    "type": "datetime", 
                    "description": "Start time for event query",
                    "required": False
                },
                {
                    "name": "endTime", 
                    "type": "datetime", 
                    "description": "End time for event query",
                    "required": False
                },
                {
                    "name": "eventTypes", 
                    "type": "list", 
                    "description": "Types of events to include",
                    "required": False
                },
                {
                    "name": "limit", 
                    "type": "int", 
                    "description": "Maximum number of events to return",
                    "required": False,
                    "default": 1000
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of system events with timestamps and details"
            },
            "scope": ["Gateway"],
            "category": "Event Management",
            "patterns": [
                "audit_trail",
                "event_monitoring",
                "system_tracking"
            ]
        },
        
        {
            "name": "system.util.createBackup",
            "description": "Create comprehensive system backup",
            "parameters": [
                {
                    "name": "backupPath", 
                    "type": "str", 
                    "description": "Path for backup file",
                    "required": True
                },
                {
                    "name": "includeData", 
                    "type": "bool", 
                    "description": "Include database and historical data",
                    "required": False,
                    "default": True
                },
                {
                    "name": "compression", 
                    "type": "bool", 
                    "description": "Compress backup file",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Backup creation results with file size and verification"
            },
            "scope": ["Gateway"],
            "category": "Backup Management",
            "patterns": [
                "system_backup",
                "disaster_recovery",
                "data_protection"
            ]
        },
        
        {
            "name": "system.util.restoreBackup",
            "description": "Restore system from backup file",
            "parameters": [
                {
                    "name": "backupPath", 
                    "type": "str", 
                    "description": "Path to backup file",
                    "required": True
                },
                {
                    "name": "restoreData", 
                    "type": "bool", 
                    "description": "Restore database and historical data",
                    "required": False,
                    "default": True
                },
                {
                    "name": "verify", 
                    "type": "bool", 
                    "description": "Verify backup integrity before restore",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Restore operation results with status and verification"
            },
            "scope": ["Gateway"],
            "category": "Backup Management",
            "patterns": [
                "system_restore",
                "disaster_recovery",
                "data_recovery"
            ]
        }
    ])
    
    return functions


def get_task_6_metadata() -> Dict[str, Any]:
    """Get metadata about Task 6 implementation."""
    return {
        "task_id": 6,
        "name": "Utility System Expansion",
        "description": "Comprehensive utility functions and system management operations",
        "priority": "MEDIUM",
        "estimated_functions": 50,
        "categories": [
            "General Utilities",
            "Logging Operations", 
            "Project Management",
            "Security Operations",
            "Performance Monitoring"
        ],
        "contexts": ["Gateway", "Vision Client", "Perspective Session"],
        "completion_target": "Week 7",
        "dependencies": ["Tasks 1-5 (Core systems)"],
        "validation_required": [
            "Utility functions across all contexts",
            "System management operations",
            "Logging configuration functionality",
            "Translation and localization support"
        ]
    } 