"""Recipe Manager.

Handles recipe creation, loading, saving, and management operations for industrial automation.
Provides comprehensive recipe lifecycle management with validation and versioning.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class RecipeManager:
    """Recipe Manager for industrial automation systems.

    Manages recipe lifecycle including creation, loading, saving, execution,
    and history tracking for batch processing and automated manufacturing.
    """

    def __init__(self) -> None:
        """Initialize the Recipe Manager."""
        self.logger = logging.getLogger(__name__)
        self.recipes: dict[str, dict[str, Any]] = {}
        self.active_executions: dict[str, dict[str, Any]] = {}

    def create_recipe(
        self,
        name: str,
        template: dict[str, Any],
        description: str = "",
        version: str = "1.0",
    ) -> str:
        """Create a new recipe from a template.

        Args:
            name: Recipe name
            template: Recipe template structure
            description: Recipe description
            version: Recipe version

        Returns:
            str: Recipe ID if successful, empty string if failed
        """
        try:
            self.logger.info(f"Creating recipe: {name} v{version}")

            # Validate template
            if not self._validate_recipe_template(template):
                self.logger.error(f"Invalid recipe template for {name}")
                return ""

            # Generate recipe ID
            recipe_id = f"{name}_{version}_{uuid.uuid4().hex[:8]}"

            # Create recipe data
            recipe_data = {
                "recipe_id": recipe_id,
                "name": name,
                "version": version,
                "description": description,
                "created_date": datetime.now(),
                "modified_date": datetime.now(),
                "template": template,
                "ingredients": template.get("ingredients", []),
                "steps": template.get("steps", []),
                "quality_parameters": template.get("quality_parameters", {}),
                "equipment_requirements": template.get("equipment_requirements", {}),
                "safety_parameters": template.get("safety_parameters", {}),
            }

            # Store recipe
            self.recipes[recipe_id] = recipe_data

            self.logger.info(f"Recipe created successfully: {recipe_id}")
            return recipe_id

        except Exception as e:
            self.logger.error(f"Error creating recipe {name}: {e}")
            return ""

    def load_recipe(
        self, recipe_name: str, version: str = "latest"
    ) -> dict[str, Any] | None:
        """Load an existing recipe.

        Args:
            recipe_name: Name of the recipe to load
            version: Specific recipe version to load

        Returns:
            dict containing recipe data or None if not found
        """
        try:
            self.logger.info(f"Loading recipe: {recipe_name} v{version}")

            # Find recipe by name and version
            matching_recipes = []
            for recipe_id, recipe_data in self.recipes.items():
                if recipe_data["name"] == recipe_name:
                    if version == "latest" or recipe_data["version"] == version:
                        matching_recipes.append((recipe_id, recipe_data))

            if not matching_recipes:
                self.logger.warning(f"Recipe not found: {recipe_name} v{version}")
                return None

            # Get latest version if requested
            if version == "latest":
                # Sort by creation date and get most recent
                matching_recipes.sort(key=lambda x: x[1]["created_date"], reverse=True)

            recipe_data = matching_recipes[0][1].copy()

            self.logger.info(f"Recipe loaded: {recipe_data['recipe_id']}")
            return recipe_data

        except Exception as e:
            self.logger.error(f"Error loading recipe {recipe_name}: {e}")
            return None

    def save_recipe(
        self, recipe_name: str, recipe_data: dict[str, Any], overwrite: bool = False
    ) -> bool:
        """Save recipe data to the recipe database.

        Args:
            recipe_name: Name of the recipe to save
            recipe_data: Complete recipe data structure
            overwrite: Allow overwriting existing recipe

        Returns:
            bool: True if saved successfully
        """
        try:
            self.logger.info(f"Saving recipe: {recipe_name}")

            # Validate recipe data
            if not self._validate_recipe_data(recipe_data):
                self.logger.error(f"Invalid recipe data for {recipe_name}")
                return False

            # Check for existing recipe
            existing_recipe = self._find_recipe_by_name(recipe_name)
            if existing_recipe and not overwrite:
                self.logger.warning(
                    f"Recipe already exists and overwrite=False: {recipe_name}"
                )
                return False

            # Generate or use existing recipe ID
            if "recipe_id" not in recipe_data:
                recipe_data["recipe_id"] = f"{recipe_name}_{uuid.uuid4().hex[:8]}"

            # Update modification date
            recipe_data["modified_date"] = datetime.now()

            # Store recipe
            self.recipes[recipe_data["recipe_id"]] = recipe_data

            self.logger.info(f"Recipe saved: {recipe_data['recipe_id']}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving recipe {recipe_name}: {e}")
            return False

    def execute_recipe(
        self,
        recipe_name: str,
        equipment_id: str,
        batch_id: str = "",
        execution_parameters: dict[str, Any] | None = None,
    ) -> str:
        """Execute a recipe on specified equipment.

        Args:
            recipe_name: Name of the recipe to execute
            equipment_id: Target equipment identifier
            batch_id: Batch identifier for tracking
            execution_parameters: Runtime execution parameters

        Returns:
            str: Execution ID if successful, empty string if failed
        """
        try:
            self.logger.info(f"Executing recipe: {recipe_name} on {equipment_id}")

            # Load recipe
            recipe_data = self.load_recipe(recipe_name)
            if not recipe_data:
                self.logger.error(f"Recipe not found for execution: {recipe_name}")
                return ""

            # Generate execution ID
            execution_id = str(uuid.uuid4())

            # Generate batch ID if not provided
            if not batch_id:
                batch_id = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create execution record
            execution_data = {
                "execution_id": execution_id,
                "recipe_id": recipe_data["recipe_id"],
                "recipe_name": recipe_name,
                "equipment_id": equipment_id,
                "batch_id": batch_id,
                "status": "running",
                "start_time": datetime.now(),
                "progress_percent": 0,
                "current_step": (
                    recipe_data["steps"][0]["name"]
                    if recipe_data["steps"]
                    else "initial"
                ),
                "execution_parameters": execution_parameters or {},
                "step_history": [],
            }

            # Store execution
            self.active_executions[execution_id] = execution_data

            self.logger.info(f"Recipe execution started: {execution_id}")
            return execution_id

        except Exception as e:
            self.logger.error(f"Error executing recipe {recipe_name}: {e}")
            return ""

    def abort_execution(
        self,
        execution_id: str,
        abort_reason: str = "User requested",
        safe_abort: bool = True,
    ) -> bool:
        """Abort a running recipe execution.

        Args:
            execution_id: Execution ID to abort
            abort_reason: Reason for aborting execution
            safe_abort: Perform safe abort with cleanup

        Returns:
            bool: True if aborted successfully
        """
        try:
            self.logger.info(
                f"Aborting execution: {execution_id} (reason: {abort_reason})"
            )

            if execution_id not in self.active_executions:
                self.logger.warning(f"Execution not found: {execution_id}")
                return False

            execution_data = self.active_executions[execution_id]

            # Update execution status
            execution_data["status"] = "aborted"
            execution_data["end_time"] = datetime.now()
            execution_data["abort_reason"] = abort_reason
            execution_data["safe_abort"] = safe_abort

            # Calculate duration
            if "start_time" in execution_data:
                duration = datetime.now() - execution_data["start_time"]
                execution_data["duration_minutes"] = duration.total_seconds() / 60

            self.logger.info(f"Execution aborted: {execution_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error aborting execution {execution_id}: {e}")
            return False

    def get_execution_status(
        self, execution_id: str, include_details: bool = False
    ) -> dict[str, Any] | None:
        """Get execution status of a running recipe.

        Args:
            execution_id: Execution ID to check
            include_details: Include detailed execution information

        Returns:
            dict containing execution status or None if not found
        """
        try:
            if execution_id not in self.active_executions:
                return None

            execution_data = self.active_executions[execution_id].copy()

            # Calculate runtime if running
            if execution_data["status"] == "running" and "start_time" in execution_data:
                runtime = datetime.now() - execution_data["start_time"]
                execution_data["runtime_minutes"] = runtime.total_seconds() / 60

            # Add estimated completion time
            if execution_data["status"] == "running":
                estimated_total_time = self._estimate_total_execution_time(
                    execution_data
                )
                if estimated_total_time:
                    estimated_completion = (
                        execution_data["start_time"] + estimated_total_time
                    )
                    execution_data["estimated_completion"] = estimated_completion

            if not include_details:
                # Return basic status only
                basic_status = {
                    "execution_id": execution_data["execution_id"],
                    "status": execution_data["status"],
                    "progress_percent": execution_data["progress_percent"],
                    "current_step": execution_data["current_step"],
                }
                return basic_status

            return execution_data

        except Exception as e:
            self.logger.error(f"Error getting execution status {execution_id}: {e}")
            return None

    def get_execution_history(
        self, recipe_name: str, limit: int = 50, include_details: bool = False
    ) -> list[dict[str, Any]]:
        """Get execution history for a recipe.

        Args:
            recipe_name: Recipe name to get history for
            limit: Maximum number of history records
            include_details: Include detailed execution data

        Returns:
            list of execution history records
        """
        try:
            history = []

            # Find executions for this recipe
            for _execution_id, execution_data in self.active_executions.items():
                if execution_data["recipe_name"] == recipe_name:
                    if include_details:
                        history.append(execution_data.copy())
                    else:
                        # Basic history record
                        basic_record = {
                            "execution_id": execution_data["execution_id"],
                            "start_time": execution_data["start_time"],
                            "end_time": execution_data.get("end_time"),
                            "duration_minutes": execution_data.get("duration_minutes"),
                            "status": execution_data["status"],
                            "operator_id": execution_data.get(
                                "execution_parameters", {}
                            ).get("operator_id"),
                            "equipment_id": execution_data["equipment_id"],
                            "batch_id": execution_data["batch_id"],
                        }
                        history.append(basic_record)

            # Sort by start time (most recent first)
            history.sort(key=lambda x: x["start_time"], reverse=True)

            # Apply limit
            return history[:limit]

        except Exception as e:
            self.logger.error(f"Error getting execution history for {recipe_name}: {e}")
            return []

    def _validate_recipe_template(self, template: dict[str, Any]) -> bool:
        """Validate recipe template structure."""
        required_fields = ["ingredients", "steps"]
        return all(field in template for field in required_fields)

    def _validate_recipe_data(self, recipe_data: dict[str, Any]) -> bool:
        """Validate recipe data structure."""
        required_fields = ["name", "version", "ingredients", "steps"]
        return all(field in recipe_data for field in required_fields)

    def _find_recipe_by_name(self, recipe_name: str) -> dict[str, Any] | None:
        """Find recipe by name."""
        for recipe_data in self.recipes.values():
            if recipe_data["name"] == recipe_name:
                return recipe_data
        return None

    def _estimate_total_execution_time(
        self, execution_data: dict[str, Any]
    ) -> datetime | None:
        """Estimate total execution time based on recipe steps."""
        # Placeholder implementation - would use step timing data
        # to estimate total execution time
        return None
