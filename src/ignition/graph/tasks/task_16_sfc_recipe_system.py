"""Task 16: Sequential Function Charts & Recipe Management System.

This module implements comprehensive SFC (Sequential Function Chart) and Recipe Management
functionality for Ignition automation systems, providing industrial-grade sequence control
and recipe execution capabilities.

Author: IGN Scripts - AI Assistant
Created: 2025-01-28
Task: 16 - SFC & Recipe Management (20+ functions)
"""

import logging
from typing import Any

from src.ignition.graph.client import IgnitionGraphClient

# Configure logging
logger = logging.getLogger(__name__)


class Task16SFCRecipeSystem:
    """Sequential Function Charts & Recipe Management System Implementation.

    Provides comprehensive SFC control and recipe management capabilities including:
    - SFC chart lifecycle management (start, stop, pause, resume, reset)
    - Recipe creation, execution, and monitoring
    - Advanced integration between SFC and recipe systems
    - Validation and error handling for industrial applications
    """

    def __init__(self, client: IgnitionGraphClient):
        """Initialize the SFC & Recipe Management system."""
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.functions_created = 0

        # Task metadata
        self.task_info = {
            "task_number": 16,
            "task_name": "SFC & Recipe Management System",
            "description": "Sequential Function Charts and Recipe Management for industrial automation",
            "function_count_target": 20,
            "categories": [
                "SFC Control Functions",
                "Recipe Management Functions",
                "Integration & Validation Functions",
            ],
        }

    def create_all_functions(self) -> dict[str, Any]:
        """Create all SFC and Recipe Management functions in the graph database."""
        try:
            self.logger.info("Starting Task 16: SFC & Recipe Management System implementation")

            # Create function categories
            sfc_functions = self._create_sfc_control_functions()
            recipe_functions = self._create_recipe_management_functions()
            integration_functions = self._create_integration_functions()

            all_functions = {
                **sfc_functions,
                **recipe_functions,
                **integration_functions,
            }

            self.logger.info(f"Task 16 completed: {len(all_functions)} functions created")
            return {
                "task_16_summary": {
                    "total_functions": len(all_functions),
                    "target_met": len(all_functions) >= self.task_info["function_count_target"],
                    "categories": {
                        "sfc_control": len(sfc_functions),
                        "recipe_management": len(recipe_functions),
                        "integration": len(integration_functions),
                    },
                },
                "functions": all_functions,
            }

        except Exception as e:
            self.logger.error(f"Error in Task 16 implementation: {e}")
            raise

    def _create_sfc_control_functions(self) -> dict[str, Any]:
        """Create Sequential Function Chart control functions."""
        sfc_functions = {}

        # 1. SFC Start Function
        sfc_functions["sfc_start"] = self._create_function(
            name="sfc.start",
            description="Start execution of a Sequential Function Chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart to start", True),
                self._create_parameter(
                    "initial_variables",
                    "dict",
                    "Initial variable values for the chart",
                    False,
                    {},
                ),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Start an SFC chart with initial variables
success = sfc.start("Plant/Line1/MainSequence", {
    "batch_id": "BATCH_001",
    "target_temperature": 75.0,
    "recipe_name": "StandardMix"
})

if success:
    system.gui.messageBox("SFC chart started successfully")
else:
    system.gui.errorBox("Failed to start SFC chart", "SFC Error")
""",
            additional_info={
                "use_cases": [
                    "Start automated production sequences",
                    "Initiate batch processing operations",
                    "Begin recipe execution workflows",
                    "Launch emergency shutdown procedures",
                ],
                "best_practices": [
                    "Validate chart path before starting",
                    "Check for conflicting chart executions",
                    "set appropriate initial variables",
                    "Monitor start operation status",
                ],
            },
        )

        # 2. SFC Stop Function
        sfc_functions["sfc_stop"] = self._create_function(
            name="sfc.stop",
            description="Stop execution of a Sequential Function Chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart to stop", True),
                self._create_parameter(
                    "force_stop",
                    "bool",
                    "Force immediate stop without cleanup",
                    False,
                    False,
                ),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Stop an SFC chart gracefully
success = sfc.stop("Plant/Line1/MainSequence", force_stop=False)

if success:
    # Log the stop operation
    logger = system.util.getLogger("SFC")
    logger.info("SFC chart stopped successfully")

    # Update status display
    system.tag.writeBlocking(["[default]SFC/Status"], ["Stopped"])
else:
    system.gui.warningBox("Failed to stop SFC chart", "SFC Warning")
""",
            additional_info={
                "use_cases": [
                    "Graceful shutdown of production sequences",
                    "Emergency stop procedures",
                    "End of batch operations",
                    "Maintenance mode activation",
                ]
            },
        )

        # 3. SFC Pause Function
        sfc_functions["sfc_pause"] = self._create_function(
            name="sfc.pause",
            description="Pause execution of a Sequential Function Chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart to pause", True),
                self._create_parameter("safe_pause", "bool", "Pause only at safe points", False, True),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Pause SFC chart at a safe point
success = sfc.pause("Plant/Line1/MainSequence", safe_pause=True)

if success:
    # Update operator display
    system.tag.writeBlocking([
        "[default]SFC/Status",
        "[default]SFC/PauseTime"
    ], [
        "Paused",
        system.date.now()
    ])

    system.gui.messageBox("SFC chart paused safely")
""",
            additional_info={
                "use_cases": [
                    "Temporary production hold",
                    "Operator intervention required",
                    "Equipment maintenance pause",
                    "Quality inspection hold",
                ]
            },
        )

        # 4. SFC Resume Function
        sfc_functions["sfc_resume"] = self._create_function(
            name="sfc.resume",
            description="Resume execution of a paused Sequential Function Chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart to resume", True),
                self._create_parameter(
                    "verify_conditions",
                    "bool",
                    "Verify safety conditions before resume",
                    False,
                    True,
                ),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Resume SFC chart with condition verification
success = sfc.resume("Plant/Line1/MainSequence", verify_conditions=True)

if success:
    # Log resume operation
    logger = system.util.getLogger("SFC")
    logger.info("SFC chart resumed from pause")

    # Clear pause indicators
    system.tag.writeBlocking([
        "[default]SFC/Status",
        "[default]SFC/PauseTime"
    ], [
        "Running",
        None
    ])
else:
    system.gui.errorBox("Cannot resume - safety conditions not met", "Resume Error")
""",
            additional_info={
                "safety_considerations": [
                    "Verify equipment readiness",
                    "Check process conditions",
                    "Validate operator clearance",
                    "Confirm material availability",
                ]
            },
        )

        # 5. SFC Reset Function
        sfc_functions["sfc_reset"] = self._create_function(
            name="sfc.reset",
            description="Reset a Sequential Function Chart to its initial state",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart to reset", True),
                self._create_parameter("clear_variables", "bool", "Clear all chart variables", False, True),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Reset SFC chart for new batch
success = sfc.reset("Plant/Line1/MainSequence", clear_variables=True)

if success:
    # Initialize for new batch
    system.tag.writeBlocking([
        "[default]SFC/BatchID",
        "[default]SFC/StartTime",
        "[default]SFC/Status"
    ], [
        "",
        None,
        "Ready"
    ])

    system.gui.messageBox("SFC chart reset for new batch")
""",
            additional_info={
                "use_cases": [
                    "Prepare for new batch",
                    "Clear error conditions",
                    "Initialize after maintenance",
                    "Start fresh production cycle",
                ]
            },
        )

        # 6. SFC Get Status Function
        sfc_functions["sfc_get_status"] = self._create_function(
            name="sfc.getStatus",
            description="Get comprehensive status information for an SFC chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart", True),
                self._create_parameter(
                    "include_variables",
                    "bool",
                    "Include chart variables in status",
                    False,
                    True,
                ),
            ],
            return_type="dict",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Get detailed SFC status
status = sfc.getStatus("Plant/Line1/MainSequence", include_variables=True)

if status:
    # Display status information
    current_step = status.get("current_step", "Unknown")
    execution_time = status.get("execution_time", 0)

    # Update HMI display
    system.tag.writeBlocking([
        "[default]HMI/SFC/CurrentStep",
        "[default]HMI/SFC/ExecutionTime",
        "[default]HMI/SFC/State"
    ], [
        current_step,
        execution_time,
        status.get("state", "Unknown")
    ])

    # Log status if needed
    if status.get("state") == "error":
        logger.error(f"SFC Error: {status.get('error_message', 'Unknown error')}")
""",
            additional_info={
                "return_structure": {
                    "state": "Current execution state (idle, running, paused, error)",
                    "current_step": "Name of currently executing step",
                    "execution_id": "Unique execution identifier",
                    "start_time": "Chart start timestamp",
                    "execution_time": "Total execution time in seconds",
                    "variables": "Chart variable values (if requested)",
                    "error_message": "Error description (if in error state)",
                }
            },
        )

        # 7. SFC Get Current Step Function
        sfc_functions["sfc_get_current_step"] = self._create_function(
            name="sfc.getCurrentStep",
            description="Get the currently executing step of an SFC chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart", True),
                self._create_parameter(
                    "include_details",
                    "bool",
                    "Include step details and timing",
                    False,
                    False,
                ),
            ],
            return_type="str",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Get current step with details
current_step = sfc.getCurrentStep("Plant/Line1/MainSequence", include_details=True)

if current_step:
    # Update step display
    system.tag.writeBlocking(["[default]HMI/CurrentStep"], [current_step])

    # Trigger step-specific actions
    if current_step == "MixingStep":
        # Enable mixing controls
        system.tag.writeBlocking(["[default]Controls/MixerEnabled"], [True])
    elif current_step == "HeatingStep":
        # Enable heating controls
        system.tag.writeBlocking(["[default]Controls/HeaterEnabled"], [True])
""",
            additional_info={
                "use_cases": [
                    "HMI step display updates",
                    "Conditional logic based on step",
                    "Step-specific control enabling",
                    "Progress monitoring",
                ]
            },
        )

        # 8. SFC Get Step History Function
        sfc_functions["sfc_get_step_history"] = self._create_function(
            name="sfc.getStepHistory",
            description="Get execution history of steps for an SFC chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart", True),
                self._create_parameter("limit", "int", "Maximum number of history entries", False, 100),
                self._create_parameter(
                    "execution_id",
                    "str",
                    "Specific execution ID (optional)",
                    False,
                    None,
                ),
            ],
            return_type="list",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="SFC Control Functions",
            code_example="""
# Get step history for analysis
history = sfc.getStepHistory("Plant/Line1/MainSequence", limit=50)

if history:
    # Analyze step durations
    total_time = 0
    for step_record in history:
        step_duration = step_record.get("duration", 0)
        total_time += step_duration

        # Log long-running steps
        if step_duration > 300:  # 5 minutes
            logger.warn(f"Long step duration: {step_record['step_name']} - {step_duration}s")

    # Update batch record
    system.tag.writeBlocking(["[default]Batch/TotalTime"], [total_time])
""",
            additional_info={
                "return_structure": [
                    {
                        "step_name": "Name of the executed step",
                        "start_time": "Step start timestamp",
                        "end_time": "Step end timestamp",
                        "duration": "Step execution duration in seconds",
                        "status": "Step completion status (completed, aborted, error)",
                        "variables": "Step variable values at completion",
                    }
                ]
            },
        )

        return sfc_functions

    def _create_recipe_management_functions(self) -> dict[str, Any]:
        """Create Recipe Management functions."""
        recipe_functions = {}

        # 9. Recipe Create Function
        recipe_functions["recipe_create"] = self._create_function(
            name="recipe.create",
            description="Create a new recipe from a template or structure",
            parameters=[
                self._create_parameter("name", "str", "Name for the new recipe", True),
                self._create_parameter("template", "dict", "Recipe template or structure definition", True),
                self._create_parameter("description", "str", "Recipe description", False, ""),
                self._create_parameter("version", "str", "Recipe version", False, "1.0"),
            ],
            return_type="str",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Recipe Management Functions",
            code_example="""
# Create a new batch recipe
recipe_template = {
    "ingredients": [
        {"name": "Water", "amount": 100, "unit": "L", "tolerance": 2.0},
        {"name": "Sugar", "amount": 50, "unit": "kg", "tolerance": 0.5},
        {"name": "Flavoring", "amount": 2, "unit": "L", "tolerance": 0.1}
    ],
    "steps": [
        {
            "name": "Fill Water",
            "action": "fill",
            "ingredient": "Water",
            "target_amount": 100,
            "flow_rate": 20,
            "timeout": 300
        },
        {
            "name": "Heat to Temperature",
            "action": "heat",
            "target_temperature": 80,
            "ramp_rate": 2,
            "timeout": 900
        },
        {
            "name": "Add Sugar",
            "action": "add",
            "ingredient": "Sugar",
            "addition_rate": 5,
            "timeout": 600
        },
        {
            "name": "Mix",
            "action": "mix",
            "speed": 200,
            "duration": 1800,
            "timeout": 2000
        }
    ],
    "quality_parameters": {
        "final_temperature": {"min": 75, "max": 85},
        "mixing_time": {"min": 1500, "max": 2000},
        "density": {"min": 1.05, "max": 1.15}
    }
}

recipe_id = recipe.create(
    name="StandardBatch_v2",
    template=recipe_template,
    description="Standard batch recipe with improved mixing",
    version="2.0"
)

if recipe_id:
    system.gui.messageBox(f"Recipe created successfully: {recipe_id}")
    # Store recipe ID for future reference
    system.tag.writeBlocking(["[default]Production/LastRecipeID"], [recipe_id])
""",
            additional_info={
                "template_structure": {
                    "ingredients": "list of recipe ingredients with amounts and tolerances",
                    "steps": "Sequential recipe steps with parameters",
                    "quality_parameters": "Quality control parameters and limits",
                    "equipment_requirements": "Required equipment specifications",
                    "safety_parameters": "Safety limits and interlocks",
                }
            },
        )

        # 10. Recipe Load Function
        recipe_functions["recipe_load"] = self._create_function(
            name="recipe.load",
            description="Load an existing recipe for execution or editing",
            parameters=[
                self._create_parameter("recipe_name", "str", "Name of the recipe to load", True),
                self._create_parameter("version", "str", "Specific recipe version to load", False, "latest"),
            ],
            return_type="dict",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Recipe Management Functions",
            code_example="""
# Load recipe for production
recipe_data = recipe.load("StandardBatch_v2", version="latest")

if recipe_data:
    # Validate recipe completeness
    required_fields = ["ingredients", "steps", "quality_parameters"]
    missing_fields = [field for field in required_fields if field not in recipe_data]

    if not missing_fields:
        # Recipe is complete - prepare for execution
        batch_id = f"BATCH_{system.date.format(system.date.now(), 'yyyyMMdd_HHmmss')}"

        # Store recipe data for execution
        system.tag.writeBlocking([
            "[default]Production/LoadedRecipe",
            "[default]Production/BatchID",
            "[default]Production/RecipeVersion"
        ], [
            recipe_data["name"],
            batch_id,
            recipe_data["version"]
        ])

        system.gui.messageBox(f"Recipe loaded for batch: {batch_id}")
    else:
        system.gui.errorBox(f"Recipe incomplete - missing: {missing_fields}", "Recipe Error")
else:
    system.gui.errorBox("Failed to load recipe", "Load Error")
""",
            additional_info={
                "return_fields": [
                    "name: Recipe name",
                    "version: Recipe version",
                    "description: Recipe description",
                    "created_date: Creation timestamp",
                    "modified_date: Last modification timestamp",
                    "ingredients: Recipe ingredients list",
                    "steps: Recipe execution steps",
                    "quality_parameters: Quality control parameters",
                ]
            },
        )

        # Continue with more recipe functions...
        # 11. Recipe Save Function
        recipe_functions["recipe_save"] = self._create_function(
            name="recipe.save",
            description="Save recipe data to the recipe database",
            parameters=[
                self._create_parameter("recipe_name", "str", "Name of the recipe to save", True),
                self._create_parameter("recipe_data", "dict", "Complete recipe data structure", True),
                self._create_parameter(
                    "overwrite",
                    "bool",
                    "Allow overwriting existing recipe",
                    False,
                    False,
                ),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Recipe Management Functions",
            code_example="""
# Save modified recipe
modified_recipe = {
    "name": "StandardBatch_v3",
    "version": "3.0",
    "description": "Optimized batch recipe",
    "ingredients": [
        {"name": "Water", "amount": 95, "unit": "L", "tolerance": 1.5},
        {"name": "Sugar", "amount": 52, "unit": "kg", "tolerance": 0.3}
    ],
    "steps": [
        {"name": "Fill Water", "action": "fill", "target_amount": 95},
        {"name": "Heat", "action": "heat", "target_temperature": 82}
    ]
}

success = recipe.save("StandardBatch_v3", modified_recipe, overwrite=True)

if success:
    # Update recipe management display
    system.tag.writeBlocking([
        "[default]RecipeManager/LastSaved",
        "[default]RecipeManager/SaveTime"
    ], [
        "StandardBatch_v3",
        system.date.now()
    ])

    system.gui.messageBox("Recipe saved successfully")
else:
    system.gui.errorBox("Failed to save recipe", "Save Error")
""",
            additional_info={
                "validation_checks": [
                    "Recipe name uniqueness",
                    "Data structure completeness",
                    "Parameter value ranges",
                    "Step sequence validity",
                ]
            },
        )

        # 12. Recipe Execute Function
        recipe_functions["recipe_execute"] = self._create_function(
            name="recipe.execute",
            description="Execute a recipe on specified equipment",
            parameters=[
                self._create_parameter("recipe_name", "str", "Name of the recipe to execute", True),
                self._create_parameter("equipment_id", "str", "Target equipment identifier", True),
                self._create_parameter("batch_id", "str", "Batch identifier for tracking", False, ""),
                self._create_parameter(
                    "execution_parameters",
                    "dict",
                    "Runtime execution parameters",
                    False,
                    {},
                ),
            ],
            return_type="str",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Recipe Management Functions",
            code_example="""
# Execute recipe on production equipment
execution_id = recipe.execute(
    recipe_name="StandardBatch_v2",
    equipment_id="BatchReactor_001",
    batch_id="BATCH_20250128_001",
    execution_parameters={
        "operator_id": "OP001",
        "priority": "high",
        "quality_check": True
    }
)

if execution_id:
    # Recipe execution started successfully
    system.tag.writeBlocking([
        "[default]Production/ActiveExecutionID",
        "[default]Production/ExecutionStartTime",
        "[default]Production/OperatorID"
    ], [
        execution_id,
        system.date.now(),
        "OP001"
    ])

    # Show execution status to operator
    system.gui.messageBox(f"Recipe execution started\\nExecution ID: {execution_id}", "Recipe Execution")

    # Log execution start
    logger = system.util.getLogger("Recipe")
    logger.info(f"Recipe execution started: {execution_id}")
else:
    system.gui.errorBox("Failed to start recipe execution", "Execution Error")
""",
            additional_info={
                "return_value": "Unique execution ID for tracking",
                "execution_phases": [
                    "Preparation: Equipment readiness check",
                    "Execution: Step-by-step recipe execution",
                    "Monitoring: Real-time progress tracking",
                    "Completion: Final quality checks and cleanup",
                ],
            },
        )

        # 13. Recipe Abort Function
        recipe_functions["recipe_abort"] = self._create_function(
            name="recipe.abort",
            description="Abort a running recipe execution",
            parameters=[
                self._create_parameter("execution_id", "str", "Execution ID to abort", True),
                self._create_parameter(
                    "abort_reason",
                    "str",
                    "Reason for aborting execution",
                    False,
                    "User requested",
                ),
                self._create_parameter("safe_abort", "bool", "Perform safe abort with cleanup", False, True),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Recipe Management Functions",
            code_example="""
# Abort recipe execution safely
execution_id = system.tag.readBlocking("[default]Production/ActiveExecutionID")[0].value

if execution_id:
    success = recipe.abort(
        execution_id=execution_id,
        abort_reason="Equipment malfunction detected",
        safe_abort=True
    )

    if success:
        # Update status displays
        system.tag.writeBlocking([
            "[default]Production/ExecutionStatus",
            "[default]Production/AbortTime",
            "[default]Production/AbortReason"
        ], [
            "ABORTED",
            system.date.now(),
            "Equipment malfunction detected"
        ])

        system.gui.messageBox("Recipe execution aborted safely", "Execution Aborted")

        # Log abort operation
        logger = system.util.getLogger("Recipe")
        logger.warning(f"Recipe execution aborted: {execution_id}")
    else:
        system.gui.errorBox("Failed to abort recipe execution", "Abort Error")
else:
    system.gui.warningBox("No active execution to abort", "No Active Execution")
""",
            additional_info={
                "abort_types": [
                    "Safe abort: Completes current step then stops",
                    "Immediate abort: Stops execution immediately",
                    "Emergency abort: Immediate stop with safety actions",
                ]
            },
        )

        # 14. Recipe Get Status Function
        recipe_functions["recipe_get_status"] = self._create_function(
            name="recipe.getStatus",
            description="Get execution status of a running recipe",
            parameters=[
                self._create_parameter("execution_id", "str", "Execution ID to check", True),
                self._create_parameter(
                    "include_details",
                    "bool",
                    "Include detailed execution information",
                    False,
                    False,
                ),
            ],
            return_type="dict",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Recipe Management Functions",
            code_example="""
# Get detailed execution status
execution_id = system.tag.readBlocking("[default]Production/ActiveExecutionID")[0].value

if execution_id:
    status = recipe.getStatus(execution_id, include_details=True)

    if status:
        # Update operator displays
        system.tag.writeBlocking([
            "[default]Operator/ExecutionProgress",
            "[default]Operator/CurrentStep",
            "[default]Operator/EstimatedCompletion",
            "[default]Operator/ExecutionStatus"
        ], [
            status.get("progress_percent", 0),
            status.get("current_step", "Unknown"),
            status.get("estimated_completion", None),
            status.get("status", "Unknown")
        ])

        # Show status popup if requested
        if status["status"] == "running":
            status_msg = f"Execution Progress: {status['progress_percent']}%\\n"
            status_msg += f"Current Step: {status['current_step']}\\n"
            status_msg += f"Estimated Completion: {status.get('estimated_completion', 'N/A')}"
            system.gui.messageBox(status_msg, "Recipe Status")
        elif status["status"] == "error":
            system.gui.errorBox(f"Recipe execution error: {status.get('error_message', 'Unknown error')}", "Execution Error")
    else:
        system.gui.warningBox("Could not retrieve execution status", "Status Warning")
else:
    system.gui.warningBox("No active execution found", "No Active Execution")
""",
            additional_info={
                "status_fields": [
                    "status: Current execution status (running, completed, aborted, error)",
                    "progress_percent: Execution progress percentage",
                    "current_step: Currently executing step",
                    "start_time: Execution start timestamp",
                    "estimated_completion: Estimated completion time",
                    "error_message: Error description if status is error",
                ]
            },
        )

        # 15. Recipe Get History Function
        recipe_functions["recipe_get_history"] = self._create_function(
            name="recipe.getHistory",
            description="Get execution history for a recipe",
            parameters=[
                self._create_parameter("recipe_name", "str", "Recipe name to get history for", True),
                self._create_parameter("limit", "int", "Maximum number of history records", False, 50),
                self._create_parameter(
                    "include_details",
                    "bool",
                    "Include detailed execution data",
                    False,
                    False,
                ),
            ],
            return_type="list",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Recipe Management Functions",
            code_example="""
# Get recent execution history
history = recipe.getHistory("StandardBatch_v2", limit=10, include_details=True)

if history:
    # Display history summary
    successful_executions = [exec for exec in history if exec["status"] == "completed"]
    failed_executions = [exec for exec in history if exec["status"] in ["aborted", "error"]]

    # Update history display
    system.tag.writeBlocking([
        "[default]History/TotalExecutions",
        "[default]History/SuccessfulExecutions",
        "[default]History/FailedExecutions",
        "[default]History/SuccessRate"
    ], [
        len(history),
        len(successful_executions),
        len(failed_executions),
        (len(successful_executions) / len(history)) * 100 if history else 0
    ])

    # Show history popup
    if len(history) > 0:
        latest_execution = history[0]
        history_msg = f"Latest Execution:\\n"
        history_msg += f"Status: {latest_execution['status']}\\n"
        history_msg += f"Duration: {latest_execution.get('duration_minutes', 'N/A')} minutes\\n"
        history_msg += f"Success Rate: {(len(successful_executions) / len(history)) * 100:.1f}%"
        system.gui.messageBox(history_msg, "Recipe History")
else:
    system.gui.messageBox("No execution history found for this recipe", "No History")
""",
            additional_info={
                "history_record_structure": [
                    "execution_id: Unique execution identifier",
                    "start_time: Execution start timestamp",
                    "end_time: Execution completion timestamp",
                    "duration_minutes: Total execution duration",
                    "status: Final execution status",
                    "operator_id: Executing operator identifier",
                    "equipment_id: Equipment used for execution",
                    "batch_id: Associated batch identifier",
                ]
            },
        )

        return recipe_functions

    def _create_integration_functions(self) -> dict[str, Any]:
        """Create SFC/Recipe integration and validation functions."""
        integration_functions = {}

        # 12. SFC set Recipe Data Function
        integration_functions["sfc_set_recipe_data"] = self._create_function(
            name="sfc.setRecipeData",
            description="Bind recipe data to an SFC chart for execution",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart", True),
                self._create_parameter("recipe_data", "dict", "Recipe data to bind to the chart", True),
                self._create_parameter(
                    "validate_compatibility",
                    "bool",
                    "Validate recipe compatibility with chart",
                    False,
                    True,
                ),
            ],
            return_type="bool",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Integration & Validation Functions",
            code_example="""
# Bind recipe to SFC chart for batch execution
recipe_data = {
    "recipe_id": "BATCH_STD_001",
    "ingredients": [
        {"name": "Water", "amount": 100, "unit": "L"},
        {"name": "Sugar", "amount": 50, "unit": "kg"}
    ],
    "parameters": {
        "mix_speed": 200,
        "target_temp": 80,
        "batch_size": 1000
    }
}

success = sfc.setRecipeData("Plant/BatchReactor/MainSequence", recipe_data, validate_compatibility=True)

if success:
    # Recipe bound successfully - start the SFC
    if sfc.start("Plant/BatchReactor/MainSequence"):
        system.gui.messageBox("Batch process started with recipe")

        # Log the binding
        logger = system.util.getLogger("Recipe")
        logger.info(f"Recipe {recipe_data['recipe_id']} bound to SFC chart")
    else:
        system.gui.errorBox("Failed to start SFC with recipe", "Execution Error")
else:
    system.gui.errorBox("Recipe incompatible with SFC chart", "Compatibility Error")
""",
            additional_info={
                "validation_checks": [
                    "Recipe parameter compatibility with SFC variables",
                    "Required ingredients availability",
                    "Step sequence validation",
                    "Equipment capability verification",
                ]
            },
        )

        # 13. SFC Get Recipe Data Function
        integration_functions["sfc_get_recipe_data"] = self._create_function(
            name="sfc.getRecipeData",
            description="Retrieve recipe data currently bound to an SFC chart",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart", True),
                self._create_parameter(
                    "include_runtime_data",
                    "bool",
                    "Include runtime execution data",
                    False,
                    False,
                ),
            ],
            return_type="dict",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Integration & Validation Functions",
            code_example="""
# Get current recipe data from running SFC
recipe_data = sfc.getRecipeData("Plant/BatchReactor/MainSequence", include_runtime_data=True)

if recipe_data:
    # Display recipe information to operator
    recipe_name = recipe_data.get("recipe_id", "Unknown")
    batch_progress = recipe_data.get("runtime_data", {}).get("progress_percent", 0)

    # Update operator display
    system.tag.writeBlocking([
        "[default]Operator/CurrentRecipe",
        "[default]Operator/BatchProgress",
        "[default]Operator/EstimatedCompletion"
    ], [
        recipe_name,
        batch_progress,
        recipe_data.get("runtime_data", {}).get("estimated_completion", None)
    ])

    # Show detailed recipe info in popup
    recipe_details = f"Recipe: {recipe_name}\\nProgress: {batch_progress}%"
    system.gui.messageBox(recipe_details, "Current Recipe Status")
else:
    system.gui.warningBox("No recipe data found for SFC chart", "Recipe Warning")
""",
            additional_info={
                "return_structure": {
                    "recipe_id": "Recipe identifier",
                    "ingredients": "Recipe ingredients list",
                    "parameters": "Recipe parameters and setpoints",
                    "runtime_data": "Execution progress and timing (if requested)",
                }
            },
        )

        # 14. Recipe Structure Validation Function
        integration_functions["recipe_validate_structure"] = self._create_function(
            name="recipe.validateStructure",
            description="Validate recipe data structure and parameters",
            parameters=[
                self._create_parameter("recipe_data", "dict", "Recipe data to validate", True),
                self._create_parameter(
                    "validation_level",
                    "str",
                    "Validation strictness level",
                    False,
                    "standard",
                ),
                self._create_parameter(
                    "equipment_context",
                    "str",
                    "Equipment context for validation",
                    False,
                    "",
                ),
            ],
            return_type="dict",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Integration & Validation Functions",
            code_example="""
# Validate recipe before execution
recipe_to_validate = {
    "name": "TestBatch",
    "ingredients": [
        {"name": "Water", "amount": 100, "unit": "L", "tolerance": 2.0},
        {"name": "Sugar", "amount": 50, "unit": "kg", "tolerance": 0.5}
    ],
    "steps": [
        {"name": "Fill", "action": "fill", "ingredient": "Water", "rate": 20},
        {"name": "Heat", "action": "heat", "target_temp": 80, "ramp_rate": 2}
    ]
}

validation_result = recipe.validateStructure(
    recipe_to_validate,
    validation_level="strict",
    equipment_context="BatchReactor_001"
)

if validation_result["valid"]:
    system.gui.messageBox("Recipe validation passed", "Validation Success")

    # Proceed with recipe execution
    execution_id = recipe.execute("TestBatch", "BatchReactor_001")
else:
    # Show validation errors
    errors = "\\n".join(validation_result["errors"])
    warnings = "\\n".join(validation_result["warnings"])

    error_msg = f"Validation failed:\\n{errors}"
    if warnings:
        error_msg += f"\\n\\nWarnings:\\n{warnings}"

    system.gui.errorBox(error_msg, "Recipe Validation Failed")
""",
            additional_info={
                "validation_levels": {
                    "basic": "Check required fields and data types",
                    "standard": "Include parameter range validation",
                    "strict": "Full validation including equipment compatibility",
                },
                "return_fields": [
                    "valid: Boolean validation result",
                    "errors: list of validation errors",
                    "warnings: list of validation warnings",
                    "recommendations: Suggested improvements",
                ],
            },
        )

        # 15. Recipe Comparison Function
        integration_functions["recipe_compare"] = self._create_function(
            name="recipe.compare",
            description="Compare two recipes and highlight differences",
            parameters=[
                self._create_parameter("recipe1", "dict", "First recipe to compare", True),
                self._create_parameter("recipe2", "dict", "Second recipe to compare", True),
                self._create_parameter(
                    "comparison_depth",
                    "str",
                    "Depth of comparison analysis",
                    False,
                    "deep",
                ),
            ],
            return_type="dict",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Integration & Validation Functions",
            code_example="""
# Compare current recipe with previous version
current_recipe = recipe.load("StandardBatch", version="2.0")
previous_recipe = recipe.load("StandardBatch", version="1.0")

comparison = recipe.compare(current_recipe, previous_recipe, comparison_depth="deep")

if comparison["identical"]:
    system.gui.messageBox("Recipes are identical", "Comparison Result")
else:
    # Show differences to operator
    differences = comparison["differences"]
    changes_summary = f"Found {len(differences)} differences:\\n"

    for diff in differences[:5]:  # Show first 5 differences
        changes_summary += f"- {diff['field']}: {diff['change_type']}\\n"

    if len(differences) > 5:
        changes_summary += f"... and {len(differences) - 5} more differences"

    system.gui.messageBox(changes_summary, "Recipe Differences")

    # Log detailed comparison for audit trail
    logger = system.util.getLogger("Recipe")
    logger.info(f"Recipe comparison: {comparison['summary']}")
""",
            additional_info={
                "comparison_types": [
                    "ingredient_changes: Changes in ingredients or amounts",
                    "step_modifications: Changes in process steps",
                    "parameter_updates: Changes in process parameters",
                    "structural_changes: Changes in recipe structure",
                ]
            },
        )

        # 16. SFC Chart Validation Function
        integration_functions["sfc_validate_chart"] = self._create_function(
            name="sfc.validateChart",
            description="Validate SFC chart structure and configuration",
            parameters=[
                self._create_parameter("chart_path", "str", "Path to the SFC chart to validate", True),
                self._create_parameter(
                    "validation_type",
                    "str",
                    "Type of validation to perform",
                    False,
                    "full",
                ),
                self._create_parameter(
                    "check_dependencies",
                    "bool",
                    "Check for missing dependencies",
                    False,
                    True,
                ),
            ],
            return_type="dict",
            context=["Gateway", "Vision Client", "Perspective Session"],
            category="Integration & Validation Functions",
            code_example="""
# Validate SFC chart before deployment
validation_result = sfc.validateChart(
    "Plant/BatchReactor/MainSequence",
    validation_type="full",
    check_dependencies=True
)

if validation_result["valid"]:
    system.gui.messageBox("SFC chart validation passed", "Validation Success")

    # Chart is ready for production use
    system.tag.writeBlocking([
        "[default]SFC/ValidationStatus",
        "[default]SFC/LastValidated"
    ], [
        "PASSED",
        system.date.now()
    ])
else:
    # Show validation issues
    issues = validation_result["issues"]
    critical_issues = [issue for issue in issues if issue["severity"] == "critical"]

    if critical_issues:
        error_msg = "Critical validation failures:\\n"
        for issue in critical_issues:
            error_msg += f"- {issue['description']}\\n"
        system.gui.errorBox(error_msg, "Critical SFC Issues")
    else:
        # Only warnings - show but allow execution
        warning_msg = "SFC validation warnings:\\n"
        for issue in issues:
            warning_msg += f"- {issue['description']}\\n"
        system.gui.warningBox(warning_msg, "SFC Warnings")
""",
            additional_info={
                "validation_checks": [
                    "Step sequence integrity",
                    "Transition logic validation",
                    "Variable scope verification",
                    "Resource dependency checking",
                    "Safety interlock validation",
                ]
            },
        )

        return integration_functions

    def _create_function(
        self,
        name: str,
        description: str,
        parameters: list[dict[str, Any]],
        return_type: str,
        context: list[str],
        category: str,
        code_example: str = "",
        additional_info: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a function node in the graph database."""
        try:
            # Create function using Cypher query
            query = """
            MERGE (f:Function {name: $name})
            SET f.description = $description,
                f.return_type = $return_type,
                f.category = $category,
                f.code_example = $code_example,
                f.ignition_version = $ignition_version,
                f.complexity = $complexity,
                f.task = 'Task 16: SFC & Recipe Management'

            // Create parameter relationships
            WITH f
            UNWIND $parameters AS param
            MERGE (p:Parameter {name: param.name + "_" + $name})
            SET p.parameter_name = param.name,
                p.function_name = $name,
                p.type = param.type,
                p.description = param.description,
                p.required = param.required,
                p.default_value = coalesce(param.default_value, "")
            MERGE (f)-[:HAS_PARAMETER]->(p)

            // Create scope relationships
            WITH f
            UNWIND $context AS scope_name
            MERGE (s:Scope {name: scope_name})
            MERGE (f)-[:AVAILABLE_IN]->(s)

            RETURN f.name as function_name
            """

            params = {
                "name": name,
                "description": description,
                "return_type": return_type,
                "category": category,
                "code_example": code_example.strip(),
                "ignition_version": "8.1+",
                "complexity": "medium",
                "parameters": parameters,
                "context": context,
            }

            result = self.client.execute_query(query, params)
            self.functions_created += 1

            self.logger.info(f"Created function: {name} in category: {category}")
            return {"name": name, "category": category, "result": result}

        except Exception as e:
            self.logger.error(f"Error creating function {name}: {e}")
            raise

    def _create_parameter(
        self,
        name: str,
        param_type: str,
        description: str,
        required: bool = True,
        default_value: Any = None,
    ) -> dict[str, Any]:
        """Create a parameter definition."""
        return {
            "name": name,
            "type": param_type,
            "description": description,
            "required": required,
            "default_value": default_value,
        }


def create_task_16_functions(client: IgnitionGraphClient) -> dict[str, Any]:
    """Main entry point for creating Task 16 SFC & Recipe Management functions.

    Args:
        client: Connected IgnitionGraphClient instance

    Returns:
        Dictionary containing creation results and statistics
    """
    task_16 = Task16SFCRecipeSystem(client)
    return task_16.create_all_functions()


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)

    # Note: This would require a connected client in actual usage
    print("Task 16: SFC & Recipe Management System")
    print("This module provides Sequential Function Chart and Recipe Management capabilities")
    print("for industrial automation systems in Ignition.")
    print("\nFunctions include:")
    print("- SFC chart control (start, stop, pause, resume, reset)")
    print("- Recipe management (create, load, save, execute)")
    print("- Integration and validation functions")
    print("- Comprehensive error handling and logging")
