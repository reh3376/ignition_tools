# IGN Scripts - Testing Framework Quick Reference

## 🚀 Quick Start Commands

### 1. Initialize Agent Knowledge (Required)
```python
from ignition.code_intelligence import initialize_agent_knowledge
context = initialize_agent_knowledge()
```

### 2. Basic Module Validation
```python
from ignition.modules.testing import ModuleValidator

validator = ModuleValidator()
result = await validator.validate_module("path/to/module.modl")
print(f"Result: {'✅ PASSED' if result.success else '❌ FAILED'}")
```

### 3. Run Integration Test
```python
from ignition.modules.testing import integration_test
result = await integration_test()
```

---

## 🔧 Environment Variables (Required)

### Essential Variables
```bash
IGNITION_TEST_VERSION=8.1.25
TEST_GATEWAY_URL=http://localhost:8088
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Optional Variables
```bash
DOCKER_TEST_ENABLED=true
TEST_TIMEOUT=300
UAT_TEST_USERNAME=test_user
QA_TOOLS_PATH=/opt/qa-tools
```

---

## 📋 Common Testing Patterns

### Environment Validation First
```python
# Always validate environment before testing
validator = ModuleValidator()
env_result = await validator.validate_environment()

if not env_result.is_valid:
    print("Fix environment issues first")
    return
```

### Progressive Testing
```python
# Start simple, then comprehensive
async with validator.create_validation_context(module_path) as context:
    # Level 1: Basic validation
    basic = await validator.validate_module_structure(context)

    # Level 2: If basic passes, do compatibility
    if basic.is_valid:
        compat = await validator.test_compatibility(context)

    # Level 3: If compatibility passes, do comprehensive
    if compat.is_valid:
        full = await validator.validate_module_comprehensive(context)
```

### Proper Error Handling
```python
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

---

## 🐳 Docker Testing

### Quick Docker Test
```python
from ignition.modules.testing import TestEnvironmentManager

env_manager = TestEnvironmentManager()
docker_config = {"ignition_version": "8.1.25"}

async with env_manager.create_docker_environment(docker_config) as env:
    await env.wait_for_ready()
    # Run tests here
```

---

## 🛡️ Quality Assurance

### Quick QA Analysis
```python
from ignition.modules.testing import QualityAssurancePipeline

qa_pipeline = QualityAssurancePipeline()

async with qa_pipeline.create_qa_context(module_path) as context:
    code_quality = await qa_pipeline.analyze_code_quality(context)
    security = await qa_pipeline.scan_security(context)
    docs = await qa_pipeline.analyze_documentation(context)

    print(f"Code Quality: {code_quality.score}/100")
    print(f"Security: {security.score}/100")
    print(f"Documentation: {docs.score}/100")
```

---

## 👥 User Acceptance Testing

### Quick UAT Run
```python
from ignition.modules.testing import UserAcceptanceTestManager

uat_manager = UserAcceptanceTestManager()

async with uat_manager.create_uat_context(module_path) as context:
    scenarios = await uat_manager.generate_scenarios(context)
    results = []

    for scenario in scenarios:
        result = await uat_manager.execute_scenario(context, scenario)
        results.append(result)

    avg_score = sum(r.score for r in results) / len(results)
    print(f"UAT Average Score: {avg_score}/5.0")
```

---

## 🔧 Troubleshooting

### Check Environment Issues
```python
validator = ModuleValidator()
validation = await validator.validate_environment()

for error in validation.errors:
    print(f"❌ {error}")

for rec in validation.recommendations:
    print(f"💡 {rec}")
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('ignition.modules.testing').setLevel(logging.DEBUG)
```

### Check Component Status
```python
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
```

---

## 📊 Quality Gates

### Recommended Thresholds
```python
QUALITY_GATES = {
    "module_validation": 85,    # Module validation score
    "code_quality": 80,         # Code quality score
    "security_score": 90,       # Security scan score
    "documentation": 75,        # Documentation score
    "uat_satisfaction": 4.0     # User satisfaction rating
}

# Check against gates
if result.score < QUALITY_GATES["module_validation"]:
    print("❌ Below quality gate")
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run IGN Scripts Tests
  run: |
    python -c "
    import asyncio
    from ignition.modules.testing import integration_test
    result = asyncio.run(integration_test())
    exit(0 if result['success'] else 1)
    "
```

---

## 📁 Report Locations

### Default Report Paths
- **Validation Reports**: `reports/module_validation_*.json`
- **QA Reports**: `reports/qa_report_*.json`
- **UAT Reports**: `reports/uat_report_*.json`
- **Integration Reports**: `reports/integration_test_*.json`
- **Training Materials**: `training_materials_*/`

---

## ⚡ Performance Tips

### Enable Parallel Execution
```python
config = ValidationConfig(parallel_execution=True)
validator = ModuleValidator(config)
```

### Use Result Caching
```python
config = ValidationConfig(cache_enabled=True)
qa_pipeline = QualityAssurancePipeline(config)
```

### Increase Timeouts
```python
config = ValidationConfig(timeout_seconds=600)
validator = ModuleValidator(config)
```

---

## 📚 Additional Resources

- **Full Manual**: `docs/TESTING_VALIDATION_MANUAL.md`
- **Implementation Details**: `docs/PHASE_9_6_MODULE_TESTING_VALIDATION_COMPLETION_SUMMARY.md`
- **Source Code**: `src/ignition/modules/testing/`
- **Examples**: Run integration test for comprehensive examples

---

**Last Updated**: 2025-01-28
**Version**: Phase 9.6
**Framework**: IGN Scripts Testing & Validation
