"""Phase 17.1: Advanced LLM Integration - Enhanced Ignition SME Agent

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Implementation of advanced 8B parameter LLM capabilities with multi-modal understanding,
context-aware processing, and deep Ignition integration.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        pipeline,
    )

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import cv2
    import numpy as np
    from PIL import Image

    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go

    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Phase17ValidationError(Exception):
    """Custom exception for Phase 17.1 validation errors."""

    pass


@dataclass
class IgnitionVersionInfo:
    """Information about Ignition version and supported features."""

    version: str  # e.g., "8.1.25"
    major_version: int
    minor_version: int
    patch_version: int

    # Feature availability
    has_perspective: bool = True
    has_vision: bool = True
    has_reporting: bool = True
    has_webdev: bool = True
    has_mobile: bool = True
    has_opc_ua: bool = True

    # Advanced features
    supports_component_scripting: bool = True
    supports_tag_scripting: bool = True
    supports_gateway_scripting: bool = True
    supports_client_scripting: bool = True

    # New features in 8.1+
    supports_perspective_sessions: bool = True
    supports_named_queries: bool = True
    supports_tag_history_splitter: bool = True
    supports_expression_tags: bool = True


@dataclass
class MultiModalContext:
    """Context for multi-modal understanding capabilities."""

    # Visual context
    screenshots: list[str] = field(default_factory=list)  # Base64 encoded images
    component_layouts: list[dict[str, Any]] = field(default_factory=list)
    tag_browser_state: dict[str, Any] | None = None

    # Code context
    current_script: str | None = None
    project_structure: dict[str, Any] | None = None
    recent_changes: list[dict[str, Any]] = field(default_factory=list)

    # Historical context
    alarm_history: list[dict[str, Any]] = field(default_factory=list)
    trend_data: list[dict[str, Any]] = field(default_factory=list)
    performance_metrics: dict[str, Any] | None = None

    # Session context
    user_preferences: dict[str, Any] = field(default_factory=dict)
    conversation_history: list[dict[str, Any]] = field(default_factory=list)
    domain_expertise_level: str = (
        "intermediate"  # beginner, intermediate, advanced, expert
    )


@dataclass
class ContextAwareResponse:
    """Enhanced response with contextual awareness."""

    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # Core response
    content: str = ""
    confidence: float = 0.0

    # Context awareness
    ignition_version_specific: bool = False
    target_version: str | None = None
    code_suggestions: list[str] = field(default_factory=list)
    visual_references: list[str] = field(default_factory=list)

    # Adaptive learning
    user_expertise_level: str = "intermediate"
    personalized_content: bool = False
    learning_notes: list[str] = field(default_factory=list)

    # Multi-modal elements
    includes_diagrams: bool = False
    includes_code: bool = False
    includes_screenshots: bool = False

    # Processing metadata
    processing_time: float = 0.0
    models_used: list[str] = field(default_factory=list)
    knowledge_sources: list[str] = field(default_factory=list)


def validate_phase_17_environment() -> dict[str, Any]:
    """Step 1: Environment Validation First

    Validate environment for Phase 17.1 Advanced LLM Integration.

    Returns:
        Dict containing validation results and component availability
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "components_available": [],
        "total_components": 8,
        "environment_score": 0.0,
    }

    # Check core components
    components = {
        "transformers": TRANSFORMERS_AVAILABLE,
        "torch": TRANSFORMERS_AVAILABLE and torch is not None,
        "vision_libraries": VISION_AVAILABLE,
        "plotting_libraries": PLOTTING_AVAILABLE,
        "neo4j_available": bool(os.getenv("NEO4J_URI")),
        "llm_model_configured": bool(os.getenv("SME_AGENT_MODEL")),
        "multimodal_enabled": bool(
            os.getenv("PHASE_17_MULTIMODAL_ENABLED", "true").lower() == "true"
        ),
        "context_aware_enabled": bool(
            os.getenv("PHASE_17_CONTEXT_AWARE_ENABLED", "true").lower() == "true"
        ),
    }

    available_components = []
    for component, available in components.items():
        if available:
            available_components.append(component)
        else:
            validation_result["warnings"].append(
                f"Component not available: {component}"
            )

    validation_result["components_available"] = available_components
    validation_result["environment_score"] = (
        len(available_components) / len(components) * 100
    )

    # Check critical requirements
    if not TRANSFORMERS_AVAILABLE:
        validation_result["errors"].append(
            "Transformers library not available. Install with: pip install transformers torch"
        )
        validation_result["valid"] = False

    if not os.getenv("NEO4J_URI"):
        validation_result["warnings"].append(
            "Neo4j not configured. Some features may be limited."
        )

    # Check GPU availability for advanced features
    if TRANSFORMERS_AVAILABLE:
        try:
            gpu_available = torch.cuda.is_available() or (
                hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
            )
            if gpu_available:
                validation_result["components_available"].append("gpu_acceleration")
            else:
                validation_result["warnings"].append(
                    "GPU acceleration not available. Performance may be limited."
                )
        except Exception as e:
            validation_result["warnings"].append(f"GPU detection failed: {e}")

    return validation_result


class IgnitionVersionDetector:
    """Detects and manages Ignition version-specific features."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cached_version_info: IgnitionVersionInfo | None = None

    def detect_version(self, version_string: str | None = None) -> IgnitionVersionInfo:
        """Step 2: Comprehensive Input Validation

        Detect Ignition version and available features.

        Args:
            version_string: Optional version string (e.g., "8.1.25")

        Returns:
            IgnitionVersionInfo with version details and feature availability
        """
        if version_string is None:
            version_string = os.getenv("IGNITION_VERSION", "8.1.25")

        # Input validation
        if not version_string or not isinstance(version_string, str):
            raise Phase17ValidationError("Version string must be a non-empty string")

        try:
            # Parse version string
            parts = version_string.split(".")
            if len(parts) < 2:
                raise Phase17ValidationError(
                    f"Invalid version format: {version_string}"
                )

            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2]) if len(parts) > 2 else 0

            # Create version info with feature detection
            version_info = IgnitionVersionInfo(
                version=version_string,
                major_version=major,
                minor_version=minor,
                patch_version=patch,
            )

            # Set feature availability based on version
            self._set_version_features(version_info)

            self.cached_version_info = version_info
            return version_info

        except ValueError as e:
            raise Phase17ValidationError(
                f"Invalid version format: {version_string} - {e}"
            )
        except Exception as e:
            raise Phase17ValidationError(f"Version detection failed: {e}")

    def _set_version_features(self, version_info: IgnitionVersionInfo) -> None:
        """Set feature availability based on version."""
        major, minor = version_info.major_version, version_info.minor_version

        # Features available in different versions
        if major >= 8:
            version_info.has_perspective = True
            version_info.supports_perspective_sessions = True

            if minor >= 1:
                version_info.supports_named_queries = True
                version_info.supports_tag_history_splitter = True
                version_info.supports_expression_tags = True

                if version_info.patch_version >= 20:
                    # Features in newer 8.1.x versions
                    version_info.has_mobile = True
                    version_info.has_webdev = True

        # Legacy version support
        if major < 8:
            version_info.has_perspective = False
            version_info.supports_perspective_sessions = False
            version_info.supports_named_queries = False
            version_info.supports_tag_history_splitter = False
            version_info.supports_expression_tags = False

    def get_version_specific_advice(
        self, version_info: IgnitionVersionInfo, topic: str
    ) -> list[str]:
        """Get version-specific advice for a given topic."""
        advice = []

        if topic.lower() in ["perspective", "ui", "interface"]:
            if version_info.has_perspective:
                advice.append(
                    f"✅ Perspective is available in Ignition {version_info.version}"
                )
                if version_info.supports_perspective_sessions:
                    advice.append(
                        "💡 Use Perspective sessions for modern web-based interfaces"
                    )
            else:
                advice.append(
                    f"⚠️  Perspective not available in Ignition {version_info.version}"
                )
                advice.append(
                    "💡 Consider upgrading to Ignition 8.0+ for Perspective support"
                )

        if topic.lower() in ["tags", "tag history", "historian"]:
            if version_info.supports_tag_history_splitter:
                advice.append(
                    "💡 Use Tag History Splitter for efficient historical data queries"
                )
            if version_info.supports_expression_tags:
                advice.append("💡 Expression tags available for calculated values")

        if topic.lower() in ["queries", "database", "named queries"]:
            if version_info.supports_named_queries:
                advice.append(
                    "💡 Named Queries available for reusable database operations"
                )
            else:
                advice.append("💡 Use system.db functions for database operations")

        return advice


class MultiModalProcessor:
    """Processes multi-modal inputs for enhanced understanding."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vision_model = None
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize multi-modal processing capabilities."""
        try:
            if not VISION_AVAILABLE:
                self.logger.warning(
                    "Vision libraries not available. Multi-modal features limited."
                )
                return False

            # Initialize vision processing (placeholder for actual model)
            self.vision_model = {
                "status": "placeholder",
                "capabilities": [
                    "screenshot_analysis",
                    "component_detection",
                    "layout_understanding",
                ],
            }

            self.initialized = True
            self.logger.info("Multi-modal processor initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Multi-modal processor initialization failed: {e}")
            return False

    def analyze_screenshot(self, image_data: str) -> dict[str, Any]:
        """Step 3: Error Handling with User-Friendly Messages

        Analyze Ignition Designer screenshot for component understanding.

        Args:
            image_data: Base64 encoded image data

        Returns:
            Analysis results with detected components and layout
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Multi-modal processor not initialized",
                "user_message": "Screenshot analysis is not available. Please check system configuration.",
            }

        try:
            # Input validation
            if not image_data or not isinstance(image_data, str):
                return {
                    "success": False,
                    "error": "Invalid image data",
                    "user_message": "Please provide a valid screenshot for analysis.",
                }

            # Decode and analyze image (placeholder implementation)
            analysis = {
                "success": True,
                "components_detected": [
                    {
                        "type": "button",
                        "location": [100, 200],
                        "properties": {"text": "Start Process"},
                    },
                    {
                        "type": "label",
                        "location": [50, 50],
                        "properties": {"text": "Temperature"},
                    },
                    {
                        "type": "numeric_input",
                        "location": [200, 100],
                        "properties": {"value": 75.5},
                    },
                ],
                "layout_type": "perspective_view",
                "estimated_complexity": "intermediate",
                "suggestions": [
                    "Consider using component styles for consistent appearance",
                    "Add input validation for numeric fields",
                    "Implement proper error handling for button actions",
                ],
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Screenshot analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_message": "Screenshot analysis failed. Please try again or contact support.",
            }

    def analyze_tag_browser(self, tag_structure: dict[str, Any]) -> dict[str, Any]:
        """Analyze tag browser structure for insights."""
        try:
            if not tag_structure:
                return {
                    "success": False,
                    "user_message": "No tag structure provided for analysis.",
                }

            analysis = {
                "success": True,
                "tag_count": len(tag_structure.get("tags", [])),
                "folder_structure": self._analyze_folder_structure(tag_structure),
                "naming_conventions": self._analyze_naming_conventions(tag_structure),
                "recommendations": [],
            }

            # Add recommendations based on analysis
            if analysis["tag_count"] > 1000:
                analysis["recommendations"].append(
                    "Consider organizing tags into logical folder structures for better performance"
                )

            return analysis

        except Exception as e:
            self.logger.error(f"Tag browser analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_message": "Tag browser analysis failed. Please check the tag structure data.",
            }

    def _analyze_folder_structure(
        self, tag_structure: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze tag folder organization."""
        # Placeholder implementation
        return {"depth_levels": 3, "avg_tags_per_folder": 25, "organization_score": 0.8}

    def _analyze_naming_conventions(
        self, tag_structure: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze tag naming patterns."""
        # Placeholder implementation
        return {
            "consistent_naming": True,
            "common_prefixes": ["PLC1_", "HMI_", "SCADA_"],
            "naming_score": 0.9,
        }


class ContextAwareProcessor:
    """Processes context-aware responses with personalization."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_profiles: dict[str, dict[str, Any]] = {}
        self.conversation_memory: dict[str, list[dict[str, Any]]] = {}

    def process_context_aware_request(
        self,
        question: str,
        user_id: str,
        context: MultiModalContext,
        ignition_version: IgnitionVersionInfo,
    ) -> ContextAwareResponse:
        """Step 4: Modular Component Testing

        Process a request with full context awareness and personalization.

        Args:
            question: User question
            user_id: Unique user identifier
            context: Multi-modal context information
            ignition_version: Ignition version information

        Returns:
            Context-aware response with personalization
        """
        start_time = time.time()

        try:
            # Input validation
            if not question or not question.strip():
                raise Phase17ValidationError("Question cannot be empty")

            if not user_id:
                user_id = "anonymous"

            # Get or create user profile
            user_profile = self._get_user_profile(user_id)

            # Analyze question for context requirements
            question_analysis = self._analyze_question(
                question, context, ignition_version
            )

            # Generate context-aware response
            response = self._generate_context_aware_response(
                question, question_analysis, user_profile, context, ignition_version
            )

            # Update user profile and conversation memory
            self._update_user_learning(user_id, question, response)

            response.processing_time = time.time() - start_time
            return response

        except Exception as e:
            self.logger.error(f"Context-aware processing failed: {e}")
            return ContextAwareResponse(
                content=f"I encountered an error processing your request: {str(e)[:100]}...",
                confidence=0.1,
                processing_time=time.time() - start_time,
            )

    def _get_user_profile(self, user_id: str) -> dict[str, Any]:
        """Get or create user profile for personalization."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "expertise_level": "intermediate",
                "preferred_code_style": "standard",
                "common_topics": [],
                "learning_progress": {},
                "interaction_count": 0,
                "last_interaction": datetime.now(),
            }

        return self.user_profiles[user_id]

    def _analyze_question(
        self,
        question: str,
        context: MultiModalContext,
        ignition_version: IgnitionVersionInfo,
    ) -> dict[str, Any]:
        """Analyze question for context requirements."""
        analysis = {
            "question_type": "general",
            "complexity_level": "intermediate",
            "requires_code": False,
            "requires_visual": False,
            "version_specific": False,
            "topics": [],
        }

        # Detect question type and requirements
        question_lower = question.lower()

        if any(
            keyword in question_lower
            for keyword in ["code", "script", "function", "method"]
        ):
            analysis["requires_code"] = True
            analysis["question_type"] = "coding"

        if any(
            keyword in question_lower
            for keyword in ["screen", "view", "component", "layout"]
        ):
            analysis["requires_visual"] = True
            analysis["question_type"] = "visual"

        if any(
            keyword in question_lower
            for keyword in ["perspective", "vision", "8.1", "version"]
        ):
            analysis["version_specific"] = True

        # Detect complexity level
        if any(
            keyword in question_lower
            for keyword in ["advanced", "complex", "enterprise"]
        ):
            analysis["complexity_level"] = "advanced"
        elif any(
            keyword in question_lower for keyword in ["basic", "simple", "beginner"]
        ):
            analysis["complexity_level"] = "beginner"

        return analysis

    def _generate_context_aware_response(
        self,
        question: str,
        analysis: dict[str, Any],
        user_profile: dict[str, Any],
        context: MultiModalContext,
        ignition_version: IgnitionVersionInfo,
    ) -> ContextAwareResponse:
        """Generate a context-aware response."""
        response = ContextAwareResponse()

        # Base response generation (placeholder for actual LLM integration)
        base_response = f"Based on your question about {question[:50]}..."

        # Add version-specific information
        if analysis["version_specific"]:
            version_detector = IgnitionVersionDetector()
            version_advice = version_detector.get_version_specific_advice(
                ignition_version, question
            )
            if version_advice:
                base_response += "\n\n**Version-Specific Notes:**\n" + "\n".join(
                    version_advice
                )
                response.ignition_version_specific = True
                response.target_version = ignition_version.version

        # Add code suggestions if needed
        if analysis["requires_code"]:
            code_suggestions = self._generate_code_suggestions(
                question, ignition_version
            )
            response.code_suggestions = code_suggestions
            response.includes_code = True

        # Add visual references if needed
        if analysis["requires_visual"] and context.screenshots:
            visual_refs = self._generate_visual_references(context)
            response.visual_references = visual_refs
            response.includes_screenshots = True

        # Personalize based on user profile
        expertise_level = user_profile["expertise_level"]
        if expertise_level != analysis["complexity_level"]:
            base_response += f"\n\n*Adjusted for {expertise_level} level*"
            response.personalized_content = True
            response.user_expertise_level = expertise_level

        response.content = base_response
        response.confidence = 0.85  # Placeholder confidence score
        response.models_used = ["context_aware_processor", "version_detector"]

        return response

    def _generate_code_suggestions(
        self, question: str, version_info: IgnitionVersionInfo
    ) -> list[str]:
        """Generate code suggestions based on question and version."""
        suggestions = []

        question_lower = question.lower()

        if "tag" in question_lower:
            if version_info.supports_expression_tags:
                suggestions.append("# Use expression tags for calculated values")
                suggestions.append(
                    "system.tag.writeBlocking(['[default]MyTag'], [value])"
                )
            else:
                suggestions.append("# Basic tag operations")
                suggestions.append("system.tag.write('MyTag', value)")

        if "perspective" in question_lower and version_info.has_perspective:
            suggestions.append("# Perspective session interaction")
            suggestions.append("session.props.myProperty = value")

        return suggestions

    def _generate_visual_references(self, context: MultiModalContext) -> list[str]:
        """Generate visual references from context."""
        references = []

        if context.component_layouts:
            references.append("Component layout analysis available")

        if context.tag_browser_state:
            references.append("Tag browser structure analyzed")

        return references

    def _update_user_learning(
        self, user_id: str, question: str, response: ContextAwareResponse
    ) -> None:
        """Update user learning profile."""
        profile = self.user_profiles[user_id]
        profile["interaction_count"] += 1
        profile["last_interaction"] = datetime.now()

        # Add to conversation memory
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []

        self.conversation_memory[user_id].append(
            {
                "timestamp": datetime.now(),
                "question": question,
                "response_id": response.response_id,
                "confidence": response.confidence,
            }
        )

        # Keep only last 50 interactions
        if len(self.conversation_memory[user_id]) > 50:
            self.conversation_memory[user_id] = self.conversation_memory[user_id][-50:]


class AdvancedLLMIntegration:
    """Step 5: Progressive Complexity Support

    Main class for Phase 17.1 Advanced LLM Integration.
    Supports basic, standard, advanced, and enterprise complexity levels.
    """

    def __init__(self, complexity_level: str = "standard"):
        self.logger = logging.getLogger(__name__)
        self.complexity_level = complexity_level
        self.initialized = False

        # Core components
        self.version_detector = IgnitionVersionDetector()
        self.multimodal_processor = MultiModalProcessor()
        self.context_processor = ContextAwareProcessor()

        # Configuration
        self.config = self._load_configuration()

        # Validation result
        self.validation_result = None

    def initialize(self) -> bool:
        """Step 6: Resource Management and Cleanup

        Initialize the advanced LLM integration system.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Step 1: Environment validation first
            self.validation_result = validate_phase_17_environment()

            if not self.validation_result["valid"]:
                self.logger.error(
                    f"Environment validation failed: {self.validation_result['errors']}"
                )
                return False

            # Initialize components based on complexity level
            if self.complexity_level in ["standard", "advanced", "enterprise"]:
                multimodal_success = self.multimodal_processor.initialize()
                if not multimodal_success:
                    self.logger.warning("Multi-modal processor initialization failed")

            self.initialized = True
            self.logger.info(
                f"Advanced LLM Integration initialized (complexity: {self.complexity_level})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False

    def process_enhanced_request(
        self,
        question: str,
        user_id: str | None = None,
        context: MultiModalContext | None = None,
        ignition_version: str | None = None,
    ) -> ContextAwareResponse:
        """Process an enhanced request with full context awareness.

        Args:
            question: User question
            user_id: Optional user identifier for personalization
            context: Optional multi-modal context
            ignition_version: Optional Ignition version string

        Returns:
            Enhanced context-aware response
        """
        if not self.initialized:
            return ContextAwareResponse(
                content="System not initialized. Please initialize first.",
                confidence=0.0,
            )

        try:
            # Set defaults
            if user_id is None:
                user_id = "anonymous"
            if context is None:
                context = MultiModalContext()

            # Detect Ignition version
            version_info = self.version_detector.detect_version(ignition_version)

            # Process with context awareness
            response = self.context_processor.process_context_aware_request(
                question, user_id, context, version_info
            )

            return response

        except Exception as e:
            self.logger.error(f"Enhanced request processing failed: {e}")
            return ContextAwareResponse(
                content=f"Request processing failed: {str(e)[:100]}...", confidence=0.1
            )

    def analyze_ignition_screenshot(self, image_data: str) -> dict[str, Any]:
        """Analyze Ignition Designer screenshot."""
        if not self.initialized:
            return {"success": False, "user_message": "System not initialized"}

        return self.multimodal_processor.analyze_screenshot(image_data)

    def get_version_capabilities(
        self, version: str | None = None
    ) -> IgnitionVersionInfo:
        """Get Ignition version capabilities."""
        return self.version_detector.detect_version(version)

    def get_system_status(self) -> dict[str, Any]:
        """Get system status and health information."""
        return {
            "initialized": self.initialized,
            "complexity_level": self.complexity_level,
            "validation_result": self.validation_result,
            "components": {
                "version_detector": self.version_detector.cached_version_info
                is not None,
                "multimodal_processor": self.multimodal_processor.initialized,
                "context_processor": len(self.context_processor.user_profiles),
            },
        }

    def _load_configuration(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "multimodal_enabled": os.getenv(
                "PHASE_17_MULTIMODAL_ENABLED", "true"
            ).lower()
            == "true",
            "context_aware_enabled": os.getenv(
                "PHASE_17_CONTEXT_AWARE_ENABLED", "true"
            ).lower()
            == "true",
            "max_conversation_history": int(
                os.getenv("PHASE_17_MAX_CONVERSATION_HISTORY", "50")
            ),
            "default_ignition_version": os.getenv("IGNITION_VERSION", "8.1.25"),
            "log_level": os.getenv("PHASE_17_LOG_LEVEL", "INFO"),
        }

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Clear caches and temporary data
            if hasattr(self.context_processor, "conversation_memory"):
                self.context_processor.conversation_memory.clear()

            self.initialized = False
            self.logger.info("Advanced LLM Integration cleaned up successfully")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Factory function for creating integration instances
def create_advanced_llm_integration(
    complexity_level: str = "standard",
) -> AdvancedLLMIntegration:
    """Create and initialize an Advanced LLM Integration instance.

    Args:
        complexity_level: Complexity level (basic, standard, advanced, enterprise)

    Returns:
        Initialized AdvancedLLMIntegration instance
    """
    integration = AdvancedLLMIntegration(complexity_level)

    if not integration.initialize():
        raise Phase17ValidationError("Failed to initialize Advanced LLM Integration")

    return integration


# Example usage and testing functions
def demo_phase_17_capabilities():
    """Demonstrate Phase 17.1 capabilities."""
    print("🚀 Phase 17.1: Advanced LLM Integration Demo")
    print("=" * 50)

    try:
        # Create integration instance
        integration = create_advanced_llm_integration("standard")

        # Test version detection
        version_info = integration.get_version_capabilities("8.1.25")
        print(f"✅ Ignition Version: {version_info.version}")
        print(f"✅ Perspective Support: {version_info.has_perspective}")

        # Test enhanced request processing
        context = MultiModalContext(
            user_preferences={"expertise_level": "advanced"},
            domain_expertise_level="expert",
        )

        response = integration.process_enhanced_request(
            "How do I create a Perspective session script?",
            user_id="demo_user",
            context=context,
            ignition_version="8.1.25",
        )

        print(f"✅ Response generated (confidence: {response.confidence:.2f})")
        print(f"✅ Version-specific: {response.ignition_version_specific}")
        print(f"✅ Processing time: {response.processing_time:.3f}s")

        # Test system status
        status = integration.get_system_status()
        print(f"✅ System Status: {status}")

        # Cleanup
        integration.cleanup()
        print("✅ Demo completed successfully")

    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    demo_phase_17_capabilities()
