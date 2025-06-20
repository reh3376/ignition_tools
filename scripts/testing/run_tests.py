#!/usr/bin/env python3
"""Test runner script for IGN Scripts with Docker integration."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], capture_output: bool = False) -> tuple:
    """Run a command and return the result."""
    print(f"🔧 Running: {' '.join(cmd)}")

    try:
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd)
            return result.returncode, "", ""
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return 1, "", str(e)


def build_docker_image() -> bool:
    """Build the Docker image for testing."""
    print("🐳 Building Docker image...")
    cmd = ["docker", "build", "-t", "ign-scripts-test", "."]
    returncode, stdout, stderr = run_command(cmd, capture_output=True)

    if returncode == 0:
        print("✅ Docker image built successfully")
        return True
    else:
        print(f"❌ Failed to build Docker image: {stderr}")
        return False


def run_unit_tests() -> bool:
    """Run unit tests in Docker container."""
    print("🧪 Running unit tests...")
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/app",
        "ign-scripts-test",
        "python",
        "-m",
        "pytest",
        "tests/",
        "-v",
        "-m",
        "unit",
        "--tb=short",
        "--log-cli-level=INFO",
    ]

    returncode, _, _ = run_command(cmd)

    if returncode == 0:
        print("✅ Unit tests passed")
        return True
    else:
        print("❌ Unit tests failed")
        return False


def run_integration_tests() -> bool:
    """Run integration tests in Docker container."""
    print("🔗 Running integration tests...")
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/app",
        "ign-scripts-test",
        "python",
        "-m",
        "pytest",
        "tests/",
        "-v",
        "-m",
        "integration",
        "--tb=short",
        "--log-cli-level=INFO",
    ]

    returncode, _, _ = run_command(cmd)

    if returncode == 0:
        print("✅ Integration tests passed")
        return True
    else:
        print("❌ Integration tests failed")
        return False


def run_performance_tests() -> bool:
    """Run performance tests in Docker container."""
    print("⚡ Running performance tests...")
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/app",
        "-v",
        f"{Path.cwd()}/test-results:/app/test-results",
        "ign-scripts-test",
        "python",
        "-m",
        "pytest",
        "tests/test_performance.py",
        "-v",
        "--benchmark-only",
        "--benchmark-json=/app/test-results/benchmark.json",
    ]

    returncode, _, _ = run_command(cmd)

    if returncode == 0:
        print("✅ Performance tests completed")
        return True
    else:
        print("❌ Performance tests failed")
        return False


def run_ui_tests() -> bool:
    """Run UI tests in Docker container."""
    print("🖥️ Running UI tests...")
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/app",
        "ign-scripts-test",
        "python",
        "-m",
        "pytest",
        "tests/test_ui.py",
        "-v",
        "-m",
        "ui",
        "--tb=short",
        "--log-cli-level=INFO",
    ]

    returncode, _, _ = run_command(cmd)

    if returncode == 0:
        print("✅ UI tests passed")
        return True
    else:
        print("❌ UI tests failed")
        return False


def run_coverage_tests() -> bool:
    """Run tests with coverage reporting."""
    print("📊 Running tests with coverage...")

    # Ensure directories exist
    Path("coverage-reports").mkdir(exist_ok=True)
    Path("test-results").mkdir(exist_ok=True)

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/app",
        "-v",
        f"{Path.cwd()}/coverage-reports:/app/coverage-reports",
        "-v",
        f"{Path.cwd()}/test-results:/app/test-results",
        "ign-scripts-test",
        "python",
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=html:/app/coverage-reports/",
        "--cov-report=xml:/app/coverage-reports/coverage.xml",
        "--html=/app/test-results/report.html",
        "--tb=short",
    ]

    returncode, _, _ = run_command(cmd)

    if returncode == 0:
        print("✅ Coverage tests completed")
        print(f"📈 Coverage report: {Path.cwd()}/coverage-reports/index.html")
        print(f"📋 Test report: {Path.cwd()}/test-results/report.html")
        return True
    else:
        print("❌ Coverage tests failed")
        return False


def run_linting() -> bool:
    """Run code quality checks."""
    print("🔍 Running code quality checks...")

    # Create a temporary container for linting
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/app",
        "ign-scripts-test",
        "sh",
        "-c",
        "cd /app && python -m black --check src tests && python -m isort --check-only src tests && python -m flake8 src tests",
    ]

    returncode, stdout, stderr = run_command(cmd, capture_output=True)

    if returncode == 0:
        print("✅ Code quality checks passed")
        return True
    else:
        print("❌ Code quality issues found:")
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
        return False


def run_security_scan() -> bool:
    """Run security scanning with bandit."""
    print("🔒 Running security scan...")

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/app",
        "ign-scripts-test",
        "python",
        "-m",
        "bandit",
        "-r",
        "src/",
        "-f",
        "json",
        "-o",
        "/app/test-results/security.json",
    ]

    returncode, _, _ = run_command(cmd)

    if returncode == 0:
        print("✅ Security scan completed")
        return True
    else:
        print("⚠️ Security scan found issues (check test-results/security.json)")
        return True  # Don't fail the build for security warnings


def view_logs(container_name: str) -> None:
    """View logs from a Docker container."""
    print(f"📋 Viewing logs for {container_name}...")
    cmd = ["docker", "logs", container_name]
    run_command(cmd)


def clean_docker_resources() -> None:
    """Clean up Docker resources."""
    print("🧹 Cleaning Docker resources...")

    # Stop any running test containers
    subprocess.run(
        ["docker", "stop", "ign_scripts_test"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["docker", "stop", "ign_scripts_dev"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["docker", "stop", "ign_scripts_benchmark"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
    )

    # Remove containers
    subprocess.run(
        ["docker", "rm", "ign_scripts_test"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["docker", "rm", "ign_scripts_dev"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["docker", "rm", "ign_scripts_benchmark"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
    )

    print("✅ Docker cleanup completed")


def run_full_test_suite() -> bool:
    """Run the complete test suite."""
    print("🚀 Running full test suite...")

    # Track results
    results = []

    # Build image first
    if not build_docker_image():
        return False

    # Run all test categories
    test_functions = [
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
        ("UI Tests", run_ui_tests),
        ("Performance Tests", run_performance_tests),
        ("Code Quality", run_linting),
        ("Security Scan", run_security_scan),
        ("Coverage Report", run_coverage_tests),
    ]

    for test_name, test_func in test_functions:
        print(f"\n{'=' * 50}")
        print(f"Running {test_name}")
        print("=" * 50)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'=' * 50}")
    print("TEST SUITE SUMMARY")
    print("=" * 50)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False

    print(f"\nOverall result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed


def watch_logs() -> None:
    """Watch Docker container logs in real-time."""
    print("👀 Watching Docker logs (Ctrl+C to stop)...")

    containers = ["ign_scripts_test", "ign_scripts_dev", "ign_scripts_benchmark"]

    for container in containers:
        # Check if container is running
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", f"name={container}"],
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():
            print(f"📋 Logs for {container}:")
            try:
                subprocess.run(["docker", "logs", "-f", container])
            except KeyboardInterrupt:
                print(f"\n⏹️ Stopped watching {container}")
                break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="IGN Scripts Test Runner")
    parser.add_argument("--build", action="store_true", help="Build Docker image")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--ui", action="store_true", help="Run UI tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--lint", action="store_true", help="Run code quality checks")
    parser.add_argument("--security", action="store_true", help="Run security scan")
    parser.add_argument("--all", action="store_true", help="Run full test suite")
    parser.add_argument("--clean", action="store_true", help="Clean Docker resources")
    parser.add_argument("--logs", action="store_true", help="Watch container logs")
    parser.add_argument("--view-logs", type=str, help="View logs for specific container")

    args = parser.parse_args()

    if not any(vars(args).values()):
        # Default to running all tests if no specific option is provided
        args.all = True

    success = True

    try:
        if args.clean:
            clean_docker_resources()

        if args.build:
            success &= build_docker_image()

        if args.unit:
            success &= run_unit_tests()

        if args.integration:
            success &= run_integration_tests()

        if args.ui:
            success &= run_ui_tests()

        if args.performance:
            success &= run_performance_tests()

        if args.coverage:
            success &= run_coverage_tests()

        if args.lint:
            success &= run_linting()

        if args.security:
            success &= run_security_scan()

        if args.all:
            success = run_full_test_suite()

        if args.logs:
            watch_logs()

        if args.view_logs:
            view_logs(args.view_logs)

    except KeyboardInterrupt:
        print("\n⏹️ Test execution interrupted by user")
        success = False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
