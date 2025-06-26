"""Context-Aware Response Generator for SME Agent - Phase 11.2.

Phase 11.2: SME Agent Core Capabilities - Context-Aware Intelligence
Following crawl_mcp.py methodology for intelligent response generation.

This module provides:
- Intelligent, context-aware response generation
- Project analysis and architecture recommendations
- Code review and optimization suggestions
- Best practice enforcement and security validation
- Performance optimization and troubleshooting guidance
"""

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ContextAwareError(Exception):
    """Custom exception for context-aware response errors."""

    pass


@dataclass
class ProjectContext:
    """Represents project context for analysis."""

    project_path: str
    project_type: str  # "gateway", "vision", "perspective", "mixed"
    file_count: int
    directories: list[str] = field(default_factory=list)
    code_files: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)
    resource_files: list[str] = field(default_factory=list)
    technologies_detected: set[str] = field(default_factory=set)
    complexity_score: float = 0.0
    last_analyzed: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseContext:
    """Context information for generating responses."""

    user_query: str
    domain: str | None = None
    topic: str | None = None
    project_context: ProjectContext | None = None
    user_experience_level: str = "intermediate"  # beginner, intermediate, advanced, expert
    preferred_response_style: str = "detailed"  # brief, detailed, comprehensive
    include_examples: bool = True
    include_best_practices: bool = True
    include_warnings: bool = True
    previous_conversation: list[str] = field(default_factory=list)
    context_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextAwareResponse:
    """Response with context-aware intelligence."""

    query: str
    response: str
    confidence: float
    domain: str | None = None
    topic: str | None = None
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    best_practices: list[str] = field(default_factory=list)
    related_topics: list[str] = field(default_factory=list)
    follow_up_questions: list[str] = field(default_factory=list)
    response_time: float = 0.0
    sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ProjectAnalyzer:
    """Analyzes project structure and provides context.

    Following crawl_mcp.py methodology:
    - Step 1: Environment validation first
    - Step 2: Comprehensive input validation
    - Step 3: Error handling with user-friendly messages
    - Step 4: Modular component testing
    - Step 5: Progressive complexity support
    - Step 6: Resource management and cleanup
    """

    def __init__(self) -> Any:
        """Initialize the project analyzer."""
        self.logger = logging.getLogger(self.__class__.__name__)

        # File patterns for different project types
        self.file_patterns = {
            "gateway": {
                "scripts": [r".*\.py$", r".*\.jy$"],
                "config": [r".*\.properties$", r".*\.conf$", r".*\.xml$"],
                "resources": [r".*\.json$", r".*\.csv$", r".*\.xlsx?$"],
            },
            "vision": {
                "windows": [r".*\.vwin$"],
                "templates": [r".*\.vtemplate$"],
                "resources": [r".*\.png$", r".*\.jpg$", r".*\.gif$", r".*\.svg$"],
            },
            "perspective": {
                "views": [r".*\.view$"],
                "resources": [r".*\.resource$"],
                "themes": [r".*\.theme$"],
            },
        }

        # Technology indicators
        self.technology_indicators = {
            "database": ["sql", "database", "db", "query", "connection"],
            "opc_ua": ["opc", "opcua", "server", "client", "subscription"],
            "modbus": ["modbus", "tcp", "rtu", "device"],
            "mqtt": ["mqtt", "broker", "publish", "subscribe"],
            "rest_api": ["rest", "api", "http", "request", "response"],
            "scripting": ["script", "python", "jython", "automation"],
            "reporting": ["report", "pdf", "excel", "chart", "graph"],
            "alarming": ["alarm", "alert", "notification", "event"],
            "historian": ["tag", "history", "trend", "data", "logging"],
        }

    def analyze_project(self, project_path: str) -> ProjectContext:
        """Analyze project structure and return context.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectContext with analysis results
        """
        try:
            # Step 2: Comprehensive Input Validation
            if not project_path:
                raise ContextAwareError("Project path cannot be empty")

            path = Path(project_path)
            if not path.exists():
                raise ContextAwareError(f"Project path does not exist: {project_path}")

            if not path.is_dir():
                raise ContextAwareError(f"Project path is not a directory: {project_path}")

            # Analyze project structure
            context = ProjectContext(
                project_path=str(path.absolute()),
                project_type="unknown",
                file_count=0,
                last_analyzed=datetime.now(),
            )

            # Scan directory structure
            self._scan_directory_structure(path, context)

            # Detect project type
            context.project_type = self._detect_project_type(context)

            # Detect technologies
            context.technologies_detected = self._detect_technologies(context)

            # Calculate complexity score
            context.complexity_score = self._calculate_complexity_score(context)

            self.logger.info(f"Analyzed project: {context.project_type} with {context.file_count} files")

            return context

        except Exception as e:
            # Step 3: Error handling with user-friendly messages
            self.logger.error(f"Project analysis failed: {e}")
            raise ContextAwareError(f"Failed to analyze project: {e!s}") from e

    def _scan_directory_structure(self, path: Path, context: ProjectContext) -> None:
        """Scan directory structure and categorize files."""
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    context.file_count += 1
                    file_path = str(item.relative_to(path))

                    # Categorize files
                    if self._is_code_file(item):
                        context.code_files.append(file_path)
                    elif self._is_config_file(item):
                        context.config_files.append(file_path)
                    elif self._is_resource_file(item):
                        context.resource_files.append(file_path)

                elif item.is_dir():
                    dir_path = str(item.relative_to(path))
                    if dir_path != ".":  # Skip root directory
                        context.directories.append(dir_path)

        except Exception as e:
            self.logger.warning(f"Error scanning directory structure: {e}")

    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file."""
        code_extensions = {".py", ".jy", ".js", ".java", ".sql"}
        return file_path.suffix.lower() in code_extensions

    def _is_config_file(self, file_path: Path) -> bool:
        """Check if file is a configuration file."""
        config_extensions = {".properties", ".conf", ".xml", ".json", ".yaml", ".yml"}
        config_names = {"settings.json", "project.json", "config.json"}

        return file_path.suffix.lower() in config_extensions or file_path.name.lower() in config_names

    def _is_resource_file(self, file_path: Path) -> bool:
        """Check if file is a resource file."""
        resource_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".pdf",
            ".csv",
            ".xlsx",
            ".xls",
        }
        return file_path.suffix.lower() in resource_extensions

    def _detect_project_type(self, context: ProjectContext) -> str:
        """Detect the type of Ignition project."""
        type_scores = {"gateway": 0, "vision": 0, "perspective": 0}

        # Check file patterns
        for file_path in context.code_files + context.config_files + context.resource_files:
            file_lower = file_path.lower()

            # Gateway indicators
            if any(pattern in file_lower for pattern in ["script", "gateway", "tag", "device"]):
                type_scores["gateway"] += 1

            # Vision indicators
            if any(pattern in file_lower for pattern in ["vision", "window", "template", ".vwin"]):
                type_scores["vision"] += 1

            # Perspective indicators
            if any(pattern in file_lower for pattern in ["perspective", "view", "session", ".view"]):
                type_scores["perspective"] += 1

        # Check directory names
        for dir_path in context.directories:
            dir_lower = dir_path.lower()

            if any(pattern in dir_lower for pattern in ["gateway", "scripts", "devices"]):
                type_scores["gateway"] += 2

            if any(pattern in dir_lower for pattern in ["vision", "windows", "templates"]):
                type_scores["vision"] += 2

            if any(pattern in dir_lower for pattern in ["perspective", "views", "sessions"]):
                type_scores["perspective"] += 2

        # Determine project type
        max_score = max(type_scores.values())
        if max_score == 0:
            return "unknown"

        # Check for mixed projects
        high_scores = [ptype for ptype, score in type_scores.items() if score >= max_score * 0.7]
        if len(high_scores) > 1:
            return "mixed"

        if type_scores and any(score > 0 for score in type_scores.values()):
            return max(type_scores.keys(), key=lambda k: type_scores[k])
        return "unknown"

    def _detect_technologies(self, context: ProjectContext) -> set[str]:
        """Detect technologies used in the project."""
        technologies = set()

        # Analyze file contents (simplified - would be more sophisticated in practice)
        all_text = " ".join(context.code_files + context.config_files).lower()

        for tech, indicators in self.technology_indicators.items():
            if any(indicator in all_text for indicator in indicators):
                technologies.add(tech)

        return technologies

    def _calculate_complexity_score(self, context: ProjectContext) -> float:
        """Calculate project complexity score (0.0 to 1.0)."""
        score = 0.0

        # File count factor (normalized)
        file_factor = min(context.file_count / 100.0, 1.0) * 0.3
        score += file_factor

        # Directory structure factor
        dir_factor = min(len(context.directories) / 20.0, 1.0) * 0.2
        score += dir_factor

        # Technology diversity factor
        tech_factor = min(len(context.technologies_detected) / 5.0, 1.0) * 0.3
        score += tech_factor

        # Project type factor
        type_factors = {
            "mixed": 0.2,
            "perspective": 0.15,
            "vision": 0.1,
            "gateway": 0.05,
            "unknown": 0.0,
        }
        score += type_factors.get(context.project_type, 0.0)

        return min(score, 1.0)


class ContextAwareResponseGenerator:
    """Generates intelligent, context-aware responses.

    Following crawl_mcp.py methodology for systematic response generation.
    """

    def __init__(self, domain_managers=None, learning_engine=None, llm_manager=None) -> None:
        """Initialize the context-aware response generator.

        Args:
            domain_managers: Dictionary of domain managers
            learning_engine: Adaptive learning engine
            llm_manager: LLM manager for advanced responses
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.domain_managers = domain_managers or {}
        self.learning_engine = learning_engine
        self.llm_manager = llm_manager
        self.project_analyzer = ProjectAnalyzer()

        # Response templates
        self.response_templates = {
            "beginner": {
                "intro": "Let me explain this step by step:",
                "example_intro": "Here's a simple example:",
                "warning_intro": "⚠️ Important to know:",
                "best_practice_intro": "💡 Best practice:",
            },
            "intermediate": {
                "intro": "Here's what you need to know:",
                "example_intro": "Example implementation:",
                "warning_intro": "⚠️ Be aware:",
                "best_practice_intro": "💡 Recommended approach:",
            },
            "advanced": {
                "intro": "Technical details:",
                "example_intro": "Implementation example:",
                "warning_intro": "⚠️ Consideration:",
                "best_practice_intro": "💡 Optimization:",
            },
            "expert": {
                "intro": "Analysis:",
                "example_intro": "Reference implementation:",
                "warning_intro": "⚠️ Edge case:",
                "best_practice_intro": "💡 Advanced pattern:",
            },
        }

        # Step 1: Environment validation first
        self._validate_environment()

    def _validate_environment(self) -> None:
        """Step 1: Environment Validation First."""
        if not self.domain_managers:
            self.logger.warning("No domain managers provided - responses may be limited")

        if not self.learning_engine:
            self.logger.warning("No learning engine provided - adaptive learning disabled")

    def generate_response(self, query: str, context: ResponseContext) -> ContextAwareResponse:
        """Generate context-aware response with confidence scoring.

        Args:
            query: User query
            context: Response context

        Returns:
            ContextAwareResponse with intelligent response
        """
        start_time = time.time()

        try:
            # Step 2: Comprehensive Input Validation
            if not query or not query.strip():
                raise ContextAwareError("Query cannot be empty")

            # Initialize response
            response = ContextAwareResponse(
                query=query,
                response="",
                confidence=0.0,
                domain=context.domain,
                topic=context.topic,
            )

            # Analyze query and determine domain/topic if not provided
            if not context.domain or not context.topic:
                domain, topic = self._analyze_query(query)
                response.domain = context.domain or domain
                response.topic = context.topic or topic

            # Gather knowledge from domain managers
            knowledge_results = self._gather_domain_knowledge(query, response.domain or "General", context)

            # Generate base response
            response.response = self._generate_base_response(query, knowledge_results, context)

            # Add context-aware enhancements
            self._add_context_enhancements(response, context, knowledge_results)

            # Calculate confidence score
            response.confidence = self._calculate_response_confidence(knowledge_results, context)

            # Generate recommendations
            response.recommendations = self._generate_recommendations(query, response, context)

            # Generate follow-up questions
            response.follow_up_questions = self._generate_follow_up_questions(query, response, context)

            # Record response time
            response.response_time = time.time() - start_time

            # Learn from this interaction (if learning engine available)
            if self.learning_engine:
                self._record_interaction(query, response, context)

            self.logger.info(f"Generated response for query: {query[:50]}... (confidence: {response.confidence:.2f})")

            return response

        except Exception as e:
            # Step 3: Error handling with user-friendly messages
            self.logger.error(f"Response generation failed: {e}")

            return ContextAwareResponse(
                query=query,
                response=f"I apologize, but I encountered an error while processing your query: {e!s}",
                confidence=0.0,
                response_time=time.time() - start_time,
                warnings=[f"Response generation failed: {e!s}"],
            )

    def _analyze_query(self, query: str) -> tuple[str, str]:
        """Analyze query to determine domain and topic."""
        query_lower = query.lower()

        # Domain detection patterns
        domain_patterns = {
            "Gateway Scripting": [
                "script",
                "gateway",
                "startup",
                "shutdown",
                "timer",
                "tag event",
            ],
            "System Functions": [
                "function",
                "system.",
                "tag.",
                "database.",
                "perspective.",
                "vision.",
            ],
            "Designer Development": [
                "designer",
                "vision",
                "perspective",
                "component",
                "template",
                "binding",
            ],
            "Client Applications": [
                "client",
                "session",
                "navigation",
                "security",
                "user",
            ],
        }

        # Find matching domain
        domain = "General"
        for domain_name, patterns in domain_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                domain = domain_name
                break

        # Topic extraction (simplified)
        topic_keywords = re.findall(r"\b\w+\b", query_lower)
        topic = " ".join(topic_keywords[:3])  # Use first 3 keywords as topic

        return domain, topic

    def _gather_domain_knowledge(self, query: str, domain: str, context: ResponseContext) -> list[Any]:
        """Gather knowledge from relevant domain managers."""
        knowledge_results = []

        # Import domain query classes
        try:
            from .knowledge_domains import DomainQuery  # type: ignore[import-untyped]

            # Create domain query
            domain_query = DomainQuery(
                query_text=query,
                domain=domain,
                max_results=context.context_metadata.get("max_results", 5),
                include_examples=context.include_examples,
                include_best_practices=context.include_best_practices,
            )

            # Query relevant domain managers
            for domain_name, manager in self.domain_managers.items():
                if domain_name == domain or domain == "General":
                    try:
                        result = manager.query_knowledge(domain_query)
                        knowledge_results.append(result)
                    except Exception as e:
                        self.logger.warning(f"Domain query failed for {domain_name}: {e}")

        except ImportError:
            self.logger.warning("Knowledge domains not available")

        return knowledge_results

    def _generate_base_response(self, _query: str, knowledge_results: list[Any], context: ResponseContext) -> str:
        """Generate base response from knowledge results."""
        if not knowledge_results:
            return (
                "I don't have specific information about that topic. "
                "Could you provide more details or try rephrasing your question?"
            )

        # Get templates for user experience level
        templates = self.response_templates.get(context.user_experience_level, self.response_templates["intermediate"])

        # Start response
        response_parts = [templates["intro"]]

        # Add knowledge from results
        for result in knowledge_results:
            if hasattr(result, "results") and result.results:
                # Add best result
                best_result = result.results[0]
                response_parts.append(f"\n{best_result.description}")

                if hasattr(best_result, "content") and best_result.content:
                    response_parts.append(f"\n{best_result.content}")

        return "\n".join(response_parts)

    def _add_context_enhancements(
        self,
        response: ContextAwareResponse,
        context: ResponseContext,
        knowledge_results: list[Any],
    ) -> None:
        """Add context-aware enhancements to the response."""
        # Add examples if requested
        if context.include_examples:
            examples = []
            for result in knowledge_results:
                if hasattr(result, "results"):
                    for item in result.results:
                        if hasattr(item, "examples") and item.examples:
                            examples.extend(item.examples[:2])  # Limit examples
            response.examples = examples[:3]  # Limit total examples

        # Add best practices if requested
        if context.include_best_practices:
            best_practices = []
            for result in knowledge_results:
                if hasattr(result, "results"):
                    for item in result.results:
                        if hasattr(item, "best_practices") and item.best_practices:
                            best_practices.extend(item.best_practices[:2])
            response.best_practices = best_practices[:5]  # Limit best practices

        # Add warnings if requested
        if context.include_warnings:
            warnings = []
            for result in knowledge_results:
                if hasattr(result, "warnings") and result.warnings:
                    warnings.extend(result.warnings)
            response.warnings = warnings[:3]  # Limit warnings

        # Add project-specific context if available
        if context.project_context:
            self._add_project_context(response, context.project_context)

    def _add_project_context(self, response: ContextAwareResponse, project_context: ProjectContext) -> None:
        """Add project-specific context to the response."""
        # Add project-specific recommendations
        if project_context.project_type == "gateway":
            response.recommendations.append("Consider gateway scripting best practices for your project")
        elif project_context.project_type == "perspective":
            response.recommendations.append("Review Perspective component design patterns")
        elif project_context.project_type == "vision":
            response.recommendations.append("Consider Vision component optimization techniques")

        # Add technology-specific advice
        if "database" in project_context.technologies_detected:
            response.recommendations.append("Ensure proper database connection management")

        if "opc_ua" in project_context.technologies_detected:
            response.recommendations.append("Review OPC-UA subscription optimization")

        # Add complexity-based advice
        if project_context.complexity_score > 0.7:
            response.warnings.append("High project complexity detected - consider modular design patterns")

    def _calculate_response_confidence(self, knowledge_results: list[Any], context: ResponseContext) -> float:
        """Calculate confidence score for the response."""
        if not knowledge_results:
            return 0.1

        # Calculate average confidence from domain results
        confidences = []
        for result in knowledge_results:
            if hasattr(result, "confidence"):
                confidences.append(result.confidence)

        if not confidences:
            return 0.5

        base_confidence = sum(confidences) / len(confidences)

        # Adjust based on context
        if context.project_context:
            base_confidence += 0.1  # Boost for project context

        if len(context.previous_conversation) > 0:
            base_confidence += 0.05  # Boost for conversation context

        return min(base_confidence, 1.0)

    def _generate_recommendations(
        self, _query: str, response: ContextAwareResponse, context: ResponseContext
    ) -> list[str]:
        """Generate contextual recommendations."""
        recommendations = []

        # Add domain-specific recommendations
        if response.domain == "Gateway Scripting":
            recommendations.append("Test scripts in development environment before production deployment")
            recommendations.append("Use proper error handling and logging in all scripts")

        elif response.domain == "System Functions":
            recommendations.append("Review function documentation for latest parameters and usage")
            recommendations.append("Consider performance implications for frequently called functions")

        elif response.domain == "Designer Development":
            recommendations.append("Follow UI/UX best practices for component design")
            recommendations.append("Test components across different screen resolutions")

        # Add experience-level specific recommendations
        if context.user_experience_level == "beginner":
            recommendations.append("Start with simple implementations and gradually add complexity")
            recommendations.append("Review Ignition documentation and training materials")

        elif context.user_experience_level == "expert":
            recommendations.append("Consider advanced optimization techniques and patterns")
            recommendations.append("Review latest Ignition features and capabilities")

        return recommendations[:5]  # Limit recommendations

    def _generate_follow_up_questions(
        self, _query: str, response: ContextAwareResponse, context: ResponseContext
    ) -> list[str]:
        """Generate relevant follow-up questions."""
        follow_ups = []

        # Domain-specific follow-ups
        if response.domain == "Gateway Scripting":
            follow_ups.extend(
                [
                    "Would you like to see specific script examples?",
                    "Do you need help with error handling patterns?",
                    "Are you interested in performance optimization techniques?",
                ]
            )

        elif response.domain == "System Functions":
            follow_ups.extend(
                [
                    "Would you like to see usage examples for specific functions?",
                    "Do you need help with function parameters?",
                    "Are you looking for alternative functions?",
                ]
            )

        elif response.domain == "Designer Development":
            follow_ups.extend(
                [
                    "Would you like component configuration examples?",
                    "Do you need help with binding strategies?",
                    "Are you interested in styling and theming options?",
                ]
            )

        # Project context follow-ups
        if context.project_context and context.project_context.complexity_score > 0.5:
            follow_ups.append("Would you like architecture recommendations for your project?")

        return follow_ups[:3]  # Limit follow-up questions

    def _record_interaction(self, query: str, response: ContextAwareResponse, context: ResponseContext) -> None:
        """Record interaction for learning purposes."""
        try:
            from .adaptive_learning import ConversationData

            # Create conversation data for potential future learning
            _conversation_data = ConversationData(
                conversation_id=f"ctx_aware_{int(time.time())}",
                user_query=query,
                sme_response=response.response,
                domain=response.domain,
                topic=response.topic,
                context={
                    "user_experience_level": context.user_experience_level,
                    "response_style": context.preferred_response_style,
                    "confidence": response.confidence,
                    "response_time": response.response_time,
                },
            )

            # Note: Actual learning would happen when user provides feedback
            # This is just recording the interaction for potential future learning

        except ImportError:
            self.logger.warning("Adaptive learning not available")
        except Exception as e:
            self.logger.warning(f"Failed to record interaction: {e}")

    def analyze_project_context(self, project_files: list[str]) -> ProjectContext:
        """Analyze project for context-aware recommendations.

        Args:
            project_files: list of project file paths

        Returns:
            ProjectContext with analysis results
        """
        if not project_files:
            raise ContextAwareError("No project files provided")

        # For simplicity, analyze the directory containing the first file
        first_file_path = Path(project_files[0])
        project_path = first_file_path.parent if first_file_path.is_file() else first_file_path

        return self.project_analyzer.analyze_project(str(project_path))


# Export all context-aware components
__all__ = [
    "ContextAwareError",
    "ContextAwareResponse",
    "ContextAwareResponseGenerator",
    "ProjectAnalyzer",
    "ProjectContext",
    "ResponseContext",
]
