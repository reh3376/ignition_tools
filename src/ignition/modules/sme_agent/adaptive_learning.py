"""Adaptive Learning Engine for SME Agent - Phase 11.2.

Phase 11.2: SME Agent Core Capabilities - Adaptive Learning System
Following crawl_mcp.py methodology for systematic learning and improvement.

This module provides:
- Conversation learning and knowledge retention
- Feedback loops for accuracy improvement
- Automated knowledge validation and verification
- Domain expertise scoring and confidence metrics
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AdaptiveLearningError(Exception):
    """Custom exception for adaptive learning errors."""

    pass


@dataclass
class ConversationData:
    """Represents conversation data for learning."""

    conversation_id: str
    user_query: str
    sme_response: str
    user_feedback: str | None = None
    accuracy_rating: float | None = None  # 0.0 to 1.0
    helpfulness_rating: float | None = None  # 0.0 to 1.0
    domain: str | None = None
    topic: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: dict[str, Any] = field(default_factory=dict)
    follow_up_questions: list[str] = field(default_factory=list)
    resolution_status: str = "pending"  # pending, resolved, needs_improvement


@dataclass
class KnowledgeGap:
    """Represents an identified knowledge gap."""

    gap_id: str
    domain: str
    topic: str
    description: str
    frequency: int = 1
    severity: str = "medium"  # low, medium, high, critical
    examples: list[str] = field(default_factory=list)
    suggested_improvements: list[str] = field(default_factory=list)
    first_identified: datetime = field(default_factory=datetime.now)
    last_encountered: datetime = field(default_factory=datetime.now)
    status: str = "open"  # open, in_progress, resolved


@dataclass
class ConfidenceMetric:
    """Represents confidence metrics for a domain/topic."""

    domain: str
    topic: str
    confidence_score: float  # 0.0 to 1.0
    sample_size: int
    accuracy_history: list[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    trend: str = "stable"  # improving, declining, stable


class ConfidenceTracker:
    """Tracks confidence scores across domains and topics.

    Following crawl_mcp.py methodology:
    - Step 1: Environment validation first
    - Step 2: Comprehensive input validation
    - Step 3: Error handling with user-friendly messages
    - Step 4: Modular component testing
    - Step 5: Progressive complexity support
    - Step 6: Resource management and cleanup
    """

    def __init__(self, storage_path: Path | None = None):
        """Initialize the confidence tracker.

        Args:
            storage_path: Path to store confidence data
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.storage_path = (
            Path(storage_path) if storage_path else Path("data/confidence_metrics.json")
        )
        self.confidence_metrics: dict[str, ConfidenceMetric] = {}

        # Step 1: Environment validation first
        self._validate_environment()
        self._load_confidence_data()

    def _validate_environment(self) -> None:
        """Step 1: Environment Validation First."""
        # Ensure storage directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if not os.access(self.storage_path.parent, os.W_OK):
            self.logger.warning(
                f"Storage directory not writable: {self.storage_path.parent}"
            )

    def _load_confidence_data(self) -> None:
        """Load existing confidence data from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path) as f:
                    data = json.load(f)

                for key, metric_data in data.items():
                    metric = ConfidenceMetric(
                        domain=metric_data["domain"],
                        topic=metric_data["topic"],
                        confidence_score=metric_data["confidence_score"],
                        sample_size=metric_data["sample_size"],
                        accuracy_history=metric_data.get("accuracy_history", []),
                        last_updated=datetime.fromisoformat(
                            metric_data["last_updated"]
                        ),
                        trend=metric_data.get("trend", "stable"),
                    )
                    self.confidence_metrics[key] = metric

                self.logger.info(
                    f"Loaded {len(self.confidence_metrics)} confidence metrics"
                )

        except Exception as e:
            self.logger.warning(f"Failed to load confidence data: {e}")

    def _save_confidence_data(self) -> None:
        """Save confidence data to storage."""
        try:
            data = {}
            for key, metric in self.confidence_metrics.items():
                data[key] = {
                    "domain": metric.domain,
                    "topic": metric.topic,
                    "confidence_score": metric.confidence_score,
                    "sample_size": metric.sample_size,
                    "accuracy_history": metric.accuracy_history,
                    "last_updated": metric.last_updated.isoformat(),
                    "trend": metric.trend,
                }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save confidence data: {e}")

    def update_confidence(self, domain: str, topic: str, accuracy: float) -> None:
        """Update confidence score for a domain/topic.

        Args:
            domain: Knowledge domain
            topic: Specific topic within domain
            accuracy: Accuracy score (0.0 to 1.0)
        """
        # Step 2: Comprehensive Input Validation
        if not 0.0 <= accuracy <= 1.0:
            raise AdaptiveLearningError(
                f"Accuracy must be between 0.0 and 1.0, got {accuracy}"
            )

        if not domain or not topic:
            raise AdaptiveLearningError("Domain and topic cannot be empty")

        key = f"{domain}:{topic}"

        if key in self.confidence_metrics:
            metric = self.confidence_metrics[key]

            # Update accuracy history
            metric.accuracy_history.append(accuracy)

            # Keep only last 100 entries
            if len(metric.accuracy_history) > 100:
                metric.accuracy_history = metric.accuracy_history[-100:]

            # Calculate new confidence score (weighted average)
            old_weight = metric.sample_size / (metric.sample_size + 1)
            new_weight = 1 / (metric.sample_size + 1)
            metric.confidence_score = (old_weight * metric.confidence_score) + (
                new_weight * accuracy
            )

            metric.sample_size += 1
            metric.last_updated = datetime.now()

            # Update trend
            if len(metric.accuracy_history) >= 5:
                recent_avg = sum(metric.accuracy_history[-5:]) / 5
                older_avg = (
                    sum(metric.accuracy_history[-10:-5]) / 5
                    if len(metric.accuracy_history) >= 10
                    else metric.confidence_score
                )

                if recent_avg > older_avg + 0.05:
                    metric.trend = "improving"
                elif recent_avg < older_avg - 0.05:
                    metric.trend = "declining"
                else:
                    metric.trend = "stable"
        else:
            # Create new metric
            metric = ConfidenceMetric(
                domain=domain,
                topic=topic,
                confidence_score=accuracy,
                sample_size=1,
                accuracy_history=[accuracy],
                last_updated=datetime.now(),
                trend="stable",
            )
            self.confidence_metrics[key] = metric

        self._save_confidence_data()
        self.logger.debug(
            f"Updated confidence for {domain}:{topic} to {metric.confidence_score:.3f}"
        )

    def get_confidence(self, domain: str, topic: str) -> ConfidenceMetric | None:
        """Get confidence metric for a domain/topic."""
        key = f"{domain}:{topic}"
        return self.confidence_metrics.get(key)

    def get_domain_confidence(self, domain: str) -> dict[str, ConfidenceMetric]:
        """Get all confidence metrics for a domain."""
        return {
            key: metric
            for key, metric in self.confidence_metrics.items()
            if metric.domain == domain
        }

    def get_low_confidence_areas(
        self, threshold: float = 0.7
    ) -> list[ConfidenceMetric]:
        """Get areas with confidence below threshold."""
        return [
            metric
            for metric in self.confidence_metrics.values()
            if metric.confidence_score < threshold
        ]

    def get_statistics(self) -> dict[str, Any]:
        """Get confidence tracking statistics."""
        if not self.confidence_metrics:
            return {"total_metrics": 0}

        scores = [
            metric.confidence_score for metric in self.confidence_metrics.values()
        ]

        return {
            "total_metrics": len(self.confidence_metrics),
            "average_confidence": sum(scores) / len(scores),
            "min_confidence": min(scores),
            "max_confidence": max(scores),
            "domains": list(
                {metric.domain for metric in self.confidence_metrics.values()}
            ),
            "low_confidence_count": len(self.get_low_confidence_areas()),
            "improving_trends": len(
                [m for m in self.confidence_metrics.values() if m.trend == "improving"]
            ),
            "declining_trends": len(
                [m for m in self.confidence_metrics.values() if m.trend == "declining"]
            ),
        }


class AdaptiveLearningEngine:
    """Manages continuous learning and knowledge improvement.

    Following crawl_mcp.py methodology for systematic learning operations.
    """

    def __init__(
        self,
        decision_log_manager=None,
        knowledge_validators=None,
        storage_path: str | None = None,
    ):
        """Initialize the adaptive learning engine.

        Args:
            decision_log_manager: Manager for decision logging
            knowledge_validators: list of knowledge validation functions
            storage_path: Path to store learning data
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.decision_log_manager = decision_log_manager
        self.knowledge_validators = knowledge_validators or []
        self.storage_path = (
            Path(storage_path) if storage_path else Path("data/learning_data")
        )

        # Initialize components
        self.confidence_tracker = ConfidenceTracker(
            self.storage_path / "confidence_metrics.json"
        )
        self.conversations: list[ConversationData] = []
        self.knowledge_gaps: dict[str, KnowledgeGap] = {}

        # Learning statistics
        self.learning_stats = {
            "total_conversations": 0,
            "total_feedback_received": 0,
            "average_accuracy": 0.0,
            "knowledge_gaps_identified": 0,
            "knowledge_gaps_resolved": 0,
            "last_learning_update": None,
        }

        # Step 1: Environment validation first
        self._validate_environment()
        self._load_learning_data()

    def _validate_environment(self) -> None:
        """Step 1: Environment Validation First."""
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        if not os.access(self.storage_path, os.W_OK):
            self.logger.warning(
                f"Learning data directory not writable: {self.storage_path}"
            )

    def _load_learning_data(self) -> None:
        """Load existing learning data from storage."""
        try:
            # Load conversations
            conversations_file = self.storage_path / "conversations.json"
            if conversations_file.exists():
                with open(conversations_file) as f:
                    conversations_data = json.load(f)

                for conv_data in conversations_data:
                    conv = ConversationData(
                        conversation_id=conv_data["conversation_id"],
                        user_query=conv_data["user_query"],
                        sme_response=conv_data["sme_response"],
                        user_feedback=conv_data.get("user_feedback"),
                        accuracy_rating=conv_data.get("accuracy_rating"),
                        helpfulness_rating=conv_data.get("helpfulness_rating"),
                        domain=conv_data.get("domain"),
                        topic=conv_data.get("topic"),
                        timestamp=datetime.fromisoformat(conv_data["timestamp"]),
                        context=conv_data.get("context", {}),
                        follow_up_questions=conv_data.get("follow_up_questions", []),
                        resolution_status=conv_data.get("resolution_status", "pending"),
                    )
                    self.conversations.append(conv)

            # Load knowledge gaps
            gaps_file = self.storage_path / "knowledge_gaps.json"
            if gaps_file.exists():
                with open(gaps_file) as f:
                    gaps_data = json.load(f)

                for gap_id, gap_data in gaps_data.items():
                    gap = KnowledgeGap(
                        gap_id=gap_data["gap_id"],
                        domain=gap_data["domain"],
                        topic=gap_data["topic"],
                        description=gap_data["description"],
                        frequency=gap_data.get("frequency", 1),
                        severity=gap_data.get("severity", "medium"),
                        examples=gap_data.get("examples", []),
                        suggested_improvements=gap_data.get(
                            "suggested_improvements", []
                        ),
                        first_identified=datetime.fromisoformat(
                            gap_data["first_identified"]
                        ),
                        last_encountered=datetime.fromisoformat(
                            gap_data["last_encountered"]
                        ),
                        status=gap_data.get("status", "open"),
                    )
                    self.knowledge_gaps[gap_id] = gap

            # Load learning statistics
            stats_file = self.storage_path / "learning_stats.json"
            if stats_file.exists():
                with open(stats_file) as f:
                    self.learning_stats = json.load(f)

            self.logger.info(
                f"Loaded {len(self.conversations)} conversations and {len(self.knowledge_gaps)} knowledge gaps"
            )

        except Exception as e:
            self.logger.warning(f"Failed to load learning data: {e}")

    def _save_learning_data(self) -> None:
        """Save learning data to storage."""
        try:
            # Save conversations
            conversations_data = []
            for conv in self.conversations:
                conversations_data.append(
                    {
                        "conversation_id": conv.conversation_id,
                        "user_query": conv.user_query,
                        "sme_response": conv.sme_response,
                        "user_feedback": conv.user_feedback,
                        "accuracy_rating": conv.accuracy_rating,
                        "helpfulness_rating": conv.helpfulness_rating,
                        "domain": conv.domain,
                        "topic": conv.topic,
                        "timestamp": conv.timestamp.isoformat(),
                        "context": conv.context,
                        "follow_up_questions": conv.follow_up_questions,
                        "resolution_status": conv.resolution_status,
                    }
                )

            with open(self.storage_path / "conversations.json", "w") as f:
                json.dump(conversations_data, f, indent=2)

            # Save knowledge gaps
            gaps_data = {}
            for gap_id, gap in self.knowledge_gaps.items():
                gaps_data[gap_id] = {
                    "gap_id": gap.gap_id,
                    "domain": gap.domain,
                    "topic": gap.topic,
                    "description": gap.description,
                    "frequency": gap.frequency,
                    "severity": gap.severity,
                    "examples": gap.examples,
                    "suggested_improvements": gap.suggested_improvements,
                    "first_identified": gap.first_identified.isoformat(),
                    "last_encountered": gap.last_encountered.isoformat(),
                    "status": gap.status,
                }

            with open(self.storage_path / "knowledge_gaps.json", "w") as f:
                json.dump(gaps_data, f, indent=2)

            # Save learning statistics
            with open(self.storage_path / "learning_stats.json", "w") as f:
                json.dump(self.learning_stats, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")

    def learn_from_conversation(self, conversation_data: ConversationData) -> None:
        """Learn from user conversations and feedback.

        Args:
            conversation_data: Conversation data to learn from
        """
        try:
            # Step 2: Comprehensive Input Validation
            if not conversation_data.conversation_id:
                raise AdaptiveLearningError("Conversation ID cannot be empty")

            if not conversation_data.user_query or not conversation_data.sme_response:
                raise AdaptiveLearningError("User query and SME response are required")

            # Add to conversations
            self.conversations.append(conversation_data)

            # Update statistics
            self.learning_stats["total_conversations"] += 1

            if conversation_data.user_feedback:
                self.learning_stats["total_feedback_received"] += 1

            # Update confidence scores if accuracy rating is provided
            if (
                conversation_data.accuracy_rating is not None
                and conversation_data.domain
                and conversation_data.topic
            ):
                self.confidence_tracker.update_confidence(
                    conversation_data.domain,
                    conversation_data.topic,
                    conversation_data.accuracy_rating,
                )

            # Identify potential knowledge gaps
            if (
                conversation_data.accuracy_rating is not None
                and conversation_data.accuracy_rating < 0.7
            ):
                self._identify_knowledge_gap(conversation_data)

            # Update learning statistics
            self._update_learning_statistics()

            # Save data
            self._save_learning_data()

            self.logger.info(
                f"Learned from conversation {conversation_data.conversation_id}"
            )

        except Exception as e:
            # Step 3: Error handling with user-friendly messages
            self.logger.error(f"Failed to learn from conversation: {e}")
            raise AdaptiveLearningError(f"Learning failed: {e!s}") from e

    def _identify_knowledge_gap(self, conversation_data: ConversationData) -> None:
        """Identify and record knowledge gaps from conversation data."""
        if not conversation_data.domain or not conversation_data.topic:
            return

        gap_id = f"{conversation_data.domain}:{conversation_data.topic}"

        if gap_id in self.knowledge_gaps:
            # Update existing gap
            gap = self.knowledge_gaps[gap_id]
            gap.frequency += 1
            gap.last_encountered = datetime.now()
            gap.examples.append(conversation_data.user_query)

            # Update severity based on frequency
            if gap.frequency >= 10:
                gap.severity = "critical"
            elif gap.frequency >= 5:
                gap.severity = "high"
            elif gap.frequency >= 3:
                gap.severity = "medium"
        else:
            # Create new knowledge gap
            gap = KnowledgeGap(
                gap_id=gap_id,
                domain=conversation_data.domain,
                topic=conversation_data.topic,
                description=f"Knowledge gap in {conversation_data.domain} - {conversation_data.topic}",
                frequency=1,
                severity="low",
                examples=[conversation_data.user_query],
                suggested_improvements=[
                    f"Improve knowledge base for {conversation_data.topic}",
                    "Add more examples and use cases",
                    "Review and update documentation",
                ],
            )
            self.knowledge_gaps[gap_id] = gap
            self.learning_stats["knowledge_gaps_identified"] += 1

    def _update_learning_statistics(self) -> None:
        """Update learning statistics."""
        if self.conversations:
            # Calculate average accuracy
            accuracy_ratings = [
                conv.accuracy_rating
                for conv in self.conversations
                if conv.accuracy_rating is not None
            ]

            if accuracy_ratings:
                self.learning_stats["average_accuracy"] = sum(accuracy_ratings) / len(
                    accuracy_ratings
                )

        self.learning_stats["last_learning_update"] = datetime.now().isoformat()

    def update_confidence_scores(
        self, domain: str, topic: str, accuracy: float
    ) -> None:
        """Update confidence scores based on feedback.

        Args:
            domain: Knowledge domain
            topic: Specific topic
            accuracy: Accuracy score (0.0 to 1.0)
        """
        self.confidence_tracker.update_confidence(domain, topic, accuracy)

    def identify_knowledge_gaps(self) -> list[KnowledgeGap]:
        """Identify areas needing knowledge improvement.

        Returns:
            list of knowledge gaps sorted by severity and frequency
        """
        gaps = list(self.knowledge_gaps.values())

        # Sort by severity and frequency
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        gaps.sort(
            key=lambda x: (severity_order.get(x.severity, 0), x.frequency), reverse=True
        )

        return gaps

    def get_learning_recommendations(self) -> list[str]:
        """Get recommendations for improving the learning system."""
        recommendations = []

        # Analyze knowledge gaps
        gaps = self.identify_knowledge_gaps()
        critical_gaps = [gap for gap in gaps if gap.severity == "critical"]

        if critical_gaps:
            recommendations.append(
                f"Address {len(critical_gaps)} critical knowledge gaps immediately"
            )

        # Analyze confidence trends
        low_confidence_areas = self.confidence_tracker.get_low_confidence_areas()
        if low_confidence_areas:
            recommendations.append(
                f"Improve knowledge in {len(low_confidence_areas)} low-confidence areas"
            )

        # Analyze conversation patterns
        if self.learning_stats["total_conversations"] > 0:
            feedback_rate = (
                self.learning_stats["total_feedback_received"]
                / self.learning_stats["total_conversations"]
            )
            if feedback_rate < 0.3:
                recommendations.append(
                    "Increase user feedback collection to improve learning"
                )

        return recommendations

    def get_learning_statistics(self) -> dict[str, Any]:
        """Get comprehensive learning statistics."""
        stats = self.learning_stats.copy()

        # Add confidence statistics
        confidence_stats = self.confidence_tracker.get_statistics()
        stats["confidence_metrics"] = confidence_stats

        # Add knowledge gap statistics
        gaps = list(self.knowledge_gaps.values())
        stats["knowledge_gaps"] = {
            "total": len(gaps),
            "critical": len([g for g in gaps if g.severity == "critical"]),
            "high": len([g for g in gaps if g.severity == "high"]),
            "medium": len([g for g in gaps if g.severity == "medium"]),
            "low": len([g for g in gaps if g.severity == "low"]),
            "resolved": len([g for g in gaps if g.status == "resolved"]),
        }

        return stats

    def resolve_knowledge_gap(self, gap_id: str, resolution_notes: str = "") -> bool:
        """Mark a knowledge gap as resolved.

        Args:
            gap_id: ID of the knowledge gap to resolve
            resolution_notes: Notes about how the gap was resolved

        Returns:
            True if gap was resolved, False if not found
        """
        if gap_id in self.knowledge_gaps:
            self.knowledge_gaps[gap_id].status = "resolved"
            if resolution_notes:
                self.knowledge_gaps[gap_id].suggested_improvements.append(
                    f"Resolved: {resolution_notes}"
                )

            self.learning_stats["knowledge_gaps_resolved"] += 1
            self._save_learning_data()

            self.logger.info(f"Resolved knowledge gap: {gap_id}")
            return True

        return False

    def get_domain_learning_status(self, domain: str) -> dict[str, Any]:
        """Get learning status for a specific domain.

        Args:
            domain: Domain to analyze

        Returns:
            Dictionary with domain learning status
        """
        # Get domain conversations
        domain_conversations = [
            conv for conv in self.conversations if conv.domain == domain
        ]

        # Get domain confidence metrics
        domain_confidence = self.confidence_tracker.get_domain_confidence(domain)

        # Get domain knowledge gaps
        domain_gaps = [
            gap for gap in self.knowledge_gaps.values() if gap.domain == domain
        ]

        # Calculate domain statistics
        if domain_conversations:
            accuracy_ratings = [
                conv.accuracy_rating
                for conv in domain_conversations
                if conv.accuracy_rating is not None
            ]
            avg_accuracy = (
                sum(accuracy_ratings) / len(accuracy_ratings)
                if accuracy_ratings
                else None
            )
        else:
            avg_accuracy = None

        return {
            "domain": domain,
            "total_conversations": len(domain_conversations),
            "average_accuracy": avg_accuracy,
            "confidence_metrics": len(domain_confidence),
            "knowledge_gaps": {
                "total": len(domain_gaps),
                "critical": len([g for g in domain_gaps if g.severity == "critical"]),
                "open": len([g for g in domain_gaps if g.status == "open"]),
            },
            "topics_covered": list(
                {conv.topic for conv in domain_conversations if conv.topic}
            ),
            "learning_trend": self._calculate_domain_trend(domain_conversations),
        }

    def _calculate_domain_trend(self, conversations: list[ConversationData]) -> str:
        """Calculate learning trend for a domain based on conversations."""
        if len(conversations) < 5:
            return "insufficient_data"

        # Sort by timestamp
        conversations.sort(key=lambda x: x.timestamp)

        # Get recent and older accuracy ratings
        recent_conversations = conversations[-5:]
        older_conversations = (
            conversations[-10:-5] if len(conversations) >= 10 else conversations[:-5]
        )

        recent_accuracy = [
            conv.accuracy_rating
            for conv in recent_conversations
            if conv.accuracy_rating is not None
        ]
        older_accuracy = [
            conv.accuracy_rating
            for conv in older_conversations
            if conv.accuracy_rating is not None
        ]

        if not recent_accuracy or not older_accuracy:
            return "insufficient_feedback"

        recent_avg = sum(recent_accuracy) / len(recent_accuracy)
        older_avg = sum(older_accuracy) / len(older_accuracy)

        if recent_avg > older_avg + 0.1:
            return "improving"
        elif recent_avg < older_avg - 0.1:
            return "declining"
        else:
            return "stable"


# Export all learning components
__all__ = [
    "AdaptiveLearningEngine",
    "AdaptiveLearningError",
    "ConfidenceMetric",
    "ConfidenceTracker",
    "ConversationData",
    "KnowledgeGap",
]
