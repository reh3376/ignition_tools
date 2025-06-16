#!/usr/bin/env python3
"""Setup script for Neo4j and MCP services."""

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_docker() -> bool:
    """Check if Docker is installed and running.

    Returns:
        bool: True if Docker is available, False otherwise
    """
    try:
        subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info("✅ Docker is installed and running")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ Docker is not running")
        return False
    except FileNotFoundError:
        logger.error("❌ Docker is not installed")
        return False


def check_neo4j() -> bool:
    """Check if Neo4j is running.

    Returns:
        bool: True if Neo4j is running, False otherwise
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=neo4j"],
            capture_output=True,
            text=True,
            check=True,
        )
        if "neo4j" in result.stdout:
            logger.info("✅ Neo4j container is running")
            return True
        logger.error("❌ Neo4j container is not running")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error checking Neo4j container: {e}")
        return False


def check_env_file() -> bool:
    """Check if .env file exists and has required variables.

    Returns:
        bool: True if .env file is properly configured, False otherwise
    """
    env_path = Path(".env")
    if not env_path.exists():
        logger.error("❌ .env file not found")
        return False

    required_vars = [
        "NEO4J_URL",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
    ]

    missing_vars = []
    with open(env_path) as f:
        env_content = f.read()
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False

    logger.info("✅ .env file is properly configured")
    return True


def install_dependencies() -> bool:
    """Install required Python dependencies.

    Returns:
        bool: True if installation successful, False otherwise
    """
    try:
        # Install uv if not present
        if subprocess.run(["which", "uv"], capture_output=True).returncode != 0:
            logger.info("Installing uv...")
            subprocess.run(
                ["pip", "install", "uv"],
                check=True,
            )

        # Create virtual environment
        if not Path(".venv").exists():
            logger.info("Creating virtual environment...")
            subprocess.run(["uv", "venv"], check=True)

        # Install dependencies
        logger.info("Installing dependencies...")
        subprocess.run(
            ["uv", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )

        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error installing dependencies: {e}")
        return False


def main() -> int:
    """Run setup checks and installations.

    Returns:
        int: 0 if setup successful, 1 otherwise
    """
    logger.info("Starting Neo4j and MCP setup...")

    # Check Docker
    if not check_docker():
        return 1

    # Check Neo4j
    if not check_neo4j():
        return 1

    # Check .env file
    if not check_env_file():
        return 1

    # Install dependencies
    if not install_dependencies():
        return 1

    logger.info("✅ Setup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
