#!/usr/bin/env python3
"""
Populate Neo4j database with Task 12: Machine Learning Integration Functions

This script adds 25 comprehensive ML functions to the Ignition SCADA function library.
Functions cover model training, predictive maintenance, real-time inference, and edge ML.

Usage:
    python scripts/populate_task_12.py
"""

import sys
import os
from pathlib import Path
from typing import Any

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ignition.graph.client import IgnitionGraphClient
from ignition.graph.schema import GraphNode, GraphRelationship, NodeType, RelationshipType
from ignition.graph.tasks.task_12_ml_integration import get_ml_integration_functions, get_task_12_metadata


def create_function_node(func_data: dict[str, Any]) -> GraphNode:
    """Create a graph node for a function."""
    return GraphNode(
        node_type=NodeType.FUNCTION,
        properties={
            "name": func_data["name"],
            "description": func_data["description"],
            "parameters": func_data["parameters"],
            "returns": func_data["returns"],
            "scope": func_data["scope"],
            "category": func_data["category"],
            "patterns": func_data["patterns"],
            "task": 12,
            "version": "1.0.0",
            "status": "active"
        }
    )


def create_relationships(function_node: GraphNode, func_data: dict[str, Any]) -> list[GraphRelationship]:
    """Create relationships for a function node."""
    relationships = []
    
    # Function-Context relationships
    for context in func_data["scope"]:
        relationships.append(GraphRelationship(
            from_node_type=NodeType.FUNCTION,
            to_node_type=NodeType.CONTEXT,
            relationship_type=RelationshipType.AVAILABLE_IN,
            from_name=func_data["name"],
            to_name=context,
            properties={"task": 12}
        ))
    
    # Function-Pattern relationships
    for pattern in func_data["patterns"]:
        relationships.append(GraphRelationship(
            from_node_type=NodeType.FUNCTION,
            to_node_type=NodeType.PATTERN,
            relationship_type=RelationshipType.IMPLEMENTS,
            from_name=func_data["name"],
            to_name=pattern,
            properties={"task": 12}
        ))
    
    return relationships


def populate_task_12():
    """Populate Neo4j with Task 12: Machine Learning Integration Functions."""
    print("🚀 Starting Task 12: Machine Learning Integration Functions population...")
    
    # Initialize client
    client = IgnitionGraphClient()
    
    # Test connection
    if not client.connect():
        print("❌ Failed to connect to Neo4j database")
        return False
    
    print("✅ Connected to Neo4j database")
    
    # Get functions and metadata
    functions = get_ml_integration_functions()
    metadata = get_task_12_metadata()
    
    print(f"📊 Task 12 Overview:")
    print(f"   • Task: {metadata['task_name']}")
    print(f"   • Functions: {len(functions)}")
    print(f"   • Categories: {', '.join(metadata['categories'])}")
    print(f"   • Contexts: {', '.join(metadata['contexts'])}")
    
    # Process each function
    total_functions = len(functions)
    successful_functions = 0
    total_relationships = 0
    
    for i, func_data in enumerate(functions, 1):
        try:
            print(f"📝 Processing function {i}/{total_functions}: {func_data['name']}")
            
            # Create function node
            function_node = create_function_node(func_data)
            
            # Create the function in database
            created_node = client.create_node(function_node)
            if created_node:
                successful_functions += 1
                
                # Create relationships
                relationships = create_relationships(function_node, func_data)
                
                # Add relationships to database
                for relationship in relationships:
                    if client.create_relationship(relationship):
                        total_relationships += 1
                
                print(f"   ✅ Successfully created function with {len(relationships)} relationships")
            else:
                print(f"   ❌ Failed to create function: {func_data['name']}")
                
        except Exception as e:
            print(f"   ❌ Error processing function {func_data['name']}: {str(e)}")
            continue
    
    # Create Task 12 summary node
    task_node = GraphNode(
        node_type=NodeType.TASK,
        properties={
            "name": f"Task {metadata['task_number']}: {metadata['task_name']}",
            "number": 12,
            "description": metadata['description'],
            "total_functions": total_functions,
            "successful_functions": successful_functions,
            "total_relationships": total_relationships,
            "status": "completed",
            "version": "1.0.0"
        }
    )
    
    client.create_node(task_node)
    print(f"📋 Created Task 12 summary node")
    
    # Summary
    print(f"\n🎉 Task 12 Population Complete!")
    print(f"   ✅ Successfully created: {successful_functions}/{total_functions} functions")
    print(f"   🔗 Total relationships: {total_relationships}")
    print(f"   📈 Success rate: {(successful_functions/total_functions)*100:.1f}%")
    
    if successful_functions == total_functions:
        print(f"   🏆 Perfect score! All ML integration functions loaded successfully!")
        
        # Display function distribution
        categories = {}
        for func in functions:
            cat = func["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        print(f"\n📊 Function Distribution by Category:")
        for category, count in categories.items():
            print(f"   • {category}: {count} functions")
    
    return successful_functions == total_functions


def verify_task_12_functions():
    """Verify that Task 12 functions were created successfully."""
    print("\n🔍 Verifying Task 12 functions in database...")
    
    client = IgnitionGraphClient()
    
    # Sample function queries to verify different categories
    test_functions = [
        "system.ml.trainPredictiveModel",  # ML Training
        "system.ml.predictEquipmentFailure",  # Predictive Maintenance
        "system.ml.performRealTimeInference",  # Real-time ML
        "system.ml.enableAutoML",  # AutoML
        "system.ml.deployEdgeModel"  # Edge ML
    ]
    
    verification_results = []
    
    for func_name in test_functions:
        query = f"""
        MATCH (f:Function {{name: '{func_name}'}})
        RETURN f.name as name, f.category as category, f.task as task
        """
        
        result = client.execute_query(query)
        if result:
            verification_results.append(func_name)
            print(f"   ✅ Found: {func_name}")
        else:
            print(f"   ❌ Missing: {func_name}")
    
    # Overall verification
    if len(verification_results) == len(test_functions):
        print(f"   🎯 All {len(test_functions)} sample functions verified!")
        return True
    else:
        print(f"   ⚠️  Only {len(verification_results)}/{len(test_functions)} functions verified")
        return False


def get_database_stats():
    """Get current database statistics after Task 12."""
    print("\n📈 Database Statistics After Task 12:")
    
    client = IgnitionGraphClient()
    
    # Total functions
    query = "MATCH (f:Function) RETURN count(f) as total_functions"
    result = client.execute_query(query)
    total_functions = result[0]["total_functions"] if result else 0
    
    # Functions by task
    query = """
    MATCH (f:Function)
    RETURN f.task as task, count(f) as count
    ORDER BY f.task
    """
    result = client.execute_query(query)
    
    print(f"   📊 Total Functions: {total_functions}")
    print(f"   🏷️  Functions by Task:")
    
    for record in result:
        task_num = record["task"] if record["task"] else "Unknown"
        count = record["count"]
        print(f"      • Task {task_num}: {count} functions")
    
    # ML-specific statistics
    query = """
    MATCH (f:Function)
    WHERE f.task = 12
    RETURN f.category as category, count(f) as count
    ORDER BY count DESC
    """
    result = client.execute_query(query)
    
    print(f"   🤖 Task 12 ML Functions by Category:")
    for record in result:
        category = record["category"]
        count = record["count"]
        print(f"      • {category}: {count} functions")
    
    return total_functions


if __name__ == "__main__":
    print("=" * 80)
    print("Task 12: Machine Learning Integration Functions - Database Population")
    print("=" * 80)
    
    # Run population
    success = populate_task_12()
    
    if success:
        # Verify functions
        verify_task_12_functions()
        
        # Get updated stats
        total_functions = get_database_stats()
        
        print(f"\n🎊 Task 12 Successfully Completed!")
        print(f"   • 25 ML integration functions added")
        print(f"   • Database now contains {total_functions} total functions")
        print(f"   • ML capabilities: Training, Predictive Maintenance, Real-time Inference")
        print(f"   • Advanced features: AutoML, Edge ML, Federated Learning")
        
    else:
        print(f"\n⚠️  Task 12 completed with some issues")
        print(f"   • Check the error messages above")
        print(f"   • Some functions may need to be added manually")
    
    print("=" * 80) 