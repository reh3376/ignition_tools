#!/usr/bin/env python3
"""
AI Assistant Graph Database Utility

Quick script for AI assistants to check and start the Neo4j graph database
that serves as persistent long-term memory for this project.
"""

import subprocess
import sys
import time

import requests


def check_docker_compose():
    """Check if docker compose is available."""
    try:
        # Try new docker compose syntax first
        result = subprocess.run(
            ["docker", "compose", "version"], capture_output=True, text=True, check=True
        )
        print(f"✅ Docker Compose found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to legacy docker-compose
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"✅ Docker Compose found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose not found. Please install Docker Compose.")
            return False


def check_neo4j_status():
    """Check if Neo4j container is running."""
    try:
        # Try new docker compose syntax first
        result = subprocess.run(
            ["docker", "compose", "ps", "neo4j"],
            capture_output=True,
            text=True,
            check=True,
        )
        if "ign-scripts-neo4j" in result.stdout and "Up" in result.stdout:
            print("✅ Neo4j container is running")
            return True
        else:
            print("⚠️  Neo4j container is not running")
            return False
    except subprocess.CalledProcessError:
        # Fall back to legacy docker-compose
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "neo4j"],
                capture_output=True,
                text=True,
                check=True,
            )
            if "ign-scripts-neo4j" in result.stdout and "Up" in result.stdout:
                print("✅ Neo4j container is running")
                return True
            else:
                print("⚠️  Neo4j container is not running")
                return False
        except subprocess.CalledProcessError:
            print("❌ Error checking Neo4j status")
            return False


def start_neo4j():
    """Start the Neo4j graph database."""
    print("🚀 Starting Neo4j graph database...")
    try:
        # Try new docker compose syntax first
        subprocess.run(
            ["docker", "compose", "up", "-d", "neo4j"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ Neo4j container started successfully")
        return True
    except subprocess.CalledProcessError:
        # Fall back to legacy docker-compose
        try:
            subprocess.run(
                ["docker-compose", "up", "-d", "neo4j"],
                capture_output=True,
                text=True,
                check=True,
            )
            print("✅ Neo4j container started successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error starting Neo4j: {e.stderr}")
            return False


def wait_for_neo4j(timeout=60):
    """Wait for Neo4j to be ready."""
    print("⏳ Waiting for Neo4j to be ready...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:7474", timeout=5)
            if response.status_code == 200:
                print("✅ Neo4j is ready!")
                return True
        except requests.RequestException:
            pass

        print(".", end="", flush=True)
        time.sleep(2)

    print("\n❌ Timeout waiting for Neo4j to be ready")
    return False


def show_connection_info():
    """Display connection information for AI assistants."""
    print("\n" + "=" * 50)
    print("🧠 AI ASSISTANT GRAPH DATABASE READY")
    print("=" * 50)
    print("📍 Neo4j Browser: http://localhost:7474")
    print("🔐 Credentials: neo4j/ignition-graph")
    print("⚡ Bolt Protocol: bolt://localhost:7687")
    print("\n📚 For query examples and documentation:")
    print("    📖 docs/ai_assistant_memory_system.md")
    print("\n🔍 Quick test query (in Neo4j Browser):")
    print("    MATCH (n) RETURN count(n) as total_nodes")
    print("=" * 50)


def main():
    """Main function for AI assistant graph database management."""
    print("🤖 AI Assistant Graph Database Utility")
    print("=" * 40)

    # Check prerequisites
    if not check_docker_compose():
        sys.exit(1)

    # Check current status
    if check_neo4j_status():
        print("✅ Neo4j is already running")
    else:
        if not start_neo4j():
            sys.exit(1)

        if not wait_for_neo4j():
            sys.exit(1)

    # Show connection info
    show_connection_info()

    print("\n🎯 The graph database contains:")
    print("   • 400+ Ignition system functions")
    print("   • Context availability mappings")
    print("   • Script templates and relationships")
    print("   • Configuration patterns")
    print("   • Parameter compatibility matrices")

    print("\n💡 Use this database to provide context-aware")
    print("   assistance for Ignition script generation!")


if __name__ == "__main__":
    main()
