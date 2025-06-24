#!/usr/bin/env python3
"""
Comprehensive Test Script for Phase 11.5 - Industrial Dataset Curation & AI Model Preparation

Following crawl_mcp.py methodology:
- Environment validation first
- Comprehensive input validation
- Error handling with user-friendly messages
- Modular testing approach
- Progressive complexity
- Resource management

This script validates the complete Phase 11.5 implementation including:
- Industrial dataset curation core functionality
- Variable type classification system
- Data ingestion framework
- AI model preparation with feature engineering
- CLI command integration
- Documentation completeness
"""

import asyncio
import importlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for better output
console = Console()


def validate_environment() -> Dict[str, bool]:
    """Validate test environment following crawl_mcp.py patterns."""
    try:
        validation_results = {}
        
        # Check Python version
        validation_results["python_version"] = sys.version_info >= (3, 12)
        
        # Check required packages
        required_packages = ["click", "rich", "pandas", "numpy", "pydantic", "dotenv"]
        for package in required_packages:
            try:
                importlib.import_module(package)
                validation_results[f"package_{package}"] = True
            except ImportError:
                validation_results[f"package_{package}"] = False
        
        # Check project structure
        project_root = Path(__file__).parent
        required_paths = [
            "src/ignition/modules/sme_agent/industrial_dataset_curation.py",
            "src/ignition/modules/sme_agent/ai_model_preparation.py",
            "src/ignition/modules/sme_agent/data_ingestion_framework.py",
            "src/ignition/modules/sme_agent/variable_type_classifier.py",
            "src/ignition/modules/sme_agent/cli/dataset_curation_commands.py",
        ]
        
        for path in required_paths:
            full_path = project_root / path
            validation_results[f"file_{path.split('/')[-1]}"] = full_path.exists()
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return {"validation_error": False}


class Phase11_5Tester:
    """Comprehensive tester for Phase 11.5 implementation."""
    
    def __init__(self):
        """Initialize the tester."""
        self.console = console
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 11.5 tests."""
        try:
            self.console.print("\n🧪 [bold blue]Phase 11.5 - Industrial Dataset Curation & AI Model Preparation Tests[/bold blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Running comprehensive tests...", total=None)
                
                # Test categories
                test_categories = [
                    ("Environment Validation", self._test_environment),
                    ("Module Imports", self._test_module_imports),
                    ("Industrial Dataset Curation", self._test_industrial_dataset_curation),
                    ("AI Model Preparation", self._test_ai_model_preparation),
                    ("Data Ingestion Framework", self._test_data_ingestion_framework),
                    ("Variable Type Classifier", self._test_variable_type_classifier),
                    ("CLI Commands - Dataset Curation", self._test_cli_dataset_curation),
                    ("CLI Commands - AI Model Prep", self._test_cli_ai_model_prep),
                    ("File Structure", self._test_file_structure),
                    ("Documentation", self._test_documentation),
                ]
                
                for category_name, test_func in test_categories:
                    progress.update(task, description=f"Testing {category_name}...")
                    try:
                        result = test_func()
                        self.test_results[category_name] = result
                        if result.get("success", False):
                            self.passed_tests += 1
                        self.total_tests += 1
                    except Exception as e:
                        self.test_results[category_name] = {
                            "success": False,
                            "error": str(e),
                            "details": f"Test execution failed: {e}"
                        }
                        self.total_tests += 1
                
                progress.update(task, description="All tests completed!")
            
            return self._generate_test_report()
            
        except Exception as e:
            self.console.print(f"[red]❌ Test execution failed: {e}[/red]")
            return {"success": False, "error": str(e)}
    
    def _test_environment(self) -> Dict[str, Any]:
        """Test environment validation."""
        try:
            env_results = validate_environment()
            passed = sum(env_results.values())
            total = len(env_results)
            
            return {
                "success": passed == total,
                "passed": passed,
                "total": total,
                "details": env_results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_module_imports(self) -> Dict[str, Any]:
        """Test module imports."""
        try:
            modules_to_test = [
                "src.ignition.modules.sme_agent.industrial_dataset_curation",
                "src.ignition.modules.sme_agent.ai_model_preparation",
                "src.ignition.modules.sme_agent.data_ingestion_framework",
                "src.ignition.modules.sme_agent.variable_type_classifier",
            ]
            
            import_results = {}
            for module_name in modules_to_test:
                try:
                    importlib.import_module(module_name)
                    import_results[module_name] = True
                except ImportError as e:
                    import_results[module_name] = False
                    logger.error(f"Failed to import {module_name}: {e}")
            
            passed = sum(import_results.values())
            total = len(import_results)
            
            return {
                "success": passed == total,
                "passed": passed,
                "total": total,
                "details": import_results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_industrial_dataset_curation(self) -> Dict[str, Any]:
        """Test industrial dataset curation functionality."""
        try:
            from src.ignition.modules.sme_agent.industrial_dataset_curation import (
                IndustrialDatasetCurator,
                VariableType,
                ControllerType,
                DataSourceType,
                VariableMetadata,
                ControllerMetadata,
                validate_environment as validate_curator_env,
            )
            
            # Test basic functionality
            curator = IndustrialDatasetCurator("standard")
            
            # Test variable addition
            var_metadata = VariableMetadata(
                name="test_temp",
                variable_type=VariableType.PRIMARY_PV,
                engineering_units="°C",
                high_limit=100.0,
                low_limit=0.0,
                description="Test temperature variable"
            )
            
            var_added = curator.add_variable(var_metadata)
            
            # Test controller addition
            controller_metadata = ControllerMetadata(
                name="test_controller",
                controller_type=ControllerType.PID,
                controlled_variable="test_temp",
                process_variable="temp_sensor",
                kc_kp=1.0,
                ti_ki=0.1,
                td_kd=0.01,
            )
            
            controller_added = curator.add_controller(controller_metadata)
            
            # Test environment validation
            env_validation = validate_curator_env()
            
            return {
                "success": var_added and controller_added and any(env_validation.values()),
                "variable_added": var_added,
                "controller_added": controller_added,
                "env_validation": env_validation,
                "details": "Industrial dataset curation core functionality tested"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_ai_model_preparation(self) -> Dict[str, Any]:
        """Test AI model preparation functionality."""
        try:
            from src.ignition.modules.sme_agent.ai_model_preparation import (
                AIModelPreparation,
                FeatureEngineeringConfig,
                ModelPreparationConfig,
                validate_environment as validate_ai_env,
            )
            from src.ignition.modules.sme_agent.industrial_dataset_curation import IndustrialDatasetCurator
            
            # Test environment validation
            env_validation = validate_ai_env()
            
            # Test basic initialization
            curator = IndustrialDatasetCurator("standard")
            ai_prep = AIModelPreparation(curator, "standard")
            
            # Test configuration creation
            feature_config = FeatureEngineeringConfig(
                enable_derivatives=True,
                enable_integrals=True,
                enable_moving_averages=True,
                enable_cross_correlations=True,
                window_sizes=[5, 10, 30],
                derivative_orders=[1, 2],
                correlation_lags=[1, 5, 10],
            )
            
            model_config = ModelPreparationConfig(
                train_split=0.7,
                validation_split=0.15,
                test_split=0.15,
                target_variables=["test_target"],
                normalize_features=True,
                handle_missing_data=True,
                feature_selection_method="correlation",
                random_seed=42,
            )
            
            # Test status retrieval
            status = ai_prep.get_preparation_status()
            
            return {
                "success": True,
                "env_validation": env_validation,
                "feature_config_created": feature_config is not None,
                "model_config_created": model_config is not None,
                "status_retrieved": status is not None,
                "details": "AI model preparation functionality tested"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_data_ingestion_framework(self) -> Dict[str, Any]:
        """Test data ingestion framework."""
        try:
            from src.ignition.modules.sme_agent.data_ingestion_framework import DataIngestionFramework
            from src.ignition.modules.sme_agent.industrial_dataset_curation import IndustrialDatasetCurator
            
            # Test initialization
            curator = IndustrialDatasetCurator("standard")
            ingestion_framework = DataIngestionFramework(curator)
            
            return {
                "success": True,
                "framework_initialized": ingestion_framework is not None,
                "details": "Data ingestion framework initialized successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_variable_type_classifier(self) -> Dict[str, Any]:
        """Test variable type classifier."""
        try:
            from src.ignition.modules.sme_agent.variable_type_classifier import VariableTypeClassifier
            from src.ignition.modules.sme_agent.industrial_dataset_curation import IndustrialDatasetCurator
            
            # Test initialization
            curator = IndustrialDatasetCurator("standard")
            classifier = VariableTypeClassifier(curator)
            
            return {
                "success": True,
                "classifier_initialized": classifier is not None,
                "details": "Variable type classifier initialized successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_cli_dataset_curation(self) -> Dict[str, Any]:
        """Test dataset curation CLI commands."""
        try:
            # Test main dataset-curation command
            result = subprocess.run([
                sys.executable, "-m", "src.main", "module", "sme", "dataset-curation", "--help"
            ], capture_output=True, text=True, timeout=30)
            
            main_cmd_success = result.returncode == 0 and "Industrial Dataset Curation" in result.stdout
            
            # Test specific commands
            commands_to_test = [
                "validate-env",
                "info",
                "status",
                "list-variable-types",
            ]
            
            command_results = {}
            for cmd in commands_to_test:
                try:
                    cmd_result = subprocess.run([
                        sys.executable, "-m", "src.main", "module", "sme", "dataset-curation", cmd, "--help"
                    ], capture_output=True, text=True, timeout=30)
                    command_results[cmd] = cmd_result.returncode == 0
                except subprocess.TimeoutExpired:
                    command_results[cmd] = False
            
            passed_commands = sum(command_results.values())
            total_commands = len(command_results)
            
            return {
                "success": main_cmd_success and passed_commands == total_commands,
                "main_command": main_cmd_success,
                "individual_commands": command_results,
                "passed": passed_commands,
                "total": total_commands,
                "details": "Dataset curation CLI commands tested"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_cli_ai_model_prep(self) -> Dict[str, Any]:
        """Test AI model preparation CLI commands."""
        try:
            # Test main ai-model-prep command
            result = subprocess.run([
                sys.executable, "-m", "src.main", "module", "sme", "dataset-curation", "ai-model-prep", "--help"
            ], capture_output=True, text=True, timeout=30)
            
            main_cmd_success = result.returncode == 0 and "AI Model Preparation" in result.stdout
            
            # Test specific commands
            commands_to_test = [
                "validate-env",
                "info",
                "status",
            ]
            
            command_results = {}
            for cmd in commands_to_test:
                try:
                    cmd_result = subprocess.run([
                        sys.executable, "-m", "src.main", "module", "sme", "dataset-curation", "ai-model-prep", cmd, "--help"
                    ], capture_output=True, text=True, timeout=30)
                    command_results[cmd] = cmd_result.returncode == 0
                except subprocess.TimeoutExpired:
                    command_results[cmd] = False
            
            passed_commands = sum(command_results.values())
            total_commands = len(command_results)
            
            return {
                "success": main_cmd_success and passed_commands == total_commands,
                "main_command": main_cmd_success,
                "individual_commands": command_results,
                "passed": passed_commands,
                "total": total_commands,
                "details": "AI model preparation CLI commands tested"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_file_structure(self) -> Dict[str, Any]:
        """Test file structure completeness."""
        try:
            project_root = Path(__file__).parent
            required_files = [
                "src/ignition/modules/sme_agent/industrial_dataset_curation.py",
                "src/ignition/modules/sme_agent/ai_model_preparation.py",
                "src/ignition/modules/sme_agent/data_ingestion_framework.py",
                "src/ignition/modules/sme_agent/variable_type_classifier.py",
                "src/ignition/modules/sme_agent/cli/dataset_curation_commands.py",
                "docs/roadmap.md",
            ]
            
            file_results = {}
            for file_path in required_files:
                full_path = project_root / file_path
                file_results[file_path] = full_path.exists()
            
            passed_files = sum(file_results.values())
            total_files = len(file_results)
            
            return {
                "success": passed_files == total_files,
                "file_results": file_results,
                "passed": passed_files,
                "total": total_files,
                "details": "File structure validation completed"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_documentation(self) -> Dict[str, Any]:
        """Test documentation completeness."""
        try:
            project_root = Path(__file__).parent
            
            # Check if Phase 11.5 documentation exists
            phase_docs = list(project_root.glob("docs/phase_summary/PHASE_11_5*.md"))
            
            # Check roadmap for Phase 11.5 completion
            roadmap_path = project_root / "docs/roadmap.md"
            roadmap_content = ""
            if roadmap_path.exists():
                roadmap_content = roadmap_path.read_text()
            
            phase_11_5_mentioned = "Phase 11.5" in roadmap_content
            phase_11_5_completed = "✅ **COMPLETED**" in roadmap_content and "Phase 11.5" in roadmap_content
            
            return {
                "success": len(phase_docs) > 0 and phase_11_5_mentioned,
                "phase_documentation_exists": len(phase_docs) > 0,
                "phase_docs_count": len(phase_docs),
                "roadmap_mentions_phase": phase_11_5_mentioned,
                "roadmap_shows_completed": phase_11_5_completed,
                "details": f"Found {len(phase_docs)} Phase 11.5 documentation files"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        # Create summary table
        summary_table = Table(title="Phase 11.5 Test Results Summary")
        summary_table.add_column("Test Category", style="cyan")
        summary_table.add_column("Status", style="magenta")
        summary_table.add_column("Details", style="green")
        
        for category, result in self.test_results.items():
            status_icon = "✅" if result.get("success", False) else "❌"
            status_text = "PASS" if result.get("success", False) else "FAIL"
            
            details = result.get("details", "No details available")
            if "passed" in result and "total" in result:
                details = f"{result['passed']}/{result['total']} - {details}"
            
            summary_table.add_row(
                category,
                f"{status_icon} {status_text}",
                details
            )
        
        self.console.print(summary_table)
        
        # Overall summary
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        if self.passed_tests == self.total_tests:
            summary_color = "green"
            summary_icon = "✅"
            summary_text = f"All {self.total_tests} test categories passed!"
        else:
            summary_color = "yellow" if success_rate >= 70 else "red"
            summary_icon = "⚠️" if success_rate >= 70 else "❌"
            summary_text = f"{self.passed_tests}/{self.total_tests} test categories passed ({success_rate:.1f}%)"
        
        self.console.print(f"\n[{summary_color}]{summary_icon} {summary_text}[/{summary_color}]")
        
        # Detailed results for failed tests
        failed_tests = [cat for cat, result in self.test_results.items() if not result.get("success", False)]
        if failed_tests:
            self.console.print(f"\n[yellow]⚠️ Failed test categories:[/yellow]")
            for category in failed_tests:
                error = self.test_results[category].get("error", "Unknown error")
                self.console.print(f"  • {category}: {error}")
        
        return {
            "success": self.passed_tests == self.total_tests,
            "passed_tests": self.passed_tests,
            "total_tests": self.total_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "summary": summary_text
        }


def main():
    """Main test execution function."""
    console.print(Panel.fit(
        "[bold blue]Phase 11.5 - Industrial Dataset Curation & AI Model Preparation[/bold blue]\n"
        "[cyan]Comprehensive Test Suite[/cyan]\n\n"
        "Testing complete implementation including:\n"
        "• Industrial dataset curation core functionality\n"
        "• AI model preparation with feature engineering\n"
        "• Data ingestion framework\n"
        "• Variable type classification\n"
        "• CLI command integration\n"
        "• Documentation completeness",
        title="🧪 Phase 11.5 Test Suite"
    ))
    
    # Initialize and run tests
    tester = Phase11_5Tester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main() 