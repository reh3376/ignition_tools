"""Task 13: Integration & External Systems Functions.

Integration and external system connectivity functions for Ignition SCADA systems.
This module provides comprehensive integration capabilities including:
- REST API & Web Service Integration
- Network Communication Protocols
- Data Exchange & Message Queuing
- Cloud Service Integration
- Enterprise Service Bus Functions
- Authentication & Authorization
- Third-party System Connectors
- Real-time Data Synchronization

Total Functions: 30 functions
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2), Security (Task 9)
"""

from typing import Any


def get_integration_external_functions() -> list[dict[str, Any]]:
    """Get comprehensive integration & external systems functions for Task 13."""
    functions = []

    # ============================================================================
    # REST API & WEB SERVICE INTEGRATION (10 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.integration.callRestAPI",
                "description": "Call REST APIs with comprehensive error handling and authentication",
                "parameters": "url:str:required, method:str:optional:GET, headers:dict:optional, body:str:optional, timeout:int:optional:30, authentication:dict:optional, retryPolicy:dict:optional",
                "returns": "dict - REST API response with status, data, and metadata",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "REST API",
                "patterns": [
                    "rest_api",
                    "web_service",
                    "http_client",
                    "external_integration",
                ],
            },
            {
                "name": "system.integration.createWebService",
                "description": "Create and expose web service endpoints from Ignition",
                "parameters": "serviceName:str:required, endpoint:str:required, methods:list:required, authentication:bool:optional:true, corsEnabled:bool:optional:false, rateLimiting:dict:optional",
                "returns": "dict - Web service configuration with endpoint URL and status",
                "scope": ["Gateway"],
                "category": "Web Service",
                "patterns": [
                    "web_service",
                    "rest_endpoint",
                    "service_creation",
                    "api_exposure",
                ],
            },
            {
                "name": "system.integration.configureOAuth",
                "description": "Configure OAuth authentication for external API integrations",
                "parameters": "providerName:str:required, clientId:str:required, clientSecret:str:required, scopes:list:optional, authUrl:str:required, tokenUrl:str:required, refreshEnabled:bool:optional:true",
                "returns": "dict - OAuth configuration with authentication status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "OAuth Authentication",
                "patterns": [
                    "oauth",
                    "authentication",
                    "external_auth",
                    "secure_integration",
                ],
            },
            {
                "name": "system.integration.manageAPIKeys",
                "description": "Manage API keys for external service integrations",
                "parameters": "keyName:str:required, apiKey:str:required, provider:str:required, permissions:list:optional, expirationDate:str:optional, rotationPolicy:dict:optional",
                "returns": "dict - API key management status with security metrics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "API Management",
                "patterns": [
                    "api_key",
                    "credential_management",
                    "security",
                    "access_control",
                ],
            },
            {
                "name": "system.integration.validateAPIResponse",
                "description": "Validate and parse API responses with schema validation",
                "parameters": "response:dict:required, schema:dict:optional, validationRules:list:optional, errorHandling:str:optional:strict, parseFormat:str:optional:json",
                "returns": "dict - Validated response data with parsing results",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "API Validation",
                "patterns": [
                    "response_validation",
                    "schema_validation",
                    "data_parsing",
                    "error_handling",
                ],
            },
            {
                "name": "system.integration.cacheAPIResponses",
                "description": "Cache API responses for improved performance and reduced external calls",
                "parameters": "cacheKey:str:required, response:dict:required, ttl:int:optional:3600, cacheStrategy:str:optional:lru, invalidationRules:list:optional",
                "returns": "dict - Cache status with hit/miss statistics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "API Caching",
                "patterns": [
                    "response_caching",
                    "performance_optimization",
                    "cache_management",
                    "data_efficiency",
                ],
            },
            {
                "name": "system.integration.monitorAPIHealth",
                "description": "Monitor health and performance of external API integrations",
                "parameters": "apiEndpoints:list:required, healthCheckInterval:int:optional:300, performanceThresholds:dict:optional, alerting:bool:optional:true, metrics:list:optional",
                "returns": "dict - API health status with performance metrics and alerts",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "API Monitoring",
                "patterns": [
                    "health_monitoring",
                    "performance_tracking",
                    "api_analytics",
                    "system_reliability",
                ],
            },
            {
                "name": "system.integration.handleWebhooks",
                "description": "Handle incoming webhooks from external systems",
                "parameters": "webhookUrl:str:required, eventTypes:list:required, authentication:dict:optional, processingLogic:str:required, responseFormat:str:optional:json",
                "returns": "dict - Webhook processing status with event handling results",
                "scope": ["Gateway"],
                "category": "Webhook Handling",
                "patterns": [
                    "webhook",
                    "event_handling",
                    "external_events",
                    "real_time_integration",
                ],
            },
            {
                "name": "system.integration.synchronizeData",
                "description": "Synchronize data between Ignition and external systems",
                "parameters": "sourceSystem:str:required, targetSystem:str:required, dataMapping:dict:required, syncStrategy:str:optional:bidirectional, conflictResolution:str:optional:timestamp",
                "returns": "dict - Data synchronization results with conflict resolution details",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Synchronization",
                "patterns": [
                    "data_sync",
                    "bi_directional_sync",
                    "conflict_resolution",
                    "data_integration",
                ],
            },
            {
                "name": "system.integration.transformData",
                "description": "Transform data between different formats for external system integration",
                "parameters": "inputData:dict:required, sourceFormat:str:required, targetFormat:str:required, transformationRules:dict:required, validationEnabled:bool:optional:true",
                "returns": "dict - Transformed data with validation results",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Transformation",
                "patterns": [
                    "data_transformation",
                    "format_conversion",
                    "data_mapping",
                    "integration_pipeline",
                ],
            },
        ]
    )

    # ============================================================================
    # NETWORK COMMUNICATION & PROTOCOLS (10 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.integration.configureTCP",
                "description": "Configure TCP communication for external system connectivity",
                "parameters": "host:str:required, port:int:required, connectionTimeout:int:optional:5000, keepAlive:bool:optional:true, bufferSize:int:optional:8192, encryption:bool:optional:false",
                "returns": "dict - TCP connection status with performance metrics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "TCP Communication",
                "patterns": [
                    "tcp_client",
                    "network_communication",
                    "socket_communication",
                    "external_connectivity",
                ],
            },
            {
                "name": "system.integration.configureUDP",
                "description": "Configure UDP communication for real-time data exchange",
                "parameters": "host:str:required, port:int:required, broadcastEnabled:bool:optional:false, multicastGroup:str:optional, packetSize:int:optional:1024, errorHandling:str:optional:ignore",
                "returns": "dict - UDP configuration status with network parameters",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "UDP Communication",
                "patterns": [
                    "udp_client",
                    "real_time_communication",
                    "broadcast_communication",
                    "network_protocols",
                ],
            },
            {
                "name": "system.integration.manageFTP",
                "description": "Manage FTP file transfers with external systems",
                "parameters": "ftpServer:str:required, username:str:required, password:str:required, transferMode:str:optional:binary, encryption:str:optional:none, passiveMode:bool:optional:true",
                "returns": "dict - FTP operation results with transfer statistics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "FTP Management",
                "patterns": [
                    "ftp_client",
                    "file_transfer",
                    "secure_transfer",
                    "external_file_system",
                ],
            },
            {
                "name": "system.integration.configureSFTP",
                "description": "Configure secure SFTP connections for file transfers",
                "parameters": "sftpServer:str:required, username:str:required, privateKey:str:optional, password:str:optional, hostKeyVerification:bool:optional:true, compressionEnabled:bool:optional:false",
                "returns": "dict - SFTP connection status with security parameters",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "SFTP Management",
                "patterns": [
                    "sftp_client",
                    "secure_transfer",
                    "ssh_protocol",
                    "encrypted_communication",
                ],
            },
            {
                "name": "system.integration.handleSMTP",
                "description": "Handle SMTP email communication for system notifications",
                "parameters": "smtpServer:str:required, port:int:optional:587, authentication:dict:required, encryption:str:optional:tls, connectionPooling:bool:optional:true, rateLimiting:dict:optional",
                "returns": "dict - SMTP configuration with email delivery status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "SMTP Communication",
                "patterns": [
                    "smtp_client",
                    "email_communication",
                    "notification_system",
                    "messaging",
                ],
            },
            {
                "name": "system.integration.configureSNMP",
                "description": "Configure SNMP for network device monitoring and management",
                "parameters": "snmpHost:str:required, community:str:required, version:str:optional:v2c, port:int:optional:161, timeout:int:optional:5000, retries:int:optional:3",
                "returns": "dict - SNMP configuration with device monitoring status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "SNMP Management",
                "patterns": [
                    "snmp_client",
                    "network_monitoring",
                    "device_management",
                    "infrastructure_monitoring",
                ],
            },
            {
                "name": "system.integration.manageLDAP",
                "description": "Manage LDAP directory services for user authentication and authorization",
                "parameters": "ldapServer:str:required, bindDN:str:required, bindPassword:str:required, baseDN:str:required, encryption:str:optional:none, connectionPooling:bool:optional:true",
                "returns": "dict - LDAP connection status with directory service configuration",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "LDAP Management",
                "patterns": [
                    "ldap_client",
                    "directory_services",
                    "user_authentication",
                    "enterprise_integration",
                ],
            },
            {
                "name": "system.integration.configureSSL",
                "description": "Configure SSL/TLS encryption for secure external communications",
                "parameters": "protocol:str:optional:TLSv1.2, certificatePath:str:optional, privateKeyPath:str:optional, caCertificatePath:str:optional, verifyMode:str:optional:required, cipherSuites:list:optional",
                "returns": "dict - SSL configuration status with encryption parameters",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "SSL Configuration",
                "patterns": [
                    "ssl_configuration",
                    "encryption",
                    "secure_communication",
                    "certificate_management",
                ],
            },
            {
                "name": "system.integration.monitorNetworkPerformance",
                "description": "Monitor network performance for external system integrations",
                "parameters": "endpoints:list:required, metrics:list:optional, alertThresholds:dict:optional, reportingInterval:int:optional:60, historicalData:bool:optional:true",
                "returns": "dict - Network performance metrics with trend analysis",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Network Monitoring",
                "patterns": [
                    "network_monitoring",
                    "performance_analysis",
                    "connectivity_tracking",
                    "infrastructure_health",
                ],
            },
            {
                "name": "system.integration.handleVPN",
                "description": "Handle VPN connections for secure external system access",
                "parameters": "vpnServer:str:required, vpnType:str:required, credentials:dict:required, autoConnect:bool:optional:true, connectionTimeout:int:optional:30000, healthCheck:bool:optional:true",
                "returns": "dict - VPN connection status with security metrics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "VPN Management",
                "patterns": [
                    "vpn_client",
                    "secure_tunneling",
                    "remote_access",
                    "network_security",
                ],
            },
        ]
    )

    # ============================================================================
    # MESSAGE QUEUING & ENTERPRISE INTEGRATION (10 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.integration.configureMQTT",
                "description": "Configure MQTT messaging for IoT and real-time data exchange",
                "parameters": "brokerUrl:str:required, clientId:str:required, credentials:dict:optional, qos:int:optional:1, keepAlive:int:optional:60, cleanSession:bool:optional:true",
                "returns": "dict - MQTT connection status with messaging configuration",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "MQTT Messaging",
                "patterns": [
                    "mqtt_client",
                    "iot_communication",
                    "pub_sub_messaging",
                    "real_time_data",
                ],
            },
            {
                "name": "system.integration.manageJMS",
                "description": "Manage Java Message Service (JMS) for enterprise messaging",
                "parameters": "connectionFactory:str:required, destination:str:required, messageType:str:optional:queue, persistence:bool:optional:true, transacted:bool:optional:false, acknowledgeMode:str:optional:auto",
                "returns": "dict - JMS configuration with message handling status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "JMS Messaging",
                "patterns": [
                    "jms_client",
                    "enterprise_messaging",
                    "message_queue",
                    "async_communication",
                ],
            },
            {
                "name": "system.integration.configureKafka",
                "description": "Configure Apache Kafka for high-throughput data streaming",
                "parameters": "bootstrapServers:str:required, topic:str:required, groupId:str:optional, keySerializer:str:optional, valueSerializer:str:optional, batchSize:int:optional:16384",
                "returns": "dict - Kafka configuration with streaming status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Kafka Streaming",
                "patterns": [
                    "kafka_client",
                    "data_streaming",
                    "event_streaming",
                    "big_data_integration",
                ],
            },
            {
                "name": "system.integration.handleRabbitMQ",
                "description": "Handle RabbitMQ message brokering for reliable messaging",
                "parameters": "host:str:required, virtualHost:str:optional:/, exchange:str:required, routingKey:str:required, credentials:dict:required, durable:bool:optional:true",
                "returns": "dict - RabbitMQ configuration with message broker status",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "RabbitMQ Messaging",
                "patterns": [
                    "rabbitmq_client",
                    "message_broker",
                    "reliable_messaging",
                    "enterprise_queue",
                ],
            },
            {
                "name": "system.integration.configureWebSockets",
                "description": "Configure WebSocket connections for real-time bidirectional communication",
                "parameters": "websocketUrl:str:required, protocols:list:optional, headers:dict:optional, heartbeatInterval:int:optional:30, reconnectEnabled:bool:optional:true, maxReconnectAttempts:int:optional:5",
                "returns": "dict - WebSocket connection status with real-time capabilities",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "WebSocket Communication",
                "patterns": [
                    "websocket_client",
                    "real_time_communication",
                    "bidirectional_messaging",
                    "live_updates",
                ],
            },
            {
                "name": "system.integration.manageESB",
                "description": "Manage Enterprise Service Bus (ESB) integration patterns",
                "parameters": "esbEndpoint:str:required, serviceConfig:dict:required, routingRules:list:required, transformationPipeline:list:optional, errorHandling:dict:optional, monitoring:bool:optional:true",
                "returns": "dict - ESB integration status with service orchestration results",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "ESB Management",
                "patterns": [
                    "esb_integration",
                    "service_orchestration",
                    "enterprise_integration",
                    "message_routing",
                ],
            },
            {
                "name": "system.integration.handleFileWatcher",
                "description": "Handle file system watching for external data integration",
                "parameters": "watchDirectory:str:required, filePattern:str:optional:*, events:list:optional, processingScript:str:required, bufferTime:int:optional:1000, recursiveWatch:bool:optional:false",
                "returns": "dict - File watcher status with processing results",
                "scope": ["Gateway"],
                "category": "File Watching",
                "patterns": [
                    "file_watcher",
                    "file_system_monitoring",
                    "automated_processing",
                    "data_ingestion",
                ],
            },
            {
                "name": "system.integration.configureCron",
                "description": "Configure cron-style scheduling for external system integrations",
                "parameters": "cronExpression:str:required, taskName:str:required, integrationScript:str:required, timezone:str:optional:UTC, enabled:bool:optional:true, errorNotification:bool:optional:true",
                "returns": "dict - Cron configuration with scheduling status",
                "scope": ["Gateway"],
                "category": "Task Scheduling",
                "patterns": [
                    "cron_scheduler",
                    "task_automation",
                    "scheduled_integration",
                    "batch_processing",
                ],
            },
            {
                "name": "system.integration.manageCache",
                "description": "Manage distributed cache for external system integration performance",
                "parameters": "cacheProvider:str:required, configuration:dict:required, expiration:dict:optional, evictionPolicy:str:optional:lru, clustering:bool:optional:false, persistence:bool:optional:false",
                "returns": "dict - Cache configuration with performance metrics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Cache Management",
                "patterns": [
                    "distributed_cache",
                    "performance_optimization",
                    "data_caching",
                    "integration_acceleration",
                ],
            },
            {
                "name": "system.integration.orchestrateWorkflow",
                "description": "Orchestrate complex workflows across multiple external systems",
                "parameters": "workflowDefinition:dict:required, participants:list:required, executionStrategy:str:optional:sequential, errorHandling:dict:optional, compensation:dict:optional, monitoring:bool:optional:true",
                "returns": "dict - Workflow orchestration status with execution results",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Workflow Orchestration",
                "patterns": [
                    "workflow_orchestration",
                    "process_automation",
                    "system_coordination",
                    "business_process",
                ],
            },
        ]
    )

    return functions


def get_task_13_metadata() -> dict[str, Any]:
    """Get metadata about Task 13: Integration & External Systems Functions."""
    return {
        "task_number": 13,
        "task_name": "Integration & External Systems Functions",
        "description": "Comprehensive external system integration functions for REST APIs, network protocols, messaging, and enterprise connectivity",
        "total_functions": 30,
        "categories": ["REST API", "Network Communication", "Message Queuing"],
        "contexts": ["Gateway", "Vision Client", "Perspective Session"],
        "dependencies": [
            "Task 1: Tag System",
            "Task 2: Database System",
            "Task 9: Security System",
        ],
        "priority": "HIGH",
        "estimated_completion": "Week 15",
    }


if __name__ == "__main__":
    functions = get_integration_external_functions()
    metadata = get_task_13_metadata()
    print(f"Task 13: {metadata['task_name']}")
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

    print("\n🎯 Integration Focus Areas:")
    print("   • REST API & Web Services: Modern API integration")
    print("   • Network Protocols: TCP, UDP, FTP, SFTP, SMTP, SNMP")
    print("   • Message Queuing: MQTT, JMS, Kafka, RabbitMQ, WebSockets")
    print("   • Enterprise Integration: ESB, Workflow Orchestration, Caching")
