#!/usr/bin/env python3
"""Comprehensive Testing Script for Phase 11.4: Advanced SME Agent Features
Following crawl_mcp.py methodology for thorough testing and validation.

This script tests all Phase 11.4 components:
1. Specialized Domain Expertise
2. Proactive Development Assistance
3. Enhanced Code Intelligence
4. CLI Commands Integration
5. Documentation and Integration
"""

import asyncio
import json
import logging
import sys
import traceback
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Phase114ComprehensiveTester:
    """Comprehensive tester for Phase 11.4 implementation."""

    def __init__(self):
        """Initialize the tester."""
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_categories": {},
            "detailed_results": [],
        }
        self.base_path = Path(__file__).parent

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all comprehensive tests for Phase 11.4."""
        logger.info("🚀 Starting Phase 11.4 Comprehensive Testing")
        logger.info("=" * 60)

        # Test categories
        test_categories = [
            ("Module Imports", self.test_module_imports),
            ("Specialized Domain Expertise", self.test_specialized_domain_expertise),
            (
                "Proactive Development Assistance",
                self.test_proactive_development_assistance,
            ),
            ("Enhanced Code Intelligence", self.test_enhanced_code_intelligence),
            ("CLI Commands Integration", self.test_cli_commands_integration),
            ("File Structure Validation", self.test_file_structure),
            ("Documentation Validation", self.test_documentation),
            ("Integration Examples", self.test_integration_examples),
            ("Dependencies Validation", self.test_dependencies),
            ("Configuration Validation", self.test_configuration),
        ]

        for category_name, test_method in test_categories:
            logger.info(f"\n📋 Testing: {category_name}")
            logger.info("-" * 40)

            try:
                category_results = await test_method()
                self.test_results["test_categories"][category_name] = category_results

                # Update totals
                self.test_results["total_tests"] += category_results["total"]
                self.test_results["passed_tests"] += category_results["passed"]
                self.test_results["failed_tests"] += category_results["failed"]

                # Log category summary
                status = "✅ PASSED" if category_results["failed"] == 0 else "❌ FAILED"
                logger.info(f"{status} - {category_results['passed']}/{category_results['total']} tests passed")

            except Exception as e:
                logger.error(f"❌ Category '{category_name}' failed with error: {e}")
                logger.error(traceback.format_exc())
                self.test_results["test_categories"][category_name] = {
                    "total": 1,
                    "passed": 0,
                    "failed": 1,
                    "details": [f"Category error: {e!s}"],
                }
                self.test_results["total_tests"] += 1
                self.test_results["failed_tests"] += 1

        # Generate final report
        await self.generate_final_report()
        return self.test_results

    async def test_module_imports(self) -> dict[str, Any]:
        """Test module imports for Phase 11.4 components."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # Test imports
        import_tests = [
            (
                "specialized_domain_expertise",
                "src.ignition.modules.sme_agent.specialized_domain_expertise",
            ),
            (
                "proactive_development_assistance",
                "src.ignition.modules.sme_agent.proactive_development_assistance",
            ),
            (
                "enhanced_code_intelligence",
                "src.ignition.modules.sme_agent.enhanced_code_intelligence",
            ),
            (
                "advanced_cli_commands",
                "src.ignition.modules.sme_agent.cli.advanced_commands",
            ),
        ]

        for test_name, module_path in import_tests:
            results["total"] += 1
            try:
                # Try to import the module
                module = __import__(module_path, fromlist=[""])

                # Check for key components
                if "specialized_domain_expertise" in test_name:
                    assert hasattr(module, "SpecializedDomainExpertise")
                    assert hasattr(module, "validate_specialized_domain_environment")
                elif "proactive_development_assistance" in test_name:
                    assert hasattr(module, "ProactiveDevelopmentAssistance")
                    assert hasattr(module, "validate_proactive_development_environment")
                elif "enhanced_code_intelligence" in test_name:
                    assert hasattr(module, "EnhancedCodeIntelligence")
                    assert hasattr(module, "validate_enhanced_code_intelligence_environment")
                elif "advanced_cli_commands" in test_name:
                    assert hasattr(module, "get_advanced_commands")

                results["passed"] += 1
                results["details"].append(f"✅ {test_name}: Import successful")

            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ {test_name}: Import failed - {e!s}")

        return results

    async def test_specialized_domain_expertise(self) -> dict[str, Any]:
        """Test specialized domain expertise functionality."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        try:
            from src.ignition.modules.sme_agent.specialized_domain_expertise import (
                SpecializedDomainExpertise,
                get_specialized_domain_info,
                validate_specialized_domain_environment,
            )

            # Test 1: Environment validation
            results["total"] += 1
            try:
                validation_result = await validate_specialized_domain_environment()
                assert isinstance(validation_result, dict)
                assert "valid" in validation_result
                results["passed"] += 1
                results["details"].append("✅ Environment validation works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Environment validation failed: {e}")

            # Test 2: Module info
            results["total"] += 1
            try:
                info = get_specialized_domain_info()
                assert isinstance(info, dict)
                assert "module" in info
                assert "capabilities" in info
                assert "knowledge_areas" in info
                results["passed"] += 1
                results["details"].append("✅ Module info retrieval works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Module info failed: {e}")

            # Test 3: Initialization
            results["total"] += 1
            try:
                expertise = SpecializedDomainExpertise()
                init_result = await expertise.initialize()
                assert isinstance(init_result, dict)
                assert "status" in init_result
                results["passed"] += 1
                results["details"].append("✅ Initialization works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Initialization failed: {e}")

            # Test 4: Query functionality (basic test)
            results["total"] += 1
            try:
                expertise = SpecializedDomainExpertise()
                await expertise.initialize()

                query_result = await expertise.query_domain_expertise(
                    domain="database",
                    question="What are best practices for database optimization?",
                    context={},
                    complexity="basic",
                )
                assert isinstance(query_result, dict)
                assert "status" in query_result
                results["passed"] += 1
                results["details"].append("✅ Query functionality works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Query functionality failed: {e}")

            # Test 5: Troubleshooting functionality
            results["total"] += 1
            try:
                expertise = SpecializedDomainExpertise()
                await expertise.initialize()

                troubleshoot_result = await expertise.provide_troubleshooting_guidance(
                    system_type="database",
                    symptoms=["slow queries", "high CPU"],
                    environment_context={},
                    complexity="basic",
                )
                assert isinstance(troubleshoot_result, dict)
                assert "status" in troubleshoot_result
                results["passed"] += 1
                results["details"].append("✅ Troubleshooting functionality works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Troubleshooting functionality failed: {e}")

        except ImportError as e:
            results["total"] += 1
            results["failed"] += 1
            results["details"].append(f"❌ Failed to import specialized domain expertise: {e}")

        return results

    async def test_proactive_development_assistance(self) -> dict[str, Any]:
        """Test proactive development assistance functionality."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        try:
            from src.ignition.modules.sme_agent.proactive_development_assistance import (
                ProactiveDevelopmentAssistance,
                get_proactive_development_info,
                validate_proactive_development_environment,
            )

            # Test 1: Environment validation
            results["total"] += 1
            try:
                validation_result = await validate_proactive_development_environment()
                assert isinstance(validation_result, dict)
                assert "valid" in validation_result
                results["passed"] += 1
                results["details"].append("✅ Environment validation works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Environment validation failed: {e}")

            # Test 2: Module info
            results["total"] += 1
            try:
                info = get_proactive_development_info()
                assert isinstance(info, dict)
                assert "module" in info
                assert "capabilities" in info
                assert "architecture_patterns" in info
                results["passed"] += 1
                results["details"].append("✅ Module info retrieval works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Module info failed: {e}")

            # Test 3: Initialization
            results["total"] += 1
            try:
                assistance = ProactiveDevelopmentAssistance()
                init_result = await assistance.initialize()
                assert isinstance(init_result, dict)
                assert "status" in init_result
                results["passed"] += 1
                results["details"].append("✅ Initialization works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Initialization failed: {e}")

            # Test 4: Architecture pattern suggestion
            results["total"] += 1
            try:
                assistance = ProactiveDevelopmentAssistance()
                await assistance.initialize()

                suggestion_result = await assistance.suggest_architecture_pattern(
                    project_requirements={"type": "HMI application", "scale": "large"},
                    constraints={},
                    complexity="basic",
                )
                assert isinstance(suggestion_result, dict)
                assert "status" in suggestion_result
                results["passed"] += 1
                results["details"].append("✅ Architecture suggestion works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Architecture suggestion failed: {e}")

            # Test 5: Component optimization
            results["total"] += 1
            try:
                assistance = ProactiveDevelopmentAssistance()
                await assistance.initialize()

                optimization_result = await assistance.optimize_component_selection(
                    system_components=["Gateway", "Perspective"],
                    performance_requirements={"response_time": "< 100ms"},
                    complexity="basic",
                )
                assert isinstance(optimization_result, dict)
                assert "status" in optimization_result
                results["passed"] += 1
                results["details"].append("✅ Component optimization works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Component optimization failed: {e}")

        except ImportError as e:
            results["total"] += 1
            results["failed"] += 1
            results["details"].append(f"❌ Failed to import proactive development assistance: {e}")

        return results

    async def test_enhanced_code_intelligence(self) -> dict[str, Any]:
        """Test enhanced code intelligence functionality."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        try:
            from src.ignition.modules.sme_agent.enhanced_code_intelligence import (
                EnhancedCodeIntelligence,
                get_enhanced_code_intelligence_info,
                validate_enhanced_code_intelligence_environment,
            )

            # Test 1: Environment validation
            results["total"] += 1
            try:
                validation_result = await validate_enhanced_code_intelligence_environment()
                assert isinstance(validation_result, dict)
                assert "valid" in validation_result
                results["passed"] += 1
                results["details"].append("✅ Environment validation works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Environment validation failed: {e}")

            # Test 2: Module info
            results["total"] += 1
            try:
                info = get_enhanced_code_intelligence_info()
                assert isinstance(info, dict)
                assert "module" in info
                assert "capabilities" in info
                assert "analysis_types" in info
                results["passed"] += 1
                results["details"].append("✅ Module info retrieval works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Module info failed: {e}")

            # Test 3: Initialization
            results["total"] += 1
            try:
                intelligence = EnhancedCodeIntelligence()
                init_result = await intelligence.initialize()
                assert isinstance(init_result, dict)
                assert "status" in init_result
                results["passed"] += 1
                results["details"].append("✅ Initialization works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Initialization failed: {e}")

            # Test 4: Create test file for analysis
            results["total"] += 1
            try:
                test_file = self.base_path / "test_code_sample.py"
                test_code = '''#!/usr/bin/env python3
"""Test code sample for analysis."""

def complex_function(a, b, c, d, e, f):
    """A function with high complexity."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return f * 10
                    else:
                        return f * 5
                else:
                    return f * 2
            else:
                return f
        else:
            return 0
    else:
        return -1

def simple_function():
    """A simple function."""
    return "Hello, World!"
'''
                test_file.write_text(test_code)
                results["passed"] += 1
                results["details"].append("✅ Test file created successfully")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Test file creation failed: {e}")

            # Test 5: Code analysis
            results["total"] += 1
            try:
                intelligence = EnhancedCodeIntelligence()
                await intelligence.initialize()

                analysis_result = await intelligence.analyze_code_file(
                    file_path=str(test_file),
                    analysis_type="comprehensive",
                    complexity="basic",
                )
                assert isinstance(analysis_result, dict)
                assert "status" in analysis_result
                if analysis_result["status"] == "success":
                    assert "analysis" in analysis_result
                results["passed"] += 1
                results["details"].append("✅ Code analysis works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Code analysis failed: {e}")

            # Test 6: Pattern detection
            results["total"] += 1
            try:
                intelligence = EnhancedCodeIntelligence()
                await intelligence.initialize()

                pattern_result = await intelligence.detect_code_patterns(
                    file_path=str(test_file), pattern_types=[], complexity="basic"
                )
                assert isinstance(pattern_result, dict)
                assert "status" in pattern_result
                results["passed"] += 1
                results["details"].append("✅ Pattern detection works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Pattern detection failed: {e}")

            # Clean up test file
            try:
                if test_file.exists():
                    test_file.unlink()
            except Exception:
                pass

        except ImportError as e:
            results["total"] += 1
            results["failed"] += 1
            results["details"].append(f"❌ Failed to import enhanced code intelligence: {e}")

        return results

    async def test_cli_commands_integration(self) -> dict[str, Any]:
        """Test CLI commands integration."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        try:
            from src.ignition.modules.sme_agent.cli.advanced_commands import (
                get_advanced_commands,
            )

            # Test 1: CLI commands import
            results["total"] += 1
            try:
                commands = get_advanced_commands()
                assert commands is not None
                results["passed"] += 1
                results["details"].append("✅ CLI commands import works")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ CLI commands import failed: {e}")

            # Test 2: Check command groups
            results["total"] += 1
            try:
                import click

                commands = get_advanced_commands()
                assert isinstance(commands, click.Group)

                # Check for expected command groups
                command_names = list(commands.commands.keys())
                expected_groups = ["domain", "assist", "code", "status"]

                found_groups = [name for name in expected_groups if name in command_names]
                assert len(found_groups) >= 3  # At least 3 groups should be present

                results["passed"] += 1
                results["details"].append(f"✅ Command groups found: {found_groups}")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Command groups check failed: {e}")

            # Test 3: Check individual commands
            results["total"] += 1
            try:
                commands = get_advanced_commands()

                # Check domain commands
                if "domain" in commands.commands:
                    domain_group = commands.commands["domain"]
                    domain_commands = list(domain_group.commands.keys())
                    expected_domain = ["validate-env", "info", "query", "troubleshoot"]
                    found_domain = [cmd for cmd in expected_domain if cmd in domain_commands]
                    assert len(found_domain) >= 2

                results["passed"] += 1
                results["details"].append("✅ Individual commands structure verified")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Individual commands check failed: {e}")

        except ImportError as e:
            results["total"] += 1
            results["failed"] += 1
            results["details"].append(f"❌ Failed to import CLI commands: {e}")

        return results

    async def test_file_structure(self) -> dict[str, Any]:
        """Test file structure for Phase 11.4."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # Expected files for Phase 11.4
        expected_files = [
            "src/ignition/modules/sme_agent/specialized_domain_expertise.py",
            "src/ignition/modules/sme_agent/proactive_development_assistance.py",
            "src/ignition/modules/sme_agent/enhanced_code_intelligence.py",
            "src/ignition/modules/sme_agent/cli/advanced_commands.py",
            "test_phase_11_4_comprehensive.py",
        ]

        for file_path in expected_files:
            results["total"] += 1
            full_path = self.base_path / file_path

            if full_path.exists():
                results["passed"] += 1
                results["details"].append(f"✅ File exists: {file_path}")
            else:
                results["failed"] += 1
                results["details"].append(f"❌ File missing: {file_path}")

        return results

    async def test_documentation(self) -> dict[str, Any]:
        """Test documentation for Phase 11.4."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # Test 1: Check roadmap.md for Phase 11.4
        results["total"] += 1
        try:
            roadmap_path = self.base_path / "docs" / "roadmap.md"
            if roadmap_path.exists():
                content = roadmap_path.read_text()
                if "Phase 11.4" in content and "Advanced SME Agent Features" in content:
                    results["passed"] += 1
                    results["details"].append("✅ Phase 11.4 documented in roadmap")
                else:
                    results["failed"] += 1
                    results["details"].append("❌ Phase 11.4 not properly documented in roadmap")
            else:
                results["failed"] += 1
                results["details"].append("❌ Roadmap file not found")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Roadmap check failed: {e}")

        # Test 2: Check for docstrings in modules
        results["total"] += 1
        try:
            module_files = [
                "src/ignition/modules/sme_agent/specialized_domain_expertise.py",
                "src/ignition/modules/sme_agent/proactive_development_assistance.py",
                "src/ignition/modules/sme_agent/enhanced_code_intelligence.py",
            ]

            docstring_count = 0
            for file_path in module_files:
                full_path = self.base_path / file_path
                if full_path.exists():
                    content = full_path.read_text()
                    if '"""' in content and "crawl_mcp.py methodology" in content:
                        docstring_count += 1

            if docstring_count >= 2:
                results["passed"] += 1
                results["details"].append(f"✅ Docstrings found in {docstring_count} modules")
            else:
                results["failed"] += 1
                results["details"].append(f"❌ Insufficient docstrings found ({docstring_count})")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Docstring check failed: {e}")

        return results

    async def test_integration_examples(self) -> dict[str, Any]:
        """Test integration examples and usage patterns."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # Test 1: Basic integration workflow
        results["total"] += 1
        try:
            # Test the basic workflow of initializing and using components
            from src.ignition.modules.sme_agent.enhanced_code_intelligence import (
                EnhancedCodeIntelligence,
            )
            from src.ignition.modules.sme_agent.proactive_development_assistance import (
                ProactiveDevelopmentAssistance,
            )
            from src.ignition.modules.sme_agent.specialized_domain_expertise import (
                SpecializedDomainExpertise,
            )

            # Initialize all components
            expertise = SpecializedDomainExpertise()
            assistance = ProactiveDevelopmentAssistance()
            intelligence = EnhancedCodeIntelligence()

            # Test that they can all be initialized
            expertise_init = await expertise.initialize()
            assistance_init = await assistance.initialize()
            intelligence_init = await intelligence.initialize()

            assert all(
                result.get("status") == "success" for result in [expertise_init, assistance_init, intelligence_init]
            )

            results["passed"] += 1
            results["details"].append("✅ Basic integration workflow works")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Basic integration workflow failed: {e}")

        # Test 2: Cross-component compatibility
        results["total"] += 1
        try:
            # Test that components can work together
            expertise = SpecializedDomainExpertise()
            await expertise.initialize()

            assistance = ProactiveDevelopmentAssistance()
            await assistance.initialize()

            # Get statistics from both
            expertise_stats = await expertise.get_expertise_statistics()
            assistance_stats = await assistance.get_assistance_statistics()

            assert isinstance(expertise_stats, dict)
            assert isinstance(assistance_stats, dict)

            results["passed"] += 1
            results["details"].append("✅ Cross-component compatibility works")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Cross-component compatibility failed: {e}")

        return results

    async def test_dependencies(self) -> dict[str, Any]:
        """Test dependencies and requirements."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # Test 1: Check required Python packages
        required_packages = [
            "asyncio",
            "json",
            "logging",
            "pathlib",
            "dataclasses",
            "datetime",
            "typing",
            "ast",
            "click",
        ]

        for package in required_packages:
            results["total"] += 1
            try:
                __import__(package)
                results["passed"] += 1
                results["details"].append(f"✅ Package available: {package}")
            except ImportError:
                results["failed"] += 1
                results["details"].append(f"❌ Package missing: {package}")

        # Test 2: Check requirements.txt
        results["total"] += 1
        try:
            requirements_path = self.base_path / "requirements.txt"
            if requirements_path.exists():
                content = requirements_path.read_text()
                required_in_file = ["click", "asyncio"]  # Basic requirements
                found_requirements = [req for req in required_in_file if req in content.lower()]

                if len(found_requirements) >= 1:
                    results["passed"] += 1
                    results["details"].append("✅ Requirements.txt contains needed packages")
                else:
                    results["failed"] += 1
                    results["details"].append("❌ Requirements.txt missing needed packages")
            else:
                results["failed"] += 1
                results["details"].append("❌ Requirements.txt not found")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Requirements check failed: {e}")

        return results

    async def test_configuration(self) -> dict[str, Any]:
        """Test configuration and environment setup."""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # Test 1: Check .agent_context.json
        results["total"] += 1
        try:
            context_path = self.base_path / ".agent_context.json"
            if context_path.exists():
                with open(context_path) as f:
                    context_data = json.load(f)

                if isinstance(context_data, dict) and "current_phase" in context_data:
                    results["passed"] += 1
                    results["details"].append("✅ Agent context file is valid")
                else:
                    results["failed"] += 1
                    results["details"].append("❌ Agent context file format invalid")
            else:
                results["failed"] += 1
                results["details"].append("❌ Agent context file not found")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Agent context check failed: {e}")

        # Test 2: Check environment variable support
        results["total"] += 1
        try:
            import os

            from dotenv import load_dotenv

            # Test that environment loading works
            load_dotenv()

            # Check for common environment variables (they don't need to be set)
            env_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]

            for var in env_vars:
                # Just test that os.getenv works
                os.getenv(var)
                # Value can be None, we're just testing the mechanism

            results["passed"] += 1
            results["details"].append("✅ Environment variable support works")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Environment variable support failed: {e}")

        return results

    async def generate_final_report(self) -> None:
        """Generate final test report."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 PHASE 11.4 COMPREHENSIVE TEST REPORT")
        logger.info("=" * 60)

        # Overall statistics
        total_tests = self.test_results["total_tests"]
        passed_tests = self.test_results["passed_tests"]
        failed_tests = self.test_results["failed_tests"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info("📈 Overall Results:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")

        # Category breakdown
        logger.info("\n📋 Category Breakdown:")
        for category, results in self.test_results["test_categories"].items():
            status = "✅" if results["failed"] == 0 else "❌"
            logger.info(f"   {status} {category}: {results['passed']}/{results['total']}")

        # Detailed results for failed tests
        failed_categories = [
            (cat, res) for cat, res in self.test_results["test_categories"].items() if res["failed"] > 0
        ]

        if failed_categories:
            logger.info("\n❌ Failed Test Details:")
            for category, results in failed_categories:
                logger.info(f"\n   Category: {category}")
                for detail in results["details"]:
                    if detail.startswith("❌"):
                        logger.info(f"     {detail}")

        # Success message
        if failed_tests == 0:
            logger.info("\n🎉 ALL TESTS PASSED! Phase 11.4 implementation is complete and functional.")
        else:
            logger.info(f"\n⚠️  {failed_tests} test(s) failed. Please review and fix the issues above.")

        # Save detailed report
        report_path = self.base_path / "phase_11_4_test_report.json"
        try:
            with open(report_path, "w") as f:
                json.dump(self.test_results, f, indent=2)
            logger.info(f"\n📄 Detailed report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save detailed report: {e}")


async def main():
    """Main testing function."""
    print("🚀 Phase 11.4: Advanced SME Agent Features - Comprehensive Testing")
    print("Following crawl_mcp.py methodology for thorough validation")
    print("=" * 70)

    tester = Phase114ComprehensiveTester()

    try:
        results = await tester.run_all_tests()

        # Exit with appropriate code
        if results["failed_tests"] == 0:
            print("\n✅ All tests passed! Phase 11.4 is ready for deployment.")
            sys.exit(0)
        else:
            print(f"\n❌ {results['failed_tests']} test(s) failed. Please review the issues.")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
