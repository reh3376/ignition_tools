#!/usr/bin/env python3
"""Phase 16.2 Test Configuration

Following crawl_mcp.py methodology for test configuration and validation.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class TestConfiguration:
    """Test configuration for Phase 16.2 Specialized Expertise Modules."""
    
    # Test environment settings
    test_environment: str = "development"
    verbose_logging: bool = True
    save_test_results: bool = True
    
    # Test data paths
    test_data_dir: str = "test_data"
    results_dir: str = "test-results"
    
    # Agent configuration
    max_test_agents: int = 3
    test_timeout_seconds: int = 30
    
    # Knowledge base settings (optional)
    use_mock_knowledge_base: bool = True
    mock_regulatory_data: bool = True
    
    # Performance test settings
    concurrent_task_limit: int = 5
    performance_threshold_seconds: float = 2.0
    
    # Error simulation settings
    simulate_errors: bool = True
    error_recovery_timeout: int = 5


class Phase16_2TestValidator:
    """Validator for Phase 16.2 test environment and configuration."""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.validation_results = {}
    
    def validate_test_environment(self) -> Dict[str, any]:
        """Validate the test environment setup."""
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "config_status": {}
        }
        
        # Check required Phase 16.2 files
        required_files = [
            "src/ignition/modules/sme_agent/specialized/__init__.py",
            "src/ignition/modules/sme_agent/specialized/base_specialized_agent.py",
            "src/ignition/modules/sme_agent/specialized/distillation_whiskey_agent.py",
            "src/ignition/modules/sme_agent/specialized/pharmaceutical_agent.py",
            "src/ignition/modules/sme_agent/specialized/power_generation_agent.py",
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            results["valid"] = False
            results["errors"].append(f"Missing required files: {missing_files}")
        
        # Check Phase 16.1 foundation
        foundation_files = [
            "src/ignition/modules/sme_agent/multi_domain_architecture.py",
            "src/ignition/modules/sme_agent/agent_coordination_framework.py",
        ]
        
        missing_foundation = []
        for file_path in foundation_files:
            if not Path(file_path).exists():
                missing_foundation.append(file_path)
        
        if missing_foundation:
            results["valid"] = False
            results["errors"].append(f"Missing Phase 16.1 foundation: {missing_foundation}")
        
        # Check test directories
        test_dirs = [self.config.test_data_dir, self.config.results_dir]
        for test_dir in test_dirs:
            if not Path(test_dir).exists():
                try:
                    Path(test_dir).mkdir(parents=True, exist_ok=True)
                    results["warnings"].append(f"Created missing test directory: {test_dir}")
                except Exception as e:
                    results["errors"].append(f"Could not create test directory {test_dir}: {e}")
                    results["valid"] = False
        
        # Check optional environment variables
        optional_env_vars = [
            "WHISKEY_DISTILLATION_KNOWLEDGE_BASE_PATH",
            "PHARMACEUTICAL_MANUFACTURING_KNOWLEDGE_BASE_PATH",
            "POWER_GENERATION_KNOWLEDGE_BASE_PATH",
            "SPECIALIZED_AGENTS_ENABLED",
        ]
        
        env_status = {}
        for var in optional_env_vars:
            env_status[var] = os.getenv(var) is not None
        
        results["config_status"]["environment_variables"] = env_status
        results["config_status"]["test_configuration"] = {
            "test_environment": self.config.test_environment,
            "max_test_agents": self.config.max_test_agents,
            "test_timeout": self.config.test_timeout_seconds,
            "use_mock_data": self.config.use_mock_knowledge_base
        }
        
        self.validation_results = results
        return results
    
    def validate_imports(self) -> Dict[str, any]:
        """Validate that all required imports work."""
        import_results = {
            "valid": True,
            "successful_imports": [],
            "failed_imports": []
        }
        
        # Test imports
        imports_to_test = [
            ("BaseSpecializedAgent", "src.ignition.modules.sme_agent.specialized.base_specialized_agent"),
            ("DistillationWhiskeyAgent", "src.ignition.modules.sme_agent.specialized.distillation_whiskey_agent"),
            ("PharmaceuticalAgent", "src.ignition.modules.sme_agent.specialized.pharmaceutical_agent"),
            ("PowerGenerationAgent", "src.ignition.modules.sme_agent.specialized.power_generation_agent"),
            ("DomainType", "src.ignition.modules.sme_agent.multi_domain_architecture"),
            ("AgentTask", "src.ignition.modules.sme_agent.multi_domain_architecture"),
        ]
        
        for class_name, module_path in imports_to_test:
            try:
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
                import_results["successful_imports"].append(f"{class_name} from {module_path}")
            except ImportError as e:
                import_results["failed_imports"].append(f"{class_name} from {module_path}: {e}")
                import_results["valid"] = False
            except AttributeError as e:
                import_results["failed_imports"].append(f"{class_name} not found in {module_path}: {e}")
                import_results["valid"] = False
        
        return import_results
    
    def get_test_summary(self) -> Dict[str, any]:
        """Get a summary of test validation results."""
        env_validation = self.validate_test_environment()
        import_validation = self.validate_imports()
        
        # Convert config to dict for JSON serialization
        config_dict = {
            "test_environment": self.config.test_environment,
            "verbose_logging": self.config.verbose_logging,
            "save_test_results": self.config.save_test_results,
            "test_data_dir": self.config.test_data_dir,
            "results_dir": self.config.results_dir,
            "max_test_agents": self.config.max_test_agents,
            "test_timeout_seconds": self.config.test_timeout_seconds,
            "use_mock_knowledge_base": self.config.use_mock_knowledge_base,
            "mock_regulatory_data": self.config.mock_regulatory_data,
            "concurrent_task_limit": self.config.concurrent_task_limit,
            "performance_threshold_seconds": self.config.performance_threshold_seconds,
            "simulate_errors": self.config.simulate_errors,
            "error_recovery_timeout": self.config.error_recovery_timeout
        }
        
        return {
            "overall_valid": env_validation["valid"] and import_validation["valid"],
            "environment_validation": env_validation,
            "import_validation": import_validation,
            "test_configuration": config_dict,
            "recommendations": self._generate_recommendations(env_validation, import_validation)
        }
    
    def _generate_recommendations(self, env_results: Dict, import_results: Dict) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if not env_results["valid"]:
            recommendations.append("Fix environment validation errors before running tests")
        
        if not import_results["valid"]:
            recommendations.append("Resolve import errors - check Phase 16.2 implementation")
        
        if env_results["warnings"]:
            recommendations.append("Review environment warnings for potential issues")
        
        if not os.getenv("SPECIALIZED_AGENTS_ENABLED"):
            recommendations.append("Consider setting SPECIALIZED_AGENTS_ENABLED=true for full testing")
        
        return recommendations


# Default test configuration
DEFAULT_TEST_CONFIG = TestConfiguration()


def get_test_config() -> TestConfiguration:
    """Get test configuration from environment or defaults."""
    config = TestConfiguration()
    
    # Override with environment variables if present
    config.test_environment = os.getenv("TEST_ENVIRONMENT", config.test_environment)
    config.verbose_logging = os.getenv("VERBOSE_LOGGING", "true").lower() == "true"
    config.save_test_results = os.getenv("SAVE_TEST_RESULTS", "true").lower() == "true"
    config.test_timeout_seconds = int(os.getenv("TEST_TIMEOUT_SECONDS", str(config.test_timeout_seconds)))
    config.use_mock_knowledge_base = os.getenv("USE_MOCK_KNOWLEDGE_BASE", "true").lower() == "true"
    
    return config


def validate_phase_16_2_test_setup() -> Dict[str, any]:
    """Validate the complete Phase 16.2 test setup."""
    config = get_test_config()
    validator = Phase16_2TestValidator(config)
    return validator.get_test_summary()


if __name__ == "__main__":
    # Run validation
    validation_summary = validate_phase_16_2_test_setup()
    
    print("🔍 Phase 16.2 Test Setup Validation")
    print("=" * 50)
    
    if validation_summary["overall_valid"]:
        print("✅ Test setup validation: PASSED")
    else:
        print("❌ Test setup validation: FAILED")
    
    print(f"\n📋 Environment Validation:")
    env_val = validation_summary["environment_validation"]
    print(f"  Valid: {env_val['valid']}")
    if env_val["errors"]:
        print(f"  Errors: {env_val['errors']}")
    if env_val["warnings"]:
        print(f"  Warnings: {env_val['warnings']}")
    
    print(f"\n📦 Import Validation:")
    import_val = validation_summary["import_validation"]
    print(f"  Valid: {import_val['valid']}")
    print(f"  Successful: {len(import_val['successful_imports'])}")
    print(f"  Failed: {len(import_val['failed_imports'])}")
    
    if validation_summary["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in validation_summary["recommendations"]:
            print(f"  • {rec}")
    
    print(f"\n🎯 Ready for Phase 16.2 testing: {'Yes' if validation_summary['overall_valid'] else 'No'}") 