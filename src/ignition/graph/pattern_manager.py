"""Pattern Management System for Learning Enhancement.

This module provides enhanced pattern storage, retrieval, and management
capabilities for the learning system, including pattern aging, relevance
scoring, cleanup, and maintenance operations.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from .client import IgnitionGraphClient

logger = logging.getLogger(__name__)


class PatternManager:
    """Manages pattern storage, retrieval, aging, and maintenance."""

    def __init__(self, client: IgnitionGraphClient):
        """Initialize pattern manager with graph client.

        Args:
            client: IgnitionGraphClient instance for database operations
        """
        self.client = client
        self.max_pattern_age_days = (
            90  # Patterns older than 90 days get reduced relevance
        )
        self.min_relevance_threshold = 0.1  # Patterns below this get archived

    def get_patterns_by_type(
        self,
        pattern_type: str,
        limit: int = 10,
        min_confidence: float = 0.0,
        min_support: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Retrieve patterns by type with filtering options.

        Args:
            pattern_type: Type of pattern to retrieve
            limit: Maximum number of patterns to return
            min_confidence: Minimum confidence threshold
            min_support: Minimum support threshold

        Returns:
            List of pattern dictionaries
        """
        query = """
        MATCH (p:PatternAnalysis {pattern_type: $pattern_type})
        WHERE p.confidence >= $min_confidence
        AND p.support >= $min_support
        AND p.relevance_score >= $min_relevance_threshold
        RETURN p, p.pattern_data as pattern_json
        ORDER BY p.relevance_score DESC, p.confidence DESC
        LIMIT $limit
        """

        result = self.client.execute_query(
            query,
            {
                "pattern_type": pattern_type,
                "limit": limit,
                "min_confidence": min_confidence,
                "min_support": min_support,
                "min_relevance_threshold": self.min_relevance_threshold,
            },
        )

        patterns = []
        for record in result:
            try:
                pattern_json = json.loads(record["pattern_json"])
                pattern_node = record["p"]

                # Add metadata from the node
                pattern_json["node_metadata"] = {
                    "relevance_score": pattern_node.get("relevance_score"),
                    "created_date": pattern_node.get("created_date"),
                    "last_updated": pattern_node.get("last_updated"),
                    "usage_count": pattern_node.get("usage_count"),
                }
                patterns.append(pattern_json)

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not parse pattern data: {e}")
                continue

        return patterns

    def get_patterns_by_entity(
        self, entity_name: str, entity_type: str = "function"
    ) -> list[dict[str, Any]]:
        """Get all patterns involving a specific entity (function or template).

        Args:
            entity_name: Name of the entity
            entity_type: Type of entity ("function" or "template")

        Returns:
            List of patterns involving the entity
        """
        if entity_type == "function":
            query = """
            MATCH (f:Function {name: $entity_name})<-[:INVOLVES]-(p:PatternAnalysis)
            WHERE p.relevance_score >= $min_relevance_threshold
            RETURN p, p.pattern_data as pattern_json
            ORDER BY p.relevance_score DESC
            """
        elif entity_type == "template":
            query = """
            MATCH (t:Template {name: $entity_name})<-[:INVOLVES]-(p:PatternAnalysis)
            WHERE p.relevance_score >= $min_relevance_threshold
            RETURN p, p.pattern_data as pattern_json
            ORDER BY p.relevance_score DESC
            """
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        result = self.client.execute_query(
            query,
            {
                "entity_name": entity_name,
                "min_relevance_threshold": self.min_relevance_threshold,
            },
        )

        patterns = []
        for record in result:
            try:
                pattern_json = json.loads(record["pattern_json"])
                patterns.append(pattern_json)
            except (json.JSONDecodeError, KeyError):
                continue

        return patterns

    def get_pattern_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics about stored patterns.

        Returns:
            Dictionary containing pattern statistics
        """
        stats = {
            "timestamp": datetime.now().isoformat(),
            "pattern_counts": {},
            "confidence_distribution": {},
            "age_distribution": {},
            "relevance_distribution": {},
        }

        # Get pattern counts by type
        count_query = """
        MATCH (p:PatternAnalysis)
        RETURN p.pattern_type as pattern_type, count(*) as count
        ORDER BY count DESC
        """

        counts = self.client.execute_query(count_query)
        for record in counts:
            stats["pattern_counts"][record["pattern_type"]] = record["count"]

        # Get confidence distribution
        confidence_query = """
        MATCH (p:PatternAnalysis)
        WITH p.confidence as conf
        RETURN
        sum(CASE WHEN conf >= 0.9 THEN 1 ELSE 0 END) as very_high,
        sum(CASE WHEN conf >= 0.7 AND conf < 0.9 THEN 1 ELSE 0 END) as high,
        sum(CASE WHEN conf >= 0.5 AND conf < 0.7 THEN 1 ELSE 0 END) as medium,
        sum(CASE WHEN conf < 0.5 THEN 1 ELSE 0 END) as low
        """

        conf_result = self.client.execute_query(confidence_query)
        if conf_result:
            stats["confidence_distribution"] = conf_result[0]

        # Get age distribution
        age_query = """
        MATCH (p:PatternAnalysis)
        WITH duration.between(p.created_date, datetime()).days as age_days
        RETURN
        sum(CASE WHEN age_days <= 7 THEN 1 ELSE 0 END) as week_1,
        sum(CASE WHEN age_days > 7 AND age_days <= 30 THEN 1 ELSE 0 END) as month_1,
        sum(CASE WHEN age_days > 30 AND age_days <= 90 THEN 1 ELSE 0 END) as month_3,
        sum(CASE WHEN age_days > 90 THEN 1 ELSE 0 END) as older
        """

        age_result = self.client.execute_query(age_query)
        if age_result:
            stats["age_distribution"] = age_result[0]

        # Get relevance distribution
        relevance_query = """
        MATCH (p:PatternAnalysis)
        WITH p.relevance_score as rel
        RETURN
        sum(CASE WHEN rel >= 0.8 THEN 1 ELSE 0 END) as very_high,
        sum(CASE WHEN rel >= 0.6 AND rel < 0.8 THEN 1 ELSE 0 END) as high,
        sum(CASE WHEN rel >= 0.4 AND rel < 0.6 THEN 1 ELSE 0 END) as medium,
        sum(CASE WHEN rel >= 0.2 AND rel < 0.4 THEN 1 ELSE 0 END) as low,
        sum(CASE WHEN rel < 0.2 THEN 1 ELSE 0 END) as very_low
        """

        rel_result = self.client.execute_query(relevance_query)
        if rel_result:
            stats["relevance_distribution"] = rel_result[0]

        return stats

    def update_pattern_relevance(
        self,
        pattern_id: str,
        new_usage_count: int | None = None,
        success_feedback: bool | None = None,
    ) -> bool:
        """Update pattern relevance based on usage and feedback.

        Args:
            pattern_id: ID of the pattern to update
            new_usage_count: New usage count
            success_feedback: Whether the pattern was successfully used

        Returns:
            True if update successful, False otherwise
        """
        try:
            # Get current pattern data
            get_query = """
            MATCH (p:PatternAnalysis {id: $pattern_id})
            RETURN p.usage_count as usage_count,
                   p.confidence as confidence,
                   p.support as support,
                   p.created_date as created_date
            """

            result = self.client.execute_query(get_query, {"pattern_id": pattern_id})
            if not result:
                logger.warning(f"Pattern {pattern_id} not found")
                return False

            pattern_data = result[0]
            current_usage = pattern_data.get("usage_count", 0)
            confidence = pattern_data.get("confidence", 0.5)
            support = pattern_data.get("support", 0.0)
            created_date = pattern_data.get("created_date")

            # Calculate age factor (newer patterns get higher relevance)
            if created_date:
                age_days = (datetime.now() - created_date).days
                age_factor = max(0.1, 1.0 - (age_days / self.max_pattern_age_days))
            else:
                age_factor = 0.5

            # Update usage count
            if new_usage_count is not None:
                current_usage = new_usage_count
            else:
                current_usage += 1

            # Adjust confidence based on feedback
            if success_feedback is not None:
                if success_feedback:
                    confidence = min(1.0, confidence * 1.05)  # Slight boost for success
                else:
                    confidence = max(
                        0.1, confidence * 0.95
                    )  # Slight penalty for failure

            # Calculate usage factor (more used patterns get higher relevance)
            usage_factor = min(1.0, current_usage / 10.0)  # Normalize to max of 1.0

            # Calculate new relevance score
            new_relevance = confidence * support * age_factor * usage_factor

            # Update pattern in database
            update_query = """
            MATCH (p:PatternAnalysis {id: $pattern_id})
            SET p.usage_count = $usage_count,
                p.confidence = $confidence,
                p.relevance_score = $relevance_score,
                p.last_updated = datetime($timestamp)
            """

            self.client.execute_write_query(
                update_query,
                {
                    "pattern_id": pattern_id,
                    "usage_count": current_usage,
                    "confidence": confidence,
                    "relevance_score": new_relevance,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            logger.debug(
                f"Updated pattern {pattern_id} relevance to {new_relevance:.3f}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update pattern relevance: {e}")
            return False

    def cleanup_old_patterns(
        self, max_age_days: int = 180, min_usage_threshold: int = 2
    ) -> int:
        """Clean up old and unused patterns.

        Args:
            max_age_days: Maximum age in days before cleanup
            min_usage_threshold: Minimum usage count to keep pattern

        Returns:
            Number of patterns cleaned up
        """
        cutoff_date = (datetime.now() - timedelta(days=max_age_days)).isoformat()

        # Find patterns to clean up
        cleanup_query = """
        MATCH (p:PatternAnalysis)
        WHERE p.created_date < datetime($cutoff_date)
        AND p.usage_count < $min_usage_threshold
        RETURN p.id as pattern_id
        """

        patterns_to_cleanup = self.client.execute_query(
            cleanup_query,
            {"cutoff_date": cutoff_date, "min_usage_threshold": min_usage_threshold},
        )

        cleanup_count = 0
        for record in patterns_to_cleanup:
            pattern_id = record["pattern_id"]

            # Delete pattern and its relationships
            delete_query = """
            MATCH (p:PatternAnalysis {id: $pattern_id})
            DETACH DELETE p
            """

            try:
                self.client.execute_write_query(
                    delete_query, {"pattern_id": pattern_id}
                )
                cleanup_count += 1
            except Exception as e:
                logger.error(f"Failed to delete pattern {pattern_id}: {e}")

        logger.info(f"Cleaned up {cleanup_count} old patterns")
        return cleanup_count

    def archive_low_relevance_patterns(self, threshold: float = 0.1) -> int:
        """Archive patterns with very low relevance.

        Args:
            threshold: Relevance threshold below which patterns are archived

        Returns:
            Number of patterns archived
        """
        archive_query = """
        MATCH (p:PatternAnalysis)
        WHERE p.relevance_score < $threshold
        SET p.archived = true, p.archived_date = datetime()
        RETURN count(p) as archived_count
        """

        result = self.client.execute_query(archive_query, {"threshold": threshold})
        archived_count = result[0]["archived_count"] if result else 0

        logger.info(f"Archived {archived_count} low relevance patterns")
        return archived_count

    def get_top_patterns_summary(self, limit: int = 10) -> dict[str, Any]:
        """Get a summary of top patterns across all types.

        Args:
            limit: Number of top patterns per type to include

        Returns:
            Dictionary containing top patterns summary
        """
        summary = {"timestamp": datetime.now().isoformat(), "top_patterns": {}}

        # Get top patterns for each type
        pattern_types = [
            "function_co_occurrence",
            "template_usage",
            "parameter_combination",
            "sequential_usage",
        ]

        for pattern_type in pattern_types:
            patterns = self.get_patterns_by_type(pattern_type, limit=limit)
            summary["top_patterns"][pattern_type] = []

            for pattern in patterns:
                # Create simplified summary
                if pattern_type == "function_co_occurrence":
                    summary_item = {
                        "functions": [pattern["function_1"], pattern["function_2"]],
                        "confidence": max(
                            pattern["confidence_1_to_2"], pattern["confidence_2_to_1"]
                        ),
                        "support": pattern["support"],
                    }
                elif pattern_type == "template_usage":
                    summary_item = {
                        "template": pattern["template_name"],
                        "usage_count": pattern["usage_count"],
                        "success_rate": pattern["success_rate"],
                    }
                elif pattern_type == "parameter_combination":
                    summary_item = {
                        "entity": pattern["entity_name"],
                        "parameter": pattern["parameter_key"],
                        "frequency": pattern["frequency"],
                        "success_rate": pattern["success_rate"],
                    }
                elif pattern_type == "sequential_usage":
                    summary_item = {
                        "sequence": pattern["sequence"],
                        "support": pattern["support"],
                    }

                summary["top_patterns"][pattern_type].append(summary_item)

        return summary

    def export_patterns(
        self, pattern_type: str | None = None, file_path: str | None = None
    ) -> dict[str, Any]:
        """Export patterns for backup or analysis.

        Args:
            pattern_type: Specific pattern type to export (all if None)
            file_path: File path to save export (return data if None)

        Returns:
            Export data dictionary
        """
        if pattern_type:
            query = """
            MATCH (p:PatternAnalysis {pattern_type: $pattern_type})
            RETURN p.id as id, p.pattern_type as type, p.pattern_data as data,
                   p.confidence as confidence, p.support as support,
                   p.relevance_score as relevance, p.created_date as created,
                   p.usage_count as usage_count
            ORDER BY p.relevance_score DESC
            """
            params = {"pattern_type": pattern_type}
        else:
            query = """
            MATCH (p:PatternAnalysis)
            RETURN p.id as id, p.pattern_type as type, p.pattern_data as data,
                   p.confidence as confidence, p.support as support,
                   p.relevance_score as relevance, p.created_date as created,
                   p.usage_count as usage_count
            ORDER BY p.pattern_type, p.relevance_score DESC
            """
            params = {}

        result = self.client.execute_query(query, params)

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "pattern_type_filter": pattern_type,
            "total_patterns": len(result),
            "patterns": [],
        }

        for record in result:
            try:
                pattern_data = json.loads(record["data"])
                export_item = {
                    "id": record["id"],
                    "type": record["type"],
                    "confidence": record["confidence"],
                    "support": record["support"],
                    "relevance": record["relevance"],
                    "created": record["created"].isoformat()
                    if record["created"]
                    else None,
                    "usage_count": record["usage_count"],
                    "pattern_data": pattern_data,
                }
                export_data["patterns"].append(export_item)
            except (json.JSONDecodeError, AttributeError):
                continue

        if file_path:
            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
            logger.info(
                f"Exported {len(export_data['patterns'])} patterns to {file_path}"
            )

        return export_data

    def maintain_patterns(self) -> dict[str, Any]:
        """Perform comprehensive pattern maintenance.

        Returns:
            Dictionary containing maintenance results
        """
        logger.info("Starting pattern maintenance...")

        maintenance_results = {
            "timestamp": datetime.now().isoformat(),
            "operations": {},
        }

        # Update relevance scores for all patterns
        logger.info("Updating pattern relevance scores...")
        update_query = """
        MATCH (p:PatternAnalysis)
        WHERE p.created_date IS NOT NULL
        WITH p, duration.between(p.created_date, datetime()).days as age_days
        SET p.relevance_score = p.confidence * p.support *
            CASE
                WHEN age_days <= 30 THEN 1.0
                WHEN age_days <= 90 THEN 0.8
                WHEN age_days <= 180 THEN 0.6
                ELSE 0.4
            END * (CASE WHEN p.usage_count >= 10 THEN 1.0 ELSE p.usage_count / 10.0 END)
        RETURN count(p) as updated_count
        """

        update_result = self.client.execute_query(update_query)
        updated_count = update_result[0]["updated_count"] if update_result else 0
        maintenance_results["operations"]["relevance_updates"] = updated_count

        # Archive low relevance patterns
        archived_count = self.archive_low_relevance_patterns()
        maintenance_results["operations"]["patterns_archived"] = archived_count

        # Clean up very old patterns
        cleaned_count = self.cleanup_old_patterns()
        maintenance_results["operations"]["patterns_cleaned"] = cleaned_count

        # Get final statistics
        stats = self.get_pattern_statistics()
        maintenance_results["final_statistics"] = stats

        logger.info(
            f"Pattern maintenance completed: {updated_count} updated, "
            f"{archived_count} archived, {cleaned_count} cleaned"
        )

        return maintenance_results
