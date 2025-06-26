"""CLI Commands for IGN Scripts Web Intelligence System - Phase 11.8.

Following crawl_mcp.py methodology for CLI implementation:
1. Environment validation before all operations
2. Comprehensive input validation using Pydantic models
3. Robust error handling with user-friendly messages
4. Progressive complexity with detailed status reporting
5. Proper resource management with cleanup

Commands Implementation (Week 29-30):
- ign web crawl <url>       # Crawl documentation with local models
- ign web search <query>    # Semantic search using local embeddings
- ign web update           # Update knowledge base from configured sources
- ign web sources          # Manage documentation sources
- ign web status           # Show crawling status and model health
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from . import format_neo4j_error, validate_environment
from .crawler import get_crawler, validate_crawl_request
from .models import (
    format_model_error,
    get_default_model_configs,
    validate_model_environment,
)

console = Console()


def web_crawl_command(url: str, **kwargs) -> dict[str, Any]:
    """Crawl documentation with local models (crawl_mcp.py methodology).

    Args:
        url: URL to crawl
        **kwargs: Additional crawl parameters

    Returns:
        dict: Crawl results and status
    """
    console.print("\n[bold blue]IGN Scripts Web Intelligence - Crawl Documentation[/bold blue]")

    # Step 1: Environment validation first (crawl_mcp.py methodology)
    console.print("\n[yellow]Validating environment...[/yellow]")
    if not validate_environment():
        return {
            "success": False,
            "error": "Environment validation failed. Check configuration and dependencies.",
        }

    # Step 2: Input validation and sanitization
    console.print("[yellow]Validating crawl request...[/yellow]")
    validation = validate_crawl_request(url, **kwargs)
    if not validation["valid"]:
        return {
            "success": False,
            "error": f"Invalid crawl request: {validation['error']}",
        }

    crawl_request = validation["request"]

    # Step 3: Model environment validation
    console.print("[yellow]Checking model environment...[/yellow]")
    if not validate_model_environment():
        return {
            "success": False,
            "error": "Model environment not ready. Check Hugging Face and Ollama setup.",
        }

    # Step 4: Execute crawl with proper resource management
    try:
        console.print(f"[green]Starting crawl of: {url}[/green]")

        # Use async context manager for proper cleanup (crawl_mcp.py patterns)
        async def run_crawl() -> Any:
            async with get_crawler() as crawler:
                result = await crawler.crawl(crawl_request)
                return result

        # Run async crawl
        result = asyncio.run(run_crawl())

        if result.success:
            # Display results table
            table = Table(title="Crawl Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("URL", result.url)
            table.add_row("Title", result.title or "N/A")
            table.add_row("Content Length", f"{len(result.content):,} characters")
            table.add_row("Chunks Created", str(len(result.chunks)))
            table.add_row("Code Blocks", str(len(result.code_blocks)))
            table.add_row("Links Found", str(len(result.links)))

            console.print(table)

            # Save output if requested
            output_file = kwargs.get("output")
            if output_file:
                try:
                    output_data = {
                        "url": result.url,
                        "title": result.title,
                        "content": result.content,
                        "chunks": result.chunks,
                        "code_blocks": result.code_blocks,
                        "links": result.links,
                        "metadata": result.metadata,
                    }

                    output_path = Path(output_file)
                    output_path.write_text(json.dumps(output_data, indent=2))
                    console.print(f"[green]Results saved to: {output_file}[/green]")

                except Exception as e:
                    console.print(f"[red]Failed to save output: {e}[/red]")

            return {
                "success": True,
                "url": result.url,
                "chunks_created": len(result.chunks),
                "code_blocks_found": len(result.code_blocks),
                "content_length": len(result.content),
            }
        else:
            console.print(f"[red]Crawl failed: {result.error}[/red]")
            return {"success": False, "error": result.error}

    except Exception as e:
        error_msg = format_model_error(e)
        console.print(f"[red]Crawl error: {error_msg}[/red]")
        return {"success": False, "error": error_msg}


def web_search_command(query: str, **kwargs) -> dict[str, Any]:
    """Semantic search using local embeddings (crawl_mcp.py methodology).

    Args:
        query: Search query
        **kwargs: Additional search parameters

    Returns:
        dict: Search results
    """
    console.print("\n[bold blue]IGN Scripts Web Intelligence - Semantic Search[/bold blue]")

    # Environment validation first
    if not validate_environment():
        return {"success": False, "error": "Environment validation failed"}

    # Input validation
    if not query or not query.strip():
        return {"success": False, "error": "Search query is required"}

    # Model validation
    if not validate_model_environment():
        return {"success": False, "error": "Model environment not ready"}

    console.print(f"[yellow]Searching for: {query}[/yellow]")

    # TODO: Implement semantic search with local embeddings
    # This would connect to Neo4j and use local embedding models
    console.print("[red]Semantic search not yet implemented[/red]")

    return {"success": False, "error": "Semantic search feature not yet implemented"}


def web_update_command(**kwargs) -> dict[str, Any]:
    """Update knowledge base from configured sources (crawl_mcp.py methodology).

    Args:
        **kwargs: Update parameters

    Returns:
        dict: Update results
    """
    console.print("\n[bold blue]IGN Scripts Web Intelligence - Update Knowledge Base[/bold blue]")

    # Environment validation
    if not validate_environment():
        return {"success": False, "error": "Environment validation failed"}

    # Get configured sources
    sources = os.getenv("DOCUMENTATION_SOURCES", "").strip()
    if not sources:
        return {
            "success": False,
            "error": "No documentation sources configured. Set DOCUMENTATION_SOURCES environment variable.",
        }

    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    console.print(f"[yellow]Configured sources: {', '.join(source_list)}[/yellow]")

    # TODO: Implement batch update functionality
    console.print("[red]Knowledge base update not yet implemented[/red]")

    return {
        "success": False,
        "error": "Knowledge base update feature not yet implemented",
    }


def web_sources_command(**kwargs) -> dict[str, Any]:
    """Manage documentation sources (crawl_mcp.py methodology).

    Args:
        **kwargs: Source management parameters

    Returns:
        dict: Source management results
    """
    console.print("\n[bold blue]IGN Scripts Web Intelligence - Manage Sources[/bold blue]")

    # Get current sources
    sources = os.getenv("DOCUMENTATION_SOURCES", "").strip()
    source_list = [s.strip() for s in sources.split(",") if s.strip()] if sources else []

    # Display sources table
    table = Table(title="Configured Documentation Sources")
    table.add_column("Index", style="cyan")
    table.add_column("Source", style="green")
    table.add_column("Status", style="yellow")

    if source_list:
        for i, source in enumerate(source_list, 1):
            # TODO: Check source status (reachable, last crawled, etc.)
            status = "Unknown"
            table.add_row(str(i), source, status)
    else:
        table.add_row("0", "No sources configured", "N/A")

    console.print(table)

    # Display configuration help
    console.print("\n[blue]Configuration:[/blue]")
    console.print("Set DOCUMENTATION_SOURCES environment variable with comma-separated URLs:")
    console.print(
        "Example: DOCUMENTATION_SOURCES=https://docs.ignitiongateway.com,https://forum.inductiveautomation.com"
    )

    return {"success": True, "sources": source_list, "total_sources": len(source_list)}


def web_status_command(**kwargs) -> dict[str, Any]:
    """Show crawling status and model health (crawl_mcp.py methodology).

    Args:
        **kwargs: Status parameters

    Returns:
        dict: System status
    """
    console.print("\n[bold blue]IGN Scripts Web Intelligence - System Status[/bold blue]")

    status_data: dict[str, Any] = {
        "success": True,
        "environment": {},
        "models": {},
        "crawling": {},
        "knowledge_graph": {},
    }

    # Environment Status
    console.print("\n[yellow]Environment Status:[/yellow]")
    env_status = validate_environment()
    status_data["environment"]["valid"] = env_status

    if env_status:
        console.print("  ✓ Environment: Ready")
    else:
        console.print("  ✗ Environment: Not Ready")

    # Model Status
    console.print("\n[yellow]Model Status:[/yellow]")
    model_status = validate_model_environment()
    status_data["models"]["environment_ready"] = model_status

    if model_status:
        console.print("  ✓ Model Environment: Ready")

        # Display model configurations
        model_configs = get_default_model_configs()

        model_table = Table(title="Available Models")
        model_table.add_column("Name", style="cyan")
        model_table.add_column("Type", style="green")
        model_table.add_column("Source", style="yellow")
        model_table.add_column("Memory", style="red")
        model_table.add_column("GPU", style="blue")

        for config in model_configs:
            gpu_req = "Yes" if config.gpu_required else "No"
            model_table.add_row(
                config.name,
                config.type,
                config.source,
                f"{config.memory_gb:.1f}GB",
                gpu_req,
            )

        console.print(model_table)
        status_data["models"]["configurations"] = len(model_configs)
    else:
        console.print("  ✗ Model Environment: Not Ready")

    # Crawling Status
    console.print("\n[yellow]Crawling Status:[/yellow]")
    sources = os.getenv("DOCUMENTATION_SOURCES", "").strip()
    if sources:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
        console.print(f"  ✓ Configured Sources: {len(source_list)}")
        status_data["crawling"]["sources_configured"] = len(source_list)
    else:
        console.print("  ✗ No sources configured")
        status_data["crawling"]["sources_configured"] = 0

    # Knowledge Graph Status
    console.print("\n[yellow]Knowledge Graph Status:[/yellow]")
    try:
        from . import validate_neo4j_connection

        neo4j_status = validate_neo4j_connection()

        if neo4j_status:
            console.print("  ✓ Neo4j: Connected")
            status_data["knowledge_graph"]["connected"] = True
        else:
            console.print("  ✗ Neo4j: Not configured")
            status_data["knowledge_graph"]["connected"] = False

    except Exception as e:
        console.print(f"  ✗ Neo4j: Error - {format_neo4j_error(e)}")
        status_data["knowledge_graph"]["connected"] = False
        status_data["knowledge_graph"]["error"] = str(e)

    # Overall Health Score
    health_checks = [
        env_status,
        model_status,
        len(sources.split(",")) > 0 if sources else False,
        status_data["knowledge_graph"]["connected"],
    ]

    health_score = (sum(health_checks) / len(health_checks)) * 100
    status_data["overall_health"] = health_score

    console.print(f"\n[bold]Overall Health: {health_score:.0f}%[/bold]")

    if health_score == 100:
        console.print("[green]All systems operational[/green]")
    elif health_score >= 75:
        console.print("[yellow]Most systems operational[/yellow]")
    elif health_score >= 50:
        console.print("[orange]Some systems need attention[/orange]")
    else:
        console.print("[red]Multiple systems need attention[/red]")

    return status_data


def validate_script(args) -> dict[str, Any]:
    """Enhanced AI code validation CLI command (Week 31-32, crawl_mcp.py methodology).

    Args:
        args: CLI arguments with script_path and validation options

    Returns:
        dict: Validation results with comprehensive analysis
    """
    try:
        # Step 1: Input validation (crawl_mcp.py patterns)
        if not hasattr(args, "script_path") or not args.script_path:
            return {
                "success": False,
                "error": "Script path is required. Usage: ign web validate <script_path>",
            }

        script_path = str(args.script_path).strip()

        # Step 2: Environment validation before proceeding
        console.print("🔍 [bold blue]IGN Enhanced Code Validator - Phase 11.8[/bold blue]")
        console.print()

        # Import enhanced validator
        try:
            from src.ignition.code_intelligence.enhanced_validator import (
                EnhancedCodeValidator,
                ValidationRequest,
                validate_script_path,
            )
        except ImportError as e:
            return {
                "success": False,
                "error": f"Enhanced validator not available: {e!s}",
            }

        # Step 3: Validate script path
        path_validation = validate_script_path(script_path)
        if not path_validation["valid"]:
            return {"success": False, "error": path_validation["error"]}

        # Step 4: Initialize validator with Neo4j credentials
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        validator = EnhancedCodeValidator(neo4j_uri=neo4j_uri, neo4j_user=neo4j_user, neo4j_password=neo4j_password)

        async def run_validation() -> Any:
            """Run validation with proper async handling."""
            try:
                # Step 5: Initialize validator environment
                console.print("🚀 Initializing enhanced code validator...")

                if not await validator.initialize():
                    return {
                        "success": False,
                        "error": "Validator initialization failed",
                    }

                # Step 6: Create validation request
                request = ValidationRequest(
                    script_path=script_path,
                    check_imports=getattr(args, "check_imports", True),
                    check_syntax=getattr(args, "check_syntax", True),
                    check_knowledge_graph=getattr(args, "check_kg", True),
                    check_hallucinations=getattr(args, "check_hallucinations", True),
                    confidence_threshold=getattr(args, "confidence_threshold", 0.7),
                )

                # Step 7: Run comprehensive validation
                console.print(f"📋 Validating script: [bold]{script_path}[/bold]")
                console.print()

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Running validation checks...", total=None)
                    result = await validator.validate_script(request)
                    progress.update(task, completed=True)

                # Step 8: Display comprehensive results
                display_validation_results(result, console)

                # Step 9: Save results if requested
                if getattr(args, "output", None):
                    save_validation_results(result, args.output)

                return {
                    "success": True,
                    "result": result,
                    "message": f"Validation completed for {script_path}",
                }

            except Exception as e:
                return {"success": False, "error": f"Validation failed: {e!s}"}
            finally:
                # Step 10: Resource cleanup (crawl_mcp.py methodology)
                await validator.close()

        # Run async validation
        import asyncio

        return asyncio.run(run_validation())

    except Exception as e:
        return {"success": False, "error": f"Enhanced validation error: {e!s}"}


def analyze_hallucinations(args) -> dict[str, Any]:
    """AI hallucination analysis CLI command (Week 31-32, crawl_mcp.py methodology).

    Args:
        args: CLI arguments with script_path and analysis options

    Returns:
        dict: Hallucination analysis results
    """
    try:
        # Step 1: Input validation (crawl_mcp.py patterns)
        if not hasattr(args, "script_path") or not args.script_path:
            return {
                "success": False,
                "error": "Script path is required. Usage: ign web hallucinations <script_path>",
            }

        script_path = str(args.script_path).strip()

        console.print("🤖 [bold red]AI Hallucination Detection - Phase 11.8[/bold red]")
        console.print()

        # Step 2: Import enhanced validator
        try:
            from src.ignition.code_intelligence.enhanced_validator import (
                EnhancedCodeValidator,
                ValidationRequest,
                validate_script_path,
            )
        except ImportError as e:
            return {
                "success": False,
                "error": f"Enhanced validator not available: {e!s}",
            }

        # Step 3: Validate script path
        path_validation = validate_script_path(script_path)
        if not path_validation["valid"]:
            return {"success": False, "error": path_validation["error"]}

        # Step 4: Initialize validator for hallucination detection only
        validator = EnhancedCodeValidator()

        async def run_hallucination_analysis() -> Any:
            """Run hallucination analysis with local models."""
            try:
                # Step 5: Initialize validator environment
                if not await validator.initialize():
                    return {
                        "success": False,
                        "error": "Validator initialization failed",
                    }

                # Step 6: Create focused validation request for hallucinations
                request = ValidationRequest(
                    script_path=script_path,
                    check_imports=False,
                    check_syntax=False,
                    check_knowledge_graph=False,
                    check_hallucinations=True,
                    confidence_threshold=getattr(args, "confidence_threshold", 0.5),
                )

                # Step 7: Run hallucination detection
                console.print(f"🔍 Analyzing potential AI hallucinations in: [bold]{script_path}[/bold]")
                console.print()

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Detecting AI hallucinations...", total=None)
                    result = await validator.validate_script(request)
                    progress.update(task, completed=True)

                # Step 8: Display focused hallucination results
                display_hallucination_results(result, console)

                return {
                    "success": True,
                    "result": result,
                    "hallucination_free": result.hallucination_free,
                    "confidence_score": result.confidence_score,
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Hallucination analysis failed: {e!s}",
                }
            finally:
                await validator.close()

        # Run async analysis
        import asyncio

        return asyncio.run(run_hallucination_analysis())

    except Exception as e:
        return {"success": False, "error": f"Hallucination analysis error: {e!s}"}


def validate_batch(args) -> dict[str, Any]:
    """Batch validation CLI command (Week 31-32, crawl_mcp.py methodology).

    Args:
        args: CLI arguments with directory path and batch options

    Returns:
        dict: Batch validation results
    """
    try:
        # Step 1: Input validation (crawl_mcp.py patterns)
        if not hasattr(args, "directory") or not args.directory:
            return {
                "success": False,
                "error": "Directory path is required. Usage: ign web validate-batch <directory>",
            }

        directory_path = str(args.directory).strip()

        # Step 2: Validate directory path
        if not os.path.exists(directory_path):
            return {"success": False, "error": f"Directory not found: {directory_path}"}

        if not os.path.isdir(directory_path):
            return {
                "success": False,
                "error": f"Path is not a directory: {directory_path}",
            }

        console.print("📂 [bold cyan]Batch Code Validation - Phase 11.8[/bold cyan]")
        console.print()

        # Step 3: Find Python scripts in directory
        python_files = []
        for root, _dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        if not python_files:
            return {
                "success": False,
                "error": f"No Python files found in directory: {directory_path}",
            }

        console.print(f"Found {len(python_files)} Python files for validation")
        console.print()

        # Step 4: Import enhanced validator
        try:
            from src.ignition.code_intelligence.enhanced_validator import (
                EnhancedCodeValidator,
                ValidationRequest,
                validate_script_path,
            )
        except ImportError as e:
            return {
                "success": False,
                "error": f"Enhanced validator not available: {e!s}",
            }

        # Step 5: Initialize validator for batch processing
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        validator = EnhancedCodeValidator(neo4j_uri=neo4j_uri, neo4j_user=neo4j_user, neo4j_password=neo4j_password)

        async def run_batch_validation() -> Any:
            """Run batch validation with progress tracking."""
            try:
                # Step 6: Initialize validator environment
                if not await validator.initialize():
                    return {
                        "success": False,
                        "error": "Validator initialization failed",
                    }

                batch_results = []

                # Step 7: Process files with progress tracking
                with Progress(
                    TextColumn("[progress.description]"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Validating Python files...", total=len(python_files))

                    for file_path in python_files:
                        # Step 8: Validate each file
                        try:
                            request = ValidationRequest(
                                script_path=file_path,
                                check_imports=getattr(args, "check_imports", True),
                                check_syntax=getattr(args, "check_syntax", True),
                                check_knowledge_graph=getattr(args, "check_kg", True),
                                check_hallucinations=getattr(args, "check_hallucinations", True),
                                confidence_threshold=getattr(args, "confidence_threshold", 0.7),
                            )

                            result = await validator.validate_script(request)
                            batch_results.append(
                                {
                                    "file": file_path,
                                    "result": result,
                                    "valid": result.valid,
                                    "confidence": result.confidence_score,
                                }
                            )

                        except Exception as e:
                            batch_results.append(
                                {
                                    "file": file_path,
                                    "result": None,
                                    "valid": False,
                                    "error": str(e),
                                }
                            )

                        progress.advance(task)

                # Step 9: Display batch results summary
                display_batch_results(batch_results, console)

                # Step 10: Save batch results if requested
                if getattr(args, "output", None):
                    save_batch_results(batch_results, args.output)

                return {
                    "success": True,
                    "batch_results": batch_results,
                    "total_files": len(python_files),
                    "valid_files": len([r for r in batch_results if r.get("valid", False)]),
                    "message": f"Batch validation completed for {len(python_files)} files",
                }

            except Exception as e:
                return {"success": False, "error": f"Batch validation failed: {e!s}"}
            finally:
                await validator.close()

        # Run async batch validation
        import asyncio

        return asyncio.run(run_batch_validation())

    except Exception as e:
        return {"success": False, "error": f"Batch validation error: {e!s}"}


def display_validation_results(result: Any, console: Console) -> None:
    """Display comprehensive validation results (crawl_mcp.py methodology)."""
    # Create results table
    table = Table(
        title="Enhanced Code Validation Results",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Confidence", justify="center")
    table.add_column("Details")

    # Add validation results
    status_icon = "✅" if result.syntax_valid else "❌"
    table.add_row("Syntax", status_icon, "-", "AST parsing and structure analysis")

    status_icon = "✅" if result.imports_valid else "❌"
    table.add_row("Imports", status_icon, "-", "Module availability validation")

    status_icon = "✅" if result.knowledge_graph_valid else "❌"
    table.add_row("Knowledge Graph", status_icon, "-", "Neo4j cross-validation")

    status_icon = "✅" if result.hallucination_free else "❌"
    table.add_row("Hallucination Free", status_icon, "-", "AI-generated code detection")

    console.print(table)
    console.print()

    # Display overall status
    overall_status = "✅ VALID" if result.valid else "❌ INVALID"
    confidence_color = (
        "green" if result.confidence_score >= 0.8 else "yellow" if result.confidence_score >= 0.6 else "red"
    )

    console.print(f"Overall Status: [bold]{overall_status}[/bold]")
    console.print(f"Confidence Score: [{confidence_color}]{result.confidence_score:.2f}[/{confidence_color}]")
    console.print()

    # Display issues if any
    if result.issues:
        console.print("[bold red]Issues Found:[/bold red]")
        for issue in result.issues:
            severity_color = (
                "red" if issue["severity"] == "error" else "yellow" if issue["severity"] == "warning" else "blue"
            )
            console.print(
                f"  [{severity_color}]{issue['severity'].upper()}[/{severity_color}] Line {issue['line']}: {issue['message']}"  # noqa: E501
            )
        console.print()

    # Display suggestions if any
    if result.suggestions:
        console.print("[bold blue]Suggestions:[/bold blue]")
        for suggestion in result.suggestions:
            console.print(f"  • {suggestion}")
        console.print()


def display_hallucination_results(result: Any, console: Console) -> None:
    """Display focused hallucination analysis results."""
    hallucination_issues = [issue for issue in result.issues if issue["type"] == "potential_hallucination"]

    if not hallucination_issues:
        console.print("✅ [bold green]No AI hallucinations detected[/bold green]")
        console.print(f"Confidence: {result.confidence_score:.2f}")
    else:
        console.print("⚠️ [bold yellow]Potential AI hallucinations detected:[/bold yellow]")
        for issue in hallucination_issues:
            console.print(f"  Line {issue['line']}: {issue['message']}")
        console.print(f"Confidence: {result.confidence_score:.2f}")


def display_batch_results(batch_results: list[dict[str, Any]], console: Console) -> None:
    """Display batch validation results summary."""
    # Create batch results table
    table = Table(title="Batch Validation Summary", show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Confidence", justify="center")
    table.add_column("Issues")

    for result in batch_results:
        file_name = os.path.basename(result["file"])

        if result.get("valid", False):
            status = "✅"
            confidence = f"{result.get('confidence', 0.0):.2f}"
            issues_count = len(result["result"].issues) if result["result"] else 0
            issues = str(issues_count)
        else:
            status = "❌"
            confidence = "N/A"
            issues = result.get("error", "Unknown error")

        table.add_row(file_name, status, confidence, issues)

    console.print(table)
    console.print()

    # Display summary statistics
    total_files = len(batch_results)
    valid_files = len([r for r in batch_results if r.get("valid", False)])
    invalid_files = total_files - valid_files

    console.print(f"Total Files: [bold]{total_files}[/bold]")
    console.print(f"Valid Files: [bold green]{valid_files}[/bold green]")
    console.print(f"Invalid Files: [bold red]{invalid_files}[/bold red]")
    console.print(f"Success Rate: [bold]{(valid_files / total_files) * 100:.1f}%[/bold]")


def save_validation_results(result: Any, output_path: str) -> None:
    """Save validation results to file (crawl_mcp.py methodology)."""
    try:
        import json

        # Convert result to dictionary for JSON serialization
        result_dict = {
            "script_path": result.script_path,
            "valid": result.valid,
            "confidence_score": result.confidence_score,
            "syntax_valid": result.syntax_valid,
            "imports_valid": result.imports_valid,
            "knowledge_graph_valid": result.knowledge_graph_valid,
            "hallucination_free": result.hallucination_free,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "metadata": result.metadata,
            "error_message": result.error_message,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        console.print(f"✅ Results saved to: [bold]{output_path}[/bold]")

    except Exception as e:
        console.print(f"❌ Failed to save results: {e!s}")


def save_batch_results(batch_results: list[dict[str, Any]], output_path: str) -> None:
    """Save batch validation results to file."""
    try:
        import json

        # Convert batch results for JSON serialization
        serializable_results = []
        for result in batch_results:
            if result.get("result"):
                # Convert ValidationResult to dict
                result_dict = {
                    "file": result["file"],
                    "valid": result["valid"],
                    "confidence": result.get("confidence", 0.0),
                    "validation_details": {
                        "syntax_valid": result["result"].syntax_valid,
                        "imports_valid": result["result"].imports_valid,
                        "knowledge_graph_valid": result["result"].knowledge_graph_valid,
                        "hallucination_free": result["result"].hallucination_free,
                        "issues": result["result"].issues,
                        "suggestions": result["result"].suggestions,
                    },
                }
            else:
                result_dict = {
                    "file": result["file"],
                    "valid": result["valid"],
                    "error": result.get("error", "Unknown error"),
                }

            serializable_results.append(result_dict)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)

        console.print(f"✅ Batch results saved to: [bold]{output_path}[/bold]")

    except Exception as e:
        console.print(f"❌ Failed to save batch results: {e!s}")


# Command registry for CLI integration
WEB_INTELLIGENCE_COMMANDS = {
    "crawl": web_crawl_command,
    "search": web_search_command,
    "update": web_update_command,
    "sources": web_sources_command,
    "status": web_status_command,
    "validate": validate_script,
    "hallucinations": analyze_hallucinations,
    "validate-batch": validate_batch,
}


__all__ = [
    "WEB_INTELLIGENCE_COMMANDS",
    "web_crawl_command",
    "web_search_command",
    "web_sources_command",
    "web_status_command",
    "web_update_command",
]
