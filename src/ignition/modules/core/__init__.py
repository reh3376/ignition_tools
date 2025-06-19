"""Core module framework for Ignition Module development.

This package provides the foundational classes and utilities for building
robust Ignition modules with lifecycle management, configuration persistence,
and comprehensive logging and diagnostics.
"""

from .abstract_module import AbstractIgnitionModule
from .config import ModuleConfigurationManager
from .lifecycle import ModuleLifecycleManager
from .logging import ModuleDiagnosticsManager

__all__ = [
    "AbstractIgnitionModule",
    "ModuleConfigurationManager",
    "ModuleDiagnosticsManager",
    "ModuleLifecycleManager",
]
