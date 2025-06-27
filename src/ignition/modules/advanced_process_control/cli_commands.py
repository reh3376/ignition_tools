"""Phase 15: Advanced Process Control Suite CLI Commands.

This module provides command-line interface for the Advanced Process Control Suite
with comprehensive automated tuning, multi-loop coordination, and real-time analytics.

Following crawl_mcp.py methodology:
- Step 1: Environment validation with comprehensive checks
- Step 2: Input validation using Pydantic models
- Step 3: Comprehensive error handling with user-friendly messages
- Step 4: Modular testing with progressive complexity
- Step 5: Progressive complexity with safety guarantees
- Step 6: Resource management with async context managers

Author: IGN Scripts Development Team
Version: 15.0.0
"""

import asyncio
import logging

import click
from rich.console import Console
from rich.panel import Panel

from .automated_tuning_system import AutomatedTuningSystem

# Configure logging
logger = logging.getLogger(__name__)
console = Console()


@click.group(name="advanced-process-control")
@click.pass_context
def apc_cli(ctx: click.Context) -> None:
    """Advanced Process Control Suite - Phase 15 Commands."""
    ctx.ensure_object(dict)
    console.print(
        Panel.fit(
            "[bold blue]🏭 Advanced Process Control Suite[/bold blue]\n"
            "[dim]Phase 15: Automated Tuning & Multi-Loop Coordination[/dim]",
            border_style="blue",
        )
    )


@apc_cli.command("validate-env")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed validation results")
def validate_environment(verbose: bool) -> None:
    """Validate Advanced Process Control environment and dependencies."""

    async def _validate():
        try:
            console.print(
                "🔍 [bold]Phase 15: Advanced Process Control Environment Validation[/bold]"
            )
            console.print()

            # Initialize and validate
            tuning_system = AutomatedTuningSystem()
            result = await tuning_system.initialize()

            if result["success"]:
                console.print(
                    "✅ [green]Advanced Process Control Environment: VALID[/green]"
                )
                console.print("Overall Environment Status:")
                console.print("✅ [green]READY FOR PRODUCTION[/green]")
            else:
                console.print(
                    "❌ [red]Advanced Process Control Environment: INVALID[/red]"
                )
                console.print(f"Error: {result['error']}")

        except Exception as e:
            console.print(f"❌ [red]Environment validation failed: {e}[/red]")

    asyncio.run(_validate())


@apc_cli.command("tune-pid")
@click.option(
    "--method",
    "-m",
    type=click.Choice(["ziegler_nichols_open", "cohen_coon", "imc", "ai_enhanced"]),
    default="ai_enhanced",
    help="PID tuning method to use",
)
@click.option(
    "--setpoint", "-s", type=float, default=50.0, help="Target setpoint for tuning"
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed tuning process")
def tune_pid_controller(method: str, setpoint: float, verbose: bool) -> None:
    """Perform automated PID controller tuning."""

    async def _tune():
        try:
            console.print("🎯 [bold]Starting PID Controller Tuning[/bold]")
            console.print(f"Method: [cyan]{method}[/cyan]")
            console.print(f"Setpoint: [cyan]{setpoint}[/cyan]")
            console.print()

            # Initialize tuning system
            tuning_system = AutomatedTuningSystem()
            result = await tuning_system.initialize()

            if not result["success"]:
                console.print(f"❌ [red]Initialization failed: {result['error']}[/red]")
                return

            # Perform tuning
            with console.status("[bold green]Tuning in progress..."):
                tuning_result = await tuning_system.tune_pid_controller(
                    method=method, target_setpoint=setpoint
                )

            if tuning_result["success"]:
                console.print("✅ [green]PID Tuning Completed Successfully[/green]")

                # Display results
                params = tuning_result["parameters"]
                console.print(f"Kp: {params['kp']:.4f}")
                console.print(f"Ki: {params['ki']:.4f}")
                console.print(f"Kd: {params['kd']:.4f}")
                console.print(f"Data Points: {tuning_result['data_points']}")

            else:
                console.print(
                    f"❌ [red]PID Tuning Failed: {tuning_result['error']}[/red]"
                )

        except Exception as e:
            console.print(f"❌ [red]Tuning failed: {e}[/red]")

    asyncio.run(_tune())


@apc_cli.command("status")
def show_status() -> None:
    """Show Advanced Process Control system status."""

    async def _status():
        try:
            console.print("📊 [bold]Advanced Process Control System Status[/bold]")

            # Initialize system
            tuning_system = AutomatedTuningSystem()
            result = await tuning_system.initialize()

            if result["success"]:
                console.print("✅ [green]System Status: ACTIVE[/green]")
                console.print("✅ [green]Environment: VALID[/green]")
            else:
                console.print(
                    f"❌ [red]System Error: {result.get('error', 'Unknown error')}[/red]"
                )

        except Exception as e:
            console.print(f"❌ [red]Status check failed: {e}[/red]")

    asyncio.run(_status())


@apc_cli.command("test")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed test results")
def run_tests(verbose: bool) -> None:
    """Run Advanced Process Control system tests."""

    async def _test():
        try:
            console.print("🧪 [bold]Advanced Process Control System Tests[/bold]")

            tests_passed = 0
            tests_total = 2

            # Environment test
            console.print("🔍 Testing environment validation...")
            try:
                tuning_system = AutomatedTuningSystem()
                result = await tuning_system.initialize()

                if result["success"]:
                    console.print("  ✅ Environment validation: PASSED")
                    tests_passed += 1
                else:
                    console.print("  ❌ Environment validation: FAILED")

            except Exception as e:
                console.print(f"  ❌ Environment validation: ERROR - {e}")

            # Tuning system test
            console.print("🎯 Testing automated tuning system...")
            try:
                tuning_system = AutomatedTuningSystem()
                await tuning_system.initialize()

                result = await tuning_system.tune_pid_controller(
                    method="ai_enhanced", target_setpoint=50.0
                )

                if result["success"]:
                    console.print("  ✅ Automated tuning: PASSED")
                    tests_passed += 1
                else:
                    console.print("  ❌ Automated tuning: FAILED")

            except Exception as e:
                console.print(f"  ❌ Automated tuning: ERROR - {e}")

            console.print()

            # Test summary
            if tests_passed == tests_total:
                console.print(
                    f"✅ [green]All tests passed ({tests_passed}/{tests_total})[/green]"
                )
            else:
                console.print(
                    f"⚠️ [yellow]Tests completed: {tests_passed}/{tests_total} passed[/yellow]"
                )

        except Exception as e:
            console.print(f"❌ [red]Test execution failed: {e}[/red]")

    asyncio.run(_test())


# Export CLI group
__all__ = ["apc_cli"]
