#!/usr/bin/env python3
"""
Master Testing Suite Coordinator

Comprehensive testing framework that coordinates all testing activities
for the Enhanced Graph Database project. Provides multiple testing modes
and integrates all testing components.
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(
            command, shell=True, cwd=project_root, capture_output=False, text=True
        )
        success = result.returncode == 0

        if success:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")

        return success
    except Exception as e:
        print(f"❌ {description} failed with error: {e!s}")
        return False


def health_check() -> bool:
    """Run health check."""
    return run_command(
        "python scripts/testing/periodic_health_check.py", "Health Check"
    )


def full_test_suite() -> bool:
    """Run full comprehensive test suite."""
    return run_command(
        "python scripts/testing/test_graph_functions.py", "Full Test Suite"
    )


def task_validation(task_id: int) -> bool:
    """Run task-specific validation."""
    return run_command(
        f"python scripts/testing/automated_task_validation.py {task_id}",
        f"Task {task_id} Validation",
    )


def progress_check() -> bool:
    """Run progress completion check."""
    return run_command(
        "python scripts/utilities/get_completion_stats.py", "Progress Statistics"
    )


def print_banner():
    """Print testing suite banner."""
    print("=" * 70)
    print("🧪 **ENHANCED GRAPH DATABASE TESTING SUITE**")
    print("=" * 70)
    print(f"📅 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 **Database**: http://localhost:7474")
    print("🔐 **Credentials**: neo4j / ignition-graph")
    print("=" * 70)


def print_usage():
    """Print usage information."""
    print("\nUsage: python run_testing_suite.py [mode] [options]")
    print("\nAvailable modes:")
    print("  health              - Quick health check")
    print("  full                - Complete test suite")
    print("  task <id>           - Validate specific task completion")
    print("  progress            - Show completion progress")
    print("  all                 - Run all tests (health + full + progress)")
    print("  dev                 - Development mode (health + progress)")
    print("\nExamples:")
    print("  python run_testing_suite.py health")
    print("  python run_testing_suite.py task 1")
    print("  python run_testing_suite.py all")
    print("  python run_testing_suite.py dev")


def main():
    """Main testing coordinator."""
    print_banner()

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    start_time = time.time()
    overall_success = True

    if mode == "health":
        print("\n🏥 **HEALTH CHECK MODE**")
        overall_success = health_check()

    elif mode == "full":
        print("\n🔬 **FULL TEST SUITE MODE**")
        overall_success = full_test_suite()

    elif mode == "task":
        if len(sys.argv) < 3:
            print("Error: Task ID required")
            print("Example: python run_testing_suite.py task 1")
            sys.exit(1)

        try:
            task_id = int(sys.argv[2])
            print(f"\n🎯 **TASK {task_id} VALIDATION MODE**")
            overall_success = task_validation(task_id)
        except ValueError:
            print("Error: Task ID must be a number")
            sys.exit(1)

    elif mode == "progress":
        print("\n📊 **PROGRESS CHECK MODE**")
        overall_success = progress_check()

    elif mode == "all":
        print("\n🚀 **COMPREHENSIVE TESTING MODE**")
        print("Running all tests: Health Check → Full Suite → Progress Check")

        tests = [
            ("Health Check", health_check),
            ("Full Test Suite", full_test_suite),
            ("Progress Check", progress_check),
        ]

        passed_tests = 0
        for _test_name, test_function in tests:
            if test_function():
                passed_tests += 1
            else:
                overall_success = False

        print(
            f"\n📋 **Comprehensive Testing Summary**: {passed_tests}/{len(tests)} passed"
        )

    elif mode == "dev":
        print("\n⚡ **DEVELOPMENT MODE**")
        print("Running development tests: Health Check → Progress Check")

        tests = [("Health Check", health_check), ("Progress Check", progress_check)]

        passed_tests = 0
        for _test_name, test_function in tests:
            if test_function():
                passed_tests += 1
            else:
                overall_success = False

        print(
            f"\n📋 **Development Testing Summary**: {passed_tests}/{len(tests)} passed"
        )

    else:
        print(f"Error: Unknown mode '{mode}'")
        print_usage()
        sys.exit(1)

    # Final summary
    execution_time = time.time() - start_time

    print("\n" + "=" * 70)
    print("🎯 **TESTING SUITE SUMMARY**")
    print("=" * 70)

    if overall_success:
        print("✅ **ALL TESTS PASSED**")
        print("🎉 **Database is healthy and functioning correctly**")
    else:
        print("❌ **SOME TESTS FAILED**")
        print("⚠️ **Please review failed tests and take corrective action**")

    print(f"⏱️ **Total Execution Time**: {execution_time:.2f}s")
    print(f"📅 **Completed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Recommendations
    print("\n💡 **Next Steps**:")
    if overall_success:
        if mode in ["health", "dev"]:
            print("   • Continue development - system is healthy")
            print("   • Consider running full test suite before major releases")
        elif mode == "full":
            print("   • All systems validated - ready for production")
            print("   • Database integrity confirmed")
        elif mode.startswith("task"):
            print("   • Task validation passed - proceed to next task")
            print("   • Update documentation and roadmap")
    else:
        print("   • Review failed tests for specific issues")
        print("   • Check database connectivity and data integrity")
        print("   • Run individual test components for debugging")
        print("   • Consult logs for detailed error information")

    print("\n🔗 **Quick Commands**:")
    print("   Health Check:     python run_testing_suite.py health")
    print("   Development:      python run_testing_suite.py dev")
    print("   Task Validation:  python run_testing_suite.py task <id>")
    print("   Full Suite:       python run_testing_suite.py full")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
