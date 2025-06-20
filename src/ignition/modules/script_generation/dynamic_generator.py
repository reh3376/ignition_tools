"""Dynamic Script Generation Engine for Ignition Module.

This module provides real-time script generation capabilities within the Ignition
Designer environment, leveraging existing templates and Neo4j graph data.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from jinja2 import Template

from ...generators.script_generator import IgnitionScriptGenerator
from ...graph.client import IgnitionGraphClient


class ScriptContext(str, Enum):
    """Ignition script execution contexts."""

    GATEWAY = "gateway"
    CLIENT = "client"
    DESIGNER = "designer"
    PERSPECTIVE = "perspective"
    VISION = "vision"
    TAG = "tag"
    ALARM = "alarm"
    REPORT = "report"


@dataclass
class ScriptMetadata:
    """Metadata for generated scripts."""

    name: str
    context: ScriptContext
    description: str
    template_name: str
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    validation_errors: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class GenerationRequest:
    """Request for script generation."""

    context: ScriptContext
    template_name: str
    parameters: dict[str, Any]
    project_path: str | None = None
    target_component: str | None = None
    use_ai_suggestions: bool = True
    validate_before_generation: bool = True


@dataclass
class GenerationResult:
    """Result of script generation."""

    success: bool
    script_content: str | None = None
    metadata: ScriptMetadata | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    related_scripts: list[str] = field(default_factory=list)


class DynamicScriptGenerator:
    """Dynamic script generation engine with real-time capabilities."""

    def __init__(
        self,
        templates_dir: str | Path = "templates",
        graph_client: IgnitionGraphClient | None = None,
        enable_caching: bool = True,
        cache_size: int = 100,
    ) -> None:
        """Initialize the dynamic script generator.

        Args:
            templates_dir: Path to templates directory
            graph_client: Optional Neo4j graph client for intelligence
            enable_caching: Whether to enable template caching
            cache_size: Maximum number of cached templates
        """
        self.templates_dir = Path(templates_dir)
        self.graph_client = graph_client
        self.enable_caching = enable_caching
        self.cache_size = cache_size

        # Initialize base generator
        self.base_generator = IgnitionScriptGenerator(templates_dir)

        # Template cache
        self._template_cache: dict[str, Template] = {}
        self._cache_access_times: dict[str, datetime] = {}

        # Context validators
        self._validators: dict[ScriptContext, list[Callable]] = {
            context: [] for context in ScriptContext
        }

        # Script history for suggestions
        self._generation_history: list[GenerationRequest] = []

        # Logger
        self.logger = logging.getLogger(__name__)

        # Initialize default validators
        self._setup_default_validators()

    def _setup_default_validators(self) -> None:
        """Set up default validators for each context."""
        # Gateway validators
        self._validators[ScriptContext.GATEWAY].extend(
            [
                self._validate_gateway_permissions,
                self._validate_gateway_resources,
            ]
        )

        # Tag validators
        self._validators[ScriptContext.TAG].extend(
            [
                self._validate_tag_path,
                self._validate_tag_permissions,
            ]
        )

        # Vision validators
        self._validators[ScriptContext.VISION].extend(
            [
                self._validate_component_path,
                self._validate_vision_permissions,
            ]
        )

        # Perspective validators
        self._validators[ScriptContext.PERSPECTIVE].extend(
            [
                self._validate_perspective_scope,
                self._validate_perspective_bindings,
            ]
        )

    def generate_script(self, request: GenerationRequest) -> GenerationResult:
        """Generate a script based on the request.

        Args:
            request: Generation request with parameters

        Returns:
            Generation result with script content and metadata
        """
        result = GenerationResult(success=False)

        try:
            # Validate request if enabled
            if request.validate_before_generation:
                validation_errors = self._validate_request(request)
                if validation_errors:
                    result.errors.extend(validation_errors)
                    return result

            # Get AI suggestions if enabled
            if request.use_ai_suggestions and self.graph_client:
                suggestions = self._get_ai_suggestions(request)
                result.suggestions.extend(suggestions)

                # Apply AI-suggested improvements to parameters
                request.parameters = self._apply_ai_improvements(
                    request.parameters, suggestions
                )

            # Generate script using base generator
            script_content = self.base_generator.generate_script(
                request.template_name, request.parameters
            )

            # Post-process script
            script_content = self._post_process_script(script_content, request.context)

            # Create metadata
            metadata = ScriptMetadata(
                name=request.parameters.get("script_name", "Untitled Script"),
                context=request.context,
                description=request.parameters.get("description", ""),
                template_name=request.template_name,
                tags=request.parameters.get("tags", []),
                parameters=request.parameters,
                suggestions=result.suggestions,
            )

            # Find related scripts
            if self.graph_client:
                related_scripts = self._find_related_scripts(request)
                result.related_scripts.extend(related_scripts)

            # Update history
            self._generation_history.append(request)
            if len(self._generation_history) > 1000:
                self._generation_history = self._generation_history[-1000:]

            # Set result
            result.success = True
            result.script_content = script_content
            result.metadata = metadata

        except Exception as e:
            self.logger.error(f"Script generation failed: {e}")
            result.errors.append(str(e))

        return result

    def _validate_request(self, request: GenerationRequest) -> list[str]:
        """Validate generation request.

        Args:
            request: Generation request to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Run context-specific validators
        validators = self._validators.get(request.context, [])
        for validator in validators:
            validator_errors = validator(request)
            errors.extend(validator_errors)

        # Validate template exists
        if request.template_name not in self.base_generator.list_templates():
            errors.append(f"Template '{request.template_name}' not found")

        # Validate required parameters
        required_params = self._get_required_parameters(request.template_name)
        missing_params = [
            param for param in required_params if param not in request.parameters
        ]
        if missing_params:
            errors.append(f"Missing required parameters: {', '.join(missing_params)}")

        return errors

    def _get_ai_suggestions(self, request: GenerationRequest) -> list[str]:
        """Get AI-powered suggestions for script generation.

        Args:
            request: Generation request

        Returns:
            List of suggestions
        """
        suggestions = []

        if not self.graph_client:
            return suggestions

        try:
            # Query similar scripts from graph
            query = """
            MATCH (s:Script)-[:USES_TEMPLATE]->(t:Template {name: $template_name})
            WHERE s.context = $context
            WITH s, t
            MATCH (s)-[:HAS_PARAMETER]->(p:Parameter)
            RETURN s.name as script_name,
                   collect(p.name) as parameters,
                   s.description as description
            LIMIT 5
            """

            results = self.graph_client.execute_query(
                query,
                {
                    "template_name": request.template_name,
                    "context": request.context.value,
                },
            )

            # Generate suggestions based on similar scripts
            for record in results:
                script_name = record.get("script_name", "")
                params = record.get("parameters", [])

                # Suggest missing parameters
                for param in params:
                    if param not in request.parameters:
                        suggestions.append(
                            f"Consider adding parameter '{param}' (used in similar script '{script_name}')"
                        )

            # Get best practices from graph
            best_practices_query = """
            MATCH (bp:BestPractice)-[:APPLIES_TO]->(c:Context {name: $context})
            WHERE bp.template = $template_name OR bp.template IS NULL
            RETURN bp.suggestion as suggestion
            LIMIT 3
            """

            bp_results = self.graph_client.execute_query(
                best_practices_query,
                {
                    "context": request.context.value,
                    "template_name": request.template_name,
                },
            )

            for record in bp_results:
                suggestion = record.get("suggestion")
                if suggestion:
                    suggestions.append(suggestion)

        except Exception as e:
            self.logger.warning(f"Failed to get AI suggestions: {e}")

        return suggestions

    def _apply_ai_improvements(
        self, parameters: dict[str, Any], suggestions: list[str]
    ) -> dict[str, Any]:
        """Apply AI-suggested improvements to parameters.

        Args:
            parameters: Original parameters
            suggestions: AI suggestions

        Returns:
            Improved parameters
        """
        improved_params = parameters.copy()

        # Apply specific improvements based on suggestions
        for suggestion in suggestions:
            if "error handling" in suggestion.lower():
                improved_params.setdefault("enable_error_handling", True)
                improved_params.setdefault("error_handler", "system.util.getLogger")

            if "logging" in suggestion.lower():
                improved_params.setdefault("enable_logging", True)
                improved_params.setdefault("log_level", "INFO")

            if "validation" in suggestion.lower():
                improved_params.setdefault("enable_validation", True)

            if "performance" in suggestion.lower():
                improved_params.setdefault("optimize_performance", True)

        return improved_params

    def _post_process_script(self, script_content: str, context: ScriptContext) -> str:
        """Post-process generated script.

        Args:
            script_content: Generated script content
            context: Script context

        Returns:
            Post-processed script content
        """
        # Add context-specific headers
        header = f"""# Generated by IGN Scripts Dynamic Script Generator
# Context: {context.value}
# Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Version: 1.0.0

"""

        # Add context-specific imports
        if context == ScriptContext.GATEWAY:
            header += "# Gateway-specific imports\n"
            header += "from com.inductiveautomation.ignition.gateway import IgnitionGateway\n\n"
        elif context == ScriptContext.PERSPECTIVE:
            header += "# Perspective-specific imports\n"
            header += "from com.inductiveautomation.perspective.gateway.api import PerspectiveContext\n\n"

        return header + script_content

    def _find_related_scripts(self, request: GenerationRequest) -> list[str]:
        """Find related scripts using graph intelligence.

        Args:
            request: Generation request

        Returns:
            List of related script names
        """
        related = []

        if not self.graph_client:
            return related

        try:
            query = """
            MATCH (t:Template {name: $template_name})<-[:USES_TEMPLATE]-(s:Script)
            WHERE s.context = $context
            RETURN DISTINCT s.name as script_name
            LIMIT 10
            """

            results = self.graph_client.execute_query(
                query,
                {
                    "template_name": request.template_name,
                    "context": request.context.value,
                },
            )

            for record in results:
                script_name = record.get("script_name")
                if script_name:
                    related.append(script_name)

        except Exception as e:
            self.logger.warning(f"Failed to find related scripts: {e}")

        return related

    def _get_required_parameters(self, template_name: str) -> list[str]:
        """Get required parameters for a template.

        Args:
            template_name: Template name

        Returns:
            List of required parameter names
        """
        # This would ideally be extracted from template metadata
        # For now, return common required parameters
        required = ["script_name", "component_name"]

        if "tag" in template_name.lower():
            required.append("tag_path")
        elif "database" in template_name.lower():
            required.append("database_name")
        elif "alarm" in template_name.lower():
            required.append("alarm_name")

        return required

    # Validators
    def _validate_gateway_permissions(self, request: GenerationRequest) -> list[str]:
        """Validate gateway permissions."""
        errors = []
        if request.context == ScriptContext.GATEWAY:
            # Check if user has gateway scripting permissions
            # This would integrate with Ignition's security system
            pass
        return errors

    def _validate_gateway_resources(self, request: GenerationRequest) -> list[str]:
        """Validate gateway resource availability."""
        errors = []
        if request.context == ScriptContext.GATEWAY:
            # Check if required resources are available
            # This would check system resources, modules, etc.
            pass
        return errors

    def _validate_tag_path(self, request: GenerationRequest) -> list[str]:
        """Validate tag path format."""
        errors = []
        if request.context == ScriptContext.TAG:
            tag_path = request.parameters.get("tag_path")
            if not tag_path:
                errors.append("Tag path is required for tag scripts")
            elif not tag_path.startswith("["):
                errors.append("Tag path must start with provider name in brackets")
        return errors

    def _validate_tag_permissions(self, request: GenerationRequest) -> list[str]:
        """Validate tag permissions."""
        errors = []
        if request.context == ScriptContext.TAG:
            # Check if user has permissions to create tag scripts
            pass
        return errors

    def _validate_component_path(self, request: GenerationRequest) -> list[str]:
        """Validate Vision component path."""
        errors = []
        if request.context == ScriptContext.VISION:
            component_path = request.parameters.get("component_path")
            if not component_path:
                errors.append("Component path is required for Vision scripts")
        return errors

    def _validate_vision_permissions(self, request: GenerationRequest) -> list[str]:
        """Validate Vision permissions."""
        errors = []
        if request.context == ScriptContext.VISION:
            # Check Vision module permissions
            pass
        return errors

    def _validate_perspective_scope(self, request: GenerationRequest) -> list[str]:
        """Validate Perspective scope."""
        errors = []
        if request.context == ScriptContext.PERSPECTIVE:
            scope = request.parameters.get("scope", "page")
            if scope not in ["page", "session", "view"]:
                errors.append(f"Invalid Perspective scope: {scope}")
        return errors

    def _validate_perspective_bindings(self, request: GenerationRequest) -> list[str]:
        """Validate Perspective bindings."""
        errors = []
        if request.context == ScriptContext.PERSPECTIVE:
            # Validate binding configuration
            bindings = request.parameters.get("bindings", {})
            if not isinstance(bindings, dict):
                errors.append("Bindings must be a dictionary")
        return errors

    def get_template_info(self, template_name: str) -> dict[str, Any]:
        """Get information about a template.

        Args:
            template_name: Template name

        Returns:
            Template information dictionary
        """
        info = {
            "name": template_name,
            "exists": template_name in self.base_generator.list_templates(),
            "required_parameters": self._get_required_parameters(template_name),
            "description": "",
            "examples": [],
        }

        # Get template description from graph if available
        if self.graph_client:
            try:
                query = """
                MATCH (t:Template {name: $name})
                RETURN t.description as description,
                       t.examples as examples
                """

                results = self.graph_client.execute_query(
                    query, {"name": template_name}
                )

                if results:
                    record = results[0]
                    info["description"] = record.get("description", "")
                    info["examples"] = record.get("examples", [])

            except Exception as e:
                self.logger.warning(f"Failed to get template info from graph: {e}")

        return info

    def suggest_templates(
        self, context: ScriptContext, keywords: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Suggest templates based on context and keywords.

        Args:
            context: Script context
            keywords: Optional keywords to filter by

        Returns:
            List of template suggestions with metadata
        """
        suggestions = []
        all_templates = self.base_generator.list_templates()

        # Filter by context
        context_templates = [t for t in all_templates if context.value in t.lower()]

        # Filter by keywords if provided
        if keywords:
            keyword_lower = [k.lower() for k in keywords]
            context_templates = [
                t
                for t in context_templates
                if any(k in t.lower() for k in keyword_lower)
            ]

        # Get template info for each
        for template in context_templates[:10]:  # Limit to 10 suggestions
            info = self.get_template_info(template)
            suggestions.append(info)

        # Sort by relevance (templates with descriptions first)
        suggestions.sort(key=lambda x: bool(x.get("description")), reverse=True)

        return suggestions
