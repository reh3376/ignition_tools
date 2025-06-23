#!/usr/bin/env python3
"""Validate Neo4j environment variables are properly configured.

This script checks that all Neo4j environment variables are properly set
and that connections work correctly.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main():
    """Validate Neo4j environment configuration."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    print("🔍 Validating Neo4j Environment Configuration...")

    # Load environment variables
    load_dotenv(env_file, override=True)

    # Check required variables
    required_vars = {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "ignition-graph"
    }

    all_good = True

    for var, expected in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ Missing: {var}")
            all_good = False
        elif value != expected:
            print(f"⚠️  {var} = {value} (expected: {expected})")
        else:
            print(f"✅ {var} = {value}")

    # Test connection if all variables present
    if all_good:
        try:
            sys.path.append(str(project_root / "src"))
            from ignition.graph.client import IgnitionGraphClient

            client = IgnitionGraphClient()
            client.connect()
            result = client.execute_query("RETURN 1 as test")
            client.disconnect()

            if result and result[0]["test"] == 1:
                print("✅ Neo4j connection successful!")
            else:
                print("❌ Neo4j connection failed!")
                all_good = False

        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            all_good = False

    if all_good:
        print("\n🎉 All Neo4j environment variables are properly configured!")
    else:
        print("\n❌ Neo4j environment configuration has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()
