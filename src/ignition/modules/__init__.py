"""Ignition Module Development Framework

This package provides tools and utilities for developing custom Ignition modules
using the official Inductive Automation SDK, enhanced with code intelligence
and automated generation capabilities.
"""

from .sdk_manager import IgnitionSDKManager
from .module_generator import ModuleGenerator
from .module_builder import ModuleBuilder

__all__ = [
    "IgnitionSDKManager",
    "ModuleGenerator", 
    "ModuleBuilder",
]

__version__ = "1.0.0" 