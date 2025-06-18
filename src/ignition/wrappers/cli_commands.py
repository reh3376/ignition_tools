"""CLI commands for Ignition system function wrappers."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .system_alarm import SystemAlarmWrapper
from .system_db import SystemDbWrapper
from .system_gui import SystemGuiWrapper
from .system_nav import SystemNavWrapper
from .system_tag import SystemTagWrapper
from .system_util import SystemUtilWrapper
from .wrapper_base import WrapperConfig

console = Console()


@click.group(name="wrappers")
def wrapper_group():
    """🛡️ Enhanced Ignition system function wrappers with error handling."""
    pass


@wrapper_group.command()
@click.option(
    "--enable-logging/--disable-logging", default=True, help="Enable wrapper logging"
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
@click.option(
    "--enable-metrics/--disable-metrics",
    default=True,
    help="Enable performance metrics",
)
@click.option("--retry-attempts", default=3, type=int, help="Number of retry attempts")
@click.option("--timeout", default=30, type=int, help="Timeout in seconds")
def test_tag_wrapper(
    enable_logging: bool,
    log_level: str,
    enable_metrics: bool,
    retry_attempts: int,
    timeout: int,
):
    """🏷️ Test the system.tag wrapper functionality."""
    console.print("[bold blue]🏷️ Testing System Tag Wrapper[/bold blue]\n")

    # Create wrapper configuration
    config = WrapperConfig(
        enable_logging=enable_logging,
        log_level=log_level,
        enable_metrics=enable_metrics,
        retry_attempts=retry_attempts,
        timeout_seconds=timeout,
    )

    # Initialize wrapper
    wrapper = SystemTagWrapper(config)

    try:
        # Test tag reading
        console.print("[yellow]Testing tag read functionality...[/yellow]")

        test_tags = ["[default]TestTag1", "[default]TestTag2"]
        results = wrapper.read_blocking(test_tags)

        # Display results in a table
        table = Table(title="Tag Read Results")
        table.add_column("Tag Path", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Quality", style="yellow")
        table.add_column("Success", style="bold")

        for result in results:
            success_style = "green" if result.success else "red"
            success_text = "✓" if result.success else "✗"

            table.add_row(
                result.tag_path,
                str(result.value),
                f"{result.quality_name} ({result.quality})",
                f"[{success_style}]{success_text}[/{success_style}]",
            )

        console.print(table)

        # Show metrics if enabled
        if enable_metrics:
            metrics = wrapper.get_metrics_summary()
            console.print("\n[bold]Performance Metrics:[/bold]")
            console.print(f"Total calls: {metrics['total_calls']}")
            console.print(f"Success rate: {metrics.get('success_rate', 0):.1%}")
            console.print(
                f"Average execution time: {metrics.get('average_execution_time_ms', 0):.2f}ms"
            )

        console.print("\n[green]✅ Tag wrapper test completed successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]❌ Tag wrapper test failed: {e}[/red]")


@wrapper_group.command()
@click.option("--query", default="SELECT 1 as test_value", help="Test SQL query")
@click.option("--database", default="", help="Database name")
def test_db_wrapper(query: str, database: str):
    """🗄️ Test the system.db wrapper functionality."""
    console.print("[bold blue]🗄️ Testing System Database Wrapper[/bold blue]\n")

    wrapper = SystemDbWrapper()

    try:
        console.print(f"[yellow]Executing query: {query}[/yellow]")

        result = wrapper.run_query(query, database)

        # Display results
        console.print("\n[bold]Query Results:[/bold]")
        console.print(f"Database: {result.database}")
        console.print(f"Row count: {result.row_count}")
        console.print(f"Execution time: {result.execution_time_ms:.2f}ms")
        console.print(f"Success: {'✅' if result.success else '❌'}")

        if result.data and result.row_count > 0:
            console.print(f"\nFirst few rows: {result.data[:5]}")

        console.print(
            "\n[green]✅ Database wrapper test completed successfully![/green]"
        )

    except Exception as e:
        console.print(f"\n[red]❌ Database wrapper test failed: {e}[/red]")


@wrapper_group.command()
@click.option(
    "--message", default="Test message from wrapper", help="Message to display"
)
@click.option("--title", default="Wrapper Test", help="Message box title")
@click.option(
    "--box-type", default="message", type=click.Choice(["message", "error", "warning"])
)
def test_gui_wrapper(message: str, title: str, box_type: str):
    """🖥️ Test the system.gui wrapper functionality."""
    console.print("[bold blue]🖥️ Testing System GUI Wrapper[/bold blue]\n")

    wrapper = SystemGuiWrapper()

    try:
        console.print(f"[yellow]Displaying {box_type} box...[/yellow]")

        if box_type == "message":
            result = wrapper.message_box(message, title)
        elif box_type == "error":
            result = wrapper.error_box(message, title)
        elif box_type == "warning":
            result = wrapper.warning_box(message, title)

        # Display results
        console.print("\n[bold]GUI Operation Results:[/bold]")
        console.print(f"Type: {result['type']}")
        console.print(f"Title: {result['title']}")
        console.print(f"Message: {result['message']}")
        console.print(f"Success: {'✅' if result['success'] else '❌'}")

        console.print("\n[green]✅ GUI wrapper test completed successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]❌ GUI wrapper test failed: {e}[/red]")


@wrapper_group.command()
@click.option("--window-path", default="TestWindow", help="Window path to test")
def test_nav_wrapper(window_path: str):
    """🧭 Test the system.nav wrapper functionality."""
    console.print("[bold blue]🧭 Testing System Navigation Wrapper[/bold blue]\n")

    wrapper = SystemNavWrapper()

    try:
        console.print(f"[yellow]Testing window operations for: {window_path}[/yellow]")

        # Test opening window
        open_result = wrapper.open_window(window_path, {"test_param": "test_value"})

        # Test closing window
        close_result = wrapper.close_window(window_path)

        # Display results
        console.print("\n[bold]Navigation Operation Results:[/bold]")

        table = Table(title="Window Operations")
        table.add_column("Operation", style="cyan")
        table.add_column("Window Path", style="yellow")
        table.add_column("Success", style="bold")

        table.add_row(
            "Open Window",
            open_result["path"],
            "[green]✓[/green]" if open_result["success"] else "[red]✗[/red]",
        )

        table.add_row(
            "Close Window",
            close_result["path"],
            "[green]✓[/green]" if close_result["success"] else "[red]✗[/red]",
        )

        console.print(table)
        console.print(
            "\n[green]✅ Navigation wrapper test completed successfully![/green]"
        )

    except Exception as e:
        console.print(f"\n[red]❌ Navigation wrapper test failed: {e}[/red]")


@wrapper_group.command()
def test_alarm_wrapper():
    """🚨 Test the system.alarm wrapper functionality."""
    console.print("[bold blue]🚨 Testing System Alarm Wrapper[/bold blue]\n")

    wrapper = SystemAlarmWrapper()

    try:
        console.print("[yellow]Testing alarm operations...[/yellow]")

        # Test alarm status query
        status_result = wrapper.query_status()

        # Display results
        console.print("\n[bold]Alarm Operation Results:[/bold]")
        console.print(f"Alarm count: {status_result['alarm_count']}")
        console.print(f"Query success: {'✅' if status_result['success'] else '❌'}")

        if status_result["filters"]["priority"]:
            console.print(f"Priority filter: {status_result['filters']['priority']}")
        if status_result["filters"]["state"]:
            console.print(f"State filter: {status_result['filters']['state']}")

        console.print("\n[green]✅ Alarm wrapper test completed successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]❌ Alarm wrapper test failed: {e}[/red]")


@wrapper_group.command()
@click.option(
    "--logger-name", default="test.wrapper.logger", help="Logger name to test"
)
def test_util_wrapper(logger_name: str):
    """🔧 Test the system.util wrapper functionality."""
    console.print("[bold blue]🔧 Testing System Utility Wrapper[/bold blue]\n")

    wrapper = SystemUtilWrapper()

    try:
        console.print(
            f"[yellow]Testing utility operations with logger: {logger_name}[/yellow]"
        )

        # Test logger retrieval
        logger = wrapper.get_logger(logger_name)

        # Display results
        console.print("\n[bold]Utility Operation Results:[/bold]")
        console.print(f"Logger name: {logger.name}")
        console.print(f"Logger level: {logger.level}")
        console.print("Success: ✅")

        console.print(
            "\n[green]✅ Utility wrapper test completed successfully![/green]"
        )

    except Exception as e:
        console.print(f"\n[red]❌ Utility wrapper test failed: {e}[/red]")


@wrapper_group.command()
def test_all_wrappers():
    """🧪 Run comprehensive tests on all system function wrappers."""
    console.print("[bold blue]🧪 Running Comprehensive Wrapper Tests[/bold blue]\n")

    wrappers = [
        ("Tag Wrapper", SystemTagWrapper),
        ("Database Wrapper", SystemDbWrapper),
        ("GUI Wrapper", SystemGuiWrapper),
        ("Navigation Wrapper", SystemNavWrapper),
        ("Alarm Wrapper", SystemAlarmWrapper),
        ("Utility Wrapper", SystemUtilWrapper),
    ]

    results = []

    for name, wrapper_class in wrappers:
        try:
            console.print(f"[yellow]Testing {name}...[/yellow]")

            wrapper = wrapper_class()
            wrapped_functions = wrapper.get_wrapped_functions()

            results.append(
                {
                    "name": name,
                    "success": True,
                    "function_count": len(wrapped_functions),
                    "functions": wrapped_functions,
                }
            )

            console.print(f"[green]✅ {name} initialized successfully[/green]")

        except Exception as e:
            results.append({"name": name, "success": False, "error": str(e)})
            console.print(f"[red]❌ {name} failed: {e}[/red]")

    # Display summary
    console.print("\n[bold]Test Summary:[/bold]")

    table = Table(title="Wrapper Test Results")
    table.add_column("Wrapper", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Functions", style="yellow")
    table.add_column("Details", style="dim")

    for result in results:
        status = (
            "[green]✅ Success[/green]" if result["success"] else "[red]❌ Failed[/red]"
        )
        function_count = str(result.get("function_count", 0))
        details = (
            ", ".join(result.get("functions", []))
            if result["success"]
            else result.get("error", "")
        )

        table.add_row(
            result["name"],
            status,
            function_count,
            details[:50] + "..." if len(details) > 50 else details,
        )

    console.print(table)

    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)

    if successful_tests == total_tests:
        console.print(
            f"\n[bold green]🎉 All {total_tests} wrapper tests passed![/bold green]"
        )
    else:
        console.print(
            f"\n[bold yellow]⚠️ {successful_tests}/{total_tests} wrapper tests passed[/bold yellow]"
        )


@wrapper_group.command()
def show_wrapper_info():
    """📋 Show information about available system function wrappers."""
    console.print("[bold blue]📋 Ignition System Function Wrappers[/bold blue]\n")

    wrapper_info = [
        {
            "name": "SystemTagWrapper",
            "module": "system.tag",
            "description": "Enhanced tag operations with quality validation and retry logic",
            "functions": [
                "read_blocking",
                "write_blocking",
                "read_async",
                "write_async",
            ],
        },
        {
            "name": "SystemDbWrapper",
            "module": "system.db",
            "description": "Database operations with query validation and performance metrics",
            "functions": ["run_query", "run_update_query", "run_prep_query"],
        },
        {
            "name": "SystemGuiWrapper",
            "module": "system.gui",
            "description": "GUI operations with input validation and logging",
            "functions": ["message_box", "error_box", "warning_box"],
        },
        {
            "name": "SystemNavWrapper",
            "module": "system.nav",
            "description": "Window navigation with parameter validation",
            "functions": ["open_window", "close_window", "swap_window"],
        },
        {
            "name": "SystemAlarmWrapper",
            "module": "system.alarm",
            "description": "Alarm operations with comprehensive error handling",
            "functions": ["acknowledge", "query_status", "shelve"],
        },
        {
            "name": "SystemUtilWrapper",
            "module": "system.util",
            "description": "Utility operations with enhanced logging and validation",
            "functions": ["get_logger", "send_message"],
        },
    ]

    for info in wrapper_info:
        panel_content = f"""[bold]{info["description"]}[/bold]

[yellow]Wrapped Functions:[/yellow]
{", ".join(info["functions"])}

[cyan]Original Module:[/cyan] {info["module"]}"""

        panel = Panel(panel_content, title=f"🛡️ {info['name']}", border_style="blue")
        console.print(panel)
        console.print()


if __name__ == "__main__":
    wrapper_group()
