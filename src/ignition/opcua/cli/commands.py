"""OPC-UA CLI Commands.

Command-line interface for OPC-UA client operations.
SAFETY: All commands are designed for READ-ONLY operations to protect live systems.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from ignition.opcua import IgnitionOPCUAClient

console = Console()
logger = logging.getLogger(__name__)

# Global client instance for CLI session
_current_client: IgnitionOPCUAClient | None = None
_connection_config: dict[str, Any] = {}


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--log-level",
    default="INFO",
    help="Set logging level (DEBUG, INFO, WARNING, ERROR)",
)
def opcua(verbose: bool, log_level: str):
    """OPC-UA Client Commands.

    🔒 SAFETY: All operations are READ-ONLY to protect live systems.

    Connect to OPC-UA servers, browse address spaces, read values,
    and monitor data changes safely.
    """
    # Configure logging
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level if verbose else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@opcua.command()
@click.option(
    "--url",
    "-u",
    required=True,
    help="OPC-UA server URL (e.g., opc.tcp://localhost:4840)",
)
@click.option("--username", help="Username for authentication")
@click.option("--password", help="Password for authentication")
@click.option(
    "--security-policy",
    default="None",
    help="Security policy (None, Basic256Sha256, etc.)",
)
@click.option(
    "--security-mode", default="None", help="Security mode (None, Sign, SignAndEncrypt)"
)
@click.option("--timeout", default=10.0, help="Connection timeout in seconds")
@click.option("--save-config", help="Save connection config to file")
def connect(
    url: str,
    username: str | None,
    password: str | None,
    security_policy: str,
    security_mode: str,
    timeout: float,
    save_config: str | None,
):
    """Connect to an OPC-UA server.

    🔒 READ-ONLY: Connection is configured for safe read operations only.

    Examples:
        ignition opcua connect -u opc.tcp://localhost:4840
        ignition opcua connect -u opc.tcp://server:4840 --username admin --password secret
    """
    asyncio.run(
        _connect_impl(
            url,
            username,
            password,
            security_policy,
            security_mode,
            timeout,
            save_config,
        )
    )


async def _connect_impl(
    url: str,
    username: str | None,
    password: str | None,
    security_policy: str,
    security_mode: str,
    timeout: float,
    save_config: str | None,
):
    """Implementation of connect command."""
    global _current_client, _connection_config

    try:
        console.print(f"🔌 Connecting to OPC-UA server: [bold blue]{url}[/bold blue]")

        # Create client with read-only configuration
        client = IgnitionOPCUAClient(
            url,
            timeout=timeout,
            name="IgnitionCLI-ReadOnly",
            description="Ignition CLI Client (Read-Only Mode)",
        )

        # Prepare connection arguments
        connect_args = {}
        if username:
            connect_args["username"] = username
        if password:
            connect_args["password"] = password
        if security_policy != "None":
            connect_args["security_policy"] = security_policy
            connect_args["security_mode"] = security_mode

        # Attempt connection with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Connecting...", total=None)

            try:
                await client.connect(**connect_args)
                progress.update(task, description="✅ Connected!")

                # Store client and config globally
                _current_client = client
                _connection_config = {
                    "url": url,
                    "username": username,
                    "security_policy": security_policy,
                    "security_mode": security_mode,
                    "timeout": timeout,
                    "connected_at": datetime.now().isoformat(),
                }

                # Get server information
                server_info = await client.get_server_info()

                # Display connection success
                console.print(
                    Panel.fit(
                        f"✅ [bold green]Successfully connected to OPC-UA server[/bold green]\n\n"
                        f"[bold]Server URL:[/bold] {url}\n"
                        f"[bold]Connected:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"[bold]Mode:[/bold] READ-ONLY (Safe Mode)\n"
                        f"[bold]Namespaces:[/bold] {len(server_info.get('namespace_uris', []))}\n"
                        f"[bold]Security:[/bold] {security_policy}/{security_mode}",
                        title="🔒 OPC-UA Connection Established",
                        border_style="green",
                    )
                )

                # Save configuration if requested
                if save_config:
                    config_to_save = _connection_config.copy()
                    if "password" in connect_args:
                        config_to_save["password"] = "***REDACTED***"

                    with open(save_config, "w") as f:
                        json.dump(config_to_save, f, indent=2)
                    console.print(
                        f"💾 Configuration saved to: [blue]{save_config}[/blue]"
                    )

                # Display available commands
                console.print("\n[bold]Next steps:[/bold]")
                console.print(
                    "• [cyan]ignition opcua info[/cyan] - Get server information"
                )
                console.print(
                    "• [cyan]ignition opcua browse[/cyan] - Browse address space"
                )
                console.print(
                    "• [cyan]ignition opcua read <node-id>[/cyan] - Read node value"
                )
                console.print(
                    "• [cyan]ignition opcua disconnect[/cyan] - Disconnect from server"
                )

            except Exception as e:
                progress.update(task, description="❌ Connection failed!")
                console.print(f"❌ [bold red]Connection failed:[/bold red] {e!s}")
                raise click.ClickException(f"Failed to connect: {e!s}")

    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e!s}")
        raise click.ClickException(str(e))


@opcua.command()
def disconnect():
    """Disconnect from the current OPC-UA server."""
    asyncio.run(_disconnect_impl())


async def _disconnect_impl():
    """Implementation of disconnect command."""
    global _current_client, _connection_config

    if not _current_client:
        console.print("❌ No active connection to disconnect from")
        return

    try:
        console.print("🔌 Disconnecting from OPC-UA server...")
        await _current_client.disconnect()

        console.print(
            Panel.fit(
                f"✅ [bold green]Successfully disconnected[/bold green]\n\n"
                f"[bold]Server:[/bold] {_connection_config.get('url', 'Unknown')}\n"
                f"[bold]Disconnected:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="🔌 OPC-UA Disconnection",
                border_style="blue",
            )
        )

        _current_client = None
        _connection_config = {}

    except Exception as e:
        console.print(f"❌ [bold red]Disconnect error:[/bold red] {e!s}")


@opcua.command()
def info():
    """Get information about the connected OPC-UA server."""
    asyncio.run(_info_impl())


async def _info_impl():
    """Implementation of info command."""
    if not _current_client or not _current_client.connected:
        console.print("❌ Not connected to any OPC-UA server. Use 'connect' first.")
        return

    try:
        console.print("📊 Retrieving server information...")

        server_info = await _current_client.get_server_info()
        health = await _current_client.health_check()

        # Create information table
        table = Table(
            title="🏭 OPC-UA Server Information",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Server URL", server_info.get("url", "Unknown"))
        table.add_row(
            "Connection Status",
            "✅ Connected" if server_info.get("connected") else "❌ Disconnected",
        )
        table.add_row("Server Time", str(server_info.get("server_time", "Unknown")))
        table.add_row("Health Status", health.get("status", "Unknown"))

        # Namespaces
        namespaces = server_info.get("namespace_uris", [])
        table.add_row("Namespace Count", str(len(namespaces)))

        # Endpoints
        endpoints = server_info.get("endpoints", [])
        table.add_row("Endpoint Count", str(len(endpoints)))

        # Connection stats
        stats = server_info.get("stats", {})
        if stats.get("connect_time"):
            table.add_row(
                "Connected At", stats["connect_time"].strftime("%Y-%m-%d %H:%M:%S")
            )
        if stats.get("last_activity"):
            table.add_row(
                "Last Activity", stats["last_activity"].strftime("%Y-%m-%d %H:%M:%S")
            )

        console.print(table)

        # Show namespaces
        if namespaces:
            console.print("\n[bold]📚 Available Namespaces:[/bold]")
            for i, ns in enumerate(namespaces):
                console.print(f"  [{i}] {ns}")

    except Exception as e:
        console.print(f"❌ [bold red]Error getting server info:[/bold red] {e!s}")


@opcua.command()
@click.option(
    "--node", "-n", default="i=85", help="Starting node ID (default: Objects folder)"
)
@click.option("--depth", "-d", default=2, help="Maximum browsing depth")
@click.option("--filter", "-f", help="Filter nodes by browse name (case-insensitive)")
@click.option("--variables-only", is_flag=True, help="Show only variable nodes")
def browse(node: str, depth: int, filter: str | None, variables_only: bool):
    """Browse the OPC-UA server address space.

    🔒 READ-ONLY: Safely browse server structure without modifications.

    Examples:
        ignition opcua browse
        ignition opcua browse --node "ns=2;i=1001" --depth 3
        ignition opcua browse --filter "temperature" --variables-only
    """
    asyncio.run(_browse_impl(node, depth, filter, variables_only))


async def _browse_impl(node: str, depth: int, filter: str | None, variables_only: bool):
    """Implementation of browse command."""
    if not _current_client or not _current_client.connected:
        console.print("❌ Not connected to any OPC-UA server. Use 'connect' first.")
        return

    try:
        console.print(f"🔍 Browsing address space from node: [bold]{node}[/bold]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Browsing...", total=None)

            # Browse the tree
            tree_data = await _current_client.browse_tree(node, depth)

            progress.update(task, description="✅ Browsing complete!")

        # Create and display tree
        tree = Tree(f"📁 [bold blue]{tree_data.get('browse_name', 'Root')}[/bold blue]")
        _build_tree_display(tree, tree_data, filter, variables_only)

        console.print(tree)

        # Show summary
        node_count = _count_nodes(tree_data)
        console.print(f"\n📊 Found [bold green]{node_count}[/bold green] nodes")

    except Exception as e:
        console.print(f"❌ [bold red]Browse error:[/bold red] {e!s}")


def _build_tree_display(
    tree: Tree, node_data: dict[str, Any], filter: str | None, variables_only: bool
):
    """Build rich tree display from node data."""
    children = node_data.get("children", [])

    for child in children:
        browse_name = child.get("browse_name", "Unknown")
        node_class = child.get("node_class", "Unknown")

        # Apply filters
        if filter and filter.lower() not in browse_name.lower():
            continue

        if variables_only and "Variable" not in node_class:
            continue

        # Choose icon based on node class
        icon = (
            "📊"
            if "Variable" in node_class
            else "📁"
            if "Object" in node_class
            else "🔧"
        )

        # Add value if it's a variable
        display_text = f"{icon} {browse_name}"
        if "Variable" in node_class and "value" in child:
            value = child["value"]
            display_text += f" = [green]{value}[/green]"

        # Add data type if available
        if child.get("data_type"):
            display_text += f" [dim]({child['data_type']})[/dim]"

        branch = tree.add(display_text)

        # Recursively add children
        if child.get("children"):
            _build_tree_display(branch, child, filter, variables_only)


def _count_nodes(node_data: dict[str, Any]) -> int:
    """Count total nodes in tree data."""
    count = 1
    for child in node_data.get("children", []):
        count += _count_nodes(child)
    return count


@opcua.command()
@click.argument("node_id", required=True)
@click.option(
    "--format",
    "-f",
    default="auto",
    type=click.Choice(["auto", "json", "table", "raw"]),
    help="Output format",
)
def read(node_id: str, format: str):
    """Read value from an OPC-UA node.

    🔒 READ-ONLY: Safely read node values without modifications.

    Examples:
        ignition opcua read "ns=2;i=1001"
        ignition opcua read "i=2258" --format json
    """
    asyncio.run(_read_impl(node_id, format))


async def _read_impl(node_id: str, format: str):
    """Implementation of read command."""
    if not _current_client or not _current_client.connected:
        console.print("❌ Not connected to any OPC-UA server. Use 'connect' first.")
        return

    try:
        console.print(f"📖 Reading value from node: [bold]{node_id}[/bold]")

        # Read the value
        value = await _current_client.read_values(node_id)

        # Get additional node information
        node_info = await _current_client.browser.get_node_info(
            _current_client.client.get_node(node_id)
        )

        # Display based on format
        if format == "json":
            result = {
                "node_id": node_id,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "node_info": node_info,
            }
            console.print(Syntax(json.dumps(result, indent=2, default=str), "json"))

        elif format == "table":
            table = Table(title=f"📖 Node Reading: {node_id}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Node ID", node_id)
            table.add_row("Value", str(value))
            table.add_row("Browse Name", node_info.get("browse_name", "Unknown"))
            table.add_row("Data Type", node_info.get("data_type", "Unknown"))
            table.add_row("Node Class", node_info.get("node_class", "Unknown"))
            table.add_row("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            console.print(table)

        elif format == "raw":
            console.print(str(value))

        else:  # auto format
            console.print(
                Panel.fit(
                    f"[bold]Node ID:[/bold] {node_id}\n"
                    f"[bold]Browse Name:[/bold] {node_info.get('browse_name', 'Unknown')}\n"
                    f"[bold]Value:[/bold] [green]{value}[/green]\n"
                    f"[bold]Data Type:[/bold] {node_info.get('data_type', 'Unknown')}\n"
                    f"[bold]Read Time:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    title="📖 OPC-UA Node Reading",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(f"❌ [bold red]Read error:[/bold red] {e!s}")


@opcua.command()
def status():
    """Show current connection status and statistics."""
    global _current_client, _connection_config

    if not _current_client:
        console.print("❌ No active OPC-UA connection")
        return

    asyncio.run(_status_impl())


async def _status_impl():
    """Implementation of status command."""
    try:
        health = await _current_client.health_check()

        # Connection status
        status_color = "green" if health.get("status") == "healthy" else "red"
        status_icon = "✅" if health.get("status") == "healthy" else "❌"

        console.print(
            Panel.fit(
                f"{status_icon} [bold {status_color}]Connection Status: {health.get('status', 'Unknown').upper()}[/bold {status_color}]\n\n"
                f"[bold]Server URL:[/bold] {_connection_config.get('url', 'Unknown')}\n"
                f"[bold]Connected At:[/bold] {_connection_config.get('connected_at', 'Unknown')}\n"
                f"[bold]Mode:[/bold] READ-ONLY (Safe Mode)\n"
                f"[bold]Client Name:[/bold] IgnitionCLI-ReadOnly",
                title="🔗 OPC-UA Connection Status",
                border_style=status_color,
            )
        )

        # Subscription status
        sub_status = health.get("subscriptions", {})
        if sub_status.get("active_subscriptions", 0) > 0:
            console.print(
                f"\n📊 Active Subscriptions: {sub_status['active_subscriptions']}"
            )

    except Exception as e:
        console.print(f"❌ [bold red]Status error:[/bold red] {e!s}")


@opcua.command()
@click.argument("node_ids", nargs=-1, required=True)
@click.option(
    "--interval", "-i", default=1000, help="Subscription interval in milliseconds"
)
@click.option(
    "--duration",
    "-t",
    default=30,
    help="Monitoring duration in seconds (0 for indefinite)",
)
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json", "csv"]),
    help="Output format for monitored data",
)
@click.option("--output", "-o", help="Output file path (default: console)")
def monitor(
    node_ids: tuple, interval: int, duration: int, format: str, output: str | None
):
    """Monitor OPC-UA nodes for real-time data changes.

    🔒 READ-ONLY: Safely monitor data changes without modifications.

    Examples:
        ignition opcua monitor "ns=2;i=1001" "ns=2;i=1002"
        ignition opcua monitor "i=2258" --interval 500 --duration 60
        ignition opcua monitor "ns=2;i=*" --format json --output monitoring.json
    """
    asyncio.run(_monitor_impl(list(node_ids), interval, duration, format, output))


async def _monitor_impl(
    node_ids: list, interval: int, duration: int, format: str, output: str | None
):
    """Implementation of monitor command."""
    if not _current_client or not _current_client.connected:
        console.print("❌ Not connected to any OPC-UA server. Use 'connect' first.")
        return

    try:
        console.print(f"📊 Starting real-time monitoring of {len(node_ids)} node(s)")
        console.print(
            f"⏱️  Interval: {interval}ms, Duration: {duration}s {'(indefinite)' if duration == 0 else ''}"
        )

        # Prepare data collection
        monitoring_data = []
        output_file = None
        if output:
            output_file = open(output, "w")
            if format == "csv":
                import csv

                fieldnames = [
                    "timestamp",
                    "node_id",
                    "value",
                    "quality",
                    "source_timestamp",
                ]
                writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                writer.writeheader()

        # Create subscription callback
        def data_change_callback(node_id, value, data):
            timestamp = datetime.now()
            quality = getattr(data, "status_code", "Unknown")
            source_timestamp = getattr(data, "source_timestamp", timestamp)

            record = {
                "timestamp": timestamp,
                "node_id": str(node_id),
                "value": value,
                "quality": str(quality),
                "source_timestamp": source_timestamp,
            }

            monitoring_data.append(record)

            # Display real-time update
            if not output or output == "console":
                if format == "table":
                    console.print(
                        f"[{timestamp.strftime('%H:%M:%S')}] {node_id}: [green]{value}[/green]"
                    )
                elif format == "json":
                    console.print(
                        json.dumps(
                            {
                                "timestamp": timestamp.isoformat(),
                                "node_id": str(node_id),
                                "value": str(value),
                                "quality": str(quality),
                            }
                        )
                    )

            # Write to file if specified
            if output_file:
                if format == "csv":
                    writer.writerow(
                        {
                            "timestamp": timestamp.isoformat(),
                            "node_id": str(node_id),
                            "value": str(value),
                            "quality": str(quality),
                            "source_timestamp": source_timestamp.isoformat()
                            if hasattr(source_timestamp, "isoformat")
                            else str(source_timestamp),
                        }
                    )
                elif format == "json":
                    json.dump(record, output_file, default=str)
                    output_file.write("\n")

                output_file.flush()

        # Create subscription
        console.print("🔗 Creating subscription...")
        subscription = await _current_client.subscribe_to_data_changes(
            node_ids, callback=data_change_callback, interval=interval
        )

        console.print("✅ Subscription created! Monitoring data changes...")
        console.print("Press Ctrl+C to stop monitoring")

        # Monitor for specified duration or indefinitely
        try:
            if duration > 0:
                await asyncio.sleep(duration)
            else:
                # Monitor indefinitely until Ctrl+C
                while True:
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n⏹️  Monitoring stopped by user")

        # Clean up subscription
        console.print("🧹 Cleaning up subscription...")
        await _current_client.unsubscribe(subscription["subscription_id"])

        if output_file:
            output_file.close()
            console.print(f"💾 Data saved to: [blue]{output}[/blue]")

        # Display summary
        console.print(
            Panel.fit(
                f"📊 [bold green]Monitoring Complete[/bold green]\n\n"
                f"[bold]Duration:[/bold] {duration}s\n"
                f"[bold]Nodes Monitored:[/bold] {len(node_ids)}\n"
                f"[bold]Data Points Collected:[/bold] {len(monitoring_data)}\n"
                f"[bold]Average Rate:[/bold] {len(monitoring_data) / max(duration, 1):.2f} points/sec",
                title="📈 Monitoring Summary",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"❌ [bold red]Monitoring error:[/bold red] {e!s}")
        if output_file:
            output_file.close()


if __name__ == "__main__":
    opcua()
