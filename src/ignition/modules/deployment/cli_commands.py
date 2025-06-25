"""CLI Commands for Module Deployment & Distribution.

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Structured logging and progress tracking
- Rich CLI interface with proper feedback
"""

import os
import platform
import subprocess
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from .deployment_manager import DeploymentConfig, DeploymentManager
from .module_packager import ModulePackager, PackagingConfig
from .module_signer import ModuleSigner, SigningConfig
from .repository_manager import RepositoryConfig, RepositoryManager

# Load environment variables
load_dotenv()

console = Console()


@click.group(name="deploy")
def deployment_cli() -> None:
    """Module Deployment & Distribution commands."""
    pass


@deployment_cli.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--version",
    "-v",
    help="Module version (auto-detected if not specified)",
)
@click.option(
    "--environment",
    "-e",
    default=lambda: os.getenv("DEPLOYMENT_ENVIRONMENT", "development"),
    help="Deployment environment",
)
@click.option(
    "--skip-packaging",
    is_flag=True,
    help="Skip module packaging step",
)
@click.option(
    "--skip-signing",
    is_flag=True,
    help="Skip module signing step",
)
@click.option(
    "--skip-upload",
    is_flag=True,
    help="Skip repository upload step",
)
@click.option(
    "--notes",
    help="Deployment notes",
)
@click.option(
    "--tags",
    help="Deployment tags (comma-separated)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without actual deployment",
)
def module(
    project_path: Path,
    version: str | None,
    environment: str,
    skip_packaging: bool,
    skip_signing: bool,
    skip_upload: bool,
    notes: str | None,
    tags: str | None,
    dry_run: bool,
) -> None:
    """Deploy a single module through the complete workflow."""
    try:
        console.print(f"🚀 Starting module deployment: {project_path.name}")

        if dry_run:
            console.print("🔍 Dry run mode - no actual deployment will occur")

        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]

        # Create deployment configuration
        config = DeploymentConfig(
            enable_packaging=not skip_packaging,
            enable_signing=not skip_signing,
            enable_repository_upload=not skip_upload,
            deployment_environment=environment,
            deployment_notes=notes or "",
            deployment_tags=tag_list,
        )

        # Validate environment before deployment
        manager = DeploymentManager(config)
        env_validation = manager.validate_environment()

        # Display environment validation
        _display_environment_validation(env_validation)

        # Check for critical issues
        critical_issues = [
            k for k, v in env_validation.items() if not v and "critical" in k.lower()
        ]
        if critical_issues and not dry_run:
            console.print(
                "❌ Critical environment issues detected. Cannot proceed with deployment."
            )
            return

        if dry_run:
            console.print("✅ Dry run completed. Environment validation shown above.")
            return

        # Perform deployment
        result = manager.deploy_module(project_path, version)

        if result.success:
            console.print("🎉 Module deployment completed successfully!")
            console.print(f"📋 Deployment ID: {result.deployment_id}")

            # Display artifacts
            if result.artifacts:
                console.print("\n📦 Generated artifacts:")
                for artifact in result.artifacts:
                    console.print(f"  • {artifact}")

        else:
            console.print("❌ Module deployment failed!")
            for error in result.errors:
                console.print(f"  Error: {error}")

            if result.warnings:
                console.print("\nWarnings:")
                for warning in result.warnings:
                    console.print(f"  Warning: {warning}")

    except Exception as e:
        console.print(f"❌ Deployment error: {e!s}")


@deployment_cli.command()
@click.argument("project_paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--environment",
    "-e",
    default=lambda: os.getenv("DEPLOYMENT_ENVIRONMENT", "development"),
    help="Deployment environment",
)
@click.option(
    "--skip-packaging",
    is_flag=True,
    help="Skip module packaging step",
)
@click.option(
    "--skip-signing",
    is_flag=True,
    help="Skip module signing step",
)
@click.option(
    "--skip-upload",
    is_flag=True,
    help="Skip repository upload step",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    help="Continue batch deployment even if individual modules fail",
)
def batch(
    project_paths: tuple[Path, ...],
    environment: str,
    skip_packaging: bool,
    skip_signing: bool,
    skip_upload: bool,
    continue_on_error: bool,
) -> None:
    """Deploy multiple modules in batch."""
    try:
        if not project_paths:
            console.print("❌ No project paths specified")
            return

        console.print(f"🚀 Starting batch deployment: {len(project_paths)} modules")

        # Create deployment configuration
        config = DeploymentConfig(
            enable_packaging=not skip_packaging,
            enable_signing=not skip_signing,
            enable_repository_upload=not skip_upload,
            deployment_environment=environment,
        )

        # Perform batch deployment
        manager = DeploymentManager(config)
        results = manager.deploy_multiple_modules(list(project_paths))

        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        console.print("\n📊 Batch deployment summary:")
        console.print(f"  • Total: {len(results)}")
        console.print(f"  • Successful: {successful}")
        console.print(f"  • Failed: {failed}")
        console.print(f"  • Success rate: {(successful / len(results) * 100):.1f}%")

        if failed > 0 and not continue_on_error:
            console.print(
                "❌ Some deployments failed. Use --continue-on-error to ignore failures."
            )

    except Exception as e:
        console.print(f"❌ Batch deployment error: {e!s}")


@deployment_cli.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for packaged module",
)
@click.option(
    "--gradle-args",
    help="Additional Gradle arguments",
)
def package(
    project_path: Path,
    output_dir: Path | None,
    gradle_args: str | None,
) -> None:
    """Package a module for distribution."""
    try:
        console.print(f"📦 Packaging module: {project_path.name}")

        # Create packaging configuration
        config = PackagingConfig()
        if output_dir:
            config.output_directory = output_dir
        if gradle_args:
            config.gradle_args.extend(gradle_args.split())

        # Package module
        packager = ModulePackager(config)
        result = packager.package_module(project_path)

        if result.success:
            console.print("✅ Module packaged successfully!")
            if result.package_file:
                console.print(f"📦 Package: {result.package_file}")
            if result.module_file:
                console.print(f"🔧 Module: {result.module_file}")
        else:
            console.print("❌ Packaging failed!")
            for error in result.errors:
                console.print(f"  Error: {error}")

    except Exception as e:
        console.print(f"❌ Packaging error: {e!s}")


@deployment_cli.command()
@click.argument("module_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--cert-path",
    help="Path to signing certificate",
)
@click.option(
    "--key-path",
    help="Path to private key",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for signed module",
)
def sign(
    module_file: Path,
    cert_path: str | None,
    key_path: str | None,
    output_dir: Path | None,
) -> None:
    """Sign a module for secure distribution."""
    try:
        console.print(f"🔐 Signing module: {module_file.name}")

        # Create signing configuration
        config = SigningConfig()
        if cert_path:
            config.certificate_path = cert_path
        if key_path:
            config.private_key_path = key_path
        if output_dir:
            config.output_directory = output_dir

        # Sign module
        signer = ModuleSigner(config)
        result = signer.sign_module(module_file)

        if result.success:
            console.print("✅ Module signed successfully!")
            if result.signed_file:
                console.print(f"🔐 Signed module: {result.signed_file}")
            if result.signature_file:
                console.print(f"📝 Signature: {result.signature_file}")

            # Display certificate info
            if result.certificate_info:
                console.print("\n📋 Certificate information:")
                for key, value in result.certificate_info.items():
                    if key != "error":
                        console.print(f"  • {key}: {value}")
        else:
            console.print("❌ Signing failed!")
            for error in result.errors:
                console.print(f"  Error: {error}")

    except Exception as e:
        console.print(f"❌ Signing error: {e!s}")


@deployment_cli.command()
@click.argument("package_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--version",
    "-v",
    help="Module version",
)
@click.option(
    "--description",
    "-d",
    help="Module description",
)
@click.option(
    "--repository-url",
    help="Repository URL (overrides environment variable)",
)
def upload(
    package_file: Path,
    version: str | None,
    description: str | None,
    repository_url: str | None,
) -> None:
    """Upload a module package to the repository."""
    try:
        console.print(f"📤 Uploading module: {package_file.name}")

        # Create repository configuration
        config = RepositoryConfig()
        if repository_url:
            config.repository_url = repository_url

        # Prepare metadata
        metadata = {}
        if version:
            metadata["version"] = version
        if description:
            metadata["description"] = description

        # Upload module
        repository = RepositoryManager(config)
        result = repository.upload_module(package_file, metadata)

        if result.success:
            console.print("✅ Module uploaded successfully!")
            if result.module_info:
                console.print("📋 Module info:")
                for key, value in result.module_info.items():
                    console.print(f"  • {key}: {value}")
        else:
            console.print("❌ Upload failed!")
            for error in result.errors:
                console.print(f"  Error: {error}")

    except Exception as e:
        console.print(f"❌ Upload error: {e!s}")


@deployment_cli.command()
@click.argument("module_name")
@click.option(
    "--version",
    "-v",
    help="Specific version to download (latest if not specified)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for downloaded module",
)
@click.option(
    "--repository-url",
    help="Repository URL (overrides environment variable)",
)
def download(
    module_name: str,
    version: str | None,
    output_dir: Path | None,
    repository_url: str | None,
) -> None:
    """Download a module from the repository."""
    try:
        console.print(f"📥 Downloading module: {module_name}")

        # Create repository configuration
        config = RepositoryConfig()
        if repository_url:
            config.repository_url = repository_url
        if output_dir:
            config.download_directory = output_dir

        # Download module
        repository = RepositoryManager(config)
        result = repository.download_module(module_name, version)

        if result.success:
            console.print("✅ Module downloaded successfully!")
            if result.file_path:
                console.print(f"📦 Downloaded to: {result.file_path}")
            if result.module_info:
                console.print("📋 Module info:")
                for key, value in result.module_info.items():
                    console.print(f"  • {key}: {value}")
        else:
            console.print("❌ Download failed!")
            for error in result.errors:
                console.print(f"  Error: {error}")

    except Exception as e:
        console.print(f"❌ Download error: {e!s}")


@deployment_cli.command()
@click.option(
    "--search",
    "-s",
    help="Search query to filter modules",
)
@click.option(
    "--repository-url",
    help="Repository URL (overrides environment variable)",
)
def list_modules(
    search: str | None,
    repository_url: str | None,
) -> None:
    """List available modules in the repository."""
    try:
        console.print("📋 Listing repository modules...")

        # Create repository configuration
        config = RepositoryConfig()
        if repository_url:
            config.repository_url = repository_url

        # list modules
        repository = RepositoryManager(config)
        result = repository.list_modules(search)

        if result.success:
            modules = result.module_info.get("modules", [])

            if not modules:
                console.print("📭 No modules found")
                return

            # Display modules in table
            table = Table(title="Available Modules")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Description", style="white")
            table.add_column("Updated", style="yellow")

            for module in modules:
                table.add_row(
                    module.get("name", ""),
                    module.get("version", ""),
                    (
                        module.get("description", "")[:50] + "..."
                        if len(module.get("description", "")) > 50
                        else module.get("description", "")
                    ),
                    module.get("updated_at", ""),
                )

            console.print(table)
            console.print(f"\n📊 Total modules: {len(modules)}")

        else:
            console.print("❌ Failed to list modules!")
            for error in result.errors:
                console.print(f"  Error: {error}")

    except Exception as e:
        console.print(f"❌ list error: {e!s}")


@deployment_cli.command()
@click.option(
    "--packaging",
    is_flag=True,
    help="Validate packaging environment",
)
@click.option(
    "--signing",
    is_flag=True,
    help="Validate signing environment",
)
@click.option(
    "--repository",
    is_flag=True,
    help="Validate repository environment",
)
def validate_env(
    packaging: bool,
    signing: bool,
    repository: bool,
) -> None:
    """Validate deployment environment and configuration."""
    try:
        console.print("🔍 Validating deployment environment...")

        # If no specific flags, validate all
        if not any([packaging, signing, repository]):
            packaging = signing = repository = True

        # Create managers and validate
        validation_results = {}

        if packaging:
            packager = ModulePackager()
            validation_results["packaging"] = packager.validate_environment()

        if signing:
            signer = ModuleSigner()
            validation_results["signing"] = signer.validate_environment()

        if repository:
            repo_manager = RepositoryManager()
            validation_results["repository"] = repo_manager.validate_environment()

        # Display results
        for component, results in validation_results.items():
            _display_environment_validation(results, component.title())

    except Exception as e:
        console.print(f"❌ Validation error: {e!s}")


def _display_environment_validation(
    validation_results: dict, title: str = "Environment Validation"
) -> None:
    """Display environment validation results in a table."""
    table = Table(title=title)
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    for check, status in validation_results.items():
        status_icon = "✅" if status else "❌"
        status_text = "PASS" if status else "FAIL"

        # Format check name
        check_display = check.replace("_", " ").title()

        table.add_row(
            check_display,
            f"{status_icon} {status_text}",
            f"{'Required' if not status else 'Available'}",
        )

    console.print(table)


@deployment_cli.command("setup-environment")
@click.option(
    "--interactive/--non-interactive", default=True, help="Run in interactive mode"
)
@click.option(
    "--force", is_flag=True, help="Force setup even if environment appears configured"
)
@click.option(
    "--report-only", is_flag=True, help="Generate report without making changes"
)
def setup_environment(interactive: bool, force: bool, report_only: bool) -> None:
    """Set up Phase 9.7 development environment following crawl_mcp.py methodology.

    This command follows the systematic approach from crawl_mcp.py:
    1. Environment Variable Validation First
    2. Comprehensive Input Validation
    3. Error Handling with User-Friendly Messages
    4. Modular Component Testing
    5. Progressive Complexity
    6. Resource Management
    """
    from .environment_setup import Phase97EnvironmentSetup

    console.print(
        Panel.fit(
            "Phase 9.7 Environment Setup\nFollowing crawl_mcp.py methodology",
            title="🚀 IGN Scripts - Environment Setup",
            border_style="blue",
        )
    )

    try:
        setup = Phase97EnvironmentSetup()

        # Step 1: Environment Variable Validation First
        console.print("\n🔍 Step 1: Environment Variable Validation", style="bold blue")
        env_results = setup.validate_environment_variables()

        # Step 2: System Requirements Validation
        console.print("\n🔍 Step 2: System Requirements Validation", style="bold blue")
        sys_results = setup.check_system_requirements()

        # Check if we should proceed with setup
        env_score = setup._calculate_environment_score(env_results)
        sys_score = setup._calculate_system_score(sys_results)

        if report_only:
            console.print("\n📊 Generating environment report only...", style="yellow")
            report = setup.generate_setup_report()

            # Save report
            import json

            report_file = "phase_97_environment_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, default=str)

            console.print(f"📄 Environment report saved to: {report_file}")
            return

        # Check if setup is needed
        if env_score >= 80 and sys_score >= 80 and not force:
            console.print(
                "✅ Environment appears to be already configured!", style="green"
            )
            if interactive:
                proceed = Confirm.ask("Run setup anyway?", default=False)
                if not proceed:
                    console.print("Environment setup skipped.")
                    return

        # Step 3: Development Environment Setup (Progressive Complexity)
        if env_score < 80 or sys_score < 80 or force:
            console.print(
                "\n🔧 Step 3: Development Environment Setup", style="bold blue"
            )
            setup_results = setup.setup_development_environment(interactive=interactive)

        # Step 4: Generate Final Report
        console.print("\n📊 Step 4: Final Validation and Report", style="bold blue")
        final_report = setup.generate_setup_report()

        # Save comprehensive report
        import json

        report_file = "phase_97_environment_setup_complete.json"
        with open(report_file, "w") as f:
            json.dump(final_report, f, indent=2, default=str)

        console.print(f"\n📄 Complete setup report saved to: {report_file}")

        # Display next steps
        if final_report["overall_score"] >= 80:
            console.print(
                "\n🎉 Environment setup complete! Ready for Phase 9.7 deployment.",
                style="bold green",
            )
            console.print("Next steps:")
            console.print("  • Run: ign deploy validate-env")
            console.print("  • Test: ign deploy package --help")
        else:
            console.print(
                "\n⚠️ Environment setup incomplete. Review recommendations above.",
                style="yellow",
            )

    except Exception as e:
        console.print(f"❌ Environment setup failed: {e}", style="red")
        console.print("Check the error details and try again.")
        raise click.Exit(1)


@deployment_cli.command("check-environment")
@click.option("--detailed", is_flag=True, help="Show detailed validation results")
@click.option(
    "--suggestions/--no-suggestions", default=True, help="Show fix suggestions"
)
def check_environment(detailed: bool, suggestions: bool) -> None:
    """Check Phase 9.7 environment configuration following crawl_mcp.py validation patterns.

    This command performs comprehensive environment validation without making changes.
    """
    from .environment_setup import Phase97EnvironmentSetup

    console.print("🔍 Checking Phase 9.7 Environment Configuration", style="bold blue")

    try:
        setup = Phase97EnvironmentSetup()

        # Validate environment variables
        env_results = setup.validate_environment_variables()

        # Check system requirements
        sys_results = setup.check_system_requirements()

        # Calculate scores
        env_score = setup._calculate_environment_score(env_results)
        sys_score = setup._calculate_system_score(sys_results)
        overall_score = (env_score + sys_score) / 2

        # Display summary
        table = Table(title="Environment Status Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Score", justify="center")
        table.add_column("Status", justify="center")

        table.add_row(
            "Environment Variables",
            f"{env_score:.1f}/100",
            (
                "✅ Ready"
                if env_score >= 80
                else "⚠️ Partial" if env_score >= 50 else "❌ Needs Setup"
            ),
        )
        table.add_row(
            "System Requirements",
            f"{sys_score:.1f}/100",
            (
                "✅ Ready"
                if sys_score >= 80
                else "⚠️ Partial" if sys_score >= 50 else "❌ Needs Setup"
            ),
        )
        table.add_row(
            "Overall",
            f"{overall_score:.1f}/100",
            (
                "✅ Ready"
                if overall_score >= 80
                else "⚠️ Partial" if overall_score >= 50 else "❌ Needs Setup"
            ),
        )

        console.print(table)

        # Show detailed results if requested
        if detailed:
            console.print("\n📋 Detailed Environment Variable Results:", style="bold")
            for env_var, result in env_results.items():
                status = "✅" if result.valid else "❌"
                req = next(
                    (r for r in setup.requirements if r.env_var == env_var), None
                )
                name = req.name if req else env_var
                console.print(
                    f"  {status} {name}: {setup._format_validation_message(result)}"
                )

            console.print("\n🔧 System Requirements Results:", style="bold")
            for component, result in sys_results.items():
                status = "✅" if result.valid else "❌"
                console.print(
                    f"  {status} {component.title()}: {setup._format_validation_message(result)}"
                )

        # Show suggestions if requested
        if suggestions and overall_score < 80:
            recommendations = setup._generate_setup_recommendations(
                env_results, sys_results
            )
            console.print("\n💡 Recommendations:", style="bold yellow")
            for rec in recommendations:
                console.print(f"  {rec}")

            next_steps = setup._generate_next_steps(env_results, sys_results)
            console.print("\n🎯 Next Steps:", style="bold green")
            for step in next_steps:
                console.print(f"  • {step}")

            console.print(
                "\n🔧 To fix issues automatically, run: [bold]ign deploy setup-environment[/bold]"
            )

        # set exit code based on results
        if overall_score < 50:
            console.print("\n❌ Environment needs significant setup.", style="red")
            raise click.Exit(1)
        elif overall_score < 80:
            console.print("\n⚠️ Environment partially configured.", style="yellow")
        else:
            console.print(
                "\n✅ Environment ready for Phase 9.7 deployment!", style="green"
            )

    except Exception as e:
        console.print(f"❌ Environment check failed: {e}", style="red")
        raise click.Exit(1)


@deployment_cli.command("install-requirements")
@click.option("--java", is_flag=True, help="Install Java (macOS with Homebrew)")
@click.option("--gradle", is_flag=True, help="Install Gradle (macOS with Homebrew)")
@click.option("--all", is_flag=True, help="Install all available tools")
@click.option("--dry-run", is_flag=True, help="Show commands without executing")
def install_requirements(java: bool, gradle: bool, all: bool, dry_run: bool) -> None:
    """Install system requirements for Phase 9.7 deployment (macOS with Homebrew).

    This command helps install Java and Gradle on macOS systems using Homebrew.
    For other platforms, manual installation instructions are provided.
    """
    console.print("🔧 Phase 9.7 System Requirements Installation", style="bold blue")

    # Check platform
    if platform.system() != "Darwin" and not dry_run:
        console.print(
            "❌ Automated installation only supported on macOS with Homebrew.",
            style="red",
        )
        console.print("\nManual installation instructions:")
        console.print("• Java 11+: https://adoptium.net/")
        console.print("• Gradle 7+: https://gradle.org/install/")
        return

    # Check if Homebrew is available
    if not dry_run:
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            console.print(
                "❌ Homebrew not found. Please install Homebrew first:", style="red"
            )
            console.print("https://brew.sh/")
            raise click.Exit(1)

    commands = []

    if java or all:
        commands.extend(
            [
                "brew install openjdk@11",
                "sudo ln -sfn $(brew --prefix)/opt/openjdk@11/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-11.jdk",
            ]
        )

    if gradle or all:
        commands.append("brew install gradle")

    if not commands:
        console.print(
            "❌ No installation options selected. Use --java, --gradle, or --all",
            style="red",
        )
        raise click.Exit(1)

    if dry_run:
        console.print("🔍 Commands that would be executed:", style="yellow")
        for cmd in commands:
            console.print(f"  {cmd}")
        return

    # Execute commands
    console.print("📦 Installing system requirements...", style="blue")

    for cmd in commands:
        console.print(f"Running: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                console.print("  ✅ Success", style="green")
            else:
                console.print(f"  ❌ Failed: {result.stderr}", style="red")
        except Exception as e:
            console.print(f"  ❌ Error: {e}", style="red")

    console.print("\n🔍 Verifying installation...")

    # Verify Java
    if java or all:
        try:
            result = subprocess.run(
                ["java", "-version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                console.print("  ✅ Java installed successfully", style="green")
                console.print("    set JAVA_HOME=$(brew --prefix)/opt/openjdk@11")
            else:
                console.print("  ❌ Java installation verification failed", style="red")
        except FileNotFoundError:
            console.print("  ❌ Java not found after installation", style="red")

    # Verify Gradle
    if gradle or all:
        try:
            result = subprocess.run(
                ["gradle", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                console.print("  ✅ Gradle installed successfully", style="green")
            else:
                console.print(
                    "  ❌ Gradle installation verification failed", style="red"
                )
        except FileNotFoundError:
            console.print("  ❌ Gradle not found after installation", style="red")

    console.print("\n🎯 Next steps:")
    console.print("  • set environment variables (JAVA_HOME, GRADLE_HOME)")
    console.print("  • Run: ign deploy setup-environment")
    console.print("  • Verify: ign deploy check-environment")
