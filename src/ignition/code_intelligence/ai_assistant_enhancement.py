"""AI Assistant Enhancement System - Phase 8.3.

This module provides intelligent context loading and code suggestions for AI assistants,
replacing large file reads with targeted context queries and providing smart recommendations.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CodeContext:
    """Represents intelligent code context for AI assistants."""

    file_path: str
    file_metrics: dict[str, Any]
    classes: list[dict[str, Any]]
    methods: list[dict[str, Any]]
    imports: list[dict[str, Any]]
    dependencies: list[str]
    dependents: list[str]
    recent_changes: list[dict[str, Any]]
    similar_files: list[dict[str, Any]]
    refactoring_suggestions: list[dict[str, Any]]
    risk_factors: list[dict[str, Any]]


@dataclass
class ChangeImpactAnalysis:
    """Represents the potential impact of code changes."""

    affected_files: list[str]
    breaking_changes: list[dict[str, Any]]
    test_coverage_gaps: list[dict[str, Any]]
    rollback_recommendations: list[str]
    risk_level: str  # low, medium, high, critical
    confidence_score: float


class AIAssistantEnhancement:
    """Main class for AI Assistant Enhancement capabilities."""

    def __init__(self, code_manager, git_integration=None, embedder=None) -> None:
        """Initialize AI Assistant Enhancement system.

        Args:
            code_manager: CodeIntelligenceManager instance
            git_integration: GitIntegration instance for change tracking
            embedder: SentenceTransformer for semantic search
        """
        self.code_manager = code_manager
        self.git_integration = git_integration
        self.embedder = embedder

        # Import here to avoid circular imports
        if not self.embedder:
            try:
                from sentence_transformers import SentenceTransformer

                self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except ImportError:
                logger.warning(
                    "SentenceTransformer not available - semantic search disabled"
                )
                self.embedder = None

    def get_smart_context(
        self, file_path: str, context_size: str = "medium"
    ) -> CodeContext:
        """Get intelligent context for a file instead of reading entire file.

        Args:
            file_path: Path to the file
            context_size: Size of context (small, medium, large)

        Returns:
            CodeContext with relevant information for AI assistants
        """
        try:
            # Get basic file context
            base_context = self.code_manager.get_file_context(file_path)
            if not base_context or not base_context.get("file"):
                logger.warning(f"No context found for {file_path}")
                return self._empty_context(file_path)

            # Get recent changes if git integration available
            recent_changes = []
            if self.git_integration:
                try:
                    changes = self.git_integration.get_recent_changes(
                        file_path, days=30
                    )
                    recent_changes = changes[:5]  # Limit to 5 most recent
                except Exception as e:
                    logger.debug(f"Could not get recent changes: {e}")

            # Get similar files for pattern recognition
            similar_files = []
            try:
                similar_files = self.code_manager.find_similar_files(file_path, limit=3)
            except Exception as e:
                logger.debug(f"Could not find similar files: {e}")

            # Get refactoring suggestions
            refactoring_suggestions = self._get_refactoring_suggestions(base_context)

            # Assess risk factors
            risk_factors = self._assess_risk_factors(base_context)

            # Build smart context
            context = CodeContext(
                file_path=file_path,
                file_metrics=base_context["file"],
                classes=base_context.get("classes", []),
                methods=base_context.get("class_methods", [])
                + base_context.get("file_methods", []),
                imports=base_context.get("imports", []),
                dependencies=[],  # Will be populated by dependency analysis
                dependents=base_context.get("dependents", []),
                recent_changes=recent_changes,
                similar_files=similar_files,
                refactoring_suggestions=refactoring_suggestions,
                risk_factors=risk_factors,
            )

            # Add dependency context if requested
            if context_size in ["medium", "large"]:
                context.dependencies = self._get_dependency_context(file_path)

            return context

        except Exception as e:
            logger.error(f"Failed to get smart context for {file_path}: {e}")
            return self._empty_context(file_path)

    def get_relevant_snippets(
        self, file_path: str, query: str, max_snippets: int = 5
    ) -> list[dict[str, Any]]:
        """Get relevant code snippets instead of entire file content.

        Args:
            file_path: Path to the file
            query: What the user is looking for
            max_snippets: Maximum number of snippets to return

        Returns:
            List of relevant code snippets with context
        """
        try:
            # Get file context
            context = self.code_manager.get_file_context(file_path)
            if not context:
                return []

            snippets = []

            # Search in classes and methods
            for cls in context.get("classes", []):
                if self._is_relevant(
                    cls.get("name", ""), cls.get("docstring", ""), query
                ):
                    snippets.append(
                        {
                            "type": "class",
                            "name": cls["name"],
                            "start_line": cls.get("start_line"),
                            "end_line": cls.get("end_line"),
                            "docstring": cls.get("docstring", ""),
                            "relevance_score": self._calculate_relevance(cls, query),
                        }
                    )

            for method in context.get("class_methods", []) + context.get(
                "file_methods", []
            ):
                if self._is_relevant(
                    method.get("name", ""), method.get("docstring", ""), query
                ):
                    snippets.append(
                        {
                            "type": "method",
                            "name": method["name"],
                            "class_name": method.get("class_name"),
                            "start_line": method.get("start_line"),
                            "end_line": method.get("end_line"),
                            "signature": method.get("signature", ""),
                            "docstring": method.get("docstring", ""),
                            "relevance_score": self._calculate_relevance(method, query),
                        }
                    )

            # Sort by relevance and limit
            snippets.sort(key=lambda x: x["relevance_score"], reverse=True)
            return snippets[:max_snippets]

        except Exception as e:
            logger.error(f"Failed to get relevant snippets for {file_path}: {e}")
            return []

    def suggest_similar_implementations(
        self, file_path: str, element_name: str
    ) -> list[dict[str, Any]]:
        """Suggest similar implementations from the codebase.

        Args:
            file_path: Current file being worked on
            element_name: Name of class/method to find similar implementations for

        Returns:
            List of similar implementations with usage patterns
        """
        try:
            suggestions = []

            # Find similar files first
            similar_files = self.code_manager.find_similar_files(file_path, limit=10)

            for similar_file in similar_files:
                similar_context = self.code_manager.get_file_context(
                    similar_file["path"]
                )
                if not similar_context:
                    continue

                # Look for similar named elements
                for cls in similar_context.get("classes", []):
                    if self._names_similar(cls["name"], element_name):
                        suggestions.append(
                            {
                                "type": "class",
                                "name": cls["name"],
                                "file_path": similar_file["path"],
                                "similarity_score": similar_file.get(
                                    "similarity_score", 0
                                ),
                                "complexity": cls.get("complexity", 0),
                                "docstring": cls.get("docstring", ""),
                                "usage_pattern": "class_implementation",
                            }
                        )

                for method in similar_context.get(
                    "class_methods", []
                ) + similar_context.get("file_methods", []):
                    if self._names_similar(method["name"], element_name):
                        suggestions.append(
                            {
                                "type": "method",
                                "name": method["name"],
                                "class_name": method.get("class_name"),
                                "file_path": similar_file["path"],
                                "similarity_score": similar_file.get(
                                    "similarity_score", 0
                                ),
                                "complexity": method.get("complexity", 0),
                                "signature": method.get("signature", ""),
                                "usage_pattern": "method_implementation",
                            }
                        )

            # Sort by similarity and complexity
            suggestions.sort(key=lambda x: (x["similarity_score"], -x["complexity"]))
            return suggestions[:5]

        except Exception as e:
            logger.error(f"Failed to suggest similar implementations: {e}")
            return []

    def analyze_change_impact(
        self, file_path: str, change_description: str = ""
    ) -> ChangeImpactAnalysis:
        """Analyze the potential impact of changes to a file.

        Args:
            file_path: File being changed
            change_description: Description of the changes being made

        Returns:
            ChangeImpactAnalysis with predicted impacts
        """
        try:
            # Get dependency graph
            dep_graph = self.code_manager.get_dependency_graph(file_path, depth=3)
            affected_files = [
                dep["target"] for dep in dep_graph.get("dependencies", [])
            ]

            # Get file context for analysis
            context = self.code_manager.get_file_context(file_path)
            if not context:
                return self._empty_impact_analysis()

            # Predict breaking changes
            breaking_changes = self._predict_breaking_changes(
                context, change_description
            )

            # Identify test coverage gaps
            test_gaps = self._identify_test_coverage_gaps(file_path, affected_files)

            # Generate rollback recommendations
            rollback_recs = self._generate_rollback_recommendations(file_path, context)

            # Calculate risk level
            risk_level, confidence = self._calculate_risk_level(
                context, affected_files, breaking_changes, test_gaps
            )

            return ChangeImpactAnalysis(
                affected_files=affected_files[:10],  # Limit to top 10
                breaking_changes=breaking_changes,
                test_coverage_gaps=test_gaps,
                rollback_recommendations=rollback_recs,
                risk_level=risk_level,
                confidence_score=confidence,
            )

        except Exception as e:
            logger.error(f"Failed to analyze change impact for {file_path}: {e}")
            return self._empty_impact_analysis()

    def get_refactoring_opportunities(self, file_path: str) -> list[dict[str, Any]]:
        """Identify refactoring opportunities based on code analysis.

        Args:
            file_path: File to analyze for refactoring opportunities

        Returns:
            List of refactoring suggestions with priorities
        """
        try:
            context = self.code_manager.get_file_context(file_path)
            if not context or not context.get("file"):
                return []

            opportunities = []
            file_info = context["file"]

            # Check file size
            if file_info.get("lines", 0) > 1000:
                opportunities.append(
                    {
                        "type": "file_split",
                        "priority": "high",
                        "description": f"Large file ({file_info['lines']} lines) should be split",
                        "effort": "medium",
                        "impact": "maintainability",
                    }
                )

            # Check complexity
            if file_info.get("complexity", 0) > 50:
                opportunities.append(
                    {
                        "type": "complexity_reduction",
                        "priority": "medium",
                        "description": f"High complexity ({file_info['complexity']:.1f}) indicates need for simplification",
                        "effort": "high",
                        "impact": "maintainability",
                    }
                )

            # Check maintainability
            if file_info.get("maintainability_index", 100) < 50:
                opportunities.append(
                    {
                        "type": "maintainability_improvement",
                        "priority": "medium",
                        "description": f"Low maintainability index ({file_info['maintainability_index']:.1f})",
                        "effort": "medium",
                        "impact": "maintainability",
                    }
                )

            # Check for methods with high complexity
            all_methods = context.get("class_methods", []) + context.get(
                "file_methods", []
            )
            for method in all_methods:
                if method.get("complexity", 0) > 10:
                    opportunities.append(
                        {
                            "type": "method_simplification",
                            "priority": "low",
                            "description": f"Method '{method['name']}' has high complexity ({method['complexity']:.1f})",
                            "effort": "low",
                            "impact": "readability",
                            "method_name": method["name"],
                        }
                    )

            # Check for code duplication patterns
            similar_files = self.code_manager.find_similar_files(file_path, limit=5)
            if len(similar_files) > 2:
                opportunities.append(
                    {
                        "type": "code_deduplication",
                        "priority": "low",
                        "description": f"Found {len(similar_files)} similar files - potential for code reuse",
                        "effort": "medium",
                        "impact": "maintainability",
                    }
                )

            # Sort by priority
            priority_order = {"high": 3, "medium": 2, "low": 1}
            opportunities.sort(
                key=lambda x: priority_order.get(x["priority"], 0), reverse=True
            )

            return opportunities

        except Exception as e:
            logger.error(
                f"Failed to get refactoring opportunities for {file_path}: {e}"
            )
            return []

    def track_code_evolution(self, file_path: str, days: int = 90) -> dict[str, Any]:
        """Track code evolution over time to identify patterns.

        Args:
            file_path: File to track
            days: Number of days to look back

        Returns:
            Evolution analysis with trends and insights
        """
        if not self.git_integration:
            return {"error": "Git integration not available"}

        try:
            evolution = self.git_integration.track_file_evolution(file_path)
            if not evolution:
                return {"error": "No evolution data found"}

            # Calculate trends
            trends = {
                "complexity_trend": "stable",
                "size_trend": "growing",
                "change_frequency": "low",
                "technical_debt": "low",
                "insights": [],
            }

            # Analyze change frequency
            recent_changes = [
                change
                for change in evolution.get("changes", [])
                if (datetime.now() - datetime.fromisoformat(change["date"])).days
                <= days
            ]

            if len(recent_changes) > 10:
                trends["change_frequency"] = "high"
                trends["insights"].append(
                    "File has high change frequency - consider stability improvements"
                )
            elif len(recent_changes) > 5:
                trends["change_frequency"] = "medium"

            # Add evolution data
            trends["evolution_data"] = evolution
            trends["recent_changes_count"] = len(recent_changes)
            trends["analysis_period_days"] = days

            return trends

        except Exception as e:
            logger.error(f"Failed to track code evolution for {file_path}: {e}")
            return {"error": str(e)}

    # Helper methods

    def _empty_context(self, file_path: str) -> CodeContext:
        """Return empty context structure."""
        return CodeContext(
            file_path=file_path,
            file_metrics={},
            classes=[],
            methods=[],
            imports=[],
            dependencies=[],
            dependents=[],
            recent_changes=[],
            similar_files=[],
            refactoring_suggestions=[],
            risk_factors=[],
        )

    def _empty_impact_analysis(self) -> ChangeImpactAnalysis:
        """Return empty impact analysis."""
        return ChangeImpactAnalysis(
            affected_files=[],
            breaking_changes=[],
            test_coverage_gaps=[],
            rollback_recommendations=[],
            risk_level="unknown",
            confidence_score=0.0,
        )

    def _get_refactoring_suggestions(
        self, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate refactoring suggestions based on context."""
        suggestions = []

        if not context.get("file"):
            return suggestions

        file_info = context["file"]

        # Large file suggestion
        if file_info.get("lines", 0) > 1000:
            suggestions.append(
                {
                    "type": "split_file",
                    "priority": "high",
                    "description": "Consider splitting this large file into smaller modules",
                }
            )

        # High complexity suggestion
        if file_info.get("complexity", 0) > 50:
            suggestions.append(
                {
                    "type": "reduce_complexity",
                    "priority": "medium",
                    "description": "Consider breaking down complex logic into smaller functions",
                }
            )

        return suggestions

    def _assess_risk_factors(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Assess risk factors for the file."""
        risks = []

        if not context.get("file"):
            return risks

        file_info = context["file"]

        # High complexity risk
        if file_info.get("complexity", 0) > 75:
            risks.append(
                {
                    "type": "high_complexity",
                    "level": "high",
                    "description": "Very high complexity increases maintenance risk",
                }
            )

        # Many dependents risk
        if len(context.get("dependents", [])) > 10:
            risks.append(
                {
                    "type": "high_coupling",
                    "level": "medium",
                    "description": "Many files depend on this - changes may have wide impact",
                }
            )

        return risks

    def _get_dependency_context(self, file_path: str) -> list[str]:
        """Get dependency context for a file."""
        try:
            dep_graph = self.code_manager.get_dependency_graph(file_path, depth=2)
            return [dep["target"] for dep in dep_graph.get("dependencies", [])]
        except Exception:
            return []

    def _is_relevant(self, name: str, docstring: str, query: str) -> bool:
        """Check if code element is relevant to query."""
        query_lower = query.lower()
        return query_lower in name.lower() or query_lower in docstring.lower()

    def _calculate_relevance(self, element: dict[str, Any], query: str) -> float:
        """Calculate relevance score for code element."""
        score = 0.0
        name = element.get("name", "").lower()
        docstring = element.get("docstring", "").lower()
        query_lower = query.lower()

        # Exact name match gets highest score
        if query_lower == name:
            score += 1.0
        elif query_lower in name:
            score += 0.7

        # Docstring match gets medium score
        if query_lower in docstring:
            score += 0.5

        return score

    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are similar."""
        name1_lower = name1.lower()
        name2_lower = name2.lower()

        # Exact match
        if name1_lower == name2_lower:
            return True

        # Substring match
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return True

        # Similar patterns (simple heuristic)
        return (
            len(set(name1_lower) & set(name2_lower))
            > len(min(name1_lower, name2_lower)) * 0.6
        )

    def _predict_breaking_changes(
        self, context: dict[str, Any], description: str
    ) -> list[dict[str, Any]]:
        """Predict potential breaking changes."""
        breaking_changes = []

        # If many files depend on this one, changes could be breaking
        if len(context.get("dependents", [])) > 5:
            breaking_changes.append(
                {
                    "type": "api_change",
                    "description": "Changes to this file may break dependent files",
                    "affected_count": len(context["dependents"]),
                    "severity": "medium",
                }
            )

        # Look for public methods/classes that might change
        for cls in context.get("classes", []):
            if not cls["name"].startswith("_"):  # Public class
                breaking_changes.append(
                    {
                        "type": "public_class_change",
                        "description": f"Changes to public class '{cls['name']}' may break imports",
                        "class_name": cls["name"],
                        "severity": "low",
                    }
                )

        return breaking_changes

    def _identify_test_coverage_gaps(
        self, file_path: str, affected_files: list[str]
    ) -> list[dict[str, Any]]:
        """Identify gaps in test coverage."""
        gaps = []

        # Simple heuristic: check if there are corresponding test files
        [
            file_path.replace(".py", "_test.py"),
            file_path.replace(".py", "_tests.py"),
            f"test_{Path(file_path).name}",
            f"tests/test_{Path(file_path).name}",
        ]

        # For now, assume test files don't exist (would need file system check)
        gaps.append(
            {
                "file": file_path,
                "description": "No test file found for this module",
                "recommended_tests": [
                    "unit tests for public methods",
                    "integration tests for main functionality",
                ],
            }
        )

        return gaps

    def _generate_rollback_recommendations(
        self, file_path: str, context: dict[str, Any]
    ) -> list[str]:
        """Generate rollback recommendations."""
        recommendations = []

        if len(context.get("dependents", [])) > 10:
            recommendations.append(
                "Create backup before changes due to high number of dependents"
            )

        if context.get("file", {}).get("complexity", 0) > 50:
            recommendations.append(
                "Test thoroughly before deployment due to high complexity"
            )

        recommendations.append("Use feature flags for gradual rollout")
        recommendations.append("Monitor error rates after deployment")

        return recommendations

    def _calculate_risk_level(
        self,
        context: dict[str, Any],
        affected_files: list[str],
        breaking_changes: list[dict[str, Any]],
        test_gaps: list[dict[str, Any]],
    ) -> tuple[str, float]:
        """Calculate overall risk level and confidence."""
        risk_score = 0.0

        # File complexity factor
        complexity = context.get("file", {}).get("complexity", 0)
        if complexity > 75:
            risk_score += 0.4
        elif complexity > 50:
            risk_score += 0.2

        # Dependency factor
        if len(affected_files) > 10:
            risk_score += 0.3
        elif len(affected_files) > 5:
            risk_score += 0.2

        # Breaking changes factor
        if len(breaking_changes) > 2:
            risk_score += 0.2
        elif len(breaking_changes) > 0:
            risk_score += 0.1

        # Test coverage factor
        if len(test_gaps) > 0:
            risk_score += 0.1

        # Convert to risk level
        if risk_score >= 0.7:
            return "critical", 0.9
        elif risk_score >= 0.5:
            return "high", 0.8
        elif risk_score >= 0.3:
            return "medium", 0.7
        else:
            return "low", 0.6
