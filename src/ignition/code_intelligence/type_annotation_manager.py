"""
Type Annotation Management System for IGN Scripts

Following crawl_mcp.py methodology:
1. Environment validation first
2. Input validation and sanitization
3. Comprehensive error handling
4. Modular testing integration
5. Progressive complexity
6. Resource management
"""

import ast
import logging
import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field, field_validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type definitions
ValidationResult = Dict[str, Any]
F = TypeVar('F', bound=Callable[..., Any])


class TypeAnnotationConfig(BaseModel):
    """Configuration for type annotation management."""

    auto_fix_enabled: bool = Field(default=True, description="Enable automatic type annotation fixes")
    strict_mode: bool = Field(default=False, description="Enable strict type checking mode")
    validation_enabled: bool = Field(default=True, description="Enable validation result type checking")
    pydantic_validator_fix: bool = Field(default=True, description="Fix Pydantic validator decorators")
    neo4j_type_fix: bool = Field(default=True, description="Fix Neo4j type annotations")
    excluded_files: List[str] = Field(default_factory=list, description="Files to exclude from processing")

    @field_validator("excluded_files")
    @classmethod
    def validate_excluded_files(cls, v: List[str]) -> List[str]:
        """Validate excluded files list."""
        return [str(Path(f).resolve()) for f in v]


class ValidationResultType:
    """Helper for creating properly typed validation results."""

    @staticmethod
    def create_validation_result(
        valid: bool = True,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        components: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> ValidationResult:
        """Create a properly typed validation result."""
        return {
            "valid": valid,
            "errors": errors or [],
            "warnings": warnings or [],
            "components": components or {},
            **kwargs
        }

    @staticmethod
    def is_validation_result(obj: Any) -> bool:
        """Check if object is a validation result."""
        if not isinstance(obj, dict):
            return False
        required_keys = {"valid", "errors", "warnings", "components"}
        return required_keys.issubset(obj.keys())


class PydanticValidatorFix:
    """Helper for fixing Pydantic validator type annotations."""

    @staticmethod
    def typed_field_validator(field_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Create properly typed field validator decorator."""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Preserve original function with proper typing
            @field_validator(field_name)
            @wraps(func)
            def wrapper(cls: Type[BaseModel], v: Any) -> Any:
                return func(cls, v)
            return wrapper
        return decorator

    @staticmethod
    def fix_validator_function(func: Callable[..., Any]) -> Callable[..., Any]:
        """Fix validator function type annotations."""
        if hasattr(func, '__annotations__'):
            # Update annotations for proper typing
            func.__annotations__.update({
                'cls': Type[BaseModel],
                'v': Any,
                'return': Any
            })
            
            @wraps(func)
            def typed_validator(cls: Type[BaseModel], v: Any) -> Any:
                return func(cls, v)
            return typed_validator
        return func


class Neo4jTypeFix:
    """Helper for fixing Neo4j type annotations."""

    @staticmethod
    def get_neo4j_driver_type() -> str:
        """Get proper Neo4j driver type annotation."""
        try:
            import neo4j
            return f"neo4j.Driver"
        except ImportError:
            return "Any"

    @staticmethod
    def get_neo4j_session_type() -> str:
        """Get proper Neo4j session type annotation."""
        try:
            import neo4j
            return f"neo4j.Session"
        except ImportError:
            return "Any"


class OptionalTypeHandler:
    """Helper for handling optional types safely."""

    @staticmethod
    def safe_attribute_access(obj: Optional[Any], attr: str, default: Any = None) -> Any:
        """Safely access attribute on potentially None object."""
        if obj is None:
            return default
        return getattr(obj, attr, default)

    @staticmethod
    def safe_dict_access(obj: Optional[Dict[str, Any]], key: str, default: Any = None) -> Any:
        """Safely access dictionary key on potentially None dict."""
        if obj is None:
            return default
        return obj.get(key, default)

    @staticmethod
    def ensure_not_none(obj: Optional[Any], error_msg: str = "Object cannot be None") -> Any:
        """Ensure object is not None."""
        if obj is None:
            raise ValueError(error_msg)
        return obj


class TypeAnnotationAnalyzer:
    """Analyzer for type annotation issues in Python files."""

    def __init__(self, config: Optional[TypeAnnotationConfig] = None):
        self.config = config or TypeAnnotationConfig()
        logger.info("🔍 TypeAnnotationAnalyzer initialized")

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for type annotation issues."""
        logger.info(f"📄 Analyzing file: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            issues = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_issue = self._analyze_function(node)
                    if func_issue:
                        issues.append(func_issue)
                elif isinstance(node, ast.ClassDef):
                    class_issues = self._analyze_class(node)
                    issues.extend(class_issues)

            return {
                "file": str(file_path),
                "total_issues": sum(len(issue.get("issues", [])) for issue in issues),
                "fixable": sum(len([i for i in issue.get("issues", []) if i.get("fixable")]) for issue in issues),
                "issues": issues
            }

        except Exception as e:
            logger.error(f"❌ Error analyzing file {file_path}: {e}")
            return {
                "file": str(file_path),
                "error": str(e),
                "total_issues": 0,
                "fixable": 0,
                "issues": []
            }

    def _analyze_function(self, node: ast.FunctionDef) -> Optional[Dict[str, Any]]:
        """Analyze a function for type annotation issues."""
        issues = []

        # Check return type annotation
        if node.returns is None:
            issues.append({
                "type": "missing_return_annotation",
                "line": node.lineno,
                "function": node.name,
                "fixable": True,
                "suggestion": "Add return type annotation"
            })

        # Check parameter annotations
        for arg in node.args.args:
            if arg.annotation is None:
                issues.append({
                    "type": "missing_parameter_annotation",
                    "line": node.lineno,
                    "function": node.name,
                    "parameter": arg.arg,
                    "fixable": True,
                    "suggestion": f"Add type annotation for parameter '{arg.arg}'"
                })

        # Check for Pydantic validator patterns
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == 'field_validator':
                    issues.append({
                        "type": "pydantic_validator_typing",
                        "line": node.lineno,
                        "function": node.name,
                        "fixable": True,
                        "suggestion": "Fix Pydantic validator type annotations"
                    })

        return {
            "function": node.name,
            "line": node.lineno,
            "issues": issues
        } if issues else None

    def _analyze_class(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Analyze a class for type annotation issues."""
        issues = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                func_issue = self._analyze_function(item)
                if func_issue:
                    func_issue["class"] = node.name
                    issues.append(func_issue)

        return issues

    def generate_fixes(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate fix suggestions for type annotation issues."""
        fixes = []

        for issue_group in analysis_result.get("issues", []):
            for issue in issue_group.get("issues", []):
                if issue.get("fixable"):
                    fix = self._generate_fix_for_issue(issue, issue_group)
                    if fix:
                        fixes.append(fix)

        return fixes

    def _generate_fix_for_issue(self, issue: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """Generate a specific fix for an issue."""
        issue_type = issue.get("type")

        if issue_type == "missing_return_annotation":
            return f"Add '-> None' or appropriate return type to {context.get('function')}()"

        elif issue_type == "missing_parameter_annotation":
            param = issue.get("parameter")
            return f"Add type annotation for parameter '{param}' in {context.get('function')}()"

        elif issue_type == "pydantic_validator_typing":
            return f"Fix Pydantic validator in {context.get('function')}() using TypeAnnotationManager.pydantic_helper"

        return None


class TypeAnnotationManager:
    """Main manager for type annotation operations."""

    def __init__(self, config: Optional[TypeAnnotationConfig] = None):
        self.config = config or TypeAnnotationConfig()
        self.analyzer = TypeAnnotationAnalyzer(self.config)
        self.validation_helper = ValidationResultType()
        self.pydantic_helper = PydanticValidatorFix()
        self.neo4j_helper = Neo4jTypeFix()
        self.optional_helper = OptionalTypeHandler()

    def validate_environment(self) -> ValidationResult:
        """Validate environment for type annotation management."""
        logger.info("🔍 Validating type annotation environment...")

        try:
            # Check required packages
            required_packages = ["ast", "inspect", "typing", "pydantic"]
            missing_packages = []

            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)

            if missing_packages:
                return self.validation_helper.create_validation_result(
                    valid=False,
                    errors=[f"Missing required packages: {', '.join(missing_packages)}"]
                )

            # Check Python version compatibility
            import sys
            if sys.version_info < (3, 9):
                return self.validation_helper.create_validation_result(
                    valid=False,
                    warnings=["Python 3.9+ recommended for best type annotation support"]
                )

            return self.validation_helper.create_validation_result(
                valid=True,
                components={
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "packages": "all_available",
                    "config": self.config.model_dump()
                }
            )

        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            return self.validation_helper.create_validation_result(
                valid=False,
                errors=[f"Environment validation error: {e!s}"]
            )

    def analyze_project(self, project_path: Path) -> Dict[str, Any]:
        """Analyze entire project for type annotation issues."""
        logger.info(f"🔍 Analyzing project type annotations: {project_path}")

        results = []
        total_issues = 0
        total_fixable = 0

        # Find all Python files
        python_files = list(project_path.rglob("*.py"))

        for file_path in python_files:
            # Skip excluded files
            if str(file_path.resolve()) in self.config.excluded_files:
                continue

            # Skip __pycache__ and .venv directories
            if "__pycache__" in str(file_path) or ".venv" in str(file_path):
                continue

            result = self.analyzer.analyze_file(file_path)
            if result.get("issues"):
                results.append(result)
                total_issues += result.get("total_issues", 0)
                total_fixable += result.get("fixable", 0)

        return {
            "project_path": str(project_path),
            "files_analyzed": len(python_files),
            "files_with_issues": len(results),
            "total_issues": total_issues,
            "total_fixable": total_fixable,
            "results": results,
            "config": self.config.model_dump()
        }


# Utility functions for common use cases

def ensure_typed_validation_result(func: F) -> F:
    """Decorator to ensure function returns properly typed validation result."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ValidationResult:
        result = func(*args, **kwargs)

        # Ensure result is properly typed
        if not ValidationResultType.is_validation_result(result):
            logger.warning(f"Function {func.__name__} returned improperly typed validation result")
            return ValidationResultType.create_validation_result(
                valid=False,
                errors=["Invalid validation result format"],
                components={"original_result": result}
            )

        return result

    return wrapper  # type: ignore


def safe_optional_access(obj: Optional[Any], attr: str, default: Any = None) -> Any:
    """Safely access attribute on potentially None object."""
    return OptionalTypeHandler.safe_attribute_access(obj, attr, default)


def safe_dict_get(obj: Optional[Dict[str, Any]], key: str, default: Any = None) -> Any:
    """Safely get dictionary value from potentially None dict."""
    return OptionalTypeHandler.safe_dict_access(obj, key, default)


# Example usage and testing functions

async def test_type_annotation_manager() -> ValidationResult:
    """Test the type annotation management system."""
    logger.info("🧪 Testing Type Annotation Manager...")

    try:
        # Initialize manager
        config = TypeAnnotationConfig(
            auto_fix_enabled=True,
            strict_mode=False,
            validation_enabled=True
        )

        manager = TypeAnnotationManager(config)

        # Validate environment
        env_result = manager.validate_environment()
        if not env_result["valid"]:
            return ValidationResultType.create_validation_result(
                valid=False,
                errors=["Environment validation failed"],
                components={"env_validation": env_result}
            )

        # Test project analysis (on a small subset)
        project_path = Path("src/ignition/modules/sme_agent")
        if project_path.exists():
            analysis_result = manager.analyze_project(project_path)

            return ValidationResultType.create_validation_result(
                valid=True,
                components={
                    "environment": env_result,
                    "analysis": analysis_result
                }
            )

        return ValidationResultType.create_validation_result(
            valid=True,
            warnings=["Project path not found for testing"],
            components={"environment": env_result}
        )

    except Exception as e:
        logger.error(f"❌ Type annotation manager test failed: {e}")
        return ValidationResultType.create_validation_result(
            valid=False,
            errors=[f"Test failed: {e!s}"]
        )


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Main function for testing."""
        result = await test_type_annotation_manager()

        if result["valid"]:
            print("✅ Type Annotation Manager test passed")
            if result.get("components", {}).get("analysis"):
                analysis = result["components"]["analysis"]
                print(f"📊 Analysis: {analysis['files_with_issues']} files with {analysis['total_issues']} issues")
        else:
            print("❌ Type Annotation Manager test failed")
            for error in result.get("errors", []):
                print(f"   Error: {error}")

    asyncio.run(main()) 