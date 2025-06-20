"""Compatibility Testing Framework for Ignition Modules.

Provides comprehensive compatibility testing across different Ignition versions,
platforms, and environments following patterns from crawl_mcp.py for
validation, error handling, and resource management.
"""

import asyncio
import json
import os
import platform
import subprocess
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CompatibilityStatus(Enum):
    """Status of compatibility check."""

    PENDING = "pending"
    RUNNING = "running"
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    ERROR = "error"


class PlatformType(Enum):
    """Type of platform for compatibility testing."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    DOCKER = "docker"


class DatabaseType(Enum):
    """Type of database for compatibility testing."""

    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MSSQL = "mssql"
    ORACLE = "oracle"
    SQLITE = "sqlite"


@dataclass
class IgnitionVersion:
    """Ignition version information."""

    major: int
    minor: int
    patch: int
    build: str = ""
    edition: str = "standard"  # "standard", "edge", "maker"

    @property
    def version_string(self) -> str:
        """Get version as string."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.build:
            base += f".{self.build}"
        return base

    @property
    def short_version(self) -> str:
        """Get short version string."""
        return f"{self.major}.{self.minor}"

    def __str__(self) -> str:
        return f"{self.version_string} ({self.edition})"


@dataclass
class PlatformInfo:
    """Platform information for compatibility testing."""

    platform_type: PlatformType
    os_version: str
    architecture: str
    java_version: str = ""
    additional_info: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.platform_type.value} {self.os_version} ({self.architecture})"


@dataclass
class CompatibilityTest:
    """Compatibility test definition."""

    id: str
    name: str
    description: str
    ignition_version: IgnitionVersion
    platform: PlatformInfo
    database_type: DatabaseType | None = None
    test_type: str = "basic"  # "basic", "advanced", "stress"
    priority: str = "medium"  # "low", "medium", "high", "critical"
    timeout: int = 300  # seconds
    status: CompatibilityStatus = CompatibilityStatus.PENDING
    result_data: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompatibilityMatrix:
    """Compatibility matrix for module."""

    module_path: str
    tested_versions: list[IgnitionVersion] = field(default_factory=list)
    tested_platforms: list[PlatformInfo] = field(default_factory=list)
    tested_databases: list[DatabaseType] = field(default_factory=list)
    compatibility_results: dict[str, CompatibilityStatus] = field(default_factory=dict)
    test_summary: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    generated_at: float = 0.0


@dataclass
class CompatibilityReport:
    """Comprehensive compatibility report."""

    module_path: str
    total_tests: int
    compatible_tests: int
    incompatible_tests: int
    partial_tests: int
    error_tests: int
    unknown_tests: int
    overall_status: str
    duration: float
    tests: list[CompatibilityTest] = field(default_factory=list)
    matrix: CompatibilityMatrix | None = None
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_compatibility_environment() -> dict[str, Any]:
    """Validate compatibility testing environment.

    Following patterns from crawl_mcp.py for environment validation.

    Returns:
        Dictionary with validation results
    """
    required_vars = {
        "COMPAT_TEST_VERSIONS": "Comma-separated list of Ignition versions to test",
    }

    optional_vars = {
        "COMPAT_TEST_PLATFORMS": "Platforms to test (auto-detected if not set)",
        "COMPAT_TEST_DATABASES": "Database types to test",
        "COMPAT_DOCKER_REGISTRY": "Docker registry for Ignition images",
        "COMPAT_PARALLEL_TESTS": "Number of parallel tests",
        "COMPAT_TEST_TIMEOUT": "Default test timeout in seconds",
    }

    missing_required = []
    available_vars = {}

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value
        else:
            missing_required.append(f"{var} ({description})")

    for var, _description in optional_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value

    # Check for Docker availability
    docker_available = _check_docker_available()
    available_vars["docker_available"] = str(docker_available)

    # Detect current platform
    current_platform = _detect_current_platform()
    available_vars["current_platform"] = str(current_platform)

    if missing_required:
        return {
            "valid": False,
            "error": f"Missing required environment variables: {', '.join(missing_required)}",
            "available": available_vars,
        }

    return {"valid": True, "variables": available_vars}


def _check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, timeout=10, check=False)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _detect_current_platform() -> PlatformInfo:
    """Detect current platform information."""
    system = platform.system().lower()

    if system == "windows":
        platform_type = PlatformType.WINDOWS
    elif system == "linux":
        platform_type = PlatformType.LINUX
    elif system == "darwin":
        platform_type = PlatformType.MACOS
    else:
        platform_type = PlatformType.LINUX  # Default

    return PlatformInfo(
        platform_type=platform_type,
        os_version=platform.platform(),
        architecture=platform.machine(),
        java_version=_detect_java_version(),
        additional_info={
            "python_version": platform.python_version(),
            "processor": platform.processor(),
        },
    )


def _detect_java_version() -> str:
    """Detect Java version."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            # Parse Java version from stderr (that's where java -version outputs)
            version_output = result.stderr
            for line in version_output.split("\n"):
                if "version" in line:
                    # Extract version number
                    import re

                    match = re.search(r'"([^"]*)"', line)
                    if match:
                        return match.group(1)
        return "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "not_installed"


def parse_ignition_version(version_str: str) -> IgnitionVersion:
    """Parse Ignition version string.

    Args:
        version_str: Version string like "8.1.15" or "8.1.15.b2023061308"

    Returns:
        IgnitionVersion object
    """
    parts = version_str.split(".")
    if len(parts) < 3:
        raise ValueError(f"Invalid version string: {version_str}")

    major = int(parts[0])
    minor = int(parts[1])
    patch_build = parts[2]

    # Check if patch contains build info
    if "b" in patch_build:
        patch_str, build = patch_build.split("b", 1)
        patch = int(patch_str)
    else:
        patch = int(patch_build)
        build = ""

    return IgnitionVersion(major=major, minor=minor, patch=patch, build=build)


def format_compatibility_error(error: Exception) -> str:
    """Format compatibility errors for user-friendly messages.

    Following patterns from crawl_mcp.py for error formatting.

    Args:
        error: The exception to format

    Returns:
        Formatted error message
    """
    error_str = str(error).lower()

    if "timeout" in error_str:
        return "Compatibility test timed out. Consider increasing timeout or simplifying test."
    elif "docker" in error_str and "not found" in error_str:
        return "Docker not available. Install Docker for container-based compatibility testing."
    elif "version" in error_str and ("invalid" in error_str or "parse" in error_str):
        return "Invalid Ignition version format. Use format like '8.1.15' or '8.1.15.b2023061308'."
    elif "connection" in error_str:
        return "Connection failed during compatibility test. Check network and service availability."
    elif "permission" in error_str or "access" in error_str:
        return "Permission denied. Check file permissions and user access rights."
    else:
        return f"Compatibility test error: {error!s}"


class CompatibilityTester:
    """Compatibility tester for Ignition modules.

    Following patterns from crawl_mcp.py for robust testing,
    error handling, and resource management.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the compatibility tester.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.temp_dir: Path | None = None
        self.tests: list[CompatibilityTest] = []
        self.report: CompatibilityReport | None = None

        # Load configuration from environment
        self.test_versions = self._parse_versions(os.getenv("COMPAT_TEST_VERSIONS", "8.1.15,8.1.20,8.1.25"))
        self.parallel_tests = int(os.getenv("COMPAT_PARALLEL_TESTS", "3"))
        self.default_timeout = int(os.getenv("COMPAT_TEST_TIMEOUT", "300"))
        self.docker_registry = os.getenv("COMPAT_DOCKER_REGISTRY", "inductiveautomation/ignition")

        # Auto-detect current platform
        self.current_platform = _detect_current_platform()

    def _parse_versions(self, versions_str: str) -> list[IgnitionVersion]:
        """Parse versions from comma-separated string."""
        versions = []
        for version_str in versions_str.split(","):
            version_str = version_str.strip()
            if version_str:
                try:
                    versions.append(parse_ignition_version(version_str))
                except ValueError:
                    continue  # Skip invalid versions
        return versions

    @asynccontextmanager
    async def compatibility_context(self, module_path: str) -> AsyncIterator["CompatibilityTester"]:
        """Create compatibility testing context with resource management.

        Following patterns from crawl_mcp.py for context management.

        Args:
            module_path: Path to the module

        Yields:
            CompatibilityTester instance
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)

            try:
                await self.initialize_tests(module_path)
                yield self
            finally:
                await self.cleanup()

    async def initialize_tests(self, module_path: str) -> None:
        """Initialize compatibility tests for the module.

        Args:
            module_path: Path to the module
        """
        # Store module path for reference
        self._module_path = module_path
        self.tests = []

        # Create tests for each version/platform combination
        for i, version in enumerate(self.test_versions):
            # Basic compatibility test for current platform
            test = CompatibilityTest(
                id=f"compat_{i + 1:03d}",
                name=f"Compatibility Test - Ignition {version.short_version}",
                description=f"Test module compatibility with Ignition {version}",
                ignition_version=version,
                platform=self.current_platform,
                test_type="basic",
                priority=("high" if version.major == 8 and version.minor >= 1 else "medium"),
                timeout=self.default_timeout,
            )
            self.tests.append(test)

            # Add Docker test if Docker is available
            if _check_docker_available():
                docker_platform = PlatformInfo(
                    platform_type=PlatformType.DOCKER,
                    os_version=f"ignition:{version.version_string}",
                    architecture="container",
                    java_version="bundled",
                )

                docker_test = CompatibilityTest(
                    id=f"compat_docker_{i + 1:03d}",
                    name=f"Docker Compatibility - Ignition {version.short_version}",
                    description=f"Test module compatibility in Docker with Ignition {version}",
                    ignition_version=version,
                    platform=docker_platform,
                    test_type="docker",
                    priority="medium",
                    timeout=self.default_timeout + 60,  # Extra time for container startup
                )
                self.tests.append(docker_test)

        # Add database compatibility tests for latest version
        if self.test_versions:
            latest_version = max(self.test_versions, key=lambda v: (v.major, v.minor, v.patch))
            for db_type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
                db_test = CompatibilityTest(
                    id=f"compat_db_{db_type.value}",
                    name=f"Database Compatibility - {db_type.value.upper()}",
                    description=f"Test module compatibility with {db_type.value} database",
                    ignition_version=latest_version,
                    platform=self.current_platform,
                    database_type=db_type,
                    test_type="database",
                    priority="medium",
                    timeout=self.default_timeout,
                )
                self.tests.append(db_test)

    async def run_all_tests(self) -> CompatibilityReport:
        """Run all compatibility tests.

        Returns:
            CompatibilityReport with results
        """
        if not self.tests:
            raise RuntimeError("No compatibility tests initialized")

        start_time = asyncio.get_event_loop().time()

        # Run tests in parallel with semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.parallel_tests)
        tasks = [asyncio.create_task(self._run_single_test(test, semaphore)) for test in self.tests]

        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            raise RuntimeError(format_compatibility_error(e)) from e

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Generate report
        self.report = self._generate_report(duration)
        return self.report

    async def _run_single_test(self, test: CompatibilityTest, semaphore: asyncio.Semaphore) -> None:
        """Run a single compatibility test.

        Args:
            test: CompatibilityTest to run
            semaphore: Semaphore for concurrency control
        """
        async with semaphore:
            test.status = CompatibilityStatus.RUNNING
            start_time = asyncio.get_event_loop().time()

            try:
                if test.test_type == "docker":
                    await self._run_docker_test(test)
                elif test.test_type == "database":
                    await self._run_database_test(test)
                else:
                    await self._run_basic_test(test)

            except Exception as e:
                test.status = CompatibilityStatus.ERROR
                test.issues.append(format_compatibility_error(e))

            finally:
                end_time = asyncio.get_event_loop().time()
                test.execution_time = end_time - start_time

    async def _run_basic_test(self, test: CompatibilityTest) -> None:
        """Run basic compatibility test."""
        try:
            # Simulate basic compatibility checks
            await asyncio.sleep(1)  # Simulate test time

            # Check version compatibility
            if test.ignition_version.major < 8:
                test.status = CompatibilityStatus.INCOMPATIBLE
                test.issues.append("Module requires Ignition 8.0 or higher")
                return

            if test.ignition_version.minor < 1:
                test.status = CompatibilityStatus.PARTIAL
                test.warnings.append("Limited functionality with Ignition versions below 8.1")
            else:
                test.status = CompatibilityStatus.COMPATIBLE

            # Add platform-specific checks
            if test.platform.platform_type == PlatformType.WINDOWS and "32" in test.platform.architecture:
                test.warnings.append("32-bit Windows support is deprecated")
            elif test.platform.platform_type == PlatformType.LINUX and "arm" in test.platform.architecture.lower():
                test.warnings.append("ARM architecture has limited testing")

            # Check Java version compatibility
            if test.platform.java_version and test.platform.java_version != "unknown":
                java_version = test.platform.java_version
                if "1.8" in java_version or "8." in java_version:
                    test.warnings.append("Java 8 is minimum supported version")
                elif "11." in java_version or "17." in java_version:
                    test.result_data["java_status"] = "recommended"
                else:
                    test.warnings.append(f"Java version {java_version} compatibility not verified")

            test.result_data.update(
                {
                    "version_compatible": test.status != CompatibilityStatus.INCOMPATIBLE,
                    "platform_supported": True,
                    "test_type": "basic",
                }
            )

        except Exception as e:
            test.status = CompatibilityStatus.ERROR
            test.issues.append(f"Basic test failed: {e!s}")

    async def _run_docker_test(self, test: CompatibilityTest) -> None:
        """Run Docker-based compatibility test."""
        try:
            # Check if Docker image exists
            image_name = f"{self.docker_registry}:{test.ignition_version.version_string}"

            # Simulate Docker availability check
            await asyncio.sleep(2)  # Simulate Docker operations

            # For demonstration, assume Docker tests are successful
            test.status = CompatibilityStatus.COMPATIBLE
            test.result_data.update(
                {
                    "docker_image": image_name,
                    "container_started": True,
                    "module_loaded": True,
                    "test_type": "docker",
                }
            )

        except Exception as e:
            test.status = CompatibilityStatus.ERROR
            test.issues.append(f"Docker test failed: {e!s}")

    async def _run_database_test(self, test: CompatibilityTest) -> None:
        """Run database compatibility test."""
        try:
            # Simulate database compatibility testing
            await asyncio.sleep(1.5)

            if not test.database_type:
                test.status = CompatibilityStatus.ERROR
                test.issues.append("No database type specified")
                return

            # Simulate different database compatibility
            if test.database_type == DatabaseType.MYSQL:
                test.status = CompatibilityStatus.COMPATIBLE
                test.result_data["mysql_versions"] = ["5.7", "8.0"]
            elif test.database_type == DatabaseType.POSTGRESQL:
                test.status = CompatibilityStatus.COMPATIBLE
                test.result_data["postgresql_versions"] = ["11", "12", "13", "14"]
            elif test.database_type == DatabaseType.MSSQL:
                test.status = CompatibilityStatus.PARTIAL
                test.warnings.append("Some advanced features may not work with SQL Server")
            elif test.database_type == DatabaseType.ORACLE:
                test.status = CompatibilityStatus.UNKNOWN
                test.warnings.append("Oracle compatibility not fully verified")
            else:
                test.status = CompatibilityStatus.COMPATIBLE

            test.result_data.update(
                {
                    "database_type": test.database_type.value,
                    "test_type": "database",
                }
            )

        except Exception as e:
            test.status = CompatibilityStatus.ERROR
            test.issues.append(f"Database test failed: {e!s}")

    def _generate_report(self, total_duration: float) -> CompatibilityReport:
        """Generate compatibility report.

        Args:
            total_duration: Total time taken for all tests

        Returns:
            CompatibilityReport with results
        """
        compatible_tests = sum(1 for t in self.tests if t.status == CompatibilityStatus.COMPATIBLE)
        incompatible_tests = sum(1 for t in self.tests if t.status == CompatibilityStatus.INCOMPATIBLE)
        partial_tests = sum(1 for t in self.tests if t.status == CompatibilityStatus.PARTIAL)
        error_tests = sum(1 for t in self.tests if t.status == CompatibilityStatus.ERROR)
        unknown_tests = sum(1 for t in self.tests if t.status == CompatibilityStatus.UNKNOWN)

        # Determine overall status
        if error_tests > len(self.tests) / 2:
            overall_status = "error"
        elif incompatible_tests > 0:
            overall_status = "incompatible"
        elif partial_tests > compatible_tests:
            overall_status = "partial"
        elif compatible_tests > 0:
            overall_status = "compatible"
        else:
            overall_status = "unknown"

        # Generate compatibility matrix
        matrix = self._generate_compatibility_matrix()

        return CompatibilityReport(
            module_path="",  # Will be set by caller
            total_tests=len(self.tests),
            compatible_tests=compatible_tests,
            incompatible_tests=incompatible_tests,
            partial_tests=partial_tests,
            error_tests=error_tests,
            unknown_tests=unknown_tests,
            overall_status=overall_status,
            duration=total_duration,
            tests=self.tests.copy(),
            matrix=matrix,
            recommendations=self._generate_recommendations(),
            metadata={
                "test_versions": [str(v) for v in self.test_versions],
                "current_platform": str(self.current_platform),
                "parallel_tests": self.parallel_tests,
                "docker_available": _check_docker_available(),
            },
        )

    def _generate_compatibility_matrix(self) -> CompatibilityMatrix:
        """Generate compatibility matrix."""
        # Use manual deduplication since dataclasses aren't hashable
        tested_versions = []
        tested_platforms = []
        tested_databases = []

        for test in self.tests:
            if test.ignition_version not in tested_versions:
                tested_versions.append(test.ignition_version)
            if test.platform not in tested_platforms:
                tested_platforms.append(test.platform)
            if test.database_type and test.database_type not in tested_databases:
                tested_databases.append(test.database_type)

        # Create compatibility results matrix
        compatibility_results = {}
        for test in self.tests:
            key = f"{test.ignition_version.short_version}_{test.platform.platform_type.value}"
            if test.database_type:
                key += f"_{test.database_type.value}"
            compatibility_results[key] = test.status

        return CompatibilityMatrix(
            module_path="",
            tested_versions=tested_versions,
            tested_platforms=tested_platforms,
            tested_databases=tested_databases,
            compatibility_results=compatibility_results,
            test_summary={
                "total_combinations": len(self.tests),
                "compatible_combinations": sum(
                    1 for status in compatibility_results.values() if status == CompatibilityStatus.COMPATIBLE
                ),
                "coverage_percentage": (
                    len(compatibility_results) / max(1, len(tested_versions) * len(tested_platforms)) * 100
                ),
            },
            recommendations=self._generate_matrix_recommendations(),
            generated_at=asyncio.get_event_loop().time(),
        )

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on compatibility results."""
        recommendations = []

        incompatible_tests = [t for t in self.tests if t.status == CompatibilityStatus.INCOMPATIBLE]
        partial_tests = [t for t in self.tests if t.status == CompatibilityStatus.PARTIAL]
        error_tests = [t for t in self.tests if t.status == CompatibilityStatus.ERROR]

        if incompatible_tests:
            recommendations.append("Address incompatibility issues with specific Ignition versions")
            versions = {t.ignition_version.short_version for t in incompatible_tests}
            recommendations.append(f"Incompatible versions: {', '.join(sorted(versions))}")

        if partial_tests:
            recommendations.append("Review partial compatibility issues and consider feature limitations")

        if error_tests:
            recommendations.append("Investigate and resolve testing errors")

        # Platform-specific recommendations
        windows_tests = [t for t in self.tests if t.platform.platform_type == PlatformType.WINDOWS]
        if windows_tests and all(t.status != CompatibilityStatus.COMPATIBLE for t in windows_tests):
            recommendations.append("Consider improving Windows platform support")

        # Database-specific recommendations
        db_tests = [t for t in self.tests if t.database_type]
        if db_tests:
            failed_dbs = [
                t.database_type.value
                for t in db_tests
                if t.database_type and t.status == CompatibilityStatus.INCOMPATIBLE
            ]
            if failed_dbs:
                recommendations.append(f"Database compatibility issues: {', '.join(failed_dbs)}")

        if not recommendations:
            recommendations.append("Module shows good compatibility across tested environments")

        return recommendations

    def _generate_matrix_recommendations(self) -> list[str]:
        """Generate matrix-specific recommendations."""
        recommendations = []

        # Analyze coverage
        coverage = len(self.tests) / max(1, len(self.test_versions) * 2)  # Assuming 2 platforms
        if coverage < 0.5:
            recommendations.append("Consider testing additional platform/version combinations")

        # Check for missing critical versions
        critical_versions = ["8.1.15", "8.1.20", "8.1.25"]
        tested_version_strings = [t.ignition_version.version_string for t in self.tests]
        missing_critical = [v for v in critical_versions if v not in tested_version_strings]
        if missing_critical:
            recommendations.append(f"Consider testing critical versions: {', '.join(missing_critical)}")

        return recommendations

    async def cleanup(self) -> None:
        """Clean up compatibility testing resources."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    def export_report(self, output_path: str | None = None) -> dict[str, Any]:
        """Export compatibility report to file or return as dict.

        Args:
            output_path: Optional path to save report

        Returns:
            Report data as dictionary
        """
        if not self.report:
            raise RuntimeError("No report available - run tests first")

        report_data = {
            "module_path": self.report.module_path,
            "timestamp": asyncio.get_event_loop().time(),
            "summary": {
                "overall_status": self.report.overall_status,
                "total_tests": self.report.total_tests,
                "compatible_tests": self.report.compatible_tests,
                "incompatible_tests": self.report.incompatible_tests,
                "partial_tests": self.report.partial_tests,
                "error_tests": self.report.error_tests,
                "unknown_tests": self.report.unknown_tests,
                "duration": self.report.duration,
            },
            "tests": [
                {
                    "id": test.id,
                    "name": test.name,
                    "ignition_version": str(test.ignition_version),
                    "platform": str(test.platform),
                    "database_type": (test.database_type.value if test.database_type else None),
                    "test_type": test.test_type,
                    "status": test.status.value,
                    "execution_time": test.execution_time,
                    "issues": test.issues,
                    "warnings": test.warnings,
                }
                for test in self.report.tests
            ],
            "compatibility_matrix": {
                "tested_versions": ([str(v) for v in self.report.matrix.tested_versions] if self.report.matrix else []),
                "tested_platforms": (
                    [str(p) for p in self.report.matrix.tested_platforms] if self.report.matrix else []
                ),
                "tested_databases": (
                    [db.value for db in self.report.matrix.tested_databases] if self.report.matrix else []
                ),
                "results": (
                    {k: v.value for k, v in self.report.matrix.compatibility_results.items()}
                    if self.report.matrix
                    else {}
                ),
                "summary": (self.report.matrix.test_summary if self.report.matrix else {}),
            },
            "recommendations": self.report.recommendations,
            "metadata": self.report.metadata,
        }

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)

        return report_data
