"""Code Intelligence Integration for Script Generation Module.

This module integrates existing code intelligence capabilities including
vector embeddings, semantic search, and AI-powered recommendations.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.ignition.code_intelligence.analyzer import CodeAnalyzer
from src.ignition.code_intelligence.embeddings import CodeEmbeddingGenerator, SemanticCodeSearch
from src.ignition.code_intelligence.refactor_analyzer import RefactoringRecommendationEngine
from src.ignition.graph.client import IgnitionGraphClient


@dataclass
class CodeSuggestion:
    """A code suggestion from the intelligence system."""

    type: str  # "function", "pattern", "best_practice", "refactoring"
    title: str
    description: str
    code_snippet: str | None = None
    relevance_score: float = 1.0
    source: str = "code_intelligence"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAssessment:
    """Quality assessment for generated script."""

    overall_score: float
    complexity_score: float
    maintainability_score: float
    issues: list[dict[str, Any]] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticSearchResult:
    """Result from semantic code search."""

    file_path: str
    function_name: str | None
    code_snippet: str
    similarity_score: float
    context: dict[str, Any] = field(default_factory=dict)


class CodeIntelligenceIntegration:
    """Integration layer for code intelligence in script generation."""

    def __init__(
        self,
        graph_client: IgnitionGraphClient | None = None,
        embeddings_dir: str | Path = ".embeddings",
        enable_ai_suggestions: bool = True,
        enable_quality_analysis: bool = True,
        enable_refactoring_suggestions: bool = True,
    ) -> None:
        """Initialize code intelligence integration.

        Args:
            graph_client: Optional Neo4j graph client
            embeddings_dir: Directory for vector embeddings
            enable_ai_suggestions: Whether to enable AI suggestions
            enable_quality_analysis: Whether to enable quality analysis
            enable_refactoring_suggestions: Whether to enable refactoring suggestions
        """
        self.graph_client = graph_client
        self.embeddings_dir = Path(embeddings_dir)
        self.enable_ai_suggestions = enable_ai_suggestions
        self.enable_quality_analysis = enable_quality_analysis
        self.enable_refactoring_suggestions = enable_refactoring_suggestions

        # Initialize components
        self._init_components()

        # Logger
        self.logger = logging.getLogger(__name__)

    def _init_components(self) -> None:
        """Initialize code intelligence components."""
        # Code embeddings
        if self.enable_ai_suggestions:
            self.embedding_generator = CodeEmbeddingGenerator()
            self.semantic_search = (
                SemanticCodeSearch(self.graph_client, self.embedding_generator) if self.graph_client else None
            )
        else:
            self.embedding_generator = None
            self.semantic_search = None

        # Quality analyzer
        if self.enable_quality_analysis:
            self.quality_analyzer = CodeAnalyzer()
        else:
            self.quality_analyzer = None

        # Refactoring analyzer
        if self.enable_refactoring_suggestions:
            self.refactoring_analyzer = RefactoringRecommendationEngine()
        else:
            self.refactoring_analyzer = None

    def search_similar_scripts(
        self,
        query: str,
        script_context: str | None = None,
        limit: int = 5,
    ) -> list[SemanticSearchResult]:
        """Search for similar scripts using semantic search.

        Args:
            query: Search query (natural language or code snippet)
            script_context: Optional script context filter
            limit: Maximum results to return

        Returns:
            List of semantic search results
        """
        results = []

        if not self.semantic_search:
            return results

        try:
            # Perform semantic search
            search_results = self.semantic_search.find_similar_code(
                query=query,
                limit=limit * 2,  # Get more results for filtering
            )

            # Filter by context if provided
            for result in search_results:
                if script_context and script_context not in result.get("context", ""):
                    continue

                results.append(
                    SemanticSearchResult(
                        file_path=result.get("file_path", ""),
                        function_name=result.get("function_name"),
                        code_snippet=result.get("code_snippet", ""),
                        similarity_score=result.get("similarity_score", 0.0),
                        context=result.get("metadata", {}),
                    )
                )

                if len(results) >= limit:
                    break

        except Exception as e:
            self.logger.warning(f"Failed to search similar scripts: {e}")

        return results

    def get_ai_suggestions(
        self,
        template_name: str,
        parameters: dict[str, Any],
        context: str,
    ) -> list[CodeSuggestion]:
        """Get AI-powered suggestions for script generation.

        Args:
            template_name: Template being used
            parameters: Template parameters
            context: Script execution context

        Returns:
            List of code suggestions
        """
        suggestions = []

        if not self.enable_ai_suggestions or not self.graph_client:
            return suggestions

        try:
            # Get function suggestions from graph
            function_suggestions = self._get_function_suggestions(template_name, context)
            suggestions.extend(function_suggestions)

            # Get pattern suggestions
            pattern_suggestions = self._get_pattern_suggestions(template_name, parameters)
            suggestions.extend(pattern_suggestions)

            # Get best practice suggestions
            best_practices = self._get_best_practices(context)
            suggestions.extend(best_practices)

            # Sort by relevance
            suggestions.sort(key=lambda x: x.relevance_score, reverse=True)

        except Exception as e:
            self.logger.warning(f"Failed to get AI suggestions: {e}")

        return suggestions[:10]  # Limit to top 10 suggestions

    def _get_function_suggestions(self, template_name: str, context: str) -> list[CodeSuggestion]:
        """Get function suggestions from graph.

        Args:
            template_name: Template name
            context: Script context

        Returns:
            List of function suggestions
        """
        suggestions = []

        if not self.graph_client:
            return suggestions

        try:
            query = """
            MATCH (t:Template {name: $template_name})-[:USES_FUNCTION]->(f:Function)
            WHERE f.context = $context OR f.context = 'all'
            RETURN f.name as function_name,
                   f.description as description,
                   f.example as example,
                   f.module as module
            LIMIT 5
            """

            results = self.graph_client.execute_query(query, {"template_name": template_name, "context": context})

            for record in results:
                function_name = record.get("function_name", "")
                module = record.get("module", "system")

                suggestions.append(
                    CodeSuggestion(
                        type="function",
                        title=f"Use {module}.{function_name}",
                        description=record.get("description", ""),
                        code_snippet=record.get("example"),
                        relevance_score=5.0,
                        source="function_graph",
                        metadata={
                            "module": module,
                            "function": function_name,
                        },
                    )
                )

        except Exception as e:
            self.logger.warning(f"Failed to get function suggestions: {e}")

        return suggestions

    def _get_pattern_suggestions(self, template_name: str, parameters: dict[str, Any]) -> list[CodeSuggestion]:
        """Get pattern suggestions based on parameters.

        Args:
            template_name: Template name
            parameters: Template parameters

        Returns:
            List of pattern suggestions
        """
        suggestions = []

        # Suggest error handling pattern if not present
        if not parameters.get("enable_error_handling"):
            suggestions.append(
                CodeSuggestion(
                    type="pattern",
                    title="Add Error Handling",
                    description="Wrap critical operations in try-except blocks",
                    code_snippet="""try:
    # Your code here
    result = system.tag.readBlocking([tagPath])[0]
    if result.quality.isGood():
        return result.value
except Exception as e:
    system.util.getLogger("Script").error("Error: %s" % str(e))
    return None""",
                    relevance_score=4.0,
                    source="pattern_library",
                )
            )

        # Suggest logging pattern if not present
        if not parameters.get("enable_logging"):
            suggestions.append(
                CodeSuggestion(
                    type="pattern",
                    title="Add Logging",
                    description="Add logging for debugging and monitoring",
                    code_snippet="""logger = system.util.getLogger("ScriptName")
logger.info("Script started")
# Your code here
logger.info("Script completed successfully")""",
                    relevance_score=3.5,
                    source="pattern_library",
                )
            )

        # Suggest validation pattern
        if "tag" in template_name.lower() and not parameters.get("enable_validation"):
            suggestions.append(
                CodeSuggestion(
                    type="pattern",
                    title="Add Tag Validation",
                    description="Validate tag paths and values before operations",
                    code_snippet="""def validateTagPath(tagPath):
    if not tagPath or not tagPath.startswith("["):
        raise ValueError("Invalid tag path: %s" % tagPath)
    return True

# Validate before use
if validateTagPath(tagPath):
    # Proceed with tag operation""",
                    relevance_score=3.0,
                    source="pattern_library",
                )
            )

        return suggestions

    def _get_best_practices(self, context: str) -> list[CodeSuggestion]:
        """Get best practice suggestions for context.

        Args:
            context: Script context

        Returns:
            List of best practice suggestions
        """
        suggestions = []

        if not self.graph_client:
            return suggestions

        try:
            query = """
            MATCH (bp:BestPractice)-[:APPLIES_TO]->(c:Context {name: $context})
            RETURN bp.title as title,
                   bp.description as description,
                   bp.example as example,
                   bp.priority as priority
            ORDER BY bp.priority DESC
            LIMIT 3
            """

            results = self.graph_client.execute_query(query, {"context": context})

            for record in results:
                suggestions.append(
                    CodeSuggestion(
                        type="best_practice",
                        title=record.get("title", ""),
                        description=record.get("description", ""),
                        code_snippet=record.get("example"),
                        relevance_score=float(record.get("priority", 1.0)),
                        source="best_practices",
                    )
                )

        except Exception as e:
            self.logger.warning(f"Failed to get best practices: {e}")

        return suggestions

    def analyze_script_quality(self, script_content: str) -> QualityAssessment:
        """Analyze the quality of generated script.

        Args:
            script_content: Generated script content

        Returns:
            Quality assessment with scores and suggestions
        """
        if not self.enable_quality_analysis or not self.quality_analyzer:
            return QualityAssessment(
                overall_score=1.0,
                complexity_score=1.0,
                maintainability_score=1.0,
            )

        try:
            # Analyze code quality
            # Create a temporary file for analysis
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(script_content)
                temp_path = Path(f.name)

            analysis = self.quality_analyzer.analyze_file(temp_path)
            temp_path.unlink()  # Clean up temp file

            # Extract metrics
            metrics = analysis.get("metrics", {})
            complexity = metrics.get("complexity", 1)
            lines = metrics.get("lines_of_code", 1)

            # Calculate scores (0-1 scale)
            complexity_score = max(0, 1 - (complexity - 10) / 20) if complexity > 10 else 1.0
            maintainability_score = max(0, 1 - (lines - 50) / 100) if lines > 50 else 1.0

            # Overall score
            overall_score = (complexity_score + maintainability_score) / 2

            # Extract issues and suggestions
            issues = analysis.get("issues", [])
            suggestions = []

            for issue in issues:
                if issue.get("severity") in ["high", "critical"]:
                    suggestions.append(issue.get("message", ""))

            return QualityAssessment(
                overall_score=overall_score,
                complexity_score=complexity_score,
                maintainability_score=maintainability_score,
                issues=issues,
                suggestions=suggestions[:5],  # Limit suggestions
                metrics=metrics,
            )

        except Exception as e:
            self.logger.warning(f"Failed to analyze script quality: {e}")
            return QualityAssessment(
                overall_score=0.8,
                complexity_score=0.8,
                maintainability_score=0.8,
            )

    def get_refactoring_suggestions(self, script_content: str, max_suggestions: int = 3) -> list[CodeSuggestion]:
        """Get refactoring suggestions for script.

        Args:
            script_content: Script content to analyze
            max_suggestions: Maximum suggestions to return

        Returns:
            List of refactoring suggestions
        """
        suggestions = []

        if not self.enable_refactoring_suggestions or not self.refactoring_analyzer:
            return suggestions

        try:
            # Analyze for refactoring opportunities
            opportunities = self.refactoring_analyzer.analyze_code(script_content)

            for opp in opportunities[:max_suggestions]:
                suggestions.append(
                    CodeSuggestion(
                        type="refactoring",
                        title=opp.get("title", "Refactoring Suggestion"),
                        description=opp.get("description", ""),
                        code_snippet=opp.get("suggested_code"),
                        relevance_score=float(opp.get("impact", 1.0)),
                        source="refactoring_analyzer",
                        metadata={
                            "type": opp.get("refactoring_type"),
                            "complexity_reduction": opp.get("complexity_reduction", 0),
                        },
                    )
                )

        except Exception as e:
            self.logger.warning(f"Failed to get refactoring suggestions: {e}")

        return suggestions

    def validate_script_context(self, script_content: str, expected_context: str) -> tuple[bool, list[str]]:
        """Validate script is appropriate for context.

        Args:
            script_content: Script content to validate
            expected_context: Expected execution context

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Context-specific validation rules
        context_rules = {
            "gateway": {
                "forbidden": ["system.gui", "system.nav", "event.source"],
                "required": [],
            },
            "vision": {
                "forbidden": ["system.perspective"],
                "required": [],
            },
            "perspective": {
                "forbidden": ["system.gui", "system.nav"],
                "required": [],
            },
            "tag": {
                "forbidden": ["system.gui", "system.nav", "system.perspective"],
                "required": ["currentValue", "previousValue"],
            },
        }

        rules = context_rules.get(expected_context, {})

        # Check for forbidden elements
        for forbidden in rules.get("forbidden", []):
            if forbidden in script_content:
                issues.append(f"'{forbidden}' is not available in {expected_context} context")

        # Check for required elements in tag scripts
        if expected_context == "tag":
            for required in rules.get("required", []):
                if required not in script_content:
                    issues.append(f"Tag scripts should reference '{required}'")

        return len(issues) == 0, issues

    def enhance_script_with_intelligence(
        self,
        script_content: str,
        context: str,
        parameters: dict[str, Any],
    ) -> str:
        """Enhance script with code intelligence features.

        Args:
            script_content: Original script content
            context: Script execution context
            parameters: Script parameters

        Returns:
            Enhanced script content
        """
        enhanced = script_content

        try:
            # Add intelligent imports based on usage
            enhanced = self._add_intelligent_imports(enhanced, context)

            # Add performance optimizations
            if parameters.get("optimize_performance", False):
                enhanced = self._add_performance_optimizations(enhanced)

            # Add debugging helpers
            if parameters.get("debug_mode", False):
                enhanced = self._add_debug_helpers(enhanced)

        except Exception as e:
            self.logger.warning(f"Failed to enhance script: {e}")

        return enhanced

    def _add_intelligent_imports(self, script_content: str, context: str) -> str:
        """Add intelligent imports based on script usage.

        Args:
            script_content: Script content
            context: Script context

        Returns:
            Script with added imports
        """
        imports = []

        # Detect usage and add imports
        if "java.util.Date" in script_content:
            imports.append("from java.util import Date")

        if "java.text.SimpleDateFormat" in script_content:
            imports.append("from java.text import SimpleDateFormat")

        if "ArrayList" in script_content:
            imports.append("from java.util import ArrayList")

        if context == "gateway" and "Thread" in script_content:
            imports.append("from java.lang import Thread")

        if imports:
            import_block = "\n".join(imports) + "\n\n"
            return import_block + script_content

        return script_content

    def _add_performance_optimizations(self, script_content: str) -> str:
        """Add performance optimizations to script.

        Args:
            script_content: Script content

        Returns:
            Optimized script content
        """
        # Replace multiple tag reads with batch read
        if "system.tag.read(" in script_content:
            script_content = script_content.replace(
                "system.tag.read(",
                "# Consider using system.tag.readBlocking for better performance\n# system.tag.read(",
            )

        # Suggest caching for repeated operations
        if script_content.count("system.db.runQuery") > 2:
            header = """# Performance tip: Consider caching query results for repeated use
# Example: query_cache = {}

"""
            script_content = header + script_content

        return script_content

    def _add_debug_helpers(self, script_content: str) -> str:
        """Add debugging helpers to script.

        Args:
            script_content: Script content

        Returns:
            Script with debug helpers
        """
        debug_header = """# Debug mode enabled
import time
_start_time = time.time()

def debug_log(message):
    elapsed = time.time() - _start_time
    system.util.getLogger("DEBUG").info("[%.3fs] %s" % (elapsed, message))

debug_log("Script started")

"""

        debug_footer = """
debug_log("Script completed")
"""

        return debug_header + script_content + debug_footer

    def get_related_documentation(
        self,
        template_name: str,
        functions_used: list[str],
    ) -> list[dict[str, str]]:
        """Get related documentation links.

        Args:
            template_name: Template name
            functions_used: List of functions used in script

        Returns:
            List of documentation links
        """
        docs = []

        if not self.graph_client:
            return docs

        try:
            # Get documentation for functions
            for function in functions_used[:5]:  # Limit to 5
                query = """
                MATCH (f:Function {name: $function})
                RETURN f.documentation_url as url,
                       f.description as description
                """

                results = self.graph_client.execute_query(query, {"function": function})

                if results:
                    record = results[0]
                    if record.get("url"):
                        docs.append(
                            {
                                "title": f"Documentation: {function}",
                                "url": record["url"],
                                "description": record.get("description", ""),
                            }
                        )

            # Get template documentation
            template_query = """
            MATCH (t:Template {name: $template_name})
            RETURN t.documentation_url as url,
                   t.help_text as description
            """

            results = self.graph_client.execute_query(template_query, {"template_name": template_name})

            if results:
                record = results[0]
                if record.get("url"):
                    docs.append(
                        {
                            "title": f"Template Guide: {template_name}",
                            "url": record["url"],
                            "description": record.get("description", ""),
                        }
                    )

        except Exception as e:
            self.logger.warning(f"Failed to get documentation: {e}")

        return docs
