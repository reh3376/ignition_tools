"""
Working Unit Tests for Phase 11.2 SME Agent Core Capabilities

This test suite follows crawl_mcp.py methodology with practical, working tests.
"""

import os
import tempfile
from pathlib import Path


# Test environment validation first
def test_phase_11_2_environment():
    """Test Phase 11.2 environment setup."""
    # Check if files exist
    required_files = [
        "src/ignition/modules/sme_agent/knowledge_domains.py",
        "src/ignition/modules/sme_agent/adaptive_learning.py",
        "src/ignition/modules/sme_agent/context_aware_response.py",
    ]

    for file_path in required_files:
        assert Path(file_path).exists(), f"Required file missing: {file_path}"

    # Check environment variables
    required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
    for var in required_vars:
        assert os.getenv(var) is not None, f"Environment variable missing: {var}"


def test_imports():
    """Test that Phase 11.2 components can be imported."""
    try:
        from src.ignition.modules.sme_agent.adaptive_learning import (
            AdaptiveLearningEngine,
            ConfidenceTracker,
        )
        from src.ignition.modules.sme_agent.context_aware_response import (
            ContextAwareResponseGenerator,
            ProjectAnalyzer,
        )
        from src.ignition.modules.sme_agent.knowledge_domains import (
            GatewayScriptingDomainManager,
            SystemFunctionsDomainManager,
        )

        print("✅ All Phase 11.2 imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_gateway_scripting_domain_manager():
    """Test GatewayScriptingDomainManager basic functionality."""
    try:
        from src.ignition.modules.sme_agent.knowledge_domains import (
            GatewayScriptingDomainManager,
        )

        # Test initialization
        manager = GatewayScriptingDomainManager()
        assert manager.domain_name == "gateway_scripting"
        assert hasattr(manager, "statistics")

        # Test input validation
        assert manager.validate_input("test query") == True
        assert manager.validate_input("") == False

        print("✅ GatewayScriptingDomainManager tests passed")
        return True
    except Exception as e:
        print(f"❌ GatewayScriptingDomainManager test failed: {e}")
        return False


def test_system_functions_domain_manager():
    """Test SystemFunctionsDomainManager basic functionality."""
    try:
        from src.ignition.modules.sme_agent.knowledge_domains import (
            SystemFunctionsDomainManager,
        )

        # Test initialization
        manager = SystemFunctionsDomainManager()
        assert manager.domain_name == "system_functions"
        assert hasattr(manager, "statistics")

        # Test input validation
        assert manager.validate_input("test query") == True
        assert manager.validate_input("") == False

        print("✅ SystemFunctionsDomainManager tests passed")
        return True
    except Exception as e:
        print(f"❌ SystemFunctionsDomainManager test failed: {e}")
        return False


def test_adaptive_learning_engine():
    """Test AdaptiveLearningEngine basic functionality."""
    try:
        from src.ignition.modules.sme_agent.adaptive_learning import (
            AdaptiveLearningEngine,
        )

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test initialization
            engine = AdaptiveLearningEngine(temp_dir)
            assert hasattr(engine, "confidence_tracker")
            assert hasattr(engine, "conversation_history")
            assert hasattr(engine, "knowledge_gaps")

            # Test storage path creation
            assert hasattr(engine, "storage_path")

            print("✅ AdaptiveLearningEngine tests passed")
            return True
    except Exception as e:
        print(f"❌ AdaptiveLearningEngine test failed: {e}")
        return False


def test_confidence_tracker():
    """Test ConfidenceTracker basic functionality."""
    try:
        from src.ignition.modules.sme_agent.adaptive_learning import ConfidenceTracker

        # Test initialization
        tracker = ConfidenceTracker()
        assert hasattr(tracker, "update_confidence")
        assert hasattr(tracker, "get_confidence_trend")

        print("✅ ConfidenceTracker tests passed")
        return True
    except Exception as e:
        print(f"❌ ConfidenceTracker test failed: {e}")
        return False


def test_project_analyzer():
    """Test ProjectAnalyzer basic functionality."""
    try:
        from src.ignition.modules.sme_agent.context_aware_response import (
            ProjectAnalyzer,
        )

        # Test initialization
        analyzer = ProjectAnalyzer()
        assert hasattr(analyzer, "analyze_project")
        assert hasattr(analyzer, "file_patterns")
        assert hasattr(analyzer, "technology_indicators")

        # Test with temporary project directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "test.py").write_text("# Test script")
            (Path(temp_dir) / "config.properties").write_text("test=value")

            # Test analysis
            context = analyzer.analyze_project(temp_dir)
            assert hasattr(context, "project_path")
            assert hasattr(context, "project_type")
            assert hasattr(context, "file_count")
            assert context.file_count >= 2

        print("✅ ProjectAnalyzer tests passed")
        return True
    except Exception as e:
        print(f"❌ ProjectAnalyzer test failed: {e}")
        return False


def test_context_aware_response_generator():
    """Test ContextAwareResponseGenerator basic functionality."""
    try:
        from src.ignition.modules.sme_agent.context_aware_response import (
            ContextAwareResponseGenerator,
        )

        # Test initialization
        generator = ContextAwareResponseGenerator()
        assert hasattr(generator, "generate_response")
        assert hasattr(generator, "project_analyzer")

        print("✅ ContextAwareResponseGenerator tests passed")
        return True
    except Exception as e:
        print(f"❌ ContextAwareResponseGenerator test failed: {e}")
        return False


def test_file_structure():
    """Test that all Phase 11.2 files have proper structure."""
    try:
        # Check file sizes (should be substantial)
        files_to_check = [
            ("src/ignition/modules/sme_agent/knowledge_domains.py", 1000),
            ("src/ignition/modules/sme_agent/adaptive_learning.py", 500),
            ("src/ignition/modules/sme_agent/context_aware_response.py", 500),
        ]

        for file_path, min_size in files_to_check:
            path = Path(file_path)
            assert path.exists(), f"File missing: {file_path}"

            size = path.stat().st_size
            assert size > min_size, f"File too small: {file_path} ({size} bytes)"

        print("✅ File structure tests passed")
        return True
    except Exception as e:
        print(f"❌ File structure test failed: {e}")
        return False


def test_documentation_exists():
    """Test that Phase 11.2 documentation exists."""
    try:
        docs = [
            "docs/phase_summary/PHASE_11_2_SME_AGENT_CORE_CAPABILITIES.md",
            "docs/phase_summary/PHASE_11_2_COMPLETION_SUMMARY.md",
        ]

        for doc_path in docs:
            path = Path(doc_path)
            assert path.exists(), f"Documentation missing: {doc_path}"

            # Check content is substantial
            content = path.read_text()
            assert len(content) > 1000, f"Documentation too short: {doc_path}"

        print("✅ Documentation tests passed")
        return True
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False


def run_all_tests():
    """Run all Phase 11.2 tests."""
    tests = [
        test_phase_11_2_environment,
        test_imports,
        test_gateway_scripting_domain_manager,
        test_system_functions_domain_manager,
        test_adaptive_learning_engine,
        test_confidence_tracker,
        test_project_analyzer,
        test_context_aware_response_generator,
        test_file_structure,
        test_documentation_exists,
    ]

    results = []
    passed = 0
    failed = 0

    print("🧪 Running Phase 11.2 Comprehensive Tests")
    print("=" * 50)

    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
                results.append((test.__name__, "PASSED", None))
            else:
                failed += 1
                results.append((test.__name__, "FAILED", "Test returned False"))
        except Exception as e:
            failed += 1
            results.append((test.__name__, "FAILED", str(e)))

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 50)

    for test_name, status, error in results:
        status_emoji = "✅" if status == "PASSED" else "❌"
        print(f"{status_emoji} {test_name}: {status}")
        if error:
            print(f"   Error: {error}")

    return passed, failed, results


if __name__ == "__main__":
    run_all_tests()
