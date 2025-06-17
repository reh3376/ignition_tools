"""Ignition SDK Manager for development environment setup and management."""

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console()


@dataclass
class SDKEnvironment:
    """Configuration for Ignition SDK development environment."""
    
    jdk_version: str = "11"
    gradle_version: str = "8.5"
    ignition_version: str = "8.1.44"
    sdk_version: str = "8.1.44"
    tools_repo_url: str = "https://github.com/inductiveautomation/ignition-module-tools"
    workspace_path: Path = Path("ignition-modules")
    

@dataclass
class ModuleProjectConfig:
    """Configuration for a new Ignition module project."""
    
    name: str
    scopes: str = "GCD"  # Gateway, Client, Designer
    root_package: str = "com.ignscripts.modules"
    language: str = "kotlin"
    description: str = ""
    min_ignition_version: str = "8.1.0"
    

class IgnitionSDKManager:
    """Manager for Ignition Module SDK development environment."""
    
    def __init__(self, workspace_path: Optional[Path] = None):
        """Initialize the SDK manager.
        
        Args:
            workspace_path: Path to the SDK workspace directory
        """
        self.workspace_path = workspace_path or Path.cwd() / "ignition-modules"
        self.tools_path = self.workspace_path / "ignition-module-tools"
        self.environment = SDKEnvironment(workspace_path=self.workspace_path)
        
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are installed.
        
        Returns:
            Dictionary mapping prerequisite names to availability status
        """
        prerequisites = {}
        
        # Check Java/JDK
        try:
            result = subprocess.run(
                ["java", "-version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            prerequisites["java"] = result.returncode == 0
            if prerequisites["java"]:
                # Extract version info
                version_line = result.stderr.split('\n')[0]
                prerequisites["java_version"] = version_line
        except (subprocess.TimeoutExpired, FileNotFoundError):
            prerequisites["java"] = False
            prerequisites["java_version"] = "Not found"
            
        # Check Git
        try:
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            prerequisites["git"] = result.returncode == 0
            if prerequisites["git"]:
                prerequisites["git_version"] = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            prerequisites["git"] = False
            prerequisites["git_version"] = "Not found"
            
        # Check Gradle (optional - can use wrapper)
        try:
            result = subprocess.run(
                ["gradle", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            prerequisites["gradle"] = result.returncode == 0
            if prerequisites["gradle"]:
                version_lines = result.stdout.split('\n')
                for line in version_lines:
                    if line.startswith("Gradle"):
                        prerequisites["gradle_version"] = line
                        break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            prerequisites["gradle"] = False
            prerequisites["gradle_version"] = "Not found (will use wrapper)"
            
        return prerequisites
        
    def setup_workspace(self) -> bool:
        """Set up the SDK workspace directory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            console.print(f"✅ Created workspace directory: {self.workspace_path}")
            return True
        except Exception as e:
            console.print(f"❌ Failed to create workspace: {e}")
            return False
            
    def clone_module_tools(self) -> bool:
        """Clone the Ignition module tools repository.
        
        Returns:
            True if successful, False otherwise
        """
        if self.tools_path.exists():
            console.print(f"📁 Module tools already exist at: {self.tools_path}")
            return True
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Cloning module tools repository...", total=None)
                
                result = subprocess.run([
                    "git", "clone", 
                    self.environment.tools_repo_url,
                    str(self.tools_path)
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    console.print(f"✅ Cloned module tools to: {self.tools_path}")
                    return True
                else:
                    console.print(f"❌ Failed to clone module tools: {result.stderr}")
                    return False
                    
        except subprocess.TimeoutExpired:
            console.print("❌ Timeout while cloning module tools repository")
            return False
        except Exception as e:
            console.print(f"❌ Error cloning module tools: {e}")
            return False
            
    def build_module_tools(self) -> bool:
        """Build the module tools generator.
        
        Returns:
            True if successful, False otherwise
        """
        generator_path = self.tools_path / "generator"
        if not generator_path.exists():
            console.print("❌ Generator directory not found in module tools")
            return False
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Building module tools...", total=None)
                
                # Use gradlew wrapper
                gradlew_cmd = "./gradlew" if os.name != 'nt' else "gradlew.bat"
                
                result = subprocess.run([
                    gradlew_cmd, "clean", "build"
                ], cwd=generator_path, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    console.print("✅ Successfully built module tools")
                    return True
                else:
                    console.print(f"❌ Failed to build module tools: {result.stderr}")
                    return False
                    
        except subprocess.TimeoutExpired:
            console.print("❌ Timeout while building module tools")
            return False
        except Exception as e:
            console.print(f"❌ Error building module tools: {e}")
            return False
            
    def create_module_project(self, config: ModuleProjectConfig) -> bool:
        """Create a new Ignition module project.
        
        Args:
            config: Configuration for the new module project
            
        Returns:
            True if successful, False otherwise
        """
        generator_path = self.tools_path / "generator"
        if not generator_path.exists():
            console.print("❌ Module tools not found. Run setup first.")
            return False
            
        project_path = self.workspace_path / config.name
        if project_path.exists():
            console.print(f"❌ Project directory already exists: {project_path}")
            return False
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Creating module project: {config.name}...", total=None)
                
                # Use gradlew wrapper
                gradlew_cmd = "./gradlew" if os.name != 'nt' else "gradlew.bat"
                
                # Create input file for automated project generation
                input_data = f"""{config.scopes}
{config.name}
{config.root_package}.{config.name.lower().replace('-', '')}
{config.language}
"""
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(input_data)
                    input_file = f.name
                    
                try:
                    # Run the generator with input file
                    with open(input_file, 'r') as input_f:
                        result = subprocess.run([
                            gradlew_cmd, "runCli", "--console", "plain"
                        ], cwd=generator_path, stdin=input_f, 
                           capture_output=True, text=True, timeout=120)
                    
                    if result.returncode == 0:
                        # Move generated project to workspace
                        generated_name = config.name.replace('-', '').replace('_', '')
                        generated_path = generator_path / generated_name
                        
                        if generated_path.exists():
                            shutil.move(str(generated_path), str(project_path))
                            console.print(f"✅ Created module project: {project_path}")
                            return True
                        else:
                            console.print(f"❌ Generated project not found at: {generated_path}")
                            return False
                    else:
                        console.print(f"❌ Failed to create project: {result.stderr}")
                        return False
                        
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(input_file)
                    except OSError:
                        pass
                    
        except subprocess.TimeoutExpired:
            console.print("❌ Timeout while creating module project")
            return False
        except Exception as e:
            console.print(f"❌ Error creating module project: {e}")
            return False
            
    def list_projects(self) -> List[Path]:
        """List existing module projects in the workspace.
        
        Returns:
            List of project directory paths
        """
        if not self.workspace_path.exists():
            return []
            
        projects = []
        for item in self.workspace_path.iterdir():
            if item.is_dir() and item.name != "ignition-module-tools":
                # Check if it looks like a module project
                if (item / "build.gradle.kts").exists() or (item / "build.gradle").exists():
                    projects.append(item)
                    
        return projects
        
    def get_project_info(self, project_path: Path) -> Dict[str, Any]:
        """Get information about a module project.
        
        Args:
            project_path: Path to the module project
            
        Returns:
            Dictionary with project information
        """
        info = {
            "name": project_path.name,
            "path": str(project_path),
            "exists": project_path.exists(),
            "build_file": None,
            "module_xml": None,
        }
        
        if not project_path.exists():
            return info
            
        # Check for build files
        if (project_path / "build.gradle.kts").exists():
            info["build_file"] = "build.gradle.kts"
        elif (project_path / "build.gradle").exists():
            info["build_file"] = "build.gradle"
            
        # Check for module.xml in build output
        module_xml_path = project_path / "build" / "module.xml"
        if module_xml_path.exists():
            info["module_xml"] = str(module_xml_path)
            
        return info
        
    def build_project(self, project_path: Path) -> bool:
        """Build a module project.
        
        Args:
            project_path: Path to the module project
            
        Returns:
            True if successful, False otherwise
        """
        if not project_path.exists():
            console.print(f"❌ Project not found: {project_path}")
            return False
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Building project: {project_path.name}...", total=None)
                
                # Use gradlew wrapper
                gradlew_cmd = "./gradlew" if os.name != 'nt' else "gradlew.bat"
                
                result = subprocess.run([
                    gradlew_cmd, "build"
                ], cwd=project_path, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    console.print(f"✅ Successfully built project: {project_path.name}")
                    
                    # Check for .modl file
                    build_dir = project_path / "build"
                    modl_files = list(build_dir.glob("*.modl"))
                    if modl_files:
                        console.print(f"📦 Module file created: {modl_files[0]}")
                    
                    return True
                else:
                    console.print(f"❌ Failed to build project: {result.stderr}")
                    return False
                    
        except subprocess.TimeoutExpired:
            console.print("❌ Timeout while building project")
            return False
        except Exception as e:
            console.print(f"❌ Error building project: {e}")
            return False
            
    def get_environment_status(self) -> Dict[str, Any]:
        """Get the current status of the SDK environment.
        
        Returns:
            Dictionary with environment status information
        """
        status = {
            "workspace_exists": self.workspace_path.exists(),
            "workspace_path": str(self.workspace_path),
            "tools_cloned": self.tools_path.exists(),
            "tools_built": False,
            "projects": [],
            "prerequisites": self.check_prerequisites()
        }
        
        # Check if tools are built
        if self.tools_path.exists():
            generator_path = self.tools_path / "generator"
            build_dir = generator_path / "build"
            status["tools_built"] = build_dir.exists() and any(build_dir.iterdir())
            
        # List projects
        status["projects"] = [
            self.get_project_info(p) for p in self.list_projects()
        ]
        
        return status 