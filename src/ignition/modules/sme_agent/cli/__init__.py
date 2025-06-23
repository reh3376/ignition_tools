"""SME Agent CLI Package - Modular Command Interface

Following crawl_mcp.py methodology with modular design.
"""

from .core_commands import core_commands
from .evaluation_commands import evaluation_commands
from .infrastructure_commands import infrastructure_commands
from .knowledge_commands import knowledge_commands

__all__ = [
    "core_commands",
    "evaluation_commands",
    "infrastructure_commands",
    "knowledge_commands",
]
