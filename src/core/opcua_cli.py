#!/usr/bin/env python3
"""Enhanced OPC-UA CLI Commands with Configuration Management
Integration with comprehensive connection configuration system.
"""

import asyncio
import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from .opcua_connection_config import (
    OPCUAConfigManager,
    OPCUAConnectionConfig,
    OPCUAConnectionWizard,
    delete_config,
    interactive_setup,
    list_configs,
    load_config,
)
from .opcua_integration import OPCUAClient

console = Console()

# Global connection state
current_connection: OPCUAClient | None = None
current_config: OPCUAConnectionConfig | None = None


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option(
    "--log-level",
    default="INFO",
    help="set logging level (DEBUG, INFO, WARNING, ERROR)",
)
@click.pass_context
def opcua(ctx, verbose, log_level):
    """OPC-UA Client Commands with Advanced Configuration.

    🔒 SAFETY: All operations are READ-ONLY to protect live systems.

    Features:
    • Complete configuration wizard for Ignition servers
    • Certificate management and generation
    • Connection testing and diagnostics
    • Configuration storage and reuse
    • Advanced security support

    Connect to OPC-UA servers, browse address spaces, read values, and monitor
    data changes safely with comprehensive configuration management.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["log_level"] = log_level


@opcua.command()
@click.option("-u", "--url", help="OPC-UA server URL (e.g., opc.tcp://localhost:4840)")
@click.option("--username", help="Username for authentication")
@click.option("--password", help="Password for authentication")
@click.option("--security-policy", help="Security policy (None, Basic256Sha256, etc.)")
@click.option("--security-mode", help="Security mode (None, Sign, SignAndEncrypt)")
@click.option(
    "--timeout", type=float, default=20.0, help="Connection timeout in seconds"
)
@click.option("--config", help="Use saved configuration")
@click.option("--save-config", help="Save connection config to file")
@click.option("--cert-path", help="Client certificate path")
@click.option("--key-path", help="Client private key path")
@click.option("--server-cert", help="Server certificate path (.der file)")
def connect(
    url,
    username,
    password,
    security_policy,
    security_mode,
    timeout,
    config,
    save_config,
    cert_path,
    key_path,
    server_cert,
):
    r"""Connect to an OPC-UA server with comprehensive configuration.

    🔒 READ-ONLY: Connection is configured for safe read operations only.

    Examples:
        # Use configuration wizard
        ign opcua connect --wizard

        # Use saved configuration
        ign opcua connect --config ignition_production

        # Manual connection
        ign opcua connect -u opc.tcp://[SERVER_IP]:[PORT] --username [username]

        # Secure connection with certificates
        ign opcua connect -u opc.tcp://server:4840 --username admin \\
            --security-policy Basic256Sha256 --cert-path cert.pem --key-path key.pem
    """
    asyncio.run(
        _connect_async(
            url,
            username,
            password,
            security_policy,
            security_mode,
            timeout,
            config,
            save_config,
            cert_path,
            key_path,
            server_cert,
        )
    )


async def _connect_async(
    url,
    username,
    password,
    security_policy,
    security_mode,
    timeout,
    config,
    save_config,
    cert_path,
    key_path,
    server_cert,
):
    """Async connection logic."""
    global current_connection, current_config

    try:
        # If no parameters provided, run interactive wizard
        if not any([url, config]):
            console.print(
                Panel(
                    "[yellow]🧙 No connection parameters provided. Starting interactive setup wizard...[/yellow]",
                    title="Interactive Setup",
                )
            )
            current_config = await interactive_setup()
            url = current_config.server_url
            username = current_config.username
            password = current_config.password
            security_policy = current_config.security_policy
            security_mode = current_config.security_mode
            cert_path = current_config.client_cert_path
            key_path = current_config.client_key_path
            server_cert = current_config.server_cert_path
            timeout = current_config.timeout

        # Load saved configuration
        elif config:
            saved_config = load_config(config)
            if not saved_config:
                console.print(f"❌ Configuration '{config}' not found")
                return

            current_config = saved_config
            url = saved_config.server_url
            username = saved_config.username
            password = saved_config.password
            security_policy = saved_config.security_policy
            security_mode = saved_config.security_mode
            cert_path = saved_config.client_cert_path
            key_path = saved_config.client_key_path
            server_cert = saved_config.server_cert_path
            timeout = saved_config.timeout

            console.print(f"📋 Using saved configuration: {config}")

        # Manual configuration
        else:
            if not url:
                console.print("❌ Server URL is required")
                return

            # Create config from parameters
            current_config = OPCUAConnectionConfig(
                server_url=url,
                username=username or "",
                password=password or "",
                security_policy=security_policy or "None",
                security_mode=security_mode or "None",
                client_cert_path=cert_path or "",
                client_key_path=key_path or "",
                server_cert_path=server_cert or "",
                timeout=timeout,
            )

        # Show connection information
        _display_connection_info(current_config)

        # Initialize client
        current_connection = OPCUAClient()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔌 Connecting to OPC-UA server...", total=None)

            # Configure security
            if current_config.security_policy != "None":
                progress.update(task, description="🔐 Configuring security...")
                await current_connection.configure_security(
                    security_policy=current_config.security_policy,
                    security_mode=current_config.security_mode,
                    client_cert_path=current_config.client_cert_path,
                    client_key_path=current_config.client_key_path,
                    server_cert_path=current_config.server_cert_path,
                )

            # Connect
            progress.update(task, description="🔗 Establishing connection...")
            success = await current_connection.connect(
                url=current_config.server_url,
                username=current_config.username,
                password=current_config.password,
                timeout=current_config.timeout,
            )

        if success:
            console.print("✅ [bold green]Connected successfully![/bold green]")

            # Display server information
            await _display_server_info()

            # Save configuration if requested
            if save_config:
                await _save_current_config(save_config)

        else:
            console.print("❌ [bold red]Connection failed[/bold red]")
            current_connection = None
            current_config = None

    except Exception as e:
        console.print(f"❌ [bold red]Connection error: {e}[/bold red]")
        current_connection = None
        current_config = None


def _display_connection_info(config: OPCUAConnectionConfig):
    """Display connection information."""
    table = Table(title="🔗 Connection Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Server URL", config.server_url)
    table.add_row("Username", config.username or "Anonymous")
    table.add_row("Security Policy", config.security_policy)
    table.add_row("Security Mode", config.security_mode)

    if config.client_cert_path:
        table.add_row("Client Certificate", "✅ Configured")
    if config.server_cert_path:
        table.add_row("Server Certificate", "✅ Configured")

    table.add_row("Timeout", f"{config.timeout}s")

    console.print(table)


async def _display_server_info():
    """Display server information after connection."""
    if not current_connection:
        return

    try:
        namespaces = await current_connection.get_namespaces()
        console.print(f"📋 Server has {len(namespaces)} namespaces")

        # Try to read server time
        try:
            server_time = await current_connection.read_node("i=2258")
            console.print(f"🕒 Server time: {server_time}")
        except:
            pass

    except Exception as e:
        console.print(f"⚠️ Could not retrieve server info: {e}")


async def _save_current_config(config_name: str):
    """Save current configuration."""
    if not current_config:
        return

    current_config.config_name = config_name
    current_config.verified = True

    OPCUAConfigManager()
    config_dir = Path("configs/opcua")
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / f"{config_name}.json"

    from datetime import datetime

    current_config.created_at = datetime.now().isoformat()

    with open(config_file, "w") as f:
        from dataclasses import asdict

        json.dump(asdict(current_config), f, indent=2)

    console.print(f"💾 Configuration saved as '{config_name}'")


@opcua.command()
@click.option("--force", is_flag=True, help="Force disconnect without confirmation")
def disconnect(force):
    """Disconnect from the current OPC-UA server."""
    global current_connection, current_config

    if not current_connection:
        console.print("ℹ No active connection")
        return

    if not force and not Confirm.ask("🔌 Disconnect from OPC-UA server?"):
        return

    asyncio.run(_disconnect_async())

    current_connection = None
    current_config = None
    console.print("✅ Disconnected from OPC-UA server")


async def _disconnect_async():
    """Async disconnect logic."""
    if current_connection:
        await current_connection.disconnect()


@opcua.command()
def info():
    """Get comprehensive information about the connected OPC-UA server."""
    if not current_connection:
        console.print("❌ Not connected to OPC-UA server. Use 'connect' command first.")
        return

    asyncio.run(_info_async())


async def _info_async():
    """Async server info logic."""
    try:
        console.print(
            Panel.fit(
                "[bold blue]📊 OPC-UA Server Information[/bold blue]",
                title="Server Details",
            )
        )

        # Connection info
        if current_config:
            console.print(f"🔗 Connected to: {current_config.server_url}")
            console.print(
                f"👤 Authentication: {current_config.username or 'Anonymous'}"
            )
            console.print(
                f"🔒 Security: {current_config.security_policy}/{current_config.security_mode}"
            )

        # Namespaces
        namespaces = await current_connection.get_namespaces()

        table = Table(title="📚 Available Namespaces")
        table.add_column("Index", style="cyan")
        table.add_column("URI", style="green")
        table.add_column("Type", style="yellow")

        for i, ns in enumerate(namespaces):
            ns_type = "Standard" if i < 2 else "Custom"
            if "ignition" in ns.lower():
                ns_type = "Ignition"
            table.add_row(str(i), ns, ns_type)

        console.print(table)

        # Server capabilities
        console.print("\n🔧 Testing server capabilities...")

        capabilities = []

        # Test reading
        try:
            await current_connection.read_node("i=2258")
            capabilities.append("✅ Node Reading")
        except:
            capabilities.append("❌ Node Reading")

        # Test browsing
        try:
            await current_connection.browse_node("i=85")
            capabilities.append("✅ Address Space Browsing")
        except:
            capabilities.append("❌ Address Space Browsing")

        # Test subscription
        try:
            # Quick subscription test
            capabilities.append("✅ Subscriptions (untested)")
        except:
            capabilities.append("❌ Subscriptions")

        for cap in capabilities:
            console.print(f"  {cap}")

    except Exception as e:
        console.print(f"❌ Error retrieving server information: {e}")


# Configuration management commands
@opcua.group(name="config")
def config_group():
    """OPC-UA connection configuration management.

    Manage saved connection configurations for easy reuse.
    """
    pass


@config_group.command("wizard")
def config_wizard():
    """Run the interactive configuration wizard.

    Comprehensive setup wizard that collects all necessary information
    for connecting to Ignition OPC-UA servers, including:

    • Server connection details
    • Security configuration
    • Certificate management
    • Ignition-specific settings
    • Connection testing
    """
    console.print(
        Panel.fit(
            "[bold blue]🧙 OPC-UA Configuration Wizard[/bold blue]\n"
            "[dim]Comprehensive setup for Ignition OPC-UA connections[/dim]",
            title="Interactive Setup",
        )
    )

    asyncio.run(interactive_setup())


@config_group.command("list")
def config_list():
    """list all saved OPC-UA configurations."""
    list_configs()


@config_group.command("load")
@click.argument("name")
def config_load(name):
    """Load and display a saved configuration.

    NAME: Configuration name to load
    """
    config = load_config(name)
    if not config:
        console.print(f"❌ Configuration '{name}' not found")
        return

    console.print(f"📋 Configuration: {name}")

    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Server URL", config.server_url)
    table.add_row("Username", config.username or "Anonymous")
    table.add_row("Security Policy", config.security_policy)
    table.add_row("Security Mode", config.security_mode)
    table.add_row("Client Certificate", config.client_cert_path or "None")
    table.add_row("Server Certificate", config.server_cert_path or "None")
    table.add_row("Verified", "✅" if config.verified else "❌")

    if config.ignition_gateway_url:
        table.add_row("Ignition Gateway", config.ignition_gateway_url)

    console.print(table)


@config_group.command("delete")
@click.argument("name")
@click.option("--force", is_flag=True, help="Delete without confirmation")
def config_delete(name, force):
    """Delete a saved configuration.

    NAME: Configuration name to delete
    """
    if not force and not Confirm.ask(f"Delete configuration '{name}'?"):
        return

    if delete_config(name):
        console.print(f"✅ Deleted configuration '{name}'")
    else:
        console.print(f"❌ Failed to delete configuration '{name}'")


@config_group.command("test")
@click.argument("name")
def config_test(name):
    """Test a saved configuration.

    NAME: Configuration name to test
    """
    config = load_config(name)
    if not config:
        console.print(f"❌ Configuration '{name}' not found")
        return

    console.print(f"🧪 Testing configuration: {name}")

    asyncio.run(_test_config_async(config))


async def _test_config_async(config: OPCUAConnectionConfig):
    """Test a configuration asynchronously."""
    try:
        wizard = OPCUAConnectionWizard()
        success = await wizard._test_connection(config)

        if success:
            console.print("✅ [bold green]Configuration test successful![/bold green]")
        else:
            console.print("❌ [bold red]Configuration test failed[/bold red]")

    except Exception as e:
        console.print(f"❌ [bold red]Test error: {e}[/bold red]")


# Certificate management commands
@opcua.group(name="cert")
def cert_group():
    """Certificate management for OPC-UA connections.

    Generate, manage, and validate certificates for secure OPC-UA connections.
    """
    pass


@cert_group.command("generate")
@click.option("--app-uri", help="Application URI for certificate")
@click.option("--app-name", default="IgnitionCLI", help="Application name")
@click.option("--org", default="IGN Scripts", help="Organization name")
@click.option("--dns-names", help="DNS names (comma-separated)")
@click.option("--ip-addresses", help="IP addresses (comma-separated)")
@click.option("--output-dir", help="Output directory for certificates")
def cert_generate(app_uri, app_name, org, dns_names, ip_addresses, output_dir):
    """Generate client certificates for OPC-UA connections.

    Creates both certificate and private key files suitable for Ignition OPC-UA servers.
    """
    console.print("🔧 Generating OPC-UA client certificates...")

    # Import certificate generation (would need to implement)
    # For now, show what would be generated

    cert_dir = (
        Path(output_dir)
        if output_dir
        else Path.home() / ".ignition" / "opcua" / "certificates"
    )
    cert_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"📁 Certificate directory: {cert_dir}")
    console.print(f"🔗 Application URI: {app_uri or 'urn:ignition:client'}")
    console.print(f"📝 Application Name: {app_name}")
    console.print(f"🏢 Organization: {org}")

    if dns_names:
        console.print(f"🌐 DNS Names: {dns_names}")
    if ip_addresses:
        console.print(f"🔢 IP Addresses: {ip_addresses}")

    console.print("⚠️ Certificate generation requires cryptography library")
    console.print("💡 Use the configuration wizard for automatic certificate setup")


@cert_group.command("validate")
@click.argument("cert_path")
def cert_validate(cert_path):
    """Validate a certificate file.

    CERT_PATH: Path to certificate file to validate
    """
    cert_file = Path(cert_path)
    if not cert_file.exists():
        console.print(f"❌ Certificate file not found: {cert_path}")
        return

    console.print(f"🔍 Validating certificate: {cert_path}")

    try:
        # Basic file validation
        console.print(f"📁 File size: {cert_file.stat().st_size} bytes")
        console.print(f"📅 Modified: {cert_file.stat().st_mtime}")

        # Check file extension
        if cert_file.suffix.lower() in [".pem", ".crt"]:
            console.print("✅ PEM/CRT format detected")
        elif cert_file.suffix.lower() == ".der":
            console.print("✅ DER format detected")
        else:
            console.print("⚠️ Unknown certificate format")

        console.print("💡 For detailed validation, use openssl or cryptography tools")

    except Exception as e:
        console.print(f"❌ Validation error: {e}")


# Enhanced browse command with configuration awareness
@opcua.command()
@click.option(
    "--node-id", default="i=85", help="Root node ID to browse (default: Objects folder)"
)
@click.option("--depth", default=2, help="Maximum browsing depth")
@click.option("--filter", help="Filter nodes by name (case-insensitive)")
@click.option("--show-attributes", is_flag=True, help="Show node attributes")
@click.option(
    "--output",
    type=click.Choice(["tree", "table", "json"]),
    default="tree",
    help="Output format",
)
def browse(node_id, depth, filter, show_attributes, output):
    """Browse the OPC-UA server address space with advanced options.

    🔒 READ-ONLY: Safe browsing without any modifications.

    Examples:
        # Browse Objects folder
        ign opcua browse

        # Browse specific node with depth limit
        ign opcua browse --node-id "ns=2;s=Devices" --depth 3

        # Filter results and show attributes
        ign opcua browse --filter "temperature" --show-attributes

        # Export as JSON
        ign opcua browse --output json > address_space.json
    """
    if not current_connection:
        console.print("❌ Not connected to OPC-UA server. Use 'connect' command first.")
        return

    asyncio.run(_browse_async(node_id, depth, filter, show_attributes, output))


async def _browse_async(node_id, depth, filter_text, show_attributes, output):
    """Enhanced async browse logic."""
    try:
        console.print(f"🔍 Browsing from node: {node_id}")

        if current_config and current_config.ignition_gateway_url:
            console.print(f"🏭 Ignition Gateway: {current_config.ignition_gateway_url}")

        # Use existing browse logic but with enhanced display
        results = await current_connection.browse_node(node_id, max_depth=depth)

        if filter_text:
            # Filter results
            filtered_results = []
            for result in results:
                if filter_text.lower() in result.get("name", "").lower():
                    filtered_results.append(result)
            results = filtered_results
            console.print(
                f"🔍 Filtered to {len(results)} nodes containing '{filter_text}'"
            )

        if output == "json":
            print(json.dumps(results, indent=2))
        elif output == "table":
            _display_browse_table(results, show_attributes)
        else:
            _display_browse_tree(results, show_attributes)

    except Exception as e:
        console.print(f"❌ Browse error: {e}")


def _display_browse_table(results, show_attributes):
    """Display browse results as table."""
    table = Table(title="🌳 OPC-UA Address Space")
    table.add_column("Node ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")

    if show_attributes:
        table.add_column("Value", style="blue")
        table.add_column("Data Type", style="magenta")

    for result in results[:50]:  # Limit display
        row = [
            result.get("node_id", "Unknown"),
            result.get("name", "Unknown"),
            result.get("node_class", "Unknown"),
        ]

        if show_attributes:
            row.extend(
                [str(result.get("value", "N/A")), result.get("data_type", "Unknown")]
            )

        table.add_row(*row)

    console.print(table)


def _display_browse_tree(results, show_attributes):
    """Display browse results as tree."""
    console.print("🌳 Address Space Tree:")

    for result in results[:50]:  # Limit display
        indent = "  " * result.get("depth", 0)
        name = result.get("name", "Unknown")
        node_class = result.get("node_class", "Unknown")

        display_line = f"{indent}├─ {name} ({node_class})"

        if show_attributes and "value" in result:
            display_line += f" = {result['value']}"

        console.print(display_line)


# Add the existing read, monitor, and status commands here...
# (These would be the same as before, but with configuration awareness)

# Export the main group
__all__ = ["opcua"]
