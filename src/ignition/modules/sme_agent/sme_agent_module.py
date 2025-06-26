"""SME Agent Module - Core Implementation.

Phase 11.1: SME Agent Infrastructure & LLM Setup
Following crawl_mcp.py methodology for systematic development.

Enhanced with Human SME Evaluation and Reinforcement Learning capabilities.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Self

from dotenv import load_dotenv

from . import SMEAgentValidationError, validate_sme_agent_environment

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class SMEDecisionLog:
    """Log entry for SME Agent decisions for human evaluation."""

    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    question: str = ""
    context: str | None = None
    agent_response: str = ""
    confidence: float = 0.0
    sources_used: list[str] = field(default_factory=list)
    knowledge_sources: list[str] = field(default_factory=list)
    processing_time: float = 0.0
    model_used: str = ""

    # Human evaluation fields
    human_evaluation: dict[str, Any] | None = None
    evaluation_timestamp: datetime | None = None
    human_sme_id: str | None = None

    # Reinforcement learning fields
    correct_response: str | None = None
    improvement_suggestions: list[str] = field(default_factory=list)
    rating: int | None = None  # 1-5 scale
    feedback_incorporated: bool = False

    def to_dict(self: Self) -> dict[str, Any]:
        """Convert decision log to dictionary for storage."""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "question": self.question,
            "context": self.context,
            "agent_response": self.agent_response,
            "confidence": self.confidence,
            "sources_used": self.sources_used,
            "knowledge_sources": self.knowledge_sources,
            "processing_time": self.processing_time,
            "model_used": self.model_used,
            "human_evaluation": self.human_evaluation,
            "evaluation_timestamp": (self.evaluation_timestamp.isoformat() if self.evaluation_timestamp else None),
            "human_sme_id": self.human_sme_id,
            "correct_response": self.correct_response,
            "improvement_suggestions": self.improvement_suggestions,
            "rating": self.rating,
            "feedback_incorporated": self.feedback_incorporated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SMEDecisionLog":
        """Create decision log from dictionary."""
        log = cls()
        log.decision_id = data.get("decision_id", str(uuid.uuid4()))
        log.timestamp = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now()
        log.question = data.get("question", "")
        log.context = data.get("context")
        log.agent_response = data.get("agent_response", "")
        log.confidence = data.get("confidence", 0.0)
        log.sources_used = data.get("sources_used", [])
        log.knowledge_sources = data.get("knowledge_sources", [])
        log.processing_time = data.get("processing_time", 0.0)
        log.model_used = data.get("model_used", "")
        log.human_evaluation = data.get("human_evaluation")
        log.evaluation_timestamp = (
            datetime.fromisoformat(data["evaluation_timestamp"]) if data.get("evaluation_timestamp") else None
        )
        log.human_sme_id = data.get("human_sme_id")
        log.correct_response = data.get("correct_response")
        log.improvement_suggestions = data.get("improvement_suggestions", [])
        log.rating = data.get("rating")
        log.feedback_incorporated = data.get("feedback_incorporated", False)
        return log


@dataclass
class HumanEvaluationBatch:
    """Batch of decisions for human SME evaluation."""

    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_timestamp: datetime = field(default_factory=datetime.now)
    decision_logs: list[SMEDecisionLog] = field(default_factory=list)
    status: str = "pending"  # pending, in_review, completed
    human_sme_id: str | None = None
    evaluation_summary: str | None = None
    overall_rating: float | None = None

    def to_dict(self: Self) -> dict[str, Any]:
        """Convert evaluation batch to dictionary."""
        return {
            "batch_id": self.batch_id,
            "created_timestamp": self.created_timestamp.isoformat(),
            "decision_logs": [log.to_dict() for log in self.decision_logs],
            "status": self.status,
            "human_sme_id": self.human_sme_id,
            "evaluation_summary": self.evaluation_summary,
            "overall_rating": self.overall_rating,
        }


@dataclass
class SMEAgentConfig:
    """Configuration for SME Agent with validation."""

    # LLM Configuration
    model_name: str = "llama3.1-8b"
    quantization: str = "int8"
    gpu_enabled: bool = False
    max_context: int = 8192
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048

    # Knowledge Base Configuration
    use_knowledge_graph: bool = True
    use_vector_embeddings: bool = True

    # Neo4j Configuration
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""

    # Human Evaluation Configuration
    enable_human_evaluation: bool = True
    evaluation_batch_size: int = 10
    evaluation_frequency_hours: int = 24
    decision_log_retention_days: int = 90

    # System Configuration
    log_level: str = "INFO"
    cache_dir: str = "cache"
    data_dir: str = "data"
    evaluation_dir: str = "evaluation"

    def __post_init__(self: Self) -> None:
        """Validate configuration after initialization."""
        # Convert string booleans
        if isinstance(self.gpu_enabled, str):
            self.gpu_enabled = self.gpu_enabled.lower() == "true"
        if isinstance(self.use_knowledge_graph, str):
            self.use_knowledge_graph = self.use_knowledge_graph.lower() == "true"
        if isinstance(self.use_vector_embeddings, str):
            self.use_vector_embeddings = self.use_vector_embeddings.lower() == "true"
        if isinstance(self.enable_human_evaluation, str):
            self.enable_human_evaluation = self.enable_human_evaluation.lower() == "true"

        # Validate numeric ranges
        if not 0.0 <= self.temperature <= 2.0:
            raise SMEAgentValidationError(f"Temperature {self.temperature} must be between 0.0 and 2.0")
        if not 0.0 <= self.top_p <= 1.0:
            raise SMEAgentValidationError(f"Top-p {self.top_p} must be between 0.0 and 1.0")
        if self.max_context <= 0:
            raise SMEAgentValidationError(f"Max context {self.max_context} must be positive")
        if self.max_tokens <= 0:
            raise SMEAgentValidationError(f"Max tokens {self.max_tokens} must be positive")
        if self.evaluation_batch_size <= 0:
            raise SMEAgentValidationError(f"Evaluation batch size {self.evaluation_batch_size} must be positive")
        if self.evaluation_frequency_hours <= 0:
            raise SMEAgentValidationError(f"Evaluation frequency {self.evaluation_frequency_hours} must be positive")


@dataclass
class SMEAgentResponse:
    """Response from SME Agent with metadata."""

    response: str
    confidence: float
    sources: list[str]
    processing_time: float
    model_used: str
    knowledge_sources: list[str]
    decision_log: SMEDecisionLog | None = None

    def to_dict(self: Self) -> dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "response": self.response,
            "confidence": self.confidence,
            "sources": self.sources,
            "processing_time": self.processing_time,
            "model_used": self.model_used,
            "knowledge_sources": self.knowledge_sources,
        }
        if self.decision_log:
            result["decision_log"] = self.decision_log.to_dict()
        return result


class SMEAgentModule:
    """SME Agent Module - Phase 11: Process SME Agent & AI Enhancement Platform.

    Following crawl_mcp.py methodology:
    - Step 1: Environment validation first
    - Step 2: Comprehensive input validation
    - Step 3: Error handling with user-friendly messages
    - Step 4: Modular component testing
    - Step 5: Progressive complexity support
    - Step 6: Resource management and cleanup

    Enhanced with Human SME Evaluation and Reinforcement Learning:
    - Decision logging for all agent responses
    - Human evaluation batch processing
    - Feedback incorporation and fine-tuning
    - Performance tracking and improvement
    """

    def __init__(self: Self, config: SMEAgentConfig | None = None):
        """Initialize SME Agent Module.

        Args:
            config: Optional SME Agent configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.validation_result = None
        self.neo4j_driver = None
        self.llm_model = None
        self.vector_store = None
        self.initialized = False

        # Human evaluation components
        self.decision_logs: list[SMEDecisionLog] = []
        self.evaluation_batches: list[HumanEvaluationBatch] = []
        self.evaluation_dir = None

        # Step 1: Environment Validation First
        try:
            self.validation_result = validate_sme_agent_environment()
            if not self.validation_result["valid"]:
                raise SMEAgentValidationError(f"Environment validation failed: {self.validation_result['errors']}")
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            raise SMEAgentValidationError(f"Environment validation failed: {e}")

        # Step 2: Comprehensive Input Validation
        if self.config is None:
            self.config = self._create_config_from_environment()

        # Validate configuration
        try:
            # This will trigger __post_init__ validation
            if not isinstance(self.config, SMEAgentConfig):
                raise SMEAgentValidationError("Invalid configuration type")
        except Exception as e:
            raise SMEAgentValidationError(f"Configuration validation failed: {e}")

        self.logger.info("SME Agent Module initialized successfully")

    def _create_config_from_environment(self: Self) -> SMEAgentConfig:
        """Create configuration from environment variables."""
        env_config = self.validation_result["config"]

        return SMEAgentConfig(
            model_name=env_config.get("SME_AGENT_MODEL", "llama3.1-8b"),
            quantization=env_config.get("SME_AGENT_QUANTIZATION", "int8"),
            gpu_enabled=env_config.get("SME_AGENT_GPU_ENABLED", "false").lower() == "true",
            max_context=int(env_config.get("SME_AGENT_MAX_CONTEXT", "8192")),
            temperature=float(env_config.get("SME_AGENT_TEMPERATURE", "0.7")),
            top_p=float(env_config.get("SME_AGENT_TOP_P", "0.9")),
            max_tokens=int(env_config.get("SME_AGENT_MAX_TOKENS", "2048")),
            use_knowledge_graph=env_config.get("USE_KNOWLEDGE_GRAPH", "true").lower() == "true",
            use_vector_embeddings=env_config.get("USE_VECTOR_EMBEDDINGS", "true").lower() == "true",
            neo4j_uri=env_config.get("NEO4J_URI", ""),
            neo4j_user=env_config.get("NEO4J_USER", ""),
            neo4j_password=env_config.get("NEO4J_PASSWORD", ""),
            log_level=env_config.get("SME_AGENT_LOG_LEVEL", "INFO"),
            enable_human_evaluation=env_config.get("SME_AGENT_ENABLE_HUMAN_EVALUATION", "true").lower() == "true",
            evaluation_batch_size=int(env_config.get("SME_AGENT_EVALUATION_BATCH_SIZE", "10")),
            evaluation_frequency_hours=int(env_config.get("SME_AGENT_EVALUATION_FREQUENCY_HOURS", "24")),
            decision_log_retention_days=int(env_config.get("SME_AGENT_DECISION_LOG_RETENTION_DAYS", "90")),
        )

    def validate_environment(self: Self) -> dict[str, Any]:
        """Step 1: Environment Validation First.

        Returns:
            dict containing validation results
        """
        if self.validation_result is None:
            self.validation_result = validate_sme_agent_environment()

        return self.validation_result

    def initialize_components(self: Self, complexity_level: str = "basic") -> dict[str, Any]:
        """Step 5: Progressive Complexity Support.

        Initialize SME Agent components based on complexity level.

        Args:
            complexity_level: "basic", "standard", "advanced", or "enterprise"

        Returns:
            dict containing initialization results
        """
        start_time = time.time()

        initialization_result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "components_initialized": [],
            "complexity_level": complexity_level,
            "initialization_time": 0.0,
        }

        try:
            # Step 4: Modular Component Testing
            if complexity_level in ["basic", "standard", "advanced", "enterprise"]:
                # Initialize basic components
                self._initialize_logging()
                initialization_result["components_initialized"].append("logging")

                self._initialize_directories()
                initialization_result["components_initialized"].append("directories")

            if complexity_level in ["standard", "advanced", "enterprise"]:
                # Initialize knowledge graph connection
                if self.config.use_knowledge_graph:
                    self._initialize_neo4j()
                    initialization_result["components_initialized"].append("neo4j")

            if complexity_level in ["advanced", "enterprise"]:
                # Initialize LLM model (placeholder for now)
                self._initialize_llm_placeholder()
                initialization_result["components_initialized"].append("llm_placeholder")

            if complexity_level == "enterprise":
                # Initialize vector embeddings (placeholder for now)
                self._initialize_vector_store_placeholder()
                initialization_result["components_initialized"].append("vector_store_placeholder")

            self.initialized = True

        except Exception as e:
            initialization_result["success"] = False
            initialization_result["errors"].append(str(e))
            self.logger.error(f"Component initialization failed: {e}")

        initialization_result["initialization_time"] = time.time() - start_time
        return initialization_result

    def _initialize_logging(self: Self) -> None:
        """Initialize logging configuration."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger.info("Logging initialized")

    def _initialize_directories(self: Self) -> None:
        """Initialize required directories."""
        dirs = [self.config.cache_dir, self.config.data_dir, "logs"]
        for dir_name in dirs:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True)
        self.logger.info("Directories initialized")

    def _initialize_neo4j(self: Self) -> None:
        """Initialize Neo4j connection."""
        try:
            if self.validation_result["components_available"]["neo4j"]:
                from neo4j import GraphDatabase

                self.neo4j_driver = GraphDatabase.driver(
                    self.config.neo4j_uri,
                    auth=(self.config.neo4j_user, self.config.neo4j_password),
                )
                self.logger.info("Neo4j connection initialized")
            else:
                self.logger.warning("Neo4j not available, skipping initialization")
        except Exception as e:
            self.logger.error(f"Neo4j initialization failed: {e}")
            raise

    def _initialize_llm_placeholder(self: Self) -> None:
        """Initialize LLM model with real integration."""
        try:
            # Import LLM integration module
            from .llm_integration import (
                LLMConfig,
                LLMModelManager,
                validate_llm_environment,
            )

            # Create LLM configuration from SME Agent config
            llm_config = LLMConfig(
                model_name=self.config.model_name,
                quantization=self.config.quantization,
                gpu_enabled=self.config.gpu_enabled,
                max_context=self.config.max_context,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_tokens,
                cache_dir=self.config.cache_dir,
                log_level=self.config.log_level,
            )

            # Initialize LLM model manager
            self.llm_model = LLMModelManager(llm_config)

            # Validate LLM environment
            llm_validation = validate_llm_environment()
            if llm_validation["valid"]:
                self.logger.info(f"LLM infrastructure initialized: {self.config.model_name}")
                self.logger.info(f"LLM validation: {len(llm_validation['components_available'])} components available")
            else:
                self.logger.warning(f"LLM validation issues: {llm_validation['errors']}")

        except Exception as e:
            # Fallback to placeholder if LLM integration fails
            self.llm_model = {
                "model_name": self.config.model_name,
                "status": "placeholder",
                "quantization": self.config.quantization,
                "gpu_enabled": self.config.gpu_enabled,
                "error": str(e),
            }
            self.logger.warning(f"LLM integration failed, using placeholder: {e}")
            self.logger.info(f"LLM placeholder initialized: {self.config.model_name}")

    def _initialize_vector_store_placeholder(self: Self) -> None:
        """Initialize vector store (placeholder implementation)."""
        # Placeholder for vector store initialization
        self.vector_store = {
            "status": "placeholder",
            "embeddings_enabled": self.config.use_vector_embeddings,
        }
        self.logger.info("Vector store placeholder initialized")

    def ask_question(self, question: str, context: str | None = None) -> SMEAgentResponse:
        """Step 2: Comprehensive Input Validation
        Step 3: Error Handling and User-Friendly Messages.

        Process a question through the SME Agent.

        Args:
            question: User question
            context: Optional context for the question

        Returns:
            SMEAgentResponse with answer and metadata
        """
        start_time = time.time()

        # Input validation
        if not question or not question.strip():
            raise SMEAgentValidationError("Question cannot be empty")

        if len(question) > 10000:  # Reasonable limit
            raise SMEAgentValidationError("Question too long (max 10,000 characters)")

        try:
            # Create decision log entry
            decision_log = SMEDecisionLog(
                question=question.strip(),
                context=context,
                model_used=self.config.model_name,
            )

            # Generate response using LLM integration
            try:
                if hasattr(self.llm_model, "generate_response"):
                    # Use real LLM model manager
                    llm_response = self.llm_model.generate_response(
                        prompt=(
                            f"Context: {context}\n\nQuestion: {question}\n\nProvide a helpful and accurate response:"
                            if context
                            else f"Question: {question}\n\nProvide a helpful and accurate response:"
                        ),
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                    )

                    if llm_response.get("success"):
                        response_text = llm_response["response"]
                        confidence = 0.9  # High confidence for successful LLM response
                        sources = ["llm_model", "knowledge_graph"] if self.config.use_knowledge_graph else ["llm_model"]
                        knowledge_sources = (
                            ["LLM Model", "Neo4j Knowledge Graph"] if self.config.use_knowledge_graph else ["LLM Model"]
                        )
                    else:
                        # LLM failed, use fallback
                        response_text = f"[LLM ERROR] {llm_response.get('error', 'Unknown error')}"
                        confidence = 0.3
                        sources = ["error_fallback"]
                        knowledge_sources = []

                elif isinstance(self.llm_model, dict) and self.llm_model.get("status") == "placeholder":
                    # Placeholder response
                    response_text = f"[PLACEHOLDER] This is a simulated response to: {question[:100]}..."
                    confidence = 0.8
                    sources = (
                        ["knowledge_graph", "vector_embeddings"]
                        if self.config.use_knowledge_graph
                        else ["vector_embeddings"]
                    )
                    knowledge_sources = ["Neo4j Knowledge Graph"] if self.config.use_knowledge_graph else []
                else:
                    response_text = "SME Agent not fully initialized"
                    confidence = 0.0
                    sources = []
                    knowledge_sources = []

            except Exception as e:
                self.logger.error(f"LLM response generation failed: {e}")
                response_text = f"[ERROR] Response generation failed: {str(e)[:100]}..."
                confidence = 0.1
                sources = ["error_fallback"]
                knowledge_sources = []

            processing_time = time.time() - start_time

            # Complete decision log
            decision_log.agent_response = response_text
            decision_log.confidence = confidence
            decision_log.sources_used = sources
            decision_log.knowledge_sources = knowledge_sources
            decision_log.processing_time = processing_time

            # Store decision log if human evaluation is enabled
            if self.config.enable_human_evaluation:
                self.decision_logs.append(decision_log)
                self._check_evaluation_batch_creation()

            # Create response
            response = SMEAgentResponse(
                response=response_text,
                confidence=confidence,
                sources=sources,
                processing_time=processing_time,
                model_used=self.config.model_name,
                knowledge_sources=knowledge_sources,
                decision_log=(decision_log if self.config.enable_human_evaluation else None),
            )

            return response

        except Exception as e:
            self.logger.error(f"Question processing failed: {e}")
            raise SMEAgentValidationError(f"Question processing failed: {e}")

    def _check_evaluation_batch_creation(self: Self) -> Any:
        """Check if it's time to create a new evaluation batch."""
        if len(self.decision_logs) >= self.config.evaluation_batch_size:
            self._create_evaluation_batch()

    def _create_evaluation_batch(self: Self) -> Any:
        """Create a new evaluation batch from pending decision logs."""
        if not self.decision_logs:
            return

        # Take logs for batch (up to batch size)
        logs_for_batch = self.decision_logs[: self.config.evaluation_batch_size]

        # Create evaluation batch
        batch = HumanEvaluationBatch(decision_logs=logs_for_batch.copy(), status="pending")

        self.evaluation_batches.append(batch)

        # Remove logs from pending list
        self.decision_logs = self.decision_logs[self.config.evaluation_batch_size :]

        # Save batch to file
        self._save_evaluation_batch(batch)

        self.logger.info(f"Created evaluation batch {batch.batch_id} with {len(batch.decision_logs)} decisions")

    def _save_evaluation_batch(self: Self, batch: HumanEvaluationBatch) -> Any:
        """Save evaluation batch to file for human review."""
        if not hasattr(self, "evaluation_dir") or self.evaluation_dir is None:
            self.evaluation_dir = Path(self.config.evaluation_dir)
            self.evaluation_dir.mkdir(exist_ok=True)

        batch_file = self.evaluation_dir / f"batch_{batch.batch_id}.json"

        try:
            with open(batch_file, "w", encoding="utf-8") as f:
                json.dump(batch.to_dict(), f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved evaluation batch to {batch_file}")

        except Exception as e:
            self.logger.error(f"Failed to save evaluation batch: {e}")

    def get_pending_evaluation_batches(self: Self) -> dict[str, Any]:
        """Get all pending evaluation batches for human review."""
        pending_batches = [batch.to_dict() for batch in self.evaluation_batches if batch.status == "pending"]

        return {
            "pending_batches": pending_batches,
            "count": len(pending_batches),
            "total_decisions": sum(len(batch["decision_logs"]) for batch in pending_batches),
        }

    def export_batch_for_review(self, batch_id: str, export_format: str = "json") -> dict[str, Any]:
        """Export evaluation batch for human SME review.

        Args:
            batch_id: ID of the batch to export
            export_format: Export format ("json", "csv", "xlsx")

        Returns:
            dict with export information
        """
        # Find the batch
        batch = None
        for b in self.evaluation_batches:
            if b.batch_id == batch_id:
                batch = b
                break

        if not batch:
            raise SMEAgentValidationError(f"Batch {batch_id} not found")

        if not hasattr(self, "evaluation_dir") or self.evaluation_dir is None:
            self.evaluation_dir = Path(self.config.evaluation_dir)
            self.evaluation_dir.mkdir(exist_ok=True)

        export_file = None

        try:
            if export_format.lower() == "json":
                export_file = self.evaluation_dir / f"review_{batch_id}.json"

                # Create human-friendly review format
                review_data = {
                    "batch_info": {
                        "batch_id": batch.batch_id,
                        "created": batch.created_timestamp.isoformat(),
                        "total_decisions": len(batch.decision_logs),
                        "status": batch.status,
                    },
                    "instructions": {
                        "rating_scale": "Rate each decision from 1-5 (1=Poor, 2=Below Average, 3=Average, 4=Good, 5=Excellent)",  # noqa: E501
                        "evaluation_fields": [
                            "rating: Required integer 1-5",
                            "correct_response: Optional better response if needed",
                            "improvement_suggestions: list of specific improvements",
                            "human_evaluation: Any additional notes or context",
                        ],
                    },
                    "decisions": [],
                }

                for i, log in enumerate(batch.decision_logs):
                    decision_review = {
                        "decision_number": i + 1,
                        "decision_id": log.decision_id,
                        "timestamp": log.timestamp.isoformat(),
                        "question": log.question,
                        "context": log.context,
                        "agent_response": log.agent_response,
                        "agent_confidence": log.confidence,
                        "sources_used": log.sources_used,
                        "processing_time": log.processing_time,
                        # Fields for human SME to fill out
                        "human_evaluation": {
                            "rating": None,  # 1-5 scale
                            "correct_response": None,  # Optional better response
                            "improvement_suggestions": [],  # list of improvements
                            "notes": None,  # Additional notes
                        },
                    }
                    review_data["decisions"].append(decision_review)

                with open(export_file, "w", encoding="utf-8") as f:
                    json.dump(review_data, f, indent=2, ensure_ascii=False)

            elif export_format.lower() == "csv":
                import csv

                export_file = self.evaluation_dir / f"review_{batch_id}.csv"

                with open(export_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)

                    # Write header
                    writer.writerow(
                        [
                            "Decision_ID",
                            "Timestamp",
                            "Question",
                            "Context",
                            "Agent_Response",
                            "Confidence",
                            "Sources",
                            "Processing_Time",
                            "Human_Rating",
                            "Correct_Response",
                            "Improvement_Suggestions",
                            "Notes",
                        ]
                    )

                    # Write data rows
                    for log in batch.decision_logs:
                        writer.writerow(
                            [
                                log.decision_id,
                                log.timestamp.isoformat(),
                                log.question,
                                log.context or "",
                                log.agent_response,
                                log.confidence,
                                "; ".join(log.sources_used),
                                log.processing_time,
                                "",  # Human_Rating - to be filled
                                "",  # Correct_Response - to be filled
                                "",  # Improvement_Suggestions - to be filled
                                "",  # Notes - to be filled
                            ]
                        )

            else:
                raise SMEAgentValidationError(f"Unsupported export format: {export_format}")

            # Update batch status
            batch.status = "exported"
            self._save_evaluation_batch(batch)

            return {
                "success": True,
                "batch_id": batch_id,
                "export_file": str(export_file),
                "export_format": export_format,
                "decisions_count": len(batch.decision_logs),
                "message": f"Batch exported to {export_file} for human review",
            }

        except Exception as e:
            self.logger.error(f"Failed to export batch {batch_id}: {e}")
            return {"success": False, "batch_id": batch_id, "error": str(e)}

    def import_human_evaluation(self, batch_id: str, evaluation_file: str, human_sme_id: str) -> dict[str, Any]:
        """Import human SME evaluation results and incorporate feedback.

        Args:
            batch_id: ID of the batch being evaluated
            evaluation_file: Path to the evaluation file with human feedback
            human_sme_id: ID of the human SME who performed the evaluation

        Returns:
            dict with import and processing results
        """
        try:
            # Find the batch
            batch = None
            for b in self.evaluation_batches:
                if b.batch_id == batch_id:
                    batch = b
                    break

            if not batch:
                raise SMEAgentValidationError(f"Batch {batch_id} not found")

            # Load evaluation data
            evaluation_path = Path(evaluation_file)
            if not evaluation_path.exists():
                raise SMEAgentValidationError(f"Evaluation file not found: {evaluation_file}")

            with open(evaluation_path, encoding="utf-8") as f:
                evaluation_data = json.load(f)

            # Process evaluations
            processed_count = 0
            improvement_count = 0
            ratings = []

            for decision_data in evaluation_data.get("decisions", []):
                decision_id = decision_data.get("decision_id")
                human_eval = decision_data.get("human_evaluation", {})

                # Find corresponding decision log
                decision_log = None
                for log in batch.decision_logs:
                    if log.decision_id == decision_id:
                        decision_log = log
                        break

                if decision_log and human_eval:
                    # Update decision log with human evaluation
                    decision_log.human_evaluation = human_eval
                    decision_log.evaluation_timestamp = datetime.now()
                    decision_log.human_sme_id = human_sme_id
                    decision_log.rating = human_eval.get("rating")
                    decision_log.correct_response = human_eval.get("correct_response")
                    decision_log.improvement_suggestions = human_eval.get("improvement_suggestions", [])
                    decision_log.feedback_incorporated = True

                    processed_count += 1

                    if human_eval.get("rating"):
                        ratings.append(human_eval["rating"])

                    if human_eval.get("correct_response") or human_eval.get("improvement_suggestions"):
                        improvement_count += 1

            # Update batch metadata
            batch.status = "completed"
            batch.human_sme_id = human_sme_id
            batch.evaluation_summary = evaluation_data.get("evaluation_summary", "")
            batch.overall_rating = sum(ratings) / len(ratings) if ratings else None

            # Save updated batch
            self._save_evaluation_batch(batch)

            # Generate reinforcement learning insights
            rl_insights = self._generate_reinforcement_learning_insights(batch)

            return {
                "success": True,
                "batch_id": batch_id,
                "processed_decisions": processed_count,
                "decisions_with_improvements": improvement_count,
                "average_rating": batch.overall_rating,
                "reinforcement_learning_insights": rl_insights,
                "message": f"Successfully processed {processed_count} evaluations from {human_sme_id}",
            }

        except Exception as e:
            self.logger.error(f"Failed to import evaluation for batch {batch_id}: {e}")
            return {"success": False, "batch_id": batch_id, "error": str(e)}

    def _generate_reinforcement_learning_insights(self, batch: HumanEvaluationBatch) -> dict[str, Any]:
        """Generate insights for reinforcement learning from human evaluation."""
        insights: Any = {
            "performance_metrics": {},
            "improvement_patterns": [],
            "common_issues": [],
            "recommendations": [],
        }

        evaluated_logs = [log for log in batch.decision_logs if log.feedback_incorporated]

        if not evaluated_logs:
            return insights

        # Performance metrics
        ratings = [log.rating for log in evaluated_logs if log.rating]
        if ratings:
            insights["performance_metrics"] = {
                "average_rating": sum(ratings) / len(ratings),
                "rating_distribution": {
                    "excellent": len([r for r in ratings if r == 5]),
                    "good": len([r for r in ratings if r == 4]),
                    "average": len([r for r in ratings if r == 3]),
                    "below_average": len([r for r in ratings if r == 2]),
                    "poor": len([r for r in ratings if r == 1]),
                },
            }

        # Improvement patterns
        all_suggestions = []
        for log in evaluated_logs:
            if log.improvement_suggestions:
                all_suggestions.extend(log.improvement_suggestions)

        # Count common improvement suggestions
        suggestion_counts = {}
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1

        insights["improvement_patterns"] = [
            {"suggestion": suggestion, "frequency": count}
            for suggestion, count in sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Common issues (low-rated responses)
        low_rated_logs = [log for log in evaluated_logs if log.rating and log.rating <= 2]
        if low_rated_logs:
            insights["common_issues"] = [
                {
                    "question_type": "Low confidence responses",
                    "frequency": len([log for log in low_rated_logs if log.confidence < 0.5]),
                    "description": "Agent responses with low confidence scores",
                },
                {
                    "question_type": "Long processing time",
                    "frequency": len([log for log in low_rated_logs if log.processing_time > 5.0]),
                    "description": "Responses that took longer than 5 seconds",
                },
            ]

        # Recommendations for model improvement
        if insights["performance_metrics"].get("average_rating", 0) < 3.5:
            insights["recommendations"].append("Consider additional training data or fine-tuning")

        if len([log for log in evaluated_logs if log.correct_response]) > len(evaluated_logs) * 0.3:
            insights["recommendations"].append("High correction rate - review training data quality")

        return insights

    def get_reinforcement_learning_summary(self: Self) -> dict[str, Any]:
        """Get comprehensive reinforcement learning summary across all evaluations."""
        all_evaluated_logs = []

        for batch in self.evaluation_batches:
            if batch.status == "completed":
                evaluated_logs = [log for log in batch.decision_logs if log.feedback_incorporated]
                all_evaluated_logs.extend(evaluated_logs)

        if not all_evaluated_logs:
            return {
                "total_evaluations": 0,
                "message": "No completed evaluations available",
            }

        # Aggregate metrics
        ratings = [log.rating for log in all_evaluated_logs if log.rating]
        confidences = [log.confidence for log in all_evaluated_logs]
        processing_times = [log.processing_time for log in all_evaluated_logs]

        summary = {
            "total_evaluations": len(all_evaluated_logs),
            "total_batches": len([b for b in self.evaluation_batches if b.status == "completed"]),
            "performance_trends": {
                "average_human_rating": sum(ratings) / len(ratings) if ratings else 0,
                "average_agent_confidence": (sum(confidences) / len(confidences) if confidences else 0),
                "average_processing_time": (sum(processing_times) / len(processing_times) if processing_times else 0),
                "improvement_rate": len(
                    [log for log in all_evaluated_logs if log.correct_response or log.improvement_suggestions]
                )
                / len(all_evaluated_logs),
            },
            "learning_opportunities": [],
            "model_performance": {
                "high_quality_responses": len([log for log in all_evaluated_logs if log.rating and log.rating >= 4]),
                "needs_improvement": len([log for log in all_evaluated_logs if log.rating and log.rating <= 2]),
                "consistency_score": (1.0 - (max(confidences) - min(confidences)) if confidences else 0),
            },
        }

        # Identify learning opportunities
        all_suggestions = []
        for log in all_evaluated_logs:
            if log.improvement_suggestions:
                all_suggestions.extend(log.improvement_suggestions)

        suggestion_counts = {}
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1

        summary["learning_opportunities"] = [
            {
                "improvement": suggestion,
                "frequency": count,
                "priority": "high" if count > 3 else "medium",
            }
            for suggestion, count in sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        return summary

    def get_status(self: Self) -> dict[str, Any]:
        """Get current status of SME Agent."""
        return {
            "initialized": self.initialized,
            "config": {
                "model_name": self.config.model_name,
                "use_knowledge_graph": self.config.use_knowledge_graph,
                "use_vector_embeddings": self.config.use_vector_embeddings,
            },
            "components": {
                "neo4j_connected": self.neo4j_driver is not None,
                "llm_loaded": self.llm_model is not None,
                "vector_store_ready": self.vector_store is not None,
            },
            "validation": self.validation_result,
        }

    def cleanup(self: Self) -> Any:
        """Step 6: Resource Management and Cleanup.

        Clean up resources and connections.
        """
        try:
            if self.neo4j_driver:
                self.neo4j_driver.close()
                self.neo4j_driver = None
                self.logger.info("Neo4j driver closed")

            # Additional cleanup for LLM model and vector store would go here

            self.initialized = False
            self.logger.info("SME Agent cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

    def __enter__(self: Self) -> Any:
        """Context manager entry."""
        return self

    def __exit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with cleanup."""
        self.cleanup()
