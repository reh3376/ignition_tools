"""General Utilities Module for Task 6.

Provides general utility functions including:
- Translation and internationalization support
- Locale configuration and management
- Timezone operations
- System information and diagnostics

Functions: 15 functions
Contexts: Gateway, Vision Client, Perspective Session
"""

from typing import Any


def get_general_utilities_functions() -> list[dict[str, Any]]:
    """Get general utility functions.

    Returns:
        list[dict[str, Any]]: list of general utility function definitions
    """
    return [
        {
            "name": "system.util.modifyTranslation",
            "description": "Modify translation strings for internationalization support",
            "parameters": [
                {
                    "name": "key",
                    "type": "str",
                    "description": "Translation key to modify",
                    "required": True,
                },
                {
                    "name": "locale",
                    "type": "str",
                    "description": "Locale code (e.g., 'en_US', 'es_ES')",
                    "required": True,
                },
                {
                    "name": "value",
                    "type": "str",
                    "description": "New translation value",
                    "required": True,
                },
                {
                    "name": "persist",
                    "type": "bool",
                    "description": "Whether to persist changes to disk",
                    "required": False,
                    "default": True,
                },
            ],
            "returns": {
                "type": "bool",
                "description": "True if translation was successfully modified",
            },
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "internationalization",
                "localization_management",
                "translation_updates",
            ],
        },
        {
            "name": "system.util.translate",
            "description": "Translate text using current locale settings",
            "parameters": [
                {
                    "name": "key",
                    "type": "str",
                    "description": "Translation key to translate",
                    "required": True,
                },
                {
                    "name": "locale",
                    "type": "str",
                    "description": "Optional locale override",
                    "required": False,
                },
                {
                    "name": "defaultValue",
                    "type": "str",
                    "description": "Default value if translation not found",
                    "required": False,
                },
                {
                    "name": "params",
                    "type": "dict",
                    "description": "Parameters for parameterized translations",
                    "required": False,
                },
            ],
            "returns": {
                "type": "str",
                "description": "Translated text or default value",
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "internationalization",
                "localization_display",
                "multi_language_support",
            ],
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
                    "default": "system",
                }
            ],
            "returns": {
                "type": "dict",
                "description": "Locale information including language, country, and variant",
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "locale_detection",
                "system_configuration",
                "internationalization_info",
            ],
        },
        {
            "name": "system.util.setLocale",
            "description": "set system locale configuration",
            "parameters": [
                {
                    "name": "locale",
                    "type": "str",
                    "description": "Locale string (e.g., 'en_US', 'fr_FR')",
                    "required": True,
                },
                {
                    "name": "context",
                    "type": "str",
                    "description": "Context to set locale for",
                    "required": False,
                    "default": "system",
                },
                {
                    "name": "persist",
                    "type": "bool",
                    "description": "Whether to persist locale changes",
                    "required": False,
                    "default": True,
                },
            ],
            "returns": {
                "type": "bool",
                "description": "True if locale was successfully set",
            },
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "locale_configuration",
                "system_settings",
                "internationalization_setup",
            ],
        },
        {
            "name": "system.util.getTimezone",
            "description": "Get current system timezone configuration",
            "parameters": [
                {
                    "name": "format",
                    "type": "str",
                    "description": "Return format: 'id', 'display', 'offset'",
                    "required": False,
                    "default": "id",
                }
            ],
            "returns": {
                "type": "str",
                "description": "Timezone information in requested format",
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "timezone_detection",
                "system_time_management",
                "time_configuration",
            ],
        },
        {
            "name": "system.util.setTimezone",
            "description": "set system timezone configuration",
            "parameters": [
                {
                    "name": "timezone",
                    "type": "str",
                    "description": "Timezone ID (e.g., 'America/New_York')",
                    "required": True,
                },
                {
                    "name": "persist",
                    "type": "bool",
                    "description": "Whether to persist timezone changes",
                    "required": False,
                    "default": True,
                },
            ],
            "returns": {
                "type": "bool",
                "description": "True if timezone was successfully set",
            },
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "timezone_configuration",
                "system_time_setup",
                "time_zone_management",
            ],
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
                    "default": True,
                },
                {
                    "name": "format",
                    "type": "str",
                    "description": "Output format: 'text', 'json', 'xml'",
                    "required": False,
                    "default": "text",
                },
            ],
            "returns": {"type": "str", "description": "Thread dump information"},
            "scope": ["Gateway"],
            "category": "Utility Operations",
            "patterns": [
                "system_diagnostics",
                "performance_troubleshooting",
                "thread_analysis",
            ],
        },
        {
            "name": "system.util.version",
            "description": "Get Ignition system version information",
            "parameters": [
                {
                    "name": "component",
                    "type": "str",
                    "description": "Specific component version to get",
                    "required": False,
                },
                {
                    "name": "detailed",
                    "type": "bool",
                    "description": "Include detailed build information",
                    "required": False,
                    "default": False,
                },
            ],
            "returns": {
                "type": "dict",
                "description": "Version information including build, edition, and modules",
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Utility Operations",
            "patterns": [
                "version_checking",
                "system_information",
                "compatibility_verification",
            ],
        },
    ]
