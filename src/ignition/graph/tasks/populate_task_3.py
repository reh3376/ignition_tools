#!/usr/bin/env python3
"""Task 3: GUI System Population Script.
===================================

This script populates the Neo4j graph database with Task 3 GUI system functions.
Loads comprehensive Vision Client GUI management functions.

Author: Assistant
Date: 2025-01-23
Task: 3/10 - GUI System (MEDIUM Priority)
Functions: 25 comprehensive GUI functions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

import logging

from src.ignition.graph.client import IgnitionGraphClient as Neo4jManager
from src.ignition.graph.tasks.task_3_gui_system import get_gui_system_functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_gui_system_functions():
    """Populate Neo4j database with Task 3 GUI system functions."""
    # Initialize Neo4j connection
    db_manager = Neo4jManager()

    try:
        # Test connection
        if not db_manager.connect():
            logger.error("Failed to connect to Neo4j database")
            return False

        logger.info("Connected to Neo4j database successfully")

        # Clear existing basic GUI functions
        logger.info("Clearing existing basic GUI functions...")
        clear_query = """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.gui.'
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

        logger.info("Cleared existing GUI functions and orphaned parameters")

        # Get all GUI system functions
        functions = get_gui_system_functions()
        logger.info(f"Loading {len(functions)} GUI system functions...")

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
                task: 'Task 3',
                priority: 'MEDIUM',
                complexity: 3,
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
        WHERE f.name STARTS WITH 'system.gui.'
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
        WHERE f.name STARTS WITH 'system.gui.'
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
        WHERE f.name STARTS WITH 'system.gui.'
        MERGE (t:Task {name: 'Task 3', description: 'GUI System Expansion', priority: 'MEDIUM'})
        CREATE (t)-[:INCLUDES]->(f)
        """

        db_manager.execute_query(task_query)

        # Verify population
        verify_query = """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.gui.'
        RETURN count(f) as function_count
        """

        result = db_manager.execute_query(verify_query)
        function_count = result[0]["function_count"]

        logger.info(f"Successfully populated {function_count} GUI system functions")

        # Get relationship counts
        rel_query = """
        MATCH (f:Function)-[r]->()
        WHERE f.name STARTS WITH 'system.gui.'
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
    print("Task 3: GUI System Population")
    print("=" * 50)

    success = populate_gui_system_functions()

    if success:
        print("\n✅ Task 3 GUI system functions populated successfully!")
        print("\nGUI System Functions Added:")
        print("- GUI Management: 10 functions")
        print("  • Desktop Operations: 3 functions")
        print("  • Window Management: 3 functions")
        print("  • Container Access: 1 function")
        print("  • Coordinate Operations: 1 function")
        print("  • Client Information: 1 function")
        print("  • Data Quality: 1 function")
        print("  • Screen Management: 2 functions")
        print("  • Display Control: 1 function")
        print("- GUI Dialogs: 3 functions")
        print("  • Selection Dialogs: 1 function")
        print("  • Message Dialogs: 2 functions")
        print("- GUI Components: 4 functions")
        print("  • Dynamic Creation: 1 function")
        print("  • Dynamic Management: 1 function")
        print("  • Component Operations: 1 function")
        print("  • Component Discovery: 1 function")
        print("- GUI Operations: 8 functions")
        print("  • System Integration: 2 functions")
        print("  • Input Methods: 1 function")
        print("  • Mouse Operations: 1 function")
        print("  • Audio Feedback: 1 function")
        print("  • Haptic Feedback: 1 function")
        print("\nTotal: 25 comprehensive GUI functions")
        print("Progress: Task 3/10 completed!")
    else:
        print("\n❌ Failed to populate GUI system functions")
        sys.exit(1)
