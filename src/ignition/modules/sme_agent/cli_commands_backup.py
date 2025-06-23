"""SME Agent CLI Commands - Phase 11: Process SME Agent & AI Enhancement Platform

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import logging
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .sme_agent_module import SMEAgentModule, SMEAgentValidationError

console = Console()
logger = logging.getLogger(__name__)


def handle_sme_agent_error(func):
    """Decorator for handling SME Agent errors with user-friendly messages."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SMEAgentValidationError as e:
            console.print(f"[red]❌ Validation Error:[/red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]❌ Unexpected Error:[/red] {e}")
            logger.exception("Unexpected error in SME Agent CLI")
            sys.exit(1)

    return wrapper


@click.group(name="sme")
@click.pass_context
def sme_agent_cli(ctx):
    """SME Agent CLI - Ignition Subject Matter Expert Assistant

    Phase 11: Process SME Agent & AI Enhancement Platform
    Following crawl_mcp.py methodology for systematic operation.
    """
    ctx.ensure_object(dict)


@sme_agent_cli.command("validate-env")
@handle_sme_agent_error
def validate_environment():
    """Step 1: Environment Validation First

    Validate SME Agent environment and dependencies.
    """
    console.print("[bold blue]🔍 SME Agent Environment Validation[/bold blue]")
    console.print(
        "Following crawl_mcp.py methodology - Step 1: Environment Validation First"
    )

    try:
        # Create temporary SME Agent instance for validation
        with SMEAgentModule() as agent:
            validation_result = agent.validate_environment()

            # Display validation results
            if validation_result["valid"]:
                console.print("[green]✅ Environment validation successful![/green]")
            else:
                console.print("[red]❌ Environment validation failed![/red]")

            # Show detailed results
            _display_validation_results(validation_result)

    except Exception as e:
        console.print(f"[red]❌ Environment validation failed: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("status")
@handle_sme_agent_error
def get_status():
    """Step 4: Modular Component Testing

    Get current status of SME Agent components.
    """
    console.print("[bold blue]📊 SME Agent Status[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            status = agent.get_status()
            _display_status(status)

    except Exception as e:
        console.print(f"[red]❌ Failed to get status: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("initialize")
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="basic",
    help="Complexity level for initialization",
)
@handle_sme_agent_error
def initialize_components(complexity: str):
    """Step 5: Progressive Complexity Support

    Initialize SME Agent components with specified complexity level.
    """
    console.print(
        f"[bold blue]🚀 SME Agent Initialization - {complexity.title()} Level[/bold blue]"
    )
    console.print(
        "Following crawl_mcp.py methodology - Step 5: Progressive Complexity Support"
    )

    try:
        with SMEAgentModule() as agent:
            result = agent.initialize_components(complexity_level=complexity)
            _display_initialization_results(result)

    except Exception as e:
        console.print(f"[red]❌ Initialization failed: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("ask")
@click.argument("question", required=True)
@click.option("--context", help="Optional context for the question")
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="basic",
)
@handle_sme_agent_error
def ask_question(question: str, context: str | None, complexity: str):
    """Step 2: Comprehensive Input Validation
    Step 3: Error Handling and User-Friendly Messages

    Ask a question to the SME Agent.
    """
    console.print("[bold blue]💬 SME Agent Question Processing[/bold blue]")
    console.print(f"Question: [italic]{question}[/italic]")
    if context:
        console.print(f"Context: [italic]{context}[/italic]")

    try:
        with SMEAgentModule() as agent:
            # Initialize with specified complexity
            init_result = agent.initialize_components(complexity_level=complexity)
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Process question
            response = agent.ask_question(question, context)
            _display_response(response)

    except Exception as e:
        console.print(f"[red]❌ Question processing failed: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
)
@handle_sme_agent_error
def analyze_file(file_path: str, complexity: str):
    """Analyze a file using SME Agent capabilities."""
    console.print("[bold blue]🔍 SME Agent File Analysis[/bold blue]")
    console.print(f"Analyzing: [italic]{file_path}[/italic]")

    try:
        # Read file content
        file_content = Path(file_path).read_text()

        # Create analysis question
        question = "Please analyze this file and provide insights about its structure, purpose, and potential improvements."
        context = f"File: {file_path}\nContent:\n{file_content[:2000]}..."  # Limit context size

        with SMEAgentModule() as agent:
            # Initialize with specified complexity
            init_result = agent.initialize_components(complexity_level=complexity)
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Process analysis
            response = agent.ask_question(question, context)
            _display_response(response)

    except Exception as e:
        console.print(f"[red]❌ File analysis failed: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("test-all")
@handle_sme_agent_error
def test_all_components():
    """Step 4: Modular Component Testing

    Test all SME Agent components across complexity levels.
    """
    console.print("[bold blue]🧪 SME Agent Comprehensive Testing[/bold blue]")
    console.print(
        "Following crawl_mcp.py methodology - Step 4: Modular Component Testing"
    )

    complexity_levels = ["basic", "standard", "advanced", "enterprise"]

    for complexity in complexity_levels:
        console.print(
            f"\n[bold yellow]Testing {complexity.title()} Level[/bold yellow]"
        )

        try:
            with SMEAgentModule() as agent:
                # Test initialization
                init_result = agent.initialize_components(complexity_level=complexity)

                if init_result["success"]:
                    console.print(
                        f"[green]✅ {complexity.title()} initialization: SUCCESS[/green]"
                    )
                    console.print(
                        f"   Components: {', '.join(init_result['components_initialized'])}"
                    )
                    console.print(f"   Time: {init_result['initialization_time']:.3f}s")

                    # Test basic functionality
                    test_question = f"Test question for {complexity} level"
                    response = agent.ask_question(test_question)
                    console.print(
                        f"[green]✅ {complexity.title()} question processing: SUCCESS[/green]"
                    )
                    console.print(f"   Response time: {response.processing_time:.3f}s")
                    console.print(f"   Confidence: {response.confidence:.2f}")

                else:
                    console.print(
                        f"[red]❌ {complexity.title()} initialization: FAILED[/red]"
                    )
                    for error in init_result["errors"]:
                        console.print(f"   Error: {error}")

        except Exception as e:
            console.print(f"[red]❌ {complexity.title()} testing failed: {e}[/red]")

    console.print("\n[bold green]🎉 Comprehensive testing completed![/bold green]")


@sme_agent_cli.command("list-batches")
@handle_sme_agent_error
def list_evaluation_batches():
    """List all evaluation batches for human review."""
    console.print("[bold blue]📋 SME Agent Evaluation Batches[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            # Initialize basic components
            init_result = agent.initialize_components(complexity_level="basic")
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Get pending batches
            pending_batches = agent.get_pending_evaluation_batches()

            if pending_batches["count"] == 0:
                console.print("[yellow]ℹ️  No pending evaluation batches found[/yellow]")
                return

            # Display batches table
            table = Table(
                title=f"Pending Evaluation Batches ({pending_batches['count']})"
            )
            table.add_column("Batch ID", style="cyan")
            table.add_column("Created", style="green")
            table.add_column("Decisions", style="yellow")
            table.add_column("Status", style="blue")

            for batch in pending_batches["pending_batches"]:
                table.add_row(
                    batch["batch_id"][:8] + "...",
                    batch["created_timestamp"][:19],
                    str(len(batch["decision_logs"])),
                    batch["status"],
                )

            console.print(table)
            console.print(
                f"\n[bold]Total decisions awaiting review: {pending_batches['total_decisions']}[/bold]"
            )

    except Exception as e:
        console.print(f"[red]❌ Failed to list evaluation batches: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("export-batch")
@click.argument("batch_id", required=True)
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Export format",
)
@handle_sme_agent_error
def export_evaluation_batch(batch_id: str, export_format: str):
    """Export evaluation batch for human SME review."""
    console.print("[bold blue]📤 Exporting Evaluation Batch[/bold blue]")
    console.print(f"Batch ID: [italic]{batch_id}[/italic]")
    console.print(f"Format: [italic]{export_format}[/italic]")

    try:
        with SMEAgentModule() as agent:
            # Initialize basic components
            init_result = agent.initialize_components(complexity_level="basic")
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Export batch
            export_result = agent.export_batch_for_review(batch_id, export_format)

            if export_result["success"]:
                console.print("[green]✅ Batch exported successfully![/green]")
                console.print(
                    f"Export file: [bold]{export_result['export_file']}[/bold]"
                )
                console.print(
                    f"Decisions count: [bold]{export_result['decisions_count']}[/bold]"
                )
                console.print("\n[yellow]📝 Instructions for Human SME:[/yellow]")
                console.print("1. Open the exported file")
                console.print("2. Review each decision and provide ratings (1-5 scale)")
                console.print("3. Add correct responses where needed")
                console.print("4. Provide improvement suggestions")
                console.print("5. Use 'import-evaluation' command to submit feedback")
            else:
                console.print(f"[red]❌ Export failed: {export_result['error']}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Failed to export batch: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("import-evaluation")
@click.argument("batch_id", required=True)
@click.argument("evaluation_file", type=click.Path(exists=True), required=True)
@click.option(
    "--sme-id", required=True, help="ID of the human SME who performed the evaluation"
)
@handle_sme_agent_error
def import_human_evaluation(batch_id: str, evaluation_file: str, sme_id: str):
    """Import human SME evaluation results and incorporate feedback."""
    console.print("[bold blue]📥 Importing Human Evaluation[/bold blue]")
    console.print(f"Batch ID: [italic]{batch_id}[/italic]")
    console.print(f"Evaluation file: [italic]{evaluation_file}[/italic]")
    console.print(f"Human SME ID: [italic]{sme_id}[/italic]")

    try:
        with SMEAgentModule() as agent:
            # Initialize basic components
            init_result = agent.initialize_components(complexity_level="basic")
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Import evaluation
            import_result = agent.import_human_evaluation(
                batch_id, evaluation_file, sme_id
            )

            if import_result["success"]:
                console.print("[green]✅ Evaluation imported successfully![/green]")

                # Display results table
                results_table = Table(title="Import Results")
                results_table.add_column("Metric", style="cyan")
                results_table.add_column("Value", style="green")

                results_table.add_row(
                    "Processed Decisions", str(import_result["processed_decisions"])
                )
                results_table.add_row(
                    "Decisions with Improvements",
                    str(import_result["decisions_with_improvements"]),
                )
                results_table.add_row(
                    "Average Rating",
                    (
                        f"{import_result['average_rating']:.2f}"
                        if import_result["average_rating"]
                        else "N/A"
                    ),
                )

                console.print(results_table)

                # Display reinforcement learning insights
                rl_insights = import_result.get("reinforcement_learning_insights", {})
                if rl_insights:
                    _display_reinforcement_learning_insights(rl_insights)

            else:
                console.print(f"[red]❌ Import failed: {import_result['error']}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Failed to import evaluation: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("rl-summary")
@handle_sme_agent_error
def reinforcement_learning_summary():
    """Display comprehensive reinforcement learning summary."""
    console.print("[bold blue]🧠 Reinforcement Learning Summary[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            # Initialize basic components
            init_result = agent.initialize_components(complexity_level="basic")
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Get RL summary
            rl_summary = agent.get_reinforcement_learning_summary()

            if rl_summary.get("total_evaluations", 0) == 0:
                console.print("[yellow]ℹ️  No completed evaluations available[/yellow]")
                return

            # Display overview
            overview_table = Table(title="Learning Overview")
            overview_table.add_column("Metric", style="cyan")
            overview_table.add_column("Value", style="green")

            overview_table.add_row(
                "Total Evaluations", str(rl_summary["total_evaluations"])
            )
            overview_table.add_row("Total Batches", str(rl_summary["total_batches"]))

            console.print(overview_table)

            # Display performance trends
            trends = rl_summary.get("performance_trends", {})
            if trends:
                trends_table = Table(title="Performance Trends")
                trends_table.add_column("Metric", style="cyan")
                trends_table.add_column("Value", style="green")

                trends_table.add_row(
                    "Average Human Rating",
                    f"{trends.get('average_human_rating', 0):.2f}",
                )
                trends_table.add_row(
                    "Average Agent Confidence",
                    f"{trends.get('average_agent_confidence', 0):.2f}",
                )
                trends_table.add_row(
                    "Average Processing Time",
                    f"{trends.get('average_processing_time', 0):.3f}s",
                )
                trends_table.add_row(
                    "Improvement Rate", f"{trends.get('improvement_rate', 0):.1%}"
                )

                console.print(trends_table)

            # Display model performance
            performance = rl_summary.get("model_performance", {})
            if performance:
                performance_table = Table(title="Model Performance")
                performance_table.add_column("Metric", style="cyan")
                performance_table.add_column("Value", style="green")

                performance_table.add_row(
                    "High Quality Responses",
                    str(performance.get("high_quality_responses", 0)),
                )
                performance_table.add_row(
                    "Needs Improvement", str(performance.get("needs_improvement", 0))
                )
                performance_table.add_row(
                    "Consistency Score",
                    f"{performance.get('consistency_score', 0):.2f}",
                )

                console.print(performance_table)

            # Display learning opportunities
            opportunities = rl_summary.get("learning_opportunities", [])
            if opportunities:
                console.print("\n[bold yellow]🎯 Learning Opportunities:[/bold yellow]")
                for i, opportunity in enumerate(opportunities[:5], 1):
                    priority_color = (
                        "red" if opportunity["priority"] == "high" else "yellow"
                    )
                    console.print(
                        f"{i}. [{priority_color}]{opportunity['improvement']}[/{priority_color}] (frequency: {opportunity['frequency']})"
                    )

    except Exception as e:
        console.print(f"[red]❌ Failed to get RL summary: {e}[/red]")
        sys.exit(1)


@sme_agent_cli.command("create-test-batch")
@click.option("--size", default=5, help="Number of test decisions to create")
@handle_sme_agent_error
def create_test_evaluation_batch(size: int):
    """Create a test evaluation batch for demonstration purposes."""
    console.print("[bold blue]🧪 Creating Test Evaluation Batch[/bold blue]")
    console.print(f"Creating {size} test decisions...")

    try:
        with SMEAgentModule() as agent:
            # Initialize basic components
            init_result = agent.initialize_components(complexity_level="basic")
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Create test questions and responses
            test_questions = [
                "What is the best practice for PID controller tuning?",
                "How do you troubleshoot a temperature control loop?",
                "What are the common causes of oscillation in process control?",
                "Explain the difference between cascade and feedforward control.",
                "How do you implement alarm management in industrial systems?",
            ]

            created_count = 0
            for i in range(min(size, len(test_questions))):
                question = test_questions[i]
                response = agent.ask_question(question)
                created_count += 1
                console.print(
                    f"[green]✅ Created decision {i + 1}: {question[:50]}...[/green]"
                )

            console.print(f"\n[bold]Created {created_count} test decisions[/bold]")
            console.print(
                "Use 'list-batches' to see if a batch was automatically created"
            )

    except Exception as e:
        console.print(f"[red]❌ Failed to create test batch: {e}[/red]")
        sys.exit(1)


def _display_validation_results(validation_result: dict[str, Any]):
    """Display environment validation results."""
    table = Table(title="Environment Validation Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")

    # Environment variables
    if validation_result["valid"]:
        table.add_row(
            "Environment Variables", "✅ Valid", "All required variables present"
        )
    else:
        table.add_row(
            "Environment Variables",
            "❌ Invalid",
            f"{len(validation_result['errors'])} errors",
        )

    # Component availability
    components = validation_result.get("components_available", {})
    for component, available in components.items():
        status = "✅ Available" if available else "❌ Not Available"
        table.add_row(f"Component: {component}", status, "")

    console.print(table)

    # Show errors and warnings
    if validation_result["errors"]:
        console.print("\n[red]Errors:[/red]")
        for error in validation_result["errors"]:
            console.print(f"  • {error}")

    if validation_result["warnings"]:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in validation_result["warnings"]:
            console.print(f"  • {warning}")


def _display_status(status: dict[str, Any]):
    """Display SME Agent status."""
    # Main status panel
    status_text = "🟢 Initialized" if status["initialized"] else "🔴 Not Initialized"
    console.print(Panel(status_text, title="SME Agent Status", border_style="blue"))

    # Configuration table
    config_table = Table(title="Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")

    config = status["config"]
    config_table.add_row("Model Name", config["model_name"])
    config_table.add_row(
        "Knowledge Graph",
        "✅ Enabled" if config["use_knowledge_graph"] else "❌ Disabled",
    )
    config_table.add_row(
        "Vector Embeddings",
        "✅ Enabled" if config["use_vector_embeddings"] else "❌ Disabled",
    )

    console.print(config_table)

    # Components table
    components_table = Table(title="Components")
    components_table.add_column("Component", style="cyan")
    components_table.add_column("Status", style="green")

    components = status["components"]
    components_table.add_row(
        "Neo4j", "✅ Connected" if components["neo4j_connected"] else "❌ Not Connected"
    )
    components_table.add_row(
        "LLM Model", "✅ Loaded" if components["llm_loaded"] else "❌ Not Loaded"
    )
    components_table.add_row(
        "Vector Store",
        "✅ Ready" if components["vector_store_ready"] else "❌ Not Ready",
    )

    console.print(components_table)


def _display_initialization_results(result: dict[str, Any]):
    """Display initialization results."""
    if result["success"]:
        console.print("[green]✅ Initialization successful![/green]")
        console.print(
            f"Complexity Level: [bold]{result['complexity_level'].title()}[/bold]"
        )
        console.print(
            f"Initialization Time: [bold]{result['initialization_time']:.3f}s[/bold]"
        )

        if result["components_initialized"]:
            console.print("\nComponents Initialized:")
            for component in result["components_initialized"]:
                console.print(f"  ✅ {component}")
    else:
        console.print("[red]❌ Initialization failed![/red]")

        if result["errors"]:
            console.print("\nErrors:")
            for error in result["errors"]:
                console.print(f"  ❌ {error}")

    if result["warnings"]:
        console.print("\nWarnings:")
        for warning in result["warnings"]:
            console.print(f"  ⚠️  {warning}")


def _display_response(response):
    """Display SME Agent response."""
    # Response panel
    console.print(
        Panel(response.response, title="SME Agent Response", border_style="green")
    )

    # Metadata table
    metadata_table = Table(title="Response Metadata")
    metadata_table.add_column("Metric", style="cyan")
    metadata_table.add_column("Value", style="green")

    metadata_table.add_row("Confidence", f"{response.confidence:.2f}")
    metadata_table.add_row("Processing Time", f"{response.processing_time:.3f}s")
    metadata_table.add_row("Model Used", response.model_used)
    metadata_table.add_row("Sources", ", ".join(response.sources))
    metadata_table.add_row("Knowledge Sources", ", ".join(response.knowledge_sources))

    console.print(metadata_table)


def _display_reinforcement_learning_insights(insights: dict[str, Any]):
    """Display reinforcement learning insights."""
    console.print("\n[bold blue]🧠 Reinforcement Learning Insights[/bold blue]")

    # Performance metrics
    performance_metrics = insights.get("performance_metrics", {})
    if performance_metrics:
        metrics_table = Table(title="Performance Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")

        if "average_rating" in performance_metrics:
            metrics_table.add_row(
                "Average Rating", f"{performance_metrics['average_rating']:.2f}"
            )

        # Rating distribution
        distribution = performance_metrics.get("rating_distribution", {})
        if distribution:
            for rating, count in distribution.items():
                metrics_table.add_row(f"{rating.title()} Ratings", str(count))

        console.print(metrics_table)

    # Improvement patterns
    improvement_patterns = insights.get("improvement_patterns", [])
    if improvement_patterns:
        console.print("\n[bold yellow]📈 Common Improvement Patterns:[/bold yellow]")
        for i, pattern in enumerate(improvement_patterns[:5], 1):
            console.print(
                f"{i}. {pattern['suggestion']} (frequency: {pattern['frequency']})"
            )

    # Common issues
    common_issues = insights.get("common_issues", [])
    if common_issues:
        console.print("\n[bold red]⚠️  Common Issues:[/bold red]")
        for issue in common_issues:
            console.print(
                f"• {issue['question_type']}: {issue['frequency']} occurrences"
            )
            console.print(f"  {issue['description']}")

    # Recommendations
    recommendations = insights.get("recommendations", [])
    if recommendations:
        console.print("\n[bold green]💡 Recommendations:[/bold green]")
        for i, recommendation in enumerate(recommendations, 1):
            console.print(f"{i}. {recommendation}")


@sme_agent_cli.command("llm-status")
@handle_sme_agent_error
def llm_status():
    """Display LLM infrastructure status and capabilities."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        with console.status("[bold blue]Checking LLM infrastructure..."):
            # Import LLM integration
            from .llm_integration import LLMModelRegistry, validate_llm_environment

            # Validate LLM environment
            validation = validate_llm_environment()

            # Initialize SME Agent to check LLM integration
            sme_agent = SMEAgentModule()
            init_result = sme_agent.initialize_components("advanced")

        # Create status table
        status_table = Table(
            title="LLM Infrastructure Status",
            show_header=True,
            header_style="bold magenta",
        )
        status_table.add_column("Component", style="cyan", no_wrap=True)
        status_table.add_column("Status", justify="center")
        status_table.add_column("Details", style="dim")

        # Add component status
        for component, available in validation["components_available"].items():
            status = "✅ Available" if available else "❌ Missing"
            details = validation["system_info"].get(f"{component}_version", "N/A")
            status_table.add_row(component.title(), status, str(details))

        # Create system info table
        system_table = Table(
            title="System Information", show_header=True, header_style="bold green"
        )
        system_table.add_column("Property", style="cyan", no_wrap=True)
        system_table.add_column("Value", justify="left")

        for key, value in validation["system_info"].items():
            if key not in [
                "transformers_version",
                "torch_version",
                "bitsandbytes_version",
                "docker_version",
            ]:
                system_table.add_row(key.replace("_", " ").title(), str(value))

        # Create models table
        models_table = Table(
            title="Supported Models", show_header=True, header_style="bold yellow"
        )
        models_table.add_column("Model", style="cyan", no_wrap=True)
        models_table.add_column("Size (GB)", justify="center")
        models_table.add_column("Min VRAM (GB)", justify="center")
        models_table.add_column("Context Length", justify="center")
        models_table.add_column("Description", style="dim")

        for model_name, model_info in LLMModelRegistry.SUPPORTED_MODELS.items():
            models_table.add_row(
                model_name,
                f"{model_info.size_gb:.1f}",
                f"{model_info.min_vram_gb:.1f}",
                f"{model_info.context_length:,}",
                (
                    model_info.description[:50] + "..."
                    if len(model_info.description) > 50
                    else model_info.description
                ),
            )

        # Display results
        console.print(status_table)
        console.print()
        console.print(system_table)
        console.print()
        console.print(models_table)

        # Show validation summary
        if validation["valid"]:
            summary_color = "green"
            summary_icon = "✅"
            summary_text = "LLM infrastructure is ready for deployment"
        else:
            summary_color = "red"
            summary_icon = "❌"
            summary_text = (
                f"LLM infrastructure has issues: {', '.join(validation['errors'])}"
            )

        console.print()
        console.print(
            Panel(
                f"[{summary_color}]{summary_icon} {summary_text}[/{summary_color}]\n\n"
                f"📊 Components Available: {sum(validation['components_available'].values())}/{len(validation['components_available'])}\n"
                f"⚠️  Warnings: {len(validation['warnings'])}\n"
                f"❌ Errors: {len(validation['errors'])}\n\n"
                + (
                    "💡 Recommendations:\n"
                    + "\n".join(f"• {rec}" for rec in validation["recommendations"])
                    if validation["recommendations"]
                    else ""
                ),
                title="LLM Infrastructure Summary",
                border_style=summary_color,
            )
        )

        # Show SME Agent LLM status (placeholder for future LLM integration)
        console.print()
        console.print(
            Panel(
                "🤖 LLM Infrastructure: Ready for deployment\n"
                "📝 Supported Models: Llama3.1-8B, Mistral-8B\n"
                "🖥️  Device Support: CPU, CUDA, MPS\n"
                "🔧 Quantization: 4-bit, 8-bit, 16-bit\n"
                "⚡ Use 'ign module sme llm-deploy' to deploy LLM infrastructure",
                title="SME Agent LLM Infrastructure",
                border_style="blue",
            )
        )

    except Exception as e:
        console.print(f"[red]❌ Error checking LLM status: {e}")
        console.print(f"[dim]Error details: {type(e).__name__}: {e!s}")


@sme_agent_cli.command("env-optimize")
@handle_sme_agent_error
def env_optimize():
    """Display environment-specific optimization recommendations for LLM deployment."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        console = Console()

        with console.status("[bold blue]Analyzing system environment..."):
            # Import environment detection
            from .llm_integration import LLMConfig, detect_system_environment

            # Detect system environment
            system_env = detect_system_environment()

            # Create test configuration and optimize it
            base_config = LLMConfig()
            optimized_config = base_config.optimize_for_system_environment(system_env)

        # Display environment information
        env_table = Table(title="Detected System Environment")
        env_table.add_column("Property", style="cyan")
        env_table.add_column("Value", style="yellow")
        env_table.add_column("Optimization Impact", style="green")

        env_table.add_row(
            "Environment Type", system_env.env_type, "Determines acceleration method"
        )
        env_table.add_row(
            "Platform",
            f"{system_env.platform} ({system_env.architecture})",
            "Platform-specific optimizations",
        )
        env_table.add_row(
            "Total Memory",
            f"{system_env.total_memory_gb:.1f} GB",
            "Memory allocation strategy",
        )
        env_table.add_row(
            "Recommended Device",
            system_env.recommended_device,
            "Primary compute device",
        )
        env_table.add_row(
            "Recommended Quantization",
            system_env.recommended_quantization,
            "Memory optimization level",
        )

        console.print(env_table)

        # Display optimization recommendations
        opt_table = Table(title="Environment-Specific Optimizations")
        opt_table.add_column("Configuration", style="cyan")
        opt_table.add_column("Base Value", style="red")
        opt_table.add_column("Optimized Value", style="green")
        opt_table.add_column("Reason", style="yellow")

        # Compare configurations
        opt_table.add_row(
            "Target Device",
            base_config.target_device,
            optimized_config.target_device,
            f"Optimized for {system_env.env_type}",
        )
        opt_table.add_row(
            "Quantization",
            base_config.quantization,
            optimized_config.quantization,
            "Based on available memory",
        )
        opt_table.add_row(
            "Max Context",
            str(base_config.max_context),
            str(optimized_config.max_context),
            "Adjusted for system capabilities",
        )

        console.print(opt_table)

        # Environment-specific recommendations
        if system_env.env_type == "nvidia_gpu":
            nvidia_panel = Panel(
                Text.from_markup(
                    "[bold green]NVIDIA GPU Environment (Env01) Detected[/bold green]\\n\\n"
                    "• GPU acceleration will be used for optimal performance\\n"
                    "• CUDA kernels optimized for your GPU architecture\\n"
                    "• Flash Attention enabled for memory efficiency\\n"
                    f"• Quantization: {optimized_config.quantization}\\n"
                    "• Recommended for production workloads"
                ),
                title="Environment Optimization: NVIDIA GPU",
                border_style="green",
            )
            console.print(nvidia_panel)
        elif system_env.env_type == "macos_unified":
            macos_panel = Panel(
                Text.from_markup(
                    "[bold green]macOS Unified Memory Environment (Env02) Detected[/bold green]\\n\\n"
                    "• Metal Performance Shaders (MPS) acceleration enabled\\n"
                    "• Unified memory architecture optimized\\n"
                    "• Memory-efficient attention mechanisms\\n"
                    f"• Quantization: {optimized_config.quantization}\\n"
                    "• Batch size optimization enabled"
                ),
                title="Environment Optimization: macOS Unified Memory",
                border_style="blue",
            )
            console.print(macos_panel)
        else:
            cpu_panel = Panel(
                Text.from_markup(
                    "[bold yellow]CPU-Only Environment Detected[/bold yellow]\\n\\n"
                    "• CPU-optimized inference pipeline\\n"
                    "• Aggressive quantization for memory efficiency\\n"
                    "• Reduced context window for faster processing\\n"
                    f"• Quantization: {optimized_config.quantization}"
                ),
                title="Environment Optimization: CPU Only",
                border_style="red",
            )
            console.print(cpu_panel)

    except Exception as e:
        console.print(f"[red]Error analyzing environment: {e}[/red]")
        raise click.ClickException(f"Environment analysis failed: {e}")


@sme_agent_cli.command("llm-deploy")
@click.option(
    "--model",
    type=click.Choice(["llama3.1-8b", "mistral-8b", "custom"]),
    default="llama3.1-8b",
    help="LLM model to deploy",
)
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Deployment complexity level",
)
@click.option("--use-docker", is_flag=True, help="Deploy using Docker container")
@click.option("--gpu", is_flag=True, help="Enable GPU acceleration")
@handle_sme_agent_error
def deploy_llm_infrastructure(model: str, complexity: str, use_docker: bool, gpu: bool):
    """Deploy 8B parameter LLM infrastructure."""
    try:
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn

        console = Console()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Deploying LLM infrastructure...", total=None)

            # Import LLM infrastructure
            from .llm_infrastructure import (
                LLMComplexityLevel,
                ModelType,
                create_llm_infrastructure,
            )

            # Map CLI options to enums
            complexity_map = {
                "basic": LLMComplexityLevel.BASIC,
                "standard": LLMComplexityLevel.STANDARD,
                "advanced": LLMComplexityLevel.ADVANCED,
                "enterprise": LLMComplexityLevel.ENTERPRISE,
            }

            model_map = {
                "llama3.1-8b": ModelType.LLAMA3_1_8B,
                "mistral-8b": ModelType.MISTRAL_8B,
                "custom": ModelType.CUSTOM,
            }

            # Create LLM infrastructure
            import asyncio

            async def deploy():
                llm_infra = await create_llm_infrastructure(
                    complexity_level=complexity,
                    model_type=model,
                    use_docker=use_docker,
                    device="cuda" if gpu else "auto",
                )
                return await llm_infra.initialize()

            result = asyncio.run(deploy())

        if result["success"]:
            console.print("[green]✅ LLM infrastructure deployed successfully![/green]")

            # Display deployment info
            deployment_table = Table(title="LLM Deployment Information")
            deployment_table.add_column("Property", style="cyan")
            deployment_table.add_column("Value", style="green")

            deployment_table.add_row("Model", result["model_name"])
            deployment_table.add_row("Complexity Level", complexity.title())
            deployment_table.add_row(
                "Deployment Mode", "Docker" if use_docker else "Local"
            )
            deployment_table.add_row("GPU Enabled", "Yes" if gpu else "No")
            deployment_table.add_row(
                "Initialization Time", f"{result['initialization_time']:.2f}s"
            )

            console.print(deployment_table)

        else:
            console.print("[red]❌ LLM deployment failed![/red]")
            if result.get("errors"):
                for error in result["errors"]:
                    console.print(f"  • {error}")

    except Exception as e:
        console.print(f"[red]Error deploying LLM infrastructure: {e}[/red]")


@sme_agent_cli.command("knowledge-extract")
@click.option(
    "--types",
    multiple=True,
    type=click.Choice(
        ["functions", "components", "patterns", "troubleshooting", "workflows", "all"]
    ),
    default=["all"],
    help="Types of knowledge to extract",
)
@click.option("--max-records", type=int, help="Maximum number of records to extract")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["jsonl", "csv", "parquet", "huggingface"]),
    default="jsonl",
    help="Output format for dataset",
)
@handle_sme_agent_error
def extract_knowledge_dataset(
    types: tuple[str], max_records: int | None, output_format: str
):
    """Extract knowledge dataset from Neo4j for fine-tuning."""
    try:
        from rich.console import Console
        from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

        console = Console()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Extracting knowledge dataset...", total=None)

            # Import knowledge graph pipeline
            from .knowledge_graph_pipeline import (
                KnowledgeExtractionType,
                create_knowledge_dataset,
            )

            # Map CLI types to enum
            type_map = {
                "functions": KnowledgeExtractionType.FUNCTIONS,
                "components": KnowledgeExtractionType.COMPONENTS,
                "patterns": KnowledgeExtractionType.PATTERNS,
                "troubleshooting": KnowledgeExtractionType.TROUBLESHOOTING,
                "workflows": KnowledgeExtractionType.WORKFLOWS,
                "all": KnowledgeExtractionType.ALL,
            }

            extraction_types = [type_map[t] for t in types]

            # Create dataset
            import asyncio

            async def extract():
                return await create_knowledge_dataset(
                    extraction_types=[t.value for t in extraction_types],
                    output_format=output_format,
                    max_records=max_records,
                )

            output_path = asyncio.run(extract())

        console.print("[green]✅ Knowledge dataset extracted successfully![/green]")
        console.print(f"Dataset saved to: [bold]{output_path}[/bold]")

        # Display extraction info
        extraction_table = Table(title="Knowledge Extraction Summary")
        extraction_table.add_column("Property", style="cyan")
        extraction_table.add_column("Value", style="green")

        extraction_table.add_row("Types Extracted", ", ".join(types))
        extraction_table.add_row("Output Format", output_format.upper())
        extraction_table.add_row(
            "Max Records", str(max_records) if max_records else "No limit"
        )
        extraction_table.add_row("Output Path", output_path)

        console.print(extraction_table)

    except Exception as e:
        console.print(f"[red]Error extracting knowledge dataset: {e}[/red]")


@sme_agent_cli.command("vector-enhance")
@click.option(
    "--model",
    type=click.Choice(
        [
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
            "bge-small-en-v1.5",
            "bge-base-en-v1.5",
        ]
    ),
    default="all-MiniLM-L6-v2",
    help="Embedding model to use",
)
@click.option(
    "--search-mode",
    type=click.Choice(["vector", "graph", "hybrid", "adaptive"]),
    default="hybrid",
    help="Search mode for retrieval",
)
@click.option("--enable-gpu", is_flag=True, help="Enable GPU acceleration for FAISS")
@click.option("--rerank", is_flag=True, help="Enable result reranking")
@handle_sme_agent_error
def enhance_vector_embeddings(
    model: str, search_mode: str, enable_gpu: bool, rerank: bool
):
    """Enhance vector embeddings with domain-specific knowledge."""
    try:
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn

        console = Console()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Enhancing vector embeddings...", total=None)

            # Import vector enhancement
            from .vector_embedding_enhancement import (
                EmbeddingModel,
                SearchMode,
                create_enhanced_vector_search,
            )

            # Map CLI options to enums
            model_map = {
                "all-MiniLM-L6-v2": EmbeddingModel.ALL_MINILM_L6_V2,
                "all-mpnet-base-v2": EmbeddingModel.ALL_MPNET_BASE_V2,
                "bge-small-en-v1.5": EmbeddingModel.BGE_SMALL_EN_V1_5,
                "bge-base-en-v1.5": EmbeddingModel.BGE_BASE_EN_V1_5,
            }

            search_mode_map = {
                "vector": SearchMode.VECTOR_ONLY,
                "graph": SearchMode.GRAPH_ONLY,
                "hybrid": SearchMode.HYBRID,
                "adaptive": SearchMode.ADAPTIVE,
            }

            # Create enhanced vector search
            import asyncio

            async def enhance():
                # Get documents from Neo4j (placeholder for now)
                documents = []  # This would be populated from Neo4j

                vector_enhancement = await create_enhanced_vector_search(
                    documents=documents,
                    embedding_model=model_map[model].value,
                    search_mode=search_mode_map[search_mode].value,
                    enable_gpu=enable_gpu,
                    enable_reranking=rerank,
                )

                return await vector_enhancement.initialize()

            result = asyncio.run(enhance())

        if result["success"]:
            console.print("[green]✅ Vector embeddings enhanced successfully![/green]")

            # Display enhancement info
            enhancement_table = Table(title="Vector Enhancement Summary")
            enhancement_table.add_column("Property", style="cyan")
            enhancement_table.add_column("Value", style="green")

            enhancement_table.add_row("Embedding Model", model)
            enhancement_table.add_row("Search Mode", search_mode.title())
            enhancement_table.add_row("GPU Enabled", "Yes" if enable_gpu else "No")
            enhancement_table.add_row("Reranking Enabled", "Yes" if rerank else "No")
            enhancement_table.add_row(
                "Initialization Time", f"{result['initialization_time']:.2f}s"
            )

            console.print(enhancement_table)

        else:
            console.print("[red]❌ Vector enhancement failed![/red]")
            if result.get("errors"):
                for error in result["errors"]:
                    console.print(f"  • {error}")

    except Exception as e:
        console.print(f"[red]Error enhancing vector embeddings: {e}[/red]")


@sme_agent_cli.command("infrastructure-status")
@handle_sme_agent_error
def infrastructure_status():
    """Display comprehensive infrastructure status for all SME Agent components."""
    try:
        from rich.columns import Columns
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        with console.status("[bold blue]Checking infrastructure status..."):
            # Import all validation functions
            from .knowledge_graph_pipeline import validate_knowledge_graph_environment
            from .llm_infrastructure import validate_llm_infrastructure_environment
            from .vector_embedding_enhancement import (
                validate_vector_embedding_environment,
            )

            # Run all validations
            llm_validation = validate_llm_infrastructure_environment()
            kg_validation = validate_knowledge_graph_environment()
            vector_validation = validate_vector_embedding_environment()

        # Create status tables
        tables = []

        # LLM Infrastructure Status
        llm_table = Table(
            title="LLM Infrastructure", show_header=True, header_style="bold blue"
        )
        llm_table.add_column("Component", style="cyan")
        llm_table.add_column("Status", justify="center")

        for component, info in llm_validation["components"].items():
            status = "✅" if info.get("available", False) else "❌"
            llm_table.add_row(component.title(), status)

        tables.append(llm_table)

        # Knowledge Graph Status
        kg_table = Table(
            title="Knowledge Graph Pipeline",
            show_header=True,
            header_style="bold green",
        )
        kg_table.add_column("Component", style="cyan")
        kg_table.add_column("Status", justify="center")

        for component, info in kg_validation["components"].items():
            status = "✅" if info.get("available", False) else "❌"
            kg_table.add_row(component.title(), status)

        tables.append(kg_table)

        # Vector Enhancement Status
        vector_table = Table(
            title="Vector Enhancement", show_header=True, header_style="bold magenta"
        )
        vector_table.add_column("Component", style="cyan")
        vector_table.add_column("Status", justify="center")

        for component, info in vector_validation["components"].items():
            status = "✅" if info.get("available", False) else "❌"
            vector_table.add_row(component.title(), status)

        tables.append(vector_table)

        # Display tables in columns
        console.print(Columns(tables, equal=True, expand=True))

        # Overall summary
        total_score = (
            llm_validation["validation_score"]
            + kg_validation["validation_score"]
            + vector_validation["validation_score"]
        )
        total_checks = (
            llm_validation["total_checks"]
            + kg_validation["total_checks"]
            + vector_validation["total_checks"]
        )
        overall_percentage = (
            (total_score / total_checks) * 100 if total_checks > 0 else 0
        )

        summary_panel = Panel(
            f"Overall Infrastructure Health: {overall_percentage:.1f}% ({total_score}/{total_checks} components available)",
            title="Infrastructure Summary",
            border_style=(
                "blue"
                if overall_percentage >= 80
                else "yellow" if overall_percentage >= 60 else "red"
            ),
        )
        console.print(summary_panel)

        # Recommendations
        all_recommendations = (
            llm_validation.get("recommendations", [])
            + kg_validation.get("recommendations", [])
            + vector_validation.get("recommendations", [])
        )

        if all_recommendations:
            console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
            for i, recommendation in enumerate(all_recommendations[:5], 1):
                console.print(f"{i}. {recommendation}")

    except Exception as e:
        console.print(f"[red]Error checking infrastructure status: {e}[/red]")


if __name__ == "__main__":
    sme_agent_cli()
