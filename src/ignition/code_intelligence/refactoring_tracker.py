"""Refactoring Documentation & Tracking System

This module provides comprehensive tracking and documentation for refactoring operations,
including architecture diagram generation, Neo4j history tracking, and impact reporting.
"""

import ast
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RefactoringOperation:
    """Represents a completed refactoring operation."""

    operation_id: str
    operation_type: str  # "split_file", "extract_class", "move_method", etc.
    timestamp: datetime
    source_files: list[str]
    target_files: list[str]
    lines_moved: int
    complexity_before: float
    complexity_after: float
    maintainability_before: float
    maintainability_after: float
    git_commits: list[str]
    success: bool
    rollback_available: bool
    impact_score: float
    user_notes: str | None = None


@dataclass
class ArchitectureDiagram:
    """Represents an architecture diagram for refactored code."""

    diagram_id: str
    diagram_type: str  # "class_diagram", "module_diagram", "dependency_graph"
    source_file: str
    target_files: list[str]
    mermaid_code: str
    svg_content: str | None = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TODOComment:
    """Represents a TODO comment for manual domain input."""

    file_path: str
    line_number: int
    comment_type: str  # "domain_knowledge", "business_logic", "validation", "naming"
    description: str
    priority: str  # "high", "medium", "low"
    created_at: datetime
    resolved: bool = False
    resolution_notes: str | None = None


@dataclass
class RefactoringMetrics:
    """Metrics for refactoring impact analysis."""

    operation_id: str
    files_affected: int
    total_lines_moved: int
    complexity_reduction: float
    maintainability_improvement: float
    test_coverage_change: float
    build_time_change: float
    performance_impact: str  # "positive", "negative", "neutral"
    developer_satisfaction: int | None = None  # 1-10 scale


class RefactoringTracker:
    """Tracks and documents refactoring operations."""

    def __init__(self, project_root: Path, graph_client=None):
        self.project_root = project_root
        self.graph_client = graph_client
        self.tracking_dir = project_root / ".refactoring_tracking"
        self.tracking_dir.mkdir(exist_ok=True)

        # Initialize tracking files
        self.operations_file = self.tracking_dir / "operations.json"
        self.diagrams_dir = self.tracking_dir / "diagrams"
        self.diagrams_dir.mkdir(exist_ok=True)
        self.todos_file = self.tracking_dir / "todos.json"
        self.metrics_file = self.tracking_dir / "metrics.json"

        # Load existing data
        self.operations = self._load_operations()
        self.todos = self._load_todos()
        self.metrics = self._load_metrics()

    def track_refactoring_operation(self, operation: RefactoringOperation) -> bool:
        """Track a completed refactoring operation."""
        try:
            # Store in local tracking
            self.operations[operation.operation_id] = asdict(operation)
            self._save_operations()

            # Store in Neo4j if available
            if self.graph_client:
                self._store_operation_in_graph(operation)

            # Generate documentation
            self._generate_operation_documentation(operation)

            logger.info(f"Tracked refactoring operation: {operation.operation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to track refactoring operation: {e}")
            return False

    def generate_architecture_diagram(
        self, operation: RefactoringOperation
    ) -> ArchitectureDiagram | None:
        """Generate architecture diagram for a refactoring operation."""
        try:
            if operation.operation_type == "split_file":
                return self._generate_file_split_diagram(operation)
            elif operation.operation_type == "extract_class":
                return self._generate_class_extraction_diagram(operation)
            elif operation.operation_type == "move_method":
                return self._generate_method_move_diagram(operation)
            else:
                return self._generate_generic_diagram(operation)

        except Exception as e:
            logger.error(f"Failed to generate architecture diagram: {e}")
            return None

    def _generate_file_split_diagram(
        self, operation: RefactoringOperation
    ) -> ArchitectureDiagram:
        """Generate diagram for file split operation."""
        source_file = operation.source_files[0] if operation.source_files else "unknown"
        target_files = operation.target_files

        # Create Mermaid diagram
        mermaid_code = f"""
graph TD
    A["{Path(source_file).name}<br/>Original File<br/>{operation.complexity_before:.1f} complexity"]

    %% Target files
"""

        for i, target_file in enumerate(target_files):
            file_name = Path(target_file).name
            letter = chr(ord("B") + i)
            mermaid_code += f'    {letter}["{file_name}<br/>Extracted Module"]\n'
            mermaid_code += f"    A --> {letter}\n"

        mermaid_code += f"""

    %% Styling
    classDef original fill:#ffcccc
    classDef extracted fill:#ccffcc

    class A original
    class {",".join(chr(ord("B") + i) for i in range(len(target_files)))} extracted
"""

        diagram = ArchitectureDiagram(
            diagram_id=f"{operation.operation_id}_architecture",
            diagram_type="file_split_diagram",
            source_file=source_file,
            target_files=target_files,
            mermaid_code=mermaid_code.strip(),
        )

        # Save diagram
        self._save_diagram(diagram)

        return diagram

    def _generate_class_extraction_diagram(
        self, operation: RefactoringOperation
    ) -> ArchitectureDiagram:
        """Generate diagram for class extraction operation."""
        mermaid_code = f"""
classDiagram
    class OriginalFile {{
        -extracted_classes
        +remaining_methods()
        +public_interface()
    }}

    class ExtractedModule {{
        +extracted_classes
        +specialized_methods()
    }}

    OriginalFile --> ExtractedModule : extracts

    note for OriginalFile "Complexity: {operation.complexity_before:.1f} → {operation.complexity_after:.1f}"
    note for ExtractedModule "Lines moved: {operation.lines_moved}"
"""

        diagram = ArchitectureDiagram(
            diagram_id=f"{operation.operation_id}_class_extraction",
            diagram_type="class_diagram",
            source_file=operation.source_files[0] if operation.source_files else "",
            target_files=operation.target_files,
            mermaid_code=mermaid_code.strip(),
        )

        self._save_diagram(diagram)
        return diagram

    def _generate_method_move_diagram(
        self, operation: RefactoringOperation
    ) -> ArchitectureDiagram:
        """Generate diagram for method move operation."""
        mermaid_code = f"""
sequenceDiagram
    participant S as Source Class
    participant T as Target Class

    Note over S,T: Method Movement Refactoring
    S->>T: move_method()
    T-->>S: dependency_resolved

    Note over S: Complexity: {operation.complexity_before:.1f}
    Note over T: Complexity: {operation.complexity_after:.1f}
"""

        diagram = ArchitectureDiagram(
            diagram_id=f"{operation.operation_id}_method_move",
            diagram_type="sequence_diagram",
            source_file=operation.source_files[0] if operation.source_files else "",
            target_files=operation.target_files,
            mermaid_code=mermaid_code.strip(),
        )

        self._save_diagram(diagram)
        return diagram

    def _generate_generic_diagram(
        self, operation: RefactoringOperation
    ) -> ArchitectureDiagram:
        """Generate generic diagram for other refactoring types."""
        mermaid_code = f"""
graph LR
    A[Before Refactoring<br/>Complexity: {operation.complexity_before:.1f}]
    B[After Refactoring<br/>Complexity: {operation.complexity_after:.1f}]

    A --> B

    classDef before fill:#ffcccc
    classDef after fill:#ccffcc

    class A before
    class B after
"""

        diagram = ArchitectureDiagram(
            diagram_id=f"{operation.operation_id}_generic",
            diagram_type="generic_diagram",
            source_file=operation.source_files[0] if operation.source_files else "",
            target_files=operation.target_files,
            mermaid_code=mermaid_code.strip(),
        )

        self._save_diagram(diagram)
        return diagram

    def create_todo_comments(
        self, file_path: str, refactoring_context: dict[str, Any]
    ) -> list[TODOComment]:
        """Create TODO comments for manual domain input needs."""
        todos = []

        try:
            # Analyze the file to identify areas needing domain knowledge
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Find areas that need domain input
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for generic function names that need domain-specific naming
                    if any(
                        generic in node.name.lower()
                        for generic in ["process", "handle", "manage", "execute"]
                    ):
                        todo = TODOComment(
                            file_path=file_path,
                            line_number=node.lineno,
                            comment_type="naming",
                            description=f"Consider more domain-specific name for function '{node.name}'",
                            priority="medium",
                            created_at=datetime.now(),
                        )
                        todos.append(todo)

                elif isinstance(node, ast.ClassDef):
                    # Check for generic class names
                    if any(
                        generic in node.name.lower()
                        for generic in ["manager", "handler", "processor"]
                    ):
                        todo = TODOComment(
                            file_path=file_path,
                            line_number=node.lineno,
                            comment_type="naming",
                            description=f"Consider more domain-specific name for class '{node.name}'",
                            priority="medium",
                            created_at=datetime.now(),
                        )
                        todos.append(todo)

                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    # Check for magic strings that might need configuration
                    if len(node.value) > 10 and any(
                        char.isdigit() for char in node.value
                    ):
                        todo = TODOComment(
                            file_path=file_path,
                            line_number=node.lineno,
                            comment_type="business_logic",
                            description=f"Review magic string: '{node.value[:50]}...' - consider configuration",
                            priority="low",
                            created_at=datetime.now(),
                        )
                        todos.append(todo)

            # Add context-specific TODOs based on refactoring
            if refactoring_context.get("split_type") == "responsibility_separation":
                todo = TODOComment(
                    file_path=file_path,
                    line_number=1,
                    comment_type="domain_knowledge",
                    description="Review extracted responsibilities for domain accuracy and completeness",
                    priority="high",
                    created_at=datetime.now(),
                )
                todos.append(todo)

            # Store TODOs
            for todo in todos:
                todo_id = f"{todo.file_path}_{todo.line_number}_{todo.comment_type}"
                self.todos[todo_id] = asdict(todo)

            self._save_todos()

        except Exception as e:
            logger.error(f"Failed to create TODO comments: {e}")

        return todos

    def track_refactoring_history_in_graph(
        self, operation: RefactoringOperation
    ) -> bool:
        """Store refactoring history in Neo4j graph database."""
        if not self.graph_client:
            logger.warning("No graph client available for storing refactoring history")
            return False

        try:
            # Create RefactoringOperation node
            cypher = """
            CREATE (ro:RefactoringOperation {
                operation_id: $operation_id,
                operation_type: $operation_type,
                timestamp: datetime($timestamp),
                lines_moved: $lines_moved,
                complexity_before: $complexity_before,
                complexity_after: $complexity_after,
                maintainability_before: $maintainability_before,
                maintainability_after: $maintainability_after,
                success: $success,
                impact_score: $impact_score,
                user_notes: $user_notes
            })
            RETURN ro
            """

            result = self.graph_client.execute_query(
                cypher,
                {
                    "operation_id": operation.operation_id,
                    "operation_type": operation.operation_type,
                    "timestamp": operation.timestamp.isoformat(),
                    "lines_moved": operation.lines_moved,
                    "complexity_before": operation.complexity_before,
                    "complexity_after": operation.complexity_after,
                    "maintainability_before": operation.maintainability_before,
                    "maintainability_after": operation.maintainability_after,
                    "success": operation.success,
                    "impact_score": operation.impact_score,
                    "user_notes": operation.user_notes,
                },
            )

            # Link to affected files
            for source_file in operation.source_files:
                self._link_operation_to_file(
                    operation.operation_id, source_file, "SOURCE"
                )

            for target_file in operation.target_files:
                self._link_operation_to_file(
                    operation.operation_id, target_file, "TARGET"
                )

            # Link to git commits
            for commit_hash in operation.git_commits:
                self._link_operation_to_commit(operation.operation_id, commit_hash)

            logger.info(
                f"Stored refactoring operation {operation.operation_id} in graph database"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to store refactoring history in graph: {e}")
            return False

    def _link_operation_to_file(
        self, operation_id: str, file_path: str, relationship_type: str
    ) -> None:
        """Link refactoring operation to a file."""
        cypher = """
        MATCH (ro:RefactoringOperation {operation_id: $operation_id})
        MERGE (cf:CodeFile {path: $file_path})
        MERGE (ro)-[:AFFECTS {type: $relationship_type}]->(cf)
        """

        self.graph_client.execute_query(
            cypher,
            {
                "operation_id": operation_id,
                "file_path": file_path,
                "relationship_type": relationship_type,
            },
        )

    def _link_operation_to_commit(self, operation_id: str, commit_hash: str) -> None:
        """Link refactoring operation to a git commit."""
        cypher = """
        MATCH (ro:RefactoringOperation {operation_id: $operation_id})
        MERGE (gc:GitCommit {hash: $commit_hash})
        MERGE (ro)-[:IMPLEMENTED_IN]->(gc)
        """

        self.graph_client.execute_query(
            cypher, {"operation_id": operation_id, "commit_hash": commit_hash}
        )

    def build_refactoring_impact_report(
        self, operation_id: str | None = None, days: int = 30
    ) -> dict[str, Any]:
        """Build comprehensive refactoring impact report."""
        try:
            if operation_id:
                # Report for specific operation
                return self._build_operation_report(operation_id)
            else:
                # Report for recent operations
                return self._build_period_report(days)

        except Exception as e:
            logger.error(f"Failed to build refactoring impact report: {e}")
            return {"error": str(e)}

    def _build_operation_report(self, operation_id: str) -> dict[str, Any]:
        """Build report for a specific refactoring operation."""
        if operation_id not in self.operations:
            return {"error": f"Operation {operation_id} not found"}

        operation_data = self.operations[operation_id]
        operation = RefactoringOperation(**operation_data)

        # Calculate metrics
        complexity_improvement = (
            operation.complexity_before - operation.complexity_after
        )
        maintainability_improvement = (
            operation.maintainability_after - operation.maintainability_before
        )

        # Get related TODOs
        related_todos = [
            todo
            for todo in self.todos.values()
            if any(
                file_path in todo["file_path"]
                for file_path in operation.source_files + operation.target_files
            )
        ]

        # Get architecture diagram
        diagram_path = self.diagrams_dir / f"{operation_id}_architecture.json"
        diagram_info = None
        if diagram_path.exists():
            with open(diagram_path) as f:
                diagram_info = json.load(f)

        report = {
            "operation_id": operation_id,
            "operation_type": operation.operation_type,
            "timestamp": operation.timestamp.isoformat(),
            "success": operation.success,
            "impact_analysis": {
                "files_affected": len(operation.source_files)
                + len(operation.target_files),
                "lines_moved": operation.lines_moved,
                "complexity_improvement": complexity_improvement,
                "maintainability_improvement": maintainability_improvement,
                "impact_score": operation.impact_score,
            },
            "files": {
                "source_files": operation.source_files,
                "target_files": operation.target_files,
            },
            "git_commits": operation.git_commits,
            "todos_created": len(related_todos),
            "architecture_diagram": diagram_info,
            "recommendations": self._generate_operation_recommendations(operation),
        }

        return report

    def _build_period_report(self, days: int) -> dict[str, Any]:
        """Build report for operations in the specified period."""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)

        recent_operations = [
            op
            for op in self.operations.values()
            if datetime.fromisoformat(op["timestamp"]).timestamp() > cutoff_date
        ]

        if not recent_operations:
            return {
                "period_days": days,
                "operations_count": 0,
                "message": "No refactoring operations in the specified period",
            }

        # Calculate aggregate metrics
        total_lines_moved = sum(op["lines_moved"] for op in recent_operations)
        total_complexity_reduction = sum(
            op["complexity_before"] - op["complexity_after"] for op in recent_operations
        )
        successful_operations = sum(1 for op in recent_operations if op["success"])

        # Group by operation type
        operation_types = {}
        for op in recent_operations:
            op_type = op["operation_type"]
            if op_type not in operation_types:
                operation_types[op_type] = 0
            operation_types[op_type] += 1

        # Get all TODOs from the period
        recent_todos = [
            todo
            for todo in self.todos.values()
            if datetime.fromisoformat(todo["created_at"]).timestamp() > cutoff_date
        ]

        report = {
            "period_days": days,
            "analysis_date": datetime.now().isoformat(),
            "summary": {
                "total_operations": len(recent_operations),
                "successful_operations": successful_operations,
                "success_rate": successful_operations / len(recent_operations) * 100,
                "total_lines_moved": total_lines_moved,
                "total_complexity_reduction": total_complexity_reduction,
                "average_impact_score": sum(
                    op["impact_score"] for op in recent_operations
                )
                / len(recent_operations),
            },
            "operation_types": operation_types,
            "todos_created": len(recent_todos),
            "todos_by_priority": {
                "high": sum(1 for todo in recent_todos if todo["priority"] == "high"),
                "medium": sum(
                    1 for todo in recent_todos if todo["priority"] == "medium"
                ),
                "low": sum(1 for todo in recent_todos if todo["priority"] == "low"),
            },
            "recommendations": self._generate_period_recommendations(
                recent_operations, recent_todos
            ),
        }

        return report

    def _generate_operation_recommendations(
        self, operation: RefactoringOperation
    ) -> list[str]:
        """Generate recommendations based on a specific operation."""
        recommendations = []

        complexity_improvement = (
            operation.complexity_before - operation.complexity_after
        )
        maintainability_improvement = (
            operation.maintainability_after - operation.maintainability_before
        )

        if complexity_improvement > 10:
            recommendations.append(
                "Excellent complexity reduction achieved. Consider similar patterns for other large files."
            )
        elif complexity_improvement < 0:
            recommendations.append(
                "Complexity increased. Review the refactoring approach and consider alternative strategies."
            )

        if maintainability_improvement > 10:
            recommendations.append(
                "Significant maintainability improvement. Document the approach for future reference."
            )

        if operation.lines_moved > 500:
            recommendations.append(
                "Large amount of code moved. Ensure comprehensive testing and documentation updates."
            )

        if not operation.success:
            recommendations.append(
                "Operation failed. Review logs and consider rollback if necessary."
            )

        if operation.impact_score > 0.8:
            recommendations.append(
                "High impact operation. Monitor for any unexpected side effects."
            )

        return recommendations

    def _generate_period_recommendations(
        self, operations: list[dict], todos: list[dict]
    ) -> list[str]:
        """Generate recommendations based on period analysis."""
        recommendations = []

        if len(operations) > 10:
            recommendations.append(
                "High refactoring activity. Ensure adequate testing and code review processes."
            )

        success_rate = (
            sum(1 for op in operations if op["success"]) / len(operations) * 100
        )
        if success_rate < 80:
            recommendations.append(
                f"Success rate is {success_rate:.1f}%. Review failed operations and improve processes."
            )

        high_priority_todos = sum(1 for todo in todos if todo["priority"] == "high")
        if high_priority_todos > 5:
            recommendations.append(
                f"{high_priority_todos} high-priority TODOs created. Address these promptly."
            )

        avg_complexity_reduction = sum(
            op["complexity_before"] - op["complexity_after"] for op in operations
        ) / len(operations)

        if avg_complexity_reduction < 5:
            recommendations.append(
                "Low average complexity reduction. Consider more aggressive refactoring strategies."
            )

        return recommendations

    def _save_diagram(self, diagram: ArchitectureDiagram) -> None:
        """Save architecture diagram to file."""
        diagram_file = self.diagrams_dir / f"{diagram.diagram_id}.json"
        with open(diagram_file, "w") as f:
            json.dump(asdict(diagram), f, indent=2, default=str)

        # Also save Mermaid code separately for easy viewing
        mermaid_file = self.diagrams_dir / f"{diagram.diagram_id}.mmd"
        with open(mermaid_file, "w") as f:
            f.write(diagram.mermaid_code)

    def _store_operation_in_graph(self, operation: RefactoringOperation) -> None:
        """Store operation in graph database."""
        # This calls the method we already implemented
        self.track_refactoring_history_in_graph(operation)

    def _generate_operation_documentation(
        self, operation: RefactoringOperation
    ) -> None:
        """Generate documentation for the operation."""
        # Generate architecture diagram
        diagram = self.generate_architecture_diagram(operation)

        # Create TODO comments for affected files
        for file_path in operation.target_files:
            if Path(file_path).exists():
                self.create_todo_comments(
                    file_path,
                    {
                        "operation_id": operation.operation_id,
                        "split_type": (
                            "responsibility_separation"
                            if operation.operation_type == "split_file"
                            else "other"
                        ),
                    },
                )

    def _load_operations(self) -> dict[str, Any]:
        """Load operations from file."""
        if self.operations_file.exists():
            try:
                with open(self.operations_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load operations: {e}")
        return {}

    def _save_operations(self) -> None:
        """Save operations to file."""
        try:
            with open(self.operations_file, "w") as f:
                json.dump(self.operations, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save operations: {e}")

    def _load_todos(self) -> dict[str, Any]:
        """Load TODOs from file."""
        if self.todos_file.exists():
            try:
                with open(self.todos_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load TODOs: {e}")
        return {}

    def _save_todos(self) -> None:
        """Save TODOs to file."""
        try:
            with open(self.todos_file, "w") as f:
                json.dump(self.todos, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save TODOs: {e}")

    def _load_metrics(self) -> dict[str, Any]:
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
        return {}

    def _save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            with open(self.metrics_file, "w") as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_refactoring_statistics(self) -> dict[str, Any]:
        """Get comprehensive refactoring statistics."""
        total_operations = len(self.operations)
        successful_operations = sum(
            1 for op in self.operations.values() if op["success"]
        )
        total_lines_moved = sum(op["lines_moved"] for op in self.operations.values())

        # Calculate average improvements
        complexity_improvements = [
            op["complexity_before"] - op["complexity_after"]
            for op in self.operations.values()
        ]
        avg_complexity_improvement = (
            sum(complexity_improvements) / len(complexity_improvements)
            if complexity_improvements
            else 0
        )

        maintainability_improvements = [
            op["maintainability_after"] - op["maintainability_before"]
            for op in self.operations.values()
        ]
        avg_maintainability_improvement = (
            sum(maintainability_improvements) / len(maintainability_improvements)
            if maintainability_improvements
            else 0
        )

        # TODO statistics
        total_todos = len(self.todos)
        resolved_todos = sum(1 for todo in self.todos.values() if todo["resolved"])

        return {
            "operations": {
                "total": total_operations,
                "successful": successful_operations,
                "success_rate": (
                    (successful_operations / total_operations * 100)
                    if total_operations > 0
                    else 0
                ),
                "total_lines_moved": total_lines_moved,
            },
            "improvements": {
                "average_complexity_reduction": avg_complexity_improvement,
                "average_maintainability_improvement": avg_maintainability_improvement,
            },
            "todos": {
                "total": total_todos,
                "resolved": resolved_todos,
                "resolution_rate": (
                    (resolved_todos / total_todos * 100) if total_todos > 0 else 0
                ),
            },
            "diagrams_generated": len(list(self.diagrams_dir.glob("*.json"))),
        }


def main():
    """Main function for testing the refactoring tracker."""
    tracker = RefactoringTracker(Path.cwd())

    # Example operation
    operation = RefactoringOperation(
        operation_id="test_split_001",
        operation_type="split_file",
        timestamp=datetime.now(),
        source_files=["src/core/enhanced_cli.py"],
        target_files=["src/core/cli_commands.py", "src/core/cli_utils.py"],
        lines_moved=500,
        complexity_before=85.2,
        complexity_after=45.1,
        maintainability_before=42.1,
        maintainability_after=68.3,
        git_commits=["abc123", "def456"],
        success=True,
        rollback_available=True,
        impact_score=0.7,
        user_notes="Split large CLI file into focused modules",
    )

    # Track the operation
    success = tracker.track_refactoring_operation(operation)
    print(f"Operation tracking: {'Success' if success else 'Failed'}")

    # Generate report
    report = tracker.build_refactoring_impact_report(operation.operation_id)
    print("\nOperation Report:")
    print(json.dumps(report, indent=2, default=str))

    # Get statistics
    stats = tracker.get_refactoring_statistics()
    print("\nRefactoring Statistics:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
