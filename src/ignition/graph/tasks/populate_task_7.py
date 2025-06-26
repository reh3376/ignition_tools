#!/usr/bin/env python3
"""Populate Task 7: Alarm System Expansion.

This script loads comprehensive alarm system functions into the Neo4j graph database.
Task 7 focuses on alarm management, monitoring, and notification operations.

Total Functions: 28 functions
Categories: Alarm Operations
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2)
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.tasks.task_7_alarm_system import get_alarm_system_functions


def populate_task_7_alarm_system() -> bool:
    """Populate Task 7: Alarm System Expansion functions into Neo4j database.

    This function:
    1. Connects to Neo4j database
    2. Loads 28 alarm system functions
    3. Creates comprehensive relationships for alarm operations
    4. Validates successful population
    """
    print("🚀 Starting Task 7: Alarm System Expansion Population")
    print("=" * 60)

    # Initialize client
    client = IgnitionGraphClient()

    try:
        # Connect to database
        print("📡 Connecting to Neo4j database...")
        client.connect()
        print("✅ Connected successfully!")

        # Get alarm system functions
        print("\n📚 Loading alarm system functions...")
        alarm_functions = get_alarm_system_functions()
        print(f"✅ Loaded {len(alarm_functions)} alarm system functions")

        # Validate function structure
        print("\n🔍 Validating function structure...")
        total_parameters = 0
        total_patterns = 0
        categories = set()
        scopes = set()

        for func in alarm_functions:
            # Validate required fields
            required_fields = [
                "name",
                "description",
                "parameters",
                "returns",
                "scope",
                "category",
                "patterns",
            ]
            missing_fields = [field for field in required_fields if field not in func]

            if missing_fields:
                print(f"❌ Function {func.get('name', 'UNKNOWN')} missing fields: {missing_fields}")
                continue

            # Count metrics
            total_parameters += len(func["parameters"])
            total_patterns += len(func["patterns"])
            categories.add(func["category"])
            scopes.update(func["scope"])

            print(f"✅ {func['name']} - {len(func['parameters'])} params, {len(func['patterns'])} patterns")

        print("\n📊 Function Metrics:")
        print(f"   • Total Functions: {len(alarm_functions)}")
        print(f"   • Total Parameters: {total_parameters}")
        print(f"   • Total Patterns: {total_patterns}")
        print(f"   • Categories: {sorted(categories)}")
        print(f"   • Scopes: {sorted(scopes)}")

        # Load functions into database
        print(f"\n💾 Loading {len(alarm_functions)} functions into Neo4j...")
        successful_loads = 0
        failed_loads = 0

        for i, func_data in enumerate(alarm_functions, 1):
            try:
                print(f"   [{i:2d}/{len(alarm_functions)}] Loading {func_data['name']}...")

                # Create function with relationships using direct query execution
                query = """
                // Create the function node
                MERGE (f:Function {name: $name})
                SET f.description = $description,
                    f.returns_type = $returns_type,
                    f.returns_description = $returns_description,
                    f.category = $category,
                    f.task = 'Task 7: Alarm System'

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
                    successful_loads += 1
                    print(f"      ✅ Successfully loaded {func_data['name']}")
                else:
                    failed_loads += 1
                    print(f"      ❌ Failed to load {func_data['name']}")

            except Exception as e:
                failed_loads += 1
                print(f"      ❌ Error loading {func_data['name']}: {e!s}")

        print("\n📈 Loading Results:")
        print(f"   • Successful: {successful_loads}")
        print(f"   • Failed: {failed_loads}")
        print(f"   • Success Rate: {(successful_loads / len(alarm_functions) * 100):.1f}%")

        # Validate database state
        print("\n🔍 Validating database state...")

        # Count total functions
        result = client.execute_query("MATCH (f:Function) RETURN count(f) as total")
        total_functions = result[0]["total"] if result else 0

        # Count Task 7 functions
        result = client.execute_query(
            "MATCH (f:Function) WHERE f.task = 'Task 7: Alarm System' RETURN count(f) as task7_count"
        )
        task7_functions = result[0]["task7_count"] if result else 0

        # Count relationships
        result = client.execute_query("MATCH ()-[r]->() RETURN count(r) as total_relationships")
        total_relationships = result[0]["total_relationships"] if result else 0

        # Count alarm-specific relationships
        result = client.execute_query(
            """
            MATCH (f:Function)-[r]->(n)
            WHERE f.task = 'Task 7: Alarm System'
            RETURN count(r) as task7_relationships
        """
        )
        task7_relationships = result[0]["task7_relationships"] if result else 0

        print(f"   • Total Functions in DB: {total_functions}")
        print(f"   • Task 7 Functions: {task7_functions}")
        print(f"   • Total Relationships: {total_relationships}")
        print(f"   • Task 7 Relationships: {task7_relationships}")

        # Expected relationships calculation
        expected_relationships = total_parameters + total_patterns + len(scopes) * len(alarm_functions)
        print(f"   • Expected Task 7 Relationships: ~{expected_relationships}")

        if task7_functions == len(alarm_functions):
            print("✅ All alarm functions loaded successfully!")
        else:
            print(f"⚠️  Expected {len(alarm_functions)} functions, found {task7_functions}")

        print("\n🎉 Task 7: Alarm System Expansion Population Complete!")
        print(f"   • Successfully loaded {task7_functions} alarm functions")
        print(f"   • Created {task7_relationships} relationships")
        print(f"   • Database now contains {total_functions} total functions")

        return True

    except Exception as e:
        print(f"❌ Error during population: {e!s}")
        return False

    finally:
        # Close connection
        try:
            client.close()
            print("📪 Database connection closed.")
        except Exception:
            pass


def main() -> None:
    """Main entry point for Task 7 population."""
    print("Task 7: Alarm System Expansion - Neo4j Population")
    print("=" * 55)

    success = populate_task_7_alarm_system()

    if success:
        print("\n🎯 Ready for Task 7 validation!")
        print("Run: python scripts/testing/automated_task_validation.py --task 7")
        sys.exit(0)
    else:
        print("\n❌ Population failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
