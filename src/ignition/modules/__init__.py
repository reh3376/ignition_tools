"""Ignition Modules Package.

This package contains all Ignition development modules including:
- Base module framework
- Data Integration Module
- AI Assistant Module
- CLI interface
"""

from .ai_assistant import AIAssistantModule, create_ai_assistant_module
from .base import AbstractIgnitionModule, ModuleConfig, ModuleContext
from .data_integration import DataIntegrationModule, create_data_integration_module

__all__ = [
    # AI Assistant Module
    "AIAssistantModule",
    # Base framework
    "AbstractIgnitionModule",
    # Data Integration Module
    "DataIntegrationModule",
    "ModuleConfig",
    "ModuleContext",
    "create_ai_assistant_module",
    "create_data_integration_module",
]

__version__ = "1.0.0"
