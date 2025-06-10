"""
Task 7: Alarm System Expansion
Enhanced alarm management and monitoring functions for Ignition SCADA systems.

This module provides comprehensive alarm operations including:
- Alarm Journal Operations
- Alarm Status Management  
- Alarm Pipeline Operations
- Alarm Event Operations
- Alarm Configuration Management

Total Functions: 29 functions
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2)
"""

from typing import List, Dict, Any


def get_alarm_system_functions() -> List[Dict[str, Any]]:
    """
    Get comprehensive alarm system functions for Task 7.
    
    Returns:
        List[Dict[str, Any]]: List of alarm function definitions
    """
    
    functions = []
    
    # ============================================================================
    # ALARM JOURNAL OPERATIONS (6 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.alarm.queryJournal",
            "description": "Query the alarm journal with advanced filtering and sorting options",
            "parameters": [
                {
                    "name": "startDate", 
                    "type": "datetime", 
                    "description": "Start date for journal query",
                    "required": True
                },
                {
                    "name": "endDate", 
                    "type": "datetime", 
                    "description": "End date for journal query",
                    "required": True
                },
                {
                    "name": "journalName", 
                    "type": "str", 
                    "description": "Name of alarm journal to query",
                    "required": False,
                    "default": "Default"
                },
                {
                    "name": "priority", 
                    "type": "str", 
                    "description": "Filter by alarm priority level",
                    "required": False
                },
                {
                    "name": "state", 
                    "type": "list", 
                    "description": "List of alarm states to include",
                    "required": False
                },
                {
                    "name": "path", 
                    "type": "list", 
                    "description": "List of alarm paths to filter",
                    "required": False
                },
                {
                    "name": "source", 
                    "type": "list", 
                    "description": "List of alarm sources to include",
                    "required": False
                },
                {
                    "name": "displaypath", 
                    "type": "list", 
                    "description": "List of display paths to filter",
                    "required": False
                },
                {
                    "name": "all_properties", 
                    "type": "list", 
                    "description": "Additional properties to include in results",
                    "required": False
                },
                {
                    "name": "any_properties", 
                    "type": "list", 
                    "description": "Properties where any match is sufficient",
                    "required": False
                },
                {
                    "name": "defined", 
                    "type": "list", 
                    "description": "Properties that must be defined",
                    "required": False
                },
                {
                    "name": "orderBy", 
                    "type": "str", 
                    "description": "Field to order results by",
                    "required": False,
                    "default": "eventTime"
                },
                {
                    "name": "orderDirection", 
                    "type": "str", 
                    "description": "Sort direction (ASC/DESC)",
                    "required": False,
                    "default": "DESC"
                }
            ],
            "returns": {
                "type": "Dataset", 
                "description": "Alarm journal entries matching the query criteria"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_journal_basic_query",
                "alarm_journal_filtered_query", 
                "alarm_journal_advanced_query",
                "alarm_historical_analysis"
            ]
        },
        
        {
            "name": "system.alarm.addJournalEntry",
            "description": "Add a custom entry to the alarm journal for documentation and tracking",
            "parameters": [
                {
                    "name": "alarmPath", 
                    "type": "str", 
                    "description": "Path of the alarm to add journal entry for",
                    "required": True
                },
                {
                    "name": "eventType", 
                    "type": "str", 
                    "description": "Type of journal entry event",
                    "required": True
                },
                {
                    "name": "user", 
                    "type": "str", 
                    "description": "Username adding the entry",
                    "required": False
                },
                {
                    "name": "source", 
                    "type": "str", 
                    "description": "Source of the journal entry",
                    "required": False
                },
                {
                    "name": "timestamp", 
                    "type": "datetime", 
                    "description": "Timestamp for the entry",
                    "required": False
                },
                {
                    "name": "message", 
                    "type": "str", 
                    "description": "Custom message for the journal entry",
                    "required": False
                },
                {
                    "name": "priority", 
                    "type": "int", 
                    "description": "Priority level for the entry",
                    "required": False
                },
                {
                    "name": "properties", 
                    "type": "dict", 
                    "description": "Additional properties for the entry",
                    "required": False
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if journal entry was successfully added"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_journal_documentation",
                "alarm_manual_entry",
                "alarm_event_logging",
                "alarm_audit_trail"
            ]
        },
        
        {
            "name": "system.alarm.queryJournalCount",
            "description": "Get count of alarm journal entries matching specified criteria",
            "parameters": [
                {
                    "name": "startDate", 
                    "type": "datetime", 
                    "description": "Start date for count query",
                    "required": True
                },
                {
                    "name": "endDate", 
                    "type": "datetime", 
                    "description": "End date for count query",
                    "required": True
                },
                {
                    "name": "journalName", 
                    "type": "str", 
                    "description": "Name of alarm journal",
                    "required": False,
                    "default": "Default"
                },
                {
                    "name": "priority", 
                    "type": "str", 
                    "description": "Filter by alarm priority level",
                    "required": False
                },
                {
                    "name": "state", 
                    "type": "list", 
                    "description": "List of alarm states to count",
                    "required": False
                },
                {
                    "name": "path", 
                    "type": "list", 
                    "description": "List of alarm paths to include",
                    "required": False
                }
            ],
            "returns": {
                "type": "int", 
                "description": "Number of journal entries matching criteria"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_statistics",
                "alarm_reporting_metrics",
                "alarm_count_analysis",
                "alarm_performance_monitoring"
            ]
        },
        
        {
            "name": "system.alarm.getJournalNames",
            "description": "Retrieve list of available alarm journal names in the system",
            "parameters": [],
            "returns": {
                "type": "list", 
                "description": "List of alarm journal names"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_journal_discovery",
                "alarm_system_inspection",
                "alarm_configuration_audit"
            ]
        },
        
        {
            "name": "system.alarm.purgeJournal",
            "description": "Remove old entries from alarm journal to manage database size",
            "parameters": [
                {
                    "name": "journalName", 
                    "type": "str", 
                    "description": "Name of journal to purge",
                    "required": True
                },
                {
                    "name": "beforeDate", 
                    "type": "datetime", 
                    "description": "Remove entries before this date",
                    "required": True
                },
                {
                    "name": "priority", 
                    "type": "str", 
                    "description": "Only purge entries of this priority",
                    "required": False
                },
                {
                    "name": "dryRun", 
                    "type": "bool", 
                    "description": "Preview purge without actually deleting",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "int", 
                "description": "Number of entries that were/would be purged"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_journal_maintenance",
                "alarm_database_cleanup",
                "alarm_storage_management"
            ]
        },
        
        {
            "name": "system.alarm.exportJournal",
            "description": "Export alarm journal data to external formats for reporting and analysis",
            "parameters": [
                {
                    "name": "startDate", 
                    "type": "datetime", 
                    "description": "Start date for export",
                    "required": True
                },
                {
                    "name": "endDate", 
                    "type": "datetime", 
                    "description": "End date for export",
                    "required": True
                },
                {
                    "name": "filePath", 
                    "type": "str", 
                    "description": "Output file path for export",
                    "required": True
                },
                {
                    "name": "format", 
                    "type": "str", 
                    "description": "Export format (CSV, XML, JSON)",
                    "required": False,
                    "default": "CSV"
                },
                {
                    "name": "journalName", 
                    "type": "str", 
                    "description": "Name of journal to export",
                    "required": False,
                    "default": "Default"
                },
                {
                    "name": "includeProperties", 
                    "type": "bool", 
                    "description": "Include extended properties in export",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if export completed successfully"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_data_export",
                "alarm_reporting",
                "alarm_compliance_documentation",
                "alarm_analysis_preparation"
            ]
        }
    ])
    
    # ============================================================================
    # ALARM STATUS MANAGEMENT (8 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.alarm.queryStatus",
            "description": "Query current alarm status with advanced filtering and real-time information",
            "parameters": [
                {
                    "name": "priority", 
                    "type": "list", 
                    "description": "List of priorities to include",
                    "required": False
                },
                {
                    "name": "state", 
                    "type": "list", 
                    "description": "List of alarm states to query",
                    "required": False
                },
                {
                    "name": "path", 
                    "type": "list", 
                    "description": "List of alarm paths to include",
                    "required": False
                },
                {
                    "name": "source", 
                    "type": "list", 
                    "description": "List of alarm sources",
                    "required": False
                },
                {
                    "name": "displaypath", 
                    "type": "list", 
                    "description": "List of display paths to filter",
                    "required": False
                },
                {
                    "name": "all_properties", 
                    "type": "list", 
                    "description": "Properties that must all match",
                    "required": False
                },
                {
                    "name": "any_properties", 
                    "type": "list", 
                    "description": "Properties where any match is sufficient",
                    "required": False
                },
                {
                    "name": "defined", 
                    "type": "list", 
                    "description": "Properties that must be defined",
                    "required": False
                },
                {
                    "name": "includeShelved", 
                    "type": "bool", 
                    "description": "Include shelved alarms in results",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "Dataset", 
                "description": "Current alarm status information"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_status_monitoring",
                "alarm_real_time_query",
                "alarm_dashboard_display",
                "alarm_operator_interface"
            ]
        },
        
        {
            "name": "system.alarm.acknowledge",
            "description": "Acknowledge one or more active alarms to confirm operator awareness",
            "parameters": [
                {
                    "name": "alarmIds", 
                    "type": "list", 
                    "description": "List of alarm IDs to acknowledge",
                    "required": True
                },
                {
                    "name": "acknowledgeNote", 
                    "type": "str", 
                    "description": "Note explaining the acknowledgment",
                    "required": False
                },
                {
                    "name": "username", 
                    "type": "str", 
                    "description": "Username performing acknowledgment",
                    "required": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of successfully acknowledged alarm IDs"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_acknowledgment",
                "alarm_operator_response",
                "alarm_manual_handling",
                "alarm_workflow_completion"
            ]
        },
        
        {
            "name": "system.alarm.cancel",
            "description": "Cancel active alarms that are no longer relevant or were triggered in error",
            "parameters": [
                {
                    "name": "alarmIds", 
                    "type": "list", 
                    "description": "List of alarm IDs to cancel",
                    "required": True
                },
                {
                    "name": "cancelNote", 
                    "type": "str", 
                    "description": "Reason for canceling the alarms",
                    "required": False
                },
                {
                    "name": "username", 
                    "type": "str", 
                    "description": "Username performing cancellation",
                    "required": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of successfully canceled alarm IDs"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_cancellation",
                "alarm_error_correction",
                "alarm_manual_clearing",
                "alarm_false_positive_handling"
            ]
        },
        
        {
            "name": "system.alarm.shelve",
            "description": "Temporarily shelve alarms to suppress notifications while maintaining monitoring",
            "parameters": [
                {
                    "name": "alarmPaths", 
                    "type": "list", 
                    "description": "List of alarm paths to shelve",
                    "required": True
                },
                {
                    "name": "timeoutSeconds", 
                    "type": "int", 
                    "description": "Shelve timeout in seconds",
                    "required": False
                },
                {
                    "name": "shelveNote", 
                    "type": "str", 
                    "description": "Reason for shelving",
                    "required": False
                },
                {
                    "name": "username", 
                    "type": "str", 
                    "description": "Username performing shelving",
                    "required": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of successfully shelved alarm paths"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_shelving",
                "alarm_temporary_suppression",
                "alarm_maintenance_mode",
                "alarm_notification_control"
            ]
        },
        
        {
            "name": "system.alarm.unshelve",
            "description": "Remove shelving from alarms to restore normal notification behavior",
            "parameters": [
                {
                    "name": "alarmPaths", 
                    "type": "list", 
                    "description": "List of alarm paths to unshelve",
                    "required": True
                },
                {
                    "name": "unshelveNote", 
                    "type": "str", 
                    "description": "Reason for unshelving",
                    "required": False
                },
                {
                    "name": "username", 
                    "type": "str", 
                    "description": "Username performing unshelving",
                    "required": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of successfully unshelved alarm paths"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_unshelving",
                "alarm_notification_restoration",
                "alarm_maintenance_completion",
                "alarm_monitoring_resumption"
            ]
        },
        
        {
            "name": "system.alarm.clearAlarm",
            "description": "Clear alarm conditions and reset alarm state to normal",
            "parameters": [
                {
                    "name": "alarmPath", 
                    "type": "str", 
                    "description": "Path of alarm to clear",
                    "required": True
                },
                {
                    "name": "clearNote", 
                    "type": "str", 
                    "description": "Note explaining alarm clearing",
                    "required": False
                },
                {
                    "name": "username", 
                    "type": "str", 
                    "description": "Username clearing the alarm",
                    "required": False
                },
                {
                    "name": "force", 
                    "type": "bool", 
                    "description": "Force clear even if condition persists",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if alarm was successfully cleared"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_clearing",
                "alarm_reset",
                "alarm_condition_resolution",
                "alarm_manual_override"
            ]
        },
        
        {
            "name": "system.alarm.createAlarm",
            "description": "Programmatically create alarm events for custom conditions and notifications",
            "parameters": [
                {
                    "name": "alarmPath", 
                    "type": "str", 
                    "description": "Path where alarm should be created",
                    "required": True
                },
                {
                    "name": "alarmState", 
                    "type": "str", 
                    "description": "Initial state of the alarm",
                    "required": True
                },
                {
                    "name": "message", 
                    "type": "str", 
                    "description": "Alarm message text",
                    "required": True
                },
                {
                    "name": "priority", 
                    "type": "str", 
                    "description": "Alarm priority level",
                    "required": False,
                    "default": "Medium"
                },
                {
                    "name": "timestamp", 
                    "type": "datetime", 
                    "description": "Alarm timestamp",
                    "required": False
                },
                {
                    "name": "source", 
                    "type": "str", 
                    "description": "Source that triggered the alarm",
                    "required": False
                },
                {
                    "name": "displayPath", 
                    "type": "str", 
                    "description": "Display path for the alarm",
                    "required": False
                },
                {
                    "name": "properties", 
                    "type": "dict", 
                    "description": "Additional alarm properties",
                    "required": False
                }
            ],
            "returns": {
                "type": "str", 
                "description": "ID of the created alarm"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_creation",
                "alarm_programmatic_generation",
                "alarm_custom_conditions",
                "alarm_script_triggered"
            ]
        },
        
        {
            "name": "system.alarm.getAlarmStates",
            "description": "Retrieve list of available alarm states in the system",
            "parameters": [],
            "returns": {
                "type": "list", 
                "description": "List of alarm state names"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_state_discovery",
                "alarm_configuration_inspection",
                "alarm_system_capabilities"
            ]
        }
    ])
    
    # ============================================================================
    # ALARM PIPELINE OPERATIONS (5 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.alarm.listPipelines",
            "description": "Get list of configured alarm notification pipelines",
            "parameters": [
                {
                    "name": "includeDisabled", 
                    "type": "bool", 
                    "description": "Include disabled pipelines in results",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of alarm pipeline names"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_pipeline_discovery",
                "alarm_notification_inspection",
                "alarm_system_configuration"
            ]
        },
        
        {
            "name": "system.alarm.getPipelineInfo",
            "description": "Get detailed information about a specific alarm notification pipeline",
            "parameters": [
                {
                    "name": "pipelineName", 
                    "type": "str", 
                    "description": "Name of pipeline to inspect",
                    "required": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Pipeline configuration and status information"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_pipeline_inspection",
                "alarm_notification_details",
                "alarm_configuration_audit"
            ]
        },
        
        {
            "name": "system.alarm.testPipeline",
            "description": "Test alarm notification pipeline to verify configuration and connectivity",
            "parameters": [
                {
                    "name": "pipelineName", 
                    "type": "str", 
                    "description": "Name of pipeline to test",
                    "required": True
                },
                {
                    "name": "testMessage", 
                    "type": "str", 
                    "description": "Test message to send",
                    "required": False,
                    "default": "Alarm Pipeline Test"
                },
                {
                    "name": "recipient", 
                    "type": "str", 
                    "description": "Specific recipient for test",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Test results including success status and details"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_pipeline_testing",
                "alarm_notification_verification",
                "alarm_system_diagnostics"
            ]
        },
        
        {
            "name": "system.alarm.setPipelineEnabled",
            "description": "Enable or disable an alarm notification pipeline",
            "parameters": [
                {
                    "name": "pipelineName", 
                    "type": "str", 
                    "description": "Name of pipeline to modify",
                    "required": True
                },
                {
                    "name": "enabled", 
                    "type": "bool", 
                    "description": "Enable or disable the pipeline",
                    "required": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if pipeline state was successfully changed"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_pipeline_control",
                "alarm_notification_management",
                "alarm_system_administration"
            ]
        },
        
        {
            "name": "system.alarm.executeNotification",
            "description": "Manually execute alarm notification through specified pipeline",
            "parameters": [
                {
                    "name": "pipelineName", 
                    "type": "str", 
                    "description": "Pipeline to use for notification",
                    "required": True
                },
                {
                    "name": "alarmEvent", 
                    "type": "dict", 
                    "description": "Alarm event data for notification",
                    "required": True
                },
                {
                    "name": "overrideRecipients", 
                    "type": "list", 
                    "description": "Override default recipients",
                    "required": False
                },
                {
                    "name": "priority", 
                    "type": "str", 
                    "description": "Notification priority override",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Notification execution results"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_manual_notification",
                "alarm_custom_messaging",
                "alarm_escalation_handling"
            ]
        }
    ])
    
    # ============================================================================
    # ALARM CONFIGURATION OPERATIONS (5 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.alarm.getDisplayPaths",
            "description": "Retrieve alarm display paths for navigation and organization",
            "parameters": [
                {
                    "name": "alarmPath", 
                    "type": "str", 
                    "description": "Alarm path to get display paths for",
                    "required": False
                },
                {
                    "name": "includeDisabled", 
                    "type": "bool", 
                    "description": "Include disabled alarms",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of alarm display paths"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_navigation",
                "alarm_organization",
                "alarm_hierarchy_inspection",
                "alarm_display_management"
            ]
        },
        
        {
            "name": "system.alarm.getAlarmConfiguration",
            "description": "Retrieve detailed configuration for specific alarm",
            "parameters": [
                {
                    "name": "alarmPath", 
                    "type": "str", 
                    "description": "Path of alarm to inspect",
                    "required": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Alarm configuration details"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_configuration_inspection",
                "alarm_setup_verification",
                "alarm_troubleshooting",
                "alarm_documentation"
            ]
        },
        
        {
            "name": "system.alarm.setAlarmEnabled",
            "description": "Enable or disable specific alarms for maintenance or testing",
            "parameters": [
                {
                    "name": "alarmPath", 
                    "type": "str", 
                    "description": "Path of alarm to modify",
                    "required": True
                },
                {
                    "name": "enabled", 
                    "type": "bool", 
                    "description": "Enable or disable the alarm",
                    "required": True
                },
                {
                    "name": "reason", 
                    "type": "str", 
                    "description": "Reason for enabling/disabling",
                    "required": False
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if alarm state was successfully changed"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_enable_disable",
                "alarm_maintenance_control",
                "alarm_testing_setup",
                "alarm_configuration_management"
            ]
        },
        
        {
            "name": "system.alarm.getAlarmSummary",
            "description": "Get summary statistics and counts for alarm system status",
            "parameters": [
                {
                    "name": "groupBy", 
                    "type": "str", 
                    "description": "Group summary by (priority, state, source)",
                    "required": False,
                    "default": "priority"
                },
                {
                    "name": "includeAcknowledged", 
                    "type": "bool", 
                    "description": "Include acknowledged alarms in summary",
                    "required": False,
                    "default": True
                },
                {
                    "name": "includeShelved", 
                    "type": "bool", 
                    "description": "Include shelved alarms in summary",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Alarm summary statistics and counts"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_dashboard_summary",
                "alarm_statistics_reporting",
                "alarm_kpi_monitoring",
                "alarm_overview_display"
            ]
        },
        
        {
            "name": "system.alarm.validateConfiguration",
            "description": "Validate alarm system configuration and identify potential issues",
            "parameters": [
                {
                    "name": "checkPipelines", 
                    "type": "bool", 
                    "description": "Validate notification pipelines",
                    "required": False,
                    "default": True
                },
                {
                    "name": "checkAlarmPaths", 
                    "type": "bool", 
                    "description": "Validate alarm path references",
                    "required": False,
                    "default": True
                },
                {
                    "name": "checkTagReferences", 
                    "type": "bool", 
                    "description": "Check tag reference validity",
                    "required": False,
                    "default": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Validation results with issues and recommendations"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_configuration_validation",
                "alarm_system_diagnostics",
                "alarm_troubleshooting",
                "alarm_health_check"
            ]
        }
    ])
    
    # ============================================================================
    # ALARM ROSTER OPERATIONS (5 functions)
    # ============================================================================
    
    functions.extend([
        {
            "name": "system.alarm.getRoster",
            "description": "Retrieve alarm notification roster information for scheduling",
            "parameters": [
                {
                    "name": "rosterName", 
                    "type": "str", 
                    "description": "Name of roster to retrieve",
                    "required": True
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Roster configuration and current assignments"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_roster_management",
                "alarm_notification_scheduling",
                "alarm_personnel_assignment"
            ]
        },
        
        {
            "name": "system.alarm.setRosterContact",
            "description": "Update contact information in alarm notification roster",
            "parameters": [
                {
                    "name": "rosterName", 
                    "type": "str", 
                    "description": "Name of roster to modify",
                    "required": True
                },
                {
                    "name": "contactId", 
                    "type": "str", 
                    "description": "Contact ID to update",
                    "required": True
                },
                {
                    "name": "properties", 
                    "type": "dict", 
                    "description": "Contact properties to update",
                    "required": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if contact was successfully updated"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_roster_contact_management",
                "alarm_notification_contact_update",
                "alarm_personnel_information_management"
            ]
        },
        
        {
            "name": "system.alarm.getRosterActiveContact",
            "description": "Get currently active contact from alarm notification roster",
            "parameters": [
                {
                    "name": "rosterName", 
                    "type": "str", 
                    "description": "Name of roster to query",
                    "required": True
                },
                {
                    "name": "timestamp", 
                    "type": "datetime", 
                    "description": "Time to check active contact for",
                    "required": False
                }
            ],
            "returns": {
                "type": "dict", 
                "description": "Active contact information"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_roster_current_contact",
                "alarm_notification_routing",
                "alarm_on_call_determination"
            ]
        },
        
        {
            "name": "system.alarm.setRosterEnabled",
            "description": "Enable or disable alarm notification roster",
            "parameters": [
                {
                    "name": "rosterName", 
                    "type": "str", 
                    "description": "Name of roster to modify",
                    "required": True
                },
                {
                    "name": "enabled", 
                    "type": "bool", 
                    "description": "Enable or disable the roster",
                    "required": True
                }
            ],
            "returns": {
                "type": "bool", 
                "description": "True if roster state was successfully changed"
            },
            "scope": ["Gateway"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_roster_control",
                "alarm_notification_management",
                "alarm_personnel_scheduling_control"
            ]
        },
        
        {
            "name": "system.alarm.listRosters",
            "description": "Get list of available alarm notification rosters",
            "parameters": [
                {
                    "name": "includeDisabled", 
                    "type": "bool", 
                    "description": "Include disabled rosters in results",
                    "required": False,
                    "default": False
                }
            ],
            "returns": {
                "type": "list", 
                "description": "List of roster names"
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Alarm Operations",
            "patterns": [
                "alarm_roster_discovery",
                "alarm_notification_roster_inspection",
                "alarm_personnel_management_overview"
            ]
        }
    ])
    
    return functions


# Export for easy import
__all__ = ['get_alarm_system_functions'] 