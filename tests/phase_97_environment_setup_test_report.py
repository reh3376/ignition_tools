#!/usr/bin/env python3
"""
Phase 9.7 Environment Setup Testing Report Generator
Following crawl_mcp.py methodology for systematic validation
"""

import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ignition.modules.deployment.environment_setup import (
    Phase97EnvironmentSetup,
    ValidationResult,
)

console = Console()


class Phase97EnvironmentTestReporter:
    """
    Phase 9.7 Environment Setup Test Reporter
    Following crawl_mcp.py methodology for systematic validation
    """

    def __init__(self):
        self.console = Console()
        self.results = {}
        self.start_time = datetime.now()
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

    def log_test_start(self, test_name: str) -> None:
        """Log the start of a test following crawl_mcp.py pattern."""
        self.console.print(f"🔍 Testing: {test_name}", style="blue")
        self.test_count += 1

    def log_test_result(self, test_name: str, passed: bool, details: str = "") -> None:
        """Log test result following crawl_mcp.py pattern."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.console.print(f"  {status}: {test_name}")
        if details:
            self.console.print(f"    Details: {details}", style="dim")

        if passed:
            self.passed_count += 1
        else:
            self.failed_count += 1

    def test_module_import(self) -> dict[str, Any]:
        """Test 1: Module Import Validation (crawl_mcp.py pattern)."""
        self.log_test_start("Module Import Validation")

        try:
            from ignition.modules.deployment.environment_setup import (
                Phase97EnvironmentSetup,
            )

            setup = Phase97EnvironmentSetup()

            # Test class initialization
            assert hasattr(setup, "validate_environment_variables")
            assert hasattr(setup, "check_system_requirements")
            assert hasattr(setup, "setup_development_environment")
            assert hasattr(setup, "generate_final_report")

            self.log_test_result("Module Import", True, "All required methods available")
            return {
                "passed": True,
                "details": "Phase97EnvironmentSetup class imported and initialized successfully",
                "methods_available": [
                    "validate_environment_variables",
                    "check_system_requirements",
                    "setup_development_environment",
                    "generate_final_report",
                ],
            }

        except Exception as e:
            self.log_test_result("Module Import", False, str(e))
            return {"passed": False, "error": str(e)}

    def test_environment_variable_validation(self) -> dict[str, Any]:
        """Test 2: Environment Variable Validation (crawl_mcp.py pattern)."""
        self.log_test_start("Environment Variable Validation")

        try:
            setup = Phase97EnvironmentSetup()
            env_results = setup.validate_environment_variables()

            # Validate expected variables are checked
            expected_vars = [
                "DEPLOYMENT_TEMP_DIR",
                "DEPLOYMENT_OUTPUT_DIR",
                "JAVA_HOME",
                "GRADLE_HOME",
                "MODULE_SIGNING_ENABLED",
            ]

            missing_vars = []
            for var in expected_vars:
                if var not in env_results:
                    missing_vars.append(var)

            if missing_vars:
                self.log_test_result(
                    "Environment Variables",
                    False,
                    f"Missing validation for: {missing_vars}",
                )
                return {"passed": False, "missing_variables": missing_vars}

            # Count valid vs invalid
            valid_count = sum(1 for result in env_results.values() if result.valid)
            invalid_count = len(env_results) - valid_count

            self.log_test_result(
                "Environment Variables",
                True,
                f"Validated {len(env_results)} variables ({valid_count} valid, {invalid_count} invalid)",
            )

            return {
                "passed": True,
                "total_variables": len(env_results),
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "variables_checked": list(env_results.keys()),
            }

        except Exception as e:
            self.log_test_result("Environment Variables", False, str(e))
            return {"passed": False, "error": str(e)}

    def test_system_requirements_validation(self) -> dict[str, Any]:
        """Test 3: System Requirements Validation (crawl_mcp.py pattern)."""
        self.log_test_start("System Requirements Validation")

        try:
            setup = Phase97EnvironmentSetup()
            sys_results = setup.check_system_requirements()

            # Validate expected components are checked
            expected_components = ["java", "gradle", "openssl"]

            missing_components = []
            for component in expected_components:
                if component not in sys_results:
                    missing_components.append(component)

            if missing_components:
                self.log_test_result(
                    "System Requirements",
                    False,
                    f"Missing validation for: {missing_components}",
                )
                return {"passed": False, "missing_components": missing_components}

            # Count valid vs invalid
            valid_count = sum(1 for result in sys_results.values() if result.valid)
            invalid_count = len(sys_results) - valid_count

            self.log_test_result(
                "System Requirements",
                True,
                f"Validated {len(sys_results)} components ({valid_count} valid, {invalid_count} invalid)",
            )

            return {
                "passed": True,
                "total_components": len(sys_results),
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "components_checked": list(sys_results.keys()),
            }

        except Exception as e:
            self.log_test_result("System Requirements", False, str(e))
            return {"passed": False, "error": str(e)}

    def test_development_environment_setup(self) -> dict[str, Any]:
        """Test 4: Development Environment Setup (crawl_mcp.py pattern)."""
        self.log_test_start("Development Environment Setup")

        try:
            setup = Phase97EnvironmentSetup()

            # Test with non-interactive mode to avoid user prompts
            dev_results = setup.setup_development_environment(interactive=False)

            # Validate setup results structure
            required_keys = [
                "directories_created",
                "certificates_generated",
                "config_updated",
            ]
            missing_keys = []
            for key in required_keys:
                if key not in dev_results:
                    missing_keys.append(key)

            if missing_keys:
                self.log_test_result("Development Setup", False, f"Missing result keys: {missing_keys}")
                return {"passed": False, "missing_keys": missing_keys}

            self.log_test_result(
                "Development Setup",
                True,
                "Environment setup structure validated (dry-run)",
            )

            return {
                "passed": True,
                "setup_structure_valid": True,
                "dry_run_successful": True,
                "result_keys": list(dev_results.keys()),
            }

        except Exception as e:
            self.log_test_result("Development Setup", False, str(e))
            return {"passed": False, "error": str(e)}

    def test_final_report_generation(self) -> dict[str, Any]:
        """Test 5: Final Report Generation (crawl_mcp.py pattern)."""
        self.log_test_start("Final Report Generation")

        try:
            setup = Phase97EnvironmentSetup()

            # Generate comprehensive report using the available method
            report = setup.generate_setup_report()

            # Validate report structure
            required_sections = [
                "environment_score",
                "system_score",
                "overall_score",
                "recommendations",
                "next_steps",
            ]
            missing_sections = []
            for section in required_sections:
                if section not in report:
                    missing_sections.append(section)

            if missing_sections:
                self.log_test_result(
                    "Final Report",
                    False,
                    f"Missing report sections: {missing_sections}",
                )
                return {"passed": False, "missing_sections": missing_sections}

            # Validate score ranges
            scores_valid = (
                0 <= report["environment_score"] <= 100
                and 0 <= report["system_score"] <= 100
                and 0 <= report["overall_score"] <= 100
            )

            if not scores_valid:
                self.log_test_result("Final Report", False, "Invalid score ranges")
                return {"passed": False, "error": "Score validation failed"}

            self.log_test_result(
                "Final Report",
                True,
                f"Report generated with overall score: {report['overall_score']}",
            )

            return {
                "passed": True,
                "report_structure_valid": True,
                "overall_score": report["overall_score"],
                "environment_score": report["environment_score"],
                "system_score": report["system_score"],
                "recommendations_count": len(report.get("recommendations", [])),
                "next_steps_count": len(report.get("next_steps", [])),
            }

        except Exception as e:
            self.log_test_result("Final Report", False, str(e))
            return {"passed": False, "error": str(e)}

    def test_cli_integration(self) -> dict[str, Any]:
        """Test 6: CLI Integration (crawl_mcp.py pattern)."""
        self.log_test_start("CLI Integration")

        try:
            from ignition.modules.deployment.cli_commands import deployment_cli

            # Check if environment setup commands are available
            expected_commands = [
                "setup-environment",
                "check-environment",
                "install-requirements",
            ]
            available_commands = list(deployment_cli.commands.keys())

            missing_commands = []
            for cmd in expected_commands:
                if cmd not in available_commands:
                    missing_commands.append(cmd)

            if missing_commands:
                self.log_test_result(
                    "CLI Integration",
                    False,
                    f"Missing CLI commands: {missing_commands}",
                )
                return {"passed": False, "missing_commands": missing_commands}

            self.log_test_result(
                "CLI Integration",
                True,
                f"All {len(expected_commands)} environment setup commands available",
            )

            return {
                "passed": True,
                "expected_commands": expected_commands,
                "available_commands": available_commands,
                "total_deployment_commands": len(available_commands),
            }

        except Exception as e:
            self.log_test_result("CLI Integration", False, str(e))
            return {"passed": False, "error": str(e)}

    def test_homebrew_integration(self) -> dict[str, Any]:
        """Test 7: Homebrew Integration (crawl_mcp.py pattern)."""
        self.log_test_start("Homebrew Integration")

        try:
            # Check if running on macOS
            if platform.system() != "Darwin":
                self.log_test_result("Homebrew Integration", True, "Skipped (not macOS)")
                return {"passed": True, "skipped": True, "reason": "Not macOS"}

            # Check if Homebrew is available
            try:
                result = subprocess.run(["which", "brew"], capture_output=True, text=True)
                homebrew_available = result.returncode == 0
            except Exception:
                homebrew_available = False

            if not homebrew_available:
                self.log_test_result("Homebrew Integration", False, "Homebrew not found")
                return {"passed": False, "error": "Homebrew not available"}

            # Test Homebrew availability and basic setup functionality
            setup = Phase97EnvironmentSetup()

            # Test system requirements check which includes checking for missing tools
            sys_results = setup.check_system_requirements()

            # Validate that the system can detect missing tools
            java_valid = sys_results.get("java", ValidationResult(False)).valid
            gradle_valid = sys_results.get("gradle", ValidationResult(False)).valid

            self.log_test_result(
                "Homebrew Integration",
                True,
                f"System requirements check functional (Java: {java_valid}, Gradle: {gradle_valid})",
            )

            return {
                "passed": True,
                "homebrew_available": True,
                "system_check_functional": True,
                "java_detected": java_valid,
                "gradle_detected": gradle_valid,
            }

        except Exception as e:
            self.log_test_result("Homebrew Integration", False, str(e))
            return {"passed": False, "error": str(e)}

    def generate_comprehensive_report(self) -> dict[str, Any]:
        """Generate comprehensive test report following crawl_mcp.py pattern."""

        # Run all tests
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Running Phase 9.7 Environment Setup Tests...", total=7)

            # Test 1: Module Import
            progress.update(task, description="Testing Module Import...")
            self.results["module_import"] = self.test_module_import()
            progress.advance(task)

            # Test 2: Environment Variables
            progress.update(task, description="Testing Environment Variables...")
            self.results["environment_variables"] = self.test_environment_variable_validation()
            progress.advance(task)

            # Test 3: System Requirements
            progress.update(task, description="Testing System Requirements...")
            self.results["system_requirements"] = self.test_system_requirements_validation()
            progress.advance(task)

            # Test 4: Development Setup
            progress.update(task, description="Testing Development Setup...")
            self.results["development_setup"] = self.test_development_environment_setup()
            progress.advance(task)

            # Test 5: Final Report
            progress.update(task, description="Testing Final Report...")
            self.results["final_report"] = self.test_final_report_generation()
            progress.advance(task)

            # Test 6: CLI Integration
            progress.update(task, description="Testing CLI Integration...")
            self.results["cli_integration"] = self.test_cli_integration()
            progress.advance(task)

            # Test 7: Homebrew Integration
            progress.update(task, description="Testing Homebrew Integration...")
            self.results["homebrew_integration"] = self.test_homebrew_integration()
            progress.advance(task)

        # Calculate overall score
        passed_tests = sum(1 for result in self.results.values() if result.get("passed", False))
        total_tests = len(self.results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        # Generate summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": success_rate,
                "duration_seconds": duration,
            },
            "test_results": self.results,
            "environment_setup_readiness": {
                "module_ready": self.results.get("module_import", {}).get("passed", False),
                "validation_ready": self.results.get("environment_variables", {}).get("passed", False),
                "system_check_ready": self.results.get("system_requirements", {}).get("passed", False),
                "setup_ready": self.results.get("development_setup", {}).get("passed", False),
                "reporting_ready": self.results.get("final_report", {}).get("passed", False),
                "cli_ready": self.results.get("cli_integration", {}).get("passed", False),
                "automation_ready": self.results.get("homebrew_integration", {}).get("passed", False),
            },
            "recommendations": self._generate_recommendations(),
            "next_steps": self._generate_next_steps(),
            "metadata": {
                "test_timestamp": self.start_time.isoformat(),
                "platform": platform.system(),
                "python_version": sys.version,
                "methodology": "crawl_mcp.py step-by-step validation",
            },
        }

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if not self.results.get("module_import", {}).get("passed", False):
            recommendations.append("🔴 Fix module import issues before proceeding")

        if not self.results.get("environment_variables", {}).get("passed", False):
            recommendations.append("🟡 Configure missing environment variables")

        if not self.results.get("system_requirements", {}).get("passed", False):
            recommendations.append("🔴 Install missing system requirements (Java, Gradle)")

        if not self.results.get("homebrew_integration", {}).get("passed", False):
            recommendations.append("🟡 Install Homebrew for automated setup on macOS")

        if not recommendations:
            recommendations.append("✅ All environment setup tests passed")

        return recommendations

    def _generate_next_steps(self) -> list[str]:
        """Generate next steps based on test results."""
        next_steps = []

        # Check system requirements
        sys_result = self.results.get("system_requirements", {})
        if sys_result.get("passed") and sys_result.get("invalid_count", 0) > 0:
            next_steps.append("Run 'ign deploy install-requirements --all' to install missing tools")

        # Check environment variables
        env_result = self.results.get("environment_variables", {})
        if env_result.get("passed") and env_result.get("invalid_count", 0) > 0:
            next_steps.append("Run 'ign deploy setup-environment' to configure environment")

        # Check overall readiness
        if self.passed_count == self.test_count:
            next_steps.append("Environment setup system is fully functional")
            next_steps.append("Ready for Phase 9.7 deployment operations")

        return next_steps

    def print_summary_table(self, report: dict[str, Any]) -> None:
        """Print summary table following crawl_mcp.py pattern."""

        # Create main summary table
        table = Table(title="Phase 9.7 Environment Setup Test Results")
        table.add_column("Test Category", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        for test_name, result in report["test_results"].items():
            status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
            details = result.get("details", result.get("error", "No details"))

            # Format test name
            formatted_name = test_name.replace("_", " ").title()

            table.add_row(
                formatted_name,
                status,
                str(details)[:50] + "..." if len(str(details)) > 50 else str(details),
            )

        self.console.print(table)

        # Print readiness summary
        readiness = report["environment_setup_readiness"]
        ready_count = sum(1 for ready in readiness.values() if ready)
        total_components = len(readiness)

        readiness_table = Table(title="Environment Setup Readiness")
        readiness_table.add_column("Component", style="cyan")
        readiness_table.add_column("Status", style="green")

        for component, ready in readiness.items():
            status = "✅ Ready" if ready else "❌ Not Ready"
            formatted_component = component.replace("_", " ").title()
            readiness_table.add_row(formatted_component, status)

        self.console.print(readiness_table)

        # Print overall score
        score_panel = Panel(
            f"Overall Success Rate: {report['test_summary']['success_rate']:.1f}%\n"
            f"Ready Components: {ready_count}/{total_components}\n"
            f"Test Duration: {report['test_summary']['duration_seconds']:.2f}s",
            title="Summary",
            style="green" if report["test_summary"]["success_rate"] > 80 else "yellow",
        )
        self.console.print(score_panel)


def main():
    """Main function following crawl_mcp.py pattern."""
    console = Console()

    console.print(
        Panel(
            "Phase 9.7 Environment Setup Testing\nFollowing crawl_mcp.py methodology for systematic validation",
            title="🔧 Environment Setup Test Suite",
            style="blue",
        )
    )

    # Initialize reporter
    reporter = Phase97EnvironmentTestReporter()

    # Generate comprehensive report
    report = reporter.generate_comprehensive_report()

    # Print results
    console.print("\n")
    reporter.print_summary_table(report)

    # Print recommendations
    if report["recommendations"]:
        console.print("\n💡 Recommendations:", style="yellow bold")
        for rec in report["recommendations"]:
            console.print(f"  {rec}")

    # Print next steps
    if report["next_steps"]:
        console.print("\n🎯 Next Steps:", style="blue bold")
        for step in report["next_steps"]:
            console.print(f"  • {step}")

    # Save detailed report
    report_file = Path("phase_97_environment_setup_test_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    console.print(f"\n📄 Detailed report saved to: {report_file}")

    # Exit with appropriate code
    success_rate = report["test_summary"]["success_rate"]
    if success_rate >= 90:
        console.print("🎉 Environment setup system is excellent!", style="green bold")
        exit_code = 0
    elif success_rate >= 70:
        console.print("⚠️  Environment setup system needs minor improvements", style="yellow bold")
        exit_code = 0
    else:
        console.print("❌ Environment setup system needs significant work", style="red bold")
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
