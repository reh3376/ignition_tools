#!/usr/bin/env python3
"""Populate Task 5: Device Communication Expansion
Load comprehensive device communication functions into Neo4j graph database.

This script populates the Neo4j database with Task 5 functions covering:
- OPC Classic Operations (8 functions)
- OPC-UA Operations (10 functions)
- Device Management Operations (8 functions)
- BACnet Protocol Operations (6 functions)
- DNP3 Protocol Operations (5 functions)

Total: 37 functions for industrial device communication protocols
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.ignition.graph.client import IgnitionGraphClient
    from src.ignition.graph.tasks.task_5_device_communication import (
        get_device_communication_functions,
    )

    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    sys.exit(1)


def populate_task_5_functions() -> Any:
    """Populate Neo4j database with Task 5: Device Communication functions.

    Returns:
        tuple: (success_count, total_count, relationships_created)
    """
    print("🚀 Starting Task 5: Device Communication Expansion population...")

    # Initialize Neo4j connection
    try:
        client = IgnitionGraphClient()
        client.connect()
        print("✅ Connected to Neo4j database")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        return 0, 0, 0

    # Get Task 5 functions
    functions = get_device_communication_functions()
    print(f"📊 Found {len(functions)} device communication functions to populate")

    success_count = 0
    total_count = len(functions)
    relationships_created = 0

    # Function categories for Task 5
    categories = {
        "OPC Classic": [
            "system.opc.writeValues",
            "system.opc.readValues",
            "system.opc.browseSimple",
            "system.opc.getServerState",
            "system.opc.setServerEnabled",
            "system.opc.getServerInfo",
            "system.opc.subscribeToItems",
            "system.opc.unsubscribeFromItems",
        ],
        "OPC-UA": [
            "system.opcua.readValues",
            "system.opcua.writeValues",
            "system.opcua.browseNodes",
            "system.opcua.getConnectionInfo",
            "system.opcua.addConnection",
            "system.opcua.removeConnection",
            "system.opcua.callMethod",
            "system.opcua.createSubscription",
            "system.opcua.deleteSubscription",
            "system.opcua.getServerCertificate",
        ],
        "Device Management": [
            "system.device.addDevice",
            "system.device.removeDevice",
            "system.device.setDeviceEnabled",
            "system.device.getDeviceConfiguration",
            "system.device.setDeviceConfiguration",
            "system.device.getDeviceStatus",
            "system.device.restartDevice",
            "system.device.listDevices",
        ],
        "BACnet Protocol": [
            "system.bacnet.synchronizeTime",
            "system.bacnet.readProperty",
            "system.bacnet.writeProperty",
            "system.bacnet.releaseProperty",
            "system.bacnet.discoverDevices",
            "system.bacnet.readObjectList",
        ],
        "DNP3 Protocol": [
            "system.dnp3.request",
            "system.dnp3.sendDataSet",
            "system.dnp3.readClass0Data",
            "system.dnp3.readEventData",
            "system.dnp3.performIntegrityPoll",
        ],
    }

    print("\n📋 Task 5 Categories:")
    for category, funcs in categories.items():
        print(f"   • {category}: {len(funcs)} functions")

    # Process each function
    for i, func_data in enumerate(functions, 1):
        func_name = func_data["name"]
        print(f"\n[{i:2d}/{total_count}] Processing: {func_name}")

        try:
            # Create function with relationships using direct query execution
            query = """
            // Create the function node
            MERGE (f:Function {name: $name})
            SET f.description = $description,
                f.returns_type = $returns_type,
                f.returns_description = $returns_description,
                f.category = $category,
                f.task = 'Task 5: Device Communication'

            // Create parameter relationships
            WITH f
            UNWIND $parameters AS param
            MERGE (p:Parameter {name: param.name + "_" + $name})
            SET p.parameter_name = param.name,
                p.function_name = $name,
                p.type = param.type,
                p.description = param.description,
                p.required = param.required,
                p.default_value = coalesce(param.default_value, param.default)
            MERGE (f)-[:HAS_PARAMETER]->(p)

            // Create pattern relationships
            WITH f
            UNWIND $patterns AS pattern_name
            MERGE (pat:Pattern {name: pattern_name})
            MERGE (f)-[:MATCHES_PATTERN]->(pat)

            // Create scope relationships
            WITH f
            UNWIND $scopes AS scope_name
            MERGE (s:Scope {name: scope_name})
            MERGE (f)-[:AVAILABLE_IN]->(s)

            RETURN f.name as function_name
            """

            params = {
                "name": func_data["name"],
                "description": func_data["description"],
                "returns_type": func_data["returns"]["type"],
                "returns_description": func_data["returns"]["description"],
                "category": func_data["category"],
                "parameters": func_data["parameters"],
                "patterns": func_data["patterns"],
                "scopes": func_data["scope"],
            }

            result = client.execute_query(query, params)
            if result:
                success_count += 1
                print(f"   ✅ Successfully added: {func_name}")

                # Count relationships (parameters + patterns + scope)
                param_count = len(func_data.get("parameters", []))
                pattern_count = len(func_data.get("patterns", []))
                scope_count = len(func_data.get("scope", []))
                func_relationships = param_count + pattern_count + scope_count + 1  # +1 for category
                relationships_created += func_relationships

                print(f"   📊 Created {func_relationships} relationships")
            else:
                print(f"   ❌ Failed to add: {func_name}")

        except Exception as e:
            print(f"   ❌ Error processing {func_name}: {e}")

    # Create Task 5 task node for tracking
    print("\n📋 Creating Task 5 master node...")
    try:
        task_query = """
        MERGE (t:Task {task_id: 'task_5'})
        SET t.name = 'Device Communication Expansion',
            t.description = 'Advanced device communication protocols including OPC, OPC-UA, BACnet, and DNP3',
            t.priority = 'HIGH',
            t.estimated_functions = $function_count,
            t.completion_week = 'Week 5-6',
            t.status = 'COMPLETED'
        RETURN t.name as task_name
        """

        task_result = client.execute_query(task_query, {"function_count": len(functions)})
        if task_result:
            print("   ✅ Created Task 5 master node")
            relationships_created += 1

    except Exception as e:
        print(f"   ❌ Error creating Task 5 node: {e}")

    # Close connection
    client.disconnect()

    # Final summary
    print("\n" + "=" * 60)
    print("📊 TASK 5 POPULATION SUMMARY")
    print("=" * 60)
    print(f"✅ Functions Added: {success_count}/{total_count} ({success_count / total_count * 100:.1f}%)")
    print(f"🔗 Relationships Created: {relationships_created}")
    print(f"📁 Categories: {len(categories)}")
    print(f"🎯 Task Status: {'COMPLETED' if success_count == total_count else 'PARTIAL'}")

    if success_count < total_count:
        print(f"⚠️  {total_count - success_count} functions failed to populate")

    print("=" * 60)

    return success_count, total_count, relationships_created


def verify_task_5_population() -> bool:
    """Verify Task 5 population by checking function counts and relationships."""
    print("\n🔍 Verifying Task 5 population...")

    try:
        client = IgnitionGraphClient()
        client.connect()

        # Check function count
        query = """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.opc.' OR
              f.name STARTS WITH 'system.opcua.' OR
              f.name STARTS WITH 'system.device.' OR
              f.name STARTS WITH 'system.bacnet.' OR
              f.name STARTS WITH 'system.dnp3.'
        RETURN count(f) as function_count
        """

        result = client.execute_query(query)
        if result:
            function_count = result[0]["function_count"]
            print(f"   📊 Found {function_count} Task 5 functions in database")

        # Check Task 5 node
        task_query = """
        MATCH (t:Task {task_id: 'task_5'})
        RETURN t.name as name, t.priority as priority
        """

        task_result = client.execute_query(task_query)
        if task_result:
            task_info = task_result[0]
            print(f"   📋 Task 5 Node: {task_info['name']} (Priority: {task_info['priority']})")

        client.disconnect()
        return True

    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Task 5: Device Communication Expansion - Neo4j Population")
    print("=" * 60)

    # Populate Task 5 functions
    success_count, total_count, relationships_created = populate_task_5_functions()

    if success_count > 0:
        # Verify population
        verify_task_5_population()

        print("\n🎉 Task 5 population completed!")
        print(f"   📊 {success_count}/{total_count} functions loaded")
        print(f"   🔗 {relationships_created} relationships created")

        if success_count == total_count:
            print("   ✅ All Task 5 functions successfully populated!")
        else:
            print(f"   ⚠️  {total_count - success_count} functions need attention")
    else:
        print("\n❌ Task 5 population failed - no functions were loaded")
        sys.exit(1)
