"""SME Agent CLI Package - Modular Command Interface

Following crawl_mcp.py methodology with modular design.
"""

from .control_optimization_commands import control_group, mpc_group, pid_group
from .core_commands import core_commands
from .dataset_curation_commands import dataset_curation
from .evaluation_commands import evaluation_commands
from .infrastructure_commands import infrastructure_commands
from .knowledge_commands import knowledge_commands
from .production_deployment_commands import deployment_group

__all__ = [
    "control_group",
    "core_commands",
    "dataset_curation",
    "deployment_group",
    "evaluation_commands",
    "infrastructure_commands",
    "knowledge_commands",
    "mpc_group",
    "pid_group",
]
