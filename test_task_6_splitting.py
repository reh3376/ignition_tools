#!/usr/bin/env python3
"""Comprehensive Testing Script for Task 6 Utility System Split.

This script validates the modular implementation of task_6_utility_system.py
to ensure all functionality is preserved before proceeding to the next file.

Test Categories:
1. Import and Module Loading
2. Function Discovery and Availability
3. Data Structure Validation
4. Cross-Module Integration
5. Performance Impact Assessment
6. Backward Compatibility Verification
"""

import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

class Task6TestSuite:
    """Comprehensive test suite for Task 6 utility system split."""
    
    def __init__(self):
        self.test_results: Dict[str, Any] = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "warnings": [],
            "performance": {}
        }
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result."""
        self.test_results["total_tests"] += 1
        if status == "PASS":
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: {status}")
        elif status == "FAIL":
            self.test_results["failed"] += 1
            print(f"❌ {test_name}: {status}")
            if details:
                print(f"   Details: {details}")
                self.test_results["errors"].append(f"{test_name}: {details}")
        elif status == "WARN":
            print(f"⚠️  {test_name}: {status}")
            if details:
                print(f"   Details: {details}")
                self.test_results["warnings"].append(f"{test_name}: {details}")
        
        if details and status == "PASS":
            print(f"   {details}")
    
    def test_1_import_validation(self):
        """Test 1: Import and Module Loading Validation."""
        print("\n🔍 Test 1: Import and Module Loading Validation")
        print("-" * 50)
        
        try:
            # Test main module import
            from ignition.graph.tasks.task_6_utility_system import (
                get_utility_system_functions, 
                get_task_6_metadata
            )
            self.log_test("Main module import", "PASS", "task_6_utility_system imports successfully")
            
            # Test submodule imports
            from ignition.graph.tasks.utility_modules.general_utilities import get_general_utilities_functions
            self.log_test("General utilities import", "PASS", "general_utilities module imports successfully")
            
            from ignition.graph.tasks.utility_modules.logging_operations import get_logging_operations_functions
            self.log_test("Logging operations import", "PASS", "logging_operations module imports successfully")
            
            # Test package import
            from ignition.graph.tasks.utility_modules import (
                get_general_utilities_functions as pkg_general,
                get_logging_operations_functions as pkg_logging
            )
            self.log_test("Package-level imports", "PASS", "utility_modules package imports working")
            
        except ImportError as e:
            self.log_test("Import validation", "FAIL", f"Import error: {str(e)}")
        except Exception as e:
            self.log_test("Import validation", "FAIL", f"Unexpected error: {str(e)}")
    
    def test_2_function_discovery(self):
        """Test 2: Function Discovery and Availability."""
        print("\n🔍 Test 2: Function Discovery and Availability")
        print("-" * 50)
        
        try:
            from ignition.graph.tasks.task_6_utility_system import get_utility_system_functions
            
            # Get all functions
            start_time = time.time()
            functions = get_utility_system_functions()
            load_time = time.time() - start_time
            
            self.test_results["performance"]["function_load_time"] = load_time
            
            if not isinstance(functions, list):
                self.log_test("Function return type", "FAIL", f"Expected list, got {type(functions)}")
                return
            
            self.log_test("Function return type", "PASS", f"Returns list with {len(functions)} functions")
            
            # Validate function count
            expected_count = 11  # 8 general + 3 logging
            if len(functions) == expected_count:
                self.log_test("Function count", "PASS", f"Expected {expected_count}, got {len(functions)}")
            else:
                self.log_test("Function count", "WARN", f"Expected {expected_count}, got {len(functions)}")
            
            # Validate function structure
            required_keys = ["name", "description", "parameters", "returns", "scope", "category", "patterns"]
            for i, func in enumerate(functions[:3]):  # Test first 3 functions
                missing_keys = [key for key in required_keys if key not in func]
                if missing_keys:
                    self.log_test(f"Function {i+1} structure", "FAIL", f"Missing keys: {missing_keys}")
                else:
                    self.log_test(f"Function {i+1} structure", "PASS", f"All required keys present")
            
            # Test specific functions
            expected_functions = [
                "system.util.modifyTranslation",
                "system.util.translate", 
                "system.util.getLoggerLevel",
                "system.util.setLoggerLevel"
            ]
            
            function_names = [f["name"] for f in functions]
            for expected_func in expected_functions:
                if expected_func in function_names:
                    self.log_test(f"Function {expected_func}", "PASS", "Function found in collection")
                else:
                    self.log_test(f"Function {expected_func}", "FAIL", "Function missing from collection")
                    
        except Exception as e:
            self.log_test("Function discovery", "FAIL", f"Error: {str(e)}")
    
    def test_3_data_structure_validation(self):
        """Test 3: Data Structure Validation."""
        print("\n🔍 Test 3: Data Structure Validation")
        print("-" * 50)
        
        try:
            from ignition.graph.tasks.task_6_utility_system import get_task_6_metadata
            
            # Test metadata structure
            metadata = get_task_6_metadata()
            
            if not isinstance(metadata, dict):
                self.log_test("Metadata type", "FAIL", f"Expected dict, got {type(metadata)}")
                return
            
            self.log_test("Metadata type", "PASS", "Returns dictionary")
            
            # Check required metadata fields
            required_fields = ["task_id", "name", "description", "categories", "contexts"]
            missing_fields = [field for field in required_fields if field not in metadata]
            
            if missing_fields:
                self.log_test("Metadata completeness", "FAIL", f"Missing fields: {missing_fields}")
            else:
                self.log_test("Metadata completeness", "PASS", "All required fields present")
            
            # Validate specific values
            if metadata.get("task_id") == 6:
                self.log_test("Task ID validation", "PASS", "Correct task ID (6)")
            else:
                self.log_test("Task ID validation", "FAIL", f"Expected 6, got {metadata.get('task_id')}")
            
            if "Utility System Expansion" in metadata.get("name", ""):
                self.log_test("Task name validation", "PASS", "Correct task name")
            else:
                self.log_test("Task name validation", "FAIL", f"Unexpected name: {metadata.get('name')}")
                
        except Exception as e:
            self.log_test("Data structure validation", "FAIL", f"Error: {str(e)}")
    
    def test_4_cross_module_integration(self):
        """Test 4: Cross-Module Integration."""
        print("\n🔍 Test 4: Cross-Module Integration")
        print("-" * 50)
        
        try:
            # Test individual module functions
            from ignition.graph.tasks.utility_modules.general_utilities import get_general_utilities_functions
            from ignition.graph.tasks.utility_modules.logging_operations import get_logging_operations_functions
            
            general_functions = get_general_utilities_functions()
            logging_functions = get_logging_operations_functions()
            
            # Validate individual modules
            if isinstance(general_functions, list) and len(general_functions) > 0:
                self.log_test("General utilities module", "PASS", f"{len(general_functions)} functions loaded")
            else:
                self.log_test("General utilities module", "FAIL", "Failed to load functions")
            
            if isinstance(logging_functions, list) and len(logging_functions) > 0:
                self.log_test("Logging operations module", "PASS", f"{len(logging_functions)} functions loaded")
            else:
                self.log_test("Logging operations module", "FAIL", "Failed to load functions")
            
            # Test aggregation
            from ignition.graph.tasks.task_6_utility_system import get_utility_system_functions
            all_functions = get_utility_system_functions()
            
            expected_total = len(general_functions) + len(logging_functions)
            if len(all_functions) == expected_total:
                self.log_test("Function aggregation", "PASS", f"Correctly aggregated {expected_total} functions")
            else:
                self.log_test("Function aggregation", "WARN", f"Expected {expected_total}, got {len(all_functions)}")
            
            # Test for duplicates
            all_names = [f["name"] for f in all_functions]
            duplicates = [name for name in set(all_names) if all_names.count(name) > 1]
            
            if duplicates:
                self.log_test("Duplicate functions", "FAIL", f"Found duplicates: {duplicates}")
            else:
                self.log_test("Duplicate functions", "PASS", "No duplicate functions found")
                
        except Exception as e:
            self.log_test("Cross-module integration", "FAIL", f"Error: {str(e)}")
    
    def test_5_performance_assessment(self):
        """Test 5: Performance Impact Assessment."""
        print("\n🔍 Test 5: Performance Impact Assessment")
        print("-" * 50)
        
        try:
            from ignition.graph.tasks.task_6_utility_system import get_utility_system_functions
            
            # Test multiple loads for performance
            load_times = []
            for i in range(5):
                start_time = time.time()
                functions = get_utility_system_functions()
                load_time = time.time() - start_time
                load_times.append(load_time)
            
            avg_load_time = sum(load_times) / len(load_times)
            max_load_time = max(load_times)
            min_load_time = min(load_times)
            
            self.test_results["performance"]["avg_load_time"] = avg_load_time
            self.test_results["performance"]["max_load_time"] = max_load_time
            self.test_results["performance"]["min_load_time"] = min_load_time
            
            # Performance thresholds (reasonable for function definition loading)
            if avg_load_time < 0.1:  # 100ms threshold
                self.log_test("Average load time", "PASS", f"{avg_load_time:.4f}s (< 0.1s threshold)")
            elif avg_load_time < 0.5:  # 500ms warning threshold
                self.log_test("Average load time", "WARN", f"{avg_load_time:.4f}s (> 0.1s but < 0.5s)")
            else:
                self.log_test("Average load time", "FAIL", f"{avg_load_time:.4f}s (> 0.5s threshold)")
            
            # Memory usage test (basic)
            import sys
            initial_modules = len(sys.modules)
            
            # Import modules
            from ignition.graph.tasks.utility_modules import general_utilities, logging_operations
            
            final_modules = len(sys.modules)
            module_increase = final_modules - initial_modules
            
            self.log_test("Module loading impact", "PASS", f"Loaded {module_increase} additional modules")
            
        except Exception as e:
            self.log_test("Performance assessment", "FAIL", f"Error: {str(e)}")
    
    def test_6_backward_compatibility(self):
        """Test 6: Backward Compatibility Verification."""
        print("\n🔍 Test 6: Backward Compatibility Verification")
        print("-" * 50)
        
        try:
            # Test that the main interface hasn't changed
            from ignition.graph.tasks.task_6_utility_system import get_utility_system_functions, get_task_6_metadata
            
            # These should work exactly as before
            functions = get_utility_system_functions()
            metadata = get_task_6_metadata()
            
            # Test function signatures (basic validation)
            if callable(get_utility_system_functions):
                self.log_test("Function callable", "PASS", "get_utility_system_functions is callable")
            else:
                self.log_test("Function callable", "FAIL", "get_utility_system_functions not callable")
            
            if callable(get_task_6_metadata):
                self.log_test("Metadata callable", "PASS", "get_task_6_metadata is callable")
            else:
                self.log_test("Metadata callable", "FAIL", "get_task_6_metadata not callable")
            
            # Test that backup file exists (safety check)
            backup_path = Path("src/ignition/graph/tasks/task_6_utility_system_backup.py")
            if backup_path.exists():
                self.log_test("Backup file exists", "PASS", "Original file backed up safely")
            else:
                self.log_test("Backup file exists", "WARN", "No backup file found")
            
            # Test file sizes
            current_path = Path("src/ignition/graph/tasks/task_6_utility_system.py")
            if current_path.exists():
                with open(current_path, 'r') as f:
                    current_lines = len(f.readlines())
                
                if current_lines < 200:  # Should be much smaller now
                    self.log_test("File size reduction", "PASS", f"Reduced to {current_lines} lines")
                else:
                    self.log_test("File size reduction", "WARN", f"Still {current_lines} lines (expected < 200)")
            
        except Exception as e:
            self.log_test("Backward compatibility", "FAIL", f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Starting Comprehensive Task 6 Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_1_import_validation()
        self.test_2_function_discovery()
        self.test_3_data_structure_validation()
        self.test_4_cross_module_integration()
        self.test_5_performance_assessment()
        self.test_6_backward_compatibility()
        
        total_time = time.time() - start_time
        self.test_results["performance"]["total_test_time"] = total_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        warnings = len(self.test_results["warnings"])
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print(f"Test Duration: {total_time:.2f}s")
        
        # Performance summary
        perf = self.test_results["performance"]
        if "avg_load_time" in perf:
            print(f"\n📈 PERFORMANCE METRICS")
            print(f"Average Load Time: {perf['avg_load_time']:.4f}s")
            print(f"Min/Max Load Time: {perf['min_load_time']:.4f}s / {perf['max_load_time']:.4f}s")
        
        # Show errors if any
        if self.test_results["errors"]:
            print(f"\n❌ ERRORS ({len(self.test_results['errors'])})")
            for error in self.test_results["errors"]:
                print(f"  • {error}")
        
        # Show warnings if any
        if self.test_results["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.test_results['warnings'])})")
            for warning in self.test_results["warnings"]:
                print(f"  • {warning}")
        
        # Final verdict
        print("\n" + "=" * 60)
        if failed == 0:
            print("🎉 ALL TESTS PASSED - READY TO PROCEED TO NEXT FILE")
            return True
        else:
            print("❌ TESTS FAILED - DO NOT PROCEED UNTIL ISSUES ARE RESOLVED")
            return False

if __name__ == "__main__":
    test_suite = Task6TestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1) 