"""Task 14: OPC-UA Client Integration Functions.

OPC-UA (Open Platform Communications Unified Architecture) client functions for Ignition SCADA systems.
This module provides comprehensive OPC-UA client capabilities including:
- Connection Management & Security
- Address Space Navigation & Browsing
- Data Operations (Read/Write/Method Calls)
- Real-time Subscriptions & Monitoring
- Alarm Handling & Historical Data Access
- Certificate Management & Authentication

Total Functions: 12 functions
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2), Security (Task 9), Integration (Task 13)
"""

from typing import Any


def get_opcua_client_functions() -> list[dict[str, Any]]:
    """Get comprehensive OPC-UA client functions for Task 14."""
    functions = []

    # ============================================================================
    # CONNECTION MANAGEMENT & SECURITY (3 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.opcua.createConnection",
                "description": "Create and configure OPC-UA client connections with automatic discovery and security",
                "parameters": "serverUrl:str:required, applicationName:str:optional:IgnitionOPCClient, securityMode:str:optional:SignAndEncrypt, securityPolicy:str:optional:Basic256Sha256, authentication:dict:optional, sessionTimeout:int:optional:300000, connectTimeout:int:optional:30000, autoReconnect:bool:optional:true",
                "returns": "dict - OPC-UA connection handle with server info, security status, and session details",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "OPC-UA Connection",
                "patterns": [
                    "opcua_client",
                    "industrial_connectivity",
                    "server_connection",
                    "secure_communication",
                ],
            },
            {
                "name": "system.opcua.manageEndpoints",
                "description": "Discover and manage OPC-UA server endpoints with filtering and selection capabilities",
                "parameters": "discoveryUrl:str:required, endpointFilters:dict:optional, securityRequirements:dict:optional, applicationFilters:list:optional, timeout:int:optional:10000, maxEndpoints:int:optional:50",
                "returns": "dict - Available endpoints with security policies, transport profiles, and server capabilities",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Endpoint Discovery",
                "patterns": [
                    "endpoint_discovery",
                    "server_discovery",
                    "opcua_browsing",
                    "connectivity_management",
                ],
            },
            {
                "name": "system.opcua.handleSecurity",
                "description": "Configure OPC-UA security including certificates, authentication, and encryption policies",
                "parameters": "connectionId:str:required, certificateConfig:dict:required, privateKeyConfig:dict:optional, trustedCertificates:list:optional, userIdentity:dict:optional, encryptionEnabled:bool:optional:true, signatureValidation:bool:optional:true",
                "returns": "dict - Security configuration status with certificate validation and authentication results",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Security Management",
                "patterns": [
                    "certificate_management",
                    "security_config",
                    "authentication",
                    "encryption",
                ],
            },
        ]
    )

    # ============================================================================
    # ADDRESS SPACE NAVIGATION & BROWSING (2 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.opcua.browseNodes",
                "description": "Browse OPC-UA server address space with hierarchical navigation and filtering",
                "parameters": "connectionId:str:required, startingNode:str:optional:Objects, browseDirection:str:optional:Forward, nodeClassMask:int:optional:255, resultMask:int:optional:63, maxResults:int:optional:1000, includeSubtypes:bool:optional:true, filterCriteria:dict:optional",
                "returns": "dict - Node hierarchy with references, attributes, data types, and browsing continuation points",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Address Space Browsing",
                "patterns": [
                    "node_browsing",
                    "address_space",
                    "hierarchy_navigation",
                    "opcua_discovery",
                ],
            },
            {
                "name": "system.opcua.resolveNodeIds",
                "description": "Resolve and validate OPC-UA node identifiers with reference following",
                "parameters": "connectionId:str:required, nodeIds:list:required, resolveReferences:bool:optional:true, includeAttributes:bool:optional:true, validateExistence:bool:optional:true, attributeFilter:list:optional",
                "returns": "dict - Resolved node information with attributes, references, data types, and validation status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Node Resolution",
                "patterns": [
                    "node_resolution",
                    "node_validation",
                    "reference_following",
                    "node_attributes",
                ],
            },
        ]
    )

    # ============================================================================
    # DATA OPERATIONS (3 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.opcua.readNodes",
                "description": "Read values from OPC-UA nodes with batch operations and quality validation",
                "parameters": "connectionId:str:required, nodeIds:list:required, attributes:list:optional:Value, maxAge:int:optional:0, timestampsToReturn:str:optional:Both, batchSize:int:optional:100, qualityValidation:bool:optional:true, retryPolicy:dict:optional",
                "returns": "dict - Node values with quality codes, timestamps, status codes, and data type information",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Reading",
                "patterns": [
                    "data_reading",
                    "batch_operations",
                    "quality_codes",
                    "value_access",
                ],
            },
            {
                "name": "system.opcua.writeNodes",
                "description": "Write values to OPC-UA nodes with data validation and status reporting",
                "parameters": "connectionId:str:required, writeRequests:list:required, dataValidation:bool:optional:true, typeConversion:bool:optional:true, batchSize:int:optional:100, writeTimeout:int:optional:30000, confirmationRequired:bool:optional:false",
                "returns": "dict - Write operation results with status codes, error details, and confirmation data",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Writing",
                "patterns": [
                    "data_writing",
                    "value_setting",
                    "write_validation",
                    "status_reporting",
                ],
            },
            {
                "name": "system.opcua.callMethods",
                "description": "Execute OPC-UA methods on server objects with parameter validation",
                "parameters": "connectionId:str:required, methodCalls:list:required, parameterValidation:bool:optional:true, outputValidation:bool:optional:true, executionTimeout:int:optional:60000, asyncExecution:bool:optional:false",
                "returns": "dict - Method execution results with output parameters, status codes, and execution details",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Method Execution",
                "patterns": [
                    "method_calls",
                    "server_methods",
                    "parameter_validation",
                    "remote_execution",
                ],
            },
        ]
    )

    # ============================================================================
    # SUBSCRIPTION & MONITORING (4 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.opcua.createSubscriptions",
                "description": "Create and manage OPC-UA subscriptions for real-time data monitoring",
                "parameters": "connectionId:str:required, subscriptionConfig:dict:required, publishingInterval:int:optional:1000, lifetimeCount:int:optional:1200, maxKeepAliveCount:int:optional:10, maxNotificationsPerPublish:int:optional:0, priority:int:optional:0, publishingEnabled:bool:optional:true",
                "returns": "dict - Subscription handle with configuration details, status, and notification settings",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Subscription Management",
                "patterns": [
                    "subscription_creation",
                    "real_time_monitoring",
                    "data_notifications",
                    "live_updates",
                ],
            },
            {
                "name": "system.opcua.monitorItems",
                "description": "Monitor specific OPC-UA items for value and status changes with filtering",
                "parameters": "subscriptionId:str:required, monitoredItems:list:required, samplingInterval:int:optional:1000, deadbandType:str:optional:Absolute, deadbandValue:float:optional:0.0, discardOldest:bool:optional:true, queueSize:int:optional:10",
                "returns": "dict - Monitoring configuration with item handles, filter settings, and notification status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Item Monitoring",
                "patterns": [
                    "item_monitoring",
                    "change_detection",
                    "deadband_filtering",
                    "data_changes",
                ],
            },
            {
                "name": "system.opcua.handleNotifications",
                "description": "Process OPC-UA subscription notifications and data change events",
                "parameters": "subscriptionId:str:required, notificationHandler:str:required, eventFiltering:dict:optional, dataProcessing:dict:optional, batchProcessing:bool:optional:false, errorHandling:str:optional:log, queueManagement:dict:optional",
                "returns": "dict - Notification processing status with event counts, error details, and queue statistics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Notification Handling",
                "patterns": [
                    "notification_processing",
                    "event_handling",
                    "data_change_events",
                    "subscription_data",
                ],
            },
            {
                "name": "system.opcua.manageSubscriptionLifecycle",
                "description": "Manage OPC-UA subscription lifecycle including creation, modification, and cleanup",
                "parameters": "connectionId:str:required, operation:str:required, subscriptionId:str:optional, modificationParams:dict:optional, cleanupPolicy:str:optional:graceful, transferPolicy:dict:optional",
                "returns": "dict - Subscription lifecycle status with operation results and resource management details",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Subscription Lifecycle",
                "patterns": [
                    "subscription_lifecycle",
                    "resource_management",
                    "subscription_cleanup",
                    "lifecycle_management",
                ],
            },
        ]
    )

    # ============================================================================
    # ADVANCED FEATURES (2 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.opcua.manageAlarms",
                "description": "Handle OPC-UA alarms and conditions with acknowledgment and filtering",
                "parameters": "connectionId:str:required, alarmConfig:dict:required, conditionTypes:list:optional, acknowledgmentHandling:bool:optional:true, alarmFiltering:dict:optional, historicalAlarms:bool:optional:false, escalationRules:dict:optional",
                "returns": "dict - Alarm management status with active conditions, acknowledgment results, and alarm history",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Alarm Management",
                "patterns": [
                    "alarm_handling",
                    "condition_monitoring",
                    "alarm_acknowledgment",
                    "event_management",
                ],
            },
            {
                "name": "system.opcua.performHistoricalRead",
                "description": "Read historical data from OPC-UA servers with time-based queries and aggregation",
                "parameters": "connectionId:str:required, nodeIds:list:required, startTime:str:required, endTime:str:required, aggregateType:str:optional:Raw, processingInterval:int:optional:0, maxValues:int:optional:1000, returnBounds:bool:optional:false, qualityFilter:dict:optional",
                "returns": "dict - Historical data with timestamps, values, quality codes, and aggregation results",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Historical Data Access",
                "patterns": [
                    "historical_data",
                    "time_series_data",
                    "data_aggregation",
                    "historical_queries",
                ],
            },
        ]
    )

    return functions


def get_task_14_metadata() -> dict[str, Any]:
    """Get metadata about Task 14: OPC-UA Client Integration Functions."""
    return {
        "task_number": 14,
        "task_name": "OPC-UA Client Integration Functions",
        "description": "Comprehensive OPC-UA client capabilities for industrial automation, device connectivity, and real-time data exchange",
        "total_functions": 12,
        "categories": [
            "Connection Management",
            "Address Space Navigation",
            "Data Operations",
            "Subscription & Monitoring",
            "Advanced Features",
        ],
        "contexts": ["Gateway", "Vision Client", "Perspective Session"],
        "dependencies": [
            "Task 1: Tag System",
            "Task 2: Database System",
            "Task 9: Security System",
            "Task 13: Integration & External Systems",
        ],
        "priority": "HIGH",
        "industrial_focus": "Manufacturing, Process Control, Industrial IoT",
        "estimated_completion": "Week 15",
    }


if __name__ == "__main__":
    functions = get_opcua_client_functions()
    metadata = get_task_14_metadata()
    print(f"Task 14: {metadata['task_name']}")
    print(f"Total Functions: {len(functions)}")
    print(f"Expected: {metadata['total_functions']}")

    # Verify function structure
    for func in functions:
        assert "name" in func
        assert "description" in func
        assert "parameters" in func
        assert "returns" in func
        assert "scope" in func
        assert "category" in func
        assert "patterns" in func

    print("✅ All function definitions are valid!")

    # Display function categories
    categories = {}
    for func in functions:
        cat = func["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(func["name"])

    print("\n📊 Function Categories:")
    for category, funcs in categories.items():
        print(f"   • {category}: {len(funcs)} functions")

    print("\n🏭 Industrial OPC-UA Capabilities:")
    print("   • Connection Management: Multi-server support with security")
    print("   • Address Space Browsing: Complete node hierarchy navigation")
    print("   • Data Operations: Read/write with quality codes and validation")
    print("   • Real-time Monitoring: Subscriptions with deadband filtering")
    print("   • Advanced Features: Alarms, historical data, method execution")
    print("   • Industrial Integration: PLCs, SCADA, MES, and DCS systems")
