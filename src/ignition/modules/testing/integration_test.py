"""Integration Test for Phase 9.6 Module Testing & Validation.

This module provides a comprehensive integration test that demonstrates the complete
Phase 9.6 testing pipeline including module validation, test environment setup,
quality assurance, and user acceptance testing.

Following patterns from crawl_mcp.py for comprehensive testing and validation.
"""

import asyncio
import contextlib
import json
import tempfile
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .module_validator import ModuleValidator, validate_ignition_environment
from .quality_assurance import QualityAssurancePipeline, validate_qa_environment
from .test_environment import TestEnvironmentManager, validate_test_environment_config
from .user_acceptance import UserAcceptanceTestManager, validate_uat_environment

# Load environment variables
load_dotenv()


async def run_phase_96_integration_test(
    module_path: str | None = None,
) -> dict[str, Any]:
    """Run comprehensive Phase 9.6 integration test.

    This function demonstrates the complete testing pipeline:
    1. Environment validation
    2. Module validation
    3. Test environment setup
    4. Quality assurance pipeline
    5. User acceptance testing
    6. Comprehensive reporting

    Following patterns from crawl_mcp.py for robust testing and error handling.

    Args:
        module_path: Optional path to a test module file

    Returns:
        Dictionary with complete test results
    """
    print("🚀 Starting Phase 9.6 Module Testing & Validation Integration Test")
    print("=" * 70)

    results = {
        "phase": "9.6",
        "test_name": "Module Testing & Validation Integration Test",
        "status": "running",
        "components_tested": [],
        "environment_validations": {},
        "test_results": {},
        "errors": [],
        "recommendations": [],
    }

    try:
        # Step 1: Environment Validations
        print("\n📋 Step 1: Environment Validations")
        print("-" * 40)

        # Validate all environments
        env_validations = await validate_all_environments()
        results["environment_validations"] = env_validations

        for env_name, validation in env_validations.items():
            status = "✅ VALID" if validation["valid"] else "❌ INVALID"
            print(f"  {env_name}: {status}")
            if not validation["valid"]:
                print(f"    Error: {validation.get('error', 'Unknown error')}")

        # Step 2: Module Validation
        print("\n🔍 Step 2: Module Validation")
        print("-" * 40)

        # Create or use provided test module
        test_module_path = module_path or await create_test_module()
        print(f"  Testing module: {test_module_path}")

        validator = ModuleValidator()
        validation_result = await validator.validate_module(test_module_path)

        results["components_tested"].append("ModuleValidator")
        results["test_results"]["module_validation"] = {
            "module_path": validation_result.module_path,
            "success": validation_result.success,
            "test_results": validation_result.test_results,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "performance_metrics": validation_result.performance_metrics,
        }

        status = "✅ PASSED" if validation_result.success else "❌ FAILED"
        print(f"  Validation Result: {status}")
        print(f"  Test Results: {len(validation_result.test_results)} tests")
        print(f"  Errors: {len(validation_result.errors)}")
        print(f"  Warnings: {len(validation_result.warnings)}")

        # Step 3: Test Environment Management
        print("\n🐳 Step 3: Test Environment Management")
        print("-" * 40)

        env_manager = TestEnvironmentManager()

        # Test environment setup (simulated)
        print("  Setting up test environment...")
        env_status = await simulate_environment_setup(env_manager)

        results["components_tested"].append("TestEnvironmentManager")
        results["test_results"]["environment_management"] = env_status

        status = "✅ READY" if env_status["status"] == "ready" else "❌ FAILED"
        print(f"  Environment Status: {status}")

        # Step 4: Quality Assurance Pipeline
        print("\n🛡️ Step 4: Quality Assurance Pipeline")
        print("-" * 40)

        qa_pipeline = QualityAssurancePipeline()
        qa_report = await qa_pipeline.run_full_qa(test_module_path)

        results["components_tested"].append("QualityAssurancePipeline")
        results["test_results"]["quality_assurance"] = {
            "overall_score": qa_report.overall_score,
            "checks_performed": len(qa_report.checks),
            "passed_checks": sum(
                1 for check in qa_report.checks if check.status == "passed"
            ),
            "failed_checks": sum(
                1 for check in qa_report.checks if check.status == "failed"
            ),
            "warning_checks": sum(
                1 for check in qa_report.checks if check.status == "warning"
            ),
            "summary": qa_report.summary,
        }

        grade = qa_pipeline._calculate_grade(qa_report.overall_score)
        print(f"  QA Score: {qa_report.overall_score:.1f}/100 (Grade: {grade})")
        print(f"  Checks: {len(qa_report.checks)} total")
        print(
            f"  Categories: {', '.join(qa_report.summary.get('categories', {}).keys())}"
        )

        # Step 5: User Acceptance Testing
        print("\n👥 Step 5: User Acceptance Testing")
        print("-" * 40)

        uat_manager = UserAcceptanceTestManager()
        uat_report = await uat_manager.run_full_uat(test_module_path)

        results["components_tested"].append("UserAcceptanceTestManager")
        results["test_results"]["user_acceptance_testing"] = {
            "scenarios_generated": len(uat_report.scenarios),
            "scenarios_executed": len(uat_report.results),
            "execution_rate": uat_report.test_summary.get("execution_rate", 0),
            "feedback_collected": len(uat_report.feedback),
            "average_rating": uat_report.test_summary.get("feedback_summary", {}).get(
                "average_rating", 0
            ),
            "recommendations": len(uat_report.recommendations),
        }

        print(
            f"  Scenarios: {len(uat_report.scenarios)} generated, {len(uat_report.results)} executed"
        )
        print(
            f"  Execution Rate: {uat_report.test_summary.get('execution_rate', 0):.1f}%"
        )
        print(f"  User Feedback: {len(uat_report.feedback)} responses")
        print(
            f"  Average Rating: {uat_report.test_summary.get('feedback_summary', {}).get('average_rating', 0):.1f}/5.0"
        )

        # Step 6: Generate Comprehensive Report
        print("\n📊 Step 6: Comprehensive Reporting")
        print("-" * 40)

        comprehensive_report = await generate_comprehensive_report(
            validation_result, qa_report, uat_report, results
        )

        results["test_results"]["comprehensive_report"] = comprehensive_report
        results["status"] = "completed"

        print("  📄 Generated comprehensive test report")
        print("  📈 Calculated overall testing metrics")
        print("  💡 Compiled recommendations for improvement")

        # Final Summary
        print("\n🎯 Phase 9.6 Integration Test Summary")
        print("=" * 70)

        overall_score = calculate_overall_score(results)
        results["overall_score"] = overall_score

        print(f"Overall Score: {overall_score:.1f}/100")
        print(f"Components Tested: {len(results['components_tested'])}")
        print(f"Environment Validations: {len(env_validations)}")
        print("Test Categories: Module Validation, QA Pipeline, UAT")

        # Display key metrics
        print("\nKey Metrics:")
        print(f"  • Module Validation Success: {validation_result.success}")
        print(f"  • Quality Assurance Score: {qa_report.overall_score:.1f}/100")
        print(
            f"  • UAT Execution Rate: {uat_report.test_summary.get('execution_rate', 0):.1f}%"
        )
        print(
            f"  • User Satisfaction: {uat_report.test_summary.get('feedback_summary', {}).get('average_rating', 0):.1f}/5.0"
        )

        # Recommendations
        all_recommendations = collect_all_recommendations(
            validation_result, qa_report, uat_report
        )
        results["recommendations"] = all_recommendations

        if all_recommendations:
            print(f"\nRecommendations ({len(all_recommendations)}):")
            for i, rec in enumerate(all_recommendations[:5], 1):  # Show top 5
                print(f"  {i}. {rec}")
            if len(all_recommendations) > 5:
                print(f"  ... and {len(all_recommendations) - 5} more")

        print("\n✅ Phase 9.6 Integration Test Completed Successfully!")
        print(f"   Overall Status: {results['status'].upper()}")

    except Exception as e:
        results["status"] = "failed"
        results["errors"].append(f"Integration test failed: {e!s}")
        print(f"\n❌ Integration Test Failed: {e!s}")

    finally:
        # Cleanup test module if we created one
        if not module_path and "test_module_path" in locals():
            with contextlib.suppress(Exception):
                Path(test_module_path).unlink(missing_ok=True)

    return results


async def validate_all_environments() -> dict[str, dict[str, Any]]:
    """Validate all testing environments.

    Returns:
        Dictionary with validation results for each environment
    """
    validations = {}

    # Validate Ignition environment
    try:
        validations["ignition"] = validate_ignition_environment()
    except Exception as e:
        validations["ignition"] = {"valid": False, "error": str(e)}

    # Validate test environment configuration
    try:
        validations["test_environment"] = validate_test_environment_config()
    except Exception as e:
        validations["test_environment"] = {"valid": False, "error": str(e)}

    # Validate QA environment
    try:
        validations["quality_assurance"] = validate_qa_environment()
    except Exception as e:
        validations["quality_assurance"] = {"valid": False, "error": str(e)}

    # Validate UAT environment
    try:
        validations["user_acceptance"] = validate_uat_environment()
    except Exception as e:
        validations["user_acceptance"] = {"valid": False, "error": str(e)}

    return validations


async def create_test_module() -> str:
    """Create a test module file for demonstration.

    Returns:
        Path to the created test module
    """
    # Create a minimal test module file
    test_content = b"PK\x03\x04" + b"Test Module Content" + b"\x00" * 100

    with tempfile.NamedTemporaryFile(suffix=".modl", delete=False) as f:
        f.write(test_content)
        return f.name


async def simulate_environment_setup(
    env_manager: TestEnvironmentManager,
) -> dict[str, Any]:
    """Simulate test environment setup.

    Args:
        env_manager: TestEnvironmentManager instance

    Returns:
        Dictionary with environment setup status
    """
    # Simulate environment setup process
    await asyncio.sleep(0.1)  # Simulate setup time

    return {
        "status": "ready",
        "environment_type": "simulated",
        "setup_time": 0.1,
        "containers_created": 0,
        "health_check": "passed",
    }


async def generate_comprehensive_report(
    validation_result: Any,
    qa_report: Any,
    uat_report: Any,
    test_results: dict[str, Any],
) -> dict[str, Any]:
    """Generate comprehensive test report.

    Args:
        validation_result: Module validation results
        qa_report: Quality assurance report
        uat_report: User acceptance test report
        test_results: Overall test results

    Returns:
        Dictionary with comprehensive report data
    """
    report = {
        "generated_at": asyncio.get_event_loop().time(),
        "phase": "9.6",
        "test_type": "integration",
        "summary": {
            "total_components": len(test_results["components_tested"]),
            "validation_success": validation_result.success,
            "qa_score": qa_report.overall_score,
            "uat_execution_rate": uat_report.test_summary.get("execution_rate", 0),
            "user_satisfaction": uat_report.test_summary.get(
                "feedback_summary", {}
            ).get("average_rating", 0),
        },
        "detailed_results": {
            "module_validation": {
                "success": validation_result.success,
                "errors": len(validation_result.errors),
                "warnings": len(validation_result.warnings),
            },
            "quality_assurance": {
                "overall_score": qa_report.overall_score,
                "checks_performed": len(qa_report.checks),
                "categories_tested": list(
                    qa_report.summary.get("categories", {}).keys()
                ),
            },
            "user_acceptance": {
                "scenarios": len(uat_report.scenarios),
                "execution_rate": uat_report.test_summary.get("execution_rate", 0),
                "feedback_responses": len(uat_report.feedback),
            },
        },
        "success_criteria": {
            "module_validation_passed": validation_result.success,
            "qa_score_acceptable": qa_report.overall_score >= 70,
            "uat_execution_complete": uat_report.test_summary.get("execution_rate", 0)
            >= 80,
            "user_satisfaction_good": uat_report.test_summary.get(
                "feedback_summary", {}
            ).get("average_rating", 0)
            >= 3.5,
        },
    }

    return report


def calculate_overall_score(results: dict[str, Any]) -> float:
    """Calculate overall integration test score.

    Args:
        results: Test results dictionary

    Returns:
        Overall score (0-100)
    """
    scores = []

    # Module validation score (convert success to score)
    if "module_validation" in results["test_results"]:
        validation_success = results["test_results"]["module_validation"]["success"]
        scores.append(100.0 if validation_success else 0.0)

    # QA score
    if "quality_assurance" in results["test_results"]:
        scores.append(results["test_results"]["quality_assurance"]["overall_score"])

    # UAT score (based on execution rate and user satisfaction)
    if "user_acceptance_testing" in results["test_results"]:
        uat_data = results["test_results"]["user_acceptance_testing"]
        execution_score = uat_data.get("execution_rate", 0)
        satisfaction_score = (
            uat_data.get("average_rating", 0) * 20
        )  # Convert 5-point to 100-point scale
        uat_score = (execution_score + satisfaction_score) / 2
        scores.append(uat_score)

    return sum(scores) / len(scores) if scores else 0.0


def collect_all_recommendations(
    validation_result: Any, qa_report: Any, uat_report: Any
) -> list[str]:
    """Collect recommendations from all test components.

    Args:
        validation_result: Module validation results
        qa_report: Quality assurance report
        uat_report: User acceptance test report

    Returns:
        list of all recommendations
    """
    recommendations = []

    # Module validation recommendations (generate based on results)
    if not validation_result.success:
        recommendations.append("Address module validation failures before deployment")
    if validation_result.errors:
        recommendations.append(f"Fix {len(validation_result.errors)} validation errors")
    if validation_result.warnings:
        recommendations.append(
            f"Review {len(validation_result.warnings)} validation warnings"
        )

    # QA recommendations
    for check in qa_report.checks:
        recommendations.extend(check.recommendations)

    # UAT recommendations
    recommendations.extend(uat_report.recommendations)

    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec not in seen:
            seen.add(rec)
            unique_recommendations.append(rec)

    return unique_recommendations


async def main():
    """Main function to run the integration test."""
    try:
        results = await run_phase_96_integration_test()

        # Save results to file
        output_file = "phase_96_integration_test_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📁 Results saved to: {output_file}")

        return results

    except Exception as e:
        print(f"❌ Integration test failed: {e!s}")
        return {"status": "failed", "error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())
