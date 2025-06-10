"""Task 5: Device Communication Expansion
Advanced device communication protocols and management for Ignition SCADA systems.

This module provides comprehensive device communication operations including:
- OPC Classic Operations
- OPC-UA Operations
- Device Management
- BACnet Protocol Support
- DNP3 Protocol Support
- Communication Monitoring and Diagnostics

Total Functions: 37 functions
Contexts: Gateway (primarily), Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2)
"""

from typing import Any


def get_device_communication_functions() -> list[dict[str, Any]]:
    """Get comprehensive device communication functions for Task 5.

    Returns:
        List[Dict[str, Any]]: List of device communication function definitions
    """
    functions = []

    # ============================================================================
    # OPC CLASSIC OPERATIONS (8 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.opc.writeValues",
                "description": "Write values to OPC Classic server items with transaction support",
                "parameters": [
                    {
                        "name": "serverName",
                        "type": "str",
                        "description": "Name of OPC server",
                        "required": True,
                    },
                    {
                        "name": "itemPaths",
                        "type": "list",
                        "description": "List of OPC item paths to write",
                        "required": True,
                    },
                    {
                        "name": "values",
                        "type": "list",
                        "description": "List of values to write",
                        "required": True,
                    },
                    {
                        "name": "timeout",
                        "type": "int",
                        "description": "Write timeout in milliseconds",
                        "required": False,
                        "default": 5000,
                    },
                    {
                        "name": "synchronous",
                        "type": "bool",
                        "description": "Synchronous or asynchronous write",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of write operation results",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_classic_write",
                    "device_data_output",
                    "industrial_communication",
                    "opc_transaction_handling",
                ],
            },
            {
                "name": "system.opc.readValues",
                "description": "Read values from OPC Classic server items with quality information",
                "parameters": [
                    {
                        "name": "serverName",
                        "type": "str",
                        "description": "Name of OPC server",
                        "required": True,
                    },
                    {
                        "name": "itemPaths",
                        "type": "list",
                        "description": "List of OPC item paths to read",
                        "required": True,
                    },
                    {
                        "name": "timeout",
                        "type": "int",
                        "description": "Read timeout in milliseconds",
                        "required": False,
                        "default": 5000,
                    },
                    {
                        "name": "includeTimestamp",
                        "type": "bool",
                        "description": "Include timestamp in results",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of read results with value, quality, and timestamp",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_classic_read",
                    "device_data_input",
                    "industrial_communication",
                    "opc_quality_monitoring",
                ],
            },
            {
                "name": "system.opc.browseSimple",
                "description": "Browse OPC server namespace for available items",
                "parameters": [
                    {
                        "name": "serverName",
                        "type": "str",
                        "description": "Name of OPC server",
                        "required": True,
                    },
                    {
                        "name": "itemPath",
                        "type": "str",
                        "description": "Starting path for browsing",
                        "required": False,
                        "default": "",
                    },
                    {
                        "name": "recursive",
                        "type": "bool",
                        "description": "Browse recursively through subdirectories",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of available OPC items and groups",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_browsing",
                    "device_discovery",
                    "opc_namespace_exploration",
                ],
            },
            {
                "name": "system.opc.getServerState",
                "description": "Get current state and status of OPC Classic server",
                "parameters": [
                    {
                        "name": "serverName",
                        "type": "str",
                        "description": "Name of OPC server",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "dict",
                    "description": "Server state information including status, connection state, and statistics",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_server_monitoring",
                    "device_status_check",
                    "opc_diagnostics",
                ],
            },
            {
                "name": "system.opc.setServerEnabled",
                "description": "Enable or disable OPC Classic server connection",
                "parameters": [
                    {
                        "name": "serverName",
                        "type": "str",
                        "description": "Name of OPC server",
                        "required": True,
                    },
                    {
                        "name": "enabled",
                        "type": "bool",
                        "description": "Enable or disable the server",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if server state was successfully changed",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_server_control",
                    "device_connection_management",
                    "opc_administrative_tasks",
                ],
            },
            {
                "name": "system.opc.getServerInfo",
                "description": "Get detailed information about OPC Classic server configuration",
                "parameters": [
                    {
                        "name": "serverName",
                        "type": "str",
                        "description": "Name of OPC server",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "dict",
                    "description": "Server configuration and capability information",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_server_inspection",
                    "device_configuration_audit",
                    "opc_capabilities_check",
                ],
            },
            {
                "name": "system.opc.subscribeToItems",
                "description": "Subscribe to OPC items for real-time value changes",
                "parameters": [
                    {
                        "name": "serverName",
                        "type": "str",
                        "description": "Name of OPC server",
                        "required": True,
                    },
                    {
                        "name": "itemPaths",
                        "type": "list",
                        "description": "List of OPC item paths to subscribe to",
                        "required": True,
                    },
                    {
                        "name": "updateRate",
                        "type": "int",
                        "description": "Update rate in milliseconds",
                        "required": False,
                        "default": 1000,
                    },
                    {
                        "name": "deadband",
                        "type": "float",
                        "description": "Deadband for change detection",
                        "required": False,
                        "default": 0.0,
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "Subscription ID for managing the subscription",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_subscription",
                    "real_time_monitoring",
                    "opc_change_detection",
                ],
            },
            {
                "name": "system.opc.unsubscribeFromItems",
                "description": "Unsubscribe from OPC item change notifications",
                "parameters": [
                    {
                        "name": "subscriptionId",
                        "type": "str",
                        "description": "Subscription ID to cancel",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if subscription was successfully cancelled",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opc_subscription_management",
                    "resource_cleanup",
                    "opc_connection_cleanup",
                ],
            },
        ]
    )

    # ============================================================================
    # OPC-UA OPERATIONS (10 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.opcua.readValues",
                "description": "Read values from OPC-UA server nodes with enhanced metadata",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    },
                    {
                        "name": "nodeIds",
                        "type": "list",
                        "description": "List of OPC-UA node IDs to read",
                        "required": True,
                    },
                    {
                        "name": "maxAge",
                        "type": "int",
                        "description": "Maximum age of cached values in milliseconds",
                        "required": False,
                        "default": 0,
                    },
                    {
                        "name": "includeServerTimestamp",
                        "type": "bool",
                        "description": "Include server timestamp in results",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of read results with value, status, timestamps, and metadata",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_read_operation",
                    "modern_industrial_communication",
                    "opcua_data_access",
                    "secure_device_communication",
                ],
            },
            {
                "name": "system.opcua.writeValues",
                "description": "Write values to OPC-UA server nodes with transaction support",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    },
                    {
                        "name": "nodeIds",
                        "type": "list",
                        "description": "List of OPC-UA node IDs to write",
                        "required": True,
                    },
                    {
                        "name": "values",
                        "type": "list",
                        "description": "List of values to write",
                        "required": True,
                    },
                    {
                        "name": "dataTypes",
                        "type": "list",
                        "description": "List of data types for each value",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of write operation results with status codes",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_write_operation",
                    "modern_industrial_communication",
                    "opcua_data_control",
                    "secure_device_communication",
                ],
            },
            {
                "name": "system.opcua.browseNodes",
                "description": "Browse OPC-UA server address space for nodes and references",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    },
                    {
                        "name": "startingNode",
                        "type": "str",
                        "description": "Starting node ID for browsing",
                        "required": False,
                        "default": "Objects",
                    },
                    {
                        "name": "browseDirection",
                        "type": "str",
                        "description": "Browse direction (Forward, Inverse, Both)",
                        "required": False,
                        "default": "Forward",
                    },
                    {
                        "name": "includeSubtypes",
                        "type": "bool",
                        "description": "Include subtypes in browse results",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "nodeClassMask",
                        "type": "int",
                        "description": "Node class mask for filtering",
                        "required": False,
                        "default": 255,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of browse results with node information and references",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_browsing",
                    "address_space_exploration",
                    "opcua_node_discovery",
                    "information_model_inspection",
                ],
            },
            {
                "name": "system.opcua.getConnectionInfo",
                "description": "Get detailed information about OPC-UA connection status and configuration",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "dict",
                    "description": "Connection information including status, security settings, and server capabilities",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_connection_monitoring",
                    "security_configuration_check",
                    "opcua_diagnostics",
                ],
            },
            {
                "name": "system.opcua.addConnection",
                "description": "Add new OPC-UA connection configuration",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name for the new connection",
                        "required": True,
                    },
                    {
                        "name": "endpointUrl",
                        "type": "str",
                        "description": "OPC-UA server endpoint URL",
                        "required": True,
                    },
                    {
                        "name": "securityPolicy",
                        "type": "str",
                        "description": "Security policy to use",
                        "required": False,
                        "default": "None",
                    },
                    {
                        "name": "securityMode",
                        "type": "str",
                        "description": "Security mode (None, Sign, SignAndEncrypt)",
                        "required": False,
                        "default": "None",
                    },
                    {
                        "name": "username",
                        "type": "str",
                        "description": "Username for authentication",
                        "required": False,
                    },
                    {
                        "name": "password",
                        "type": "str",
                        "description": "Password for authentication",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if connection was successfully added",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_connection_setup",
                    "dynamic_device_configuration",
                    "opcua_security_configuration",
                ],
            },
            {
                "name": "system.opcua.removeConnection",
                "description": "Remove OPC-UA connection configuration",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of connection to remove",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if connection was successfully removed",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_connection_cleanup",
                    "device_decommissioning",
                    "configuration_management",
                ],
            },
            {
                "name": "system.opcua.callMethod",
                "description": "Call OPC-UA method on server with input parameters",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    },
                    {
                        "name": "objectId",
                        "type": "str",
                        "description": "Node ID of object containing the method",
                        "required": True,
                    },
                    {
                        "name": "methodId",
                        "type": "str",
                        "description": "Node ID of method to call",
                        "required": True,
                    },
                    {
                        "name": "inputArguments",
                        "type": "list",
                        "description": "List of input arguments for the method",
                        "required": False,
                        "default": [],
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Method call results including output arguments and status",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_method_execution",
                    "remote_procedure_call",
                    "device_command_execution",
                ],
            },
            {
                "name": "system.opcua.createSubscription",
                "description": "Create OPC-UA subscription for monitoring data changes",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    },
                    {
                        "name": "nodeIds",
                        "type": "list",
                        "description": "List of node IDs to monitor",
                        "required": True,
                    },
                    {
                        "name": "publishingInterval",
                        "type": "int",
                        "description": "Publishing interval in milliseconds",
                        "required": False,
                        "default": 1000,
                    },
                    {
                        "name": "samplingInterval",
                        "type": "int",
                        "description": "Sampling interval in milliseconds",
                        "required": False,
                        "default": 1000,
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "Subscription ID for managing the subscription",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_subscription",
                    "real_time_data_monitoring",
                    "event_driven_communication",
                ],
            },
            {
                "name": "system.opcua.deleteSubscription",
                "description": "Delete OPC-UA subscription to stop monitoring",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    },
                    {
                        "name": "subscriptionId",
                        "type": "str",
                        "description": "Subscription ID to delete",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if subscription was successfully deleted",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_subscription_cleanup",
                    "resource_management",
                    "monitoring_lifecycle",
                ],
            },
            {
                "name": "system.opcua.getServerCertificate",
                "description": "Get OPC-UA server certificate information for security validation",
                "parameters": [
                    {
                        "name": "connectionName",
                        "type": "str",
                        "description": "Name of OPC-UA connection",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "dict",
                    "description": "Server certificate information including validity and trust status",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "opcua_security_validation",
                    "certificate_management",
                    "security_audit",
                ],
            },
        ]
    )

    # ============================================================================
    # DEVICE MANAGEMENT OPERATIONS (8 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.device.addDevice",
                "description": "Add new device to the gateway configuration",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name for the new device",
                        "required": True,
                    },
                    {
                        "name": "deviceType",
                        "type": "str",
                        "description": "Type of device driver to use",
                        "required": True,
                    },
                    {
                        "name": "connectionProperties",
                        "type": "dict",
                        "description": "Device connection properties",
                        "required": True,
                    },
                    {
                        "name": "enabled",
                        "type": "bool",
                        "description": "Enable device after creation",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if device was successfully added",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "device_configuration",
                    "dynamic_device_setup",
                    "industrial_connectivity",
                ],
            },
            {
                "name": "system.device.removeDevice",
                "description": "Remove device from gateway configuration",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of device to remove",
                        "required": True,
                    },
                    {
                        "name": "force",
                        "type": "bool",
                        "description": "Force removal even if device has active connections",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if device was successfully removed",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "device_decommissioning",
                    "configuration_cleanup",
                    "device_lifecycle_management",
                ],
            },
            {
                "name": "system.device.setDeviceEnabled",
                "description": "Enable or disable device connection",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of device to modify",
                        "required": True,
                    },
                    {
                        "name": "enabled",
                        "type": "bool",
                        "description": "Enable or disable the device",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if device state was successfully changed",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "device_control",
                    "connection_management",
                    "maintenance_operations",
                ],
            },
            {
                "name": "system.device.getDeviceConfiguration",
                "description": "Get complete device configuration including connection properties",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of device to inspect",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "dict",
                    "description": "Complete device configuration including properties and status",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "device_inspection",
                    "configuration_audit",
                    "troubleshooting_support",
                ],
            },
            {
                "name": "system.device.setDeviceConfiguration",
                "description": "Update device configuration properties",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of device to configure",
                        "required": True,
                    },
                    {
                        "name": "properties",
                        "type": "dict",
                        "description": "Configuration properties to update",
                        "required": True,
                    },
                    {
                        "name": "restart",
                        "type": "bool",
                        "description": "Restart device after configuration change",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if configuration was successfully updated",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "device_configuration_update",
                    "runtime_reconfiguration",
                    "device_management",
                ],
            },
            {
                "name": "system.device.getDeviceStatus",
                "description": "Get current status and diagnostics for device",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of device to check",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "dict",
                    "description": "Device status including connection state, statistics, and error information",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Device Communication",
                "patterns": [
                    "device_monitoring",
                    "diagnostics",
                    "health_check",
                    "status_reporting",
                ],
            },
            {
                "name": "system.device.restartDevice",
                "description": "Restart device connection to apply configuration changes",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of device to restart",
                        "required": True,
                    },
                    {
                        "name": "timeout",
                        "type": "int",
                        "description": "Timeout for restart operation in seconds",
                        "required": False,
                        "default": 30,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if device restarted successfully",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "device_restart",
                    "connection_recovery",
                    "maintenance_operations",
                ],
            },
            {
                "name": "system.device.listDevices",
                "description": "Get list of all configured devices with status information",
                "parameters": [
                    {
                        "name": "includeDisabled",
                        "type": "bool",
                        "description": "Include disabled devices in results",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "deviceType",
                        "type": "str",
                        "description": "Filter by device type",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of device information including names, types, and status",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Device Communication",
                "patterns": ["device_inventory", "system_overview", "device_discovery"],
            },
        ]
    )

    # ============================================================================
    # BACNET PROTOCOL OPERATIONS (6 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.bacnet.synchronizeTime",
                "description": "Synchronize time with BACnet devices on the network",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of BACnet device connection",
                        "required": True,
                    },
                    {
                        "name": "deviceInstanceId",
                        "type": "int",
                        "description": "BACnet device instance ID",
                        "required": False,
                    },
                    {
                        "name": "broadcast",
                        "type": "bool",
                        "description": "Broadcast time synchronization to all devices",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if time synchronization was successful",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "bacnet_time_sync",
                    "building_automation",
                    "network_coordination",
                ],
            },
            {
                "name": "system.bacnet.readProperty",
                "description": "Read BACnet property from device object",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of BACnet device connection",
                        "required": True,
                    },
                    {
                        "name": "deviceInstanceId",
                        "type": "int",
                        "description": "BACnet device instance ID",
                        "required": True,
                    },
                    {
                        "name": "objectType",
                        "type": "str",
                        "description": "BACnet object type",
                        "required": True,
                    },
                    {
                        "name": "objectInstance",
                        "type": "int",
                        "description": "BACnet object instance",
                        "required": True,
                    },
                    {
                        "name": "propertyId",
                        "type": "str",
                        "description": "BACnet property identifier",
                        "required": True,
                    },
                    {
                        "name": "arrayIndex",
                        "type": "int",
                        "description": "Array index for array properties",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "Any",
                    "description": "Property value with appropriate BACnet data type",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "bacnet_property_read",
                    "building_automation_data",
                    "bacnet_object_access",
                ],
            },
            {
                "name": "system.bacnet.writeProperty",
                "description": "Write BACnet property to device object",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of BACnet device connection",
                        "required": True,
                    },
                    {
                        "name": "deviceInstanceId",
                        "type": "int",
                        "description": "BACnet device instance ID",
                        "required": True,
                    },
                    {
                        "name": "objectType",
                        "type": "str",
                        "description": "BACnet object type",
                        "required": True,
                    },
                    {
                        "name": "objectInstance",
                        "type": "int",
                        "description": "BACnet object instance",
                        "required": True,
                    },
                    {
                        "name": "propertyId",
                        "type": "str",
                        "description": "BACnet property identifier",
                        "required": True,
                    },
                    {
                        "name": "value",
                        "type": "Any",
                        "description": "Value to write to the property",
                        "required": True,
                    },
                    {
                        "name": "priority",
                        "type": "int",
                        "description": "Write priority (1-16)",
                        "required": False,
                        "default": 16,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if property was successfully written",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "bacnet_property_write",
                    "building_automation_control",
                    "bacnet_object_control",
                ],
            },
            {
                "name": "system.bacnet.releaseProperty",
                "description": "Release BACnet property by clearing write priority",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of BACnet device connection",
                        "required": True,
                    },
                    {
                        "name": "deviceInstanceId",
                        "type": "int",
                        "description": "BACnet device instance ID",
                        "required": True,
                    },
                    {
                        "name": "objectType",
                        "type": "str",
                        "description": "BACnet object type",
                        "required": True,
                    },
                    {
                        "name": "objectInstance",
                        "type": "int",
                        "description": "BACnet object instance",
                        "required": True,
                    },
                    {
                        "name": "propertyId",
                        "type": "str",
                        "description": "BACnet property identifier",
                        "required": True,
                    },
                    {
                        "name": "priority",
                        "type": "int",
                        "description": "Priority level to release (1-16)",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if property priority was successfully released",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "bacnet_priority_release",
                    "building_automation_release",
                    "bacnet_control_handoff",
                ],
            },
            {
                "name": "system.bacnet.discoverDevices",
                "description": "Discover BACnet devices on the network",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of BACnet device connection",
                        "required": True,
                    },
                    {
                        "name": "timeout",
                        "type": "int",
                        "description": "Discovery timeout in seconds",
                        "required": False,
                        "default": 10,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of discovered BACnet devices with instance IDs and network information",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "bacnet_device_discovery",
                    "network_scanning",
                    "building_automation_commissioning",
                ],
            },
            {
                "name": "system.bacnet.readObjectList",
                "description": "Read object list from BACnet device to discover available objects",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of BACnet device connection",
                        "required": True,
                    },
                    {
                        "name": "deviceInstanceId",
                        "type": "int",
                        "description": "BACnet device instance ID",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of BACnet objects available on the device",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "bacnet_object_discovery",
                    "device_enumeration",
                    "building_automation_inspection",
                ],
            },
        ]
    )

    # ============================================================================
    # DNP3 PROTOCOL OPERATIONS (5 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.dnp3.request",
                "description": "Send DNP3 request to outstation device",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of DNP3 device connection",
                        "required": True,
                    },
                    {
                        "name": "functionCode",
                        "type": "int",
                        "description": "DNP3 function code for the request",
                        "required": True,
                    },
                    {
                        "name": "objectGroup",
                        "type": "int",
                        "description": "DNP3 object group",
                        "required": True,
                    },
                    {
                        "name": "variation",
                        "type": "int",
                        "description": "DNP3 object variation",
                        "required": True,
                    },
                    {
                        "name": "startIndex",
                        "type": "int",
                        "description": "Starting index for the request",
                        "required": False,
                        "default": 0,
                    },
                    {
                        "name": "endIndex",
                        "type": "int",
                        "description": "Ending index for the request",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "DNP3 response data including values and status information",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": ["dnp3_request", "scada_communication", "utility_protocol"],
            },
            {
                "name": "system.dnp3.sendDataSet",
                "description": "Send DNP3 dataset to outstation for control operations",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of DNP3 device connection",
                        "required": True,
                    },
                    {
                        "name": "dataSet",
                        "type": "Dataset",
                        "description": "Dataset containing DNP3 points and values",
                        "required": True,
                    },
                    {
                        "name": "operationType",
                        "type": "str",
                        "description": "Type of operation (SELECT, OPERATE, DIRECT_OPERATE)",
                        "required": False,
                        "default": "DIRECT_OPERATE",
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Operation results including success status and response details",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "dnp3_control",
                    "scada_control_operation",
                    "utility_command_execution",
                ],
            },
            {
                "name": "system.dnp3.readClass0Data",
                "description": "Perform DNP3 Class 0 data read (static data)",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of DNP3 device connection",
                        "required": True,
                    },
                    {
                        "name": "includeTimeSync",
                        "type": "bool",
                        "description": "Include time synchronization in request",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "Dataset",
                    "description": "Dataset containing all static data from the outstation",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": ["dnp3_static_read", "data_acquisition", "scada_polling"],
            },
            {
                "name": "system.dnp3.readEventData",
                "description": "Read DNP3 event data (Class 1, 2, 3 events)",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of DNP3 device connection",
                        "required": True,
                    },
                    {
                        "name": "eventClasses",
                        "type": "list",
                        "description": "List of event classes to read (1, 2, 3)",
                        "required": False,
                        "default": [1, 2, 3],
                    },
                ],
                "returns": {
                    "type": "Dataset",
                    "description": "Dataset containing event data from the outstation",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "dnp3_event_read",
                    "change_of_state_monitoring",
                    "event_driven_communication",
                ],
            },
            {
                "name": "system.dnp3.performIntegrityPoll",
                "description": "Perform DNP3 integrity poll to read all data",
                "parameters": [
                    {
                        "name": "deviceName",
                        "type": "str",
                        "description": "Name of DNP3 device connection",
                        "required": True,
                    }
                ],
                "returns": {
                    "type": "Dataset",
                    "description": "Complete dataset with all static and event data",
                },
                "scope": ["Gateway"],
                "category": "Device Communication",
                "patterns": [
                    "dnp3_integrity_poll",
                    "complete_data_refresh",
                    "system_synchronization",
                ],
            },
        ]
    )

    return functions


# Export for easy import
__all__ = ["get_device_communication_functions"]
