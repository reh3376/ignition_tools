#!/usr/bin/env python3
"""Population script for Task 10: File & Report System Expansion.

This script loads comprehensive file operations and reporting functions
into the Neo4j graph database for the Ignition SCADA system.

Task 10 includes:
- File System Operations (8 functions)
- Report Generation & Distribution (9 functions)
- Data Processing & Analysis (8 functions)

Total: 25 functions
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.tasks.task_10_file_report_system import (
    get_file_report_system_functions,
    get_task_10_metadata,
)


def populate_task_10_functions():
    """Populate Task 10 file and report system functions in the graph database."""
    print("🚀 Starting Task 10: File & Report System Expansion")
    print("=" * 60)

    # Initialize graph client
    client = IgnitionGraphClient()

    try:
        # Connect to Neo4j
        print("📡 Connecting to Neo4j database...")
        client.connect()

        # Get function definitions
        print("📋 Loading function definitions...")
        file_report_functions = get_file_report_system_functions()
        task_metadata = get_task_10_metadata()

        print("📊 Task 10 Summary:")
        print(f"   • Task: {task_metadata['task_name']}")
        print(f"   • Functions: {len(file_report_functions)}")
        print(f"   • Categories: {', '.join(task_metadata['categories'])}")
        print(f"   • Priority: {task_metadata['priority']}")
        print()

        # Validate database connection
        print("🔍 Validating database connection...")
        pre_count_result = client.execute_query(
            "MATCH (f:Function) RETURN count(f) as total"
        )
        pre_count = pre_count_result[0]["total"] if pre_count_result else 0
        print(f"   • Current functions in database: {pre_count}")

        # Load functions into database
        print("📤 Loading functions into database...")
        successful_loads = 0
        failed_loads = 0

        for i, func_data in enumerate(file_report_functions, 1):
            try:
                print(f"   📦 Loading function {i:2d}/25: {func_data['name']}")

                # Clean parameters to handle Neo4j constraints
                cleaned_parameters = []
                for param in func_data["parameters"]:
                    cleaned_param = param.copy()
                    # Convert empty dict defaults to string representation
                    if "default" in cleaned_param and cleaned_param["default"] == {}:
                        cleaned_param["default"] = "{}"
                    elif "default" in cleaned_param and isinstance(
                        cleaned_param["default"], dict
                    ):
                        cleaned_param["default"] = str(cleaned_param["default"])
                    cleaned_parameters.append(cleaned_param)

                # Create function with relationships using direct query execution
                query = """
                // Create the function node
                MERGE (f:Function {name: $name})
                SET f.description = $description,
                    f.returns_type = $returns_type,
                    f.returns_description = $returns_description,
                    f.category = $category,
                    f.task = 'Task 10: File & Report System'

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
                    "parameters": cleaned_parameters,
                    "patterns": func_data["patterns"],
                    "scopes": func_data["scope"],
                }

                result = client.execute_query(query, params)
                if result:
                    successful_loads += 1
                else:
                    failed_loads += 1

            except Exception as e:
                print(f"   ❌ Failed to load {func_data['name']}: {e}")
                failed_loads += 1

        print()
        print("📊 Loading Results:")
        print(f"   • Total Functions: {len(file_report_functions)}")
        print(f"   • Successful: {successful_loads}")
        print(f"   • Failed: {failed_loads}")
        print(
            f"   • Success Rate: {(successful_loads/len(file_report_functions)*100):.1f}%"
        )

        # Validate database state
        print()
        print("🔍 Validating database state...")
        post_count_result = client.execute_query(
            "MATCH (f:Function) RETURN count(f) as total"
        )
        post_count = post_count_result[0]["total"] if post_count_result else 0
        functions_added = post_count - pre_count

        print(f"   • Functions before: {pre_count}")
        print(f"   • Functions after: {post_count}")
        print(f"   • Functions added: {functions_added}")

        # Verify specific Task 10 functions
        print()
        print("🔍 Verifying Task 10 functions...")

        # Check key functions from each category
        key_functions = [
            "system.file.readFileContent",
            "system.file.writeFileContent",
            "system.report.generateDataReport",
            "system.report.scheduleReport",
            "system.file.parseCSVFile",
            "system.file.parseLogFile",
        ]

        for func_name in key_functions:
            result = client.execute_query(
                "MATCH (f:Function {name: $name}) RETURN f.name as name",
                {"name": func_name},
            )
            if result:
                print(f"   ✅ {func_name}")
            else:
                print(f"   ❌ Missing: {func_name}")

        # Get category distribution
        print()
        print("📊 Function Category Distribution:")
        category_query = """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.file.' OR f.name STARTS WITH 'system.report.'
        RETURN f.category as category, count(f) as count
        ORDER BY count DESC
        """

        category_results = client.execute_query(category_query)
        for result in category_results:
            print(f"   • {result['category']}: {result['count']} functions")

        # Get total relationships
        print()
        print("🔗 Relationship Analysis:")
        rel_query = "MATCH ()-[r]->() RETURN count(r) as total_relationships"
        rel_result = client.execute_query(rel_query)
        total_rels = rel_result[0]["total_relationships"] if rel_result else 0
        print(f"   • Total relationships: {total_rels}")

        # Calculate completion percentage
        target_functions = 400  # Estimated target
        completion_percentage = (post_count / target_functions) * 100
        print()
        print("🎯 Progress Update:")
        print(f"   • Current Progress: {post_count}/{target_functions}+ functions")
        print(f"   • Completion: {completion_percentage:.1f}%")
        print(
            f"   • Task 10 Status: ✅ COMPLETE ({successful_loads}/{len(file_report_functions)} functions)"
        )

        if successful_loads == len(file_report_functions):
            print(
                "\n🎉 Task 10: File & Report System Expansion - COMPLETED SUCCESSFULLY!"
            )
            print("   All 25 file and report functions loaded successfully.")
            print(
                "   Database now includes comprehensive file operations and reporting capabilities."
            )
        else:
            print(f"\n⚠️  Task 10 completed with {failed_loads} failures.")
            print("   Some functions may need manual review.")

    except Exception as e:
        print(f"❌ Error during Task 10 population: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\n🔚 Closing database connection...")
        client.disconnect()
        print("Task 10 population script completed.")


if __name__ == "__main__":
    populate_task_10_functions()
