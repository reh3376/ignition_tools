#!/usr/bin/env python3
"""OPC-UA Connection Configuration Management.

Provides classes and utilities for managing OPC-UA server connections,
including configuration storage, validation, and connection management.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


@dataclass
class OPCUAConnectionConfig:
    """Complete OPC-UA connection configuration."""

    # Basic Connection
    server_url: str
    username: str = ""
    password: str = ""

    # Security Configuration
    security_policy: str = "Basic256Sha256"
    security_mode: str = "SignAndEncrypt"

    # Certificate Paths
    client_cert_path: str = ""
    client_key_path: str = ""
    server_cert_path: str = ""

    # Certificate Generation Parameters
    application_uri: str = ""
    application_name: str = "IgnitionCLI"
    organization: str = "IGN Scripts"
    dns_names: list[str] = None
    ip_addresses: list[str] = None

    # Connection Settings
    timeout: float = 20.0
    session_timeout: int = 3600000
    subscription_period: int = 1000

    # Ignition-Specific Settings
    ignition_gateway_url: str = ""
    ignition_project: str = ""

    # Configuration Metadata
    config_name: str = "default"
    description: str = ""
    created_at: str = ""
    verified: bool = False

    def __post_init__(self) -> None:
        if self.dns_names is None:
            self.dns_names = []
        if self.ip_addresses is None:
            self.ip_addresses = []


class OPCUAConnectionWizard:
    """Interactive wizard for OPC-UA connection configuration."""

    def __init__(self) -> None:
        self.console = Console()

    async def run_interactive_setup(self) -> OPCUAConnectionConfig:
        """Run interactive setup wizard."""
        self.console.print(
            Panel.fit(
                "[bold blue]🔧 OPC-UA Connection Configuration Wizard[/bold blue]\n"
                "[dim]Collect all necessary information for Ignition OPC-UA connection[/dim]",
                title="Setup Wizard",
            )
        )

        config = OPCUAConnectionConfig(server_url="")

        # Step 1: Basic Connection Information
        config = await self._collect_basic_info(config)

        # Step 2: Security Configuration
        config = await self._collect_security_info(config)

        # Step 3: Certificate Configuration
        config = await self._collect_certificate_info(config)

        # Step 4: Advanced Settings
        config = await self._collect_advanced_settings(config)

        # Step 5: Ignition-Specific Settings
        config = await self._collect_ignition_settings(config)

        # Step 6: Test Connection
        if Confirm.ask("🧪 Test connection now?"):
            await self._test_connection(config)

        # Step 7: Save Configuration
        if Confirm.ask("💾 Save this configuration?"):
            await self._save_configuration(config)

        return config

    async def _collect_basic_info(self, config: OPCUAConnectionConfig) -> OPCUAConnectionConfig:
        """Collect basic connection information."""
        self.console.print("\n[bold yellow]📡 Basic Connection Information[/bold yellow]")

        # Server URL
        config.server_url = Prompt.ask("🔗 OPC-UA Server URL", default="opc.tcp://localhost:4840")

        # Configuration name
        config.config_name = Prompt.ask(
            "📝 Configuration name",
            default=f"ignition_{config.server_url.split(':')[-1]}",
        )

        # Description
        config.description = Prompt.ask(
            "📄 Description (optional)",
            default=f"Ignition OPC-UA connection to {config.server_url}",
        )

        # Authentication
        if Confirm.ask("👤 Does the server require authentication?", default=True):
            config.username = Prompt.ask("👤 Username", default="admin")
            config.password = Prompt.ask("🔒 Password", password=True)

        return config

    async def _collect_security_info(self, config: OPCUAConnectionConfig) -> OPCUAConnectionConfig:
        """Collect security configuration."""
        self.console.print("\n[bold yellow]🔐 Security Configuration[/bold yellow]")

        # Security Policy
        policies = [
            "None",
            "Basic256Sha256",
            "Basic256",
            "Aes128_Sha256_RsaOaep",
            "Aes256_Sha256_RsaPss",
        ]

        self.console.print("Available security policies:")
        for i, policy in enumerate(policies, 1):
            recommended = " [bold green](Recommended for Ignition)[/bold green]" if policy == "Basic256Sha256" else ""
            self.console.print(f"  {i}. {policy}{recommended}")

        policy_choice = Prompt.ask(
            "🔒 Select security policy",
            choices=[str(i) for i in range(1, len(policies) + 1)],
            default="2",
        )
        config.security_policy = policies[int(policy_choice) - 1]

        # Security Mode
        if config.security_policy != "None":
            modes = ["None", "Sign", "SignAndEncrypt"]

            self.console.print("Available security modes:")
            for i, mode in enumerate(modes, 1):
                recommended = " [bold green](Recommended)[/bold green]" if mode == "SignAndEncrypt" else ""
                self.console.print(f"  {i}. {mode}{recommended}")

            mode_choice = Prompt.ask(
                "🔐 Select security mode",
                choices=[str(i) for i in range(1, len(modes) + 1)],
                default="3",
            )
            config.security_mode = modes[int(mode_choice) - 1]

        return config

    async def _collect_certificate_info(self, config: OPCUAConnectionConfig) -> OPCUAConnectionConfig:
        """Collect certificate configuration."""
        if config.security_policy == "None":
            return config

        self.console.print("\n[bold yellow]📜 Certificate Configuration[/bold yellow]")

        # Default certificate directory
        cert_dir = Path.home() / ".ignition" / "opcua" / "certificates"

        # Check for existing certificates
        default_client_cert = cert_dir / "IgnitionOPCUA-Client_cert.pem"
        default_client_key = cert_dir / "IgnitionOPCUA-Client_key.pem"

        if default_client_cert.exists() and default_client_key.exists():
            if Confirm.ask(f"📜 Use existing client certificates in {cert_dir}?", default=True):
                config.client_cert_path = str(default_client_cert)
                config.client_key_path = str(default_client_key)
            else:
                config.client_cert_path = Prompt.ask("📜 Client certificate path")
                config.client_key_path = Prompt.ask("🔑 Client private key path")
        else:
            if Confirm.ask("🔧 Generate new client certificates?", default=True):
                config = await self._collect_cert_generation_info(config)
            else:
                config.client_cert_path = Prompt.ask("📜 Client certificate path")
                config.client_key_path = Prompt.ask("🔑 Client private key path")

        # Server certificate
        self.console.print(
            "\n[dim]Server certificate is required for secure connections to verify server identity[/dim]"
        )

        # Check common server certificate locations
        common_locations = [
            Path.cwd() / ".secret_env",
            Path.cwd() / "certificates",
            Path.home() / "Downloads",
        ]

        found_server_certs = []
        for location in common_locations:
            if location.exists():
                der_files = list(location.glob("*.der"))
                found_server_certs.extend(der_files)

        if found_server_certs:
            self.console.print("🔍 Found server certificate files:")
            for i, cert_file in enumerate(found_server_certs, 1):
                self.console.print(f"  {i}. {cert_file}")

            if Confirm.ask("Use one of the found certificates?"):
                cert_choice = Prompt.ask(
                    "Select certificate",
                    choices=[str(i) for i in range(1, len(found_server_certs) + 1)],
                )
                config.server_cert_path = str(found_server_certs[int(cert_choice) - 1])
            else:
                config.server_cert_path = Prompt.ask("🏢 Server certificate path (.der file)")
        else:
            config.server_cert_path = Prompt.ask(
                "🏢 Server certificate path (.der file)",
                default=str(Path.cwd() / ".secret_env" / "server_cert.der"),
            )

        return config

    async def _collect_cert_generation_info(self, config: OPCUAConnectionConfig) -> OPCUAConnectionConfig:
        """Collect certificate generation parameters."""
        self.console.print("\n[bold yellow]🔧 Certificate Generation Parameters[/bold yellow]")

        # Application URI
        default_uri = f"urn:ignition:client:{config.config_name}"
        config.application_uri = Prompt.ask("🔗 Application URI", default=default_uri)

        # Application Name
        config.application_name = Prompt.ask("📝 Application Name", default="IgnitionCLI")

        # Organization
        config.organization = Prompt.ask("🏢 Organization", default="IGN Scripts")

        # DNS Names
        if Confirm.ask("📡 Add DNS names to certificate? (Recommended for hostname validation)"):
            dns_input = Prompt.ask("🌐 DNS names (comma-separated)", default="localhost")
            config.dns_names = [name.strip() for name in dns_input.split(",") if name.strip()]

        # IP Addresses
        if Confirm.ask("🌐 Add IP addresses to certificate?"):
            ip_input = Prompt.ask("🔢 IP addresses (comma-separated)", default="127.0.0.1")
            config.ip_addresses = [ip.strip() for ip in ip_input.split(",") if ip.strip()]

        return config

    async def _collect_advanced_settings(self, config: OPCUAConnectionConfig) -> OPCUAConnectionConfig:
        """Collect advanced connection settings."""
        if not Confirm.ask("\n⚙️ Configure advanced settings?"):
            return config

        self.console.print("\n[bold yellow]⚙️ Advanced Connection Settings[/bold yellow]")

        # Timeout settings
        config.timeout = float(Prompt.ask("⏱️ Connection timeout (seconds)", default=str(config.timeout)))

        config.session_timeout = int(
            Prompt.ask("🔗 Session timeout (milliseconds)", default=str(config.session_timeout))
        )

        config.subscription_period = int(
            Prompt.ask(
                "📊 Subscription period (milliseconds)",
                default=str(config.subscription_period),
            )
        )

        return config

    async def _collect_ignition_settings(self, config: OPCUAConnectionConfig) -> OPCUAConnectionConfig:
        """Collect Ignition-specific settings."""
        if not Confirm.ask("\n🏭 Configure Ignition-specific settings?"):
            return config

        self.console.print("\n[bold yellow]🏭 Ignition-Specific Settings[/bold yellow]")

        # Extract hostname from OPC-UA URL for Gateway URL
        try:
            from urllib.parse import urlparse

            parsed = urlparse(config.server_url.replace("opc.tcp://", "http://"))
            default_gateway = f"http://{parsed.hostname}:8088"
        except Exception:
            default_gateway = "http://localhost:8088"

        config.ignition_gateway_url = Prompt.ask("🌐 Ignition Gateway URL (for web interface)", default=default_gateway)

        config.ignition_project = Prompt.ask("📂 Ignition Project name (optional)", default="")

        return config

    async def _test_connection(self, config: OPCUAConnectionConfig) -> bool:
        """Test the OPC-UA connection."""
        self.console.print("\n[bold yellow]🧪 Testing Connection[/bold yellow]")

        try:
            # Import here to avoid circular dependencies
            from asyncua import Client

            with self.console.status("[bold green]Connecting..."):
                client = Client(config.server_url)

                # Configure security if needed
                if config.security_policy != "None":
                    from asyncua.crypto.security_policies import (
                        SecurityPolicyBasic256Sha256,
                    )

                    if config.server_cert_path:
                        # Use security string with server cert
                        security_string = f"{config.security_policy},{config.security_mode},{config.client_cert_path},{config.client_key_path},{config.server_cert_path}"  # noqa: E501
                        await client.set_security_string(security_string)
                    else:
                        # Use basic security without server cert
                        await client.set_security(
                            SecurityPolicyBasic256Sha256,
                            config.client_cert_path,
                            config.client_key_path,
                            mode=3 if config.security_mode == "SignAndEncrypt" else 2,
                        )

                # set authentication
                if config.username:
                    client.set_user(config.username)
                    client.set_password(config.password)

                # Test connection
                await client.connect()
                self.console.print("✅ [bold green]Connection successful![/bold green]")

                # Test basic operations
                namespaces = await client.get_namespace_array()
                self.console.print(f"📋 Found {len(namespaces)} namespaces")

                # Try to read server time
                try:
                    time_node = client.get_node("i=2258")
                    server_time = await time_node.read_value()
                    self.console.print(f"🕒 Server time: {server_time}")
                except Exception as e:
                    self.console.print(f"⚠️ Could not read server time: {e}")

                await client.disconnect()
                config.verified = True
                return True

        except Exception as e:
            self.console.print(f"❌ [bold red]Connection test failed: {e}[/bold red]")
            return False

    async def _save_configuration(self, config: OPCUAConnectionConfig) -> None:
        """Save configuration to file."""
        config_dir = Path("configs/opcua")
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / f"{config.config_name}.json"

        # Add timestamp
        from datetime import datetime

        config.created_at = datetime.now().isoformat()

        # Save configuration
        with open(config_file, "w") as f:
            json.dump(asdict(config), f, indent=2)

        self.console.print(f"💾 Configuration saved to: {config_file}")

        # Also save as environment file
        env_file = config_dir / f"{config.config_name}.env"
        self._save_env_file(config, env_file)
        self.console.print(f"📄 Environment file saved to: {env_file}")

    def _save_env_file(self, config: OPCUAConnectionConfig, env_file: Path) -> None:
        """Save configuration as environment file."""
        env_content = f"""# OPC-UA Connection Configuration: {config.config_name}
# Generated by IGN Scripts OPC-UA Configuration Wizard
# {config.description}

# Basic Connection
OPCUA_SERVER_URL={config.server_url}
OPCUA_USERNAME={config.username}
OPCUA_PASSWORD={config.password}

# Security Configuration
OPCUA_SECURITY_POLICY={config.security_policy}
OPCUA_SECURITY_MODE={config.security_mode}

# Certificate Paths
OPCUA_CLIENT_CERT_PATH={config.client_cert_path}
OPCUA_CLIENT_KEY_PATH={config.client_key_path}
OPCUA_SERVER_CERT_PATH={config.server_cert_path}

# Certificate Generation Parameters
OPCUA_APPLICATION_URI={config.application_uri}
OPCUA_APPLICATION_NAME={config.application_name}
OPCUA_ORGANIZATION={config.organization}
OPCUA_DNS_NAMES={",".join(config.dns_names)}
OPCUA_IP_ADDRESSES={",".join(config.ip_addresses)}

# Connection Settings
OPCUA_TIMEOUT={config.timeout}
OPCUA_SESSION_TIMEOUT={config.session_timeout}
OPCUA_SUBSCRIPTION_PERIOD={config.subscription_period}

# Ignition Settings
IGNITION_GATEWAY_URL={config.ignition_gateway_url}
IGNITION_PROJECT={config.ignition_project}

# Metadata
CONFIG_NAME={config.config_name}
CONFIG_VERIFIED={str(config.verified).lower()}
CONFIG_CREATED={config.created_at}
"""

        with open(env_file, "w") as f:
            f.write(env_content)


class OPCUAConfigManager:
    """Manage OPC-UA connection configurations."""

    def __init__(self) -> Any:
        self.config_dir = Path("configs/opcua")
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def list_configurations(self) -> list[OPCUAConnectionConfig]:
        """List all saved configurations."""
        configs = []
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file) as f:
                    data = json.load(f)
                    configs.append(OPCUAConnectionConfig(**data))
            except Exception as e:
                console.print(f"⚠️ Error loading {config_file}: {e}")

        return configs

    def load_configuration(self, name: str) -> OPCUAConnectionConfig | None:
        """Load a specific configuration."""
        config_file = self.config_dir / f"{name}.json"
        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                data = json.load(f)
                return OPCUAConnectionConfig(**data)
        except Exception as e:
            console.print(f"⚠️ Error loading configuration: {e}")
            return None

    def delete_configuration(self, name: str) -> bool:
        """Delete a configuration."""
        config_file = self.config_dir / f"{name}.json"
        env_file = self.config_dir / f"{name}.env"

        try:
            if config_file.exists():
                config_file.unlink()
            if env_file.exists():
                env_file.unlink()
            return True
        except Exception as e:
            console.print(f"⚠️ Error deleting configuration: {e}")
            return False

    def display_configurations(self) -> None:
        """Display all configurations in a table."""
        configs = self.list_configurations()

        if not configs:
            console.print("📄 No saved configurations found")
            return

        table = Table(title="🔧 Saved OPC-UA Configurations")
        table.add_column("Name", style="cyan")
        table.add_column("Server URL", style="blue")
        table.add_column("Security", style="green")
        table.add_column("Username", style="yellow")
        table.add_column("Verified", style="bold")
        table.add_column("Created", style="dim")

        for config in configs:
            verified_icon = "✅" if config.verified else "❌"
            security = f"{config.security_policy}/{config.security_mode}"

            table.add_row(
                config.config_name,
                config.server_url,
                security,
                config.username or "Anonymous",
                verified_icon,
                config.created_at.split("T")[0] if config.created_at else "Unknown",
            )

        console.print(table)


# CLI Integration Functions
async def interactive_setup() -> OPCUAConnectionConfig:
    """Run interactive setup wizard."""
    wizard = OPCUAConnectionWizard()
    return await wizard.run_interactive_setup()


def list_configs() -> None:
    """List all saved configurations."""
    manager = OPCUAConfigManager()
    manager.display_configurations()


def load_config(name: str) -> OPCUAConnectionConfig | None:
    """Load a specific configuration."""
    manager = OPCUAConfigManager()
    return manager.load_configuration(name)


def delete_config(name: str) -> bool:
    """Delete a configuration."""
    manager = OPCUAConfigManager()
    return manager.delete_configuration(name)
