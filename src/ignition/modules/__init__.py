"""Ignition Module Development Framework.

This package provides tools and utilities for developing custom Ignition modules
using the official Inductive Automation SDK, enhanced with code intelligence
and automated generation capabilities.
"""

from .module_builder import ModuleBuilder
from .module_generator import ModuleGenerator
from .sdk_manager import IgnitionSDKManager

__all__ = [
    "IgnitionSDKManager",
    "ModuleBuilder",
    "ModuleGenerator",
]

__version__ = "1.0.0"
