"""Ignition Modules Package

This package contains all Ignition development modules including:
- Base module framework
- Data Integration Module  
- AI Assistant Module
- CLI interface
"""

from .base import AbstractIgnitionModule, ModuleConfig, ModuleContext
from .data_integration import create_data_integration_module, DataIntegrationModule
from .ai_assistant import create_ai_assistant_module, AIAssistantModule

__all__ = [
    # Base framework
    "AbstractIgnitionModule",
    "ModuleConfig", 
    "ModuleContext",
    
    # Data Integration Module
    "DataIntegrationModule",
    "create_data_integration_module",
    
    # AI Assistant Module
    "AIAssistantModule",
    "create_ai_assistant_module",
]

__version__ = "1.0.0"
