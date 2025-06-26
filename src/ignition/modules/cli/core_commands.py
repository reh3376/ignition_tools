"""CLI commands for the core module framework."""

from pathlib import Path
from typing import Any

import click

from ignition.modules.examples.basic_module import create_basic_example_module


@click.group(name="core")
def core_group() -> None:
    """Core module framework commands."""
    pass


@core_group.command("demo")
@click.option(
    "--module-path",
    type=click.Path(exists=True, path_type=Path),
    default=Path.cwd() / "modules",
    help="Path to module files",
)
@click.option(
    "--config-path",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "config",
    help="Path to configuration files",
)
@click.option(
    "--data-path",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "data",
    help="Path to data files",
)
@click.option(
    "--log-path",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "logs",
    help="Path to log files",
)
@click.option(
    "--temp-path",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "temp",
    help="Path to temporary files",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def demo_command(
    module_path: Path,
    config_path: Path,
    data_path: Path,
    log_path: Path,
    temp_path: Path,
    verbose: bool,
):
    """Demonstrate the core module framework with BasicExampleModule."""
    click.echo("🚀 Core Module Framework Demo")
    click.echo("=" * 50)

    try:
        # Create module instance
        click.echo("Creating BasicExampleModule instance...")
        module = create_basic_example_module(
            module_path=module_path,
            config_path=config_path,
            data_path=data_path,
            log_path=log_path,
            temp_path=temp_path,
        )

        if verbose:
            module.diagnostics_manager.set_log_level("DEBUG")

        click.echo(f"✅ Module created: {module.metadata.name} v{module.metadata.version}")

        # Load configuration
        click.echo("\nLoading module configuration...")
        if module.config_manager.load_configuration():
            click.echo("✅ Configuration loaded successfully")
        else:
            click.echo("❌ Configuration loading failed")
            return

        # Validate configuration
        click.echo("\nValidating configuration...")
        if module.validate_configuration():
            click.echo("✅ Configuration validation passed")
        else:
            click.echo("❌ Configuration validation failed")
            return

        # Initialize module
        click.echo("\nInitializing module...")
        if module.initialize_module():
            click.echo("✅ Module initialized successfully")
        else:
            click.echo("❌ Module initialization failed")
            return

        # Start module
        click.echo("\nStarting module...")
        if module.startup_module():
            click.echo("✅ Module started successfully")
        else:
            click.echo("❌ Module startup failed")
            return

        # Demonstrate functionality
        click.echo("\nDemonstrating module functionality...")

        # Process some data
        for i in range(5):
            if module.process_data(f"test_data_{i}"):
                click.echo(f"  ✅ Processed data item {i + 1}")
            else:
                click.echo(f"  ❌ Failed to process data item {i + 1}")

        # Get module info
        click.echo("\nModule Information:")
        module_info = module.get_module_info()
        for key, value in module_info.items():
            if key == "configuration":
                click.echo(f"  {key}: <configuration data>")
            else:
                click.echo(f"  {key}: {value}")

        # Get processing stats
        click.echo("\nProcessing Statistics:")
        stats = module.get_processing_stats()
        for key, value in stats.items():
            click.echo(f"  {key}: {value}")

        # Health check
        click.echo("\nPerforming health check...")
        health = module.diagnostics_manager.check_health()
        click.echo(f"  Overall Status: {health['overall_status']}")
        click.echo(f"  Error Count: {health['error_count']}")
        click.echo(f"  Warning Count: {health['warning_count']}")

        # Lifecycle information
        click.echo("\nLifecycle Information:")
        lifecycle_stats = module.lifecycle_manager.get_statistics()
        click.echo(f"  Current State: {lifecycle_stats['current_state']}")
        click.echo(f"  Uptime: {lifecycle_stats['uptime_formatted']}")
        click.echo(f"  Restart Count: {lifecycle_stats['restart_count']}")
        click.echo(f"  Error Count: {lifecycle_stats['error_count']}")

        # Configuration management demo
        click.echo("\nDemonstrating configuration management...")

        # Update configuration
        new_config = {"batch_size": 150, "timeout_seconds": 45}
        if module.config_manager.update(new_config):
            click.echo("✅ Configuration updated successfully")
            click.echo(f"  New batch_size: {module.config_manager.get('batch_size')}")
            click.echo(f"  New timeout_seconds: {module.config_manager.get('timeout_seconds')}")
        else:
            click.echo("❌ Configuration update failed")

        # Demonstrate module reconfiguration
        if module.configure_module(new_config):
            click.echo("✅ Module reconfigured successfully")
        else:
            click.echo("❌ Module reconfiguration failed")

        # Stop module
        click.echo("\nStopping module...")
        if module.shutdown_module():
            click.echo("✅ Module stopped successfully")
        else:
            click.echo("❌ Module stop failed")

        # Final status
        click.echo("\nFinal Module Status:")
        click.echo(f"  State: {module.state.value}")
        click.echo(f"  Health: {module.diagnostics_manager.health_status}")

        click.echo("\n🎉 Core Module Framework Demo completed successfully!")

    except Exception as e:
        click.echo(f"\n❌ Demo failed with error: {e}")
        if verbose:
            import traceback

            click.echo(traceback.format_exc())


@core_group.command("test")
@click.option(
    "--module-path",
    type=click.Path(exists=True, path_type=Path),
    default=Path.cwd() / "modules",
    help="Path to module files",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def test_command(module_path: Path, verbose: bool) -> bool:
    """Test the core module framework components."""
    click.echo("🧪 Core Module Framework Tests")
    click.echo("=" * 50)

    test_results = []

    def run_test(test_name: str, test_func) -> bool:
        """Run a test and record the result."""
        try:
            click.echo(f"\nRunning test: {test_name}")
            result = test_func()
            if result:
                click.echo(f"  ✅ {test_name} PASSED")
                test_results.append((test_name, True, None))
                return True
            else:
                click.echo(f"  ❌ {test_name} FAILED")
                test_results.append((test_name, False, "Test returned False"))
                return False
        except Exception as e:
            click.echo(f"  ❌ {test_name} FAILED with exception: {e}")
            test_results.append((test_name, False, str(e)))
            if verbose:
                import traceback

                click.echo(f"    {traceback.format_exc()}")
            return False

    # Test 1: Module Creation
    def test_module_creation() -> Any:
        module = create_basic_example_module(
            module_path=module_path,
            config_path=module_path / "config",
            data_path=module_path / "data",
            log_path=module_path / "logs",
            temp_path=module_path / "temp",
        )
        return module is not None and module.metadata.name == "Basic Example Module"

    # Test 2: Configuration Loading
    def test_configuration_loading() -> Any:
        module = create_basic_example_module(
            module_path=module_path,
            config_path=module_path / "config",
            data_path=module_path / "data",
            log_path=module_path / "logs",
            temp_path=module_path / "temp",
        )
        return module.config_manager.load_configuration()

    # Test 3: Module Lifecycle
    def test_module_lifecycle() -> bool:
        module = create_basic_example_module(
            module_path=module_path,
            config_path=module_path / "config",
            data_path=module_path / "data",
            log_path=module_path / "logs",
            temp_path=module_path / "temp",
        )

        # Load config and initialize
        if not module.config_manager.load_configuration():
            return False

        if not module.initialize_module():
            return False

        if not module.startup_module():
            return False

        return module.shutdown_module()

    # Test 4: Health Monitoring
    def test_health_monitoring() -> Any:
        module = create_basic_example_module(
            module_path=module_path,
            config_path=module_path / "config",
            data_path=module_path / "data",
            log_path=module_path / "logs",
            temp_path=module_path / "temp",
        )

        health = module.diagnostics_manager.check_health()
        return isinstance(health, dict) and "overall_status" in health

    # Test 5: Configuration Management
    def test_configuration_management() -> bool:
        module = create_basic_example_module(
            module_path=module_path,
            config_path=module_path / "config",
            data_path=module_path / "data",
            log_path=module_path / "logs",
            temp_path=module_path / "temp",
        )

        # Load configuration
        if not module.config_manager.load_configuration():
            return False

        # Test setting and getting values
        if not module.config_manager.set("test_key", "test_value", save=False):
            return False

        return module.config_manager.get("test_key") == "test_value"

    # Run all tests
    run_test("Module Creation", test_module_creation)
    run_test("Configuration Loading", test_configuration_loading)
    run_test("Module Lifecycle", test_module_lifecycle)
    run_test("Health Monitoring", test_health_monitoring)
    run_test("Configuration Management", test_configuration_management)

    # Summary
    click.echo("\n" + "=" * 50)
    click.echo("Test Results Summary:")

    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)

    for test_name, success, error in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        click.echo(f"  {status}: {test_name}")
        if not success and error and verbose:
            click.echo(f"    Error: {error}")

    click.echo(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        click.echo("🎉 All tests passed!")
        return True
    else:
        click.echo("❌ Some tests failed")
        return False


@core_group.command("info")
def info_command() -> None:
    """Display information about the core module framework."""
    click.echo("📋 Core Module Framework Information")
    click.echo("=" * 50)

    click.echo("\n🏗️  Framework Components:")
    click.echo("  • AbstractIgnitionModule - Base class for all modules")
    click.echo("  • ModuleLifecycleManager - Manages module lifecycle and health")
    click.echo("  • ModuleConfigurationManager - Handles configuration persistence")
    click.echo("  • ModuleDiagnosticsManager - Provides logging and diagnostics")

    click.echo("\n📊 Module States:")
    from ignition.modules.core.lifecycle import ModuleState

    for state in ModuleState:
        click.echo(f"  • {state.value}")

    click.echo("\n🎯 Module Scopes:")
    from ignition.modules.core.abstract_module import ModuleScope

    for scope in ModuleScope:
        click.echo(f"  • {scope.value} - {scope.name}")

    click.echo("\n🔧 Available Commands:")
    click.echo("  • ign module core demo - Run framework demonstration")
    click.echo("  • ign module core test - Run framework tests")
    click.echo("  • ign module core info - Show this information")

    click.echo("\n📁 Example Usage:")
    click.echo("  ign module core demo --verbose")
    click.echo("  ign module core test --module-path ./modules")

    click.echo("\n✨ Features:")
    click.echo("  • Comprehensive lifecycle management")
    click.echo("  • Configuration persistence with validation")
    click.echo("  • Health monitoring and diagnostics")
    click.echo("  • Structured logging with rotation")
    click.echo("  • Environment variable integration")
    click.echo("  • Backup and recovery capabilities")


# Register the command group
def register_commands(cli) -> None:
    """Register core framework commands with the CLI."""
    cli.add_command(core_group)

    # Register LLM Infrastructure commands (Phase 13.1)
    try:
        from ignition.modules.llm_infrastructure.cli_commands import (
            llm_infrastructure_cli,
        )

        cli.add_command(llm_infrastructure_cli)
    except ImportError:
        # LLM Infrastructure module not available
        pass
