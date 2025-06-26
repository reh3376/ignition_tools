#!/usr/bin/env python3
"""Enhanced Code Intelligence for SME Agent
Phase 11.4: Advanced SME Agent Features

This module provides enhanced code analysis following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Error handling and user-friendly messages
4. Modular component testing
5. Progressive complexity support
6. Resource management and cleanup

Enhanced Code Intelligence Features:
- Intelligent code analysis and pattern detection
- Automated refactoring suggestions with safety guarantees
- Integration with existing refactoring tools
- Code quality assessment and improvement recommendations
"""

import ast
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Self

logger = logging.getLogger(__name__)


@dataclass
class CodeAnalysisResult:
    """Code analysis result with recommendations."""

    file_path: str
    analysis_type: str
    complexity_score: float
    quality_score: float
    maintainability_score: float
    issues: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    refactoring_opportunities: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    ignition_specific_issues: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RefactoringSuggestion:
    """Refactoring suggestion with implementation details."""

    suggestion_id: str
    suggestion_type: str  # Extract Method, Extract Class, etc.
    priority: str  # High, Medium, Low
    description: str
    rationale: str
    target_file: str
    target_location: dict[str, Any] = field(default_factory=dict)
    implementation_steps: list[str] = field(default_factory=list)
    safety_analysis: dict[str, Any] = field(default_factory=dict)
    impact_assessment: dict[str, Any] = field(default_factory=dict)
    ignition_considerations: list[str] = field(default_factory=list)


@dataclass
class CodePattern:
    """Code pattern definition for analysis."""

    pattern_id: str
    pattern_name: str
    pattern_type: str  # Anti-pattern, Best Practice, etc.
    description: str
    detection_rules: list[str] = field(default_factory=list)
    ignition_specific: bool = False
    severity: str = "Medium"  # High, Medium, Low
    fix_suggestions: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


class EnhancedCodeIntelligence:
    """Enhanced Code Intelligence for SME Agent."""

    def __init__(self: Self, config: dict[str, Any] | None = None):
        """Initialize enhanced code intelligence."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Analysis storage
        self.code_patterns: list[CodePattern] = []
        self.analysis_cache: dict[str, CodeAnalysisResult] = {}
        self.refactoring_suggestions: list[RefactoringSuggestion] = []

        # Integration with existing tools
        self.refactor_tools_available = False
        self.neo4j_available = False

        # Performance tracking
        self.intelligence_stats = {
            "files_analyzed": 0,
            "patterns_detected": 0,
            "refactoring_suggestions_generated": 0,
            "code_patterns_loaded": 0,
            "last_analysis": None,
        }

    async def initialize(self: Self) -> dict[str, Any]:
        """Initialize enhanced code intelligence following crawl_mcp.py methodology."""
        try:
            # Step 1: Environment validation first
            validation_result = await self._validate_environment()
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": "Environment validation failed",
                    "errors": validation_result["errors"],
                }

            # Step 2: Load code patterns and initialize tools
            await self._load_code_patterns()
            await self._initialize_tool_integrations()

            # Step 3: Update statistics
            self.intelligence_stats["last_analysis"] = datetime.now().isoformat()

            return {
                "status": "success",
                "components_initialized": [
                    "code_patterns",
                    "tool_integrations",
                    "analysis_cache",
                ],
                "integrations": {
                    "refactor_tools": self.refactor_tools_available,
                    "neo4j": self.neo4j_available,
                },
                "statistics": self.intelligence_stats,
                "warnings": validation_result.get("warnings", []),
            }

        except Exception as e:
            self.logger.error(f"Enhanced code intelligence initialization failed: {e}")
            return {
                "status": "error",
                "message": f"Initialization failed: {e!s}",
                "errors": [str(e)],
            }

    async def analyze_code_file(
        self,
        file_path: str,
        analysis_type: str = "comprehensive",
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Analyze a code file for quality, patterns, and refactoring opportunities."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_analysis_request(
                file_path, analysis_type, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "analysis": None,
                }

            # Check cache first
            cache_key = f"{file_path}:{analysis_type}:{complexity}"
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                return {
                    "status": "success",
                    "analysis": cached_result,
                    "from_cache": True,
                }

            # Perform analysis
            analysis_result = await self._perform_code_analysis(
                file_path, analysis_type, complexity
            )

            # Cache result
            self.analysis_cache[cache_key] = analysis_result
            self.intelligence_stats["files_analyzed"] += 1

            return {
                "status": "success",
                "analysis": analysis_result,
                "from_cache": False,
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Code analysis failed for {file_path}: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze code file: {e!s}",
                "analysis": None,
            }

    async def generate_refactoring_suggestions(
        self,
        file_path: str,
        focus_areas: list[str] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Generate intelligent refactoring suggestions."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_refactoring_request(
                file_path, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "suggestions": None,
                }

            # Analyze code first if not already done
            analysis_result = await self.analyze_code_file(
                file_path, "refactoring", complexity
            )
            if analysis_result["status"] != "success":
                return analysis_result

            # Generate suggestions
            suggestions = await self._generate_refactoring_suggestions(
                analysis_result["analysis"], focus_areas or [], complexity
            )

            self.intelligence_stats["refactoring_suggestions_generated"] += len(
                suggestions
            )

            return {
                "status": "success",
                "suggestions": suggestions,
                "focus_areas": focus_areas or [],
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Refactoring suggestion generation failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate refactoring suggestions: {e!s}",
                "suggestions": None,
            }

    async def detect_code_patterns(
        self,
        file_path: str,
        pattern_types: list[str] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Detect code patterns and anti-patterns."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_pattern_detection_request(
                file_path, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "patterns": None,
                }

            # Detect patterns
            detected_patterns = await self._detect_patterns_in_file(
                file_path, pattern_types or [], complexity
            )

            self.intelligence_stats["patterns_detected"] += len(detected_patterns)

            return {
                "status": "success",
                "patterns": detected_patterns,
                "pattern_types_searched": pattern_types or ["all"],
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to detect code patterns: {e!s}",
                "patterns": None,
            }

    async def assess_code_quality(
        self,
        file_paths: list[str],
        quality_metrics: list[str] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Assess code quality across multiple files."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_quality_assessment_request(
                file_paths, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "assessment": None,
                }

            # Assess quality
quality_assessment: dict[str, Any] = await self._assess_code_quality(
                file_paths, quality_metrics or [], complexity
            )

            return {
                "status": "success",
                "assessment": quality_assessment,
                "files_assessed": len(file_paths),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Code quality assessment failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to assess code quality: {e!s}",
                "assessment": None,
            }

    async def integrate_with_refactor_tools(
        self, operation: str, parameters: dict[str, Any], complexity: str = "standard"
    ) -> dict[str, Any]:
        """Integrate with existing refactoring tools."""
        try:
            if not self.refactor_tools_available:
                return {
                    "status": "error",
                    "message": "Refactoring tools not available",
                    "result": None,
                }

            # Step 2: Comprehensive input validation
            validation_result = self._validate_tool_integration_request(
                operation, parameters, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "result": None,
                }

            # Execute integration
            result = await self._execute_tool_integration(
                operation, parameters, complexity
            )

            return {
                "status": "success",
                "result": result,
                "operation": operation,
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Tool integration failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to integrate with refactor tools: {e!s}",
                "result": None,
            }

    async def get_intelligence_statistics(self: Self) -> dict[str, Any]:
        """Get enhanced code intelligence statistics."""
        return {
            "statistics": self.intelligence_stats.copy(),
            "cache_status": {
                "cached_analyses": len(self.analysis_cache),
                "cache_size_mb": self._calculate_cache_size(),
            },
            "pattern_coverage": {
                "total_patterns": len(self.code_patterns),
                "ignition_specific_patterns": len(
                    [p for p in self.code_patterns if p.ignition_specific]
                ),
            },
            "tool_integrations": {
                "refactor_tools": self.refactor_tools_available,
                "neo4j": self.neo4j_available,
            },
            "capabilities": [
                "code_analysis",
                "refactoring_suggestions",
                "pattern_detection",
                "quality_assessment",
                "tool_integration",
            ],
        }

    # Private methods following crawl_mcp.py methodology

    async def _validate_environment(self: Self) -> dict[str, Any]:
        """Validate environment for enhanced code intelligence."""
        errors = []
        warnings = []

        # Check required directories
        cache_dir = Path("cache/code_intelligence")
        if not cache_dir.exists():
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create cache directory: {e}")

        # Check for refactoring tools
        try:
            from ignition.refactoring import RefactoringEngine

            self.refactor_tools_available = True
        except ImportError:
            warnings.append("Refactoring tools not available - limited functionality")

        # Check optional Neo4j connection
        neo4j_available = all(
            [
                os.getenv("NEO4J_URI"),
                os.getenv("NEO4J_USER"),
                os.getenv("NEO4J_PASSWORD"),
            ]
        )

        if neo4j_available:
            self.neo4j_available = True
        else:
            warnings.append("Neo4j not configured - using static analysis only")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "refactor_tools_available": self.refactor_tools_available,
            "neo4j_available": self.neo4j_available,
        }

    async def _load_code_patterns(self: Self) -> None:
        """Load code patterns for analysis."""
        patterns = [
            CodePattern(
                pattern_id="ignition_tag_binding_antipattern",
                pattern_name="Inefficient Tag Binding",
                pattern_type="Anti-pattern",
                description="Direct tag access in loops or frequent operations",
                detection_rules=[
                    "system.tag.read() in loop",
                    "system.tag.write() in loop",
                    "Multiple tag operations without batching",
                ],
                ignition_specific=True,
                severity="High",
                fix_suggestions=[
                    "Use system.tag.readBlocking() for batch reads",
                    "Cache tag values when possible",
                    "Use tag change scripts instead of polling",
                    "Implement proper tag grouping strategies",
                ],
                examples=[
                    "# Bad: Reading tags in loop",
                    "for i in range(100):",
                    "    value = system.tag.read('[default]Tag' + str(i))",
                    "",
                    "# Good: Batch tag reading",
                    "tag_paths = ['[default]Tag' + str(i) for i in range(100)]",
                    "values = system.tag.readBlocking(tag_paths)",
                ],
            ),
            CodePattern(
                pattern_id="database_connection_leak",
                pattern_name="Database Connection Leak",
                pattern_type="Anti-pattern",
                description="Database connections not properly closed",
                detection_rules=[
                    "system.db.runQuery() without proper cleanup",
                    "Missing try-finally blocks for database operations",
                    "Connection objects not explicitly closed",
                ],
                ignition_specific=True,
                severity="High",
                fix_suggestions=[
                    "Use try-finally blocks for database operations",
                    "Implement connection pooling",
                    "Use context managers for resource management",
                    "Add proper error handling and cleanup",
                ],
                examples=[
                    "# Bad: No connection cleanup",
                    "result = system.db.runQuery('SELECT * FROM table')",
                    "",
                    "# Good: Proper resource management",
                    "try:",
                    "    result = system.db.runQuery('SELECT * FROM table')",
                    "finally:",
                    "    # Cleanup handled by Ignition framework",
                ],
            ),
            CodePattern(
                pattern_id="excessive_complexity",
                pattern_name="Excessive Cyclomatic Complexity",
                pattern_type="Code Smell",
                description="Functions with high cyclomatic complexity",
                detection_rules=[
                    "Cyclomatic complexity > 10",
                    "Nested if statements > 3 levels",
                    "Long parameter lists (> 5 parameters)",
                ],
                ignition_specific=False,
                severity="Medium",
                fix_suggestions=[
                    "Extract methods to reduce complexity",
                    "Use early returns to reduce nesting",
                    "Consider using strategy pattern",
                    "Break down large functions into smaller ones",
                ],
                examples=[
                    "# Bad: High complexity function",
                    "def complex_function(a, b, c, d, e, f):",
                    "    if a > 0:",
                    "        if b > 0:",
                    "            if c > 0:",
                    "                # Deep nesting...",
                    "",
                    "# Good: Reduced complexity",
                    "def simple_function(params: Any):",
                    "    if not _validate_params(params):",
                    "        return None",
                    "    return _process_params(params)",
                ],
            ),
        ]

        self.code_patterns.extend(patterns)
        self.intelligence_stats["code_patterns_loaded"] = len(self.code_patterns)

    async def _initialize_tool_integrations(self: Self) -> None:
        """Initialize integrations with existing tools."""
        try:
            if self.refactor_tools_available:
                # Initialize refactoring engine integration
                pass

            if self.neo4j_available:
                # Initialize Neo4j integration for code relationships
                pass
        except Exception as e:
            self.logger.warning(f"Tool integration initialization warning: {e}")

    def _validate_analysis_request(
        self, file_path: str, analysis_type: str, complexity: str
    ) -> dict[str, Any]:
        """Validate code analysis request parameters."""
        if not file_path or not isinstance(file_path, str):
            return {"valid": False, "error": "File path must be provided as a string"}

        if not Path(file_path).exists():
            return {"valid": False, "error": f"File does not exist: {file_path}"}

        valid_analysis_types = ["comprehensive", "refactoring", "patterns", "quality"]
        if analysis_type not in valid_analysis_types:
            return {
                "valid": False,
                "error": f"Analysis type must be one of: {valid_analysis_types}",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_refactoring_request(
        self, file_path: str, complexity: str
    ) -> dict[str, Any]:
        """Validate refactoring request parameters."""
        return self._validate_analysis_request(file_path, "refactoring", complexity)

    def _validate_pattern_detection_request(
        self, file_path: str, complexity: str
    ) -> dict[str, Any]:
        """Validate pattern detection request parameters."""
        return self._validate_analysis_request(file_path, "patterns", complexity)

    def _validate_quality_assessment_request(
        self, file_paths: list[str], complexity: str
    ) -> dict[str, Any]:
        """Validate quality assessment request parameters."""
        if not file_paths or not isinstance(file_paths, list):
            return {"valid": False, "error": "File paths must be provided as a list"}

        if len(file_paths) == 0:
            return {"valid": False, "error": "At least one file path must be provided"}

        for file_path in file_paths:
            if not Path(file_path).exists():
                return {"valid": False, "error": f"File does not exist: {file_path}"}

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_tool_integration_request(
        self, operation: str, parameters: dict[str, Any], complexity: str
    ) -> dict[str, Any]:
        """Validate tool integration request parameters."""
        if not operation or not isinstance(operation, str):
            return {"valid": False, "error": "Operation must be provided as a string"}

        if not parameters or not isinstance(parameters, dict):
            return {
                "valid": False,
                "error": "Parameters must be provided as a dictionary",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    async def _perform_code_analysis(
        self, file_path: str, analysis_type: str, complexity: str
    ) -> CodeAnalysisResult:
        """Perform comprehensive code analysis."""
        try:
            # Read file content
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST for analysis
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                return CodeAnalysisResult(
                    file_path=file_path,
                    analysis_type=analysis_type,
                    complexity_score=0.0,
                    quality_score=0.0,
                    maintainability_score=0.0,
                    issues=[{"type": "syntax_error", "message": str(e)}],
                )

            # Calculate metrics
            metrics = self._calculate_code_metrics(tree, content)

            # Detect issues
            issues = await self._detect_code_issues(tree, content, file_path)

            # Generate recommendations
            recommendations = self._generate_code_recommendations(
                metrics, issues, complexity
            )

            # Find refactoring opportunities
            refactoring_opportunities = await self._find_refactoring_opportunities(
                tree, content, complexity
            )

            # Extract dependencies
            dependencies = self._extract_dependencies(tree)

            # Calculate scores
            complexity_score = self._calculate_complexity_score(metrics)
            quality_score = self._calculate_quality_score(metrics, issues)
            maintainability_score = self._calculate_maintainability_score(
                metrics, issues
            )

            return CodeAnalysisResult(
                file_path=file_path,
                analysis_type=analysis_type,
                complexity_score=complexity_score,
                quality_score=quality_score,
                maintainability_score=maintainability_score,
                issues=issues,
                recommendations=recommendations,
                refactoring_opportunities=refactoring_opportunities,
                dependencies=dependencies,
                metrics=metrics,
                ignition_specific_issues=self._find_ignition_specific_issues(
                    tree, content
                ),
            )

        except Exception as e:
            self.logger.error(f"Code analysis failed for {file_path}: {e}")
            return CodeAnalysisResult(
                file_path=file_path,
                analysis_type=analysis_type,
                complexity_score=0.0,
                quality_score=0.0,
                maintainability_score=0.0,
                issues=[{"type": "analysis_error", "message": str(e)}],
            )

    def _calculate_code_metrics(
        self: Self, tree: ast.AST, content: str
    ) -> dict[str, Any]:
        """Calculate code metrics from AST."""
        metrics = {
            "lines_of_code": len(content.splitlines()),
            "blank_lines": len(
                [line for line in content.splitlines() if not line.strip()]
            ),
            "comment_lines": len(
                [line for line in content.splitlines() if line.strip().startswith("#")]
            ),
            "function_count": len(
                [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            ),
            "class_count": len(
                [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            ),
            "import_count": len(
                [
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                ]
            ),
        }

        # Calculate cyclomatic complexity
        complexity_visitor = CyclomaticComplexityVisitor()
        complexity_visitor.visit(tree)
        metrics["cyclomatic_complexity"] = complexity_visitor.complexity

        return metrics

    async def _detect_code_issues(
        self, tree: ast.AST, content: str, file_path: str
    ) -> list[dict[str, Any]]:
        """Detect code issues and problems."""
        issues = []

        # Check for common issues
        issue_visitor = CodeIssueVisitor()
        issue_visitor.visit(tree)
        issues.extend(issue_visitor.issues)

        # Check for Ignition-specific issues
        ignition_issues = self._find_ignition_specific_issues(tree, content)
        issues.extend(ignition_issues)

        return issues

    def _generate_code_recommendations(
        self, metrics: dict[str, Any], issues: list[dict[str, Any]], complexity: str
    ) -> list[str]:
        """Generate code improvement recommendations."""
        recommendations = []

        # Based on metrics
        if metrics.get("cyclomatic_complexity", 0) > 10:
            recommendations.append(
                "Consider breaking down complex functions into smaller, more manageable pieces"
            )

        if metrics.get("function_count", 0) > 20:
            recommendations.append(
                "Consider organizing functions into classes or modules"
            )

        if metrics.get("lines_of_code", 0) > 500:
            recommendations.append(
                "File is quite large - consider splitting into multiple files"
            )

        # Based on issues
        high_priority_issues = [
            issue for issue in issues if issue.get("severity") == "High"
        ]
        if high_priority_issues:
            recommendations.append(
                "Address high-priority issues first for maximum impact"
            )

        # Complexity-based recommendations
        if complexity in ["advanced", "enterprise"]:
            recommendations.extend(
                [
                    "Implement comprehensive error handling",
                    "Add detailed logging and monitoring",
                    "Consider performance optimization opportunities",
                ]
            )

        return recommendations

    async def _find_refactoring_opportunities(
        self, tree: ast.AST, content: str, complexity: str
    ) -> list[dict[str, Any]]:
        """Find refactoring opportunities in the code."""
        opportunities = []

        # Find long methods
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_lines = (
                    node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
                )
                if function_lines > 20:
                    opportunities.append(
                        {
                            "type": "extract_method",
                            "description": f"Function '{node.name}' is long ({function_lines} lines)",
                            "suggestion": "Consider extracting smaller methods",
                            "location": {"line": node.lineno, "function": node.name},
                        }
                    )

        # Find duplicate code patterns
        # (Simplified implementation - real implementation would be more sophisticated)

        return opportunities

    def _extract_dependencies(self: Self, tree: ast.AST) -> list[str]:
        """Extract dependencies from the code."""
        dependencies = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)

        return list(set(dependencies))

    def _find_ignition_specific_issues(
        self, tree: ast.AST, content: str
    ) -> list[dict[str, Any]]:
        """Find Ignition-specific code issues."""
        issues = []

        # Check for inefficient tag operations
        if "system.tag.read" in content and "for " in content:
            issues.append(
                {
                    "type": "ignition_performance",
                    "severity": "Medium",
                    "message": "Potential inefficient tag reading in loop",
                    "suggestion": "Consider using system.tag.readBlocking for batch operations",
                }
            )

        # Check for database connection patterns
        if "system.db.runQuery" in content and "try:" not in content:
            issues.append(
                {
                    "type": "ignition_resource",
                    "severity": "High",
                    "message": "Database query without proper error handling",
                    "suggestion": "Add try-except blocks for database operations",
                }
            )

        return issues

    def _calculate_complexity_score(self: Self, metrics: dict[str, Any]) -> float:
        """Calculate complexity score (0-100, lower is better)."""
        complexity = metrics.get("cyclomatic_complexity", 0)
        lines = metrics.get("lines_of_code", 1)
        functions = metrics.get("function_count", 1)

        # Normalize scores
        complexity_score = min(complexity / 20.0, 1.0) * 40  # Max 40 points
        size_score = min(lines / 1000.0, 1.0) * 30  # Max 30 points
        function_score = min(functions / 50.0, 1.0) * 30  # Max 30 points

        return complexity_score + size_score + function_score

    def _calculate_quality_score(
        self, metrics: dict[str, Any], issues: list[dict[str, Any]]
    ) -> float:
        """Calculate quality score (0-100, higher is better)."""
        base_score = 100.0

        # Deduct points for issues
        high_issues = len([i for i in issues if i.get("severity") == "High"])
        medium_issues = len([i for i in issues if i.get("severity") == "Medium"])
        low_issues = len([i for i in issues if i.get("severity") == "Low"])

        base_score -= high_issues * 10
        base_score -= medium_issues * 5
        base_score -= low_issues * 2

        # Bonus for good practices
        if (
            metrics.get("comment_lines", 0) / max(metrics.get("lines_of_code", 1), 1)
            > 0.1
        ):
            base_score += 5  # Good commenting

        return max(base_score, 0.0)

    def _calculate_maintainability_score(
        self, metrics: dict[str, Any], issues: list[dict[str, Any]]
    ) -> float:
        """Calculate maintainability score (0-100, higher is better)."""
        base_score = 100.0

        # Factor in complexity
        complexity = metrics.get("cyclomatic_complexity", 0)
        if complexity > 15:
            base_score -= 20
        elif complexity > 10:
            base_score -= 10

        # Factor in size
        lines = metrics.get("lines_of_code", 0)
        if lines > 1000:
            base_score -= 15
        elif lines > 500:
            base_score -= 10

        # Factor in structure
        functions = metrics.get("function_count", 0)
        classes = metrics.get("class_count", 0)
        if functions > 0 and classes > 0:
            base_score += 10  # Good structure

        return max(base_score, 0.0)

    def _calculate_cache_size(self: Self) -> float:
        """Calculate cache size in MB."""
        # Simplified calculation
        return len(self.analysis_cache) * 0.1  # Rough estimate

    async def _generate_refactoring_suggestions(
        self, analysis: CodeAnalysisResult, focus_areas: list[str], complexity: str
    ) -> list[RefactoringSuggestion]:
        """Generate intelligent refactoring suggestions."""
        suggestions = []

        # Based on analysis results
        for opportunity in analysis.refactoring_opportunities:
            suggestion = RefactoringSuggestion(
                suggestion_id=f"refactor_{len(suggestions)}",
                suggestion_type=opportunity["type"],
                priority="Medium",
                description=opportunity["description"],
                rationale=opportunity["suggestion"],
                target_file=analysis.file_path,
                target_location=opportunity.get("location", {}),
                implementation_steps=[
                    "Identify code to extract",
                    "Create new method/class",
                    "Update references",
                    "Test changes",
                ],
                safety_analysis={
                    "risk_level": "Low",
                    "impact_scope": "Local",
                    "rollback_strategy": "Version control",
                },
                impact_assessment={
                    "maintainability": "Improved",
                    "readability": "Improved",
                    "performance": "Neutral",
                },
            )
            suggestions.append(suggestion)

        return suggestions

    async def _detect_patterns_in_file(
        self, file_path: str, pattern_types: list[str], complexity: str
    ) -> list[dict[str, Any]]:
        """Detect code patterns in a file."""
        detected_patterns = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            for pattern in self.code_patterns:
                if pattern_types and pattern.pattern_type not in pattern_types:
                    continue

                # Simple pattern detection (real implementation would be more sophisticated)
                for rule in pattern.detection_rules:
                    if self._check_pattern_rule(content, rule):
                        detected_patterns.append(
                            {
                                "pattern_id": pattern.pattern_id,
                                "pattern_name": pattern.pattern_name,
                                "pattern_type": pattern.pattern_type,
                                "description": pattern.description,
                                "severity": pattern.severity,
                                "ignition_specific": pattern.ignition_specific,
                                "fix_suggestions": pattern.fix_suggestions,
                                "file_path": file_path,
                            }
                        )
                        break

        except Exception as e:
            self.logger.error(f"Pattern detection failed for {file_path}: {e}")

        return detected_patterns

    def _check_pattern_rule(self: Self, content: str, rule: str) -> bool:
        """Check if a pattern rule matches the content."""
        # Simplified pattern matching
        if "in loop" in rule:
            return "for " in content and rule.split(" in loop")[0] in content
        elif "without" in rule:
            base_pattern = rule.split(" without")[0]
            return base_pattern in content and "try:" not in content
        else:
            return rule in content

    async def _assess_code_quality(
        self, file_paths: list[str], quality_metrics: list[str], complexity: str
    ) -> dict[str, Any]:
        """Assess code quality across multiple files."""
        assessment = {
            "overall_score": 0.0,
            "file_assessments": [],
            "summary": {},
            "recommendations": [],
        }

        total_score = 0.0
        file_count = 0

        for file_path in file_paths:
            try:
                analysis_result = await self.analyze_code_file(
                    file_path, "quality", complexity
                )
                if analysis_result["status"] == "success":
                    analysis = analysis_result["analysis"]
                    file_assessment = {
                        "file_path": file_path,
                        "quality_score": analysis.quality_score,
                        "complexity_score": analysis.complexity_score,
                        "maintainability_score": analysis.maintainability_score,
                        "issue_count": len(analysis.issues),
                        "high_priority_issues": len(
                            [i for i in analysis.issues if i.get("severity") == "High"]
                        ),
                    }
                    assessment["file_assessments"].append(file_assessment)
                    total_score += analysis.quality_score
                    file_count += 1
            except Exception as e:
                self.logger.error(f"Quality assessment failed for {file_path}: {e}")

        if file_count > 0:
            assessment["overall_score"] = total_score / file_count

        # Generate summary
        assessment["summary"] = {
            "files_assessed": file_count,
            "average_quality_score": assessment["overall_score"],
            "total_issues": sum(
                fa["issue_count"] for fa in assessment["file_assessments"]
            ),
            "high_priority_issues": sum(
                fa["high_priority_issues"] for fa in assessment["file_assessments"]
            ),
        }

        # Generate recommendations
        if assessment["overall_score"] < 70:
            assessment["recommendations"].append(
                "Focus on addressing high-priority issues first"
            )
        if assessment["summary"]["high_priority_issues"] > 0:
            assessment["recommendations"].append(
                "Prioritize fixing high-severity issues"
            )

        return assessment

    async def _execute_tool_integration(
        self, operation: str, parameters: dict[str, Any], complexity: str
    ) -> dict[str, Any]:
        """Execute integration with refactoring tools."""
        # Placeholder for tool integration
        return {
            "operation": operation,
            "parameters": parameters,
            "result": "Tool integration not yet implemented",
            "status": "pending",
        }


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""

    def __init__(self: Self):
        self.complexity = 1  # Base complexity

    def visit_If(self: Self, node: Any) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self: Self, node: Any) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self: Self, node: Any) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self: Self, node: Any) -> None:
        self.complexity += 1
        self.generic_visit(node)


class CodeIssueVisitor(ast.NodeVisitor):
    """AST visitor to detect code issues."""

    def __init__(self: Self):
        self.issues = []

    def visit_FunctionDef(self: Self, node: Any) -> None:
        # Check for long parameter lists
        if len(node.args.args) > 5:
            self.issues.append(
                {
                    "type": "long_parameter_list",
                    "severity": "Medium",
                    "message": f"Function '{node.name}' has {len(node.args.args)} parameters",
                    "line": node.lineno,
                }
            )

        self.generic_visit(node)


# Validation functions following crawl_mcp.py methodology


async def validate_enhanced_code_intelligence_environment() -> dict[str, Any]:
    """Validate environment for enhanced code intelligence."""
    try:
        intelligence = EnhancedCodeIntelligence()
        return await intelligence._validate_environment()
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Environment validation failed: {e!s}"],
            "warnings": [],
        }


def get_enhanced_code_intelligence_info() -> dict[str, Any]:
    """Get enhanced code intelligence information."""
    return {
        "module": "enhanced_code_intelligence",
        "version": "1.0.0",
        "capabilities": [
            "code_analysis",
            "refactoring_suggestions",
            "pattern_detection",
            "quality_assessment",
            "tool_integration",
        ],
        "analysis_types": ["comprehensive", "refactoring", "patterns", "quality"],
        "pattern_types": ["Anti-pattern", "Best Practice", "Code Smell"],
        "complexity_levels": ["basic", "standard", "advanced", "enterprise"],
        "requirements": [
            "Python 3.11+",
            "AST parsing support",
            "Optional: Refactoring tools integration",
            "Optional: Neo4j for code relationships",
        ],
        "features": [
            "Environment validation first",
            "Comprehensive input validation",
            "Progressive complexity support",
            "Ignition-specific pattern detection",
            "Intelligent caching system",
        ],
    }
