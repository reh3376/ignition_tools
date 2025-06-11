"""Recipe Management Module

This module provides recipe management functionality for Ignition systems including
recipe creation, execution, monitoring, and validation.
"""

from .execution_engine import RecipeExecutionEngine
from .recipe_manager import RecipeManager
from .template_system import RecipeTemplateSystem

__all__ = ["RecipeManager", "RecipeExecutionEngine", "RecipeTemplateSystem"]
