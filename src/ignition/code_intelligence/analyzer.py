from typing import Dict, List

"""Code Analyzer for extracting structure from Python files using AST."""

import ast
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .schema import ClassNode, CodeFileNode, ImportNode, MethodNode

logger = logging.getLogger(__name__)


class ComplexityCalculator(ast.NodeVisitor):
    """Calculate cyclomatic complexity of code."""

    def __init__(self) -> None:
        self.complexity = 1  # Base complexity

    def visit_If(self) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_Try(self) -> None:
        self.complexity += len(node.handlers)
        self.generic_visit(node)

    def visit_With(self) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self) -> None:
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_Compare(self) -> None:
        self.complexity += len(node.comparators)
        self.generic_visit(node)


class CodeAnalyzer:
    """Analyzes Python code files and extracts structural information."""

    def __init__(self) -> None:
        """Initialize the code analyzer."""
        self.supported_extensions = {".py"}

    def analyze_file(self, file_path: Path) -> dict[str, Any] | None:
        """Analyze a single Python file and extract all structural information."""
        try:
            if not self._is_supported_file(file_path):
                return None

            # Read file content
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {e}")
                return None

            # Extract file information
            file_info = self._analyze_file_info(file_path, content)

            # Extract classes
            classes = self._extract_classes(tree, file_path)

            # Extract functions/methods
            methods = self._extract_methods(tree, file_path)

            # Extract imports
            imports = self._extract_imports(tree, file_path)

            return {
                "file": file_info,
                "classes": classes,
                "methods": methods,
                "imports": imports,
            }

        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return None

    def analyze_directory(
        self, directory_path: Path, recursive: bool = True
    ) -> list[dict[str, Any]]:
        """Analyze all Python files in a directory."""
        results = []

        try:
            pattern = "**/*.py" if recursive else "*.py"

            for file_path in directory_path.glob(pattern):
                if file_path.is_file():
                    result = self.analyze_file(file_path)
                    if result:
                        results.append(result)

        except Exception as e:
            logger.error(f"Failed to analyze directory {directory_path}: {e}")

        return results

    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported for analysis."""
        return file_path.suffix.lower() in self.supported_extensions

    def _get_relative_path(self, file_path: Path) -> str:
        """Get relative path, handling both absolute and relative paths."""
        try:
            return str(file_path.relative_to(Path.cwd()))
        except ValueError:
            # If file is not under current directory, use the full path
            return str(file_path)

    def _analyze_file_info(self, file_path: Path, content: str) -> CodeFileNode:
        """Extract basic file information."""
        stat = file_path.stat()

        # Calculate complexity
        tree = ast.parse(content)
        complexity_calc = ComplexityCalculator()
        complexity_calc.visit(tree)

        # Calculate maintainability index (simplified)
        lines = len(content.splitlines())
        maintainability = max(0, 171 - 5.2 * complexity_calc.complexity - 0.23 * lines)

        # Calculate content hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        return CodeFileNode(
            path=self._get_relative_path(file_path),
            lines=lines,
            complexity=complexity_calc.complexity,
            maintainability_index=maintainability,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            content_hash=content_hash,
            language="python",
            size_bytes=stat.st_size,
        )

    def _extract_classes(self, tree: ast.AST, file_path: Path) -> list[ClassNode]:
        """Extract class information from AST."""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Calculate class complexity
                complexity_calc = ComplexityCalculator()
                complexity_calc.visit(node)

                # Count methods
                methods_count = sum(
                    1 for n in node.body if isinstance(n, ast.FunctionDef)
                )

                # Extract inheritance
                inheritance = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        inheritance.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        inheritance.append(ast.unparse(base))

                # Extract docstring
                docstring = None
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    docstring = node.body[0].value.value

                class_node = ClassNode(
                    name=node.name,
                    file_path=str(file_path.relative_to(Path.cwd())),
                    start_line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    methods_count=methods_count,
                    complexity=complexity_calc.complexity,
                    docstring=docstring,
                    inheritance=inheritance if inheritance else None,
                )

                classes.append(class_node)

        return classes

    def _extract_methods(self, tree: ast.AST, file_path: Path) -> list[MethodNode]:
        """Extract method/function information from AST."""
        methods = []

        # Track class context
        class_stack = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_stack.append(node.name)
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Calculate method complexity
                complexity_calc = ComplexityCalculator()
                complexity_calc.visit(node)

                # Extract parameters
                parameters = []
                for arg in node.args.args:
                    parameters.append(arg.arg)

                # Extract return type
                return_type = None
                if node.returns:
                    return_type = ast.unparse(node.returns)

                # Extract docstring
                docstring = None
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    docstring = node.body[0].value.value

                # Determine class context
                class_name = class_stack[-1] if class_stack else None

                method_node = MethodNode(
                    name=node.name,
                    class_name=class_name,
                    file_path=str(file_path.relative_to(Path.cwd())),
                    start_line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    parameters=parameters,
                    complexity=complexity_calc.complexity,
                    return_type=return_type,
                    docstring=docstring,
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                )

                methods.append(method_node)

        return methods

    def _extract_imports(self, tree: ast.AST, file_path: Path) -> list[ImportNode]:
        """Extract import information from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_node = ImportNode(
                        module=alias.name,
                        alias=alias.asname,
                        from_module=None,
                        file_path=str(file_path.relative_to(Path.cwd())),
                        line_number=node.lineno,
                        is_local=self._is_local_import(alias.name),
                    )
                    imports.append(import_node)

            elif (
                isinstance(node, ast.ImportFrom) and node.module
            ):  # Skip relative imports without module
                for alias in node.names:
                    import_node = ImportNode(
                        module=alias.name,
                        alias=alias.asname,
                        from_module=node.module,
                        file_path=str(file_path.relative_to(Path.cwd())),
                        line_number=node.lineno,
                        is_local=self._is_local_import(node.module),
                    )
                    imports.append(import_node)

        return imports

    def _is_local_import(self, module_name: str) -> bool:
        """Determine if an import is local to the project."""
        # Simple heuristic: if it starts with 'src.' or doesn't contain dots, it might be local
        if module_name.startswith("src."):
            return True
        return bool(
            "." not in module_name
            and module_name not in ["os", "sys", "json", "datetime", "logging"]
        )

    def get_file_dependencies(self, file_analysis: dict[str, Any]) -> list[str]:
        """Extract file dependencies from analysis results."""
        dependencies = []

        for import_info in file_analysis.get("imports", []):
            if import_info.is_local:
                # Convert module name to file path
                if import_info.from_module:
                    module_path = import_info.from_module.replace(".", "/") + ".py"
                else:
                    module_path = import_info.module.replace(".", "/") + ".py"
                dependencies.append(module_path)

        return dependencies

    def calculate_change_impact(
        self, file_path: Path, changes: list[str]
    ) -> dict[str, Any]:
        """Calculate the potential impact of changes to a file."""
        # This is a simplified implementation
        # In a full implementation, this would analyze the specific changes

        impact_score = 0
        affected_components = []

        # Analyze current file
        analysis = self.analyze_file(file_path)
        if not analysis:
            return {"impact_score": 0, "affected_components": []}

        # Calculate impact based on file characteristics
        file_info = analysis["file"]
        impact_score += file_info.complexity * 0.1
        impact_score += len(analysis["classes"]) * 0.2
        impact_score += len(analysis["methods"]) * 0.1

        # Add affected components
        affected_components.extend([c.name for c in analysis["classes"]])
        affected_components.extend([m.name for m in analysis["methods"]])

        return {
            "impact_score": min(impact_score, 10.0),  # Cap at 10
            "affected_components": affected_components,
            "file_complexity": file_info.complexity,
            "maintainability_index": file_info.maintainability_index,
        }
