"""Abstract base class for Ignition modules with comprehensive framework support."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .config import ModuleConfigurationManager
from .lifecycle import ModuleLifecycleManager, ModuleState
from .logging import ModuleDiagnosticsManager


class ModuleScope(Enum):
    """Enumeration of Ignition module scopes."""

    GATEWAY = "G"
    CLIENT = "C"
    DESIGNER = "D"


@dataclass
class ModuleMetadata:
    """Metadata for an Ignition module."""

    name: str
    id: str
    version: str
    description: str
    vendor: str
    scopes: list[ModuleScope]
    min_ignition_version: str = "8.1.0"
    dependencies: list[str] | None = None

    def __post_init__(self):
        """Initialize default values."""
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ModuleContext:
    """Context information for module execution."""

    module_path: Path
    config_path: Path
    data_path: Path
    log_path: Path
    temp_path: Path
    ignition_home: Path | None = None
    gateway_context: Any | None = None
    designer_context: Any | None = None
    client_context: Any | None = None


class AbstractIgnitionModule(ABC):
    """Abstract base class for all Ignition modules.

    This class provides the foundational framework for building robust Ignition
    modules with proper lifecycle management, configuration persistence, logging,
    and diagnostics capabilities.

    All custom Ignition modules should inherit from this class and implement
    the required abstract methods for their specific functionality.
    """

    def __init__(self, metadata: ModuleMetadata, context: ModuleContext):
        """Initialize the abstract module.

        Args:
            metadata: Module metadata information
            context: Module execution context
        """
        self._metadata = metadata
        self._context = context

        # Initialize core managers
        self._lifecycle_manager = ModuleLifecycleManager(self)
        self._config_manager = ModuleConfigurationManager(self)
        self._diagnostics_manager = ModuleDiagnosticsManager(self)

        # Module state
        self._state = ModuleState.UNINITIALIZED
        self._error_state: str | None = None

        # Module components
        self._gateway_hook: Any | None = None
        self._designer_hook: Any | None = None
        self._client_hook: Any | None = None

        # Initialize logging
        self._logger = self._diagnostics_manager.get_logger()
        self._logger.info(f"Initializing module: {self._metadata.name} v{self._metadata.version}")

    # Properties

    @property
    def metadata(self) -> ModuleMetadata:
        """Get module metadata."""
        return self._metadata

    @property
    def context(self) -> ModuleContext:
        """Get module context."""
        return self._context

    @property
    def state(self) -> ModuleState:
        """Get current module state."""
        return self._state

    @property
    def lifecycle_manager(self) -> ModuleLifecycleManager:
        """Get lifecycle manager."""
        return self._lifecycle_manager

    @property
    def config_manager(self) -> ModuleConfigurationManager:
        """Get configuration manager."""
        return self._config_manager

    @property
    def diagnostics_manager(self) -> ModuleDiagnosticsManager:
        """Get diagnostics manager."""
        return self._diagnostics_manager

    @property
    def logger(self):
        """Get module logger."""
        return self._logger

    @property
    def error_state(self) -> str | None:
        """Get error state if any."""
        return self._error_state

    # Abstract methods - must be implemented by subclasses

    @abstractmethod
    def get_module_info(self) -> dict[str, Any]:
        """Get detailed module information.

        Returns:
            Dictionary containing module information
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validate module configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    @abstractmethod
    def initialize_module(self) -> bool:
        """Initialize the module.

        This method is called during module startup to perform any necessary
        initialization tasks.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def startup_module(self) -> bool:
        """Start the module.

        This method is called to start the module after initialization.

        Returns:
            True if startup successful, False otherwise
        """
        pass

    @abstractmethod
    def shutdown_module(self) -> bool:
        """Shutdown the module.

        This method is called to gracefully shutdown the module.

        Returns:
            True if shutdown successful, False otherwise
        """
        pass

    @abstractmethod
    def configure_module(self, config: dict[str, Any]) -> bool:
        """Configure the module with new settings.

        Args:
            config: Configuration dictionary

        Returns:
            True if configuration successful, False otherwise
        """
        pass

    # Optional hook methods - can be overridden by subclasses

    def create_gateway_hook(self) -> Any | None:
        """Create and return Gateway hook instance.

        Override this method to provide Gateway-specific functionality.

        Returns:
            Gateway hook instance or None if not applicable
        """
        return None

    def create_designer_hook(self) -> Any | None:
        """Create and return Designer hook instance.

        Override this method to provide Designer-specific functionality.

        Returns:
            Designer hook instance or None if not applicable
        """
        return None

    def create_client_hook(self) -> Any | None:
        """Create and return Client hook instance.

        Override this method to provide Client-specific functionality.

        Returns:
            Client hook instance or None if not applicable
        """
        return None

    # Lifecycle management methods

    def _set_state(self, new_state: ModuleState, error_message: str | None = None):
        """Set module state.

        Args:
            new_state: New module state
            error_message: Error message if transitioning to error state
        """
        old_state = self._state
        self._state = new_state
        self._error_state = error_message

        self._logger.info(f"Module state changed: {old_state} -> {new_state}")
        if error_message:
            self._logger.error(f"Module error: {error_message}")

        # Notify lifecycle manager
        self._lifecycle_manager.on_state_changed(old_state, new_state)

    def start(self) -> bool:
        """Start the module lifecycle.

        Returns:
            True if started successfully, False otherwise
        """
        try:
            self._logger.info("Starting module lifecycle")

            # Initialize
            if not self._initialize():
                self._set_state(ModuleState.ERROR, "Initialization failed")
                return False

            # Startup
            if not self._startup():
                self._set_state(ModuleState.ERROR, "Startup failed")
                return False

            self._set_state(ModuleState.RUNNING)
            self._logger.info("Module started successfully")
            return True

        except Exception as e:
            self._set_state(ModuleState.ERROR, f"Startup exception: {e}")
            self._logger.exception("Exception during module startup")
            return False

    def stop(self) -> bool:
        """Stop the module lifecycle.

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            self._logger.info("Stopping module")

            if not self._shutdown():
                self._set_state(ModuleState.ERROR, "Shutdown failed")
                return False

            self._set_state(ModuleState.STOPPED)
            self._logger.info("Module stopped successfully")
            return True

        except Exception as e:
            self._set_state(ModuleState.ERROR, f"Shutdown exception: {e}")
            self._logger.exception("Exception during module shutdown")
            return False

    def restart(self) -> bool:
        """Restart the module.

        Returns:
            True if restarted successfully, False otherwise
        """
        self._logger.info("Restarting module")

        if self._state == ModuleState.RUNNING and not self.stop():
            return False

        return self.start()

    def configure(self, config: dict[str, Any]) -> bool:
        """Configure the module.

        Args:
            config: Configuration dictionary

        Returns:
            True if configured successfully, False otherwise
        """
        try:
            self._logger.info("Configuring module")

            # Validate configuration
            if not self.validate_configuration():
                self._logger.error("Configuration validation failed")
                return False

            # Apply configuration
            if not self.configure_module(config):
                self._logger.error("Configuration application failed")
                return False

            # Persist configuration
            if not self._config_manager.save_configuration(config):
                self._logger.error("Configuration persistence failed")
                return False

            self._logger.info("Module configured successfully")
            return True

        except Exception as e:
            self._logger.exception(f"Exception during module configuration: {e}")
            return False

    # Internal lifecycle methods

    def _initialize(self) -> bool:
        """Internal initialization method."""
        self._set_state(ModuleState.INITIALIZING)

        # Load configuration
        if not self._config_manager.load_configuration():
            self._logger.error("Failed to load configuration")
            return False

        # Initialize hooks
        self._initialize_hooks()

        # Call user initialization
        return self.initialize_module()

    def _startup(self) -> bool:
        """Internal startup method."""
        self._set_state(ModuleState.STARTING)

        # Start hooks
        self._startup_hooks()

        # Call user startup
        return self.startup_module()

    def _shutdown(self) -> bool:
        """Internal shutdown method."""
        self._set_state(ModuleState.STOPPING)

        # Shutdown hooks
        self._shutdown_hooks()

        # Call user shutdown
        return self.shutdown_module()

    def _initialize_hooks(self):
        """Initialize module hooks."""
        if ModuleScope.GATEWAY in self._metadata.scopes:
            self._gateway_hook = self.create_gateway_hook()
            if self._gateway_hook:
                self._logger.info("Gateway hook created")

        if ModuleScope.DESIGNER in self._metadata.scopes:
            self._designer_hook = self.create_designer_hook()
            if self._designer_hook:
                self._logger.info("Designer hook created")

        if ModuleScope.CLIENT in self._metadata.scopes:
            self._client_hook = self.create_client_hook()
            if self._client_hook:
                self._logger.info("Client hook created")

    def _startup_hooks(self):
        """Start module hooks."""
        if self._gateway_hook and hasattr(self._gateway_hook, "startup"):
            try:
                self._gateway_hook.startup()
                self._logger.info("Gateway hook started")
            except Exception as e:
                self._logger.exception(f"Gateway hook startup failed: {e}")

        if self._designer_hook and hasattr(self._designer_hook, "startup"):
            try:
                self._designer_hook.startup()
                self._logger.info("Designer hook started")
            except Exception as e:
                self._logger.exception(f"Designer hook startup failed: {e}")

        if self._client_hook and hasattr(self._client_hook, "startup"):
            try:
                self._client_hook.startup()
                self._logger.info("Client hook started")
            except Exception as e:
                self._logger.exception(f"Client hook startup failed: {e}")

    def _shutdown_hooks(self):
        """Shutdown module hooks."""
        if self._gateway_hook and hasattr(self._gateway_hook, "shutdown"):
            try:
                self._gateway_hook.shutdown()
                self._logger.info("Gateway hook shutdown")
            except Exception as e:
                self._logger.exception(f"Gateway hook shutdown failed: {e}")

        if self._designer_hook and hasattr(self._designer_hook, "shutdown"):
            try:
                self._designer_hook.shutdown()
                self._logger.info("Designer hook shutdown")
            except Exception as e:
                self._logger.exception(f"Designer hook shutdown failed: {e}")

        if self._client_hook and hasattr(self._client_hook, "shutdown"):
            try:
                self._client_hook.shutdown()
                self._logger.info("Client hook shutdown")
            except Exception as e:
                self._logger.exception(f"Client hook shutdown failed: {e}")

    # Utility methods

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive module status.

        Returns:
            Dictionary containing module status information
        """
        return {
            "name": self._metadata.name,
            "version": self._metadata.version,
            "state": self._state.value,
            "error_state": self._error_state,
            "scopes": [scope.value for scope in self._metadata.scopes],
            "hooks": {
                "gateway": self._gateway_hook is not None,
                "designer": self._designer_hook is not None,
                "client": self._client_hook is not None,
            },
            "configuration_loaded": self._config_manager.is_configuration_loaded(),
            "diagnostics": self._diagnostics_manager.get_health_status(),
        }

    def __str__(self) -> str:
        """String representation of the module."""
        return f"{self._metadata.name} v{self._metadata.version} ({self._state.value})"

    def __repr__(self) -> str:
        """Detailed string representation of the module."""
        return (
            f"AbstractIgnitionModule(name='{self._metadata.name}', "
            f"version='{self._metadata.version}', state='{self._state.value}', "
            f"scopes={[s.value for s in self._metadata.scopes]})"
        )
