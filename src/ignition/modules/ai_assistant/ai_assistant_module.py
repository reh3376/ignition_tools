"""AI Assistant Module for Ignition Development.

This module provides AI-powered assistance for Ignition development, including:
- Intelligent code analysis and validation
- Context-aware script suggestions
- Knowledge graph-based validation
- AST-based code parsing and analysis
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from src.ignition.modules.base import (
    AbstractIgnitionModule,
    ModuleConfig,
    ModuleContext,
)

from .code_analyzer import AnalysisResult, CodeAnalyzer
from .knowledge_validator import KnowledgeValidator, ScriptValidationResult

logger = logging.getLogger(__name__)


@dataclass
class AIAssistantConfig:
    """Configuration for AI Assistant Module."""

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    enable_web_crawling: bool = True
    enable_hallucination_detection: bool = True
    confidence_threshold: float = 0.7
    max_suggestions: int = 5


@dataclass
class CodeAnalysisRequest:
    """Request for code analysis."""

    code: str | None = None
    file_path: str | None = None
    validate_against_knowledge_graph: bool = True
    detect_hallucinations: bool = True


@dataclass
class CodeAnalysisResponse:
    """Response from code analysis."""

    analysis_result: AnalysisResult | None = None
    validation_result: ScriptValidationResult | None = None
    confidence_score: float = 0.0
    suggestions: list[str] = field(default_factory=list)
    hallucinations_detected: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class AIAssistantModule(AbstractIgnitionModule):
    """AI Assistant Module for intelligent Ignition development assistance."""

    def __init__(self, context: ModuleContext):
        super().__init__(context.config)
        self._context = context
        self.ai_config = AIAssistantConfig()
        self.code_analyzer = CodeAnalyzer()
        self.knowledge_validator: KnowledgeValidator | None = None

    async def initialize(self, context: ModuleContext | None = None) -> bool:
        """Initialize the AI Assistant Module."""
        try:
            logger.info("Initializing AI Assistant Module...")
            if context:
                self._context = context

            # Load configuration from environment
            await self._load_configuration()

            # Initialize knowledge validator if Neo4j is available
            if self._is_neo4j_available():
                self.knowledge_validator = KnowledgeValidator(
                    neo4j_uri=self.ai_config.neo4j_uri,
                    neo4j_user=self.ai_config.neo4j_user,
                    neo4j_password=self.ai_config.neo4j_password,
                )
                await self.knowledge_validator.initialize()
                logger.info("Knowledge graph validator initialized")
            else:
                logger.warning(
                    "Neo4j not available - knowledge graph validation disabled"
                )

            self._set_initialized(True)
            logger.info("AI Assistant Module initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize AI Assistant Module: {e}")
            return False

    async def shutdown(self) -> bool:
        """Shutdown the AI Assistant Module."""
        try:
            logger.info("Shutting down AI Assistant Module...")

            if self.knowledge_validator:
                await self.knowledge_validator.close()

            self._set_initialized(False)
            logger.info("AI Assistant Module shutdown complete")
            return True

        except Exception as e:
            logger.error(f"Error during AI Assistant Module shutdown: {e}")
            return False

    async def analyze_code(self, request: CodeAnalysisRequest) -> CodeAnalysisResponse:
        """Analyze code for potential issues and provide suggestions."""
        if not self.is_initialized:
            raise RuntimeError("AI Assistant Module not initialized")

        response = CodeAnalysisResponse()

        try:
            # Step 1: Perform AST analysis
            if request.code:
                response.analysis_result = self.code_analyzer.analyze_code_string(
                    request.code, request.file_path or "<string>"
                )
            elif request.file_path:
                response.analysis_result = self.code_analyzer.analyze_script(
                    request.file_path
                )
            else:
                response.errors.append("Either code or file_path must be provided")
                return response

            # Step 2: Validate against knowledge graph if requested and available
            if request.validate_against_knowledge_graph and self.knowledge_validator:
                response.validation_result = (
                    await self.knowledge_validator.validate_script(
                        response.analysis_result
                    )
                )
                response.confidence_score = (
                    response.validation_result.overall_confidence
                )
                response.hallucinations_detected = (
                    response.validation_result.hallucinations_detected
                )

                # Generate suggestions based on validation results
                response.suggestions = self._generate_suggestions(
                    response.validation_result
                )

            # Step 3: Add analysis errors to response
            if response.analysis_result and response.analysis_result.errors:
                response.errors.extend(response.analysis_result.errors)

            logger.info(
                f"Code analysis completed with confidence: {response.confidence_score:.2%}"
            )

        except Exception as e:
            error_msg = f"Code analysis failed: {e!s}"
            logger.error(error_msg)
            response.errors.append(error_msg)

        return response

    async def analyze_file(self, file_path: str) -> CodeAnalysisResponse:
        """Convenience method to analyze a file."""
        request = CodeAnalysisRequest(
            file_path=file_path,
            validate_against_knowledge_graph=True,
            detect_hallucinations=True,
        )
        return await self.analyze_code(request)

    async def analyze_code_string(
        self, code: str, file_path: str = "<string>"
    ) -> CodeAnalysisResponse:
        """Convenience method to analyze code from string."""
        request = CodeAnalysisRequest(
            code=code,
            file_path=file_path,
            validate_against_knowledge_graph=True,
            detect_hallucinations=True,
        )
        return await self.analyze_code(request)

    def get_module_info(self) -> dict[str, Any]:
        """Get comprehensive module information."""
        return {
            "module_name": "AI Assistant",
            "version": "1.0.0",
            "description": "AI-powered assistance for Ignition development",
            "features": [
                "AST-based code analysis",
                "Knowledge graph validation",
                "Hallucination detection",
                "Import validation",
                "Method signature checking",
                "Parameter validation",
                "Confidence scoring",
                "Intelligent suggestions",
            ],
            "status": "initialized" if self.is_initialized else "not_initialized",
            "configuration": {
                "neo4j_enabled": self.knowledge_validator is not None,
                "neo4j_uri": self.ai_config.neo4j_uri,
                "confidence_threshold": self.ai_config.confidence_threshold,
                "max_suggestions": self.ai_config.max_suggestions,
                "web_crawling_enabled": self.ai_config.enable_web_crawling,
                "hallucination_detection_enabled": self.ai_config.enable_hallucination_detection,
            },
            "capabilities": [
                "Python AST parsing and analysis",
                "Import statement validation",
                "Class instantiation tracking",
                "Method call analysis",
                "Attribute access validation",
                "Function call verification",
                "Variable type inference",
                "Context-aware validation",
                "Similarity-based suggestions",
                "Confidence-based scoring",
            ],
        }

    async def get_statistics(self) -> dict[str, Any]:
        """Get module statistics."""
        stats: Any = {
            "module_status": "active" if self.is_initialized else "inactive",
            "knowledge_graph_available": self.knowledge_validator is not None,
            "total_analyses_performed": 0,  # Would track in production
            "average_confidence_score": 0.0,  # Would calculate from history
            "common_issues_detected": [],  # Would track patterns
        }

        if self.knowledge_validator:
            stats.update(
                {
                    "cached_modules": len(self.knowledge_validator.module_cache),
                    "cached_classes": len(self.knowledge_validator.class_cache),
                    "cached_methods": len(self.knowledge_validator.method_cache),
                }
            )

        return stats

    async def get_status(self) -> dict[str, Any]:
        """Get the current status of the module."""
        return {
            "module": "AI Assistant",
            "version": "1.0.0",
            "status": "active" if self.is_initialized else "inactive",
            "neo4j_available": self.knowledge_validator is not None,
            "features_enabled": {
                "code_analysis": True,
                "knowledge_validation": self.knowledge_validator is not None,
                "hallucination_detection": self.ai_config.enable_hallucination_detection,
                "web_crawling": self.ai_config.enable_web_crawling,
            },
        }

    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process a request to the module."""
        try:
            request_type = request.get("type", "analyze_code")

            if request_type == "analyze_code":
                # Convert dict to CodeAnalysisRequest
                analysis_request = CodeAnalysisRequest(
                    code=request.get("code"),
                    file_path=request.get("file_path"),
                    validate_against_knowledge_graph=request.get(
                        "validate_against_knowledge_graph", True
                    ),
                    detect_hallucinations=request.get("detect_hallucinations", True),
                )

                response = await self.analyze_code(analysis_request)

                # Convert response to dict
                return {
                    "success": True,
                    "analysis_result": (
                        response.analysis_result.__dict__
                        if response.analysis_result
                        else None
                    ),
                    "validation_result": (
                        response.validation_result.__dict__
                        if response.validation_result
                        else None
                    ),
                    "confidence_score": response.confidence_score,
                    "suggestions": response.suggestions,
                    "hallucinations_detected": response.hallucinations_detected,
                    "errors": response.errors,
                }

            elif request_type == "get_info":
                return {"success": True, "info": self.get_module_info()}

            elif request_type == "get_statistics":
                return {"success": True, "statistics": await self.get_statistics()}

            else:
                return {
                    "success": False,
                    "error": f"Unknown request type: {request_type}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _load_configuration(self) -> bool:
        """Load configuration from environment variables."""
        # Load from environment variables
        self.ai_config.neo4j_uri = os.getenv("NEO4J_URI", self.ai_config.neo4j_uri)
        self.ai_config.neo4j_user = os.getenv("NEO4J_USER", self.ai_config.neo4j_user)
        self.ai_config.neo4j_password = os.getenv(
            "NEO4J_PASSWORD", self.ai_config.neo4j_password
        )

        # Load from module configuration if available
        ai_config_data = self.config.get("ai_assistant", {})
        if ai_config_data:
            self.ai_config.confidence_threshold = ai_config_data.get(
                "confidence_threshold", self.ai_config.confidence_threshold
            )
            self.ai_config.max_suggestions = ai_config_data.get(
                "max_suggestions", self.ai_config.max_suggestions
            )
            self.ai_config.enable_web_crawling = ai_config_data.get(
                "enable_web_crawling", self.ai_config.enable_web_crawling
            )
            self.ai_config.enable_hallucination_detection = ai_config_data.get(
                "enable_hallucination_detection",
                self.ai_config.enable_hallucination_detection,
            )

        logger.info(
            f"AI Assistant configuration loaded: confidence_threshold={self.ai_config.confidence_threshold}"
        )

    def _is_neo4j_available(self) -> bool:
        """Check if Neo4j is available."""
        try:
            # Try to import neo4j driver
            from neo4j import GraphDatabase

            # Try to connect briefly to test availability
            driver = GraphDatabase.driver(
                self.ai_config.neo4j_uri,
                auth=(self.ai_config.neo4j_user, self.ai_config.neo4j_password),
            )

            with driver.session() as session:
                session.run("RETURN 1")

            driver.close()
            return True

        except Exception as e:
            logger.debug(f"Neo4j not available: {e}")
            return False

    def _generate_suggestions(
        self, validation_result: ScriptValidationResult
    ) -> list[str]:
        """Generate intelligent suggestions based on validation results."""
        suggestions = []

        # Collect suggestions from all validation results
        for import_val in validation_result.import_validations:
            suggestions.extend(import_val.validation.suggestions)

        for class_val in validation_result.class_validations:
            suggestions.extend(class_val.validation.suggestions)

        for method_val in validation_result.method_validations:
            suggestions.extend(method_val.validation.suggestions)

        for attr_val in validation_result.attribute_validations:
            suggestions.extend(attr_val.validation.suggestions)

        for func_val in validation_result.function_validations:
            suggestions.extend(func_val.validation.suggestions)

        # Remove duplicates and limit to max_suggestions
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[: self.ai_config.max_suggestions]


def create_ai_assistant_module() -> AIAssistantModule:
    """Factory function to create AI Assistant Module with default configuration."""
    # Create default module configuration
    config = ModuleConfig(
        name="ai_assistant",
        version="1.0.0",
        enabled=True,
        security={
            "require_authentication": False,
            "allowed_roles": ["developer", "admin"],
            "rate_limit": 100,
        },
    )

    # Create module context
    context = ModuleContext(config=config, logger=logger, metrics={})

    module = AIAssistantModule(context)
    return module
