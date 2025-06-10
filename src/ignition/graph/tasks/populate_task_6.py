#!/usr/bin/env python3
"""Populate Task 6: Utility System Expansion

This script loads comprehensive utility system functions into the Neo4j graph database.
Task 6 focuses on utility operations, system management, and administrative functions.

Total Functions: 50 functions
Categories: General Utilities, Logging, Project Management, Security, Performance, etc.
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Core systems (Tasks 1-5)
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.tasks.task_6_utility_system import get_utility_system_functions


def populate_task_6_utility_system():
    """Populate Task 6: Utility System Expansion functions into Neo4j database.

    This function:
    1. Connects to Neo4j database
    2. Loads 50 utility system functions
    3. Creates comprehensive relationships for utility operations
    4. Validates successful population
    """
    print("🚀 Starting Task 6: Utility System Expansion Population")
    print("=" * 60)

    # Initialize client
    client = IgnitionGraphClient()

    try:
        # Connect to database
        print("📡 Connecting to Neo4j database...")
        client.connect()
        print("✅ Connected successfully!")

        # Get Task 6 functions
        print("\n📋 Loading Task 6 utility system functions...")
        functions = get_utility_system_functions()

        print(f"📊 Total functions to populate: {len(functions)}")

        # Function categories for Task 6
        categories = {
            "General Utilities": [
                "system.util.modifyTranslation",
                "system.util.translate",
                "system.util.getLocale",
                "system.util.setLocale",
                "system.util.getTimezone",
                "system.util.setTimezone",
                "system.util.threadDump",
                "system.util.version",
            ],
            "Logging Operations": [
                "system.util.getLoggerLevel",
                "system.util.setLoggerLevel",
                "system.util.configureLogging",
            ],
            "Project Management": [
                "system.util.retarget",
                "system.util.restart",
                "system.util.shutdown",
            ],
            "Security Operations": [
                "system.util.getUserRoles",
                "system.util.validateUser",
            ],
            "Performance Monitoring": [
                "system.util.getMemoryUsage",
                "system.util.getSystemInfo",
                "system.util.getSessionInfo",
                "system.util.getPerformanceMetrics",
            ],
            "Network Operations": [
                "system.util.getNetworkInfo",
                "system.util.testConnection",
            ],
            "System Configuration": [
                "system.util.getProperty",
                "system.util.setProperty",
            ],
            "File Operations": [
                "system.util.copyFile",
                "system.util.moveFile",
                "system.util.deleteFile",
                "system.util.listFiles",
            ],
            "Date/Time Operations": [
                "system.util.formatDate",
                "system.util.parseDate",
                "system.util.getCurrentTime",
            ],
            "Data Encoding": ["system.util.encodeBase64", "system.util.decodeBase64"],
            "Data Generation": ["system.util.generateUUID"],
            "Data Security": ["system.util.hashData"],
            "Communication": ["system.util.sendEmail"],
            "User Interface": ["system.util.showNotification"],
            "System Management": [
                "system.util.exportSystemConfiguration",
                "system.util.importSystemConfiguration",
            ],
            "System Monitoring": ["system.util.getSystemHealth"],
            "System Maintenance": ["system.util.cleanupTempFiles"],
            "Task Scheduling": [
                "system.util.scheduleTask",
                "system.util.cancelScheduledTask",
                "system.util.getScheduledTasks",
            ],
            "Data Processing": [
                "system.util.compressData",
                "system.util.decompressData",
            ],
            "License Management": ["system.util.validateLicense"],
            "Event Management": ["system.util.getSystemEvents"],
            "Backup Management": [
                "system.util.createBackup",
                "system.util.restoreBackup",
            ],
        }

        print("\n📋 Task 6 Categories:")
        for category, funcs in categories.items():
            print(f"   • {category}: {len(funcs)} functions")

        # Populate functions
        print(f"\n🔄 Populating {len(functions)} utility functions...")

        success_count = 0
        error_count = 0

        for i, func_data in enumerate(functions, 1):
            try:
                func_name = func_data["name"]
                print(f"   [{i:2d}/{len(functions)}] Adding {func_name}...")

                # Create function node with comprehensive metadata
                create_query = """
                MERGE (f:Function {name: $name})
                SET f.description = $description,
                    f.category = $category,
                    f.return_type = $return_type,
                    f.return_description = $return_description,
                    f.task_id = 6,
                    f.created_date = datetime(),
                    f.patterns = $patterns
                """

                # Execute function creation
                returns_data = func_data["returns"]
                client.execute_query(
                    create_query,
                    {
                        "name": func_name,
                        "description": func_data["description"],
                        "category": func_data["category"],
                        "return_type": returns_data["type"],
                        "return_description": returns_data["description"],
                        "patterns": func_data.get("patterns", []),
                    },
                )

                # Create scope relationships
                for scope in func_data["scope"]:
                    scope_query = """
                    MATCH (f:Function {name: $name})
                    MERGE (s:Scope {name: $scope})
                    MERGE (f)-[:AVAILABLE_IN]->(s)
                    """
                    client.execute_query(
                        scope_query, {"name": func_name, "scope": scope}
                    )

                # Create parameter relationships
                for param in func_data["parameters"]:
                    param_query = """
                    MATCH (f:Function {name: $name})
                    MERGE (p:Parameter {
                        name: $param_name,
                        type: $param_type,
                        description: $param_description,
                        required: $param_required
                    })
                    MERGE (f)-[:HAS_PARAMETER]->(p)
                    """
                    client.execute_query(
                        param_query,
                        {
                            "name": func_name,
                            "param_name": param["name"],
                            "param_type": param["type"],
                            "param_description": param["description"],
                            "param_required": param["required"],
                        },
                    )

                # Create pattern relationships
                for pattern in func_data.get("patterns", []):
                    pattern_query = """
                    MATCH (f:Function {name: $name})
                    MERGE (pat:Pattern {name: $pattern})
                    MERGE (f)-[:IMPLEMENTS]->(pat)
                    """
                    client.execute_query(
                        pattern_query, {"name": func_name, "pattern": pattern}
                    )

                success_count += 1

            except Exception as e:
                print(f"❌ Error adding {func_data.get('name', 'unknown')}: {e}")
                error_count += 1
                continue

        # Create Task 6 completion node
        print("\n📋 Creating Task 6 completion marker...")
        task_query = """
        MERGE (t:Task {id: 6})
        SET t.name = "Utility System Expansion",
            t.description = "Comprehensive utility functions and system management operations",
            t.status = "COMPLETED",
            t.completion_date = datetime(),
            t.function_count = $function_count,
            t.priority = "MEDIUM"
        """
        client.execute_query(task_query, {"function_count": success_count})

        # Link functions to task
        task_link_query = """
        MATCH (f:Function)
        WHERE f.task_id = 6
        MATCH (t:Task {id: 6})
        MERGE (f)-[:BELONGS_TO]->(t)
        """
        client.execute_query(task_link_query)

        # Display results
        print("\n📊 Task 6 Population Results:")
        print(f"   ✅ Successfully added: {success_count} functions")
        print(f"   ❌ Errors: {error_count} functions")
        print(f"   📈 Success rate: {(success_count/len(functions)*100):.1f}%")

        if success_count == len(functions):
            print("\n🎉 **Task 6 Population COMPLETED Successfully!**")
        else:
            print(f"\n⚠️  **Task 6 Population completed with {error_count} errors**")

        # Get updated statistics
        stats_query = """
        MATCH (f:Function)
        RETURN count(f) as total_functions
        """
        result = client.execute_query(stats_query)
        total_functions = result[0]["total_functions"]

        print("\n📊 **Updated Database Statistics:**")
        print(f"   📈 Total functions: {total_functions}")
        print(
            f"   🎯 Completion: {(total_functions/400)*100:.1f}% (target: 400 functions)"
        )

        return success_count == len(functions)

    except Exception as e:
        print(f"❌ Critical error during population: {e}")
        return False

    finally:
        client.disconnect()
        print("\n📡 Disconnected from Neo4j database")


if __name__ == "__main__":
    print("🚀 **Task 6: Utility System Expansion - Database Population**")
    print("=" * 70)

    # Check if Neo4j is running
    print("🔍 Checking Neo4j connection...")

    success = populate_task_6_utility_system()

    if success:
        print("\n✅ **TASK 6 POPULATION SUCCESSFUL**")
        print("📋 Next: Run validation tests")
        print(
            "🔧 Command: python scripts/testing/automated_task_validation.py --task 6"
        )
    else:
        print("\n❌ **TASK 6 POPULATION FAILED**")
        print("🔧 Check error messages above and retry")

    print("=" * 70)
