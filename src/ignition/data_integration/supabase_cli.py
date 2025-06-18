"""Supabase CLI Commands for IGN Scripts.

This module provides CLI commands for Supabase database management including:
- Database setup and initialization
- Backup and recovery operations
- Status monitoring and health checks
- Configuration management
- Docker container management

Commands:
- supabase setup: Initialize Supabase database and create configuration files
- supabase status: Show database status and health information
- supabase backup: Create database backup
- supabase restore: Restore from backup
- supabase start: Start Supabase Docker services
- supabase stop: Stop Supabase Docker services

Author: IGN Scripts Data Integration System
Created: 2025-01-28
"""

import json
import subprocess
import sys
from pathlib import Path

import click

# Try to import the Supabase manager
try:
    from .supabase_manager import SupabaseManager, create_supabase_manager
except ImportError:
    # Fallback if module is not available
    SupabaseManager = None
    create_supabase_manager = None


@click.group()
def supabase() -> None:
    """Supabase database management commands."""
    pass


@supabase.command()
@click.option("--force", is_flag=True, help="Force setup even if already configured")
@click.option(
    "--project-name", default="IGN Scripts Development", help="Supabase project name"
)
@click.option("--org-name", default="IGN Scripts", help="Organization name")
def setup(force: bool, project_name: str, org_name: str) -> None:
    """Initialize Supabase database and create configuration files."""
    click.echo("🚀 Setting up Supabase database for IGN Scripts...")

    if not create_supabase_manager:
        click.echo("❌ Supabase manager not available. Please install dependencies.")
        return

    try:
        # Create Supabase manager
        manager = create_supabase_manager()

        # Update configuration
        manager.config.project_name = project_name
        manager.config.organization_name = org_name

        # Create initialization files
        click.echo("📄 Creating database initialization script...")
        init_script = manager.create_initialization_script()
        click.echo(f"   ✅ Created: {init_script}")

        click.echo("🔄 Creating backup script...")
        backup_script = manager.create_backup_script()
        click.echo(f"   ✅ Created: {backup_script}")

        click.echo("⚙️ Creating environment configuration...")
        env_file = manager.create_docker_compose_env()
        click.echo(f"   ✅ Created: {env_file}")

        # Create directories
        click.echo("📁 Creating data directories...")
        Path("supabase-data/db").mkdir(parents=True, exist_ok=True)
        Path("supabase-data/backups").mkdir(parents=True, exist_ok=True)
        Path("supabase-data/init").mkdir(parents=True, exist_ok=True)
        click.echo("   ✅ Created data directories")

        click.echo("\n🎉 Supabase setup completed successfully!")
        click.echo("\n📋 Next steps:")
        click.echo("   1. Review configuration in .env.supabase")
        click.echo("   2. Start services: ign data supabase start")
        click.echo("   3. Check status: ign data supabase status")
        click.echo("   4. Access Studio: http://localhost:3001")

    except Exception as e:
        click.echo(f"❌ Setup failed: {e!s}")
        sys.exit(1)


@supabase.command()
@click.option(
    "--format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
def status(format: str) -> None:
    """Show Supabase database status and health information."""
    if not create_supabase_manager:
        click.echo("❌ Supabase manager not available.")
        return

    try:
        manager = create_supabase_manager()
        status_info = manager.get_database_status()

        if format == "json":
            click.echo(json.dumps(status_info, indent=2))
        else:
            # Table format
            click.echo("📊 Supabase Database Status")
            click.echo("=" * 50)

            if status_info.get("status") == "healthy":
                click.echo(f"🟢 Status: {status_info['status'].upper()}")
                click.echo(
                    f"💾 Database Size: {status_info.get('database_size', 'Unknown')}"
                )
                click.echo(f"🔗 Connections: {status_info.get('connection_count', 0)}")

                tables = status_info.get("tables", [])
                if tables:
                    click.echo(f"\n📋 Tables ({len(tables)}):")
                    for table in tables:
                        click.echo(
                            f"   • {table['schema']}.{table['name']} "
                            f"(I:{table['inserts']}, U:{table['updates']}, D:{table['deletes']})"
                        )
                else:
                    click.echo("\n📋 No tables found in ignition schema")

            else:
                click.echo(f"🔴 Status: {status_info.get('status', 'Unknown').upper()}")
                if "message" in status_info:
                    click.echo(f"❌ Error: {status_info['message']}")

            click.echo(
                f"\n🕒 Last checked: {status_info.get('last_checked', 'Unknown')}"
            )

    except Exception as e:
        click.echo(f"❌ Failed to get status: {e!s}")


@supabase.command()
@click.option("--name", help="Custom backup name")
def backup(name: str) -> None:
    """Create a database backup."""
    if not create_supabase_manager:
        click.echo("❌ Supabase manager not available.")
        return

    try:
        manager = create_supabase_manager()

        click.echo("🔄 Creating database backup...")
        result = manager.create_backup(name)

        if result["status"] == "success":
            click.echo("✅ Backup created successfully!")
            click.echo(f"📁 File: {result['backup_file']}")
            click.echo(f"💾 Size: {result['backup_size']} bytes")
            click.echo(f"🕒 Created: {result['created_at']}")
        else:
            click.echo(f"❌ Backup failed: {result['message']}")

    except Exception as e:
        click.echo(f"❌ Backup failed: {e!s}")


@supabase.command()
@click.option("--keep-days", default=7, help="Number of days to keep backups")
def cleanup(keep_days: int) -> None:
    """Clean up old backup files."""
    if not create_supabase_manager:
        click.echo("❌ Supabase manager not available.")
        return

    try:
        manager = create_supabase_manager()

        click.echo(f"🧹 Cleaning up backups older than {keep_days} days...")
        result = manager.cleanup_old_backups(keep_days)

        if result["status"] == "success":
            click.echo(f"✅ {result['message']}")
            if result["deleted_files"]:
                click.echo("🗑️ Deleted files:")
                for file in result["deleted_files"]:
                    click.echo(f"   • {file}")
        else:
            click.echo(f"❌ Cleanup failed: {result.get('message', 'Unknown error')}")

    except Exception as e:
        click.echo(f"❌ Cleanup failed: {e!s}")


@supabase.command()
def backups() -> None:
    """List available database backups."""
    if not create_supabase_manager:
        click.echo("❌ Supabase manager not available.")
        return

    try:
        manager = create_supabase_manager()
        backup_list = manager.list_backups()

        if backup_list:
            click.echo("📦 Available Backups")
            click.echo("=" * 50)
            for backup in backup_list:
                size_mb = backup["size"] / (1024 * 1024)
                click.echo(f"📁 {backup['name']}")
                click.echo(f"   Size: {size_mb:.2f} MB")
                click.echo(f"   Created: {backup['created_at']}")
                click.echo(f"   Age: {backup['age_days']} days")
                click.echo()
        else:
            click.echo("📦 No backups found")

    except Exception as e:
        click.echo(f"❌ Failed to list backups: {e!s}")


@supabase.command()
@click.option(
    "--services", default="all", help="Services to start (all, db, api, studio)"
)
def start(services: str) -> None:
    """Start Supabase Docker services."""
    click.echo("🚀 Starting Supabase services...")

    # Map service names to Docker Compose service names
    service_map = {
        "all": [
            "supabase-db",
            "supabase-api",
            "supabase-rest",
            "supabase-realtime",
            "supabase-studio",
            "supabase-meta",
        ],
        "db": ["supabase-db"],
        "api": ["supabase-api", "supabase-rest"],
        "studio": ["supabase-studio", "supabase-meta"],
    }

    service_list = service_map.get(services, [services])

    try:
        for service in service_list:
            click.echo(f"🔄 Starting {service}...")
            result = subprocess.run(
                ["docker-compose", "up", "-d", service], capture_output=True, text=True
            )

            if result.returncode == 0:
                click.echo(f"   ✅ {service} started")
            else:
                click.echo(f"   ❌ Failed to start {service}: {result.stderr}")

        click.echo("\n🎉 Supabase services started!")
        click.echo("🌐 Access points:")
        click.echo("   • Studio Dashboard: http://localhost:3001")
        click.echo("   • REST API: http://localhost:3000")
        click.echo("   • Auth API: http://localhost:8000")
        click.echo("   • Real-time: http://localhost:4000")
        click.echo("   • Meta API: http://localhost:8080")

    except Exception as e:
        click.echo(f"❌ Failed to start services: {e!s}")


@supabase.command()
@click.option(
    "--services", default="all", help="Services to stop (all, db, api, studio)"
)
def stop(services: str) -> None:
    """Stop Supabase Docker services."""
    click.echo("🛑 Stopping Supabase services...")

    # Map service names to Docker Compose service names
    service_map = {
        "all": [
            "supabase-db",
            "supabase-api",
            "supabase-rest",
            "supabase-realtime",
            "supabase-studio",
            "supabase-meta",
        ],
        "db": ["supabase-db"],
        "api": ["supabase-api", "supabase-rest"],
        "studio": ["supabase-studio", "supabase-meta"],
    }

    service_list = service_map.get(services, [services])

    try:
        for service in service_list:
            click.echo(f"🔄 Stopping {service}...")
            result = subprocess.run(
                ["docker-compose", "stop", service], capture_output=True, text=True
            )

            if result.returncode == 0:
                click.echo(f"   ✅ {service} stopped")
            else:
                click.echo(f"   ❌ Failed to stop {service}: {result.stderr}")

        click.echo("\n✅ Supabase services stopped!")

    except Exception as e:
        click.echo(f"❌ Failed to stop services: {e!s}")


@supabase.command()
@click.option(
    "--format",
    type=click.Choice(["json", "yaml"]),
    default="yaml",
    help="Output format",
)
def config(format: str) -> None:
    """Show Supabase configuration summary."""
    if not create_supabase_manager:
        click.echo("❌ Supabase manager not available.")
        return

    try:
        manager = create_supabase_manager()
        config_summary = manager.generate_configuration_summary()

        if format == "json":
            click.echo(json.dumps(config_summary, indent=2))
        else:
            # YAML-like format
            click.echo("📋 Supabase Configuration Summary")
            click.echo("=" * 50)

            # Database configuration
            db_config = config_summary["supabase_configuration"]["database"]
            click.echo("🗄️ Database:")
            click.echo(f"   Host: {db_config['host']}:{db_config['port']}")
            click.echo(f"   Name: {db_config['name']}")
            click.echo(f"   User: {db_config['user']}")

            # API configuration
            api_config = config_summary["supabase_configuration"]["api"]
            click.echo("\n🔌 API:")
            click.echo(f"   URL: {api_config['url']}")
            click.echo(f"   Site: {api_config['site_url']}")

            # Project configuration
            project_config = config_summary["supabase_configuration"]["project"]
            click.echo("\n📁 Project:")
            click.echo(f"   Name: {project_config['name']}")
            click.echo(f"   Organization: {project_config['organization']}")

            # Docker services
            services = config_summary["docker_services"]
            click.echo(f"\n🐳 Docker Services ({len(services)}):")
            for service in services:
                click.echo(
                    f"   • {service['name']} (:{service['port']}) - {service['description']}"
                )

            # File structure
            files = config_summary["file_structure"]
            click.echo("\n📁 File Structure:")
            for key, path in files.items():
                click.echo(f"   • {key.replace('_', ' ').title()}: {path}")

            click.echo(f"\n🕒 Generated: {config_summary['generated_at']}")

    except Exception as e:
        click.echo(f"❌ Failed to get configuration: {e!s}")


# Command aliases for convenience
@supabase.command()
def init() -> None:
    """Alias for setup command."""
    setup.callback(
        force=False, project_name="IGN Scripts Development", org_name="IGN Scripts"
    )


@supabase.command()
def health() -> None:
    """Alias for status command."""
    status.callback(format="table")


if __name__ == "__main__":
    supabase()
