#!/usr/bin/env python3
"""Populate Task 8: Print System Expansion.

This script loads comprehensive print system functions into the Neo4j graph database.
Task 8 focuses on print operations, document management, and print job handling.

Total Functions: 18 functions
Categories: Print Operations, Print Management, Print Configuration
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2), GUI System (Task 3)
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.tasks.task_8_print_system import get_print_system_functions


def populate_task_8_print_system():
    """Populate Task 8: Print System Expansion functions into Neo4j database.

    This function:
    1. Connects to Neo4j database
    2. Loads 18 print system functions
    3. Creates comprehensive relationships for print operations
    4. Validates successful population
    """
    print("🚀 Starting Task 8: Print System Expansion Population")
    print("=" * 60)

    # Initialize client
    client = IgnitionGraphClient()

    try:
        # Connect to database
        print("📡 Connecting to Neo4j database...")
        client.connect()
        print("✅ Connected successfully!")

        # Get print system functions
        print("\n📚 Loading print system functions...")
        print_functions = get_print_system_functions()
        print(f"✅ Loaded {len(print_functions)} print system functions")

        # Validate function structure
        print("\n🔍 Validating function structure...")
        total_parameters = 0
        total_patterns = 0
        categories = set()
        scopes = set()

        for func in print_functions:
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
        print(f"   • Total Functions: {len(print_functions)}")
        print(f"   • Total Parameters: {total_parameters}")
        print(f"   • Total Patterns: {total_patterns}")
        print(f"   • Categories: {sorted(categories)}")
        print(f"   • Scopes: {sorted(scopes)}")

        # Load functions into database
        print(f"\n💾 Loading {len(print_functions)} functions into Neo4j...")
        successful_loads = 0
        failed_loads = 0

        for i, func_data in enumerate(print_functions, 1):
            try:
                print(f"   [{i:2d}/{len(print_functions)}] Loading {func_data['name']}...")

                # Create function with relationships using direct query execution
                query = """
                // Create the function node
                MERGE (f:Function {name: $name})
                SET f.description = $description,
                    f.returns_type = $returns_type,
                    f.returns_description = $returns_description,
                    f.category = $category,
                    f.task = 'Task 8: Print System'

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

                # Clean parameters to handle Neo4j constraints
                cleaned_parameters = []
                for param in func_data["parameters"]:
                    cleaned_param = param.copy()
                    # Convert empty dict defaults to string representation
                    if "default" in cleaned_param and cleaned_param["default"] == {}:
                        cleaned_param["default"] = "{}"
                    elif "default" in cleaned_param and isinstance(cleaned_param["default"], dict):
                        cleaned_param["default"] = str(cleaned_param["default"])
                    cleaned_parameters.append(cleaned_param)

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
        print(f"   • Success Rate: {(successful_loads / len(print_functions) * 100):.1f}%")

        # Validate database state
        print("\n🔍 Validating database state...")

        # Count total functions
        result = client.execute_query("MATCH (f:Function) RETURN count(f) as total")
        total_functions = result[0]["total"] if result else 0

        # Count Task 8 functions
        result = client.execute_query(
            "MATCH (f:Function) WHERE f.task = 'Task 8: Print System' RETURN count(f) as task8_count"
        )
        task8_functions = result[0]["task8_count"] if result else 0

        # Count relationships
        result = client.execute_query("MATCH ()-[r]->() RETURN count(r) as total_relationships")
        total_relationships = result[0]["total_relationships"] if result else 0

        # Count print-specific relationships
        result = client.execute_query(
            """
            MATCH (f:Function)-[r]->(n)
            WHERE f.task = 'Task 8: Print System'
            RETURN count(r) as task8_relationships
        """
        )
        task8_relationships = result[0]["task8_relationships"] if result else 0

        print(f"   • Total Functions in DB: {total_functions}")
        print(f"   • Task 8 Functions: {task8_functions}")
        print(f"   • Total Relationships: {total_relationships}")
        print(f"   • Task 8 Relationships: {task8_relationships}")

        # Expected relationships calculation
        expected_relationships = total_parameters + total_patterns + len(scopes) * len(print_functions)
        print(f"   • Expected Task 8 Relationships: ~{expected_relationships}")

        if task8_functions == len(print_functions):
            print("✅ All print functions loaded successfully!")
        else:
            print(f"⚠️  Expected {len(print_functions)} functions, found {task8_functions}")

        print("\n🎉 Task 8: Print System Expansion Population Complete!")
        print(f"   • Successfully loaded {task8_functions} print functions")
        print(f"   • Created {task8_relationships} relationships")
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


def main():
    """Main entry point for Task 8 population."""
    print("Task 8: Print System Expansion - Neo4j Population")
    print("=" * 55)

    success = populate_task_8_print_system()

    if success:
        print("\n🎯 Ready for Task 8 validation!")
        print("Run: python scripts/testing/automated_task_validation.py --task 8")
        sys.exit(0)
    else:
        print("\n❌ Population failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
