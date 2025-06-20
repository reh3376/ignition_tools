"""Population script for Task 4: Perspective System Expansion.

This script loads Task 4 Perspective system functions into the Neo4j graph database.
Covers session management, navigation, messaging, components, and device operations.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

from src.ignition.graph.client import IgnitionGraphClient as Neo4jManager
from src.ignition.graph.tasks.task_4_perspective_system import (
    get_task_4_perspective_functions,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_task_4_functions():
    """Populate Neo4j database with Task 4 Perspective system functions."""
    # Initialize Neo4j connection
    db_manager = Neo4jManager()

    try:
        # Test connection
        if not db_manager.connect():
            logger.error("Failed to connect to Neo4j database")
            return False

        logger.info("Connected to Neo4j database successfully")

        # Clear existing Perspective functions if any
        logger.info("Clearing existing Perspective functions...")
        clear_query = """
        MATCH (f:Function)
        WHERE f.category = 'Perspective System'
        DETACH DELETE f
        """

        result = db_manager.execute_query(clear_query)

        # Also clear any orphaned parameters
        clear_params_query = """
        MATCH (p:Parameter)
        WHERE NOT (p)<-[:HAS_PARAMETER]-()
        DETACH DELETE p
        """
        db_manager.execute_query(clear_params_query)

        logger.info("Cleared existing Perspective functions and orphaned parameters")

        # Get all Perspective system functions
        functions = get_task_4_perspective_functions()
        logger.info(f"Loading {len(functions)} Perspective system functions...")

        # Create functions and relationships
        for func in functions:
            logger.info(f"Creating function: {func['name']}")

            # Create function node
            create_func_query = """
            CREATE (f:Function {
                name: $name,
                category: $category,
                subcategory: $subcategory,
                description: $description,
                returns_type: $returns_type,
                returns_description: $returns_description,
                code_example: $code_example,
                task: 'Task 4',
                priority: 'HIGH',
                complexity: 4,
                created_date: datetime()
            })
            RETURN f
            """

            db_manager.execute_query(
                create_func_query,
                {
                    "name": func["name"],
                    "category": func["category"],
                    "subcategory": func["subcategory"],
                    "description": func["description"],
                    "returns_type": func["returns"]["type"],
                    "returns_description": func["returns"]["description"],
                    "code_example": func["code_example"],
                },
            )

            # Create parameters
            for i, param in enumerate(func["parameters"]):
                create_param_query = """
                MATCH (f:Function {name: $func_name})
                MERGE (p:Parameter {name: $param_name})
                SET p.type = $param_type,
                    p.description = $param_description,
                    p.optional = $optional,
                    p.function_param_id = $function_param_id
                CREATE (f)-[:HAS_PARAMETER {order: $order}]->(p)
                """

                # Create unique identifier for parameter within function
                function_param_id = f"{func['name']}:{param['name']}"

                db_manager.execute_query(
                    create_param_query,
                    {
                        "func_name": func["name"],
                        "param_name": param["name"],
                        "param_type": param["type"],
                        "param_description": param["description"],
                        "optional": param.get("optional", False),
                        "function_param_id": function_param_id,
                        "order": i,
                    },
                )

            # Create scope relationships
            for scope in func["scope"]:
                create_scope_query = """
                MATCH (f:Function {name: $func_name})
                MERGE (s:Scope {name: $scope_name})
                CREATE (f)-[:AVAILABLE_IN]->(s)
                """

                db_manager.execute_query(create_scope_query, {"func_name": func["name"], "scope_name": scope})

            # Create common pattern relationships
            for pattern in func["common_patterns"]:
                create_pattern_query = """
                MATCH (f:Function {name: $func_name})
                MERGE (p:Pattern {name: $pattern_name})
                CREATE (f)-[:IMPLEMENTS_PATTERN]->(p)
                """

                db_manager.execute_query(
                    create_pattern_query,
                    {"func_name": func["name"], "pattern_name": pattern},
                )

        # Create category relationships
        logger.info("Creating category relationships...")
        category_query = """
        MATCH (f:Function)
        WHERE f.category = 'Perspective System'
        WITH f.category as category, collect(f) as functions
        MERGE (c:Category {name: category})
        FOREACH (func in functions |
            CREATE (c)-[:CONTAINS]->(func)
        )
        """

        db_manager.execute_query(category_query)

        # Create subcategory relationships
        subcategory_query = """
        MATCH (f:Function)
        WHERE f.category = 'Perspective System'
        WITH f.subcategory as subcategory, collect(f) as functions
        MERGE (sc:Subcategory {name: subcategory})
        FOREACH (func in functions |
            CREATE (sc)-[:GROUPS]->(func)
        )
        """

        db_manager.execute_query(subcategory_query)

        # Create task relationships
        task_query = """
        MATCH (f:Function)
        WHERE f.category = 'Perspective System'
        MERGE (t:Task {name: 'Task 4', description: 'Perspective System Expansion', priority: 'HIGH'})
        CREATE (t)-[:INCLUDES]->(f)
        """

        db_manager.execute_query(task_query)

        # Verify population
        verify_query = """
        MATCH (f:Function)
        WHERE f.category = 'Perspective System'
        RETURN count(f) as function_count
        """

        result = db_manager.execute_query(verify_query)
        function_count = result[0]["function_count"]

        logger.info(f"Successfully populated {function_count} Perspective system functions")

        # Get relationship counts
        rel_query = """
        MATCH (f:Function)-[r]->()
        WHERE f.category = 'Perspective System'
        RETURN type(r) as relationship_type, count(r) as count
        ORDER BY count DESC
        """

        relationships = db_manager.execute_query(rel_query)
        logger.info("Relationship summary:")
        for rel in relationships:
            logger.info(f"  {rel['relationship_type']}: {rel['count']}")

        return True

    except Exception as e:
        logger.error(f"Error populating database: {e!s}")
        return False

    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    print("Task 4: Perspective System Population")
    print("=" * 50)

    success = populate_task_4_functions()

    if success:
        print("\n✅ Task 4 Perspective system functions populated successfully!")
        print("\nPerspective System Functions Added:")
        print("- Session Management: 6 functions")
        print("  • Session Info & Properties: 3 functions")
        print("  • Device Interaction: 1 function")
        print("  • Authentication & Navigation: 2 functions")
        print("- Navigation: 4 functions")
        print("  • Page Navigation: 1 function")
        print("  • Popup Management: 2 functions")
        print("  • Print Operations: 1 function")
        print("- Messaging: 4 functions")
        print("  • Message Sending & Broadcasting: 1 function")
        print("  • Subscription Management: 2 functions")
        print("  • Message Origin Detection: 1 function")
        print("- Components: 4 functions")
        print("  • Table Operations: 2 functions")
        print("  • File Operations: 1 function")
        print("  • Component Refresh: 1 function")
        print("- Device Operations: 4 functions")
        print("  • Mobile Integration: 1 function")
        print("  • File & Camera Access: 2 functions")
        print("  • Responsive Design: 1 function")
        print()
        print("🎯 Total: 22 comprehensive Perspective functions")
        print("📱 Focus: Modern web-based HMI development")
        print("🔧 All functions scoped to Perspective Session")
    else:
        print("\n❌ Task 4 population failed!")
        print("Check the logs above for specific error details.")
