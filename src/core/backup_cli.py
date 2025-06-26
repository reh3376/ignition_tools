#!/usr/bin/env python3
"""CLI integration for Neo4j backup management."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.ignition.graph.backup_manager import Neo4jBackupManager

console = Console()


@click.group()
def backup() -> None:
    """🗄️ Neo4j database backup and restore operations."""
    pass


@backup.command()
@click.option("--reason", "-r", default="Manual backup", help="Reason for creating backup")
@click.option(
    "--auto",
    "-a",
    is_flag=True,
    help="Create backup only if significant changes detected",
)
def create(reason: str, auto: bool) -> None:
    """📦 Create a full database backup."""
    try:
        manager = Neo4jBackupManager()

        if auto:
            console.print("[bold blue]🔍 Checking for significant changes...[/bold blue]")
            if manager.auto_backup_on_significant_changes():
                console.print("[green]✅ Auto-backup created due to significant changes[/green]")
            else:
                console.print("[yellow]ℹ️ No backup needed - no significant changes detected[/yellow]")
        else:
            with console.status("[bold blue]Creating backup..."):
                success, result = manager.create_full_backup(reason)

            if success:
                console.print(f"[green]✅ Backup created successfully:[/green] {result}")
            else:
                console.print(f"[red]❌ Backup failed:[/red] {result}")

    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")


@backup.command()
@click.option(
    "--file",
    "-f",
    help="Specific backup file to restore from (if not specified, uses latest)",
)
@click.option("--confirm", "-y", is_flag=True, help="Skip confirmation prompt")
def restore(file: str, confirm: bool) -> None:
    """🔄 Restore database from backup."""
    try:
        manager = Neo4jBackupManager()

        # Show available backups
        backups = manager.list_backups()
        if not backups:
            console.print("[red]❌ No backup files found[/red]")
            return

        # Determine which backup to use
        backup_file = file or backups[0]["filename"]
        backup_info = manager.get_backup_info(backup_file)

        if not backup_info:
            console.print(f"[red]❌ Backup file not found:[/red] {backup_file}")
            return

        # Show backup information
        info_panel = Panel(
            f"[bold]Backup:[/bold] {backup_file}\n"
            f"[bold]Created:[/bold] {backup_info.get('datetime', 'Unknown')}\n"
            f"[bold]Reason:[/bold] {backup_info.get('reason', 'No reason')}\n"
            f"[bold]Nodes:[/bold] {backup_info.get('node_count', 0)}\n"
            f"[bold]Relationships:[/bold] {backup_info.get('relationship_count', 0)}\n"
            f"[bold]Size:[/bold] {backup_info.get('file_size', 0):,} bytes",
            title="🔄 Restore Information",
            border_style="yellow",
        )
        console.print(info_panel)

        # Confirmation
        if not confirm and not click.confirm("⚠️  This will DELETE all current data and restore from backup. Continue?"):
            console.print("[yellow]❌ Restore cancelled[/yellow]")
            return

        # Perform restore
        with console.status("[bold blue]Restoring database..."):
            success, result = manager.restore_from_backup(backup_file)

        if success:
            console.print(f"[green]✅ Database restored successfully:[/green] {result}")
        else:
            console.print(f"[red]❌ Restore failed:[/red] {result}")

    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")


@backup.command()
@click.option("--detailed", "-d", is_flag=True, help="Show detailed backup information")
def list(detailed: bool) -> None:
    """📋 list all available database backups."""
    try:
        manager = Neo4jBackupManager()
        backups = manager.list_backups()

        if not backups:
            console.print("[yellow]📭 No backup files found[/yellow]")
            return

        # Create table
        table = Table(
            title="📋 Available Database Backups",
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("Filename", style="cyan", no_wrap=True)
        table.add_column("Created", style="green")
        table.add_column("Reason", style="yellow")

        if detailed:
            table.add_column("Nodes", justify="right", style="blue")
            table.add_column("Relationships", justify="right", style="blue")
            table.add_column("Size", justify="right", style="dim")

        # Add backup data
        for backup in backups:
            row = [
                backup.get("filename", "Unknown"),
                (backup.get("datetime", "Unknown")[:19] if backup.get("datetime") else "Unknown"),
                (
                    backup.get("reason", "No reason")[:30] + "..."
                    if len(backup.get("reason", "")) > 30
                    else backup.get("reason", "No reason")
                ),
            ]

            if detailed:
                row.extend(
                    [
                        str(backup.get("node_count", 0)),
                        str(backup.get("relationship_count", 0)),
                        f"{backup.get('file_size', 0):,} bytes",
                    ]
                )

            table.add_row(*row)

        console.print(table)

        # Show summary
        latest = backups[0]
        summary = Panel(
            f"[bold]Latest backup:[/bold] {latest.get('filename', 'Unknown')}\n"
            f"[bold]Created:[/bold] {latest.get('datetime', 'Unknown')}\n"
            f"[bold]Data:[/bold] {latest.get('node_count', 0)} nodes, {latest.get('relationship_count', 0)} relationships",
            title="📊 Summary",
            border_style="green",
        )
        console.print(summary)

    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")


@backup.command()
@click.argument("filename")
def info(filename: str) -> None:
    """📄 Show detailed information about a specific backup."""
    try:
        manager = Neo4jBackupManager()
        backup_info = manager.get_backup_info(filename)

        if not backup_info:
            console.print(f"[red]❌ Backup file not found:[/red] {filename}")
            return

        # Create detailed info display
        info_text = ""
        for key, value in backup_info.items():
            if key == "file_size":
                value = f"{value:,} bytes"
            elif key == "datetime" and isinstance(value, str):
                value = value.replace("T", " ").split(".")[0]

            info_text += f"[bold]{key.replace('_', ' ').title()}:[/bold] {value}\n"

        info_panel = Panel(
            info_text.strip(),
            title=f"📄 Backup Information: {filename}",
            border_style="blue",
        )
        console.print(info_panel)

    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")


@backup.command()
@click.option("--threshold-nodes", default=50, help="Node count threshold for auto-backup")
@click.option("--threshold-rels", default=100, help="Relationship count threshold for auto-backup")
@click.option(
    "--threshold-percent",
    default=0.1,
    help="Percentage change threshold for auto-backup",
)
def status(threshold_nodes: int, threshold_rels: int, threshold_percent: float) -> None:
    """📊 Show database backup status and recommendations."""
    try:
        pass  # TODO: Add try block content
    except Exception:
        pass  # TODO: Handle exception
        manager = Neo4jBackupManager()

        # Get current database stats
        current_stats = manager._get_database_statistics()
        last_backup_stats = manager._get_last_backup_statistics()

        # Create status display
        status_text = f"""[bold]Current Database:[/bold]
• Nodes: {current_stats.get("node_count", 0):,}
• Relationships: {current_stats.get("relationship_count", 0):,}

[bold]Last Backup:[/bold]"""

        if last_backup_stats:
            status_text += f"""
• Nodes: {last_backup_stats.get("node_count", 0):,}
• Relationships: {last_backup_stats.get("relationship_count", 0):,}

[bold]Changes Since Last Backup:[/bold]
• Nodes: {current_stats.get("node_count", 0) - last_backup_stats.get("node_count", 0):+,}
• Relationships: {current_stats.get("relationship_count", 0) - last_backup_stats.get("relationship_count", 0):+,}"""
        else:
            status_text += "\n• No previous backup found"

        # Check if backup is recommended
        should_backup = manager._should_create_backup(current_stats, last_backup_stats)

        status_text += "\n\n[bold]Backup Recommendation:[/bold] "
        if should_backup:
            status_text += "[red]⚠️ Backup recommended[/red]"
        else:
            status_text += "[green]✅ No backup needed[/green]"

        status_panel = Panel(status_text, title="📊 Database Backup Status", border_style="blue")
        console.print(status_panel)

        # Show thresholds
        threshold_text = f"""[bold]Auto-Backup Thresholds:[/bold]
• Nodes: {threshold_nodes:,} new nodes
• Relationships: {threshold_rels:,} new relationships
• Percentage: {threshold_percent:.1%} increase"""

        threshold_panel = Panel(threshold_text, title="⚙️ Configuration", border_style="dim")
        console.print(threshold_panel)

    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")


@backup.command()
def init() -> None:
    """🚀 Create initial backup for application distribution."""
    try:
        console.print("[bold blue]🚀 Creating initial backup for application distribution...[/bold blue]")

        manager = Neo4jBackupManager()

        with console.status("[bold blue]Creating initial backup..."):
            success, result = manager.create_full_backup("Initial backup for application distribution")

        if success:
            console.print(f"[green]✅ Initial backup created:[/green] {result}")
            console.print("[green]This backup will be included with the application for new installations.[/green]")
        else:
            console.print(f"[red]❌ Failed to create initial backup:[/red] {result}")

    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")


if __name__ == "__main__":
    backup()
