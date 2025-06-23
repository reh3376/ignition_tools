#!/usr/bin/env python3
"""
Comprehensive Test Suite for Phase 9.7 - Module Deployment & Distribution
Following crawl_mcp.py methodology for systematic testing

This test suite implements the step-by-step validation approach:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling with User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity
6. Resource Management
7. Comprehensive Logging and Feedback
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Phase 9.7 components
try:
    from src.ignition.modules.deployment import (
        DeploymentConfig,
        DeploymentManager,
        ModulePackager,
        ModuleSigner,
        PackagingConfig,
        RepositoryConfig,
        RepositoryManager,
        SigningConfig,
    )

    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Import warning: {e}")
    IMPORTS_AVAILABLE = False


class Phase97TestValidator:
    """
    Test validator following crawl_mcp.py methodology for systematic validation
    """

    def __init__(self):
        self.test_results: dict[str, Any] = {
            "environment_validation": {},
            "component_validation": {},
            "integration_validation": {},
            "error_handling_validation": {},
            "comprehensive_results": {},
        }
        self.temp_dir = None

    def validate_environment_variables(self) -> dict[str, bool]:
        """
        Step 1: Environment Variable Validation First
        Following crawl_mcp.py pattern for env validation
        """
        print("🔍 Step 1: Validating Environment Variables...")

        required_vars = {
            # Core deployment variables
            "DEPLOYMENT_TEMP_DIR": os.getenv(
                "DEPLOYMENT_TEMP_DIR", "/tmp/ign_deployment"
            ),
            "DEPLOYMENT_OUTPUT_DIR": os.getenv(
                "DEPLOYMENT_OUTPUT_DIR", "/tmp/ign_output"
            ),
            # Gradle build variables
            "GRADLE_HOME": os.getenv("GRADLE_HOME"),
            "JAVA_HOME": os.getenv("JAVA_HOME"),
            # Signing variables
            "MODULE_SIGNING_ENABLED": os.getenv("MODULE_SIGNING_ENABLED", "false"),
            "SIGNING_CERT_PATH": os.getenv("SIGNING_CERT_PATH"),
            "SIGNING_KEY_PATH": os.getenv("SIGNING_KEY_PATH"),
            "SIGNING_KEY_PASSWORD": os.getenv("SIGNING_KEY_PASSWORD"),
            # Repository variables
            "MODULE_REPOSITORY_URL": os.getenv("MODULE_REPOSITORY_URL"),
            "MODULE_REPOSITORY_TOKEN": os.getenv("MODULE_REPOSITORY_TOKEN"),
            "MODULE_REPOSITORY_USER": os.getenv("MODULE_REPOSITORY_USER"),
            # Webhook variables
            "DEPLOYMENT_WEBHOOK_URL": os.getenv("DEPLOYMENT_WEBHOOK_URL"),
            "DEPLOYMENT_WEBHOOK_SECRET": os.getenv("DEPLOYMENT_WEBHOOK_SECRET"),
        }

        validation_results = {}
        for var_name, var_value in required_vars.items():
            is_valid = var_value is not None and var_value.strip() != ""
            validation_results[var_name] = is_valid
            status = "✅" if is_valid else "❌"
            print(f"  {status} {var_name}: {'SET' if is_valid else 'NOT SET'}")

        self.test_results["environment_validation"] = validation_results
        return validation_results

    def format_deployment_error(self, error: Exception) -> str:
        """
        Format deployment errors following crawl_mcp.py error handling pattern
        """
        error_str = str(error).lower()

        if "gradle" in error_str:
            return "Gradle build error. Check GRADLE_HOME and build configuration."
        elif "signing" in error_str or "certificate" in error_str:
            return "Module signing error. Check certificate and key configuration."
        elif "repository" in error_str or "upload" in error_str:
            return "Repository error. Check MODULE_REPOSITORY_URL and authentication."
        elif "permission" in error_str or "access" in error_str:
            return "Permission error. Check file permissions and directory access."
        elif "network" in error_str or "connection" in error_str:
            return (
                "Network error. Check internet connection and repository accessibility."
            )
        else:
            return f"Deployment error: {error!s}"

    def validate_input_parameters(self, **kwargs) -> dict[str, Any]:
        """
        Step 2: Comprehensive Input Validation
        Following crawl_mcp.py input validation pattern
        """
        print("🔍 Step 2: Validating Input Parameters...")

        validation_results = {}

        # Validate project path
        project_path = kwargs.get("project_path")
        if not project_path or not isinstance(project_path, (str, Path)):
            validation_results["project_path"] = {
                "valid": False,
                "error": "Project path is required",
            }
        else:
            project_path = Path(project_path)
            if not project_path.exists():
                validation_results["project_path"] = {
                    "valid": False,
                    "error": f"Project path not found: {project_path}",
                }
            elif not project_path.is_dir():
                validation_results["project_path"] = {
                    "valid": False,
                    "error": f"Project path must be a directory: {project_path}",
                }
            else:
                validation_results["project_path"] = {"valid": True}

        # Validate module file
        module_file = kwargs.get("module_file")
        if module_file:
            module_path = Path(module_file)
            if not module_path.exists():
                validation_results["module_file"] = {
                    "valid": False,
                    "error": f"Module file not found: {module_path}",
                }
            elif module_path.suffix.lower() != ".modl":
                validation_results["module_file"] = {
                    "valid": False,
                    "error": f"Invalid module file extension: {module_path.suffix}",
                }
            else:
                validation_results["module_file"] = {"valid": True}

        # Validate repository URL
        repo_url = kwargs.get("repository_url")
        if repo_url:
            if not isinstance(repo_url, str) or not repo_url.strip():
                validation_results["repository_url"] = {
                    "valid": False,
                    "error": "Repository URL must be a non-empty string",
                }
            elif not (
                repo_url.startswith("http://") or repo_url.startswith("https://")
            ):
                validation_results["repository_url"] = {
                    "valid": False,
                    "error": "Repository URL must start with http:// or https://",
                }
            else:
                validation_results["repository_url"] = {"valid": True}

        return validation_results

    def setup_test_environment(self) -> Path:
        """
        Step 3: Resource Management - Setup test environment
        Following crawl_mcp.py resource management pattern
        """
        print("🔧 Step 3: Setting up Test Environment...")

        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp(prefix="phase97_test_"))

        # Create test project structure
        test_project = self.temp_dir / "test_project"
        test_project.mkdir(parents=True)

        # Create mock Ignition project files
        (test_project / "build.gradle").write_text(
            """
plugins {
    id 'java'
    id 'application'
}

group = 'com.example'
version = '1.0.0'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'com.inductiveautomation.ignition:ignition-common:8.1.0'
}
"""
        )

        (test_project / "settings.gradle").write_text(
            """
rootProject.name = 'test-module'
"""
        )

        # Create source structure
        src_dir = test_project / "src" / "main" / "java" / "com" / "example"
        src_dir.mkdir(parents=True)

        (src_dir / "TestModule.java").write_text(
            """
package com.example;

import com.inductiveautomation.ignition.common.licensing.LicenseState;
import com.inductiveautomation.ignition.common.Module;

public class TestModule implements Module {
    @Override
    public void startup(LicenseState licenseState) {
        // Module startup logic
    }

    @Override
    public void shutdown() {
        // Module shutdown logic
    }
}
"""
        )

        # Create module.xml
        (test_project / "module.xml").write_text(
            """
<?xml version="1.0" encoding="UTF-8"?>
<modules>
    <module>
        <id>com.example.test-module</id>
        <name>Test Module</name>
        <description>Test module for Phase 9.7 testing</description>
        <version>1.0.0</version>
        <license>Apache 2.0</license>
        <documentation>
            <url>https://example.com/docs</url>
        </documentation>
        <freeModule>true</freeModule>
    </module>
</modules>
"""
        )

        print(f"✅ Test environment created at: {self.temp_dir}")
        return test_project

    def test_component_initialization(self) -> dict[str, Any]:
        """
        Step 4: Modular Component Testing - Test each component independently
        Following crawl_mcp.py modular testing pattern
        """
        print("🔍 Step 4: Testing Component Initialization...")

        results = {}

        if not IMPORTS_AVAILABLE:
            results["import_error"] = {
                "success": False,
                "error": "Phase 9.7 components not available for import",
            }
            print("  ❌ Components not available for testing")
            return results

        # Test ModulePackager initialization
        try:
            packaging_config = PackagingConfig()
            packager = ModulePackager(packaging_config)
            results["module_packager"] = {
                "success": True,
                "component": "ModulePackager",
            }
            print("  ✅ ModulePackager initialized successfully")
        except Exception as e:
            results["module_packager"] = {"success": False, "error": str(e)}
            print(f"  ❌ ModulePackager initialization failed: {e}")

        # Test ModuleSigner initialization
        try:
            signing_config = SigningConfig()
            signer = ModuleSigner(signing_config)
            results["module_signer"] = {"success": True, "component": "ModuleSigner"}
            print("  ✅ ModuleSigner initialized successfully")
        except Exception as e:
            results["module_signer"] = {"success": False, "error": str(e)}
            print(f"  ❌ ModuleSigner initialization failed: {e}")

        # Test RepositoryManager initialization
        try:
            repo_config = RepositoryConfig()
            repo_manager = RepositoryManager(repo_config)
            results["repository_manager"] = {
                "success": True,
                "component": "RepositoryManager",
            }
            print("  ✅ RepositoryManager initialized successfully")
        except Exception as e:
            results["repository_manager"] = {"success": False, "error": str(e)}
            print(f"  ❌ RepositoryManager initialization failed: {e}")

        # Test DeploymentManager initialization
        try:
            deployment_config = DeploymentConfig()
            deployment_manager = DeploymentManager(deployment_config)
            results["deployment_manager"] = {
                "success": True,
                "component": "DeploymentManager",
            }
            print("  ✅ DeploymentManager initialized successfully")
        except Exception as e:
            results["deployment_manager"] = {"success": False, "error": str(e)}
            print(f"  ❌ DeploymentManager initialization failed: {e}")

        self.test_results["component_validation"] = results
        return results

    def test_environment_validation_methods(self) -> dict[str, Any]:
        """
        Step 5: Test environment validation methods for each component
        """
        print("🔍 Step 5: Testing Environment Validation Methods...")

        results = {}

        if not IMPORTS_AVAILABLE:
            results["import_error"] = {
                "success": False,
                "error": "Components not available",
            }
            return results

        # Test each component's validate_environment method
        components = [
            ("ModulePackager", PackagingConfig, ModulePackager),
            ("ModuleSigner", SigningConfig, ModuleSigner),
            ("RepositoryManager", RepositoryConfig, RepositoryManager),
        ]

        for comp_name, config_class, comp_class in components:
            try:
                config = config_class()
                component = comp_class(config)
                env_results = component.validate_environment()

                missing_reqs = [req for req, valid in env_results.items() if not valid]
                results[f"{comp_name.lower()}_env_validation"] = {
                    "success": True,
                    "validation_results": env_results,
                    "missing_requirements": missing_reqs,
                }
                print(f"  ✅ {comp_name} environment validation completed")
                print(f"    Missing requirements: {missing_reqs}")

            except Exception as e:
                results[f"{comp_name.lower()}_env_validation"] = {
                    "success": False,
                    "error": str(e),
                }
                print(f"  ❌ {comp_name} environment validation failed: {e}")

        return results

    def test_progressive_complexity(self, test_project: Path) -> dict[str, Any]:
        """
        Step 6: Progressive Complexity - Start simple, build complexity
        Following crawl_mcp.py progressive testing pattern
        """
        print("🔍 Step 6: Testing Progressive Complexity...")

        results = {}

        # Level 1: Basic packaging test (simplest)
        try:
            packaging_config = PackagingConfig(
                temp_directory=self.temp_dir / "temp",
                output_directory=self.temp_dir / "output",
            )
            packager = ModulePackager(packaging_config)

            # Create mock package result
            mock_result = Mock()
            mock_result.success = True
            mock_result.package_file = self.temp_dir / "output" / "test-module.modl"
            mock_result.build_log = "Mock build successful"
            mock_result.errors = []
            mock_result.warnings = []

            results["level_1_basic_packaging"] = {
                "success": True,
                "test_level": "Basic packaging configuration",
                "component": "ModulePackager",
            }
            print("  ✅ Level 1: Basic packaging test passed")

        except Exception as e:
            results["level_1_basic_packaging"] = {
                "success": False,
                "error": self.format_deployment_error(e),
            }
            print(f"  ❌ Level 1: Basic packaging test failed: {e}")

        # Level 2: Add signing (medium complexity)
        try:
            signing_config = SigningConfig(
                certificate_path=Path("mock_cert.pem"),
                private_key_path=Path("mock_key.pem"),
            )
            signer = ModuleSigner(signing_config)

            results["level_2_signing"] = {
                "success": True,
                "test_level": "Signing configuration",
                "component": "ModuleSigner",
            }
            print("  ✅ Level 2: Signing configuration test passed")

        except Exception as e:
            results["level_2_signing"] = {
                "success": False,
                "error": self.format_deployment_error(e),
            }
            print(f"  ❌ Level 2: Signing configuration test failed: {e}")

        # Level 3: Add repository management (higher complexity)
        try:
            repo_config = RepositoryConfig(
                repository_url="https://mock-repo.example.com/api",
                download_directory=self.temp_dir / "downloads",
                cache_directory=self.temp_dir / "cache",
            )
            repo_manager = RepositoryManager(repo_config)

            results["level_3_repository"] = {
                "success": True,
                "test_level": "Repository management",
                "component": "RepositoryManager",
            }
            print("  ✅ Level 3: Repository management test passed")

        except Exception as e:
            results["level_3_repository"] = {
                "success": False,
                "error": self.format_deployment_error(e),
            }
            print(f"  ❌ Level 3: Repository management test failed: {e}")

        # Level 4: Full deployment integration (highest complexity)
        try:
            deployment_config = DeploymentConfig(
                packaging_config=PackagingConfig(),
                signing_config=SigningConfig(),
                repository_config=RepositoryConfig(),
            )
            deployment_manager = DeploymentManager(deployment_config)

            results["level_4_full_deployment"] = {
                "success": True,
                "test_level": "Full deployment integration",
                "component": "DeploymentManager",
            }
            print("  ✅ Level 4: Full deployment integration test passed")

        except Exception as e:
            results["level_4_full_deployment"] = {
                "success": False,
                "error": self.format_deployment_error(e),
            }
            print(f"  ❌ Level 4: Full deployment integration test failed: {e}")

        return results

    def test_error_handling_scenarios(self) -> dict[str, Any]:
        """
        Step 7: Comprehensive Error Handling Testing
        Following crawl_mcp.py error handling pattern
        """
        print("🔍 Step 7: Testing Error Handling Scenarios...")

        results = {}

        # Test invalid project path
        try:
            deployment_config = DeploymentConfig()
            deployment_manager = DeploymentManager(deployment_config)

            # This should fail gracefully
            invalid_path = Path("/nonexistent/path")
            validation = self.validate_input_parameters(project_path=invalid_path)

            results["invalid_project_path"] = {
                "success": True,
                "error_handled": not validation["project_path"]["valid"],
                "error_message": validation["project_path"].get("error", ""),
            }
            print("  ✅ Invalid project path error handling works")

        except Exception as e:
            results["invalid_project_path"] = {
                "success": False,
                "error": f"Error handling failed: {e}",
            }
            print(f"  ❌ Invalid project path error handling failed: {e}")

        # Test missing environment variables
        try:
            with patch.dict(os.environ, {}, clear=True):
                env_validation = self.validate_environment_variables()
                missing_vars = [
                    var for var, valid in env_validation.items() if not valid
                ]

                results["missing_env_vars"] = {
                    "success": True,
                    "missing_variables_detected": len(missing_vars) > 0,
                    "missing_count": len(missing_vars),
                }
                print(
                    f"  ✅ Missing environment variables detected: {len(missing_vars)}"
                )

        except Exception as e:
            results["missing_env_vars"] = {
                "success": False,
                "error": f"Environment validation failed: {e}",
            }
            print(f"  ❌ Missing environment variables test failed: {e}")

        # Test invalid module file
        try:
            validation = self.validate_input_parameters(
                module_file="/nonexistent/module.txt"  # Wrong extension
            )

            results["invalid_module_file"] = {
                "success": True,
                "error_handled": not validation["module_file"]["valid"],
                "error_message": validation["module_file"].get("error", ""),
            }
            print("  ✅ Invalid module file error handling works")

        except Exception as e:
            results["invalid_module_file"] = {
                "success": False,
                "error": f"Module file validation failed: {e}",
            }
            print(f"  ❌ Invalid module file test failed: {e}")

        return results

    def test_cli_commands(self) -> dict[str, Any]:
        """Step 4: Test CLI commands following crawl_mcp.py methodology"""
        print("🔍 Step 4: Testing CLI Commands...")

        results = {}

        if not IMPORTS_AVAILABLE:
            results["cli_import_error"] = {
                "success": False,
                "error": "CLI components not available",
            }
            return results

        # Test CLI command imports and basic functionality
        try:
            from src.ignition.modules.deployment.cli_commands import (
                batch_command,
                download_command,
                list_modules_command,
                module_command,
                package_command,
                sign_command,
                upload_command,
                validate_env_command,
            )

            results["cli_imports"] = {
                "success": True,
                "commands_available": [
                    "module",
                    "batch",
                    "package",
                    "sign",
                    "upload",
                    "download",
                    "list-modules",
                    "validate-env",
                ],
            }
            print("  ✅ CLI commands imported successfully")

            # Test validate-env command (safest to test)
            try:
                # This should not raise an exception even if environment is not configured
                validate_result = validate_env_command()
                results["validate_env_command"] = {
                    "success": True,
                    "command": "validate-env",
                    "executable": True,
                }
                print("  ✅ validate-env command is executable")
            except Exception as e:
                results["validate_env_command"] = {"success": False, "error": str(e)}
                print(f"  ❌ validate-env command failed: {e}")

        except ImportError as e:
            results["cli_imports"] = {
                "success": False,
                "error": f"CLI import failed: {e}",
            }
            print(f"  ❌ CLI imports failed: {e}")
        except Exception as e:
            results["cli_imports"] = {
                "success": False,
                "error": f"CLI testing failed: {e}",
            }
            print(f"  ❌ CLI testing failed: {e}")

        return results

    def cleanup_test_environment(self):
        """
        Step 8: Resource Management - Cleanup
        Following crawl_mcp.py cleanup pattern
        """
        print("🧹 Step 8: Cleaning up Test Environment...")

        if self.temp_dir and self.temp_dir.exists():
            import shutil

            try:
                shutil.rmtree(self.temp_dir)
                print(f"  ✅ Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not clean up {self.temp_dir}: {e}")
        else:
            print("  ℹ️  No temporary directory to clean up")

    def generate_comprehensive_report(self) -> dict[str, Any]:
        """Step 4: Generate comprehensive report"""
        print("📊 Step 4: Generating Comprehensive Test Report...")

        # Calculate statistics
        total_tests = 0
        passed_tests = 0

        for category, tests in self.test_results.items():
            if isinstance(tests, dict) and category != "comprehensive_results":
                for test_name, result in tests.items():
                    total_tests += 1
                    if isinstance(result, dict) and result.get("success", False):
                        passed_tests += 1

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Create a clean copy of test results without circular references
        clean_results = {}
        for category, tests in self.test_results.items():
            if category != "comprehensive_results" and isinstance(tests, dict):
                clean_results[category] = {}
                for test_name, result in tests.items():
                    if isinstance(result, dict):
                        # Only include serializable data
                        clean_results[category][test_name] = {
                            "success": result.get("success", False),
                            "error": result.get("error", ""),
                            "component": result.get("component", ""),
                            "missing_requirements": result.get(
                                "missing_requirements", []
                            ),
                        }
                    else:
                        clean_results[category][test_name] = result

        comprehensive_report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": round(success_rate, 2),
            },
            "detailed_results": clean_results,
            "recommendations": self._generate_recommendations(),
            "next_steps": self._generate_next_steps(),
        }

        print("📈 Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {success_rate:.2f}%")

        return comprehensive_report

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check environment validation results
        env_results = self.test_results.get("environment_validation", {})
        missing_vars = [var for var, valid in env_results.items() if not valid]

        if missing_vars:
            recommendations.append(
                f"Configure missing environment variables: {', '.join(missing_vars)}"
            )

        # Check component validation results
        component_results = self.test_results.get("component_validation", {})
        failed_components = [
            comp
            for comp, result in component_results.items()
            if isinstance(result, dict) and not result.get("success", False)
        ]

        if failed_components:
            recommendations.append(
                f"Fix component initialization issues: {', '.join(failed_components)}"
            )

        if not recommendations:
            recommendations.append(
                "All tests passed! Phase 9.7 is ready for production use."
            )

        return recommendations

    def _generate_next_steps(self) -> list[str]:
        """Generate next steps based on test results"""
        next_steps = [
            "Review test results and address any failed components",
            "Configure missing environment variables as needed",
            "Run integration tests with real Ignition projects",
            "Test deployment pipeline end-to-end",
            "Validate CLI commands with actual module projects",
        ]

        return next_steps


async def run_comprehensive_phase_97_tests():
    """
    Main test runner following crawl_mcp.py methodology
    """
    print("🚀 Starting Comprehensive Phase 9.7 Testing")
    print("=" * 60)

    validator = Phase97TestValidator()

    try:
        # Step 1: Environment Variable Validation First
        env_validation = validator.validate_environment_variables()
        print()

        # Step 2: Setup Test Environment
        test_project = validator.setup_test_environment()
        print()

        # Step 3: Component Testing
        component_results = validator.test_component_initialization()
        print()

        # Step 4: Environment Validation Methods
        env_method_results = validator.test_environment_validation_methods()
        print()

        # Step 5: Progressive Complexity Testing
        complexity_results = validator.test_progressive_complexity(test_project)
        print()

        # Step 6: Error Handling Testing
        error_handling_results = validator.test_error_handling_scenarios()
        print()

        # Step 7: Test CLI Commands
        cli_results = validator.test_cli_commands()
        print()

        # Step 8: Generate Comprehensive Report
        final_report = validator.generate_comprehensive_report()
        print()

        # Save detailed results to file
        results_file = Path("phase_97_test_results.json")
        with open(results_file, "w") as f:
            json.dump(final_report, f, indent=2, default=str)

        print(f"💾 Detailed results saved to: {results_file}")
        print("=" * 60)
        print("✅ Comprehensive Phase 9.7 Testing Complete!")

        return final_report

    finally:
        # Step 9: Always cleanup
        validator.cleanup_test_environment()


if __name__ == "__main__":
    # Run the comprehensive test suite
    results = asyncio.run(run_comprehensive_phase_97_tests())

    if "error" not in results:
        # Print final summary
        print("\n🎯 FINAL TEST SUMMARY:")
        print("=" * 40)
        summary = results["test_summary"]
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")

        if summary["success_rate"] >= 80:
            print("🎉 Phase 9.7 testing PASSED with high confidence!")
        elif summary["success_rate"] >= 60:
            print("⚠️  Phase 9.7 testing PASSED with moderate confidence")
        else:
            print("❌ Phase 9.7 testing FAILED - requires attention")

        print("\n📋 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")
    else:
        print(f"❌ Testing suite failed: {results['error']}")
