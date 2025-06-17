"""Code Intelligence Dashboard - Phase 8.4

This module provides comprehensive analytics and visualizations for the codebase,
including health metrics, dependency graphs, complexity trends, and technical debt tracking.
"""

import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CodebaseHealthMetrics:
    """Comprehensive codebase health metrics."""

    total_files: int
    total_lines: int
    total_classes: int
    total_methods: int
    total_imports: int

    # Complexity metrics
    average_complexity: float
    max_complexity: float
    complexity_distribution: dict[str, int]  # complexity_range -> count

    # Maintainability metrics
    average_maintainability: float
    maintainability_distribution: dict[str, int]  # maintainability_range -> count

    # File size metrics
    average_file_size: float
    large_files_count: int  # files > 1000 lines
    largest_files: list[dict[str, Any]]

    # Technical debt indicators
    technical_debt_score: float
    debt_hotspots: list[dict[str, Any]]
    refactoring_candidates: list[dict[str, Any]]

    # Dependency metrics
    highly_coupled_files: list[dict[str, Any]]
    dependency_depth: dict[str, int]
    circular_dependencies: list[list[str]]

    # Quality trends
    quality_trend: str  # improving, stable, degrading
    change_frequency: dict[str, int]  # file -> change_count

    # Generated timestamp
    generated_at: datetime
    analysis_period_days: int


@dataclass
class DependencyGraphNode:
    """Node in the dependency graph."""

    file_path: str
    complexity: float
    lines: int
    in_degree: int  # number of dependencies
    out_degree: int  # number of dependents
    centrality_score: float
    risk_level: str


@dataclass
class DependencyGraphEdge:
    """Edge in the dependency graph."""

    source: str
    target: str
    relationship_type: str  # imports, calls, inherits
    strength: float  # based on usage frequency


@dataclass
class TechnicalDebtItem:
    """Technical debt item with prioritization."""

    file_path: str
    debt_type: str  # complexity, size, maintainability, duplication
    severity: str  # critical, high, medium, low
    description: str
    impact_score: float
    effort_estimate: str  # hours, days, weeks
    suggested_actions: list[str]
    dependencies: list[str]  # files that depend on this


class CodeIntelligenceDashboard:
    """Main dashboard for code intelligence analytics."""

    def __init__(self, code_manager, git_integration=None):
        """Initialize the dashboard.

        Args:
            code_manager: CodeIntelligenceManager instance
            git_integration: GitIntegration instance for historical data
        """
        self.code_manager = code_manager
        self.git_integration = git_integration

        # Cache for expensive computations
        self._metrics_cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=1)

    def get_codebase_health_metrics(
        self, analysis_period_days: int = 90
    ) -> CodebaseHealthMetrics:
        """Generate comprehensive codebase health metrics."""
        try:
            # Check cache
            cache_key = f"health_metrics_{analysis_period_days}"
            if self._is_cached(cache_key):
                return self._metrics_cache[cache_key]

            # Get basic statistics
            basic_stats = self.code_manager.get_code_statistics()

            # Calculate metrics components
            complexity_dist = self._calculate_complexity_distribution()
            maintainability_dist = self._calculate_maintainability_distribution()
            large_files, largest_files = self._analyze_file_sizes()
            debt_score, debt_hotspots, refactoring_candidates = (
                self._calculate_technical_debt()
            )
            coupled_files, dependency_depth, circular_deps = (
                self._analyze_dependencies()
            )
            quality_trend, change_freq = self._analyze_quality_trends(
                analysis_period_days
            )

            metrics = CodebaseHealthMetrics(
                total_files=basic_stats.get("files", 0),
                total_lines=int(basic_stats.get("total_lines", 0)),
                total_classes=basic_stats.get("classes", 0),
                total_methods=basic_stats.get("methods", 0),
                total_imports=basic_stats.get("imports", 0),
                average_complexity=basic_stats.get("avg_complexity", 0.0),
                max_complexity=basic_stats.get("max_complexity", 0.0),
                complexity_distribution=complexity_dist,
                average_maintainability=basic_stats.get("avg_maintainability", 0.0),
                maintainability_distribution=maintainability_dist,
                average_file_size=basic_stats.get("total_lines", 0)
                / max(basic_stats.get("files", 1), 1),
                large_files_count=large_files,
                largest_files=largest_files,
                technical_debt_score=debt_score,
                debt_hotspots=debt_hotspots,
                refactoring_candidates=refactoring_candidates,
                highly_coupled_files=coupled_files,
                dependency_depth=dependency_depth,
                circular_dependencies=circular_deps,
                quality_trend=quality_trend,
                change_frequency=change_freq,
                generated_at=datetime.now(),
                analysis_period_days=analysis_period_days,
            )

            # Cache the results
            self._cache_metrics(cache_key, metrics)

            return metrics

        except Exception as e:
            logger.error(f"Failed to generate codebase health metrics: {e}")
            return self._empty_health_metrics(analysis_period_days)

    def get_dependency_graph(
        self, max_nodes: int = 50
    ) -> tuple[list[DependencyGraphNode], list[DependencyGraphEdge]]:
        """Generate dependency graph data for visualization."""
        try:
            # Get all files with their dependencies
            files_query = """
            MATCH (f:CodeFile)
            OPTIONAL MATCH (f)-[:DEPENDS_ON]->(dep:CodeFile)
            OPTIONAL MATCH (dependent:CodeFile)-[:DEPENDS_ON]->(f)
            RETURN f.path as file_path,
                   f.complexity as complexity,
                   f.lines as lines,
                   count(DISTINCT dep) as out_degree,
                   count(DISTINCT dependent) as in_degree
            ORDER BY (count(DISTINCT dep) + count(DISTINCT dependent)) DESC
            LIMIT $max_nodes
            """

            file_data = self.code_manager.client.execute_query(
                files_query, {"max_nodes": max_nodes}
            )

            nodes = []
            for file_info in file_data:
                # Calculate centrality score
                centrality = (file_info["in_degree"] + file_info["out_degree"]) / max(
                    len(file_data), 1
                )

                # Determine risk level
                risk_level = self._calculate_file_risk_level(
                    file_info["complexity"], file_info["lines"], file_info["in_degree"]
                )

                node = DependencyGraphNode(
                    file_path=file_info["file_path"],
                    complexity=file_info["complexity"],
                    lines=file_info["lines"],
                    in_degree=file_info["in_degree"],
                    out_degree=file_info["out_degree"],
                    centrality_score=centrality,
                    risk_level=risk_level,
                )
                nodes.append(node)

            # Get edges (relationships)
            edges_query = """
            MATCH (source:CodeFile)-[r:DEPENDS_ON]->(target:CodeFile)
            WHERE source.path IN $file_paths AND target.path IN $file_paths
            RETURN source.path as source,
                   target.path as target,
                   type(r) as relationship_type,
                   coalesce(r.strength, 1.0) as strength
            """

            file_paths = [node.file_path for node in nodes]
            edge_data = self.code_manager.client.execute_query(
                edges_query, {"file_paths": file_paths}
            )

            edges = []
            for edge_info in edge_data:
                edge = DependencyGraphEdge(
                    source=edge_info["source"],
                    target=edge_info["target"],
                    relationship_type=edge_info["relationship_type"],
                    strength=edge_info["strength"],
                )
                edges.append(edge)

            return nodes, edges

        except Exception as e:
            logger.error(f"Failed to generate dependency graph: {e}")
            return [], []

    def _is_cached(self, cache_key: str) -> bool:
        """Check if results are cached and still valid."""
        if cache_key not in self._metrics_cache:
            return False

        if not self._cache_timestamp:
            return False

        return datetime.now() - self._cache_timestamp < self._cache_duration

    def _cache_metrics(self, cache_key: str, metrics: Any):
        """Cache metrics results."""
        self._metrics_cache[cache_key] = metrics
        self._cache_timestamp = datetime.now()

    def _calculate_complexity_distribution(self) -> dict[str, int]:
        """Calculate complexity distribution across files."""
        try:
            complexity_query = """
            MATCH (f:CodeFile)
            RETURN f.complexity as complexity
            """

            complexities = [
                row["complexity"]
                for row in self.code_manager.client.execute_query(complexity_query)
            ]

            distribution = {
                "low (0-10)": len([c for c in complexities if 0 <= c <= 10]),
                "medium (11-25)": len([c for c in complexities if 11 <= c <= 25]),
                "high (26-50)": len([c for c in complexities if 26 <= c <= 50]),
                "very_high (51+)": len([c for c in complexities if c > 50]),
            }

            return distribution

        except Exception:
            return {"low": 0, "medium": 0, "high": 0, "very_high": 0}

    def _calculate_maintainability_distribution(self) -> dict[str, int]:
        """Calculate maintainability distribution across files."""
        try:
            maintainability_query = """
            MATCH (f:CodeFile)
            WHERE f.maintainability_index IS NOT NULL
            RETURN f.maintainability_index as maintainability
            """

            maintainabilities = [
                row["maintainability"]
                for row in self.code_manager.client.execute_query(maintainability_query)
            ]

            distribution = {
                "excellent (80-100)": len(
                    [m for m in maintainabilities if 80 <= m <= 100]
                ),
                "good (60-79)": len([m for m in maintainabilities if 60 <= m < 80]),
                "moderate (40-59)": len([m for m in maintainabilities if 40 <= m < 60]),
                "poor (0-39)": len([m for m in maintainabilities if 0 <= m < 40]),
            }

            return distribution

        except Exception:
            return {"excellent": 0, "good": 0, "moderate": 0, "poor": 0}

    def _analyze_file_sizes(self) -> tuple[int, list[dict[str, Any]]]:
        """Analyze file sizes and identify large files."""
        try:
            large_files_query = """
            MATCH (f:CodeFile)
            WHERE f.lines > 1000
            RETURN count(*) as large_count
            """

            large_count = self.code_manager.client.execute_query(large_files_query)[0][
                "large_count"
            ]

            largest_files_query = """
            MATCH (f:CodeFile)
            RETURN f.path as file_path,
                   f.lines as lines,
                   f.complexity as complexity
            ORDER BY f.lines DESC
            LIMIT 10
            """

            largest_files = self.code_manager.client.execute_query(largest_files_query)

            return large_count, largest_files

        except Exception:
            return 0, []

    def _calculate_technical_debt(
        self,
    ) -> tuple[float, list[dict[str, Any]], list[dict[str, Any]]]:
        """Calculate technical debt score and identify hotspots."""
        try:
            debt_query = """
            MATCH (f:CodeFile)
            RETURN f.path as file_path,
                   f.complexity as complexity,
                   f.maintainability_index as maintainability,
                   f.lines as lines
            """

            files = self.code_manager.client.execute_query(debt_query)

            debt_scores = []
            hotspots = []
            candidates = []

            for file_info in files:
                # Calculate debt score (higher is worse)
                complexity_factor = min(file_info["complexity"] / 50.0, 2.0)
                maintainability_factor = max(
                    0, (100 - file_info["maintainability"]) / 100.0
                )
                size_factor = min(file_info["lines"] / 1000.0, 2.0)

                debt_score = (
                    complexity_factor + maintainability_factor + size_factor
                ) / 3.0
                debt_scores.append(debt_score)

                # Identify hotspots (high debt)
                if debt_score > 0.7:
                    hotspots.append(
                        {
                            "file_path": file_info["file_path"],
                            "debt_score": debt_score,
                            "primary_issues": self._identify_primary_issues(file_info),
                        }
                    )

                # Identify refactoring candidates
                elif 0.4 < debt_score <= 0.7:
                    candidates.append(
                        {
                            "file_path": file_info["file_path"],
                            "debt_score": debt_score,
                            "improvement_potential": "medium",
                        }
                    )

            overall_debt_score = statistics.mean(debt_scores) if debt_scores else 0.0

            return overall_debt_score, hotspots[:10], candidates[:15]

        except Exception:
            return 0.0, [], []

    def _analyze_dependencies(
        self,
    ) -> tuple[list[dict[str, Any]], dict[str, int], list[list[str]]]:
        """Analyze dependency patterns and coupling."""
        try:
            # Highly coupled files
            coupling_query = """
            MATCH (f:CodeFile)
            OPTIONAL MATCH (f)-[:DEPENDS_ON]->(dep:CodeFile)
            OPTIONAL MATCH (dependent:CodeFile)-[:DEPENDS_ON]->(f)
            WITH f, count(DISTINCT dep) as out_degree, count(DISTINCT dependent) as in_degree
            WHERE out_degree + in_degree > 10
            RETURN f.path as file_path,
                   out_degree,
                   in_degree,
                   out_degree + in_degree as total_coupling
            ORDER BY total_coupling DESC
            LIMIT 10
            """

            highly_coupled = self.code_manager.client.execute_query(coupling_query)

            # Dependency depth analysis
            depth_query = """
            MATCH (f:CodeFile)
            OPTIONAL MATCH path = (f)-[:DEPENDS_ON*1..5]->(dep:CodeFile)
            RETURN f.path as file_path,
                   length(path) as max_depth
            ORDER BY max_depth DESC
            """

            depth_data = self.code_manager.client.execute_query(depth_query)
            dependency_depth = {
                row["file_path"]: row["max_depth"] or 0 for row in depth_data
            }

            return highly_coupled, dependency_depth, []

        except Exception:
            return [], {}, []

    def _analyze_quality_trends(self, days: int) -> tuple[str, dict[str, int]]:
        """Analyze quality trends over time."""
        return "stable", {}

    def _calculate_file_risk_level(
        self, complexity: float, lines: int, dependents: int
    ) -> str:
        """Calculate risk level for a file."""
        risk_score = 0

        if complexity > 50:
            risk_score += 2
        elif complexity > 25:
            risk_score += 1

        if lines > 1500:
            risk_score += 2
        elif lines > 1000:
            risk_score += 1

        if dependents > 10:
            risk_score += 2
        elif dependents > 5:
            risk_score += 1

        if risk_score >= 4:
            return "critical"
        elif risk_score >= 3:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def _identify_primary_issues(self, file_info: dict[str, Any]) -> list[str]:
        """Identify primary issues with a file."""
        issues = []

        if file_info["complexity"] > 75:
            issues.append("very_high_complexity")

        if file_info["lines"] > 1500:
            issues.append("large_file_size")

        if file_info["maintainability"] < 40:
            issues.append("low_maintainability")

        return issues

    def _empty_health_metrics(self, analysis_period_days: int) -> CodebaseHealthMetrics:
        """Return empty health metrics structure."""
        return CodebaseHealthMetrics(
            total_files=0,
            total_lines=0,
            total_classes=0,
            total_methods=0,
            total_imports=0,
            average_complexity=0.0,
            max_complexity=0.0,
            complexity_distribution={},
            average_maintainability=0.0,
            maintainability_distribution={},
            average_file_size=0.0,
            large_files_count=0,
            largest_files=[],
            technical_debt_score=0.0,
            debt_hotspots=[],
            refactoring_candidates=[],
            highly_coupled_files=[],
            dependency_depth={},
            circular_dependencies=[],
            quality_trend="unknown",
            change_frequency={},
            generated_at=datetime.now(),
            analysis_period_days=analysis_period_days,
        )
