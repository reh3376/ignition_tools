#!/usr/bin/env python3
"""
Automated Task Validation Script

Runs specific validation tests after each task completion to ensure
quality gates are met and no regressions are introduced.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.graph.client import IgnitionGraphClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TaskValidator:
    """Automated validation for task completion."""

    def __init__(self):
        self.client = IgnitionGraphClient()

    def validate_task_completion(self, task_id: int) -> dict[str, Any]:
        """Validate specific task completion based on task ID."""
        print(f"🔍 **TASK {task_id} VALIDATION**")
        print(f"📅 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        if not self.client.connect():
            return {"success": False, "error": "Database connection failed"}

        # Task-specific validation
        if task_id == 1:
            return self._validate_task_1()
        elif task_id == 2:
            return self._validate_task_2()
        elif task_id == 3:
            return self._validate_task_3()
        elif task_id == 4:
            return self._validate_task_4()
        elif task_id == 5:
            return self._validate_task_5_device_communication()
        elif task_id == 6:
            return self._validate_task_6()
        elif task_id == 7:
            return self._validate_task_7()
        else:
            return {
                "success": False,
                "error": f"No validation defined for Task {task_id}",
            }

    def _validate_task_1(self) -> dict[str, Any]:
        """Validate Task 1: Tag System Expansion completion."""
        validation_results = []

        # Test 1: Minimum function count
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
        RETURN count(f) as tag_count
        """
        )
        tag_count = result[0]["tag_count"]

        if tag_count >= 25:
            validation_results.append(
                {
                    "test": "Tag Function Count",
                    "passed": True,
                    "message": f"{tag_count} functions (target: 25+)",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Tag Function Count",
                    "passed": False,
                    "message": f"Only {tag_count} functions (target: 25+)",
                }
            )

        # Test 2: Required functions exist
        required_functions = [
            "system.tag.configure",
            "system.tag.deleteConfiguration",
            "system.tag.queryTagHistory",
            "system.tag.subscribe",
            "system.tag.exportTags",
            "system.tag.browseTags",
            "system.tag.readAll",
            "system.tag.writeAll",
        ]

        missing_functions = []
        for func_name in required_functions:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if result[0]["exists"] == 0:
                missing_functions.append(func_name)

        if len(missing_functions) == 0:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": True,
                    "message": "All key functions present",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": False,
                    "message": f"Missing: {missing_functions}",
                }
            )

        # Test 3: Context mappings validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
        WHERE NOT EXISTS((f)-[:AVAILABLE_IN]->(:Context))
        RETURN count(f) as orphaned
        """
        )
        orphaned = result[0]["orphaned"]

        if orphaned == 0:
            validation_results.append(
                {
                    "test": "Context Mappings",
                    "passed": True,
                    "message": "All tag functions have context mappings",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Context Mappings",
                    "passed": False,
                    "message": f"{orphaned} functions without context",
                }
            )

        # Test 4: Gateway scope validation for configuration functions
        config_functions = [
            "system.tag.configure",
            "system.tag.deleteConfiguration",
            "system.tag.editTags",
        ]
        gateway_issues = 0

        for func_name in config_functions:
            # Check if function exists first
            exists_result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if exists_result[0]["exists"] > 0:
                # If it's a gateway-only function, it should not have non-gateway contexts
                result = self.client.execute_query(
                    f"""
                MATCH (f:Function {{name: "{func_name}"}})
                WHERE f.scope = "gateway"
                WITH f
                MATCH (f)-[:AVAILABLE_IN]->(c:Context)
                WHERE c.name <> "Gateway"
                RETURN count(c) as invalid_contexts
                """
                )

                if result[0]["invalid_contexts"] > 0:
                    gateway_issues += 1

        if gateway_issues == 0:
            validation_results.append(
                {
                    "test": "Gateway Scope Validation",
                    "passed": True,
                    "message": "Configuration functions properly scoped",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Gateway Scope Validation",
                    "passed": False,
                    "message": f"{gateway_issues} scope violations",
                }
            )

        # Test 5: Performance validation
        import time

        start_time = time.time()
        self.client.execute_query(
            """
        MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
        RETURN f.name, f.description
        ORDER BY f.name
        """
        )
        query_time = time.time() - start_time

        if query_time < 0.5:
            validation_results.append(
                {
                    "test": "Query Performance",
                    "passed": True,
                    "message": f"Tag query: {query_time:.3f}s",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Query Performance",
                    "passed": False,
                    "message": f"Slow query: {query_time:.3f}s",
                }
            )

        # Generate summary
        passed_tests = sum(1 for r in validation_results if r["passed"])
        total_tests = len(validation_results)
        success = passed_tests == total_tests

        print("\n📋 **Task 1 Validation Results**:")
        for result in validation_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")

        if success:
            print(f"\n🎉 **Task 1 VALIDATION PASSED** ({passed_tests}/{total_tests})")
        else:
            print(f"\n❌ **Task 1 VALIDATION FAILED** ({passed_tests}/{total_tests} passed)")

        return {
            "success": success,
            "task_id": 1,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": validation_results,
            "tag_function_count": tag_count,
        }

    def _validate_task_2(self) -> dict[str, Any]:
        """Validate Task 2: Database System Expansion completion."""
        validation_results = []

        # Test 1: Minimum function count
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.db.'
        RETURN count(f) as db_count
        """
        )
        db_count = result[0]["db_count"]

        if db_count >= 17:
            validation_results.append(
                {
                    "test": "Database Function Count",
                    "passed": True,
                    "message": f"{db_count} functions (target: 17+)",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Database Function Count",
                    "passed": False,
                    "message": f"Only {db_count} functions (target: 17+)",
                }
            )

        # Test 2: Required functions exist
        required_functions = [
            "system.db.addDatasource",
            "system.db.removeDatasource",
            "system.db.getDatasourceNames",
            "system.db.createConnection",
            "system.db.closeConnection",
            "system.db.beginNamedQueryTransaction",
            "system.db.commitNamedQueryTransaction",
            "system.db.rollbackNamedQueryTransaction",
            "system.db.runNamedQuery",
            "system.db.runNamedQueryUpdate",
            "system.db.runPrepQuery",
            "system.db.runPrepUpdate",
            "system.db.runScalarQuery",
            "system.db.runScalarPrepQuery",
            "system.db.refresh",
            "system.db.execSQLUpdate",
        ]

        missing_functions = []
        for func_name in required_functions:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if result[0]["exists"] == 0:
                missing_functions.append(func_name)

        if len(missing_functions) == 0:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": True,
                    "message": "All key database functions present",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": False,
                    "message": f"Missing: {missing_functions}",
                }
            )

        # Test 3: Category and subcategory validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.db.'
        AND (f.category IS NULL OR f.subcategory IS NULL)
        RETURN count(f) as uncategorized
        """
        )
        uncategorized = result[0]["uncategorized"]

        if uncategorized == 0:
            validation_results.append(
                {
                    "test": "Categorization",
                    "passed": True,
                    "message": "All database functions properly categorized",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Categorization",
                    "passed": False,
                    "message": f"{uncategorized} functions without categories",
                }
            )

        # Test 4: Scope validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:AVAILABLE_IN]->(s:Scope)
        WHERE f.name STARTS WITH 'system.db.'
        RETURN count(DISTINCT f) as scoped_functions
        """
        )
        scoped_functions = result[0]["scoped_functions"]

        if scoped_functions >= 17:
            validation_results.append(
                {
                    "test": "Scope Mappings",
                    "passed": True,
                    "message": "All database functions have scope mappings",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Scope Mappings",
                    "passed": False,
                    "message": f"Only {scoped_functions} functions have scope mappings",
                }
            )

        # Test 5: Task relationship validation
        result = self.client.execute_query(
            """
        MATCH (t:Task {name: 'Task 2'})-[:INCLUDES]->(f:Function)
        WHERE f.name STARTS WITH 'system.db.'
        RETURN count(f) as task_functions
        """
        )
        task_functions = result[0]["task_functions"]

        if task_functions >= 17:
            validation_results.append(
                {
                    "test": "Task Relationships",
                    "passed": True,
                    "message": f"Task 2 includes {task_functions} database functions",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Task Relationships",
                    "passed": False,
                    "message": f"Task 2 only includes {task_functions} functions",
                }
            )

        # Generate summary
        passed_tests = sum(1 for r in validation_results if r["passed"])
        total_tests = len(validation_results)
        success = passed_tests == total_tests

        print("\n📋 **Task 2 Validation Results**:")
        for result in validation_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")

        if success:
            print(f"\n🎉 **Task 2 VALIDATION PASSED** ({passed_tests}/{total_tests})")
        else:
            print(f"\n❌ **Task 2 VALIDATION FAILED** ({passed_tests}/{total_tests} passed)")

        return {
            "success": success,
            "task_id": 2,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": validation_results,
            "db_function_count": db_count,
        }

    def _validate_task_3(self) -> dict[str, Any]:
        """Validate Task 3: GUI System Expansion completion."""
        validation_results = []

        # Test 1: Minimum function count
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.gui.'
        RETURN count(f) as gui_count
        """
        )
        gui_count = result[0]["gui_count"]

        if gui_count >= 25:
            validation_results.append(
                {
                    "test": "GUI Function Count",
                    "passed": True,
                    "message": f"{gui_count} functions (target: 25+)",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "GUI Function Count",
                    "passed": False,
                    "message": f"Only {gui_count} functions (target: 25+)",
                }
            )

        # Test 2: Required functions exist
        required_functions = [
            "system.gui.desktop",
            "system.gui.chooseColor",
            "system.gui.warningBox",
            "system.gui.errorBox",
            "system.gui.getRootContainer",
            "system.gui.getParentWindow",
            "system.gui.getWindow",
            "system.gui.getWindowNames",
            "system.gui.transform",
            "system.gui.openDesktop",
            "system.gui.closeDesktop",
            "system.gui.getClientId",
            "system.gui.getQuality",
            "system.gui.getScreens",
            "system.gui.setScreenIndex",
            "system.gui.createComponent",
            "system.gui.removeComponent",
            "system.gui.refreshComponent",
            "system.gui.getComponentAt",
            "system.gui.setClipboard",
            "system.gui.getClipboard",
            "system.gui.showKeyboard",
            "system.gui.setCursor",
            "system.gui.playSound",
            "system.gui.vibrate",
            "system.gui.fullscreen",
        ]

        missing_functions = []
        for func_name in required_functions:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if result[0]["exists"] == 0:
                missing_functions.append(func_name)

        if len(missing_functions) == 0:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": True,
                    "message": "All key GUI functions present",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": False,
                    "message": f"Missing: {missing_functions}",
                }
            )

        # Test 3: Vision Client scope validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:AVAILABLE_IN]->(s:Scope {name: "Vision Client"})
        WHERE f.name STARTS WITH 'system.gui.'
        RETURN count(f) as vision_functions
        """
        )
        vision_functions = result[0]["vision_functions"]

        if vision_functions >= 25:
            validation_results.append(
                {
                    "test": "Vision Client Scope",
                    "passed": True,
                    "message": f"All {vision_functions} GUI functions available in Vision Client",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Vision Client Scope",
                    "passed": False,
                    "message": f"Only {vision_functions} functions have Vision Client scope",
                }
            )

        # Test 4: Category distribution validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.gui.'
        RETURN f.category as category, count(f) as count
        ORDER BY count DESC
        """
        )

        categories = {r["category"]: r["count"] for r in result}
        expected_categories = [
            "GUI Management",
            "GUI Dialogs",
            "GUI Components",
            "GUI Operations",
        ]

        missing_categories = [cat for cat in expected_categories if cat not in categories]

        if len(missing_categories) == 0 and len(categories) >= 4:
            validation_results.append(
                {
                    "test": "Category Distribution",
                    "passed": True,
                    "message": f"Functions distributed across {len(categories)} categories",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Category Distribution",
                    "passed": False,
                    "message": f"Missing categories: {missing_categories}",
                }
            )

        # Test 5: Task relationship validation
        result = self.client.execute_query(
            """
        MATCH (t:Task {name: 'Task 3'})-[:INCLUDES]->(f:Function)
        WHERE f.name STARTS WITH 'system.gui.'
        RETURN count(f) as task_functions
        """
        )
        task_functions = result[0]["task_functions"]

        if task_functions >= 25:
            validation_results.append(
                {
                    "test": "Task Relationships",
                    "passed": True,
                    "message": f"Task 3 includes {task_functions} GUI functions",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Task Relationships",
                    "passed": False,
                    "message": f"Task 3 only includes {task_functions} functions",
                }
            )

        # Generate summary
        passed_tests = sum(1 for r in validation_results if r["passed"])
        total_tests = len(validation_results)
        success = passed_tests == total_tests

        print("\n📋 **Task 3 Validation Results**:")
        for result in validation_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")

        if success:
            print(f"\n🎉 **Task 3 VALIDATION PASSED** ({passed_tests}/{total_tests})")
        else:
            print(f"\n❌ **Task 3 VALIDATION FAILED** ({passed_tests}/{total_tests} passed)")

        return {
            "success": success,
            "task_id": 3,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": validation_results,
            "gui_function_count": gui_count,
        }

    def _validate_task_4(self) -> dict[str, Any]:
        """Validate Task 4: Perspective System Expansion completion."""
        validation_results = []

        # Test 1: Minimum function count
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.category = 'Perspective System'
        RETURN count(f) as perspective_count
        """
        )
        perspective_count = result[0]["perspective_count"]

        if perspective_count >= 22:
            validation_results.append(
                {
                    "test": "Perspective Function Count",
                    "passed": True,
                    "message": f"{perspective_count} functions (target: 22+)",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Perspective Function Count",
                    "passed": False,
                    "message": f"Only {perspective_count} functions (target: 22+)",
                }
            )

        # Test 2: Required functions exist
        required_functions = [
            "getSessionInfo",
            "navigate",
            "sendMessage",
            "alterFilter",
            "requestCamera",
            "openPopup",
            "closePopup",
            "setSessionProps",
            "getSessionProps",
        ]

        missing_functions = []
        for func_name in required_functions:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            WHERE f.category = 'Perspective System'
            RETURN count(f) as exists
            """
            )

            if result[0]["exists"] == 0:
                missing_functions.append(func_name)

        if len(missing_functions) == 0:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": True,
                    "message": "All key Perspective functions present",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": False,
                    "message": f"Missing: {missing_functions}",
                }
            )

        # Test 3: Perspective Session scope validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:AVAILABLE_IN]->(s:Scope {name: "Perspective Session"})
        WHERE f.category = 'Perspective System'
        RETURN count(f) as perspective_functions
        """
        )
        perspective_functions = result[0]["perspective_functions"]

        if perspective_functions >= 22:
            validation_results.append(
                {
                    "test": "Perspective Session Scope",
                    "passed": True,
                    "message": f"All {perspective_functions} Perspective functions available in Perspective Session",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Perspective Session Scope",
                    "passed": False,
                    "message": f"Only {perspective_functions} functions have Perspective Session scope",
                }
            )

        # Test 4: Category distribution validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.category = 'Perspective System'
        RETURN f.subcategory as subcategory, count(f) as count
        ORDER BY f.subcategory
        """
        )

        subcategories = {r["subcategory"]: r["count"] for r in result}
        expected_subcategories = {
            "Session Management": 6,
            "Navigation": 4,
            "Messaging": 4,
            "Components": 4,
            "Device Operations": 4,
        }

        distribution_correct = True
        for subcat, expected_count in expected_subcategories.items():
            if subcategories.get(subcat, 0) != expected_count:
                distribution_correct = False
                break

        if distribution_correct and len(subcategories) == 5:
            validation_results.append(
                {
                    "test": "Category Distribution",
                    "passed": True,
                    "message": f"Functions properly distributed across {len(subcategories)} subcategories",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Category Distribution",
                    "passed": False,
                    "message": f"Expected distribution: {expected_subcategories}, Actual: {subcategories}",
                }
            )

        # Test 5: Task relationship validation
        result = self.client.execute_query(
            """
        MATCH (t:Task {name: 'Task 4'})-[:INCLUDES]->(f:Function)
        WHERE f.category = 'Perspective System'
        RETURN count(f) as task_functions
        """
        )
        task_functions = result[0]["task_functions"]

        if task_functions >= 22:
            validation_results.append(
                {
                    "test": "Task Relationships",
                    "passed": True,
                    "message": f"Task 4 includes {task_functions} Perspective functions",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Task Relationships",
                    "passed": False,
                    "message": f"Task 4 only includes {task_functions} functions",
                }
            )

        # Generate summary
        passed_tests = sum(1 for r in validation_results if r["passed"])
        total_tests = len(validation_results)
        success = passed_tests == total_tests

        print("\n📋 **Task 4 Validation Results**:")
        for result in validation_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")

        if success:
            print(f"\n🎉 **Task 4 VALIDATION PASSED** ({passed_tests}/{total_tests})")
        else:
            print(f"\n❌ **Task 4 VALIDATION FAILED** ({passed_tests}/{total_tests} passed)")

        return {
            "success": success,
            "task_id": 4,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": validation_results,
            "perspective_function_count": perspective_count,
        }

    def _validate_task_5_device_communication(self) -> dict[str, Any]:
        """
        Validate Task 5: Device Communication Expansion implementation.

        Validates:
        - Function count and completeness
        - Required device communication functions
        - Protocol-specific patterns
        - Scope mapping accuracy
        - Task relationships
        """

        print("\n" + "=" * 60)
        print("🔧 TASK 5: DEVICE COMMUNICATION EXPANSION VALIDATION")
        print("=" * 60)

        try:
            self.client.connect()

            # Test 1: Function Count Validation
            print("\n📊 Test 1: Function Count Validation")

            count_query = """
            MATCH (f:Function)
            WHERE f.name STARTS WITH 'system.opc.' OR
                  f.name STARTS WITH 'system.opcua.' OR
                  f.name STARTS WITH 'system.device.' OR
                  f.name STARTS WITH 'system.bacnet.' OR
                  f.name STARTS WITH 'system.dnp3.'
            RETURN count(f) as function_count
            """

            result = self.client.execute_query(count_query)
            actual_count = result[0]["function_count"] if result else 0
            expected_count = 37  # Task 5 target

            if actual_count >= expected_count:
                print(f"   ✅ Function count: {actual_count}/{expected_count} (Expected: ≥{expected_count})")
                test_1_passed = True
            else:
                print(f"   ❌ Function count: {actual_count}/{expected_count} (Expected: ≥{expected_count})")
                test_1_passed = False

            # Test 2: Required Device Communication Functions
            print("\n🔧 Test 2: Required Device Communication Functions")

            required_functions = [
                # OPC Classic Core
                "system.opc.readValues",
                "system.opc.writeValues",
                "system.opc.browseSimple",
                # OPC-UA Core
                "system.opcua.readValues",
                "system.opcua.writeValues",
                "system.opcua.browseNodes",
                "system.opcua.addConnection",
                # Device Management Core
                "system.device.addDevice",
                "system.device.removeDevice",
                "system.device.getDeviceStatus",
                "system.device.listDevices",
                # BACnet Protocol Core
                "system.bacnet.readProperty",
                "system.bacnet.writeProperty",
                "system.bacnet.synchronizeTime",
                # DNP3 Protocol Core
                "system.dnp3.request",
                "system.dnp3.sendDataSet",
                "system.dnp3.readClass0Data",
            ]

            missing_functions = []
            for func_name in required_functions:
                check_query = "MATCH (f:Function {name: $name}) RETURN f.name"
                result = self.client.execute_query(check_query, {"name": func_name})

                if result:
                    print(f"   ✅ {func_name}")
                else:
                    print(f"   ❌ {func_name} - MISSING")
                    missing_functions.append(func_name)

            test_2_passed = len(missing_functions) == 0
            if test_2_passed:
                print(f"   ✅ All {len(required_functions)} required functions present")
            else:
                print(f"   ❌ {len(missing_functions)} required functions missing")

            # Test 3: Device Communication Patterns
            print("\n🔍 Test 3: Device Communication Patterns")

            expected_patterns = [
                "opc_classic_read",
                "opcua_read_operation",
                "device_configuration",
                "bacnet_property_read",
                "dnp3_request",
                "industrial_communication",
                "device_monitoring",
                "protocol_communication",
            ]

            pattern_results = {}
            for pattern in expected_patterns:
                pattern_query = """
                MATCH (f:Function)-[:MATCHES_PATTERN]->(p:Pattern {name: $pattern})
                WHERE f.name STARTS WITH 'system.opc.' OR
                      f.name STARTS WITH 'system.opcua.' OR
                      f.name STARTS WITH 'system.device.' OR
                      f.name STARTS WITH 'system.bacnet.' OR
                      f.name STARTS WITH 'system.dnp3.'
                RETURN count(f) as function_count
                """

                result = self.client.execute_query(pattern_query, {"pattern": pattern})
                count = result[0]["function_count"] if result else 0
                pattern_results[pattern] = count

                if count > 0:
                    print(f"   ✅ {pattern}: {count} functions")
                else:
                    print(f"   ⚠️  {pattern}: {count} functions")

            # At least 6 patterns should have functions
            active_patterns = sum(1 for count in pattern_results.values() if count > 0)
            test_3_passed = active_patterns >= 6

            if test_3_passed:
                print(f"   ✅ Pattern coverage: {active_patterns}/8 patterns active")
            else:
                print(f"   ❌ Pattern coverage: {active_patterns}/8 patterns active (Expected: ≥6)")

            # Test 4: Scope collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.Mapping Validation
            print(
                "\n🎯 Test 4: Scope collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.Mapping Validation"
            )

            scope_query = """
            MATCH (f:Function)-[:AVAILABLE_IN]->(s:Scope)
            WHERE f.name STARTS WITH 'system.opc.' OR
                  f.name STARTS WITH 'system.opcua.' OR
                  f.name STARTS WITH 'system.device.' OR
                  f.name STARTS WITH 'system.bacnet.' OR
                  f.name STARTS WITH 'system.dnp3.'
            RETURN s.name as scope, count(f) as function_count
            ORDER BY function_count DESC
            """

            scope_results = self.client.execute_query(scope_query)
            gateway_functions = 0
            client_functions = 0

            for result in scope_results:
                scope_name = result["scope"]
                func_count = result["function_count"]

                if scope_name == "Gateway":
                    gateway_functions = func_count
                elif scope_name in ["Vision Client", "Perspective Session"]:
                    client_functions += func_count

                print(f"   📊 {scope_name}: {func_count} functions")

            # Most device communication functions should be Gateway scope
            test_4_passed = gateway_functions >= 30  # Most device operations are gateway-side

            if test_4_passed:
                print(
                    f"   ✅ Scope distribution appropriate (Gateway: {gateway_functions}, Client: {client_functions})"
                )
            else:
                print(f"   ❌ Scope distribution issues (Gateway: {gateway_functions}, Client: {client_functions})")

            # Test 5: Task Relationships
            print("\n🔗 Test 5: Task Relationships")

            # Check Task 5 node
            task_query = """
            MATCH (t:Task {task_id: 'task_5'})
            RETURN t.name as name, t.priority as priority, t.status as status
            """

            task_result = self.client.execute_query(task_query)
            if task_result:
                task_info = task_result[0]
                print(f"   ✅ Task 5 Node: {task_info['name']}")
                print(f"   📊 Priority: {task_info['priority']}")
                print(f"   🎯 Status: {task_info.get('status', 'IN_PROGRESS')}")
                test_5_passed = True
            else:
                print("   ❌ Task 5 node not found")
                test_5_passed = False

                # Overall validation result
            all_tests = [
                test_1_passed,
                test_2_passed,
                test_3_passed,
                test_4_passed,
                test_5_passed,
            ]
            passed_tests = sum(all_tests)
            total_tests = len(all_tests)

            print("\n" + "=" * 60)
            print("📊 TASK 5 VALIDATION SUMMARY")
            print("=" * 60)
            print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
            print(f"📈 Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

            if passed_tests == total_tests:
                print("🎉 TASK 5: DEVICE COMMUNICATION EXPANSION - ALL TESTS PASSED!")
                success = True
            else:
                print("⚠️  TASK 5: Some tests failed - review implementation")
                success = False

            return {
                "success": success,
                "task_id": 5,
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "function_count": actual_count,
                "missing_functions": missing_functions if not test_2_passed else [],
                "pattern_coverage": active_patterns,
                "gateway_functions": gateway_functions,
                "client_functions": client_functions,
            }

        except Exception as e:
            print(f"❌ Task 5 validation error: {e}")
            return {"success": False, "task_id": 5, "error": str(e)}

        finally:
            self.client.disconnect()

    def _validate_task_6(self) -> dict[str, Any]:
        """Validate Task 6: Utility System Expansion completion."""
        validation_results = []

        # Test 1: Minimum function count
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.util.'
        RETURN count(f) as util_count
        """
        )
        util_count = result[0]["util_count"]

        if util_count >= 40:
            validation_results.append(
                {
                    "test": "Utility Function Count",
                    "passed": True,
                    "message": f"{util_count} functions (target: 40+)",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Utility Function Count",
                    "passed": False,
                    "message": f"Only {util_count} functions (target: 40+)",
                }
            )

        # Test 2: Required utility functions exist
        required_functions = [
            "system.util.translate",
            "system.util.getLocale",
            "system.util.setLocale",
            "system.util.version",
            "system.util.restart",
            "system.util.shutdown",
            "system.util.getMemoryUsage",
            "system.util.getSystemInfo",
        ]

        missing_functions = []
        for func_name in required_functions:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if result[0]["exists"] == 0:
                missing_functions.append(func_name)

        if not missing_functions:
            validation_results.append(
                {
                    "test": "Required Utility Functions",
                    "passed": True,
                    "message": f"All {len(required_functions)} required functions exist",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Required Utility Functions",
                    "passed": False,
                    "message": f"Missing: {', '.join(missing_functions)}",
                }
            )

        # Test 3: Utility function categories
        category_patterns = [
            "General Utilities",
            "Logging Operations",
            "Project Management",
            "Performance Monitoring",
            "System Configuration",
            "File Operations",
        ]

        active_categories = []
        for category in category_patterns:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function)
            WHERE f.category = "{category}"
            RETURN count(f) as count
            """
            )
            if result[0]["count"] > 0:
                active_categories.append(category)

        if len(active_categories) >= 5:
            validation_results.append(
                {
                    "test": "Utility Categories Coverage",
                    "passed": True,
                    "message": f"{len(active_categories)}/{len(category_patterns)} categories active",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Utility Categories Coverage",
                    "passed": False,
                    "message": f"Only {len(active_categories)}/{len(category_patterns)} categories active",
                }
            )

        # Test 4: Task 6 completion marker
        result = self.client.execute_query(
            """
        MATCH (t:Task {id: 6})
        RETURN count(t) as task_exists
        """
        )

        if result[0]["task_exists"] > 0:
            validation_results.append(
                {
                    "test": "Task 6 Completion Marker",
                    "passed": True,
                    "message": "Task 6 node exists in database",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Task 6 Completion Marker",
                    "passed": False,
                    "message": "Task 6 node missing from database",
                }
            )

        # Calculate success metrics
        passed_tests = sum(1 for result in validation_results if result["passed"])
        total_tests = len(validation_results)
        success = passed_tests == total_tests

        # Display results
        print("\n📊 Task 6 Validation Results:")
        for result in validation_results:
            status = "✅" if result["passed"] else "❌"
            print(f"   {status} {result['test']}: {result['message']}")

        if success:
            print(f"\n🎉 **Task 6 VALIDATION PASSED** ({passed_tests}/{total_tests})")
        else:
            print(f"\n❌ **Task 6 VALIDATION FAILED** ({passed_tests}/{total_tests} passed)")

        return {
            "success": success,
            "task_id": 6,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": validation_results,
            "util_function_count": util_count,
        }

    def _validate_task_7(self) -> dict[str, Any]:
        """Validate Task 7: Alarm System Expansion completion."""
        validation_results = []

        # Test 1: Minimum function count
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.name STARTS WITH 'system.alarm.'
        RETURN count(f) as alarm_count
        """
        )
        alarm_count = result[0]["alarm_count"]

        if alarm_count >= 25:
            validation_results.append(
                {
                    "test": "Alarm Function Count",
                    "passed": True,
                    "message": f"{alarm_count} functions (target: 25+)",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Alarm Function Count",
                    "passed": False,
                    "message": f"Only {alarm_count} functions (target: 25+)",
                }
            )

        # Test 2: Required core alarm functions exist
        required_functions = [
            "system.alarm.queryJournal",
            "system.alarm.queryStatus",
            "system.alarm.acknowledge",
            "system.alarm.cancel",
            "system.alarm.shelve",
            "system.alarm.unshelve",
            "system.alarm.clearAlarm",
            "system.alarm.listPipelines",
            "system.alarm.getDisplayPaths",
            "system.alarm.getRoster",
        ]

        missing_functions = []
        for func_name in required_functions:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if result[0]["exists"] == 0:
                missing_functions.append(func_name)

        if len(missing_functions) == 0:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": True,
                    "message": "All core alarm functions present",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": False,
                    "message": f"Missing: {missing_functions}",
                }
            )

        # Test 3: Alarm category and patterns validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:MATCHES_PATTERN]->(p:Pattern)
        WHERE f.name STARTS WITH 'system.alarm.'
        AND (p.name CONTAINS 'alarm_' OR p.name CONTAINS 'journal_' OR p.name CONTAINS 'notification_')
        RETURN count(DISTINCT f) as functions_with_patterns
        """
        )
        functions_with_patterns = result[0]["functions_with_patterns"]

        if functions_with_patterns >= 20:
            validation_results.append(
                {
                    "test": "Alarm Patterns",
                    "passed": True,
                    "message": f"{functions_with_patterns} functions have alarm-specific patterns",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Alarm Patterns",
                    "passed": False,
                    "message": f"Only {functions_with_patterns} functions have alarm patterns",
                }
            )

        # Test 4: Scope validation - alarm functions should be available in all contexts
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:AVAILABLE_IN]->(s:Scope)
        WHERE f.name STARTS WITH 'system.alarm.'
        RETURN count(DISTINCT f) as scoped_functions
        """
        )
        scoped_functions = result[0]["scoped_functions"]

        if scoped_functions >= 25:
            validation_results.append(
                {
                    "test": "Scope Mappings",
                    "passed": True,
                    "message": f"All {scoped_functions} alarm functions have scope mappings",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Scope Mappings",
                    "passed": False,
                    "message": f"Only {scoped_functions} functions have scope mappings",
                }
            )

        # Test 5: Task 7 relationship validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)
        WHERE f.task = 'Task 7: Alarm System'
        RETURN count(f) as task7_functions
        """
        )
        task7_functions = result[0]["task7_functions"]

        if task7_functions >= 25:
            validation_results.append(
                {
                    "test": "Task 7 Relationships",
                    "passed": True,
                    "message": f"Task 7 includes {task7_functions} alarm functions",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Task 7 Relationships",
                    "passed": False,
                    "message": f"Task 7 only includes {task7_functions} functions",
                }
            )

        # Generate summary
        passed_tests = sum(1 for r in validation_results if r["passed"])
        total_tests = len(validation_results)
        success = passed_tests == total_tests

        print("\n📋 **Task 7 Validation Results**:")
        for result in validation_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")

        if success:
            print(f"\n🎉 **Task 7 VALIDATION PASSED** ({passed_tests}/{total_tests})")
        else:
            print(f"\n❌ **Task 7 VALIDATION FAILED** ({passed_tests}/{total_tests} passed)")

        return {
            "success": success,
            "task_id": 7,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": validation_results,
            "alarm_function_count": alarm_count,
        }

    def generate_validation_report(self, task_id: int, results: dict[str, Any]) -> str:
        """Generate a detailed validation report."""
        report_data = {
            "validation_timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "results": results,
            "system_info": {
                "total_functions": self._get_total_function_count(),
                "completion_percentage": self._get_completion_percentage(),
            },
        }

        # Save report
        report_file = f"task_{task_id}_validation_report.json"
        report_path = Path("reports") / report_file
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return str(report_path)

    def _get_total_function_count(self) -> int:
        """Get total function count."""
        result = self.client.execute_query("MATCH (f:Function) RETURN count(f) as total")
        return result[0]["total"]

    def _get_completion_percentage(self) -> float:
        """Get completion percentage."""
        total = self._get_total_function_count()
        return (total / 400) * 100


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python automated_task_validation.py <task_id>")
        print("Example: python automated_task_validation.py 1")
        sys.exit(1)

    try:
        task_id = int(sys.argv[1])
    except ValueError:
        print("Error: Task ID must be a number")
        sys.exit(1)

    validator = TaskValidator()
    results = validator.validate_task_completion(task_id)

    if results.get("success", False):
        print(f"\n✅ Task {task_id} validation completed successfully!")

        # Generate detailed report
        report_path = validator.generate_validation_report(task_id, results)
        print(f"📄 **Detailed Report**: {report_path}")

        return True
    else:
        print(f"\n❌ Task {task_id} validation failed!")
        if "error" in results:
            print(f"Error: {results['error']}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
