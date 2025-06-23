"""CLI Commands for Module Deployment & Distribution.

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Structured logging and progress tracking
- Rich CLI interface with proper feedback
"""

import os
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .deployment_manager import DeploymentConfig, DeploymentManager
from .module_packager import ModulePackager, PackagingConfig
from .module_signer import ModuleSigner, SigningConfig
from .repository_manager import RepositoryConfig, RepositoryManager

# Load environment variables
load_dotenv()

console = Console()


@click.group(name="deploy")
def deployment_cli():
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
):
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
):
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
):
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
):
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
):
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
):
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
):
    """List available modules in the repository."""
    try:
        console.print("📋 Listing repository modules...")

        # Create repository configuration
        config = RepositoryConfig()
        if repository_url:
            config.repository_url = repository_url

        # List modules
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
        console.print(f"❌ List error: {e!s}")


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
):
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
):
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
