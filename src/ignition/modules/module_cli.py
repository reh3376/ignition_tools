"""CLI commands for Ignition Module development."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .cli.core_commands import core_group
from .module_builder import ModuleBuilder
from .module_generator import ModuleGenerator
from .sdk_manager import IgnitionSDKManager

console = Console()


def _initialize_module_systems():
    """Initialize the module development systems."""
    try:
        sdk_manager = IgnitionSDKManager()
        module_generator = ModuleGenerator(sdk_manager)
        module_builder = ModuleBuilder(sdk_manager)

        return sdk_manager, module_generator, module_builder
    except Exception as e:
        console.print(f"❌ Failed to initialize module systems: {e}")
        return None, None, None


@click.group(name="module")
def module_group() -> None:
    """Ignition Module development commands."""
    pass


# Add core framework commands as subgroup
module_group.add_command(core_group)


@module_group.command()
def status() -> None:
    """Show the status of the module development environment."""
    sdk_manager, _, _ = _initialize_module_systems()
    if not sdk_manager:
        return

    status = sdk_manager.get_environment_status()

    # Create status table
    table = Table(title="Module Development Environment Status")
    table.add_column("Component", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    # Workspace status
    workspace_status = "✅ Ready" if status["workspace_exists"] else "❌ Not found"
    table.add_row("Workspace", workspace_status, status["workspace_path"])

    # Tools status
    tools_status = (
        "✅ Ready"
        if status["tools_cloned"] and status["tools_built"]
        else "❌ Not ready"
    )
    tools_details = "Cloned and built" if status["tools_built"] else "Need setup"
    table.add_row("Module Tools", tools_status, tools_details)

    # Prerequisites
    prereqs = status["prerequisites"]
    java_status = "✅ Available" if prereqs.get("java", False) else "❌ Missing"
    java_details = prereqs.get("java_version", "Not found")
    table.add_row("Java/JDK", java_status, java_details)

    git_status = "✅ Available" if prereqs.get("git", False) else "❌ Missing"
    git_details = prereqs.get("git_version", "Not found")
    table.add_row("Git", git_status, git_details)

    gradle_status = (
        "✅ Available" if prereqs.get("gradle", False) else "⚠️ Using wrapper"
    )
    gradle_details = prereqs.get("gradle_version", "Will use wrapper")
    table.add_row("Gradle", gradle_status, gradle_details)

    # Projects
    project_count = len(status["projects"])
    project_status = f"📦 {project_count} projects"
    table.add_row("Projects", project_status, f"{project_count} module projects found")

    console.print(table)

    # Show projects if any exist
    if status["projects"]:
        console.print("\n📦 Module Projects:")
        for project in status["projects"]:
            project_status = "✅" if project["exists"] else "❌"
            console.print(
                f"  {project_status} {project['name']} ({project['build_file'] or 'no build file'})"
            )


@module_group.command()
@click.option("--force", is_flag=True, help="Force setup even if already exists")
def setup(force: bool) -> None:
    """Set up the module development environment."""
    sdk_manager, _, _ = _initialize_module_systems()
    if not sdk_manager:
        return

    console.print("🔧 Setting up Ignition Module development environment...")

    # Check prerequisites
    prereqs = sdk_manager.check_prerequisites()
    if not prereqs.get("java", False):
        console.print("❌ Java/JDK not found. Please install JDK 11+ first.")
        return

    if not prereqs.get("git", False):
        console.print("❌ Git not found. Please install Git first.")
        return

    # set up workspace
    console.print("📁 Setting up workspace...")
    if not sdk_manager.setup_workspace():
        console.print("❌ Failed to set up workspace")
        return

    # Clone module tools
    console.print("📥 Cloning module tools...")
    if not sdk_manager.clone_module_tools():
        console.print("❌ Failed to clone module tools")
        return

    # Build module tools
    console.print("🔨 Building module tools...")
    if not sdk_manager.build_module_tools():
        console.print("❌ Failed to build module tools")
        return

    console.print("✅ Module development environment setup complete!")
    console.print(f"Workspace: {sdk_manager.workspace_path}")


@module_group.command()
@click.argument("name")
@click.option(
    "--template",
    default="scripting-functions",
    help="Template to use (scripting-functions, vision-component, data-integration)",
)
@click.option("--package", default="com.ignscripts.modules", help="Root package name")
@click.option("--scopes", default="", help="Module scopes (G, C, D)")
@click.option("--description", default="", help="Module description")
def create(
    name: str, template: str, package: str, scopes: str, description: str
) -> None:
    """Create a new Ignition module project."""
    sdk_manager, generator, _ = _initialize_module_systems()
    if not sdk_manager or not generator:
        return

    # Check if environment is set up
    status = sdk_manager.get_environment_status()
    if not (status["tools_cloned"] and status["tools_built"]):
        console.print(
            "❌ Module development environment not set up. Run 'ign module setup' first."
        )
        return

    console.print(f"🚀 Creating module project: {name}")

    # Prepare requirements
    requirements = {
        "name": name,
        "package": package,
        "type": template,
        "description": description or f"Custom {template} module",
    }

    if scopes:
        requirements["scopes"] = scopes

    # Generate the module
    result = generator.generate_module(name, template, requirements)

    if result:
        console.print("✅ Module project created successfully!")
        console.print(f"📁 Path: {result.path}")
        console.print(f"🏗️ Template: {result.template.name}")
        console.print(f"📦 Scopes: {result.config.scopes}")

        # Show next steps
        console.print("\n📋 Next Steps:")
        console.print(f"  1. cd {result.path}")
        console.print(f"  2. ign module build {name}")
        console.print("  3. Install the .modl file in your Ignition gateway")
    else:
        console.print("❌ Failed to create module project")


@module_group.command()
@click.argument("project_name", required=False)
@click.option("--clean", is_flag=True, help="Clean before building")
@click.option("--all", is_flag=True, help="Build all projects")
def build(project_name: str | None, clean: bool, all: bool) -> None:
    """Build a module project."""
    sdk_manager, _, builder = _initialize_module_systems()
    if not sdk_manager or not builder:
        return

    if all:
        console.print("🔨 Building all module projects...")
        results = builder.build_all_projects()
        builder.display_build_summary(results)
        return

    if not project_name:
        console.print("❌ Project name required (or use --all)")
        return

    project_path = sdk_manager.workspace_path / project_name
    if not project_path.exists():
        console.print(f"❌ Project not found: {project_name}")
        return

    console.print(f"🔨 Building module project: {project_name}")
    result = builder.build_project(project_path, clean=clean)

    if result.success:
        console.print(f"✅ Build successful in {result.build_time:.1f}s")
        if result.module_file:
            console.print(f"📦 Module file: {result.module_file}")

        if result.warnings:
            console.print(f"⚠️ {len(result.warnings)} warnings:")
            for warning in result.warnings:
                console.print(f"  {warning}")
    else:
        console.print(f"❌ Build failed in {result.build_time:.1f}s")
        for error in result.errors:
            console.print(f"  Error: {error}")


@module_group.command()
@click.argument("project_name")
def clean(project_name: str) -> None:
    """Clean a module project."""
    sdk_manager, _, builder = _initialize_module_systems()
    if not sdk_manager or not builder:
        return

    project_path = sdk_manager.workspace_path / project_name
    if not project_path.exists():
        console.print(f"❌ Project not found: {project_name}")
        return

    console.print(f"🧹 Cleaning module project: {project_name}")
    success = builder.clean_project(project_path)

    if success:
        console.print("✅ Project cleaned successfully")
    else:
        console.print("❌ Failed to clean project")


@module_group.command()
@click.argument("project_name")
@click.option("--output", "-o", help="Output directory for packaged module")
def package(project_name: str, output: str | None) -> None:
    """Package a module for distribution."""
    sdk_manager, _, builder = _initialize_module_systems()
    if not sdk_manager or not builder:
        return

    project_path = sdk_manager.workspace_path / project_name
    if not project_path.exists():
        console.print(f"❌ Project not found: {project_name}")
        return

    output_dir = Path(output) if output else None

    console.print(f"📦 Packaging module: {project_name}")
    packaged_file = builder.package_module(project_path, output_dir)

    if packaged_file:
        console.print(f"✅ Module packaged successfully: {packaged_file}")

        # Validate the package
        validation = builder.validate_module(packaged_file)
        if validation["valid"]:
            console.print("✅ Package validation passed")
        else:
            console.print("⚠️ Package validation issues:")
            for error in validation["errors"]:
                console.print(f"  Error: {error}")
            for warning in validation["warnings"]:
                console.print(f"  Warning: {warning}")
    else:
        console.print("❌ Failed to package module")


@module_group.command()
@click.argument("module_file")
def validate(module_file: str) -> None:
    """Validate a module file."""
    _, _, builder = _initialize_module_systems()
    if not builder:
        return

    module_path = Path(module_file)
    if not module_path.exists():
        console.print(f"❌ Module file not found: {module_file}")
        return

    console.print(f"🔍 Validating module: {module_file}")
    validation = builder.validate_module(module_path)

    # Create validation table
    table = Table(title="Module Validation Results")
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    # File existence
    file_status = "✅ Exists" if validation["file_exists"] else "❌ Not found"
    table.add_row("File Exists", file_status, f"{validation['file_size']} bytes")

    # ZIP format
    zip_status = "✅ Valid ZIP" if validation["is_zip"] else "❌ Invalid ZIP"
    table.add_row("ZIP Format", zip_status, "Module files are ZIP archives")

    # Manifest
    manifest_status = "✅ Found" if validation["contains_manifest"] else "❌ Missing"
    table.add_row("Module Manifest", manifest_status, "module.xml file")

    # JAR files
    jar_status = "✅ Found" if validation["contains_jars"] else "⚠️ None found"
    table.add_row("JAR Files", jar_status, "Compiled module code")

    # Overall validation
    overall_status = "✅ Valid" if validation["valid"] else "❌ Invalid"
    table.add_row("Overall", overall_status, "Module validation result")

    console.print(table)

    # Show errors and warnings
    if validation["errors"]:
        console.print("\n❌ Errors:")
        for error in validation["errors"]:
            console.print(f"  {error}")

    if validation["warnings"]:
        console.print("\n⚠️ Warnings:")
        for warning in validation["warnings"]:
            console.print(f"  {warning}")


@module_group.command()
def list() -> None:
    """List module projects and templates."""
    sdk_manager, generator, _ = _initialize_module_systems()
    if not sdk_manager or not generator:
        return

    # list projects
    projects = sdk_manager.list_projects()
    if projects:
        console.print("📦 Module Projects:")
        for project_path in projects:
            info = sdk_manager.get_project_info(project_path)
            status = "✅" if info["exists"] else "❌"
            build_file = info.get("build_file", "unknown")
            console.print(f"  {status} {info['name']} ({build_file})")
    else:
        console.print("📦 No module projects found")

    # list templates
    templates = generator.list_templates()
    console.print(f"\n🎨 Available Templates ({len(templates)}):")
    for name, template in templates.items():
        console.print(f"  • {name}: {template.description}")
        console.print(
            f"    Scopes: {template.scopes}, Functions: {len(template.required_functions)}"
        )


@module_group.command()
@click.argument("template_name")
def template_info(template_name: str) -> None:
    """Show detailed information about a template."""
    _, generator, _ = _initialize_module_systems()
    if not generator:
        return

    template = generator.get_template_info(template_name)
    if not template:
        console.print(f"❌ Template not found: {template_name}")
        console.print(f"Available templates: {list(generator.list_templates().keys())}")
        return

    # Create template info table
    table = Table(title=f"Template: {template.name}")
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Name", template.name)
    table.add_row("Description", template.description)
    table.add_row("Scopes", template.scopes)
    table.add_row("Required Functions", str(len(template.required_functions)))
    table.add_row("Optional Functions", str(len(template.optional_functions)))
    table.add_row("Dependencies", str(len(template.dependencies)))

    console.print(table)

    # Show function lists
    if template.required_functions:
        console.print("\n🔧 Required Functions:")
        for func in template.required_functions:
            console.print(f"  • {func}")

    if template.optional_functions:
        console.print("\n⚙️ Optional Functions:")
        for func in template.optional_functions:
            console.print(f"  • {func}")

    if template.dependencies:
        console.print("\n📚 Dependencies:")
        for dep in template.dependencies:
            console.print(f"  • {dep}")


@module_group.command()
@click.argument("project_name")
def info(project_name: str) -> None:
    """Show detailed information about a module project."""
    sdk_manager, _, builder = _initialize_module_systems()
    if not sdk_manager or not builder:
        return

    project_path = sdk_manager.workspace_path / project_name
    if not project_path.exists():
        console.print(f"❌ Project not found: {project_name}")
        return

    # Get project and build info
    project_info = sdk_manager.get_project_info(project_path)
    build_info = builder.get_build_info(project_path)

    # Create info table
    table = Table(title=f"Project: {project_name}")
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Name", project_info["name"])
    table.add_row("Path", project_info["path"])
    table.add_row("Exists", "✅ Yes" if project_info["exists"] else "❌ No")
    table.add_row("Build File", project_info.get("build_file", "None"))

    if build_info["last_build"]:
        import datetime

        last_build = datetime.datetime.fromtimestamp(build_info["last_build"])
        table.add_row("Last Build", last_build.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        table.add_row("Last Build", "Never")

    table.add_row("Module Files", str(len(build_info["module_files"])))
    table.add_row("Build Artifacts", str(len(build_info["build_artifacts"])))

    console.print(table)

    # Show module files
    if build_info["module_files"]:
        console.print("\n📦 Module Files:")
        for module_file in build_info["module_files"]:
            console.print(f"  • {module_file}")

    # Show build artifacts
    if build_info["build_artifacts"]:
        console.print("\n🔨 Build Artifacts:")
        for artifact in build_info["build_artifacts"]:
            console.print(f"  • {artifact}")


# Export the command group
__all__ = ["module_group"]
