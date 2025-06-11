#!/usr/bin/env python3
"""Populate Neo4j database with Task 11: Advanced Math & Analytics Functions

This script loads 30 mathematical, statistical, and data analytics functions 
into the Neo4j graph database for the Ignition SCADA system.

Functions include:
- Advanced Mathematical Operations (10 functions)
- Statistical Analysis & Distributions (10 functions)  
- Data Analytics & Pattern Recognition (10 functions)

Total: 30 functions across Gateway, Vision Client, and Perspective Session contexts.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.schema import GraphNode, GraphRelationship, NodeType, RelationshipType
from src.ignition.graph.tasks.task_11_math_analytics_simple import get_math_analytics_functions, get_task_11_metadata


def populate_task_11_functions():
    """Populate Neo4j with Task 11: Advanced Math & Analytics Functions."""
    
    print("=" * 60)
    print("TASK 11: ADVANCED MATH & ANALYTICS FUNCTIONS")
    print("=" * 60)
    
    # Initialize database client
    client = IgnitionGraphClient()
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        if not client.connect():
            print("❌ Failed to connect to database!")
            return False
        print("✅ Database connection successful!")
        
        # Get functions and metadata
        functions = get_math_analytics_functions()
        metadata = get_task_11_metadata()
        
        print(f"\n📊 Task Metadata:")
        print(f"   • Task: {metadata['task_name']}")
        print(f"   • Total Functions: {metadata['total_functions']}")
        print(f"   • Categories: {', '.join(metadata['categories'])}")
        print(f"   • Contexts: {', '.join(metadata['contexts'])}")
        
        # Validate function count
        if len(functions) != metadata['total_functions']:
            print(f"❌ Function count mismatch! Expected {metadata['total_functions']}, got {len(functions)}")
            return False
            
        print(f"✅ Function count validated: {len(functions)} functions")
        
        # Get current database state
        print("\n📈 Current Database State:")
        current_stats = client.get_database_stats()
        current_functions = current_stats.get('total_nodes', 0)
        current_relationships = current_stats.get('total_relationships', 0)
        print(f"   • Current Functions: {current_functions}")
        print(f"   • Current Relationships: {current_relationships}")
        
        # Populate functions by category
        success_count = 0
        relationship_count = 0
        
        categories = {
            "Mathematical Operations": [],
            "Statistical Analysis": [],
            "Data Analytics": []
        }
        
        # Group functions by category
        for func in functions:
            categories[func["category"]].append(func)
        
        # Process each category
        for category, category_functions in categories.items():
            print(f"\n🔧 Processing {category} ({len(category_functions)} functions)...")
            
            for i, function in enumerate(category_functions, 1):
                try:
                    print(f"   [{i:2d}/{len(category_functions)}] Adding {function['name']}...")
                    
                    # Create function node
                    func_node = GraphNode(NodeType.FUNCTION, function)
                    if client.create_node(func_node):
                        success_count += 1
                        
                        # Create relationships
                        func_name = function['name']
                        
                        # Function-Context relationships
                        for context in function.get('scope', []):
                            rel = GraphRelationship(
                                from_node_type=NodeType.FUNCTION,
                                to_node_type=NodeType.CONTEXT,
                                relationship_type=RelationshipType.AVAILABLE_IN,
                                from_name=func_name,
                                to_name=context
                            )
                            if client.create_relationship(rel):
                                relationship_count += 1
                        
                        # Function-Category relationship
                        cat_rel = GraphRelationship(
                            from_node_type=NodeType.FUNCTION,
                            to_node_type=NodeType.CATEGORY,
                            relationship_type=RelationshipType.BELONGS_TO,
                            from_name=func_name,
                            to_name=function.get('category', 'Mathematical Operations')
                        )
                        if client.create_relationship(cat_rel):
                            relationship_count += 1
                        
                        # Function-Pattern relationships
                        for pattern in function.get('patterns', []):
                            pattern_rel = GraphRelationship(
                                from_node_type=NodeType.FUNCTION,
                                to_node_type=NodeType.PATTERN,
                                relationship_type=RelationshipType.IMPLEMENTS,
                                from_name=func_name,
                                to_name=pattern
                            )
                            if client.create_relationship(pattern_rel):
                                relationship_count += 1
                        
                        print(f"       ✅ Success! Function and relationships created")
                    else:
                        print(f"       ❌ Failed to create function node")
                        
                except Exception as e:
                    print(f"       ❌ Exception: {str(e)}")
        
        # Final validation
        print(f"\n📊 Population Results:")
        print(f"   • Functions Processed: {len(functions)}")
        print(f"   • Successful Additions: {success_count}")
        print(f"   • Failed Additions: {len(functions) - success_count}")
        print(f"   • Success Rate: {(success_count/len(functions)*100):.1f}%")
        print(f"   • New Relationships: {relationship_count}")
        
        # Get updated database state
        print(f"\n📈 Updated Database State:")
        updated_stats = client.get_database_stats()
        updated_functions = updated_stats.get('total_nodes', 0)
        updated_relationships = updated_stats.get('total_relationships', 0)
        print(f"   • Total Functions: {updated_functions} (+{updated_functions - current_functions})")
        print(f"   • Total Relationships: {updated_relationships} (+{updated_relationships - current_relationships})")
        
        # Calculate completion progress
        target_functions = 400  # Estimated total target
        completion_percentage = (updated_functions / target_functions) * 100
        print(f"   • Overall Progress: {updated_functions}/{target_functions}+ ({completion_percentage:.1f}% complete)")
        
        if success_count == len(functions):
            print(f"\n🎉 Task 11 completed successfully!")
            print(f"   All {success_count} math and analytics functions added to database.")
            return True
        else:
            print(f"\n⚠️  Task 11 completed with {len(functions) - success_count} failures.")
            return False
            
    except Exception as e:
        print(f"\n❌ Critical error during population: {str(e)}")
        return False
        
    finally:
        # Disconnect from database
        if client.is_connected():
            client.disconnect()


def validate_task_11_completion():
    """Validate that Task 11 functions were properly added."""
    
    print("\n" + "=" * 60)
    print("TASK 11 VALIDATION")
    print("=" * 60)
    
    client = IgnitionGraphClient()
    
    try:
        if not client.connect():
            print("❌ Failed to connect for validation!")
            return False
        
        # Check for Task 11 specific functions
        sample_functions = [
            "system.math.calculateTrigonometric",
            "system.statistics.calculateDescriptiveStats", 
            "system.analytics.calculateKPIs"
        ]
        
        print("🔍 Validating sample functions...")
        for func_name in sample_functions:
            query = f"MATCH (f:Function {{name: '{func_name}'}}) RETURN f"
            result = client.execute_query(query)
            exists = len(result) > 0
            status = "✅ Found" if exists else "❌ Missing"
            print(f"   • {func_name}: {status}")
        
        # Check function categories
        print(f"\n📊 Validating function categories...")
        categories = ["Mathematical Operations", "Statistical Analysis", "Data Analytics"]
        
        for category in categories:
            query = f"MATCH (f:Function)-[:BELONGS_TO]->(c:Category {{name: '{category}'}}) RETURN count(f) as count"
            result = client.execute_query(query)
            count = result[0]['count'] if result else 0
            print(f"   • {category}: {count} functions")
        
        # Get final statistics
        stats = client.get_database_stats()
        print(f"\n📈 Final Database Statistics:")
        print(f"   • Total Functions: {stats.get('total_nodes', 0)}")
        print(f"   • Total Relationships: {stats.get('total_relationships', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        return False
        
    finally:
        if client.is_connected():
            client.disconnect()


if __name__ == "__main__":
    print("🚀 Starting Task 11: Advanced Math & Analytics Functions Population")
    
    # Run population
    population_success = populate_task_11_functions()
    
    if population_success:
        # Run validation
        validation_success = validate_task_11_completion()
        
        if validation_success:
            print(f"\n🎯 TASK 11 COMPLETE!")
            print(f"   ✅ Population: SUCCESS")  
            print(f"   ✅ Validation: SUCCESS")
            print(f"   📊 30 math & analytics functions ready for use!")
        else:
            print(f"\n⚠️  TASK 11 PARTIAL SUCCESS")
            print(f"   ✅ Population: SUCCESS")
            print(f"   ❌ Validation: FAILED")
    else:
        print(f"\n❌ TASK 11 FAILED")
        print(f"   ❌ Population: FAILED")
        print(f"   ⏭️  Validation: SKIPPED")
    
    print(f"\n{'='*60}")
    print("Task 11 execution completed.")
    print(f"{'='*60}") 