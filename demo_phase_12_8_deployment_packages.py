#!/usr/bin/env python3
"""Demo Script for Phase 12.8: Deployment Package Creation & How-to Guides

This demo showcases the Phase 12.8 implementation following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Input validation and sanitization using Pydantic models
- Step 3: Comprehensive error handling with user-friendly messages
- Step 4: Modular testing integration
- Step 5: Progressive complexity
- Step 6: Resource management

Usage:
    python demo_phase_12_8_deployment_packages.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Import Phase 12.8 implementation
from src.phase_12_8_deployment_package_creation import (
    DeploymentPackageCreator,
    DeploymentTarget,
    DockerPackageConfig,
    PackageCreationRequest,
    PackageType,
    StandalonePackageConfig,
    create_docker_package,
    create_standalone_package,
    generate_comprehensive_guides,
    run_phase_12_8_implementation,
    validate_deployment_environment,
)

console = Console()


async def demo_environment_validation():
    """Demo: Environment validation following crawl_mcp.py methodology."""
    console.print(Panel(
        "[bold blue]Demo 1: Environment Validation[/bold blue]\n"
        "Following crawl_mcp.py Step 1: Environment validation first",
        title="🔍 Environment Validation",
        border_style="blue"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating deployment environment...", total=None)
        
        # Step 1: Environment validation first (crawl_mcp.py methodology)
        env_result = validate_deployment_environment()
        
        progress.update(task, completed=True)
    
    # Display results
    results_table = Table(title="Environment Validation Results")
    results_table.add_column("Component", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Details", style="white")
    
    results_table.add_row(
        "Overall Status",
        "✅ Valid" if env_result["valid"] else "❌ Invalid",
        f"Environment {'ready' if env_result['valid'] else 'needs setup'}"
    )
    
    results_table.add_row(
        "Tools Available",
        f"✅ {len(env_result['tools_available'])} found",
        ", ".join(env_result["tools_available"]) if env_result["tools_available"] else "None"
    )
    
    if env_result["errors"]:
        results_table.add_row(
            "Errors",
            f"❌ {len(env_result['errors'])} found",
            "; ".join(env_result["errors"][:2])  # Show first 2 errors
        )
    
    if env_result["warnings"]:
        results_table.add_row(
            "Warnings",
            f"⚠️ {len(env_result['warnings'])} found",
            "; ".join(env_result["warnings"][:2])  # Show first 2 warnings
        )
    
    console.print(results_table)
    
    return env_result


async def demo_input_validation():
    """Demo: Input validation using Pydantic models."""
    console.print(Panel(
        "[bold blue]Demo 2: Input Validation[/bold blue]\n"
        "Following crawl_mcp.py Step 2: Input validation using Pydantic models",
        title="✅ Input Validation",
        border_style="blue"
    ))
    
    # Demo valid configurations
    console.print("[bold green]✅ Valid Configurations:[/bold green]")
    
    # Docker configuration
    docker_config = DockerPackageConfig(
        image_name="ign-scripts-api",
        tag="1.0.0",
        expose_ports=[8000, 8501],
        environment_vars={
            "LOG_LEVEL": "INFO",
            "DEPLOYMENT_ENV": "production"
        }
    )
    console.print(f"Docker Config: {docker_config.image_name}:{docker_config.tag}")
    
    # Standalone configuration
    standalone_config = StandalonePackageConfig(
        service_name="ign-scripts",
        install_path="/opt/ign-scripts",
        user_account="ign-scripts"
    )
    console.print(f"Standalone Config: {standalone_config.service_name} -> {standalone_config.install_path}")
    
    # Package request
    request = PackageCreationRequest(
        package_type=PackageType.DOCKER,
        deployment_target=DeploymentTarget.PRODUCTION,
        version="1.0.0",
        docker_config=docker_config
    )
    console.print(f"Package Request: {request.package_type.value} for {request.deployment_target.value}")
    
    # Demo invalid configurations
    console.print("\n[bold red]❌ Invalid Configuration Examples:[/bold red]")
    
    try:
        DockerPackageConfig(image_name="invalid image name")
    except ValueError as e:
        console.print(f"Docker validation error: {e}")
    
    try:
        StandalonePackageConfig(install_path="relative/path")
    except ValueError as e:
        console.print(f"Standalone validation error: {e}")
    
    try:
        PackageCreationRequest(
            package_type=PackageType.DOCKER,
            deployment_target=DeploymentTarget.PRODUCTION,
            version="invalid.version.format.too.long"
        )
    except ValueError as e:
        console.print(f"Request validation error: {e}")
    
    return {"docker_config": docker_config, "standalone_config": standalone_config, "request": request}


async def demo_package_creation():
    """Demo: Package creation with error handling."""
    console.print(Panel(
        "[bold blue]Demo 3: Package Creation[/bold blue]\n"
        "Following crawl_mcp.py Steps 3-6: Error handling, modular testing, progressive complexity, resource management",
        title="📦 Package Creation",
        border_style="blue"
    ))
    
    results = []
    
    # Demo Docker package creation
    console.print("[bold cyan]Creating Docker Package...[/bold cyan]")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating Docker deployment package...", total=None)
            
            docker_result = await create_docker_package(
                image_name="ign-scripts-demo",
                version="1.0.0",
                deployment_target="development",
                output_dir="./demo_dist"
            )
            
            progress.update(task, completed=True)
        
        if docker_result.success:
            console.print(f"✅ Docker package created: {docker_result.package_path}")
            console.print(f"📊 Package size: {docker_result.package_size} bytes")
            results.append({"type": "docker", "success": True, "path": docker_result.package_path})
        else:
            console.print(f"❌ Docker package creation failed: {docker_result.error_message}")
            results.append({"type": "docker", "success": False, "error": docker_result.error_message})
    
    except Exception as e:
        console.print(f"❌ Docker package creation error: {e}")
        results.append({"type": "docker", "success": False, "error": str(e)})
    
    # Demo Standalone package creation
    console.print("\n[bold cyan]Creating Standalone Package...[/bold cyan]")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating standalone deployment package...", total=None)
            
            standalone_result = await create_standalone_package(
                version="1.0.0",
                deployment_target="development",
                output_dir="./demo_dist"
            )
            
            progress.update(task, completed=True)
        
        if standalone_result.success:
            console.print(f"✅ Standalone package created: {standalone_result.package_path}")
            console.print(f"📊 Package size: {standalone_result.package_size} bytes")
            results.append({"type": "standalone", "success": True, "path": standalone_result.package_path})
        else:
            console.print(f"❌ Standalone package creation failed: {standalone_result.error_message}")
            results.append({"type": "standalone", "success": False, "error": standalone_result.error_message})
    
    except Exception as e:
        console.print(f"❌ Standalone package creation error: {e}")
        results.append({"type": "standalone", "success": False, "error": str(e)})
    
    return results


async def demo_how_to_guides_generation():
    """Demo: How-to guides generation."""
    console.print(Panel(
        "[bold blue]Demo 4: How-to Guides Generation[/bold blue]\n"
        "Creating comprehensive documentation following best practices",
        title="📚 Documentation Generation",
        border_style="blue"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating comprehensive how-to guides...", total=None)
        
        guides_result = await generate_comprehensive_guides()
        
        progress.update(task, completed=True)
    
    if guides_result["success"]:
        console.print(f"✅ Generated {len(guides_result['guides'])} how-to guides:")
        for guide in guides_result["guides"]:
            console.print(f"  📄 {guide}")
            
        # Check if guides were actually created
        guides_dir = Path("docs/how-to")
        if guides_dir.exists():
            console.print(f"\n📁 Guides directory: {guides_dir}")
            for guide_file in guides_dir.glob("*.md"):
                file_size = guide_file.stat().st_size
                console.print(f"  📄 {guide_file.name} ({file_size} bytes)")
    else:
        console.print(f"❌ Guide generation failed:")
        for error in guides_result["errors"]:
            console.print(f"  ❌ {error}")
    
    return guides_result


async def demo_full_implementation():
    """Demo: Full Phase 12.8 implementation."""
    console.print(Panel(
        "[bold blue]Demo 5: Full Phase 12.8 Implementation[/bold blue]\n"
        "Complete deployment package creation and how-to guides system",
        title="🚀 Full Implementation",
        border_style="blue"
    ))
    
    start_time = datetime.now()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running complete Phase 12.8 implementation...", total=None)
        
        implementation_result = await run_phase_12_8_implementation()
        
        progress.update(task, completed=True)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Display comprehensive results
    results_table = Table(title="Phase 12.8 Implementation Results")
    results_table.add_column("Component", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Details", style="white")
    
    results_table.add_row(
        "Overall Status",
        "✅ Success" if implementation_result["success"] else "❌ Failed",
        f"Phase {implementation_result['phase']} completed"
    )
    
    results_table.add_row(
        "Environment Validation",
        "✅ Passed" if implementation_result["steps"].get("environment_validation", {}).get("valid") else "❌ Failed",
        f"Tools available: {len(implementation_result['steps'].get('environment_validation', {}).get('tools_available', []))}"
    )
    
    results_table.add_row(
        "Packages Created",
        f"📦 {len(implementation_result['packages_created'])}",
        ", ".join([p["type"] for p in implementation_result["packages_created"]])
    )
    
    results_table.add_row(
        "Documentation",
        f"📚 {len(implementation_result['documentation_generated'])} guides",
        ", ".join(implementation_result["documentation_generated"][:3])  # Show first 3
    )
    
    results_table.add_row(
        "Execution Time",
        f"⏱️ {duration:.2f}s",
        f"Started: {start_time.strftime('%H:%M:%S')}"
    )
    
    if implementation_result["errors"]:
        results_table.add_row(
            "Errors",
            f"❌ {len(implementation_result['errors'])}",
            "; ".join(implementation_result["errors"][:2])
        )
    
    if implementation_result["warnings"]:
        results_table.add_row(
            "Warnings",
            f"⚠️ {len(implementation_result['warnings'])}",
            "; ".join(implementation_result["warnings"][:2])
        )
    
    console.print(results_table)
    
    return implementation_result


async def main():
    """Main demo function."""
    console.print(Panel(
        "[bold green]🚀 Phase 12.8: Deployment Package Creation & How-to Guides Demo[/bold green]\n"
        "Following crawl_mcp.py methodology with comprehensive validation and testing",
        title="Demo Start",
        border_style="green"
    ))
    
    demo_results = {
        "start_time": datetime.now().isoformat(),
        "demos": {},
        "success": True,
        "errors": []
    }
    
    try:
        # Demo 1: Environment Validation
        console.print("\n" + "="*80)
        env_result = await demo_environment_validation()
        demo_results["demos"]["environment_validation"] = env_result
        
        # Demo 2: Input Validation
        console.print("\n" + "="*80)
        validation_result = await demo_input_validation()
        demo_results["demos"]["input_validation"] = validation_result
        
        # Demo 3: Package Creation
        console.print("\n" + "="*80)
        package_result = await demo_package_creation()
        demo_results["demos"]["package_creation"] = package_result
        
        # Demo 4: How-to Guides Generation
        console.print("\n" + "="*80)
        guides_result = await demo_how_to_guides_generation()
        demo_results["demos"]["guides_generation"] = guides_result
        
        # Demo 5: Full Implementation
        console.print("\n" + "="*80)
        implementation_result = await demo_full_implementation()
        demo_results["demos"]["full_implementation"] = implementation_result
        
        # Final summary
        demo_results["end_time"] = datetime.now().isoformat()
        demo_results["success"] = implementation_result.get("success", False)
        
        console.print("\n" + "="*80)
        console.print(Panel(
            f"[bold green]✅ Demo Completed Successfully![/bold green]\n\n"
            f"🔍 Environment Validation: {'✅ Passed' if env_result['valid'] else '❌ Failed'}\n"
            f"✅ Input Validation: ✅ Demonstrated\n"
            f"📦 Package Creation: {len([p for p in package_result if p['success']])}/{len(package_result)} successful\n"
            f"📚 Guides Generation: {'✅ Success' if guides_result['success'] else '❌ Failed'}\n"
            f"🚀 Full Implementation: {'✅ Success' if implementation_result['success'] else '❌ Failed'}\n"
            f"⏱️ Total Demo Time: {(datetime.fromisoformat(demo_results['end_time']) - datetime.fromisoformat(demo_results['start_time'])).total_seconds():.2f}s",
            title="🎉 Demo Summary",
            border_style="green"
        ))
        
        # Save demo results
        results_file = Path("demo_phase_12_8_results.json")
        with open(results_file, 'w') as f:
            json.dump(demo_results, f, indent=2, default=str)
        
        console.print(f"\n📄 Demo results saved to: {results_file}")
        
    except Exception as e:
        demo_results["success"] = False
        demo_results["errors"].append(str(e))
        demo_results["end_time"] = datetime.now().isoformat()
        
        console.print(Panel(
            f"[bold red]❌ Demo Failed[/bold red]\n\n"
            f"Error: {e}",
            title="💥 Demo Failure",
            border_style="red"
        ))
        
        return 1
    
    return 0


if __name__ == "__main__":
    # Run the demo
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 