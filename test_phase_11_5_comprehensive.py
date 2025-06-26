#!/usr/bin/env python3
"""Comprehensive Test Suite for Phase 11.5: Industrial Dataset Curation & AI Model Preparation.

Following the crawl_mcp.py methodology for structured testing:
- Comprehensive validation and error handling
- Environment variable configuration
- Modular testing and progressive complexity
- Resource management and cleanup
- User-friendly error messages

This test suite validates all Phase 11.5 components:
- Industrial dataset curation module
- Data ingestion framework
- Variable type classification system
- CLI commands integration
- File structure and documentation
"""

import asyncio
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ignition.modules.sme_agent.cli.dataset_curation_commands import (
        dataset_curation,
    )
    from ignition.modules.sme_agent.data_ingestion_framework import (
        DataIngestionFramework,
    )
    from ignition.modules.sme_agent.industrial_dataset_curation import (
        ControllerMetadata,
        ControllerType,
        DataSourceType,
        IndustrialDatasetCurator,
        VariableMetadata,
        VariableType,
        format_validation_error,
        validate_data_source,
        validate_environment,
    )
    from ignition.modules.sme_agent.variable_type_classifier import (
        VariableTypeClassifier,
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Ensure all Phase 11.5 modules are properly installed")
    sys.exit(1)


class Phase115TestSuite:
    """Comprehensive test suite for Phase 11.5 implementation."""

    def __init__(self):
        """Initialize test suite."""
        self.test_results: dict[str, Any] = {}
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results."""
        self.test_count += 1
        try:
            print(f"\n🧪 Testing: {test_name}")
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSED")
                self.passed_count += 1
                self.test_results[test_name] = {"status": "PASSED", "error": None}
                return True
            else:
                print(f"❌ {test_name}: FAILED")
                self.failed_count += 1
                self.test_results[test_name] = {
                    "status": "FAILED",
                    "error": "Test returned False",
                }
                return False
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            self.failed_count += 1
            self.test_results[test_name] = {"status": "ERROR", "error": str(e)}
            return False

    def test_1_module_imports(self) -> bool:
        """Test 1: Verify all Phase 11.5 modules can be imported."""
        try:
            # Test core module imports
            from ignition.modules.sme_agent.cli.dataset_curation_commands import (
                dataset_curation,
            )
            from ignition.modules.sme_agent.data_ingestion_framework import (
                DataIngestionFramework,
            )
            from ignition.modules.sme_agent.industrial_dataset_curation import (
                DataSourceType,
                IndustrialDatasetCurator,
                VariableType,
            )
            from ignition.modules.sme_agent.variable_type_classifier import (
                VariableTypeClassifier,
            )

            print("  ✓ All Phase 11.5 modules imported successfully")
            return True
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            return False

    def test_2_environment_validation(self) -> bool:
        """Test 2: Verify environment validation functionality."""
        try:
            # Test environment validation
            validation_results = validate_environment()

            if not isinstance(validation_results, dict):
                print("  ❌ Environment validation should return dict")
                return False

            expected_keys = [
                "python_environment",
                "required_packages",
                "data_directories",
                "database_connections",
                "opc_ua_config",
            ]

            for key in expected_keys:
                if key not in validation_results:
                    print(f"  ❌ Missing validation key: {key}")
                    return False

            print(f"  ✓ Environment validation completed with {len(validation_results)} components")
            return True
        except Exception as e:
            print(f"  ❌ Environment validation failed: {e}")
            return False

    def test_3_dataset_curator_initialization(self) -> bool:
        """Test 3: Verify dataset curator initialization."""
        try:
            # Test curator initialization with different complexity levels
            complexity_levels = ["basic", "standard", "advanced", "enterprise"]

            for level in complexity_levels:
                curator = IndustrialDatasetCurator(level)

                if not hasattr(curator, "complexity_level"):
                    print("  ❌ Curator missing complexity_level attribute")
                    return False

                if curator.complexity_level != level:
                    print(f"  ❌ Complexity level mismatch: {curator.complexity_level} != {level}")
                    return False

                # Test status method
                status = curator.get_validation_status()
                if not isinstance(status, dict):
                    print(f"  ❌ Status should be dict, got {type(status)}")
                    return False

            print("  ✓ Dataset curator initialized successfully for all complexity levels")
            return True
        except Exception as e:
            print(f"  ❌ Dataset curator initialization failed: {e}")
            return False

    def test_4_variable_metadata_management(self) -> bool:
        """Test 4: Verify variable metadata management."""
        try:
            curator = IndustrialDatasetCurator("standard")

            # Test adding variables
            test_variables = [
                VariableMetadata(
                    name="reactor_temperature",
                    variable_type=VariableType.PRIMARY_PV,
                    engineering_units="°C",
                    high_limit=150.0,
                    low_limit=0.0,
                    description="Reactor temperature measurement",
                ),
                VariableMetadata(
                    name="valve_output",
                    variable_type=VariableType.CONTROL_VARIABLE,
                    engineering_units="%",
                    high_limit=100.0,
                    low_limit=0.0,
                    description="Control valve output",
                ),
                VariableMetadata(
                    name="process_setpoint",
                    variable_type=VariableType.SETPOINT,
                    engineering_units="°C",
                    description="Process temperature setpoint",
                ),
            ]

            for var_metadata in test_variables:
                success = curator.add_variable(var_metadata)
                if not success:
                    print(f"  ❌ Failed to add variable: {var_metadata.name}")
                    return False

            # Verify variables were added
            if len(curator.variables) != len(test_variables):
                print(f"  ❌ Expected {len(test_variables)} variables, got {len(curator.variables)}")
                return False

            print(f"  ✓ Successfully managed {len(test_variables)} variable metadata entries")
            return True
        except Exception as e:
            print(f"  ❌ Variable metadata management failed: {e}")
            return False

    def test_5_data_ingestion_framework(self) -> bool:
        """Test 5: Verify data ingestion framework functionality."""
        try:
            curator = IndustrialDatasetCurator("standard")
            ingestion_framework = DataIngestionFramework(curator)

            # Create test CSV data
            test_data = pd.DataFrame(
                {
                    "timestamp": pd.date_range("2024-01-01", periods=100, freq="1min"),
                    "reactor_temp": 50 + 10 * pd.np.random.randn(100),
                    "valve_output": 50 + 20 * pd.np.random.randn(100),
                    "pressure": 1000 + 100 * pd.np.random.randn(100),
                    "flow_rate": 100 + 10 * pd.np.random.randn(100),
                }
            )

            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
                test_data.to_csv(f.name, index=False)
                temp_file = f.name

            try:
                # Test CSV ingestion
                result = asyncio.run(
                    ingestion_framework.ingest_csv_data(file_path=temp_file, timestamp_column="timestamp")
                )

                if not result.get("success", False):
                    print(f"  ❌ CSV ingestion failed: {result.get('error', 'Unknown error')}")
                    return False

                if result["rows_processed"] != 100:
                    print(f"  ❌ Expected 100 rows, processed {result['rows_processed']}")
                    return False

                if result["columns_processed"] != 4:  # timestamp becomes index
                    print(f"  ❌ Expected 4 columns, processed {result['columns_processed']}")
                    return False

                # Verify quality report
                quality_report = result.get("quality_report", {})
                if "quality_score" not in quality_report:
                    print("  ❌ Missing quality score in report")
                    return False

                print(
                    f"  ✓ Data ingestion successful: {result['rows_processed']} rows, quality score: {quality_report['quality_score']:.1f}"  # noqa: E501
                )
                return True

            finally:
                # Clean up temporary file
                os.unlink(temp_file)

        except Exception as e:
            print(f"  ❌ Data ingestion framework test failed: {e}")
            return False

    def test_6_variable_type_classification(self) -> bool:
        """Test 6: Verify variable type classification system."""
        try:
            curator = IndustrialDatasetCurator("standard")
            classifier = VariableTypeClassifier(curator)

            # Create test dataset with various variable types
            test_data = pd.DataFrame(
                {
                    "reactor_temperature": 50 + 10 * pd.np.random.randn(100),
                    "valve_output_cv": pd.np.clip(50 + 20 * pd.np.random.randn(100), 0, 100),
                    "temp_setpoint": [75] * 100,  # Constant setpoint
                    "ambient_temp_dv": 20 + 5 * pd.np.random.randn(100),
                    "pump_status_state": pd.np.random.choice([0, 1], 100),
                    "calculated_spc": 50 + 5 * pd.np.random.randn(100),
                }
            )

            # Add dataset to curator
            curator.datasets["test_classification"] = test_data

            # Test variable classification
            result = classifier.classify_variables_from_dataset(
                dataset_name="test_classification", confidence_threshold=0.5
            )

            if not result.get("success", False):
                print(f"  ❌ Classification failed: {result.get('error', 'Unknown error')}")
                return False

            if result["total_variables"] != 6:
                print(f"  ❌ Expected 6 variables, got {result['total_variables']}")
                return False

            # Verify classification results
            classification_results = result.get("classification_results", {})

            # Check specific classifications
            expected_classifications = {
                "reactor_temperature": [VariableType.PRIMARY_PV],
                "valve_output_cv": [VariableType.CONTROL_VARIABLE],
                "temp_setpoint": [VariableType.SETPOINT],
                "ambient_temp_dv": [VariableType.DISTURBANCE_VARIABLE],
                "pump_status_state": [VariableType.PROCESS_STATE],
                "calculated_spc": [VariableType.SECONDARY_PV],
            }

            correct_classifications = 0
            for var_name, expected_types in expected_classifications.items():
                if var_name in classification_results:
                    classified_type = classification_results[var_name]["variable_type"]
                    if classified_type in expected_types:
                        correct_classifications += 1

            accuracy = correct_classifications / len(expected_classifications) * 100

            print(
                f"  ✓ Variable classification completed: {result['classified_variables']}/{result['total_variables']} classified, {accuracy:.1f}% accuracy"  # noqa: E501
            )
            return True

        except Exception as e:
            print(f"  ❌ Variable type classification test failed: {e}")
            return False

    def test_7_cli_commands_integration(self) -> bool:
        """Test 7: Verify CLI commands integration."""
        try:
            # Test that CLI commands are properly defined
            if not hasattr(dataset_curation, "commands"):
                print("  ❌ Dataset curation CLI missing commands attribute")
                return False

            # Check for required commands
            expected_commands = [
                "validate-env",
                "info",
                "ingest-csv",
                "classify-variables",
                "status",
                "add-variable",
                "list-variable-types",
            ]

            available_commands = list(dataset_curation.commands.keys())

            for cmd in expected_commands:
                if cmd not in available_commands:
                    print(f"  ❌ Missing CLI command: {cmd}")
                    return False

            print(f"  ✓ All {len(expected_commands)} CLI commands are properly integrated")
            return True

        except Exception as e:
            print(f"  ❌ CLI commands integration test failed: {e}")
            return False

    def test_8_data_source_validation(self) -> bool:
        """Test 8: Verify data source validation functionality."""
        try:
            # Test CSV file validation
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
                f.write("timestamp,value\n2024-01-01,100\n")
                temp_csv = f.name

            try:
                # Valid CSV file
                result = validate_data_source(temp_csv, DataSourceType.CSV_XLS)
                if not result.get("valid", False):
                    print(f"  ❌ Valid CSV file failed validation: {result.get('error')}")
                    return False

                # Invalid file path
                result = validate_data_source("nonexistent.csv", DataSourceType.CSV_XLS)
                if result.get("valid", True):
                    print("  ❌ Nonexistent file should fail validation")
                    return False

                # OPC-UA URL validation
                result = validate_data_source("opc.tcp://localhost:4840", DataSourceType.OPC_UA)
                if not result.get("valid", False):
                    print(f"  ❌ Valid OPC-UA URL failed validation: {result.get('error')}")
                    return False

                # Invalid OPC-UA URL
                result = validate_data_source("http://localhost", DataSourceType.OPC_UA)
                if result.get("valid", True):
                    print("  ❌ Invalid OPC-UA URL should fail validation")
                    return False

                print("  ✓ Data source validation working correctly")
                return True

            finally:
                os.unlink(temp_csv)

        except Exception as e:
            print(f"  ❌ Data source validation test failed: {e}")
            return False

    def test_9_file_structure_validation(self) -> bool:
        """Test 9: Verify Phase 11.5 file structure."""
        try:
            base_path = Path("src/ignition/modules/sme_agent")

            # Check for required files
            required_files = [
                "industrial_dataset_curation.py",
                "data_ingestion_framework.py",
                "variable_type_classifier.py",
                "cli/dataset_curation_commands.py",
            ]

            for file_path in required_files:
                full_path = base_path / file_path
                if not full_path.exists():
                    print(f"  ❌ Missing required file: {full_path}")
                    return False

                # Check file is not empty
                if full_path.stat().st_size == 0:
                    print(f"  ❌ Empty file: {full_path}")
                    return False

            # Check CLI integration
            cli_init = base_path / "cli" / "__init__.py"
            if cli_init.exists():
                content = cli_init.read_text()
                if "dataset_curation" not in content:
                    print("  ❌ CLI __init__.py missing dataset_curation import")
                    return False

            print(f"  ✓ All {len(required_files)} required files present and valid")
            return True

        except Exception as e:
            print(f"  ❌ File structure validation failed: {e}")
            return False

    def test_10_error_handling_validation(self) -> bool:
        """Test 10: Verify comprehensive error handling."""
        try:
            curator = IndustrialDatasetCurator("standard")

            # Test invalid variable metadata
            invalid_metadata = VariableMetadata(
                name="",  # Invalid empty name
                variable_type=VariableType.PRIMARY_PV,
                engineering_units="°C",
            )

            success = curator.add_variable(invalid_metadata)
            if success:
                print("  ❌ Should fail for invalid variable metadata")
                return False

            # Test format_validation_error function
            test_error = FileNotFoundError("Test file not found")
            formatted_error = format_validation_error(test_error, "Test context")

            if "Test context" not in formatted_error:
                print("  ❌ Error formatting should include context")
                return False

            if "file not found" not in formatted_error.lower():
                print("  ❌ Error formatting should handle file not found errors")
                return False

            # Test data source validation with invalid inputs
            result = validate_data_source("", DataSourceType.CSV_XLS)
            if result.get("valid", True):
                print("  ❌ Empty data source path should fail validation")
                return False

            print("  ✓ Error handling validation successful")
            return True

        except Exception as e:
            print(f"  ❌ Error handling validation failed: {e}")
            return False

    def test_11_integration_examples(self) -> bool:
        """Test 11: Verify integration examples work correctly."""
        try:
            # Test full workflow integration
            curator = IndustrialDatasetCurator("standard")
            ingestion_framework = DataIngestionFramework(curator)
            classifier = VariableTypeClassifier(curator)

            # Create comprehensive test dataset
            test_data = pd.DataFrame(
                {
                    "timestamp": pd.date_range("2024-01-01", periods=50, freq="1min"),
                    "reactor_temp_pv": 75 + 10 * pd.np.random.randn(50),
                    "cooling_valve_cv": pd.np.clip(50 + 20 * pd.np.random.randn(50), 0, 100),
                    "temp_setpoint_sp": [80] * 50,
                    "ambient_temp_dv": 22 + 3 * pd.np.random.randn(50),
                    "pump_status": pd.np.random.choice([0, 1], 50),
                    "calculated_efficiency": 85 + 5 * pd.np.random.randn(50),
                }
            )

            # Save and ingest data
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
                test_data.to_csv(f.name, index=False)
                temp_file = f.name

            try:
                # Step 1: Ingest data
                ingestion_result = asyncio.run(
                    ingestion_framework.ingest_csv_data(file_path=temp_file, timestamp_column="timestamp")
                )

                if not ingestion_result.get("success"):
                    print(f"  ❌ Integration ingestion failed: {ingestion_result.get('error')}")
                    return False

                # Step 2: Classify variables
                classification_result = classifier.classify_variables_from_dataset(
                    dataset_name=ingestion_result["dataset_name"],
                    confidence_threshold=0.5,
                )

                if not classification_result.get("success"):
                    print(f"  ❌ Integration classification failed: {classification_result.get('error')}")
                    return False

                # Step 3: Get summary
                summary = classifier.get_classification_summary()

                if summary.get("error"):
                    print(f"  ❌ Integration summary failed: {summary.get('error')}")
                    return False

                print(
                    f"  ✓ Full workflow integration successful: {classification_result['classified_variables']} variables classified"  # noqa: E501
                )
                return True

            finally:
                os.unlink(temp_file)

        except Exception as e:
            print(f"  ❌ Integration examples test failed: {e}")
            return False

    def test_12_dependencies_validation(self) -> bool:
        """Test 12: Verify all required dependencies are available."""
        try:
            required_packages = ["pandas", "numpy", "click", "rich", "python-dotenv"]

            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    print(f"  ❌ Missing required package: {package}")
                    return False

            # Test specific functionality
            import numpy as np
            import pandas as pd
            from rich.console import Console

            # Test basic functionality
            pd.DataFrame({"test": [1, 2, 3]})
            np.array([1, 2, 3])
            Console()

            print(f"  ✓ All {len(required_packages)} required dependencies validated")
            return True

        except Exception as e:
            print(f"  ❌ Dependencies validation failed: {e}")
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run all tests and return comprehensive results."""
        print("🚀 Starting Phase 11.5 Comprehensive Test Suite")
        print("=" * 60)

        start_time = datetime.now()

        # Run all tests
        test_methods = [
            ("Module Imports", self.test_1_module_imports),
            ("Environment Validation", self.test_2_environment_validation),
            (
                "Dataset Curator Initialization",
                self.test_3_dataset_curator_initialization,
            ),
            ("Variable Metadata Management", self.test_4_variable_metadata_management),
            ("Data Ingestion Framework", self.test_5_data_ingestion_framework),
            ("Variable Type Classification", self.test_6_variable_type_classification),
            ("CLI Commands Integration", self.test_7_cli_commands_integration),
            ("Data Source Validation", self.test_8_data_source_validation),
            ("File Structure Validation", self.test_9_file_structure_validation),
            ("Error Handling Validation", self.test_10_error_handling_validation),
            ("Integration Examples", self.test_11_integration_examples),
            ("Dependencies Validation", self.test_12_dependencies_validation),
        ]

        for test_name, test_method in test_methods:
            self.run_test(test_name, test_method)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Generate comprehensive report
        print("\n" + "=" * 60)
        print("📊 PHASE 11.5 TEST RESULTS SUMMARY")
        print("=" * 60)

        print(f"🎯 Total Tests: {self.test_count}")
        print(f"✅ Passed: {self.passed_count}")
        print(f"❌ Failed: {self.failed_count}")
        print(f"📈 Success Rate: {(self.passed_count / self.test_count * 100):.1f}%")
        print(f"⏱️ Duration: {duration:.2f} seconds")

        if self.failed_count > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if result["status"] != "PASSED":
                    print(f"  • {test_name}: {result['status']}")
                    if result["error"]:
                        print(f"    Error: {result['error']}")

        # Overall assessment
        if self.passed_count == self.test_count:
            print("\n🎉 ALL TESTS PASSED! Phase 11.5 implementation is ready for production.")
        elif self.passed_count >= self.test_count * 0.8:
            print("\n⚠️ Most tests passed. Review failed tests before deployment.")
        else:
            print("\n❌ Significant issues detected. Address failed tests before proceeding.")

        return {
            "total_tests": self.test_count,
            "passed_tests": self.passed_count,
            "failed_tests": self.failed_count,
            "success_rate": ((self.passed_count / self.test_count * 100) if self.test_count > 0 else 0),
            "duration_seconds": duration,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "phase": "11.5",
            "description": "Industrial Dataset Curation & AI Model Preparation",
        }


def main():
    """Main function to run the comprehensive test suite."""
    test_suite = Phase115TestSuite()
    results = test_suite.run_all_tests()

    # Return appropriate exit code
    if results["failed_tests"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
