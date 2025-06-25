"""Basic example module demonstrating the Ignition module framework."""

from pathlib import Path
from typing import Self, Any

from ignition.modules.core import AbstractIgnitionModule
from ignition.modules.core.abstract_module import (
    ModuleContext,
    ModuleMetadata,
    ModuleScope,
)


class BasicExampleModule(AbstractIgnitionModule):
    """Basic example module demonstrating core framework functionality.

    This module provides a simple example of how to create an Ignition module
    using the core framework. It implements all required abstract methods and
    demonstrates basic configuration, logging, and lifecycle management.
    """

    def __init__(self: Self, context: ModuleContext):
        """Initialize the basic example module.

        Args:
            context: Module execution context
        """
        # Define module metadata
        metadata = ModuleMetadata(
            name="Basic Example Module",
            id="basic-example",
            version="1.0.0",
            description="A basic example module demonstrating the core framework",
            vendor="IGN Scripts",
            scopes=[ModuleScope.GATEWAY, ModuleScope.DESIGNER],
            min_ignition_version="8.1.0",
            dependencies=[],
        )

        # Initialize parent class
        super().__init__(metadata, context)

        # Module-specific state
        self._is_initialized = False
        self._data_processed = 0
        self._custom_config = {}

        # set default configuration
        self.config_manager.set_default_configuration(
            {
                "processing_enabled": True,
                "batch_size": 100,
                "timeout_seconds": 30,
                "custom_setting": "default_value",
            }
        )

    # Required abstract method implementations

    def get_module_info(self: Self) -> dict[str, Any]:
        """Get detailed module information."""
        return {
            "name": self.metadata.name,
            "id": self.metadata.id,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "vendor": self.metadata.vendor,
            "scopes": [scope.value for scope in self.metadata.scopes],
            "is_initialized": self._is_initialized,
            "data_processed": self._data_processed,
            "configuration": self.config_manager.config,
            "uptime": self.lifecycle_manager.uptime.total_seconds(),
            "health_status": self.diagnostics_manager.health_status,
        }

    def validate_configuration(self: Self) -> bool:
        """Validate module configuration."""
        try:
            config = self.config_manager.config

            # Check required settings
            if not isinstance(config.get("processing_enabled"), bool):
                self.logger.error("processing_enabled must be a boolean")
                return False

            batch_size = config.get("batch_size", 0)
            if not isinstance(batch_size, int) or batch_size <= 0:
                self.logger.error("batch_size must be a positive integer")
                return False

            timeout = config.get("timeout_seconds", 0)
            if not isinstance(timeout, int | float) or timeout <= 0:
                self.logger.error("timeout_seconds must be a positive number")
                return False

            self.logger.info("Configuration validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False

    def initialize_module(self: Self) -> bool:
        """Initialize the module."""
        try:
            self.logger.info("Initializing Basic Example Module")

            # Load custom configuration
            self._custom_config = self.config_manager.config.copy()

            # Initialize module-specific resources
            self._data_processed = 0

            # Perform any setup tasks
            self._setup_data_processing()

            self._is_initialized = True
            self.logger.info("Basic Example Module initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Module initialization failed: {e}")
            self.diagnostics_manager.log_error(e, "Module initialization")
            return False

    def startup_module(self: Self) -> bool:
        """Start the module."""
        try:
            if not self._is_initialized:
                self.logger.error("Cannot start module - not initialized")
                return False

            self.logger.info("Starting Basic Example Module")

            # Start processing if enabled
            if self._custom_config.get("processing_enabled", False):
                self._start_processing()

            self.logger.info("Basic Example Module started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Module startup failed: {e}")
            self.diagnostics_manager.log_error(e, "Module startup")
            return False

    def shutdown_module(self: Self) -> bool:
        """Shutdown the module."""
        try:
            self.logger.info("Shutting down Basic Example Module")

            # Stop processing
            self._stop_processing()

            # Clean up resources
            self._cleanup_resources()

            self.logger.info("Basic Example Module shutdown successfully")
            return True

        except Exception as e:
            self.logger.error(f"Module shutdown failed: {e}")
            self.diagnostics_manager.log_error(e, "Module shutdown")
            return False

    def configure_module(self: Self, config: dict[str, Any]) -> bool:
        """Configure the module with new settings."""
        try:
            self.logger.info("Configuring Basic Example Module")

            # Update custom configuration
            self._custom_config.update(config)

            # Apply configuration changes
            if "processing_enabled" in config:
                if config["processing_enabled"] and self.state.value == "running":
                    self._start_processing()
                elif not config["processing_enabled"]:
                    self._stop_processing()

            if "batch_size" in config:
                self.logger.info(f"Updated batch size to {config['batch_size']}")

            if "timeout_seconds" in config:
                self.logger.info(
                    f"Updated timeout to {config['timeout_seconds']} seconds"
                )

            self.logger.info("Basic Example Module configured successfully")
            return True

        except Exception as e:
            self.logger.error(f"Module configuration failed: {e}")
            self.diagnostics_manager.log_error(e, "Module configuration")
            return False

    # Optional hook implementations

    def create_gateway_hook(self: Self):
        """Create Gateway-specific functionality."""
        self.logger.info("Creating Gateway hook for Basic Example Module")

        # In a real implementation, this would return a Gateway hook class
        # that implements Gateway-specific functionality
        class BasicGatewayHook:
            def __init__(self: Self, module: Any):
                self.module = module
                self.logger = module.logger

            def startup(self: Self):
                self.logger.info("Gateway hook started")
                # Initialize Gateway-specific resources

            def shutdown(self: Self):
                self.logger.info("Gateway hook shutdown")
                # Clean up Gateway-specific resources

        return BasicGatewayHook(self)

    def create_designer_hook(self: Self):
        """Create Designer-specific functionality."""
        self.logger.info("Creating Designer hook for Basic Example Module")

        # In a real implementation, this would return a Designer hook class
        # that implements Designer-specific functionality
        class BasicDesignerHook:
            def __init__(self: Self, module: Any):
                self.module = module
                self.logger = module.logger

            def startup(self: Self):
                self.logger.info("Designer hook started")
                # Initialize Designer-specific resources

            def shutdown(self: Self):
                self.logger.info("Designer hook shutdown")
                # Clean up Designer-specific resources

        return BasicDesignerHook(self)

    # Module-specific methods

    def _setup_data_processing(self: Self):
        """Set up data processing components."""
        self.logger.debug("Setting up data processing")

        # Initialize processing components based on configuration
        batch_size = self._custom_config.get("batch_size", 100)
        timeout = self._custom_config.get("timeout_seconds", 30)

        self.logger.debug(
            f"Data processing setup complete - batch_size: {batch_size}, timeout: {timeout}"
        )

    def _start_processing(self: Self):
        """Start data processing."""
        if self._custom_config.get("processing_enabled", False):
            self.logger.info("Starting data processing")
            # In a real implementation, this would start background processing
        else:
            self.logger.info("Data processing disabled in configuration")

    def _stop_processing(self: Self):
        """Stop data processing."""
        self.logger.info("Stopping data processing")
        # In a real implementation, this would stop background processing

    def _cleanup_resources(self: Self):
        """Clean up module resources."""
        self.logger.debug("Cleaning up module resources")
        # Clean up any resources allocated during initialization

    # Public API methods

    def process_data(self: Self, data: Any) -> bool:
        """Process data using module functionality.

        Args:
            data: Data to process

        Returns:
            True if processing successful, False otherwise
        """
        try:
            if not self._custom_config.get("processing_enabled", False):
                self.logger.warning("Data processing is disabled")
                return False

            # Simulate data processing
            self._data_processed += 1
            self.logger.debug(f"Processed data item {self._data_processed}")

            return True

        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            self.diagnostics_manager.log_error(e, "Data processing")
            return False

    def get_processing_stats(self: Self) -> dict[str, Any]:
        """Get processing statistics.

        Returns:
            Dictionary containing processing statistics
        """
        return {
            "data_processed": self._data_processed,
            "processing_enabled": self._custom_config.get("processing_enabled", False),
            "batch_size": self._custom_config.get("batch_size", 100),
            "timeout_seconds": self._custom_config.get("timeout_seconds", 30),
        }

    def reset_processing_stats(self: Self):
        """Reset processing statistics."""
        self._data_processed = 0
        self.logger.info("Processing statistics reset")


# Factory function for creating module instances
def create_basic_example_module(
    module_path: Path,
    config_path: Path,
    data_path: Path,
    log_path: Path,
    temp_path: Path,
) -> BasicExampleModule:
    """Create a BasicExampleModule instance.

    Args:
        module_path: Path to module files
        config_path: Path to configuration files
        data_path: Path to data files
        log_path: Path to log files
        temp_path: Path to temporary files

    Returns:
        Configured BasicExampleModule instance
    """
    context = ModuleContext(
        module_path=module_path,
        config_path=config_path,
        data_path=data_path,
        log_path=log_path,
        temp_path=temp_path,
    )

    return BasicExampleModule(context)
