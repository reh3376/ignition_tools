"""CLI Commands for Automated Code Refactoring System.

This module provides CLI commands for the refactoring system, integrating
with the existing IGN Scripts CLI infrastructure.
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path

import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[2]))

from ignition.code_intelligence.code_splitter import BatchCodeSplitter, CodeSplitter
from ignition.code_intelligence.refactor_analyzer import (
    LargeFileDetector,
    RefactoringRecommendationEngine,
)
from ignition.code_intelligence.refactoring_workflow import RefactoringWorkflow


@click.group(name="refactor")
def refactor_commands() -> None:
    """Automated code refactoring commands."""
    pass


@refactor_commands.command()
@click.option(
    "--directory", "-d", default="src", help="Directory to scan for large files"
)
@click.option("--threshold", "-t", default=1000, help="Line threshold for large files")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format",
)
def detect(directory: str, threshold: int, format: str) -> None:
    """Detect files that exceed size thresholds and need refactoring."""
    detector = LargeFileDetector(line_threshold=threshold)
    engine = RefactoringRecommendationEngine()

    try:
        oversized_files = detector.scan_directory(Path(directory))

        if not oversized_files:
            click.echo(f"✅ No files found exceeding {threshold} lines in {directory}")
            return

        click.echo(f"Found {len(oversized_files)} files exceeding {threshold} lines:")

        if format == "table":
            _display_files_table(oversized_files, engine)
        elif format == "json":
            _display_files_json(oversized_files, engine)
        elif format == "detailed":
            _display_files_detailed(oversized_files, engine)

    except Exception as e:
        click.echo(f"❌ Error detecting large files: {e!s}", err=True)
        sys.exit(1)


@refactor_commands.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["summary", "detailed", "json"]),
    default="summary",
    help="Output format",
)
def analyze(file_path: str, format: str) -> None:
    """Analyze a specific file for refactoring opportunities."""
    engine = RefactoringRecommendationEngine()
    file_path_obj = Path(file_path)

    try:
        recommendation = engine.analyze_file(file_path_obj)

        if not recommendation:
            click.echo(f"❌ Could not analyze {file_path}")
            sys.exit(1)

        if format == "summary":
            _display_analysis_summary(recommendation)
        elif format == "detailed":
            _display_analysis_detailed(recommendation)
        elif format == "json":
            _display_analysis_json(recommendation)

    except Exception as e:
        click.echo(f"❌ Error analyzing file: {e!s}", err=True)
        sys.exit(1)


@refactor_commands.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Simulate split without making changes")
@click.option("--no-git", is_flag=True, help="Don't preserve git history")
def split(file_path: str, dry_run: bool, no_git: bool) -> None:
    """Split a large file into smaller modules."""
    splitter = CodeSplitter(preserve_git_history=not no_git)
    file_path_obj = Path(file_path)

    try:
        click.echo(
            f"{'🔍 Simulating' if dry_run else '🔄 Executing'} split for {file_path}"
        )

        result = splitter.split_file(file_path_obj, dry_run=dry_run)

        if result.success:
            click.echo("✅ Split completed successfully!")
            click.echo(f"   New files created: {len(result.new_files)}")

            if result.new_files:
                for new_file in result.new_files:
                    click.echo(f"     - {new_file}")

            click.echo(f"   Classes moved: {len(result.moved_classes)}")
            if result.moved_classes:
                for cls in result.moved_classes:
                    click.echo(f"     - {cls}")

            click.echo(f"   Functions moved: {len(result.moved_functions)}")
            if result.moved_functions:
                for func in result.moved_functions:
                    click.echo(f"     - {func}")

            if result.import_updates:
                click.echo(
                    f"   Import updates needed in {len(result.import_updates)} files"
                )

        else:
            click.echo(f"❌ Split failed: {result.error_message}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error during split: {e!s}", err=True)
        sys.exit(1)


@refactor_commands.command()
@click.option("--directory", "-d", default="src", help="Directory to scan")
@click.option("--dry-run", is_flag=True, help="Simulate without making changes")
@click.option("--no-git", is_flag=True, help="Don't preserve git history")
@click.option("--max-files", default=5, help="Maximum number of files to process")
def batch_split(directory: str, dry_run: bool, no_git: bool, max_files: int) -> None:
    """Split multiple large files in batch."""
    BatchCodeSplitter(preserve_git_history=not no_git)

    try:
        click.echo(
            f"{'🔍 Simulating' if dry_run else '🔄 Executing'} batch split in {directory}"
        )

        # Get oversized files
        detector = LargeFileDetector()
        oversized_files = detector.scan_directory(Path(directory))[:max_files]

        if not oversized_files:
            click.echo("✅ No files found that need splitting")
            return

        click.echo(f"Processing {len(oversized_files)} files...")

        results = {}
        for file_path in oversized_files:
            splitter = CodeSplitter(preserve_git_history=not no_git)
            result = splitter.split_file(file_path, dry_run=dry_run)
            results[str(file_path)] = result

        # Display summary
        successful = sum(1 for r in results.values() if r.success)
        total = len(results)

        click.echo(f"\n{'=' * 60}")
        click.echo("BATCH SPLIT SUMMARY")
        click.echo(f"{'=' * 60}")
        click.echo(f"Files processed: {total}")
        click.echo(f"Successful: {successful}")
        click.echo(f"Failed: {total - successful}")

        # Show details for each file
        for file_path, result in results.items():
            status = "✅" if result.success else "❌"
            click.echo(
                f"{status} {Path(file_path).name}: {result.error_message or 'Success'}"
            )

    except Exception as e:
        click.echo(f"❌ Error during batch split: {e!s}", err=True)
        sys.exit(1)


@refactor_commands.command()
@click.option("--files", multiple=True, help="Specific files to refactor")
@click.option("--directory", "-d", default="src", help="Directory to scan")
@click.option("--dry-run", is_flag=True, help="Simulate without making changes")
@click.option("--no-git", is_flag=True, help="Don't use git integration")
def workflow(files: tuple, directory: str, dry_run: bool, no_git: bool) -> None:
    """Execute a comprehensive refactoring workflow."""
    project_root = Path.cwd()
    workflow_engine = RefactoringWorkflow(project_root, enable_git=not no_git)

    try:
        if files:
            target_files = [Path(f) for f in files]
        else:
            # Find large files automatically
            detector = LargeFileDetector()
            target_files = detector.scan_directory(Path(directory))[
                :5
            ]  # Limit to top 5

        if not target_files:
            click.echo("No files found that need refactoring")
            return

        click.echo(f"Planning refactoring workflow for {len(target_files)} files...")
        operations = workflow_engine.plan_refactoring_workflow(target_files)

        if not operations:
            click.echo("No refactoring operations needed")
            return

        click.echo(f"\nPlanned {len(operations)} refactoring operations:")
        for op in operations:
            risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(
                op.risk_level, "white"
            )
            click.echo(click.style(f"  - {op.description}", fg=risk_color))
            click.echo(f"    Risk: {op.risk_level}, Estimated: {op.estimated_time}s")

        if not dry_run and not click.confirm("\nProceed with refactoring workflow?"):
            click.echo("Workflow cancelled")
            return

        # Execute workflow
        result = workflow_engine.execute_workflow(operations, dry_run=dry_run)

        click.echo(f"\n{'=' * 60}")
        click.echo("REFACTORING WORKFLOW RESULTS")
        click.echo(f"{'=' * 60}")
        click.echo(f"Workflow ID: {result.workflow_id}")

        if result.success:
            click.echo(click.style("Success: ✅", fg="green"))
        else:
            click.echo(click.style("Success: ❌", fg="red"))

        click.echo(f"Operations completed: {len(result.operations_completed)}")
        click.echo(f"Operations failed: {len(result.operations_failed)}")
        click.echo(f"Files modified: {len(result.files_modified)}")
        click.echo(f"Files created: {len(result.files_created)}")

        if not result.success and result.error_message:
            click.echo(click.style(f"Error: {result.error_message}", fg="red"))

        if result.rollback_available:
            click.echo(f"Backup available at: {result.backup_location}")

    except Exception as e:
        click.echo(f"❌ Error during workflow: {e!s}", err=True)
        sys.exit(1)


@refactor_commands.command()
@click.argument("workflow_id")
def rollback(workflow_id: str) -> None:
    """Rollback a refactoring workflow."""
    project_root = Path.cwd()
    workflow_engine = RefactoringWorkflow(project_root)

    try:
        success = workflow_engine.rollback_workflow(workflow_id)

        if success:
            click.echo(f"✅ Successfully rolled back workflow {workflow_id}")
        else:
            click.echo(f"❌ Failed to rollback workflow {workflow_id}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error during rollback: {e!s}", err=True)
        sys.exit(1)


def _display_files_table(
    files: list[Path], engine: RefactoringRecommendationEngine
) -> None:
    """Display files in table format."""
    click.echo(f"\n{'File':<50} {'Lines':<8} {'Complexity':<12} {'Issues':<8}")
    click.echo("-" * 80)

    for file_path in files:
        try:
            recommendation = engine.analyze_file(file_path)
            if recommendation:
                issues = len(recommendation.single_responsibility_violations)
                click.echo(
                    f"{file_path!s:<50} {recommendation.physical_lines:<8} {recommendation.complexity_score:<12.1f} {issues:<8}"
                )
            else:
                click.echo(f"{file_path!s:<50} {'N/A':<8} {'N/A':<12} {'N/A':<8}")
        except Exception:
            click.echo(f"{file_path!s:<50} {'ERROR':<8} {'ERROR':<12} {'ERROR':<8}")


def _display_files_json(
    files: list[Path], engine: RefactoringRecommendationEngine
) -> None:
    """Display files in JSON format."""
    import json

    data = []
    for file_path in files:
        try:
            recommendation = engine.analyze_file(file_path)
            if recommendation:
                data.append(
                    {
                        "file": str(file_path),
                        "physical_lines": recommendation.physical_lines,
                        "complexity": recommendation.complexity_score,
                        "maintainability": recommendation.maintainability_index,
                        "violations": recommendation.single_responsibility_violations,
                        "risk_level": (
                            "high"
                            if recommendation.complexity_score > 100
                            else (
                                "medium"
                                if recommendation.complexity_score > 50
                                else "low"
                            )
                        ),
                    }
                )
        except Exception:
            data.append({"file": str(file_path), "error": "Could not analyze file"})

    click.echo(json.dumps(data, indent=2))


def _display_files_detailed(
    files: list[Path], engine: RefactoringRecommendationEngine
) -> None:
    """Display files in detailed format."""
    for i, file_path in enumerate(files, 1):
        click.echo(f"\n{i}. {file_path}")
        click.echo("-" * (len(str(file_path)) + 4))

        try:
            recommendation = engine.analyze_file(file_path)
            if recommendation:
                click.echo(f"   Physical lines: {recommendation.physical_lines}")
                click.echo(f"   Complexity: {recommendation.complexity_score:.1f}")
                click.echo(
                    f"   Maintainability: {recommendation.maintainability_index:.1f}"
                )
                click.echo(
                    f"   Violations: {len(recommendation.single_responsibility_violations)}"
                )

                if recommendation.single_responsibility_violations:
                    click.echo("   Issues:")
                    for violation in recommendation.single_responsibility_violations:
                        click.echo(f"     - {violation}")

                if recommendation.suggested_splits:
                    click.echo("   Suggested splits:")
                    for split in recommendation.suggested_splits:
                        click.echo(f"     - {split.target_module_name}: {split.reason}")
            else:
                click.echo("   Could not analyze file")
        except Exception as e:
            click.echo(f"   Error: {e!s}")


def _display_analysis_summary(recommendation) -> None:
    """Display analysis in summary format."""
    click.echo("\n📊 ANALYSIS SUMMARY")
    click.echo(f"{'=' * 50}")
    click.echo(f"File: {recommendation.file_path}")
    click.echo(f"Physical lines: {recommendation.physical_lines}")
    click.echo(f"Complexity: {recommendation.complexity_score:.1f}")
    click.echo(f"Maintainability: {recommendation.maintainability_index:.1f}")
    click.echo(f"Violations: {len(recommendation.single_responsibility_violations)}")
    click.echo(f"Suggested splits: {len(recommendation.suggested_splits)}")

    # Risk assessment
    if recommendation.complexity_score > 100 or recommendation.physical_lines > 2000:
        risk = click.style("HIGH", fg="red")
    elif recommendation.complexity_score > 50 or recommendation.physical_lines > 1500:
        risk = click.style("MEDIUM", fg="yellow")
    else:
        risk = click.style("LOW", fg="green")

    click.echo(f"Risk level: {risk}")


def _display_analysis_detailed(recommendation) -> None:
    """Display analysis in detailed format."""
    _display_analysis_summary(recommendation)

    if recommendation.single_responsibility_violations:
        click.echo("\n🚨 SINGLE RESPONSIBILITY VIOLATIONS:")
        for i, violation in enumerate(
            recommendation.single_responsibility_violations, 1
        ):
            click.echo(f"  {i}. {violation}")

    if recommendation.suggested_splits:
        click.echo("\n✂️  SUGGESTED SPLITS:")
        for i, split in enumerate(recommendation.suggested_splits, 1):
            click.echo(f"  {i}. {split.target_module_name}")
            click.echo(f"     Reason: {split.reason}")
            click.echo(
                f"     Classes: {', '.join(split.classes_to_move) if split.classes_to_move else 'None'}"
            )
            click.echo(
                f"     Functions: {', '.join(split.functions_to_move) if split.functions_to_move else 'None'}"
            )
            click.echo(f"     Estimated lines: {split.estimated_lines}")
            click.echo(f"     Confidence: {split.confidence_score:.1f}")

    if recommendation.impact_analysis:
        click.echo("\n📈 IMPACT ANALYSIS:")
        impact = recommendation.impact_analysis
        click.echo(f"  Dependent files: {len(impact.get('dependent_files', []))}")
        click.echo(f"  Import complexity: {impact.get('import_complexity', 0)}")
        click.echo(f"  Risk level: {impact.get('risk_level', 'unknown')}")


def _display_analysis_json(recommendation) -> None:
    """Display analysis in JSON format."""
    import json
    from dataclasses import asdict

    # Convert dataclass to dict
    data = asdict(recommendation)
    click.echo(json.dumps(data, indent=2, default=str))


@refactor_commands.command()
@click.option(
    "--file-path", "-f", required=True, help="File path to track evolution for"
)
@click.option(
    "--days", "-d", default=30, help="Number of days to analyze (default: 30)"
)
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "detailed"]),
    help="Output format",
)
def track_evolution(file_path: str, days: int, output_format: str) -> None:
    """📈 Track code evolution over time for a specific file."""
    try:
        from pathlib import Path

        from src.ignition.git_integration import GitIntegration
        from src.ignition.manager import CodeIntelligenceManager

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            click.echo(f"❌ File not found: {file_path}", err=True)
            return

        # Initialize git integration
        git_integration = GitIntegration(Path.cwd(), graph_client=None)

        # Track file evolution
        evolution = git_integration.track_file_evolution(str(file_path_obj))
        if not evolution:
            click.echo(f"❌ Could not track evolution for {file_path}", err=True)
            return

        if output_format == "json":
            report = git_integration.generate_evolution_report(str(file_path_obj))
            click.echo(json.dumps(report, indent=2, default=str))
        elif output_format == "detailed":
            _display_detailed_evolution(evolution)
        else:
            _display_evolution_table(evolution)

    except ImportError as e:
        click.echo(f"❌ Git integration not available: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Error tracking evolution: {e}", err=True)


@refactor_commands.command()
@click.option("--source-branch", "-s", required=True, help="Source branch to analyze")
@click.option(
    "--target-branch", "-t", default="main", help="Target branch (default: main)"
)
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format",
)
def analyze_branch(source_branch: str, target_branch: str, output_format: str) -> None:
    """🔀 Analyze differences between branches for refactoring impact."""
    try:
        from pathlib import Path

        from src.ignition.git_integration import GitIntegration

        git_integration = GitIntegration(Path.cwd(), graph_client=None)

        analysis = git_integration.analyze_branch_differences(
            source_branch, target_branch
        )
        if not analysis:
            click.echo("❌ Could not analyze branch differences", err=True)
            return

        if output_format == "json":
            click.echo(json.dumps(asdict(analysis), indent=2, default=str))
        else:
            _display_branch_analysis_table(analysis)

    except ImportError as e:
        click.echo(f"❌ Git integration not available: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Error analyzing branches: {e}", err=True)


@refactor_commands.command()
@click.option("--operation-id", "-o", help="Specific operation ID to report on")
@click.option(
    "--days", "-d", default=30, help="Number of days for period report (default: 30)"
)
@click.option(
    "--format",
    "output_format",
    default="detailed",
    type=click.Choice(["table", "json", "detailed"]),
    help="Output format",
)
def tracking_report(operation_id: str, days: int, output_format: str) -> None:
    """📊 Generate refactoring tracking and impact reports."""
    try:
        from pathlib import Path

        from src.ignition.refactoring_tracker import RefactoringTracker

        tracker = RefactoringTracker(Path.cwd())

        if operation_id:
            report = tracker.build_refactoring_impact_report(operation_id)
        else:
            report = tracker.build_refactoring_impact_report(days=days)

        if output_format == "json":
            click.echo(json.dumps(report, indent=2, default=str))
        elif output_format == "detailed":
            _display_detailed_tracking_report(report)
        else:
            _display_tracking_report_table(report)

    except ImportError as e:
        click.echo(f"❌ Refactoring tracking not available: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Error generating tracking report: {e}", err=True)


@refactor_commands.command()
@click.option(
    "--operation-id", "-o", required=True, help="Operation ID to generate diagram for"
)
@click.option(
    "--output-dir", "-d", default=".", help="Output directory for diagram files"
)
def generate_diagram(operation_id: str, output_dir: str) -> None:
    """🎨 Generate architecture diagram for a refactoring operation."""
    try:
        from pathlib import Path

        from src.ignition.refactoring_tracker import RefactoringTracker

        tracker = RefactoringTracker(Path.cwd())

        # Check if operation exists
        if operation_id not in tracker.operations:
            click.echo(f"❌ Operation {operation_id} not found", err=True)
            return

        # Load operation data
        operation_data = tracker.operations[operation_id]
        from src.ignition.refactoring_tracker import RefactoringOperation

        operation = RefactoringOperation(**operation_data)

        # Generate diagram
        diagram = tracker.generate_architecture_diagram(operation)
        if not diagram:
            click.echo(
                f"❌ Could not generate diagram for operation {operation_id}", err=True
            )
            return

        # Save to output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        mermaid_file = output_path / f"{diagram.diagram_id}.mmd"
        with open(mermaid_file, "w") as f:
            f.write(diagram.mermaid_code)

        click.echo(f"✅ Architecture diagram generated: {mermaid_file}")
        click.echo(f"📝 Diagram type: {diagram.diagram_type}")
        click.echo(f"📁 Source file: {diagram.source_file}")
        click.echo(f"📂 Target files: {', '.join(diagram.target_files)}")

    except ImportError as e:
        click.echo(f"❌ Refactoring tracking not available: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Error generating diagram: {e}", err=True)


@refactor_commands.command()
@click.option(
    "--days", "-d", default=30, help="Number of days to analyze (default: 30)"
)
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format",
)
def complexity_trends(days: int, output_format: str) -> None:
    """📈 Show complexity trends across the codebase."""
    try:
        from pathlib import Path

        from src.ignition.git_integration import GitIntegration
        from src.ignition.manager import CodeIntelligenceManager

        # Initialize components
        git_integration = GitIntegration(Path.cwd(), graph_client=None)

        # Try to get graph client for enhanced analysis
        try:
            manager = CodeIntelligenceManager()
            if manager.client.is_connected():
                git_integration.graph_client = manager.client
        except Exception:
            pass

        trends = git_integration.get_complexity_trends(days)

        if output_format == "json":
            click.echo(json.dumps(trends, indent=2, default=str))
        else:
            _display_complexity_trends_table(trends)

    except ImportError as e:
        click.echo(f"❌ Git integration not available: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Error analyzing complexity trends: {e}", err=True)


@refactor_commands.command()
def statistics() -> None:
    """📊 Show comprehensive refactoring statistics."""
    try:
        from pathlib import Path

        from src.ignition.refactoring_tracker import RefactoringTracker

        tracker = RefactoringTracker(Path.cwd())
        stats = tracker.get_refactoring_statistics()

        click.echo("\n📊 REFACTORING STATISTICS")
        click.echo("=" * 50)

        # Operations statistics
        ops = stats["operations"]
        click.echo(f"Total Operations: {ops['total']}")
        click.echo(f"Successful: {ops['successful']} ({ops['success_rate']:.1f}%)")
        click.echo(f"Total Lines Moved: {ops['total_lines_moved']:,}")

        # Improvements
        improvements = stats["improvements"]
        click.echo(
            f"\nAverage Complexity Reduction: {improvements['average_complexity_reduction']:.1f}"
        )
        click.echo(
            f"Average Maintainability Improvement: {improvements['average_maintainability_improvement']:.1f}"
        )

        # TODOs
        todos = stats["todos"]
        click.echo(f"\nTODOs Created: {todos['total']}")
        click.echo(
            f"TODOs Resolved: {todos['resolved']} ({todos['resolution_rate']:.1f}%)"
        )

        # Diagrams
        click.echo(f"Architecture Diagrams Generated: {stats['diagrams_generated']}")

    except ImportError as e:
        click.echo(f"❌ Refactoring tracking not available: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Error getting statistics: {e}", err=True)


def _display_evolution_table(evolution) -> None:
    """Display evolution data in table format."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    # File info
    console.print("\n📈 [bold blue]Code Evolution Analysis[/bold blue]")
    console.print(f"File: {evolution.file_path}")
    console.print(f"Growth Rate: {evolution.growth_rate:.2f} lines/day")
    console.print(f"Complexity Trend: {evolution.complexity_trend}")

    # Recent commits table
    if evolution.commits:
        table = Table(title="Recent Commits")
        table.add_column("Hash", style="cyan")
        table.add_column("Author", style="green")
        table.add_column("Date", style="yellow")
        table.add_column("Changes", style="red")
        table.add_column("Message", style="white")

        for commit in evolution.commits[:5]:
            changes = f"+{commit.lines_added}/-{commit.lines_deleted}"
            message = (
                commit.message[:50] + "..."
                if len(commit.message) > 50
                else commit.message
            )
            table.add_row(
                commit.short_hash,
                commit.author,
                commit.date.strftime("%Y-%m-%d"),
                changes,
                message,
            )

        console.print(table)


def _display_detailed_evolution(evolution) -> None:
    """Display detailed evolution analysis."""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    # Generate full report
    from src.ignition.git_integration import GitIntegration

    git_integration = GitIntegration(Path.cwd(), graph_client=None)
    report = git_integration.generate_evolution_report(evolution.file_path)

    # Display detailed information
    console.print(
        Panel.fit(
            f"[bold blue]Code Evolution Report[/bold blue]\n{evolution.file_path}"
        )
    )

    # Size evolution
    if report.get("size_evolution"):
        size_info = report["size_evolution"]
        console.print("\n📏 [bold]Size Evolution[/bold]")
        console.print(f"Growth Rate: {size_info['growth_rate']:.2f} lines/day")

        if size_info["size_history"]:
            console.print("Recent Size History:")
            for entry in size_info["size_history"][:5]:
                date = entry["date"][:10]  # Just the date part
                console.print(f"  {date}: {entry['lines']} lines")

    # Complexity evolution
    if report.get("complexity_evolution"):
        complexity_info = report["complexity_evolution"]
        console.print("\n🧮 [bold]Complexity Evolution[/bold]")
        console.print(f"Trend: {complexity_info['trend']}")

    # Recommendations
    if report.get("recommendations"):
        console.print("\n💡 [bold]Recommendations[/bold]")
        for rec in report["recommendations"]:
            console.print(f"  • {rec}")


def _display_branch_analysis_table(analysis) -> None:
    """Display branch analysis in table format."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    console.print("\n🔀 [bold blue]Branch Analysis[/bold blue]")
    console.print(f"Source: {analysis.branch_name} → Target: {analysis.base_branch}")
    console.print(f"Commits Ahead: {analysis.commits_ahead}")
    console.print(f"Commits Behind: {analysis.commits_behind}")
    console.print(f"Risk Assessment: {analysis.risk_assessment}")

    if analysis.files_modified:
        table = Table(title="Modified Files")
        table.add_column("File Path", style="cyan")

        for file_path in analysis.files_modified[:10]:  # Show first 10
            table.add_row(file_path)

        if len(analysis.files_modified) > 10:
            table.add_row(f"... and {len(analysis.files_modified) - 10} more files")

        console.print(table)

    if analysis.merge_conflicts_predicted:
        console.print("\n⚠️  [bold red]Potential Merge Conflicts:[/bold red]")
        for conflict_file in analysis.merge_conflicts_predicted:
            console.print(f"  • {conflict_file}")


def _display_tracking_report_table(report) -> None:
    """Display tracking report in table format."""
    from rich.console import Console

    console = Console()

    if "operation_id" in report:
        # Single operation report
        console.print("\n📊 [bold blue]Operation Report[/bold blue]")
        console.print(f"Operation ID: {report['operation_id']}")
        console.print(f"Type: {report['operation_type']}")
        console.print(f"Success: {'✅' if report['success'] else '❌'}")

        if "impact_analysis" in report:
            impact = report["impact_analysis"]
            console.print(f"Files Affected: {impact['files_affected']}")
            console.print(f"Lines Moved: {impact['lines_moved']}")
            console.print(
                f"Complexity Improvement: {impact['complexity_improvement']:.1f}"
            )
            console.print(f"Impact Score: {impact['impact_score']:.2f}")
    else:
        # Period report
        console.print("\n📊 [bold blue]Refactoring Summary[/bold blue]")
        if "summary" in report:
            summary = report["summary"]
            console.print(f"Total Operations: {summary['total_operations']}")
            console.print(f"Success Rate: {summary['success_rate']:.1f}%")
            console.print(f"Total Lines Moved: {summary['total_lines_moved']:,}")
            console.print(
                f"Average Impact Score: {summary['average_impact_score']:.2f}"
            )


def _display_detailed_tracking_report(report) -> None:
    """Display detailed tracking report."""
    from rich.console import Console
    from rich.json import JSON
    from rich.panel import Panel

    console = Console()

    # Display as formatted JSON for detailed view
    console.print(Panel.fit("[bold blue]Detailed Tracking Report[/bold blue]"))
    console.print(JSON.from_data(report))


def _display_complexity_trends_table(trends) -> None:
    """Display complexity trends in table format."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    console.print("\n📈 [bold blue]Complexity Trends Analysis[/bold blue]")
    console.print(f"Files Analyzed: {trends.get('files_analyzed', 0)}")

    # High growth files
    high_growth = trends.get("high_growth_files", [])
    if high_growth:
        table = Table(title="High Growth Files (>5 lines/day)")
        table.add_column("File", style="cyan")
        table.add_column("Growth Rate", style="red")
        table.add_column("Trend", style="yellow")

        for file_info in high_growth[:10]:
            table.add_row(
                file_info["file_path"],
                f"{file_info['growth_rate']:.1f} lines/day",
                file_info["complexity_trend"],
            )

        console.print(table)

    # Summary stats
    increasing = len(trends.get("increasing_complexity", []))
    stable = len(trends.get("stable_files", []))
    improving = len(trends.get("improving_files", []))

    console.print("\n📊 [bold]Complexity Trend Summary[/bold]")
    console.print(f"Increasing Complexity: {increasing} files")
    console.print(f"Stable: {stable} files")
    console.print(f"Improving: {improving} files")


# Export the command group
__all__ = ["refactor_commands"]
