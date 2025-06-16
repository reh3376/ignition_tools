"""Version Control Intelligence Module for Ignition Projects.

This module provides intelligent analysis and recommendations for version control
operations on Ignition projects, including commit impact analysis, merge conflict
prediction, and release planning recommendations.
"""

from .change_tracker import ChangeTracker
from .conflict_predictor import MergeConflictPredictor
from .dependency_analyzer import DependencyAnalyzer
from .impact_analyzer import CommitImpactAnalyzer
from .manager import VersionControlManager
from .release_planner import ReleasePlanner

__all__ = [
    "ChangeTracker",
    "CommitImpactAnalyzer",
    "DependencyAnalyzer",
    "MergeConflictPredictor",
    "ReleasePlanner",
    "VersionControlManager",
]

__version__ = "1.0.0"
