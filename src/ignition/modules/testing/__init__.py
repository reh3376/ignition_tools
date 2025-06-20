"""Module Testing & Validation Framework.

This package provides comprehensive testing infrastructure for Ignition modules,
including Docker-based testing environments, quality assurance pipelines,
and user acceptance testing scenarios.

Following patterns from crawl_mcp.py for validation, error handling, and testing.
"""

from .module_validator import (
    ModuleValidator,
    ValidationContext,
    ValidationResult,
    validate_ignition_environment,
)
from .quality_assurance import (
    QualityAssurancePipeline,
    QualityCheck,
    QualityReport,
    validate_qa_environment,
)
from .test_environment import (
    DockerTestEnvironment,
    TestEnvironment,
    TestEnvironmentConfig,
    TestEnvironmentManager,
    TestEnvironmentStatus,
    validate_test_environment_config,
)
from .user_acceptance import (
    TestResult,
    TestScenario,
    UATReport,
    UserAcceptanceTestManager,
    UserFeedback,
    validate_uat_environment,
)

__all__ = [
    "DockerTestEnvironment",
    "ModuleValidator",
    "QualityAssurancePipeline",
    "QualityCheck",
    "QualityReport",
    "TestEnvironment",
    "TestEnvironmentConfig",
    "TestEnvironmentManager",
    "TestEnvironmentStatus",
    "TestResult",
    "TestScenario",
    "UATReport",
    "UserAcceptanceTestManager",
    "UserFeedback",
    "ValidationContext",
    "ValidationResult",
    "validate_ignition_environment",
    "validate_qa_environment",
    "validate_test_environment_config",
    "validate_uat_environment",
]
