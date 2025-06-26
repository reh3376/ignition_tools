"""MPC Framework CLI - Phase 14 Implementation.

This module provides command-line interface for the MPC Framework & Production Control system.

Following crawl_mcp.py methodology:
- Step 1: Environment validation before command execution
- Step 2: Input validation using Click parameter validation
- Step 3: Comprehensive error handling with user-friendly messages
- Step 4: Modular command structure with testing support
- Step 5: Progressive complexity with command grouping
- Step 6: Resource management with proper cleanup

Author: IGN Scripts Development Team
Version: 14.0.0
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .mpc_controller import (
    test_mpc_controller,
    validate_mpc_environment,
)
from .safety_system import (
    test_safety_system,
    validate_safety_environment,
)

# Configure logging
logger = logging.getLogger(__name__)
console = Console()


# Step 1: Environment Validation Commands (crawl_mpc.py methodology)
@click.group(name="mpc-framework")
def mpc_framework_cli() -> None:
    """Phase 14: MPC Framework & Production Control 🎛️

    Comprehensive Model Predictive Control framework with production control capabilities.

    Following crawl_mcp.py methodology for reliable industrial automation.
    """
    pass


@mpc_framework_cli.command("validate-env")
def validate_environment() -> None:
    """Step 1: Validate MPC Framework environment setup."""
    console.print(
        "[bold blue]🔍 Phase 14: MPC Framework Environment Validation[/bold blue]"
    )

    # Validate MPC environment
    console.print("\n[yellow]Validating MPC Controller Environment...[/yellow]")
    mpc_validation = validate_mpc_environment()

    if mpc_validation["valid"]:
        console.print("[green]✅ MPC Environment: VALID[/green]")
    else:
        console.print("[red]❌ MPC Environment: INVALID[/red]")
        for error in mpc_validation["errors"]:
            console.print(f"[red]  • {error}[/red]")

    if mpc_validation["warnings"]:
        console.print("[yellow]⚠️  MPC Warnings:[/yellow]")
        for warning in mpc_validation["warnings"]:
            console.print(f"[yellow]  • {warning}[/yellow]")

    # Validate Safety System environment
    console.print("\n[yellow]Validating Safety System Environment...[/yellow]")
    safety_validation = validate_safety_environment()

    if safety_validation["valid"]:
        console.print("[green]✅ Safety Environment: VALID[/green]")
    else:
        console.print("[red]❌ Safety Environment: INVALID[/red]")
        for error in safety_validation["errors"]:
            console.print(f"[red]  • {error}[/red]")

    if safety_validation["warnings"]:
        console.print("[yellow]⚠️  Safety Warnings:[/yellow]")
        for warning in safety_validation["warnings"]:
            console.print(f"[yellow]  • {warning}[/yellow]")

    # Overall status
    overall_valid = mpc_validation["valid"] and safety_validation["valid"]
    safety_critical = safety_validation.get("safety_critical", True)

    console.print("\n[bold]Overall Environment Status:[/bold]")
    if overall_valid:
        console.print("[bold green]✅ READY FOR PRODUCTION[/bold green]")
    else:
        console.print("[bold red]❌ ENVIRONMENT ISSUES DETECTED[/bold red]")

    if not safety_critical:
        console.print("[bold red]⚠️  SAFETY-CRITICAL ISSUES DETECTED[/bold red]")


# Step 2: MPC Controller Commands (crawl_mpc.py methodology)
@mpc_framework_cli.group("controller")
def controller_group() -> None:
    """MPC Controller management commands."""
    pass


@controller_group.command("create-config")
@click.option("--name", "-n", required=True, help="Configuration name")
@click.option(
    "--prediction-horizon", "-p", type=int, default=10, help="Prediction horizon"
)
@click.option("--control-horizon", "-c", type=int, default=3, help="Control horizon")
@click.option(
    "--sample-time", "-s", type=float, default=1.0, help="Sample time in seconds"
)
@click.option(
    "--model-type",
    "-m",
    type=click.Choice(["FOPDT", "StateSpace", "ARX"]),
    default="FOPDT",
    help="Process model type",
)
@click.option("--output", "-o", type=click.Path(), help="Output configuration file")
def create_controller_config(
    name: str,
    prediction_horizon: int,
    control_horizon: int,
    sample_time: float,
    model_type: str,
    output: str | None,
) -> None:
    """Create MPC controller configuration."""
    console.print(
        f"[bold blue]🎛️ Creating MPC Controller Configuration: {name}[/bold blue]"
    )

    try:
        # Step 2: Input validation
        if control_horizon > prediction_horizon:
            raise ValueError("Control horizon cannot exceed prediction horizon")

        if sample_time <= 0:
            raise ValueError("Sample time must be positive")

        # Create configuration
        config_data = {
            "name": name,
            "prediction_horizon": prediction_horizon,
            "control_horizon": control_horizon,
            "sample_time": sample_time,
            "Q": [[1.0]],  # Default output tracking weight
            "R": [[0.1]],  # Default control effort weight
            "process_model": {
                "model_type": model_type,
                "parameters": {
                    "gain": 1.0,
                    "time_constant": 5.0,
                    "dead_time": 1.0,
                },
                "sample_time": sample_time,
            },
            "constraints": {
                "u_min": [-100.0],
                "u_max": [100.0],
                "du_min": [-10.0],
                "du_max": [10.0],
                "y_min": [],
                "y_max": [],
            },
            "optimization_timeout": 5.0,
            "created_at": datetime.now().isoformat(),
        }

        # Display configuration
        config_table = Table(title=f"MPC Controller Configuration: {name}")
        config_table.add_column("Parameter", style="cyan")
        config_table.add_column("Value", style="green")
        config_table.add_column("Description", style="yellow")

        config_table.add_row(
            "Prediction Horizon", str(prediction_horizon), "Steps ahead to predict"
        )
        config_table.add_row(
            "Control Horizon", str(control_horizon), "Control moves to optimize"
        )
        config_table.add_row(
            "Sample Time", f"{sample_time:.1f}s", "Control execution interval"
        )
        config_table.add_row("Model Type", model_type, "Process model type")
        config_table.add_row("Optimization Timeout", "5.0s", "Maximum solver time")

        console.print(config_table)

        # Save configuration
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(config_data, f, indent=2)

            console.print(f"[green]✅ Configuration saved to: {output}[/green]")
        else:
            console.print("\n[yellow]Configuration JSON:[/yellow]")
            console.print(json.dumps(config_data, indent=2))

        console.print(
            "[green]✅ MPC controller configuration created successfully[/green]"
        )

    except Exception as e:
        console.print(f"[red]❌ Configuration creation failed: {e}[/red]")


@controller_group.command("test")
@click.option(
    "--config-file", "-c", type=click.Path(exists=True), help="Configuration file"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def test_controller(config_file: str | None, verbose: bool) -> None:
    """Test MPC controller functionality."""
    console.print("[bold blue]🧪 Testing MPC Controller[/bold blue]")

    async def run_test():
        try:
            # Run controller test
            test_result = await test_mpc_controller()

            if test_result.success:
                console.print(
                    f"[green]✅ MPC Controller test passed in {test_result.execution_time:.2f}s[/green]"
                )

                if verbose and test_result.performance_metrics:
                    metrics_table = Table(title="Performance Metrics")
                    metrics_table.add_column("Metric", style="cyan")
                    metrics_table.add_column("Value", style="green")

                    for metric, value in test_result.performance_metrics.items():
                        metrics_table.add_row(metric, str(value))

                    console.print(metrics_table)
            else:
                console.print(
                    f"[red]❌ MPC Controller test failed: {test_result.error_message}[/red]"
                )

        except Exception as e:
            console.print(f"[red]❌ Test execution failed: {e}[/red]")

    asyncio.run(run_test())


# Step 3: Safety System Commands (crawl_mpc.py methodology)
@mpc_framework_cli.group("safety")
def safety_group() -> None:
    """Safety system management commands."""
    pass


@safety_group.command("create-config")
@click.option("--name", "-n", required=True, help="Safety system name")
@click.option(
    "--safety-level",
    "-l",
    type=click.Choice(["SIL_1", "SIL_2", "SIL_3", "SIL_4"]),
    default="SIL_2",
    help="Safety integrity level",
)
@click.option(
    "--watchdog-interval", "-w", type=float, default=1.0, help="Watchdog check interval"
)
@click.option("--output", "-o", type=click.Path(), help="Output configuration file")
def create_safety_config(
    name: str,
    safety_level: str,
    watchdog_interval: float,
    output: str | None,
) -> None:
    """Create safety system configuration."""
    console.print(
        f"[bold blue]🛡️ Creating Safety System Configuration: {name}[/bold blue]"
    )

    try:
        # Step 2: Input validation
        if watchdog_interval <= 0:
            raise ValueError("Watchdog interval must be positive")

        # Create configuration
        config_data = {
            "system_name": name,
            "safety_level": safety_level,
            "watchdog_interval": watchdog_interval,
            "emergency_timeout": 5.0,
            "safety_limits": [
                {
                    "parameter_name": "temperature",
                    "high_limit": 85.0,
                    "safety_level": safety_level,
                    "alarm_priority": "HIGH",
                    "time_delay": 0.0,
                    "hysteresis": 2.0,
                },
                {
                    "parameter_name": "pressure",
                    "high_limit": 100.0,
                    "safety_level": safety_level,
                    "alarm_priority": "CRITICAL",
                    "time_delay": 0.0,
                    "hysteresis": 5.0,
                },
            ],
            "emergency_procedures": [
                {
                    "procedure_id": "emergency_shutdown",
                    "name": "Emergency Shutdown",
                    "trigger_conditions": ["critical alarm", "system failure"],
                    "safety_level": safety_level,
                    "timeout_seconds": 10.0,
                    "steps": [
                        "Stop all control outputs",
                        "Close emergency valves",
                        "Activate safety alarms",
                        "Notify operators",
                    ],
                    "verification_required": True,
                },
            ],
            "notification_endpoints": ["operator@company.com", "safety@company.com"],
            "escalation_enabled": True,
            "created_at": datetime.now().isoformat(),
        }

        # Display configuration
        config_table = Table(title=f"Safety System Configuration: {name}")
        config_table.add_column("Parameter", style="cyan")
        config_table.add_column("Value", style="green")
        config_table.add_column("Description", style="yellow")

        config_table.add_row("System Name", name, "Safety system identifier")
        config_table.add_row("Safety Level", safety_level, "Safety integrity level")
        config_table.add_row(
            "Watchdog Interval", f"{watchdog_interval:.1f}s", "Monitoring frequency"
        )
        config_table.add_row(
            "Safety Limits",
            str(len(config_data["safety_limits"])),
            "Monitored parameters",
        )
        config_table.add_row(
            "Emergency Procedures",
            str(len(config_data["emergency_procedures"])),
            "Configured procedures",
        )

        console.print(config_table)

        # Save configuration
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(config_data, f, indent=2)

            console.print(f"[green]✅ Configuration saved to: {output}[/green]")
        else:
            console.print("\n[yellow]Configuration JSON:[/yellow]")
            console.print(json.dumps(config_data, indent=2))

        console.print(
            "[green]✅ Safety system configuration created successfully[/green]"
        )

    except Exception as e:
        console.print(f"[red]❌ Configuration creation failed: {e}[/red]")


@safety_group.command("test")
@click.option(
    "--config-file", "-c", type=click.Path(exists=True), help="Configuration file"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def test_safety_system_cmd(config_file: str | None, verbose: bool) -> None:
    """Test safety system functionality."""
    console.print("[bold blue]🧪 Testing Safety System[/bold blue]")

    async def run_test():
        try:
            # Run safety system test
            test_result = await test_safety_system()

            if test_result["success"]:
                console.print(
                    f"[green]✅ Safety system test passed in {test_result['execution_time']:.2f}s[/green]"
                )

                if verbose and "tests_passed" in test_result:
                    tests_table = Table(title="Tests Passed")
                    tests_table.add_column("Test", style="cyan")
                    tests_table.add_column("Status", style="green")

                    for test in test_result["tests_passed"]:
                        tests_table.add_row(test, "✅ PASSED")

                    console.print(tests_table)
            else:
                console.print(
                    f"[red]❌ Safety system test failed: {test_result['error']}[/red]"
                )

        except Exception as e:
            console.print(f"[red]❌ Test execution failed: {e}[/red]")

    asyncio.run(run_test())


# Step 4: Status and Monitoring Commands (crawl_mpc.py methodology)
@mpc_framework_cli.command("status")
@click.option("--show-config", is_flag=True, help="Show configuration details")
@click.option("--show-performance", is_flag=True, help="Show performance metrics")
@click.option("--show-alarms", is_flag=True, help="Show active alarms")
def show_status(show_config: bool, show_performance: bool, show_alarms: bool) -> None:
    """Show MPC Framework system status."""
    console.print("[bold blue]📊 MPC Framework System Status[/bold blue]")

    # Environment status
    console.print("\n[yellow]Environment Status:[/yellow]")
    mpc_validation = validate_mpc_environment()
    safety_validation = validate_safety_environment()

    status_table = Table()
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="white")
    status_table.add_column("Issues", style="yellow")

    mpc_status = "✅ VALID" if mpc_validation["valid"] else "❌ INVALID"
    mpc_issues = len(mpc_validation["errors"]) + len(mpc_validation["warnings"])

    safety_status = "✅ VALID" if safety_validation["valid"] else "❌ INVALID"
    safety_issues = len(safety_validation["errors"]) + len(
        safety_validation["warnings"]
    )

    status_table.add_row("MPC Controller", mpc_status, str(mpc_issues))
    status_table.add_row("Safety System", safety_status, str(safety_issues))

    console.print(status_table)

    # Configuration details
    if show_config:
        console.print("\n[yellow]Configuration Status:[/yellow]")
        config_panel = Panel(
            "[bold]MPC Framework Configuration[/bold]\n\n"
            "• MPC Controller: Not configured\n"
            "• Safety System: Not configured\n"
            "• Performance Monitor: Not configured\n"
            "• Production Scheduler: Not configured\n\n"
            "[dim]Use 'create-config' commands to set up components[/dim]",
            title="📋 Configuration",
            border_style="blue",
        )
        console.print(config_panel)

    # Performance metrics
    if show_performance:
        console.print("\n[yellow]Performance Metrics:[/yellow]")
        perf_panel = Panel(
            "[bold]System Performance[/bold]\n\n"
            "• Average Response Time: N/A\n"
            "• Success Rate: N/A\n"
            "• Memory Usage: N/A\n"
            "• CPU Usage: N/A\n\n"
            "[dim]Start controllers to collect metrics[/dim]",
            title="📈 Performance",
            border_style="green",
        )
        console.print(perf_panel)

    # Active alarms
    if show_alarms:
        console.print("\n[yellow]Active Alarms:[/yellow]")
        alarm_panel = Panel(
            "[bold]Alarm Status[/bold]\n\n• No active alarms\n\n[dim]Start safety system to monitor alarms[/dim]",
            title="🚨 Alarms",
            border_style="red",
        )
        console.print(alarm_panel)


# Step 5: Integration Commands (crawl_mpc.py methodology)
@mpc_framework_cli.command("run-test-suite")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--output", "-o", type=click.Path(), help="Test results output file")
def run_test_suite(verbose: bool, output: str | None) -> None:
    """Run comprehensive MPC Framework test suite."""
    console.print("[bold blue]🧪 Running MPC Framework Test Suite[/bold blue]")

    async def run_tests():
        test_results = []
        start_time = datetime.now()

        try:
            # Test 1: Environment validation
            console.print("\n[yellow]Test 1: Environment Validation[/yellow]")
            mpc_env = validate_mpc_environment()
            safety_env = validate_safety_environment()

            env_test = {
                "test_name": "Environment Validation",
                "success": mpc_env["valid"] and safety_env["valid"],
                "details": {
                    "mpc_valid": mpc_env["valid"],
                    "safety_valid": safety_env["valid"],
                    "mpc_errors": mpc_env["errors"],
                    "safety_errors": safety_env["errors"],
                },
            }
            test_results.append(env_test)

            if env_test["success"]:
                console.print("[green]✅ Environment validation passed[/green]")
            else:
                console.print("[red]❌ Environment validation failed[/red]")

            # Test 2: MPC Controller
            console.print("\n[yellow]Test 2: MPC Controller[/yellow]")
            mpc_test = await test_mpc_controller()
            test_results.append(
                {
                    "test_name": "MPC Controller",
                    "success": mpc_test.success,
                    "execution_time": mpc_test.execution_time,
                    "error": mpc_test.error_message,
                    "performance_metrics": mpc_test.performance_metrics,
                }
            )

            if mpc_test.success:
                console.print(
                    f"[green]✅ MPC Controller test passed ({mpc_test.execution_time:.2f}s)[/green]"
                )
            else:
                console.print(
                    f"[red]❌ MPC Controller test failed: {mpc_test.error_message}[/red]"
                )

            # Test 3: Safety System
            console.print("\n[yellow]Test 3: Safety System[/yellow]")
            safety_test = await test_safety_system()
            test_results.append(
                {
                    "test_name": "Safety System",
                    "success": safety_test["success"],
                    "execution_time": safety_test["execution_time"],
                    "error": safety_test.get("error"),
                    "tests_passed": safety_test.get("tests_passed", []),
                }
            )

            if safety_test["success"]:
                console.print(
                    f"[green]✅ Safety System test passed ({safety_test['execution_time']:.2f}s)[/green]"
                )
            else:
                console.print(
                    f"[red]❌ Safety System test failed: {safety_test['error']}[/red]"
                )

            # Test summary
            total_time = (datetime.now() - start_time).total_seconds()
            passed_tests = sum(1 for test in test_results if test["success"])
            total_tests = len(test_results)

            console.print("\n[bold]Test Suite Summary:[/bold]")
            console.print(f"Tests Passed: {passed_tests}/{total_tests}")
            console.print(f"Total Time: {total_time:.2f}s")

            if passed_tests == total_tests:
                console.print("[bold green]✅ ALL TESTS PASSED[/bold green]")
            else:
                console.print("[bold red]❌ SOME TESTS FAILED[/bold red]")

            # Detailed results
            if verbose:
                results_table = Table(title="Detailed Test Results")
                results_table.add_column("Test", style="cyan")
                results_table.add_column("Status", style="white")
                results_table.add_column("Time", style="yellow")
                results_table.add_column("Details", style="white")

                for test in test_results:
                    status = "✅ PASS" if test["success"] else "❌ FAIL"
                    time_str = f"{test.get('execution_time', 0):.2f}s"
                    details = test.get("error", "OK") if not test["success"] else "OK"

                    results_table.add_row(test["test_name"], status, time_str, details)

                console.print(results_table)

            # Save results
            if output:
                results_data = {
                    "test_suite": "MPC Framework",
                    "timestamp": start_time.isoformat(),
                    "total_time": total_time,
                    "tests_passed": passed_tests,
                    "total_tests": total_tests,
                    "results": test_results,
                }

                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "w") as f:
                    json.dump(results_data, f, indent=2)

                console.print(f"[green]✅ Test results saved to: {output}[/green]")

        except Exception as e:
            console.print(f"[red]❌ Test suite execution failed: {e}[/red]")

    asyncio.run(run_tests())


# Step 6: Resource Management Commands (crawl_mpc.py methodology)
@mpc_framework_cli.command("cleanup")
@click.option("--temp-files", is_flag=True, help="Clean temporary files")
@click.option("--logs", is_flag=True, help="Clean log files")
@click.option("--all", "clean_all", is_flag=True, help="Clean all resources")
def cleanup_resources(temp_files: bool, logs: bool, clean_all: bool) -> None:
    """Clean up MPC Framework resources."""
    console.print("[bold blue]🧹 Cleaning MPC Framework Resources[/bold blue]")

    try:
        import os
        import shutil
        from pathlib import Path

        cleaned_items = []

        # Clean temporary files
        if temp_files or clean_all:
            temp_dir = Path(os.getenv("MPC_TEMP_DIR", "/tmp/mpc_framework"))
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                cleaned_items.append(f"Temporary directory: {temp_dir}")

        # Clean log files
        if logs or clean_all:
            log_dir = Path("logs/mpc_framework")
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_size > 100 * 1024 * 1024:  # > 100MB
                        log_file.unlink()
                        cleaned_items.append(f"Large log file: {log_file}")

        # Display results
        if cleaned_items:
            cleanup_table = Table(title="Cleaned Resources")
            cleanup_table.add_column("Resource", style="cyan")
            cleanup_table.add_column("Status", style="green")

            for item in cleaned_items:
                cleanup_table.add_row(item, "✅ Cleaned")

            console.print(cleanup_table)
        else:
            console.print("[yellow]No resources to clean[/yellow]")

        console.print("[green]✅ Resource cleanup completed[/green]")

    except Exception as e:
        console.print(f"[red]❌ Cleanup failed: {e}[/red]")


# Main CLI registration
class MPCFrameworkCLI:
    """MPC Framework CLI wrapper for integration."""

    @staticmethod
    def get_cli() -> click.Group:
        """Get the MPC Framework CLI group."""
        return mpc_framework_cli

    @staticmethod
    def register_commands(main_cli: click.Group) -> None:
        """Register MPC Framework commands with main CLI."""
        main_cli.add_command(mpc_framework_cli)


if __name__ == "__main__":
    mpc_framework_cli()
