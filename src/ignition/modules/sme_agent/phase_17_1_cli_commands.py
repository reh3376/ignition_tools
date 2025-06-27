"""Phase 17.1: Advanced LLM Integration - CLI Commands

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

CLI interface for Phase 17.1 Advanced LLM Integration capabilities.
"""

import json
import logging

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

# Import Phase 17.1 components
from .phase_17_1_advanced_llm_integration import (
    AdvancedLLMIntegration,
    MultiModalContext,
    create_advanced_llm_integration,
    validate_phase_17_environment,
)
from .phase_17_1_test_framework import run_phase_17_tests, save_test_results

# Load environment variables
load_dotenv()

# Rich console for formatted output
console = Console()
logger = logging.getLogger(__name__)


def handle_cli_error(func):
    """Step 3: Error Handling with User-Friendly Messages

    Decorator for handling CLI errors with user-friendly messages.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            console.print(f"❌ Error: {e!s}", style="red")
            logger.error(f"CLI command failed: {e}")
            return False

    return wrapper


@click.group(name="phase17")
@click.pass_context
def phase_17_cli(ctx):
    """Phase 17.1: Advanced LLM Integration CLI Commands

    Comprehensive CLI interface for advanced LLM integration capabilities
    including multi-modal understanding, context-aware processing, and
    Ignition version compatibility.
    """
    ctx.ensure_object(dict)


@phase_17_cli.command()
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed validation information"
)
@handle_cli_error
def validate_env(verbose: bool):
    """Step 1: Environment Validation First

    Validate environment for Phase 17.1 Advanced LLM Integration.
    """
    console.print("🔍 Validating Phase 17.1 Environment...", style="blue")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating environment...", total=None)

        validation_result = validate_phase_17_environment()

        progress.update(task, completed=True)

    # Display results
    if validation_result["valid"]:
        console.print("✅ Environment validation passed", style="green")
    else:
        console.print("❌ Environment validation failed", style="red")

    # Create summary table
    table = Table(title="Environment Validation Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    # Add environment score
    score = validation_result.get("environment_score", 0)
    table.add_row("Overall Score", f"{score:.1f}%", "Environment readiness percentage")

    # Add component availability
    available = validation_result.get("components_available", [])
    total = validation_result.get("total_components", 0)
    table.add_row(
        "Components Available",
        f"{len(available)}/{total}",
        ", ".join(available[:3]) + ("..." if len(available) > 3 else ""),
    )

    # Add errors and warnings
    errors = validation_result.get("errors", [])
    warnings = validation_result.get("warnings", [])

    if errors:
        table.add_row("Errors", str(len(errors)), errors[0] if errors else "None")

    if warnings:
        table.add_row(
            "Warnings", str(len(warnings)), warnings[0] if warnings else "None"
        )

    console.print(table)

    if verbose and (errors or warnings):
        if errors:
            console.print("\n❌ Errors:", style="red bold")
            for error in errors:
                console.print(f"  • {error}", style="red")

        if warnings:
            console.print("\n⚠️  Warnings:", style="yellow bold")
            for warning in warnings:
                console.print(f"  • {warning}", style="yellow")


@phase_17_cli.command()
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level for initialization",
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed initialization information"
)
@handle_cli_error
def initialize(complexity: str, verbose: bool):
    """Step 2: Comprehensive Input Validation

    Initialize Advanced LLM Integration system.
    """
    console.print(
        f"🚀 Initializing Phase 17.1 Advanced LLM Integration (complexity: {complexity})...",
        style="blue",
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing system...", total=None)

        try:
            integration = create_advanced_llm_integration(complexity)
            status = integration.get_system_status()
            integration.cleanup()

            progress.update(task, completed=True)

            console.print("✅ System initialized successfully", style="green")

            if verbose:
                # Display system status
                status_table = Table(title="System Status")
                status_table.add_column("Component", style="cyan")
                status_table.add_column("Status", style="green")
                status_table.add_column("Details", style="yellow")

                status_table.add_row(
                    "Complexity Level", complexity, "Selected complexity level"
                )

                status_table.add_row(
                    "Initialized",
                    "✅ Yes" if status.get("initialized") else "❌ No",
                    "System initialization status",
                )

                components = status.get("components", {})
                for comp_name, comp_status in components.items():
                    status_table.add_row(
                        comp_name.replace("_", " ").title(),
                        "✅ Active" if comp_status else "❌ Inactive",
                        f"Component status: {comp_status}",
                    )

                console.print(status_table)

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"❌ Initialization failed: {e}", style="red")
            return False


@phase_17_cli.command()
@click.argument("question", required=True)
@click.option("--user-id", "-u", help="User ID for personalization")
@click.option("--ignition-version", "-v", help="Ignition version (e.g., 8.1.25)")
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.option(
    "--context-file",
    "-f",
    type=click.Path(exists=True),
    help="JSON file with multi-modal context",
)
@click.option("--save-response", "-s", type=click.Path(), help="Save response to file")
@handle_cli_error
def ask(
    question: str,
    user_id: str | None,
    ignition_version: str | None,
    complexity: str,
    context_file: str | None,
    save_response: str | None,
):
    """Process an enhanced request with context awareness.

    QUESTION: The question to ask the advanced LLM system
    """
    console.print("🤖 Processing enhanced request...", style="blue")

    # Load context if provided
    context = MultiModalContext()
    if context_file:
        try:
            with open(context_file) as f:
                context_data = json.load(f)
                # Create context from loaded data (simplified)
                context = MultiModalContext(
                    user_preferences=context_data.get("user_preferences", {}),
                    domain_expertise_level=context_data.get(
                        "domain_expertise_level", "intermediate"
                    ),
                )
        except Exception as e:
            console.print(f"⚠️  Failed to load context file: {e}", style="yellow")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing request...", total=None)

        try:
            # Create integration instance
            integration = create_advanced_llm_integration(complexity)

            # Process request
            response = integration.process_enhanced_request(
                question=question,
                user_id=user_id,
                context=context,
                ignition_version=ignition_version,
            )

            integration.cleanup()
            progress.update(task, completed=True)

            # Display response
            response_panel = Panel(
                response.content,
                title=f"Response (Confidence: {response.confidence:.2f})",
                border_style="green",
            )
            console.print(response_panel)

            # Display metadata
            metadata_table = Table(title="Response Metadata")
            metadata_table.add_column("Property", style="cyan")
            metadata_table.add_column("Value", style="yellow")

            metadata_table.add_row("Response ID", response.response_id)
            metadata_table.add_row(
                "Processing Time", f"{response.processing_time:.3f}s"
            )
            metadata_table.add_row(
                "Version Specific",
                "Yes" if response.ignition_version_specific else "No",
            )
            metadata_table.add_row("Target Version", response.target_version or "N/A")
            metadata_table.add_row(
                "Personalized", "Yes" if response.personalized_content else "No"
            )
            metadata_table.add_row("User Level", response.user_expertise_level)

            console.print(metadata_table)

            # Show code suggestions if available
            if response.code_suggestions:
                console.print("\n💡 Code Suggestions:", style="blue bold")
                for i, suggestion in enumerate(response.code_suggestions, 1):
                    syntax = Syntax(
                        suggestion, "python", theme="monokai", line_numbers=True
                    )
                    console.print(f"Suggestion {i}:")
                    console.print(syntax)

            # Save response if requested
            if save_response:
                response_data = {
                    "question": question,
                    "response": response.content,
                    "metadata": {
                        "response_id": response.response_id,
                        "confidence": response.confidence,
                        "processing_time": response.processing_time,
                        "timestamp": response.timestamp.isoformat(),
                    },
                }

                with open(save_response, "w") as f:
                    json.dump(response_data, f, indent=2)

                console.print(f"✅ Response saved to: {save_response}", style="green")

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"❌ Request processing failed: {e}", style="red")
            return False


@phase_17_cli.command()
@click.argument("version", required=True)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed version information")
@handle_cli_error
def version_info(version: str, verbose: bool):
    """Get Ignition version capabilities and features.

    VERSION: Ignition version string (e.g., 8.1.25)
    """
    console.print(f"🔍 Analyzing Ignition version: {version}", style="blue")

    try:
        integration = create_advanced_llm_integration("standard")
        version_info = integration.get_version_capabilities(version)
        integration.cleanup()

        # Create version info table
        info_table = Table(title=f"Ignition {version} Capabilities")
        info_table.add_column("Feature", style="cyan")
        info_table.add_column("Available", style="green")
        info_table.add_column("Description", style="yellow")

        # Core version info
        info_table.add_row("Version", version_info.version, "Full version string")
        info_table.add_row(
            "Major.Minor.Patch",
            f"{version_info.major_version}.{version_info.minor_version}.{version_info.patch_version}",
            "Version components",
        )

        # Feature availability
        features = [
            (
                "Perspective",
                version_info.has_perspective,
                "Modern web-based HMI platform",
            ),
            ("Vision", version_info.has_vision, "Traditional Windows-based HMI"),
            (
                "Reporting",
                version_info.has_reporting,
                "Report generation and scheduling",
            ),
            ("WebDev", version_info.has_webdev, "Web development module"),
            ("Mobile", version_info.has_mobile, "Mobile app development"),
            ("OPC-UA", version_info.has_opc_ua, "OPC-UA connectivity"),
        ]

        for feature_name, available, description in features:
            status = "✅ Yes" if available else "❌ No"
            info_table.add_row(feature_name, status, description)

        if verbose:
            # Advanced features
            advanced_features = [
                (
                    "Component Scripting",
                    version_info.supports_component_scripting,
                    "Component-level scripting",
                ),
                (
                    "Tag Scripting",
                    version_info.supports_tag_scripting,
                    "Tag event scripting",
                ),
                (
                    "Gateway Scripting",
                    version_info.supports_gateway_scripting,
                    "Gateway-level scripting",
                ),
                (
                    "Client Scripting",
                    version_info.supports_client_scripting,
                    "Client-side scripting",
                ),
                (
                    "Perspective Sessions",
                    version_info.supports_perspective_sessions,
                    "Perspective session management",
                ),
                (
                    "Named Queries",
                    version_info.supports_named_queries,
                    "Reusable database queries",
                ),
                (
                    "Tag History Splitter",
                    version_info.supports_tag_history_splitter,
                    "Efficient historical queries",
                ),
                (
                    "Expression Tags",
                    version_info.supports_expression_tags,
                    "Calculated tag values",
                ),
            ]

            for feature_name, available, description in advanced_features:
                status = "✅ Yes" if available else "❌ No"
                info_table.add_row(feature_name, status, description)

        console.print(info_table)

    except Exception as e:
        console.print(f"❌ Version analysis failed: {e}", style="red")
        return False


@phase_17_cli.command()
@click.option(
    "--integration/--no-integration", default=True, help="Run integration tests"
)
@click.option(
    "--performance/--no-performance", default=True, help="Run performance tests"
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose test output")
@click.option(
    "--save-results", "-s", type=click.Path(), help="Save test results to file"
)
@handle_cli_error
def test(integration: bool, performance: bool, verbose: bool, save_results: str | None):
    """Step 4: Modular Component Testing

    Run comprehensive test suite for Phase 17.1.
    """
    console.print("🧪 Running Phase 17.1 Comprehensive Test Suite", style="blue")

    # Set test configuration
    test_config = {
        "include_integration": integration,
        "include_performance": performance,
        "verbose": verbose,
    }

    console.print(f"Test Configuration: {test_config}", style="cyan")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running tests...", total=None)

        try:
            # Run tests
            results = run_phase_17_tests(**test_config)

            progress.update(task, completed=True)

            # Display results summary
            overall = results["overall_results"]

            # Create results table
            results_table = Table(title="Test Results Summary")
            results_table.add_column("Metric", style="cyan")
            results_table.add_column("Value", style="green")
            results_table.add_column("Status", style="yellow")

            results_table.add_row("Total Tests", str(overall["total_tests"]), "")
            results_table.add_row("Passed", str(overall["passed_tests"]), "✅")
            results_table.add_row(
                "Failed",
                str(overall["failed_tests"]),
                "❌" if overall["failed_tests"] > 0 else "",
            )
            results_table.add_row(
                "Success Rate",
                f"{overall['success_rate']:.1f}%",
                (
                    "✅"
                    if overall["success_rate"] >= 80
                    else "⚠️" if overall["success_rate"] >= 60 else "❌"
                ),
            )
            results_table.add_row(
                "Total Time", f"{overall['total_execution_time']:.3f}s", ""
            )

            console.print(results_table)

            # Display test suite results
            suite_table = Table(title="Test Suite Details")
            suite_table.add_column("Suite", style="cyan")
            suite_table.add_column("Tests", style="white")
            suite_table.add_column("Passed", style="green")
            suite_table.add_column("Failed", style="red")
            suite_table.add_column("Success Rate", style="yellow")
            suite_table.add_column("Time", style="blue")

            for suite in results["test_suites"]:
                status_icon = (
                    "✅"
                    if suite["success_rate"] >= 80
                    else "⚠️" if suite["success_rate"] >= 60 else "❌"
                )
                suite_table.add_row(
                    f"{status_icon} {suite['suite_name']}",
                    str(suite["total_tests"]),
                    str(suite["passed_tests"]),
                    str(suite["failed_tests"]),
                    f"{suite['success_rate']:.1f}%",
                    f"{suite['total_execution_time']:.3f}s",
                )

            console.print(suite_table)

            # Save results if requested
            if save_results:
                save_test_results(results, save_results)
                console.print(
                    f"✅ Test results saved to: {save_results}", style="green"
                )

            # Return appropriate exit code
            return overall["success_rate"] >= 80

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"❌ Test execution failed: {e}", style="red")
            return False


@phase_17_cli.command()
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@handle_cli_error
def status(complexity: str):
    """Step 5: Progressive Complexity Support

    Get system status and health information.
    """
    console.print("📊 Getting Phase 17.1 System Status...", style="blue")

    try:
        integration = AdvancedLLMIntegration(complexity)
        init_success = integration.initialize()
        system_status = integration.get_system_status()
        integration.cleanup()

        # Create status panel
        status_content = f"""
System Initialized: {"✅ Yes" if system_status.get("initialized") else "❌ No"}
Complexity Level: {system_status.get("complexity_level", "Unknown")}
Validation Result: {"✅ Valid" if system_status.get("validation_result", {}).get("valid") else "❌ Invalid"}

Components:
"""

        components = system_status.get("components", {})
        for comp_name, comp_status in components.items():
            status_icon = "✅" if comp_status else "❌"
            comp_display = comp_name.replace("_", " ").title()
            status_content += f"  {status_icon} {comp_display}\n"

        status_panel = Panel(
            status_content.strip(),
            title=f"Phase 17.1 System Status ({complexity})",
            border_style="green" if init_success else "red",
        )

        console.print(status_panel)

        # Show validation details if available
        validation = system_status.get("validation_result", {})
        if validation:
            val_table = Table(title="Environment Validation Details")
            val_table.add_column("Property", style="cyan")
            val_table.add_column("Value", style="yellow")

            val_table.add_row(
                "Environment Score", f"{validation.get('environment_score', 0):.1f}%"
            )
            val_table.add_row(
                "Components Available",
                str(len(validation.get("components_available", []))),
            )
            val_table.add_row(
                "Total Components", str(validation.get("total_components", 0))
            )
            val_table.add_row("Errors", str(len(validation.get("errors", []))))
            val_table.add_row("Warnings", str(len(validation.get("warnings", []))))

            console.print(val_table)

    except Exception as e:
        console.print(f"❌ Status check failed: {e}", style="red")
        return False


@phase_17_cli.command()
@handle_cli_error
def demo():
    """Step 6: Resource Management and Cleanup

    Run Phase 17.1 capabilities demonstration.
    """
    console.print("🎭 Running Phase 17.1 Capabilities Demo", style="blue")

    try:
        # Import and run demo
        from .phase_17_1_advanced_llm_integration import demo_phase_17_capabilities

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running demo...", total=None)

            # Capture demo output
            demo_phase_17_capabilities()

            progress.update(task, completed=True)

        console.print("✅ Demo completed successfully", style="green")

    except Exception as e:
        console.print(f"❌ Demo failed: {e}", style="red")
        return False


# Main CLI entry point for Phase 17.1
def main():
    """Main entry point for Phase 17.1 CLI."""
    phase_17_cli()


if __name__ == "__main__":
    main()
