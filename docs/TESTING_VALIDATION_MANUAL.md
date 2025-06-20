# IGN Scripts - Testing & Validation Manual

## 📋 Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Environment Setup](#environment-setup)
4. [Module Testing Framework](#module-testing-framework)
5. [Quality Assurance Pipeline](#quality-assurance-pipeline)
6. [User Acceptance Testing](#user-acceptance-testing)
7. [Integration Testing](#integration-testing)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Best Practices](#best-practices)
10. [Advanced Usage](#advanced-usage)

---

## 🎯 Overview

This manual provides comprehensive guidance for testing and validating Ignition modules using the IGN Scripts Testing & Validation framework. Following patterns from `crawl_mcp.py`, this framework provides robust error handling, environment validation, and step-by-step guidance for successful testing workflows.

### Key Features

- **🔍 Module Validation**: Comprehensive module structure and compatibility testing
- **🐳 Test Environment Management**: Docker-based and local test environments
- **🛡️ Quality Assurance**: Automated code quality, security, and documentation analysis
- **👥 User Acceptance Testing**: Automated scenario execution and feedback collection
- **📊 Integration Testing**: End-to-end testing with comprehensive reporting
- **🔧 Environment Validation**: Automatic validation of required tools and configurations

---

## 🚀 Getting Started

### Prerequisites

Before starting, ensure you have the following installed:

```bash
# Required tools
- Python 3.11+
- Docker (optional, for containerized testing)
- Ignition Gateway (for local testing)
- Git (for version control integration)
```

### Quick Start

1. **Initialize the agent knowledge system** (required for each new session):
   ```python
   from ignition.code_intelligence import initialize_agent_knowledge
   context = initialize_agent_knowledge()
   ```

2. **Run a basic module validation**:
   ```python
   from ignition.modules.testing import ModuleValidator

   validator = ModuleValidator()
   result = await validator.validate_module("path/to/your/module.modl")
   print(f"Validation result: {result.success}")
   ```

3. **Execute integration test**:
   ```python
   from ignition.modules.testing import integration_test

   await integration_test()
   ```

---

## 🔧 Environment Setup

### Environment Variables

Following the security guidelines from the project, all configuration uses environment variables:

```bash
# Create .env file in project root
cp config/env.example .env

# Edit .env file with your configuration
nano .env
```

#### Required Environment Variables

```bash
# Module Testing
IGNITION_TEST_VERSION=8.1.25           # Ignition version for testing
TEST_GATEWAY_URL=http://localhost:8088  # Test Gateway URL
IGNITION_TEST_LICENSE=your_license_key  # Optional: Test license key
TEST_TIMEOUT=300                        # Test timeout in seconds (optional)
DOCKER_TEST_ENABLED=true               # Enable Docker-based testing (optional)

# Quality Assurance
QA_TOOLS_PATH=/opt/qa-tools            # Path to QA analysis tools (optional)
SONAR_SCANNER_PATH=/opt/sonar-scanner   # SonarQube scanner path (optional)

# User Acceptance Testing
UAT_TEST_GATEWAY_URL=http://localhost:8088  # Gateway URL for UAT testing
UAT_TEST_USERNAME=test_user                 # Username for UAT testing
UAT_SCREENSHOT_DIR=./screenshots            # Directory for UAT screenshots (optional)
UAT_REPORT_DIR=./reports                    # Directory for UAT reports (optional)
UAT_FEEDBACK_API=https://api.feedback.com   # API endpoint for feedback collection (optional)

# Neo4j Configuration (for knowledge graph features)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
USE_KNOWLEDGE_GRAPH=true
```

### Environment Validation

The framework automatically validates your environment before running tests:

```python
from ignition.modules.testing import ModuleValidator

validator = ModuleValidator()

# This will check all required environment variables and tools
validation_result = await validator.validate_environment()

if not validation_result.is_valid:
    print("Environment validation failed:")
    for error in validation_result.errors:
        print(f"  ❌ {error}")
else:
    print("✅ Environment validation passed")
```

---

## 🔍 Module Testing Framework

### Basic Module Validation

The `ModuleValidator` class provides comprehensive module validation following patterns from `crawl_mcp.py`:

```python
import asyncio
from pathlib import Path
from ignition.modules.testing import ModuleValidator

async def validate_my_module():
    """Example module validation workflow."""

    # Initialize validator
    validator = ModuleValidator()

    # Module path - must be a .modl file
    module_path = "path/to/your/module.modl"

    # Validate the module
    async with validator.create_validation_context(module_path) as context:
        result = await validator.validate_module_comprehensive(context)

        # Check results
        if result.success:
            print(f"✅ Module validation passed!")
            print(f"Score: {result.score}/100")

            # Show recommendations
            if result.recommendations:
                print("\n📋 Recommendations:")
                for rec in result.recommendations:
                    print(f"  • {rec}")
        else:
            print(f"❌ Module validation failed!")
            print(f"Errors: {len(result.errors)}")

            # Show errors
            for error in result.errors:
                print(f"  🔴 {error}")

            # Show warnings
            for warning in result.warnings:
                print(f"  🟡 {warning}")

# Run the validation
asyncio.run(validate_my_module())
```

### Advanced Module Validation

For more detailed validation with custom configurations:

```python
import asyncio
from ignition.modules.testing import ModuleValidator, ValidationConfig

async def advanced_module_validation():
    """Advanced module validation with custom configuration."""

    # Custom validation configuration
    config = ValidationConfig(
        check_compatibility=True,
        check_security=True,
        check_performance=True,
        docker_enabled=True,
        timeout_seconds=600
    )

    validator = ModuleValidator(config)

    module_path = "path/to/complex/module.modl"

    try:
        # Create validation context with cleanup
        async with validator.create_validation_context(module_path) as context:

            # Step 1: Basic validation
            print("🔍 Step 1: Basic module validation...")
            basic_result = await validator.validate_module_structure(context)

            if not basic_result.is_valid:
                print("❌ Basic validation failed, stopping...")
                return

            # Step 2: Compatibility testing
            print("🔧 Step 2: Compatibility testing...")
            compat_result = await validator.test_compatibility(context)

            # Step 3: Security analysis
            print("🛡️ Step 3: Security analysis...")
            security_result = await validator.analyze_security(context)

            # Step 4: Performance testing
            print("⚡ Step 4: Performance testing...")
            perf_result = await validator.test_performance(context)

            # Compile comprehensive report
            final_result = validator.compile_results([
                basic_result, compat_result, security_result, perf_result
            ])

            # Display results
            print(f"\n📊 Final Results:")
            print(f"Overall Score: {final_result.score}/100")
            print(f"Status: {'✅ PASSED' if final_result.success else '❌ FAILED'}")

            # Save detailed report
            report_path = f"reports/module_validation_{context.session_id}.json"
            await validator.save_validation_report(final_result, report_path)
            print(f"📄 Detailed report saved to: {report_path}")

    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        # Error details are automatically logged by the framework

asyncio.run(advanced_module_validation())
```

---

## 🐳 Test Environment Management

### Docker-Based Testing

The framework supports Docker-based testing environments for consistent, isolated testing:

```python
import asyncio
from ignition.modules.testing import TestEnvironmentManager, DockerTestEnvironment

async def docker_testing_example():
    """Example of Docker-based testing environment."""

    # Configure Docker environment
    docker_config = {
        "ignition_version": "8.1.25",
        "gateway_port": 8088,
        "database_enabled": True,
        "modules_to_install": ["module1.modl", "module2.modl"]
    }

    # Create environment manager
    env_manager = TestEnvironmentManager()

    try:
        # Create and start Docker environment
        print("🐳 Creating Docker test environment...")
        async with env_manager.create_docker_environment(docker_config) as env:

            # Wait for environment to be ready
            print("⏳ Waiting for environment to be ready...")
            await env.wait_for_ready(timeout=300)

            # Get environment status
            status = await env.get_status()
            print(f"📊 Environment Status: {status.state}")
            print(f"🌐 Gateway URL: {status.gateway_url}")

            # Run tests in the environment
            print("🧪 Running tests in Docker environment...")

            # Your test code here
            # The environment will be automatically cleaned up

    except Exception as e:
        print(f"❌ Docker environment failed: {e}")

asyncio.run(docker_testing_example())
```

### Local Testing Environment

For testing with an existing Ignition installation:

```python
import asyncio
from ignition.modules.testing import TestEnvironmentManager, LocalTestEnvironment

async def local_testing_example():
    """Example of local testing environment."""

    # Configure local environment
    local_config = {
        "gateway_url": "http://localhost:8088",
        "username": "admin",
        "password": "password",
        "backup_before_test": True,
        "restore_after_test": True
    }

    env_manager = TestEnvironmentManager()

    try:
        # Create local test environment
        print("🏠 Setting up local test environment...")
        async with env_manager.create_local_environment(local_config) as env:

            # Validate environment
            print("✅ Validating local environment...")
            validation = await env.validate_environment()

            if not validation.is_valid:
                print("❌ Local environment validation failed:")
                for error in validation.errors:
                    print(f"  • {error}")
                return

            # Install test modules
            print("📦 Installing test modules...")
            await env.install_modules(["path/to/test/module.modl"])

            # Run your tests here
            print("🧪 Running tests...")

            # Environment will be automatically restored

    except Exception as e:
        print(f"❌ Local environment setup failed: {e}")

asyncio.run(local_testing_example())
```

---

## 🛡️ Quality Assurance Pipeline

### Automated Quality Checks

The QA pipeline provides comprehensive quality analysis:

```python
import asyncio
from ignition.modules.testing import QualityAssurancePipeline

async def quality_assurance_example():
    """Example of comprehensive quality assurance."""

    # Initialize QA pipeline
    qa_pipeline = QualityAssurancePipeline()

    module_path = "path/to/your/module.modl"

    try:
        # Run comprehensive QA analysis
        print("🛡️ Starting Quality Assurance Pipeline...")

        async with qa_pipeline.create_qa_context(module_path) as context:

            # Step 1: Code Quality Analysis
            print("📊 Step 1: Code Quality Analysis...")
            code_quality = await qa_pipeline.analyze_code_quality(context)
            print(f"Code Quality Score: {code_quality.score}/100")

            # Step 2: Security Scanning
            print("🔒 Step 2: Security Scanning...")
            security_scan = await qa_pipeline.scan_security(context)
            print(f"Security Score: {security_scan.score}/100")

            # Step 3: Documentation Analysis
            print("📚 Step 3: Documentation Analysis...")
            doc_analysis = await qa_pipeline.analyze_documentation(context)
            print(f"Documentation Score: {doc_analysis.score}/100")

            # Generate comprehensive report
            print("📋 Generating QA Report...")
            qa_report = await qa_pipeline.generate_report(context, [
                code_quality, security_scan, doc_analysis
            ])

            # Display results
            print(f"\n🎯 QA Results Summary:")
            print(f"Overall Grade: {qa_report.grade}")
            print(f"Total Score: {qa_report.total_score}/100")
            print(f"Checks Passed: {qa_report.checks_passed}/{qa_report.total_checks}")

            # Show recommendations
            if qa_report.recommendations:
                print(f"\n💡 Recommendations:")
                for rec in qa_report.recommendations[:5]:  # Show top 5
                    print(f"  • {rec}")

            # Save detailed report
            report_file = f"reports/qa_report_{context.timestamp}.json"
            await qa_pipeline.save_report(qa_report, report_file)
            print(f"📄 Detailed report saved: {report_file}")

    except Exception as e:
        print(f"❌ QA Pipeline failed: {e}")

asyncio.run(quality_assurance_example())
```

### Custom Quality Rules

Define custom quality rules for your specific requirements:

```python
from ignition.modules.testing import QualityAssurancePipeline, QualityRule

# Define custom quality rules
custom_rules = [
    QualityRule(
        name="Naming Convention",
        category="code_quality",
        check_function=lambda code: "PascalCase" in code,
        weight=0.1,
        description="Check for PascalCase naming convention"
    ),
    QualityRule(
        name="Error Handling",
        category="code_quality",
        check_function=lambda code: "try:" in code and "except:" in code,
        weight=0.2,
        description="Ensure proper error handling"
    )
]

# Initialize QA pipeline with custom rules
qa_pipeline = QualityAssurancePipeline(custom_rules=custom_rules)
```

---

## 👥 User Acceptance Testing

### Automated UAT Scenarios

The UAT framework provides automated scenario execution:

```python
import asyncio
from ignition.modules.testing import UserAcceptanceTestManager

async def user_acceptance_testing():
    """Example of comprehensive user acceptance testing."""

    # Initialize UAT manager
    uat_manager = UserAcceptanceTestManager()

    module_path = "path/to/your/module.modl"

    try:
        print("👥 Starting User Acceptance Testing...")

        async with uat_manager.create_uat_context(module_path) as context:

            # Step 1: Generate test scenarios
            print("📝 Step 1: Generating test scenarios...")
            scenarios = await uat_manager.generate_scenarios(context)
            print(f"Generated {len(scenarios)} test scenarios")

            # Step 2: Execute scenarios
            print("🧪 Step 2: Executing test scenarios...")
            results = []

            for i, scenario in enumerate(scenarios, 1):
                print(f"  Running scenario {i}/{len(scenarios)}: {scenario.name}")
                result = await uat_manager.execute_scenario(context, scenario)
                results.append(result)

                # Show immediate feedback
                status = "✅ PASSED" if result.passed else "❌ FAILED"
                print(f"    {status} - Score: {result.score}/5.0")

            # Step 3: Collect feedback
            print("💬 Step 3: Collecting user feedback...")
            feedback = await uat_manager.collect_feedback(context, results)

            # Step 4: Generate training materials
            print("📚 Step 4: Generating training materials...")
            training_materials = await uat_manager.generate_training_materials(
                context, results, feedback
            )

            # Compile UAT report
            print("📊 Compiling UAT Report...")
            uat_report = await uat_manager.generate_report(
                context, results, feedback, training_materials
            )

            # Display results
            print(f"\n🎯 UAT Results Summary:")
            print(f"Execution Rate: {uat_report.execution_rate}%")
            print(f"Average Score: {uat_report.average_score}/5.0")
            print(f"User Satisfaction: {uat_report.user_satisfaction}/5.0")
            print(f"Scenarios Passed: {uat_report.scenarios_passed}/{uat_report.total_scenarios}")

            # Show key feedback
            if uat_report.key_feedback:
                print(f"\n💬 Key User Feedback:")
                for feedback_item in uat_report.key_feedback[:3]:
                    print(f"  • {feedback_item}")

            # Save materials
            materials_dir = f"training_materials_{context.timestamp}"
            await uat_manager.save_training_materials(training_materials, materials_dir)
            print(f"📚 Training materials saved to: {materials_dir}")

    except Exception as e:
        print(f"❌ UAT failed: {e}")

asyncio.run(user_acceptance_testing())
```

### Custom UAT Scenarios

Define custom test scenarios for specific use cases:

```python
from ignition.modules.testing import TestScenario, UserAcceptanceTestManager

# Define custom scenarios
custom_scenarios = [
    TestScenario(
        name="Module Installation",
        category="functional",
        description="Test module installation process",
        steps=[
            "Navigate to Config > Modules",
            "Upload module file",
            "Verify installation success",
            "Check module appears in list"
        ],
        expected_outcome="Module successfully installed and visible",
        priority="high"
    ),
    TestScenario(
        name="User Interface Navigation",
        category="usability",
        description="Test user interface navigation",
        steps=[
            "Open module interface",
            "Navigate through all tabs",
            "Test all buttons and controls",
            "Verify responsive design"
        ],
        expected_outcome="All interface elements work correctly",
        priority="medium"
    )
]

# Use custom scenarios
uat_manager = UserAcceptanceTestManager(custom_scenarios=custom_scenarios)
```

---

## 📊 Integration Testing

### End-to-End Testing

Run comprehensive integration tests across all components:

```python
import asyncio
from ignition.modules.testing import integration_test

async def run_integration_test():
    """Run comprehensive integration test."""

    print("🚀 Starting IGN Scripts Integration Test...")

    try:
        # Run the comprehensive integration test
        result = await integration_test()

        if result["success"]:
            print(f"✅ Integration test completed successfully!")
            print(f"Overall Score: {result['overall_score']}/100")
            print(f"Components Tested: {result['components_tested']}")

            # Show component results
            for component, score in result["component_scores"].items():
                status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                print(f"  {status} {component}: {score}/100")

        else:
            print(f"❌ Integration test failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Integration test failed with exception: {e}")

asyncio.run(run_integration_test())
```

### Custom Integration Tests

Create custom integration tests for specific workflows:

```python
import asyncio
from ignition.modules.testing import (
    ModuleValidator, TestEnvironmentManager,
    QualityAssurancePipeline, UserAcceptanceTestManager
)

async def custom_integration_test(module_path: str):
    """Custom integration test workflow."""

    print(f"🔧 Custom Integration Test for: {module_path}")

    # Initialize all components
    validator = ModuleValidator()
    env_manager = TestEnvironmentManager()
    qa_pipeline = QualityAssurancePipeline()
    uat_manager = UserAcceptanceTestManager()

    results = {}

    try:
        # Step 1: Module Validation
        print("1️⃣ Module Validation...")
        async with validator.create_validation_context(module_path) as ctx:
            validation_result = await validator.validate_module_comprehensive(ctx)
            results["validation"] = validation_result

        # Step 2: Environment Setup
        print("2️⃣ Environment Setup...")
        env_config = {"ignition_version": "8.1.25"}
        async with env_manager.create_docker_environment(env_config) as env:
            await env.wait_for_ready()

            # Step 3: Quality Assurance
            print("3️⃣ Quality Assurance...")
            async with qa_pipeline.create_qa_context(module_path) as qa_ctx:
                qa_result = await qa_pipeline.run_comprehensive_analysis(qa_ctx)
                results["quality"] = qa_result

            # Step 4: User Acceptance Testing
            print("4️⃣ User Acceptance Testing...")
            async with uat_manager.create_uat_context(module_path) as uat_ctx:
                uat_result = await uat_manager.run_comprehensive_uat(uat_ctx)
                results["uat"] = uat_result

        # Compile final results
        overall_score = (
            results["validation"].score * 0.3 +
            results["quality"].total_score * 0.4 +
            results["uat"].average_score * 20 * 0.3  # Convert 5-point to 100-point scale
        )

        print(f"\n🎯 Integration Test Results:")
        print(f"Overall Score: {overall_score:.1f}/100")
        print(f"✅ Validation: {results['validation'].score}/100")
        print(f"🛡️ Quality: {results['quality'].total_score}/100")
        print(f"👥 UAT: {results['uat'].average_score}/5.0")

        return {
            "success": True,
            "overall_score": overall_score,
            "results": results
        }

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return {"success": False, "error": str(e)}

# Run custom integration test
result = asyncio.run(custom_integration_test("path/to/module.modl"))
```

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### Environment Validation Failures

**Issue**: Environment validation fails with missing tools or configuration.

**Solution**:
```python
from ignition.modules.testing import ModuleValidator

# Check specific environment issues
validator = ModuleValidator()
validation = await validator.validate_environment()

# Show detailed error information
for error in validation.errors:
    print(f"❌ {error}")

# Show recommendations
for rec in validation.recommendations:
    print(f"💡 {rec}")
```

**Common fixes**:
- Install missing Docker: `docker --version`
- Check Ignition Gateway: `curl http://localhost:8088`
- Verify environment variables: `echo $IGNITION_TEST_VERSION`
- Update Python dependencies: `pip install -r requirements.txt`

#### Module Validation Errors

**Issue**: Module validation fails with structure or compatibility errors.

**Solution**:
```python
# Enable verbose logging for detailed error information
import logging
logging.basicConfig(level=logging.DEBUG)

# Run validation with detailed error reporting
validator = ModuleValidator()
async with validator.create_validation_context(module_path) as context:
    result = await validator.validate_module_structure(context)

    # Show detailed error analysis
    for error in result.errors:
        print(f"🔴 Error: {error}")

    for warning in result.warnings:
        print(f"🟡 Warning: {warning}")
```

#### Docker Environment Issues

**Issue**: Docker test environment fails to start or becomes unresponsive.

**Solution**:
```bash
# Check Docker status
docker ps -a

# Clean up stale containers
docker system prune -f

# Check Docker logs
docker logs <container_id>

# Restart Docker service (if needed)
sudo systemctl restart docker
```

```python
# Use environment validation before creating Docker environments
from ignition.modules.testing import TestEnvironmentManager

env_manager = TestEnvironmentManager()

# Check Docker availability
docker_available = await env_manager.check_docker_availability()
if not docker_available:
    print("❌ Docker not available, using local environment instead")
```

#### Performance Issues

**Issue**: Tests run slowly or timeout.

**Solution**:
```python
# Increase timeout values
config = ValidationConfig(
    timeout_seconds=600,  # Increase from default 300
    parallel_execution=True,  # Enable parallel execution
    cache_enabled=True  # Enable result caching
)

validator = ModuleValidator(config)
```

```bash
# Monitor system resources during testing
htop  # or top
docker stats  # for Docker containers
```

### Debugging Tips

#### Enable Debug Logging

```python
import logging

# Enable debug logging for all testing components
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable specific component logging
logging.getLogger('ignition.modules.testing').setLevel(logging.DEBUG)
```

#### Use Validation Context Information

```python
# Access detailed context information for debugging
async with validator.create_validation_context(module_path) as context:
    print(f"Session ID: {context.session_id}")
    print(f"Working Directory: {context.working_directory}")
    print(f"Environment: {context.environment}")

    # Your validation code here
```

#### Check Component Status

```python
# Check individual component status
from ignition.modules.testing import (
    ModuleValidator, TestEnvironmentManager,
    QualityAssurancePipeline, UserAcceptanceTestManager
)

async def check_component_status():
    """Check status of all testing components."""

    components = [
        ("Module Validator", ModuleValidator()),
        ("Environment Manager", TestEnvironmentManager()),
        ("QA Pipeline", QualityAssurancePipeline()),
        ("UAT Manager", UserAcceptanceTestManager())
    ]

    for name, component in components:
        try:
            status = await component.get_status()
            print(f"✅ {name}: {status}")
        except Exception as e:
            print(f"❌ {name}: {e}")

asyncio.run(check_component_status())
```

---

## 🎯 Best Practices

### Testing Workflow

1. **Start with Environment Validation**
   ```python
   # Always validate environment first
   validator = ModuleValidator()
   env_validation = await validator.validate_environment()

   if not env_validation.is_valid:
       print("Fix environment issues before proceeding")
       return
   ```

2. **Use Progressive Testing**
   ```python
   # Start with basic validation, then progress to comprehensive testing

   # Step 1: Basic structure validation
   basic_result = await validator.validate_module_structure(context)

   # Step 2: If basic passes, do compatibility testing
   if basic_result.is_valid:
       compat_result = await validator.test_compatibility(context)

   # Step 3: If compatibility passes, do comprehensive testing
   if compat_result.is_valid:
       full_result = await validator.validate_module_comprehensive(context)
   ```

3. **Implement Proper Error Handling**
   ```python
   # Follow crawl_mcp.py patterns for error handling
   try:
       async with validator.create_validation_context(module_path) as context:
           result = await validator.validate_module(context)
   except ValidationError as e:
       print(f"Validation error: {e}")
   except EnvironmentError as e:
       print(f"Environment error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")
   ```

### Performance Optimization

1. **Use Parallel Execution**
   ```python
   # Enable parallel execution for faster testing
   config = ValidationConfig(parallel_execution=True)
   validator = ModuleValidator(config)
   ```

2. **Cache Results**
   ```python
   # Enable result caching to avoid redundant operations
   config = ValidationConfig(cache_enabled=True)
   qa_pipeline = QualityAssurancePipeline(config)
   ```

3. **Optimize Docker Usage**
   ```python
   # Reuse Docker environments when possible
   env_config = {
       "reuse_existing": True,
       "cleanup_on_exit": False  # Keep for next test
   }
   ```

### Quality Assurance

1. **Set Quality Gates**
   ```python
   # Define minimum quality thresholds
   QUALITY_GATES = {
       "module_validation": 85,
       "code_quality": 80,
       "security_score": 90,
       "documentation": 75,
       "uat_satisfaction": 4.0
   }

   # Check against quality gates
   if result.score < QUALITY_GATES["module_validation"]:
       print("❌ Module validation below quality gate")
   ```

2. **Regular Testing Schedule**
   ```python
   # Implement regular testing schedule
   import schedule

   def run_nightly_tests():
       asyncio.run(integration_test())

   schedule.every().day.at("02:00").do(run_nightly_tests)
   ```

3. **Comprehensive Reporting**
   ```python
   # Always generate and save detailed reports
   report_data = {
       "timestamp": datetime.now().isoformat(),
       "module_path": module_path,
       "validation_results": validation_result,
       "qa_results": qa_result,
       "uat_results": uat_result
   }

   with open(f"reports/comprehensive_report_{session_id}.json", "w") as f:
       json.dump(report_data, f, indent=2)
   ```

---

## 🔬 Advanced Usage

### Custom Validation Rules

Create custom validation rules for specific requirements:

```python
from ignition.modules.testing import ValidationRule, ModuleValidator

class CustomValidationRule(ValidationRule):
    """Custom validation rule for specific requirements."""

    def __init__(self):
        super().__init__(
            name="Custom Module Validation",
            category="custom",
            weight=0.2
        )

    async def validate(self, context):
        """Custom validation logic."""
        result = ValidationResult()

        # Your custom validation logic here
        # Example: Check for specific naming conventions
        if not self._check_naming_convention(context.module_path):
            result.add_error("Module name does not follow naming convention")

        # Example: Check for required components
        if not self._check_required_components(context.module_path):
            result.add_warning("Module missing recommended components")

        return result

    def _check_naming_convention(self, module_path):
        """Check if module follows naming convention."""
        # Implementation here
        return True

    def _check_required_components(self, module_path):
        """Check for required components."""
        # Implementation here
        return True

# Use custom validation rule
custom_rule = CustomValidationRule()
validator = ModuleValidator(custom_rules=[custom_rule])
```

### Integration with CI/CD

Integrate testing framework with continuous integration:

```yaml
# .github/workflows/module-testing.yml
name: Module Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      docker:
        image: docker:dind
        options: --privileged

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Set up environment
      run: |
        cp config/env.example .env
        # Set CI-specific environment variables

    - name: Run integration tests
      run: |
        python -c "
        import asyncio
        from ignition.modules.testing import integration_test
        result = asyncio.run(integration_test())
        exit(0 if result['success'] else 1)
        "

    - name: Upload test reports
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: test-reports
        path: reports/
```

### Custom Test Environments

Create custom test environments for specific scenarios:

```python
from ignition.modules.testing import TestEnvironment

class CustomTestEnvironment(TestEnvironment):
    """Custom test environment with specific configuration."""

    def __init__(self, config):
        super().__init__(config)
        self.custom_config = config.get("custom", {})

    async def setup(self):
        """Set up custom test environment."""
        await super().setup()

        # Custom setup logic
        await self._setup_custom_database()
        await self._configure_custom_services()
        await self._load_test_data()

    async def _setup_custom_database(self):
        """Set up custom database configuration."""
        # Implementation here
        pass

    async def _configure_custom_services(self):
        """Configure custom services."""
        # Implementation here
        pass

    async def _load_test_data(self):
        """Load custom test data."""
        # Implementation here
        pass

    async def cleanup(self):
        """Clean up custom test environment."""
        await self._cleanup_test_data()
        await super().cleanup()

    async def _cleanup_test_data(self):
        """Clean up custom test data."""
        # Implementation here
        pass

# Use custom test environment
custom_config = {
    "type": "custom",
    "custom": {
        "database_type": "postgresql",
        "test_data_set": "manufacturing"
    }
}

env_manager = TestEnvironmentManager()
async with env_manager.create_environment(custom_config, CustomTestEnvironment) as env:
    # Run tests in custom environment
    pass
```

### Automated Report Generation

Generate automated reports with custom formatting:

```python
from ignition.modules.testing import ReportGenerator
import json
from datetime import datetime

class CustomReportGenerator(ReportGenerator):
    """Custom report generator with specific formatting."""

    async def generate_executive_summary(self, results):
        """Generate executive summary report."""
        summary = {
            "report_date": datetime.now().isoformat(),
            "overall_status": "PASSED" if all(r.success for r in results) else "FAILED",
            "total_modules_tested": len(results),
            "average_score": sum(r.score for r in results) / len(results),
            "key_findings": self._extract_key_findings(results),
            "recommendations": self._compile_recommendations(results)
        }

        return summary

    async def generate_detailed_report(self, results):
        """Generate detailed technical report."""
        report = {
            "executive_summary": await self.generate_executive_summary(results),
            "test_results": [self._format_result(r) for r in results],
            "environment_info": await self._get_environment_info(),
            "performance_metrics": await self._get_performance_metrics(results),
            "appendices": {
                "test_logs": await self._get_test_logs(),
                "configuration": await self._get_configuration()
            }
        }

        return report

    def _extract_key_findings(self, results):
        """Extract key findings from results."""
        findings = []

        # Analyze results for key findings
        high_scores = [r for r in results if r.score >= 90]
        low_scores = [r for r in results if r.score < 70]

        if high_scores:
            findings.append(f"{len(high_scores)} modules achieved excellent scores (≥90)")

        if low_scores:
            findings.append(f"{len(low_scores)} modules need improvement (<70)")

        return findings

    def _compile_recommendations(self, results):
        """Compile recommendations from all results."""
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)

        # Deduplicate and prioritize recommendations
        unique_recommendations = list(set(all_recommendations))
        return unique_recommendations[:10]  # Top 10 recommendations

# Use custom report generator
report_generator = CustomReportGenerator()
executive_summary = await report_generator.generate_executive_summary(test_results)
detailed_report = await report_generator.generate_detailed_report(test_results)

# Save reports
with open("reports/executive_summary.json", "w") as f:
    json.dump(executive_summary, f, indent=2)

with open("reports/detailed_report.json", "w") as f:
    json.dump(detailed_report, f, indent=2)
```

---

## 📚 Conclusion

This Testing & Validation Manual provides comprehensive guidance for using the IGN Scripts testing framework. Following the patterns established in `crawl_mcp.py`, the framework offers:

- **Robust Error Handling**: Comprehensive error detection and user-friendly error messages
- **Environment Validation**: Automatic validation of required tools and configurations
- **Step-by-Step Guidance**: Clear, logical progression through testing workflows
- **Resource Management**: Proper cleanup and resource management using async context managers
- **Extensibility**: Support for custom validation rules, test environments, and reporting

### Key Takeaways

1. **Always validate environment first** before running tests
2. **Use progressive testing** - start simple, then comprehensive
3. **Implement proper error handling** following established patterns
4. **Save detailed reports** for analysis and compliance
5. **Follow security best practices** with environment variables
6. **Use async context managers** for proper resource cleanup
7. **Enable parallel execution** for better performance
8. **Set quality gates** to maintain standards

### Next Steps

1. **Set up your environment** with required tools and configuration
2. **Start with basic module validation** to familiarize yourself with the framework
3. **Progress to comprehensive testing** as you become comfortable
4. **Customize rules and environments** for your specific needs
5. **Integrate with CI/CD** for automated testing
6. **Generate regular reports** for quality tracking

For additional support, refer to the troubleshooting section or check the project documentation for updates and enhancements.

---

**Last Updated**: 2025-01-28
**Version**: 1.0.0
**Framework Version**: Phase 9.6
**Maintainer**: IGN Scripts Testing Team
