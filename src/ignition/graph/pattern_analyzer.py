"""Pattern Analysis Engine for Learning System.

This module analyzes usage patterns from tracked events to identify:
- Function co-occurrence patterns
- Template usage patterns
- Parameter combination patterns
- Sequential usage patterns
- Context-specific patterns

The analyzer creates PatternAnalysis nodes with confidence scores and relationships.
"""

import json
import logging
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from typing import Any

from .client import IgnitionGraphClient

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes usage patterns to generate insights and recommendations."""

    def __init__(self, client: IgnitionGraphClient):
        """Initialize pattern analyzer with graph client.

        Args:
            client: IgnitionGraphClient instance for database operations
        """
        self.client = client
        self.min_support = 0.1  # Minimum frequency threshold (10%)
        self.min_confidence = 0.5  # Minimum confidence threshold (50%)

    def analyze_all_patterns(self, days_back: int = 30) -> dict[str, Any]:
        """Analyze all pattern types for recent usage data.

        Args:
            days_back: Number of days to look back for analysis

        Returns:
            Dictionary containing analysis results for all pattern types
        """
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "days_analyzed": days_back,
            "patterns": {},
        }

        # Analyze function co-occurrence patterns
        co_occurrence = self.analyze_function_co_occurrence(days_back)
        results["patterns"]["function_co_occurrence"] = co_occurrence

        # Analyze template usage patterns
        template_patterns = self.analyze_template_patterns(days_back)
        results["patterns"]["template_usage"] = template_patterns

        # Analyze parameter combination patterns
        parameter_patterns = self.analyze_parameter_patterns(days_back)
        results["patterns"]["parameter_combinations"] = parameter_patterns

        # Analyze sequential patterns
        sequential_patterns = self.analyze_sequential_patterns(days_back)
        results["patterns"]["sequential_usage"] = sequential_patterns

        # Store patterns in database
        self._store_patterns(results)

        logger.info(f"Pattern analysis completed: {len(results['patterns'])} pattern types analyzed")
        return results

    def analyze_function_co_occurrence(self, days_back: int = 30) -> list[dict[str, Any]]:
        """Analyze which functions are commonly used together in sessions.

        Args:
            days_back: Number of days to analyze

        Returns:
            list of co-occurrence patterns with confidence scores
        """
        # Get sessions with multiple function usages
        query = """
        MATCH (s:UserSession)
        WHERE s.start_time >= datetime($start_date)
        AND s.unique_functions >= 2
        MATCH (e:UsageEvent)-[:OCCURRED_IN_SESSION]->(s)
        WHERE e.event_type = 'function_query' AND e.function_name IS NOT NULL
        RETURN s.id as session_id, collect(DISTINCT e.function_name) as functions
        """

        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        sessions = self.client.execute_query(query, {"start_date": start_date})

        # Count function co-occurrences
        co_occurrences = Counter()
        function_counts = Counter()
        total_sessions = len(sessions)

        for session in sessions:
            functions = session["functions"]

            # Count individual functions
            for func in functions:
                function_counts[func] += 1

            # Count function pairs
            for func1, func2 in combinations(sorted(functions), 2):
                co_occurrences[(func1, func2)] += 1

        # Generate patterns with confidence scores
        patterns = []
        for (func1, func2), count in co_occurrences.items():
            if count < 2:  # Skip patterns with very low frequency
                continue

            support = count / total_sessions
            if support < self.min_support:
                continue

            # Calculate confidence (how often func2 appears when func1 is used)
            confidence_1_to_2 = count / function_counts[func1]
            confidence_2_to_1 = count / function_counts[func2]

            # Calculate lift (how much more likely they are together vs. independently)
            expected_together = (function_counts[func1] / total_sessions) * (function_counts[func2] / total_sessions)
            lift = support / expected_together if expected_together > 0 else 0

            if confidence_1_to_2 >= self.min_confidence or confidence_2_to_1 >= self.min_confidence:
                patterns.append(
                    {
                        "pattern_id": str(uuid.uuid4()),
                        "pattern_type": "function_co_occurrence",
                        "function_1": func1,
                        "function_2": func2,
                        "support": support,
                        "confidence_1_to_2": confidence_1_to_2,
                        "confidence_2_to_1": confidence_2_to_1,
                        "lift": lift,
                        "frequency": count,
                        "total_sessions": total_sessions,
                    }
                )

        # Sort by confidence and support
        patterns.sort(
            key=lambda x: (x["confidence_1_to_2"] + x["confidence_2_to_1"]) / 2,
            reverse=True,
        )

        logger.info(f"Found {len(patterns)} function co-occurrence patterns")
        return patterns

    def analyze_template_patterns(self, days_back: int = 30) -> list[dict[str, Any]]:
        """Analyze template usage patterns and contexts.

        Args:
            days_back: Number of days to analyze

        Returns:
            list of template usage patterns
        """
        query = """
        MATCH (e:UsageEvent)
        WHERE e.timestamp >= datetime($start_date)
        AND e.event_type = 'template_generation'
        AND e.template_name IS NOT NULL
        RETURN e.template_name as template,
               count(*) as usage_count,
               avg(e.execution_time) as avg_execution_time,
               sum(CASE WHEN e.success THEN 1 ELSE 0 END) as success_count,
               collect(e.parameters) as all_parameters
        ORDER BY usage_count DESC
        """

        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        template_data = self.client.execute_query(query, {"start_date": start_date})

        patterns = []
        for record in template_data:
            template = record["template"]
            usage_count = record["usage_count"]
            success_count = record["success_count"]
            success_rate = success_count / usage_count if usage_count > 0 else 0
            avg_time = record["avg_execution_time"] or 0

            # Analyze parameter patterns
            parameter_patterns = self._analyze_template_parameters(record["all_parameters"])

            patterns.append(
                {
                    "pattern_id": str(uuid.uuid4()),
                    "pattern_type": "template_usage",
                    "template_name": template,
                    "usage_count": usage_count,
                    "success_rate": success_rate,
                    "avg_execution_time": avg_time,
                    "common_parameters": parameter_patterns,
                    "popularity_rank": len(patterns) + 1,
                }
            )

        logger.info(f"Found {len(patterns)} template usage patterns")
        return patterns

    def analyze_parameter_patterns(self, days_back: int = 30) -> list[dict[str, Any]]:
        """Analyze common parameter combinations.

        Args:
            days_back: Number of days to analyze

        Returns:
            list of parameter combination patterns
        """
        query = """
        MATCH (e:UsageEvent)
        WHERE e.timestamp >= datetime($start_date)
        AND e.parameters IS NOT NULL
        RETURN e.function_name as function_name,
               e.template_name as template_name,
               e.parameters as parameters,
               e.success as success
        """

        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        usage_data = self.client.execute_query(query, {"start_date": start_date})

        # Group by function/template and analyze parameter patterns
        param_groups = defaultdict(list)

        for record in usage_data:
            key = record["function_name"] or record["template_name"]
            if key and record["parameters"]:
                try:
                    params = json.loads(record["parameters"])
                    param_groups[key].append({"parameters": params, "success": record["success"]})
                except json.JSONDecodeError:
                    continue

        patterns = []
        for entity, param_list in param_groups.items():
            if len(param_list) < 3:  # Need at least 3 examples
                continue

            # Analyze parameter key patterns
            key_counter = Counter()
            value_patterns = defaultdict(Counter)
            success_by_params = defaultdict(list)

            for item in param_list:
                params = item["parameters"]
                success = item["success"]

                for key, value in params.items():
                    key_counter[key] += 1
                    value_patterns[key][str(value)] += 1
                    success_by_params[key].append(success)

            # Generate patterns for common parameter keys
            for key, count in key_counter.items():
                if count < len(param_list) * 0.3:  # Must appear in at least 30% of usages
                    continue

                frequency = count / len(param_list)
                success_rate = sum(success_by_params[key]) / len(success_by_params[key])
                common_values = dict(value_patterns[key].most_common(5))

                patterns.append(
                    {
                        "pattern_id": str(uuid.uuid4()),
                        "pattern_type": "parameter_combination",
                        "entity_name": entity,
                        "parameter_key": key,
                        "frequency": frequency,
                        "success_rate": success_rate,
                        "common_values": common_values,
                        "usage_count": count,
                    }
                )

        patterns.sort(key=lambda x: x["frequency"] * x["success_rate"], reverse=True)

        logger.info(f"Found {len(patterns)} parameter combination patterns")
        return patterns

    def analyze_sequential_patterns(self, days_back: int = 30) -> list[dict[str, Any]]:
        """Analyze sequential patterns in function/template usage.

        Args:
            days_back: Number of days to analyze

        Returns:
            list of sequential usage patterns
        """
        query = """
        MATCH (s:UserSession)
        WHERE s.start_time >= datetime($start_date)
        AND s.event_count >= 3
        WITH s
        ORDER BY s.start_time
        MATCH (e:UsageEvent)-[:OCCURRED_IN_SESSION]->(s)
        WHERE e.function_name IS NOT NULL OR e.template_name IS NOT NULL
        RETURN s.id as session_id,
               collect(e.function_name) as functions,
               collect(e.template_name) as templates,
               collect(e.timestamp) as timestamps
        """

        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        sessions = self.client.execute_query(query, {"start_date": start_date})

        # Extract sequences
        sequences = []
        for session in sessions:
            # Combine functions and templates into ordered sequence
            events = []
            timestamps = session["timestamps"]
            functions = session["functions"]
            templates = session["templates"]

            # Ensure all arrays are the same length
            min_length = min(len(timestamps), len(functions), len(templates))

            for i in range(min_length):
                timestamp = timestamps[i]
                item = functions[i] or templates[i]
                if item:
                    events.append((timestamp, item))

            # Sort by timestamp and extract sequence
            events.sort(key=lambda x: x[0])
            sequence = [item for _, item in events]

            if len(sequence) >= 2:
                sequences.append(sequence)

        # Find common subsequences
        sequence_patterns = Counter()
        for sequence in sequences:
            # Generate all subsequences of length 2 and 3
            for length in [2, 3]:
                for i in range(len(sequence) - length + 1):
                    subseq = tuple(sequence[i : i + length])
                    sequence_patterns[subseq] += 1

        # Convert to patterns with confidence
        patterns = []
        total_sequences = len(sequences)

        for sequence, count in sequence_patterns.items():
            if count < 2:  # Skip very rare patterns
                continue

            support = count / total_sequences
            if support < self.min_support:
                continue

            patterns.append(
                {
                    "pattern_id": str(uuid.uuid4()),
                    "pattern_type": "sequential_usage",
                    "sequence": list(sequence),
                    "sequence_length": len(sequence),
                    "support": support,
                    "frequency": count,
                    "total_sequences": total_sequences,
                }
            )

        patterns.sort(key=lambda x: x["support"], reverse=True)

        logger.info(f"Found {len(patterns)} sequential usage patterns")
        return patterns

    def _analyze_template_parameters(self, parameter_list: list[str]) -> dict[str, Any]:
        """Analyze parameter patterns for a specific template.

        Args:
            parameter_list: list of JSON parameter strings

        Returns:
            Dictionary of parameter analysis results
        """
        if not parameter_list:
            return {}

        all_keys = Counter()
        key_values = defaultdict(Counter)

        for param_str in parameter_list:
            if not param_str:
                continue
            try:
                params = json.loads(param_str)
                for key, value in params.items():
                    all_keys[key] += 1
                    key_values[key][str(value)] += 1
            except (json.JSONDecodeError, TypeError):
                continue

        # Get most common parameters and their values
        common_params = {}
        for key, count in all_keys.most_common(10):
            frequency = count / len(parameter_list)
            if frequency >= 0.2:  # Must appear in at least 20% of usages
                common_params[key] = {
                    "frequency": frequency,
                    "common_values": dict(key_values[key].most_common(5)),
                }

        return common_params

    def _store_patterns(self, analysis_results: dict[str, Any]):
        """Store pattern analysis results in the database.

        Args:
            analysis_results: Results from pattern analysis
        """
        for _pattern_type, patterns in analysis_results["patterns"].items():
            for pattern in patterns:
                try:
                    # Create PatternAnalysis node
                    pattern_query = """
                    MERGE (p:PatternAnalysis {id: $pattern_id})
                    SET p.pattern_type = $pattern_type,
                        p.confidence = $confidence,
                        p.support = $support,
                        p.pattern_data = $pattern_data,
                        p.created_date = datetime($created_date),
                        p.last_updated = datetime($created_date),
                        p.usage_count = $usage_count,
                        p.relevance_score = $relevance_score
                    """

                    # Calculate overall confidence and support
                    confidence = self._calculate_pattern_confidence(pattern)
                    support = pattern.get("support", pattern.get("frequency", 0))
                    relevance_score = confidence * support

                    self.client.execute_write_query(
                        pattern_query,
                        {
                            "pattern_id": pattern["pattern_id"],
                            "pattern_type": pattern["pattern_type"],
                            "confidence": confidence,
                            "support": support,
                            "pattern_data": json.dumps(pattern),
                            "created_date": datetime.now().isoformat(),
                            "usage_count": pattern.get("usage_count", pattern.get("frequency", 1)),
                            "relevance_score": relevance_score,
                        },
                    )

                    # Create relationships based on pattern type
                    self._create_pattern_relationships(pattern)

                except Exception as e:
                    logger.error(f"Failed to store pattern {pattern.get('pattern_id', 'unknown')}: {e}")

    def _calculate_pattern_confidence(self, pattern: dict[str, Any]) -> float:
        """Calculate overall confidence score for a pattern.

        Args:
            pattern: Pattern dictionary

        Returns:
            Confidence score between 0 and 1
        """
        pattern_type = pattern["pattern_type"]

        if pattern_type == "function_co_occurrence":
            return max(pattern["confidence_1_to_2"], pattern["confidence_2_to_1"])
        elif pattern_type == "template_usage":
            return pattern["success_rate"]
        elif pattern_type == "parameter_combination":
            return pattern["frequency"] * pattern["success_rate"]
        elif pattern_type == "sequential_usage":
            return pattern["support"]

        return 0.5  # Default confidence

    def _create_pattern_relationships(self, pattern: dict[str, Any]):
        """Create relationships between patterns and entities.

        Args:
            pattern: Pattern dictionary
        """
        pattern_type = pattern["pattern_type"]
        pattern_id = pattern["pattern_id"]

        try:
            if pattern_type == "function_co_occurrence":
                # Link to both functions
                for func in [pattern["function_1"], pattern["function_2"]]:
                    rel_query = """
                    MATCH (p:PatternAnalysis {id: $pattern_id}), (f:Function {name: $function_name})
                    MERGE (p)-[:INVOLVES]->(f)
                    """
                    self.client.execute_write_query(rel_query, {"pattern_id": pattern_id, "function_name": func})

            elif pattern_type == "template_usage":
                # Link to template
                rel_query = """
                MATCH (p:PatternAnalysis {id: $pattern_id}), (t:Template {name: $template_name})
                MERGE (p)-[:INVOLVES]->(t)
                """
                self.client.execute_write_query(
                    rel_query,
                    {
                        "pattern_id": pattern_id,
                        "template_name": pattern["template_name"],
                    },
                )

        except Exception as e:
            logger.debug(f"Could not create pattern relationship: {e}")

    def get_patterns_by_type(self, pattern_type: str, limit: int = 10) -> list[dict[str, Any]]:
        """Retrieve patterns by type, ordered by relevance.

        Args:
            pattern_type: Type of pattern to retrieve
            limit: Maximum number of patterns to return

        Returns:
            list of pattern dictionaries
        """
        query = """
        MATCH (p:PatternAnalysis {pattern_type: $pattern_type})
        RETURN p
        ORDER BY p.relevance_score DESC, p.confidence DESC
        LIMIT $limit
        """

        result = self.client.execute_query(query, {"pattern_type": pattern_type, "limit": limit})

        patterns = []
        for record in result:
            pattern_data = record["p"]
            try:
                # Parse stored pattern data
                pattern_json = json.loads(pattern_data["pattern_data"])
                patterns.append(pattern_json)
            except (json.JSONDecodeError, KeyError):
                continue

        return patterns

    def get_recommendations_for_function(self, function_name: str, limit: int = 5) -> list[dict[str, Any]]:
        """Get function recommendations based on co-occurrence patterns.

        Args:
            function_name: Function to get recommendations for
            limit: Maximum number of recommendations

        Returns:
            list of recommended functions with confidence scores
        """
        patterns = self.get_patterns_by_type("function_co_occurrence")
        recommendations = []

        for pattern in patterns:
            if pattern["function_1"] == function_name:
                recommendations.append(
                    {
                        "recommended_function": pattern["function_2"],
                        "confidence": pattern["confidence_1_to_2"],
                        "support": pattern["support"],
                        "reasoning": f"Often used together (confidence: {pattern['confidence_1_to_2']:.2%})",
                    }
                )
            elif pattern["function_2"] == function_name:
                recommendations.append(
                    {
                        "recommended_function": pattern["function_1"],
                        "confidence": pattern["confidence_2_to_1"],
                        "support": pattern["support"],
                        "reasoning": f"Often used together (confidence: {pattern['confidence_2_to_1']:.2%})",
                    }
                )

        # Sort by confidence and return top recommendations
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        return recommendations[:limit]
