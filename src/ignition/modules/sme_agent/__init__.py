"""SME Agent Module - Phase 11: Process SME Agent & AI Enhancement Platform

This module implements a comprehensive Ignition Subject Matter Expert (SME) Agent
using an 8B parameter LLM fine-tuned with extensive Neo4j knowledge graph and vector embeddings.

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SMEAgentValidationError(Exception):
    """Custom exception for SME Agent validation errors."""

    pass


def validate_sme_agent_environment() -> dict[str, Any]:
    """Step 1: Environment Validation First (crawl_mcp.py methodology)

    Validate all required environment variables and dependencies for SME Agent.

    Returns:
        Dict containing validation results and configuration
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "config": {},
        "components_available": {},
    }

    # Required environment variables for SME Agent
    required_env_vars = {
        "NEO4J_URI": "Neo4j database connection",
        "NEO4J_USER": "Neo4j authentication user",
        "NEO4J_PASSWORD": "Neo4j authentication password",
    }

    # Optional environment variables with defaults
    optional_env_vars = {
        "SME_AGENT_MODEL": "llama3.1-8b",  # Default LLM model
        "SME_AGENT_QUANTIZATION": "int8",  # Default quantization
        "SME_AGENT_GPU_ENABLED": "false",  # GPU acceleration
        "SME_AGENT_MAX_CONTEXT": "8192",  # Maximum context length
        "SME_AGENT_TEMPERATURE": "0.7",  # Generation temperature
        "SME_AGENT_TOP_P": "0.9",  # Top-p sampling
        "SME_AGENT_MAX_TOKENS": "2048",  # Maximum response tokens
        "USE_KNOWLEDGE_GRAPH": "true",  # Enable knowledge graph integration
        "USE_VECTOR_EMBEDDINGS": "true",  # Enable vector embeddings
        "SME_AGENT_LOG_LEVEL": "INFO",  # Logging level
    }

    # Step 1.1: Validate required environment variables
    for env_var, description in required_env_vars.items():
        value = os.getenv(env_var)
        if not value:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Missing required environment variable: {env_var} ({description})"
            )
        else:
            validation_result["config"][env_var] = value

    # Step 1.2: Set optional environment variables with defaults
    for env_var, default_value in optional_env_vars.items():
        value = os.getenv(env_var, default_value)
        validation_result["config"][env_var] = value

        # Validate specific configurations
        if env_var == "SME_AGENT_MAX_CONTEXT":
            try:
                int(value)
            except ValueError:
                validation_result["warnings"].append(
                    f"Invalid {env_var}: {value}, using default 8192"
                )
                validation_result["config"][env_var] = "8192"

        elif env_var == "SME_AGENT_TEMPERATURE":
            try:
                temp_val = float(value)
                if not 0.0 <= temp_val <= 2.0:
                    validation_result["warnings"].append(
                        f"Temperature {value} outside recommended range [0.0, 2.0]"
                    )
            except ValueError:
                validation_result["warnings"].append(
                    f"Invalid temperature: {value}, using default 0.7"
                )
                validation_result["config"][env_var] = "0.7"

    # Step 1.3: Check component availability
    validation_result["components_available"]["neo4j"] = _check_neo4j_availability(
        validation_result["config"]
    )
    validation_result["components_available"][
        "transformers"
    ] = _check_transformers_availability()
    validation_result["components_available"]["torch"] = _check_torch_availability()
    validation_result["components_available"]["fastapi"] = _check_fastapi_availability()

    # Step 1.4: Validate directory structure
    project_root = Path.cwd()
    required_dirs = ["src/ignition/modules/sme_agent", "data", "logs", "cache"]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            validation_result["warnings"].append(
                f"Directory {dir_path} does not exist, will be created"
            )

    return validation_result


def _check_neo4j_availability(config: dict[str, str]) -> bool:
    """Check if Neo4j connection is available."""
    try:
        from neo4j import GraphDatabase

        uri = config.get("NEO4J_URI")
        user = config.get("NEO4J_USER")
        password = config.get("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            return False

        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        return True
    except Exception:
        return False


def _check_transformers_availability() -> bool:
    """Check if transformers library is available."""
    try:
        import transformers

        return True
    except ImportError:
        return False


def _check_torch_availability() -> bool:
    """Check if PyTorch is available."""
    try:
        import torch

        return True
    except ImportError:
        return False


def _check_fastapi_availability() -> bool:
    """Check if FastAPI is available."""
    try:
        import fastapi

        return True
    except ImportError:
        return False


# Phase 11 SME Agent Module Components
from .sme_agent_module import SMEAgentModule

__all__ = [
    "SMEAgentModule",
    "SMEAgentValidationError",
    "validate_sme_agent_environment",
]
