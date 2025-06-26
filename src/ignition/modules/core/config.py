"""Module configuration management for Ignition modules."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from .abstract_module import AbstractIgnitionModule


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""

    pass


class ConfigurationValidator:
    """Validates module configuration data."""

    def __init__(self: Self):
        """Initialize the configuration validator."""
        self._validators: dict[str, callable] = {}
        self._required_keys: list[str] = []
        self._optional_keys: list[str] = []

    def add_validator(self: Self, key: str, validator: callable) -> Any:
        """Add a validator function for a configuration key.

        Args:
            key: Configuration key to validate
            validator: Function that takes a value and returns True if valid
        """
        self._validators[key] = validator

    def add_required_key(self: Self, key: str) -> Any:
        """Add a required configuration key.

        Args:
            key: Configuration key that must be present
        """
        if key not in self._required_keys:
            self._required_keys.append(key)

    def add_optional_key(self: Self, key: str) -> Any:
        """Add an optional configuration key.

        Args:
            key: Configuration key that may be present
        """
        if key not in self._optional_keys:
            self._optional_keys.append(key)

    def validate(self: Self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate configuration data.

        Args:
            config: Configuration dictionary to validate

        Returns:
            tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required keys
        for key in self._required_keys:
            if key not in config:
                errors.append(f"Required configuration key missing: {key}")

        # Validate individual keys
        for key, value in config.items():
            if key in self._validators:
                try:
                    if not self._validators[key](value):
                        errors.append(f"Invalid value for {key}: {value}")
                except Exception as e:
                    errors.append(f"Validation error for {key}: {e}")

        return len(errors) == 0, errors


class ModuleConfigurationManager:
    """Manages configuration persistence and validation for Ignition modules.

    This class provides comprehensive configuration management including:
    - Configuration loading and saving
    - Validation and schema enforcement
    - Environment variable integration
    - Configuration versioning and migration
    - Backup and recovery
    """

    def __init__(self: Self, module: "AbstractIgnitionModule"):
        """Initialize the configuration manager.

        Args:
            module: The module instance to manage configuration for
        """
        self._module = module
        self._config_path = module.context.config_path
        self._config_file = self._config_path / f"{module.metadata.id}.json"
        self._backup_dir = self._config_path / "backups"

        # Current configuration
        self._config: dict[str, Any] = {}
        self._default_config: dict[str, Any] = {}
        self._config_loaded = False
        self._config_version = "1.0"

        # Configuration validation
        self._validator = ConfigurationValidator()
        self._setup_default_validation()

        # Configuration history
        self._config_history: list[dict[str, Any]] = []
        self._max_history = 10

        # Environment variable prefix
        self._env_prefix = f"IGN_{module.metadata.id.upper().replace('-', '_')}_"

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self: Self) -> None:
        """Ensure configuration directories exist."""
        self._config_path.mkdir(parents=True, exist_ok=True)
        self._backup_dir.mkdir(parents=True, exist_ok=True)

    def _setup_default_validation(self: Self) -> None:
        """Set up default configuration validation rules."""
        # Add common validation rules
        self._validator.add_required_key("module_id")
        self._validator.add_required_key("version")
        self._validator.add_optional_key("enabled")
        self._validator.add_optional_key("debug_mode")
        self._validator.add_optional_key("log_level")

        # Add validators
        self._validator.add_validator("module_id", lambda x: isinstance(x, str) and len(x) > 0)
        self._validator.add_validator("version", lambda x: isinstance(x, str) and len(x) > 0)
        self._validator.add_validator("enabled", lambda x: isinstance(x, bool))
        self._validator.add_validator("debug_mode", lambda x: isinstance(x, bool))
        self._validator.add_validator(
            "log_level",
            lambda x: x in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )

    # Properties

    @property
    def config(self: Self) -> dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()

    @property
    def config_file(self: Self) -> Path:
        """Get configuration file path."""
        return self._config_file

    @property
    def is_configuration_loaded(self: Self) -> bool:
        """Check if configuration is loaded."""
        return self._config_loaded

    @property
    def validator(self: Self) -> ConfigurationValidator:
        """Get configuration validator."""
        return self._validator

    # Default configuration management

    def set_default_configuration(self: Self, config: dict[str, Any]) -> Any:
        """Set default configuration values.

        Args:
            config: Default configuration dictionary
        """
        self._default_config = config.copy()
        self._module.logger.info("Default configuration set")

    def get_default_configuration(self: Self) -> dict[str, Any]:
        """Get default configuration.

        Returns:
            Default configuration dictionary
        """
        base_defaults = {
            "module_id": self._module.metadata.id,
            "version": self._module.metadata.version,
            "enabled": True,
            "debug_mode": False,
            "log_level": "INFO",
            "created_at": datetime.now().isoformat(),
        }

        # Merge with user-defined defaults
        base_defaults.update(self._default_config)
        return base_defaults

    # Configuration loading and saving

    def load_configuration(self: Self) -> bool:
        """Load configuration from file.

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self._config_file.exists():
                self._module.logger.info(f"Loading configuration from {self._config_file}")

                with open(self._config_file, encoding="utf-8") as f:
                    file_config = json.load(f)

                # Start with defaults
                self._config = self.get_default_configuration()

                # Override with file configuration
                self._config.update(file_config)

                # Override with environment variables
                self._apply_environment_variables()

                # Validate configuration
                is_valid, errors = self._validator.validate(self._config)
                if not is_valid:
                    self._module.logger.error(f"Configuration validation failed: {errors}")
                    return False

                self._config_loaded = True
                self._module.logger.info("Configuration loaded successfully")
                return True
            else:
                # No config file exists, use defaults
                self._module.logger.info("No configuration file found, using defaults")
                self._config = self.get_default_configuration()
                self._apply_environment_variables()

                # Save default configuration
                if self.save_configuration(self._config):
                    self._config_loaded = True
                    return True
                else:
                    return False

        except Exception as e:
            self._module.logger.exception(f"Failed to load configuration: {e}")
            return False

    def save_configuration(self: Self, config: dict[str, Any] | None = None) -> bool:
        """Save configuration to file.

        Args:
            config: Configuration to save (uses current config if None)

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            config_to_save = config or self._config

            # Validate before saving
            is_valid, errors = self._validator.validate(config_to_save)
            if not is_valid:
                raise ConfigurationError(f"Configuration validation failed: {errors}")

            # Create backup of existing configuration
            if self._config_file.exists():
                self._create_backup()

            # Add metadata
            config_with_metadata = config_to_save.copy()
            config_with_metadata.update(
                {
                    "config_version": self._config_version,
                    "last_modified": datetime.now().isoformat(),
                    "module_metadata": {
                        "name": self._module.metadata.name,
                        "id": self._module.metadata.id,
                        "version": self._module.metadata.version,
                    },
                }
            )

            # Save to file
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(config_with_metadata, f, indent=2, sort_keys=True)

            # Update current configuration
            self._config = config_to_save.copy()

            # Add to history
            self._add_to_history(config_to_save)

            self._module.logger.info(f"Configuration saved to {self._config_file}")
            return True

        except Exception as e:
            self._module.logger.exception(f"Failed to save configuration: {e}")
            return False

    def reload_configuration(self: Self) -> bool:
        """Reload configuration from file.

        Returns:
            True if reloaded successfully, False otherwise
        """
        self._module.logger.info("Reloading configuration")
        self._config_loaded = False
        return self.load_configuration()

    # Environment variable integration

    def _apply_environment_variables(self: Self) -> Any:
        """Apply environment variable overrides to configuration."""
        env_overrides = {}

        for key, value in os.environ.items():
            if key.startswith(self._env_prefix):
                config_key = key[len(self._env_prefix) :].lower()

                # Try to parse as JSON first, then as string
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    parsed_value = value

                env_overrides[config_key] = parsed_value

        if env_overrides:
            self._module.logger.info(f"Applying environment variable overrides: {list(env_overrides.keys())}")
            self._config.update(env_overrides)

    def get_environment_prefix(self: Self) -> str:
        """Get environment variable prefix for this module.

        Returns:
            Environment variable prefix
        """
        return self._env_prefix

    # Configuration access methods

    def get(self: Self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def set(self: Self, key: str, value: Any, save: bool = True) -> bool:
        """Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            save: Whether to save configuration immediately

        Returns:
            True if set successfully, False otherwise
        """
        try:
            self._config[key] = value

            if save:
                return self.save_configuration()

            return True

        except Exception as e:
            self._module.logger.exception(f"Failed to set configuration {key}: {e}")
            return False

    def update(self: Self, updates: dict[str, Any], save: bool = True) -> bool:
        """Update multiple configuration values.

        Args:
            updates: Dictionary of updates to apply
            save: Whether to save configuration immediately

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            self._config.update(updates)

            if save:
                return self.save_configuration()

            return True

        except Exception as e:
            self._module.logger.exception(f"Failed to update configuration: {e}")
            return False

    def remove(self: Self, key: str, save: bool = True) -> bool:
        """Remove configuration value.

        Args:
            key: Configuration key to remove
            save: Whether to save configuration immediately

        Returns:
            True if removed successfully, False otherwise
        """
        try:
            if key in self._config:
                del self._config[key]

                if save:
                    return self.save_configuration()

            return True

        except Exception as e:
            self._module.logger.exception(f"Failed to remove configuration {key}: {e}")
            return False

    # Backup and recovery

    def _create_backup(self: Self) -> Any:
        """Create backup of current configuration."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self._backup_dir / f"{self._module.metadata.id}_{timestamp}.json"

            if self._config_file.exists():
                import shutil

                shutil.copy2(self._config_file, backup_file)
                self._module.logger.info(f"Configuration backup created: {backup_file}")

        except Exception as e:
            self._module.logger.warning(f"Failed to create configuration backup: {e}")

    def list_backups(self: Self) -> list[Path]:
        """List available configuration backups.

        Returns:
            list of backup file paths
        """
        pattern = f"{self._module.metadata.id}_*.json"
        return sorted(self._backup_dir.glob(pattern), reverse=True)

    def restore_backup(self: Self, backup_file: Path) -> bool:
        """Restore configuration from backup.

        Args:
            backup_file: Path to backup file

        Returns:
            True if restored successfully, False otherwise
        """
        try:
            if not backup_file.exists():
                raise ConfigurationError(f"Backup file not found: {backup_file}")

            # Create backup of current config
            self._create_backup()

            # Copy backup to current config
            import shutil

            shutil.copy2(backup_file, self._config_file)

            # Reload configuration
            if self.reload_configuration():
                self._module.logger.info(f"Configuration restored from backup: {backup_file}")
                return True
            else:
                raise ConfigurationError("Failed to load restored configuration")

        except Exception as e:
            self._module.logger.exception(f"Failed to restore backup: {e}")
            return False

    def cleanup_backups(self: Self, keep_count: int = 5) -> Any:
        """Clean up old backup files.

        Args:
            keep_count: Number of backups to keep
        """
        try:
            backups = self.list_backups()

            if len(backups) > keep_count:
                for backup in backups[keep_count:]:
                    backup.unlink()
                    self._module.logger.info(f"Deleted old backup: {backup}")

        except Exception as e:
            self._module.logger.warning(f"Failed to cleanup backups: {e}")

    # Configuration history

    def _add_to_history(self: Self, config: dict[str, Any]) -> Any:
        """Add configuration to history.

        Args:
            config: Configuration to add to history
        """
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "config": config.copy(),
        }

        self._config_history.append(history_entry)

        # Trim history if needed
        if len(self._config_history) > self._max_history:
            self._config_history = self._config_history[-self._max_history :]

    def get_configuration_history(self: Self) -> list[dict[str, Any]]:
        """Get configuration history.

        Returns:
            list of historical configurations
        """
        return self._config_history.copy()

    def rollback_configuration(self: Self, steps: int = 1) -> bool:
        """Rollback configuration to previous version.

        Args:
            steps: Number of steps to rollback

        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if len(self._config_history) < steps:
                raise ConfigurationError(f"Not enough history for {steps} step rollback")

            # Get previous configuration
            target_index = -(steps + 1)
            previous_config = self._config_history[target_index]["config"]

            # Apply previous configuration
            if self.save_configuration(previous_config):
                self._module.logger.info(f"Configuration rolled back {steps} steps")
                return True
            else:
                raise ConfigurationError("Failed to save rolled back configuration")

        except Exception as e:
            self._module.logger.exception(f"Failed to rollback configuration: {e}")
            return False

    # Utility methods

    def export_configuration(self: Self, export_path: Path) -> bool:
        """Export configuration to file.

        Args:
            export_path: Path to export configuration to

        Returns:
            True if exported successfully, False otherwise
        """
        try:
            export_data = {
                "module_metadata": {
                    "name": self._module.metadata.name,
                    "id": self._module.metadata.id,
                    "version": self._module.metadata.version,
                },
                "config_version": self._config_version,
                "exported_at": datetime.now().isoformat(),
                "configuration": self._config.copy(),
            }

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, sort_keys=True)

            self._module.logger.info(f"Configuration exported to {export_path}")
            return True

        except Exception as e:
            self._module.logger.exception(f"Failed to export configuration: {e}")
            return False

    def import_configuration(self: Self, import_path: Path) -> bool:
        """Import configuration from file.

        Args:
            import_path: Path to import configuration from

        Returns:
            True if imported successfully, False otherwise
        """
        try:
            with open(import_path, encoding="utf-8") as f:
                import_data = json.load(f)

            if "configuration" not in import_data:
                raise ConfigurationError("Invalid configuration file format")

            imported_config = import_data["configuration"]

            # Validate imported configuration
            is_valid, errors = self._validator.validate(imported_config)
            if not is_valid:
                raise ConfigurationError(f"Imported configuration validation failed: {errors}")

            # Save imported configuration
            if self.save_configuration(imported_config):
                self._module.logger.info(f"Configuration imported from {import_path}")
                return True
            else:
                raise ConfigurationError("Failed to save imported configuration")

        except Exception as e:
            self._module.logger.exception(f"Failed to import configuration: {e}")
            return False

    def get_status(self: Self) -> dict[str, Any]:
        """Get configuration manager status.

        Returns:
            Dictionary containing status information
        """
        return {
            "config_loaded": self._config_loaded,
            "config_file": str(self._config_file),
            "config_exists": self._config_file.exists(),
            "config_size": len(self._config),
            "backup_count": len(self.list_backups()),
            "history_count": len(self._config_history),
            "env_prefix": self._env_prefix,
            "last_modified": self._config.get("last_modified"),
        }

    def __str__(self: Self) -> str:
        """String representation of the configuration manager."""
        return f"ConfigManager({self._module.metadata.name}, loaded={self._config_loaded})"

    def __repr__(self: Self) -> str:
        """Detailed string representation of the configuration manager."""
        return (
            f"ModuleConfigurationManager(module='{self._module.metadata.name}', "
            f"config_file='{self._config_file}', loaded={self._config_loaded}, "
            f"config_size={len(self._config)})"
        )
