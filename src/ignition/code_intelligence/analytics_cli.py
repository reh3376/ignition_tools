"""CLI Integration for Advanced Analytics Dashboard - Phase 8.4.

Provides command-line interface for code intelligence analytics and optimization insights.
"""

import json
from dataclasses import asdict
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from .analytics_dashboard import CodeIntelligenceDashboard
from .documentation_sync import DocumentationSynchronizer
from .manager import CodeIntelligenceManager

console = Console()


def _initialize_systems():
    """Initialize code intelligence systems with proper error handling."""
    try:
        from src.ignition.graph.client import IgnitionGraphClient

        graph_client = IgnitionGraphClient()
        if not graph_client.connect():
            console.print("❌ Failed to connect to Neo4j database", style="red")
            return None, None

        code_manager = CodeIntelligenceManager(graph_client)
        dashboard = CodeIntelligenceDashboard(code_manager)

        return code_manager, dashboard
    except Exception as e:
        console.print(f"❌ Failed to initialize systems: {e}", style="red")
        return None, None


@click.group(name="analytics")
def analytics_group() -> None:
    """Advanced analytics and optimization tools."""
    pass


@analytics_group.command()
@click.option("--days", "-d", default=90, help="Analysis period in days")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format",
)
@click.option("--save", "-s", type=click.Path(), help="Save results to file")
def health(days: int, format: str, save: str) -> None:
    """Generate comprehensive codebase health metrics."""
    console.print("🏥 Analyzing Codebase Health...", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing codebase health...", total=None)

            # Initialize systems
            code_manager, dashboard = _initialize_systems()
            if not code_manager or not dashboard:
                return

            # Get health metrics
            metrics = dashboard.get_codebase_health_metrics(days)

            progress.update(task, description="Generating report...")

            if format == "json":
                output = json.dumps(asdict(metrics), indent=2, default=str)
                console.print(output)
            elif format == "detailed":
                _display_detailed_health_report(metrics)
            else:
                _display_health_table(metrics)

            if save:
                with open(save, "w") as f:
                    json.dump(asdict(metrics), f, indent=2, default=str)
                console.print(f"✅ Results saved to {save}", style="green")

    except Exception as e:
        console.print(f"❌ Error analyzing codebase health: {e}", style="red")


@analytics_group.command()
@click.option("--max-nodes", "-n", default=50, help="Maximum nodes in graph")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "mermaid"]),
    default="table",
    help="Output format",
)
@click.option("--save", "-s", type=click.Path(), help="Save graph data to file")
def dependencies(max_nodes: int, format: str, save: str) -> None:
    """Analyze dependency graph and coupling."""
    console.print("🕸️  Analyzing Dependency Graph...", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Building dependency graph...", total=None)

            # Initialize systems
            code_manager, dashboard = _initialize_systems()
            if not code_manager or not dashboard:
                return

            # Get dependency graph
            nodes, edges = dashboard.get_dependency_graph(max_nodes)

            progress.update(task, description="Analyzing relationships...")

            if format == "json":
                output = {
                    "nodes": [asdict(node) for node in nodes],
                    "edges": [asdict(edge) for edge in edges],
                }
                console.print(json.dumps(output, indent=2))
            elif format == "mermaid":
                _display_mermaid_graph(nodes, edges)
            else:
                _display_dependency_table(nodes, edges)

            if save:
                output = {
                    "nodes": [asdict(node) for node in nodes],
                    "edges": [asdict(edge) for edge in edges],
                }
                with open(save, "w") as f:
                    json.dump(output, f, indent=2)
                console.print(f"✅ Graph data saved to {save}", style="green")

    except Exception as e:
        console.print(f"❌ Error analyzing dependencies: {e}", style="red")


@analytics_group.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "tree"]),
    default="table",
    help="Output format",
)
@click.option(
    "--severity",
    "-s",
    type=click.Choice(["all", "critical", "high", "medium"]),
    default="all",
    help="Filter by severity",
)
def debt(format: str, severity: str) -> None:
    """Identify and prioritize technical debt."""
    console.print("💳 Analyzing Technical Debt...", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Identifying technical debt...", total=None)

            # Initialize systems
            code_manager, dashboard = _initialize_systems()
            if not code_manager or not dashboard:
                return

            # Get health metrics (contains debt information)
            metrics = dashboard.get_codebase_health_metrics()

            progress.update(task, description="Prioritizing debt items...")

            if format == "json":
                output = {
                    "debt_score": metrics.technical_debt_score,
                    "hotspots": metrics.debt_hotspots,
                    "candidates": metrics.refactoring_candidates,
                }
                console.print(json.dumps(output, indent=2))
            elif format == "tree":
                _display_debt_tree(metrics)
            else:
                _display_debt_table(metrics, severity)

    except Exception as e:
        console.print(f"❌ Error analyzing technical debt: {e}", style="red")


@analytics_group.command()
@click.option("--days", "-d", default=180, help="Analysis period in days")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
def trends(days: int, format: str) -> None:
    """Analyze complexity and quality trends."""
    console.print("📈 Analyzing Code Trends...", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing trends...", total=None)

            # Initialize systems
            code_manager, dashboard = _initialize_systems()
            if not code_manager or not dashboard:
                return

            # For now, get current complexity distribution as trend indicator
            metrics = dashboard.get_codebase_health_metrics(days)

            progress.update(task, description="Calculating trends...")

            trends_data = {
                "complexity_distribution": metrics.complexity_distribution,
                "maintainability_distribution": metrics.maintainability_distribution,
                "quality_trend": metrics.quality_trend,
                "average_complexity": metrics.average_complexity,
                "max_complexity": metrics.max_complexity,
                "large_files_count": metrics.large_files_count,
            }

            if format == "json":
                console.print(json.dumps(trends_data, indent=2))
            else:
                _display_trends_table(trends_data)

    except Exception as e:
        console.print(f"❌ Error analyzing trends: {e}", style="red")


@analytics_group.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
def optimization(format: str) -> None:
    """Generate performance optimization insights."""
    console.print("⚡ Generating Optimization Insights...", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing performance patterns...", total=None)

            # Initialize systems
            code_manager, dashboard = _initialize_systems()
            if not code_manager or not dashboard:
                return

            # Get health metrics for optimization insights
            metrics = dashboard.get_codebase_health_metrics()

            progress.update(task, description="Generating recommendations...")

            # Create optimization insights from metrics
            insights = {
                "bottlenecks": [
                    {
                        "file_path": item["file_path"],
                        "reason": f"High complexity ({item.get('complexity', 0):.1f}) and {item.get('lines', 0)} lines",
                        "impact": "high" if item.get("lines", 0) > 1500 else "medium",
                    }
                    for item in metrics.largest_files[:5]
                ],
                "coupling_issues": [
                    {
                        "file_path": item["file_path"],
                        "coupling_score": item.get("total_coupling", 0),
                        "recommendation": "Reduce dependencies and improve modularity",
                    }
                    for item in metrics.highly_coupled_files[:5]
                ],
                "architectural_recommendations": [
                    "Consider implementing layered architecture for better separation",
                    "Use dependency injection to reduce coupling",
                    "Extract common functionality into shared modules",
                    "Implement proper error handling patterns",
                ],
            }

            if format == "json":
                console.print(json.dumps(insights, indent=2))
            else:
                _display_optimization_insights(insights)

    except Exception as e:
        console.print(f"❌ Error generating optimization insights: {e}", style="red")


@analytics_group.command()
def refresh() -> None:
    """Refresh dependency relationships between code files."""
    console.print("🔄 Refreshing Dependencies...", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing file dependencies...", total=None)

            # Initialize systems
            code_manager, dashboard = _initialize_systems()
            if not code_manager or not dashboard:
                return

            # Import and use dependency analyzer
            from .dependency_analyzer import DependencyAnalyzer

            analyzer = DependencyAnalyzer(code_manager.client)

            progress.update(task, description="Creating dependency relationships...")
            relationships_created = analyzer.analyze_and_create_dependencies()

            progress.update(task, description="Getting dependency metrics...")
            metrics = analyzer.get_dependency_metrics()

            console.print(
                f"✅ Created {relationships_created} dependency relationships",
                style="green",
            )

            if metrics.get("total_dependencies", 0) > 0:
                console.print(f"📊 Total dependencies: {metrics['total_dependencies']}")

                if metrics.get("circular_dependencies"):
                    console.print(
                        f"⚠️  Found {len(metrics['circular_dependencies'])} circular dependencies",
                        style="yellow",
                    )
                    for cycle in metrics["circular_dependencies"][:3]:
                        cycle_str = " → ".join([Path(f).name for f in cycle])
                        console.print(f"   • {cycle_str}", style="yellow")
                else:
                    console.print("✅ No circular dependencies found", style="green")

    except Exception as e:
        console.print(f"❌ Error refreshing dependencies: {e}", style="red")


@analytics_group.command()
@click.option("--check-sync", is_flag=True, help="Check documentation synchronization status")
@click.option("--update-api", is_flag=True, help="Update API documentation")
@click.option("--validate-refs", is_flag=True, help="Validate cross-references")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
def docs(check_sync: bool, update_api: bool, validate_refs: bool, format: str) -> None:
    """Documentation synchronization and validation."""
    console.print("📚 Analyzing Documentation...", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing documentation sync...", total=None)

            # Initialize systems
            code_manager, dashboard = _initialize_systems()
            if not code_manager or not dashboard:
                return

            project_root = Path.cwd()
            doc_sync = DocumentationSynchronizer(code_manager, project_root)

            results = {}

            if check_sync:
                progress.update(task, description="Checking documentation sync status...")
                doc_items = doc_sync.analyze_documentation_sync_status()
                results["sync_status"] = [asdict(item) for item in doc_items]

            if validate_refs:
                progress.update(task, description="Validating cross-references...")
                validation_issues = doc_sync.validate_cross_references()
                results["validation_issues"] = validation_issues

            if update_api:
                progress.update(task, description="Updating API documentation...")
                # This would update API docs for recently changed files
                results["api_updates"] = "API documentation update feature available"

            if not any([check_sync, update_api, validate_refs]):
                # Default: show sync status
                doc_items = doc_sync.analyze_documentation_sync_status()
                results["sync_status"] = [asdict(item) for item in doc_items]

            if format == "json":
                console.print(json.dumps(results, indent=2, default=str))
            else:
                _display_documentation_status(results)

    except Exception as e:
        console.print(f"❌ Error analyzing documentation: {e}", style="red")


# Display helper functions


def _display_health_table(metrics):
    """Display health metrics in table format."""
    # Main metrics table
    main_table = Table(
        title="🏥 Codebase Health Metrics",
        show_header=True,
        header_style="bold magenta",
    )
    main_table.add_column("Metric", style="cyan")
    main_table.add_column("Value", style="green")
    main_table.add_column("Status", style="yellow")

    # Determine status colors
    def get_status(value, thresholds):
        if value <= thresholds[0]:
            return "[green]Excellent[/green]"
        elif value <= thresholds[1]:
            return "[yellow]Good[/yellow]"
        elif value <= thresholds[2]:
            return "[orange3]Fair[/orange3]"
        else:
            return "[red]Poor[/red]"

    debt_status = get_status(metrics.technical_debt_score, [0.3, 0.5, 0.7])
    complexity_status = get_status(metrics.average_complexity, [15, 25, 40])

    main_table.add_row("Total Files", str(metrics.total_files), "📁")
    main_table.add_row("Total Lines", f"{metrics.total_lines:,}", "📄")
    main_table.add_row("Total Classes", str(metrics.total_classes), "🏗️")
    main_table.add_row("Total Methods", str(metrics.total_methods), "⚙️")
    main_table.add_row("Average Complexity", f"{metrics.average_complexity:.1f}", complexity_status)
    main_table.add_row("Technical Debt Score", f"{metrics.technical_debt_score:.2f}", debt_status)
    main_table.add_row("Large Files (>1000 lines)", str(metrics.large_files_count), "📊")
    main_table.add_row("Quality Trend", metrics.quality_trend, "📈")

    console.print(main_table)

    # Complexity distribution
    if metrics.complexity_distribution:
        comp_table = Table(title="📊 Complexity Distribution", show_header=True)
        comp_table.add_column("Range", style="cyan")
        comp_table.add_column("Count", style="green")
        comp_table.add_column("Percentage", style="yellow")

        total_files = sum(metrics.complexity_distribution.values())
        for range_name, count in metrics.complexity_distribution.items():
            percentage = (count / total_files * 100) if total_files > 0 else 0
            comp_table.add_row(range_name, str(count), f"{percentage:.1f}%")

        console.print(comp_table)


def _display_detailed_health_report(metrics) -> None:
    """Display detailed health report."""
    console.print(
        Panel(
            f"🏥 Codebase Health Report - {metrics.generated_at.strftime('%Y-%m-%d %H:%M')}",
            title="Health Analysis",
            border_style="blue",
        )
    )

    # Overview
    console.print("📊 **Overview**")
    console.print(f"   • Files: {metrics.total_files:,}")
    console.print(f"   • Lines of Code: {metrics.total_lines:,}")
    console.print(f"   • Average File Size: {metrics.average_file_size:.0f} lines")
    console.print(f"   • Technical Debt Score: {metrics.technical_debt_score:.2f}/1.0")
    console.print()

    # Technical debt hotspots
    if metrics.debt_hotspots:
        console.print("🔥 **Technical Debt Hotspots**")
        for hotspot in metrics.debt_hotspots[:5]:
            console.print(f"   • {hotspot['file_path']} (Score: {hotspot['debt_score']:.2f})")
        console.print()

    # Largest files
    if metrics.largest_files:
        console.print("📄 **Largest Files**")
        for file_info in metrics.largest_files[:5]:
            console.print(
                f"   • {file_info['file_path']}: {file_info['lines']} lines, complexity {file_info['complexity']:.1f}"
            )
        console.print()

    # Highly coupled files
    if metrics.highly_coupled_files:
        console.print("🕸️  **Highly Coupled Files**")
        for file_info in metrics.highly_coupled_files[:5]:
            total_coupling = file_info.get("total_coupling", 0)
            console.print(f"   • {file_info['file_path']}: {total_coupling} connections")


def _display_dependency_table(nodes, edges) -> None:
    """Display dependency graph in table format."""
    # Nodes table
    nodes_table = Table(title="🕸️  Dependency Graph - Nodes", show_header=True)
    nodes_table.add_column("File", style="cyan", width=40)
    nodes_table.add_column("Lines", style="green")
    nodes_table.add_column("Complexity", style="yellow")
    nodes_table.add_column("Dependencies", style="blue")
    nodes_table.add_column("Dependents", style="magenta")
    nodes_table.add_column("Risk", style="red")

    for node in nodes[:20]:  # Show top 20
        risk_color = {
            "critical": "[red]Critical[/red]",
            "high": "[orange3]High[/orange3]",
            "medium": "[yellow]Medium[/yellow]",
            "low": "[green]Low[/green]",
        }.get(node.risk_level, node.risk_level)

        nodes_table.add_row(
            Path(node.file_path).name,
            str(node.lines),
            f"{node.complexity:.1f}",
            str(node.out_degree),
            str(node.in_degree),
            risk_color,
        )

    console.print(nodes_table)

    # Summary stats
    if nodes:
        console.print(f"\n📈 **Summary**: {len(nodes)} nodes, {len(edges)} edges")
        avg_complexity = sum(n.complexity for n in nodes) / len(nodes)
        console.print(f"   • Average complexity: {avg_complexity:.1f}")
        console.print(f"   • High-risk files: {len([n for n in nodes if n.risk_level in ['critical', 'high']])}")


def _display_mermaid_graph(nodes, edges) -> None:
    """Display dependency graph in Mermaid format."""
    console.print("```mermaid")
    console.print("graph TD")

    # Add nodes with styling based on risk
    for node in nodes[:20]:  # Limit for readability
        node_id = Path(node.file_path).stem.replace("-", "_").replace(".", "_")
        risk_class = {
            "critical": ":::critical",
            "high": ":::high",
            "medium": ":::medium",
            "low": ":::low",
        }.get(node.risk_level, "")

        console.print(f'    {node_id}["{Path(node.file_path).name}"] {risk_class}')

    # Add edges
    displayed_nodes = {Path(n.file_path).stem.replace("-", "_").replace(".", "_") for n in nodes[:20]}
    for edge in edges:
        source_id = Path(edge.source).stem.replace("-", "_").replace(".", "_")
        target_id = Path(edge.target).stem.replace("-", "_").replace(".", "_")

        if source_id in displayed_nodes and target_id in displayed_nodes:
            console.print(f"    {source_id} --> {target_id}")

    # Add styling
    console.print("    classDef critical fill:#ff6b6b")
    console.print("    classDef high fill:#ffa726")
    console.print("    classDef medium fill:#ffeb3b")
    console.print("    classDef low fill:#4caf50")
    console.print("```")


def _display_debt_table(metrics, severity_filter) -> None:
    """Display technical debt in table format."""
    # Debt overview
    console.print(
        Panel(
            f"💳 Technical Debt Score: {metrics.technical_debt_score:.2f}/1.0",
            title="Debt Overview",
            border_style="yellow",
        )
    )

    # Hotspots table
    if metrics.debt_hotspots:
        hotspots_table = Table(title="🔥 Technical Debt Hotspots", show_header=True)
        hotspots_table.add_column("File", style="cyan", width=40)
        hotspots_table.add_column("Debt Score", style="red")
        hotspots_table.add_column("Primary Issues", style="yellow")

        for hotspot in metrics.debt_hotspots:
            if severity_filter == "all" or "critical" in str(hotspot.get("debt_score", 0)):
                issues = ", ".join(hotspot.get("primary_issues", []))
                hotspots_table.add_row(
                    Path(hotspot["file_path"]).name,
                    f"{hotspot['debt_score']:.2f}",
                    issues,
                )

        console.print(hotspots_table)

    # Refactoring candidates
    if metrics.refactoring_candidates:
        candidates_table = Table(title="🔧 Refactoring Candidates", show_header=True)
        candidates_table.add_column("File", style="cyan", width=40)
        candidates_table.add_column("Debt Score", style="orange3")
        candidates_table.add_column("Potential", style="green")

        for candidate in metrics.refactoring_candidates[:10]:
            candidates_table.add_row(
                Path(candidate["file_path"]).name,
                f"{candidate['debt_score']:.2f}",
                candidate.get("improvement_potential", "medium"),
            )

        console.print(candidates_table)


def _display_debt_tree(metrics) -> None:
    """Display technical debt in tree format."""
    tree = Tree("💳 Technical Debt Analysis")

    # Overall score
    tree.add(f"Overall Debt Score: {metrics.technical_debt_score:.2f}/1.0")

    # Hotspots
    if metrics.debt_hotspots:
        hotspots_branch = tree.add("🔥 Critical Hotspots")
        for hotspot in metrics.debt_hotspots[:5]:
            file_branch = hotspots_branch.add(f"{Path(hotspot['file_path']).name} (Score: {hotspot['debt_score']:.2f})")
            for issue in hotspot.get("primary_issues", []):
                file_branch.add(f"❌ {issue}")

    # Candidates
    if metrics.refactoring_candidates:
        candidates_branch = tree.add("🔧 Refactoring Candidates")
        for candidate in metrics.refactoring_candidates[:5]:
            candidates_branch.add(f"{Path(candidate['file_path']).name} (Score: {candidate['debt_score']:.2f})")

    console.print(tree)


def _display_trends_table(trends_data) -> None:
    """Display trends analysis in table format."""
    # Complexity trends
    comp_table = Table(title="📈 Complexity Trends", show_header=True)
    comp_table.add_column("Metric", style="cyan")
    comp_table.add_column("Current Value", style="green")
    comp_table.add_column("Trend", style="yellow")

    comp_table.add_row(
        "Average Complexity",
        f"{trends_data['average_complexity']:.1f}",
        trends_data["quality_trend"],
    )
    comp_table.add_row("Maximum Complexity", f"{trends_data['max_complexity']:.1f}", "")
    comp_table.add_row("Large Files Count", str(trends_data["large_files_count"]), "")

    console.print(comp_table)

    # Distribution tables
    if trends_data["complexity_distribution"]:
        dist_table = Table(title="📊 Current Distribution", show_header=True)
        dist_table.add_column("Category", style="cyan")
        dist_table.add_column("Complexity", style="green")
        dist_table.add_column("Maintainability", style="blue")

        comp_dist = trends_data["complexity_distribution"]
        maint_dist = trends_data["maintainability_distribution"]

        # Match up the distributions for display
        categories = ["Low", "Medium", "High", "Very High"]
        comp_keys = list(comp_dist.keys())
        maint_keys = list(maint_dist.keys())

        for i, category in enumerate(categories):
            comp_val = comp_dist.get(comp_keys[i] if i < len(comp_keys) else "", 0)
            maint_val = maint_dist.get(maint_keys[i] if i < len(maint_keys) else "", 0)
            dist_table.add_row(category, str(comp_val), str(maint_val))

        console.print(dist_table)


def _display_optimization_insights(insights) -> None:
    """Display optimization insights."""
    # Bottlenecks
    if insights["bottlenecks"]:
        bottlenecks_table = Table(title="⚡ Performance Bottlenecks", show_header=True)
        bottlenecks_table.add_column("File", style="cyan", width=30)
        bottlenecks_table.add_column("Reason", style="yellow", width=40)
        bottlenecks_table.add_column("Impact", style="red")

        for bottleneck in insights["bottlenecks"]:
            impact_color = "[red]High[/red]" if bottleneck["impact"] == "high" else "[yellow]Medium[/yellow]"
            bottlenecks_table.add_row(Path(bottleneck["file_path"]).name, bottleneck["reason"], impact_color)

        console.print(bottlenecks_table)

    # Coupling issues
    if insights["coupling_issues"]:
        coupling_table = Table(title="🕸️  Coupling Issues", show_header=True)
        coupling_table.add_column("File", style="cyan", width=30)
        coupling_table.add_column("Coupling Score", style="yellow")
        coupling_table.add_column("Recommendation", style="green", width=40)

        for issue in insights["coupling_issues"]:
            coupling_table.add_row(
                Path(issue["file_path"]).name,
                str(issue["coupling_score"]),
                issue["recommendation"],
            )

        console.print(coupling_table)

    # Architectural recommendations
    if insights["architectural_recommendations"]:
        console.print("\n🏗️  **Architectural Recommendations:**")
        for i, rec in enumerate(insights["architectural_recommendations"], 1):
            console.print(f"   {i}. {rec}")


def _display_documentation_status(results) -> None:
    """Display documentation analysis results."""
    if "sync_status" in results:
        sync_table = Table(title="📚 Documentation Sync Status", show_header=True)
        sync_table.add_column("Document", style="cyan", width=30)
        sync_table.add_column("Type", style="blue")
        sync_table.add_column("Status", style="green")
        sync_table.add_column("Priority", style="yellow")
        sync_table.add_column("Last Updated", style="magenta")

        for item in results["sync_status"][:15]:  # Show top 15
            status_color = {
                "synced": "[green]Synced[/green]",
                "outdated": "[yellow]Outdated[/yellow]",
                "missing": "[red]Missing[/red]",
            }.get(item["sync_status"], item["sync_status"])

            priority_color = {
                "critical": "[red]Critical[/red]",
                "high": "[orange3]High[/orange3]",
                "medium": "[yellow]Medium[/yellow]",
                "low": "[green]Low[/green]",
            }.get(item["update_priority"], item["update_priority"])

            sync_table.add_row(
                Path(item["doc_path"]).name,
                item["doc_type"],
                status_color,
                priority_color,
                (
                    item["last_updated"][:10]
                    if isinstance(item["last_updated"], str)
                    else str(item["last_updated"])[:10]
                ),
            )

        console.print(sync_table)

    if results.get("validation_issues"):
        issues_table = Table(title="❌ Cross-Reference Issues", show_header=True)
        issues_table.add_column("Document", style="cyan", width=25)
        issues_table.add_column("Reference", style="yellow", width=25)
        issues_table.add_column("Issue", style="red", width=30)

        for issue in results["validation_issues"][:10]:
            issues_table.add_row(Path(issue["doc_file"]).name, issue["reference"], issue["issue"])

        console.print(issues_table)

    if "api_updates" in results:
        console.print(f"\n✅ {results['api_updates']}")


# Export the command group
__all__ = ["analytics_group"]
