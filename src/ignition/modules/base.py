"""Base module framework for Ignition Modules.

This module provides the foundational classes and interfaces for building
Ignition modules with consistent structure and behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union
import logging
from pathlib import Path


@dataclass
class ModuleConfig:
    """Configuration for an Ignition module."""
    
    name: str
    version: str = "1.0.0"
    description: str = ""
    enabled: bool = True
    debug: bool = False
    log_level: str = "INFO"
    module_id: Optional[str] = None
    security: Dict[str, Any] = field(default_factory=dict)
    config_data: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config_data[key] = value


@dataclass
class ModuleContext:
    """Runtime context for an Ignition module."""
    
    config: ModuleConfig
    logger: logging.Logger
    metrics: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    module_name: Optional[str] = None
    workspace_path: Optional[Path] = None
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        return self.session_data.get(key, default)
    
    def set_session_data(self, key: str, value: Any) -> None:
        """Set session data."""
        self.session_data[key] = value


class AbstractIgnitionModule(ABC):
    """Abstract base class for all Ignition modules.
    
    This class provides the standard interface and lifecycle methods
    that all Ignition modules must implement.
    """
    
    def __init__(self, config: ModuleConfig):
        """Initialize the module with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"ignition.modules.{config.name}")
        self.logger.setLevel(getattr(logging, config.log_level.upper()))
        self._initialized = False
        self._context: Optional[ModuleContext] = None
    
    @property
    def name(self) -> str:
        """Get the module name."""
        return self.config.name
    
    @property
    def version(self) -> str:
        """Get the module version."""
        return self.config.version
    
    @property
    def description(self) -> str:
        """Get the module description."""
        return self.config.description
    
    @property
    def is_initialized(self) -> bool:
        """Check if the module is initialized."""
        return self._initialized
    
    @property
    def context(self) -> Optional[ModuleContext]:
        """Get the module context."""
        return self._context
    
    @abstractmethod
    async def initialize(self, context: ModuleContext) -> bool:
        """Initialize the module with the given context.
        
        Args:
            context: The module runtime context
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the module and cleanup resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the module.
        
        Returns:
            Dictionary containing module status information
        """
        pass
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request to the module.
        
        Args:
            request: The request data
            
        Returns:
            The response data
        """
        pass
    
    async def configure(self, config_updates: Dict[str, Any]) -> bool:
        """Update module configuration.
        
        Args:
            config_updates: Configuration updates to apply
            
        Returns:
            True if configuration was updated successfully
        """
        try:
            for key, value in config_updates.items():
                self.config.set(key, value)
            self.logger.info(f"Configuration updated: {list(config_updates.keys())}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False
    
    async def get_info(self) -> Dict[str, Any]:
        """Get module information.
        
        Returns:
            Dictionary containing module information
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "initialized": self.is_initialized,
            "enabled": self.config.enabled,
            "debug": self.config.debug,
            "log_level": self.config.log_level
        }
    
    def _set_context(self, context: ModuleContext) -> None:
        """Set the module context (internal use)."""
        self._context = context
    
    def _set_initialized(self, initialized: bool) -> None:
        """Set the initialized flag (internal use)."""
        self._initialized = initialized


class ModuleError(Exception):
    """Base exception for module-related errors."""
    
    def __init__(self, message: str, module_name: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.module_name = module_name
        self.details = details or {}


class ModuleInitializationError(ModuleError):
    """Exception raised when module initialization fails."""
    pass


class ModuleConfigurationError(ModuleError):
    """Exception raised when module configuration is invalid."""
    pass


class ModuleProcessingError(ModuleError):
    """Exception raised when module request processing fails."""
    pass 