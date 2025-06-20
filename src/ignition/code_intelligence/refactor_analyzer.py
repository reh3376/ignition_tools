"""Automated Code Refactoring System - Large File Detection & Analysis.

This module implements intelligent analysis of oversized Python files to identify
refactoring opportunities and single responsibility violations.
"""

import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[2]))

from ignition.code_intelligence.analyzer import CodeAnalyzer


@dataclass
class RefactoringRecommendation:
    """Represents a refactoring recommendation for an oversized file."""

    file_path: str
    current_lines: int
    physical_lines: int  # Excluding blank lines and comments
    complexity_score: float
    maintainability_index: float
    single_responsibility_violations: list[str]
    suggested_splits: list["SplitRecommendation"]
    public_surface_size: int
    private_helpers_count: int
    impact_analysis: dict[str, Any]


@dataclass
class SplitRecommendation:
    """Represents a recommendation to split code into a separate module."""

    target_module_name: str
    classes_to_move: list[str]
    functions_to_move: list[str]
    estimated_lines: int
    dependencies: list[str]
    reason: str
    confidence_score: float


class LargeFileDetector:
    """Detects and analyzes files that exceed size thresholds."""

    def __init__(self, line_threshold: int = 950, complexity_threshold: float = 50.0) -> None:
        self.line_threshold = line_threshold
        self.complexity_threshold = complexity_threshold
        self.analyzer = CodeAnalyzer()

    def scan_directory(self, directory: Path) -> list[Path]:
        """Scan directory for Python files exceeding the line threshold."""
        oversized_files = []

        for py_file in directory.rglob("*.py"):
            if self._is_oversized(py_file):
                oversized_files.append(py_file)

        return sorted(oversized_files, key=lambda f: self._count_physical_lines(f), reverse=True)

    def _is_oversized(self, file_path: Path) -> bool:
        """Check if a file exceeds the line threshold."""
        try:
            physical_lines = self._count_physical_lines(file_path)
            return physical_lines > self.line_threshold
        except Exception:
            return False

    def _count_physical_lines(self, file_path: Path) -> int:
        """Count physical lines of code (excluding blank lines and comments)."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            physical_lines = 0
            in_multiline_string = False

            for line in lines:
                stripped = line.strip()

                # Skip empty lines
                if not stripped:
                    continue

                # Handle multiline strings/docstrings
                if '"""' in stripped or "'''" in stripped:
                    quote_count = stripped.count('"""') + stripped.count("'''")
                    if quote_count % 2 == 1:
                        in_multiline_string = not in_multiline_string
                    if in_multiline_string and quote_count == 1:
                        continue

                if in_multiline_string:
                    continue

                # Skip comment-only lines
                if stripped.startswith("#"):
                    continue

                physical_lines += 1

            return physical_lines
        except Exception:
            return 0


class SingleResponsibilityAnalyzer:
    """Analyzes files for single responsibility principle violations."""

    def __init__(self) -> None:
        self.analyzer = CodeAnalyzer()

    def analyze_file(self, file_path: Path) -> list[str]:
        """Analyze a file for single responsibility violations."""
        violations = []

        try:
            analysis = self.analyzer.analyze_file(file_path)
            if not analysis:
                return ["Could not analyze file - syntax error or other issue"]

            # Check for multiple unrelated class hierarchies
            class_purposes = self._categorize_classes(analysis["classes"])
            if len(class_purposes) > 1:
                violations.append(f"Multiple unrelated class hierarchies: {', '.join(class_purposes.keys())}")

            # Check for mixed concerns in imports
            import_categories = self._categorize_imports(analysis["imports"])
            if len(import_categories) > 3:  # Allow some mixing, but not too much
                violations.append(f"Mixed import concerns: {', '.join(import_categories.keys())}")

            # Check for excessive method count in single class
            for class_info in analysis["classes"]:
                if class_info.methods_count > 20:
                    violations.append(f"Class '{class_info.name}' has too many methods ({class_info.methods_count})")

            # Check for file-level complexity
            file_complexity = analysis["file"].complexity
            if file_complexity > 100:
                violations.append(f"Excessive file complexity: {file_complexity:.1f}")

        except Exception as e:
            violations.append(f"Analysis error: {e!s}")

        return violations

    def _categorize_classes(self, classes: list[Any]) -> dict[str, list[str]]:
        """Categorize classes by their apparent purpose."""
        categories = defaultdict(list)

        for class_info in classes:
            name = class_info.name.lower()

            if any(keyword in name for keyword in ["cli", "command", "interface"]):
                categories["CLI/Interface"].append(class_info.name)
            elif any(keyword in name for keyword in ["client", "connection", "gateway"]):
                categories["Network/Client"].append(class_info.name)
            elif any(keyword in name for keyword in ["analyzer", "parser", "processor"]):
                categories["Analysis/Processing"].append(class_info.name)
            elif any(keyword in name for keyword in ["manager", "controller", "handler"]):
                categories["Management/Control"].append(class_info.name)
            elif any(keyword in name for keyword in ["model", "data", "schema"]):
                categories["Data/Model"].append(class_info.name)
            else:
                categories["Other"].append(class_info.name)

        return dict(categories)

    def _categorize_imports(self, imports: list[Any]) -> dict[str, list[str]]:
        """Categorize imports by their purpose."""
        categories = defaultdict(list)

        for import_info in imports:
            module = import_info.module.lower() if import_info.module else ""
            from_module = import_info.from_module.lower() if import_info.from_module else ""

            # Use the from_module if available, otherwise use module
            module_to_check = from_module if from_module else module

            if any(keyword in module_to_check for keyword in ["os", "sys", "pathlib", "subprocess"]):
                categories["System"].append(module_to_check)
            elif any(keyword in module_to_check for keyword in ["click", "argparse", "rich", "prompt"]):
                categories["CLI"].append(module_to_check)
            elif any(keyword in module_to_check for keyword in ["requests", "urllib", "http", "socket"]):
                categories["Network"].append(module_to_check)
            elif any(keyword in module_to_check for keyword in ["json", "yaml", "csv", "xml"]):
                categories["Data"].append(module_to_check)
            elif any(keyword in module_to_check for keyword in ["neo4j", "sqlite", "postgres", "mysql"]):
                categories["Database"].append(module_to_check)
            elif module_to_check.startswith("src.") or module_to_check.startswith("ignition."):
                categories["Internal"].append(module_to_check)
            else:
                categories["External"].append(module_to_check)

        return dict(categories)


class RefactoringRecommendationEngine:
    """Generates intelligent refactoring recommendations for oversized files."""

    def __init__(self) -> None:
        self.detector = LargeFileDetector()
        self.sr_analyzer = SingleResponsibilityAnalyzer()
        self.analyzer = CodeAnalyzer()

    def analyze_file(self, file_path: Path) -> RefactoringRecommendation | None:
        """Generate comprehensive refactoring recommendations for a file."""
        # Basic metrics
        physical_lines = self.detector._count_physical_lines(file_path)
        try:
            total_lines = sum(1 for _ in open(file_path, encoding="utf-8"))
        except Exception:
            total_lines = physical_lines

        # Code analysis
        analysis = self.analyzer.analyze_file(file_path)
        if not analysis:
            print(f"Could not analyze {file_path} - skipping")
            return None

        # Single responsibility analysis
        violations = self.sr_analyzer.analyze_file(file_path)

        # Generate split recommendations
        split_recommendations = self._generate_split_recommendations(file_path, analysis)

        # Calculate public surface size
        public_surface_size = self._calculate_public_surface_size(analysis)

        # Count private helpers
        private_helpers_count = self._count_private_helpers(analysis)

        # Impact analysis
        impact_analysis = self._analyze_impact(file_path, analysis)

        return RefactoringRecommendation(
            file_path=str(file_path),
            current_lines=total_lines,
            physical_lines=physical_lines,
            complexity_score=analysis["file"].complexity,
            maintainability_index=analysis["file"].maintainability_index,
            single_responsibility_violations=violations,
            suggested_splits=split_recommendations,
            public_surface_size=public_surface_size,
            private_helpers_count=private_helpers_count,
            impact_analysis=impact_analysis,
        )

    def _generate_split_recommendations(self, file_path: Path, analysis) -> list[SplitRecommendation]:
        """Generate recommendations for splitting the file."""
        recommendations = []

        # Group classes by category
        class_categories = self.sr_analyzer._categorize_classes(analysis["classes"])

        for category, class_names in class_categories.items():
            if len(class_names) > 1 and category != "Other":
                # Estimate lines for this category
                estimated_lines = self._estimate_category_lines(analysis["classes"], class_names)

                if estimated_lines > 100:  # Only recommend if substantial
                    module_name = self._suggest_module_name(file_path, category)

                    recommendations.append(
                        SplitRecommendation(
                            target_module_name=module_name,
                            classes_to_move=class_names,
                            functions_to_move=[],  # TODO: Analyze functions
                            estimated_lines=estimated_lines,
                            dependencies=self._analyze_dependencies(analysis, class_names),
                            reason=f"Extract {category.lower()} functionality",
                            confidence_score=0.8 if len(class_names) > 2 else 0.6,
                        )
                    )

        return recommendations

    def _calculate_public_surface_size(self, analysis) -> int:
        """Calculate the size of the public API surface."""
        public_lines = 0

        # Count public classes and their public methods
        for class_info in analysis["classes"]:
            if not class_info.name.startswith("_"):
                public_lines += 10  # Estimate for class definition

        # Count public functions
        for method_info in analysis["methods"]:
            if not method_info.name.startswith("_"):
                public_lines += 5  # Estimate for function signature

        return public_lines

    def _count_private_helpers(self, analysis) -> int:
        """Count private helper functions and methods."""
        private_count = 0

        # Count private methods
        for method_info in analysis["methods"]:
            if method_info.name.startswith("_") and not method_info.name.startswith("__"):
                private_count += 1

        return private_count

    def _analyze_impact(self, file_path: Path, analysis) -> dict[str, Any]:
        """Analyze the impact of refactoring this file."""
        impact = {
            "dependent_files": [],
            "import_complexity": len(analysis["imports"]),
            "external_dependencies": 0,
            "risk_level": "low",
        }

        # Find files that import this module
        try:
            module_name = self._path_to_module_name(file_path)
            project_root = Path.cwd()

            for py_file in project_root.rglob("*.py"):
                if py_file == file_path:
                    continue

                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()
                        if module_name in content:
                            try:
                                relative_path = py_file.relative_to(project_root)
                                impact["dependent_files"].append(str(relative_path))
                            except ValueError:
                                impact["dependent_files"].append(str(py_file))
                except Exception:
                    continue
        except Exception:
            pass

        # Assess risk level
        if len(impact["dependent_files"]) > 10:
            impact["risk_level"] = "high"
        elif len(impact["dependent_files"]) > 5:
            impact["risk_level"] = "medium"

        return impact

    def _estimate_category_lines(self, classes: list[Any], class_names: list[str]) -> int:
        """Estimate lines of code for a category of classes."""
        total_lines = 0
        for class_info in classes:
            if class_info.name in class_names:
                # Rough estimate: 10 lines per method + 20 for class overhead
                method_count = class_info.methods_count
                total_lines += (method_count * 10) + 20
        return total_lines

    def _suggest_module_name(self, file_path: Path, category: str) -> str:
        """Suggest a module name for the extracted code."""
        base_name = file_path.stem
        category_map = {
            "CLI/Interface": "cli",
            "Network/Client": "client",
            "Analysis/Processing": "analyzer",
            "Management/Control": "manager",
            "Data/Model": "models",
        }

        suffix = category_map.get(category, category.lower().replace("/", "_"))
        return f"{base_name}_{suffix}"

    def _analyze_dependencies(self, analysis, class_names: list[str]) -> list[str]:
        """Analyze dependencies for classes to be moved."""
        dependencies = set()

        # Add imports that might be needed
        for import_info in analysis["imports"]:
            if import_info.from_module:
                dependencies.add(import_info.from_module)
            else:
                dependencies.add(import_info.module)

        return list(dependencies)[:5]  # Limit to top 5 for brevity

    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            # Get relative path from current working directory
            relative_path = file_path.relative_to(Path.cwd())
            parts = relative_path.parts

            if "src" in parts:
                src_index = parts.index("src")
                module_parts = parts[src_index + 1 :]
                module_name = ".".join(module_parts).replace(".py", "")
                return module_name
            else:
                # Fallback to just the stem
                return file_path.stem
        except Exception:
            return file_path.stem


def main() -> None:
    """Main function for testing the refactor analyzer."""
    detector = LargeFileDetector()
    engine = RefactoringRecommendationEngine()

    # Scan for oversized files
    src_dir = Path("src")
    oversized_files = detector.scan_directory(src_dir)

    print(f"Found {len(oversized_files)} files exceeding {detector.line_threshold} lines:")

    for file_path in oversized_files[:5]:  # Analyze top 5
        print(f"\n{'=' * 60}")
        print(f"Analyzing: {file_path}")
        print(f"{'=' * 60}")

        recommendation = engine.analyze_file(file_path)
        if not recommendation:
            continue

        print(f"Physical lines: {recommendation.physical_lines}")
        print(f"Complexity: {recommendation.complexity_score:.1f}")
        print(f"Maintainability: {recommendation.maintainability_index:.1f}")
        print(f"Public surface size: {recommendation.public_surface_size} lines")
        print(f"Private helpers: {recommendation.private_helpers_count}")

        if recommendation.single_responsibility_violations:
            print("\nSingle Responsibility Violations:")
            for violation in recommendation.single_responsibility_violations:
                print(f"  - {violation}")

        if recommendation.suggested_splits:
            print("\nSuggested Splits:")
            for split in recommendation.suggested_splits:
                print(f"  - {split.target_module_name}: {split.reason}")
                print(f"    Classes: {', '.join(split.classes_to_move)}")
                print(f"    Estimated lines: {split.estimated_lines}")
                print(f"    Confidence: {split.confidence_score:.1f}")


if __name__ == "__main__":
    main()
