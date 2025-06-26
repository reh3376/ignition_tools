"""Learning System Integration for Streamlit UI.

This module provides components and utilities to integrate the learning system
into the Streamlit interface, including usage tracking, recommendations display,
and analytics visualization.
"""

from contextlib import contextmanager
from typing import Any, Self

import streamlit as st

# Import learning system components
try:
    from src.ignition.graph.client import IgnitionGraphClient
    from src.ignition.graph.pattern_analyzer import PatternAnalyzer
    from src.ignition.graph.pattern_manager import PatternManager
    from src.ignition.graph.usage_tracker import UsageTracker
except ImportError:
    IgnitionGraphClient = None
    UsageTracker = None
    PatternAnalyzer = None
    PatternManager = None


class LearningSystemUI:
    """Learning system integration for Streamlit UI."""

    def __init__(self: Self) -> None:
        """Initialize the learning system UI components."""
        self.client = None
        self.tracker = None
        self.analyzer = None
        self.manager = None
        self._initialize_components()

    def _initialize_components(self: Self) -> None:
        """Initialize learning system components."""
        if not IgnitionGraphClient:
            return

        try:
            self.client = IgnitionGraphClient()
            if self.client.connect():
                self.tracker = UsageTracker(self.client)
                self.analyzer = PatternAnalyzer(self.client)
                self.manager = PatternManager(self.client)
        except Exception as e:
            st.warning(f"Learning system not available: {e}")

    def is_available(self: Self) -> bool:
        """Check if learning system is available."""
        return all([self.client, self.tracker, self.analyzer, self.manager])

    @contextmanager
    def track_session(self: Self, user_id: str = "streamlit_user", session_type: str = "ui_session") -> None:
        """Context manager for tracking UI sessions."""
        session_id = None

        if self.tracker:
            try:
                session_id = self.tracker.start_session(user_id=user_id, session_type=session_type)
                yield session_id
            finally:
                if session_id:
                    self.tracker.end_session()
        else:
            yield None

    def track_action(
        self,
        action_type: str,
        details: dict[str, Any] | None = None,
        success: bool = True,
    ) -> None:
        """Track user actions in the UI."""
        if not self.tracker:
            return

        try:
            # Start session if none exists
            if not self.tracker.current_session_id:
                self.tracker.start_session(user_id="streamlit_user", session_type="ui_session")

            # Track the action
            self.tracker.track_function_query(
                function_name=f"ui.{action_type}",
                context="Streamlit UI",
                parameters=details,
                success=success,
            )
        except Exception:
            # Silently fail for usage tracking
            pass

    def get_recommendations(self: Self, current_action: str, limit: int = 5) -> list[dict[str, Any]]:
        """Get UI recommendations based on usage patterns."""
        if not self.analyzer:
            return []

        try:
            function_name = f"ui.{current_action}"
            recommendations = self.analyzer.get_recommendations_for_function(function_name)

            # Convert to UI actions
            ui_recommendations = []
            for rec in recommendations[:limit]:
                if rec["recommended_function"].startswith("ui."):
                    action = rec["recommended_function"].replace("ui.", "")
                    ui_recommendations.append(
                        {
                            "action": action,
                            "confidence": rec["confidence"],
                            "reasoning": rec["reasoning"],
                        }
                    )

            return ui_recommendations
        except Exception:
            return []

    def display_learning_status(self: Self) -> None:
        """Display learning system status in the UI."""
        if self.is_available():
            st.success("🧠 Learning System: Connected")
            return True
        else:
            st.warning("⚠️ Learning System: Not Available")
            return False

    def display_recommendations(self: Self, current_action: str, container=None) -> None:
        """Display recommendations for the current action."""
        recommendations = self.get_recommendations(current_action)

        if not recommendations:
            return

        if container:
            with container:
                self._render_recommendations(recommendations, current_action)
        else:
            self._render_recommendations(recommendations, current_action)

    def _render_recommendations(self: Self, recommendations: list[dict[str, Any]], current_action: str) -> None:
        """Render recommendations in the UI."""
        st.markdown("### 🎯 Smart Recommendations")
        st.markdown(f"*Based on your {current_action} usage patterns*")

        for i, rec in enumerate(recommendations, 1):
            action = rec["action"]
            confidence = rec["confidence"]
            reasoning = rec["reasoning"]

            with st.expander(f"💡 {action.replace('_', ' ').title()} (Confidence: {confidence:.1%})"):
                st.markdown(f"**Why this suggestion?** {reasoning}")

                # Add action buttons for common recommendations
                if action == "script_generation":
                    if st.button(f"🚀 Generate Script #{i}", key=f"rec_script_{i}"):
                        st.session_state.page = "generator"
                        st.rerun()
                elif action == "template_browsing":
                    if st.button(f"📋 Browse Templates #{i}", key=f"rec_template_{i}"):
                        st.session_state.page = "templates"
                        st.rerun()
                elif action == "validation" and st.button(f"✅ Validate Script #{i}", key=f"rec_validate_{i}"):
                    st.session_state.page = "validation"
                    st.rerun()

    def display_usage_insights(self: Self) -> None:
        """Display usage insights and analytics."""
        if not self.manager:
            st.info("Learning system not available for insights")
            return

        st.markdown("### 📊 Usage Insights")

        try:
            # Get pattern statistics
            stats = self.manager.get_pattern_statistics()

            col1, col2, col3 = st.columns(3)

            with col1:
                total_patterns = sum(stats.get("pattern_counts", {}).values())
                st.metric("Total Patterns", total_patterns)

            with col2:
                conf_dist = stats.get("confidence_distribution", {})
                high_conf = conf_dist.get("high_confidence", 0)
                st.metric("High Confidence", high_conf)

            with col3:
                template_patterns = stats.get("pattern_counts", {}).get("template_usage", 0)
                st.metric("Template Patterns", template_patterns)

            # Pattern distribution chart
            if stats.get("pattern_counts"):
                self._display_pattern_chart(stats["pattern_counts"])

            # Top patterns
            self._display_top_patterns()

        except Exception as e:
            st.error(f"Error loading insights: {e}")

    def _display_pattern_chart(self: Self, pattern_counts: dict[str, int]) -> None:
        """Display pattern distribution chart."""
        import pandas as pd
        import plotly.express as px

        # Prepare data for chart
        chart_data = []
        for pattern_type, count in pattern_counts.items():
            chart_data.append({"Pattern Type": pattern_type.replace("_", " ").title(), "Count": count})

        if chart_data:
            df = pd.DataFrame(chart_data)

            # Create pie chart
            fig = px.pie(
                df,
                values="Count",
                names="Pattern Type",
                title="Pattern Distribution by Type",
            )

            st.plotly_chart(fig, use_container_width=True)

    def _display_top_patterns(self: Self) -> None:
        """Display top patterns summary."""
        try:
            top_patterns = self.manager.get_top_patterns_summary(limit=5)

            st.markdown("#### 🌟 Top Patterns")

            # Function co-occurrence patterns
            co_patterns = top_patterns.get("top_patterns", {}).get("function_co_occurrence", [])
            if co_patterns:
                st.markdown("**Most Common Function Combinations:**")
                for pattern in co_patterns[:3]:
                    func1 = pattern.get("function_1", "")
                    func2 = pattern.get("function_2", "")
                    confidence = pattern.get("confidence_1_to_2", 0)
                    st.markdown(f"• {func1} → {func2} (Confidence: {confidence:.1%})")

            # Template usage patterns
            template_patterns = top_patterns.get("top_patterns", {}).get("template_usage", [])
            if template_patterns:
                st.markdown("**Most Popular Templates:**")
                for pattern in template_patterns[:3]:
                    template = pattern.get("template_name", "")
                    usage = pattern.get("usage_count", 0)
                    success = pattern.get("success_rate", 0)
                    st.markdown(f"• {template} ({usage} uses, {success:.1%} success)")

        except Exception as e:
            st.warning(f"Could not load top patterns: {e}")

    def display_learning_dashboard(self: Self) -> None:
        """Display comprehensive learning system dashboard."""
        if not self.is_available():
            st.warning("Learning system not available")
            return

        st.markdown("## 🧠 Learning System Dashboard")

        # System status
        col1, col2, col3, col4 = st.columns(4)

        try:
            stats = self.manager.get_pattern_statistics()

            with col1:
                total_patterns = sum(stats.get("pattern_counts", {}).values())
                st.metric("Total Patterns", total_patterns, delta=None)

            with col2:
                conf_dist = stats.get("confidence_distribution", {})
                high_conf = conf_dist.get("high_confidence", 0)
                med_conf = conf_dist.get("medium_confidence", 0)
                low_conf = conf_dist.get("low_confidence", 0)
                confidence_rate = (
                    (high_conf / (high_conf + med_conf + low_conf)) if (high_conf + med_conf + low_conf) > 0 else 0
                )
                st.metric("Confidence Rate", f"{confidence_rate:.1%}")

            with col3:
                pattern_counts = stats.get("pattern_counts", {})
                active_types = len([count for count in pattern_counts.values() if count > 0])
                st.metric("Active Pattern Types", active_types)

            with col4:
                # Age distribution - patterns created in last week
                age_dist = stats.get("age_distribution", {})
                recent_patterns = age_dist.get("less_than_week", 0)
                st.metric("Recent Patterns", recent_patterns)

        except Exception as e:
            st.error(f"Error loading dashboard data: {e}")
            return

        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔗 Co-occurrence", "📋 Templates", "⚙️ Parameters"])

        with tab1:
            self.display_usage_insights()

        with tab2:
            self._display_cooccurrence_patterns()

        with tab3:
            self._display_template_patterns()

        with tab4:
            self._display_parameter_patterns()

    def _display_cooccurrence_patterns(self: Self) -> None:
        """Display function co-occurrence patterns."""
        st.markdown("### 🔗 Function Co-occurrence Patterns")

        try:
            patterns = self.manager.get_patterns_by_type("function_co_occurrence", limit=10)

            if patterns:
                # Create a table of co-occurrence patterns
                pattern_data = []
                for pattern in patterns:
                    pattern_data.append(
                        {
                            "Function 1": pattern.get("function_1", ""),
                            "Function 2": pattern.get("function_2", ""),
                            "Confidence (1→2)": f"{pattern.get('confidence_1_to_2', 0):.1%}",
                            "Confidence (2→1)": f"{pattern.get('confidence_2_to_1', 0):.1%}",
                            "Support": f"{pattern.get('support', 0):.1%}",
                            "Created": (pattern.get("created_at", "")[:10] if pattern.get("created_at") else ""),
                        }
                    )

                st.dataframe(pattern_data, use_container_width=True)
            else:
                st.info("No co-occurrence patterns found")

        except Exception as e:
            st.error(f"Error loading co-occurrence patterns: {e}")

    def _display_template_patterns(self: Self) -> None:
        """Display template usage patterns."""
        st.markdown("### 📋 Template Usage Patterns")

        try:
            patterns = self.manager.get_patterns_by_type("template_usage", limit=10)

            if patterns:
                # Create a table of template patterns
                pattern_data = []
                for pattern in patterns:
                    pattern_data.append(
                        {
                            "Template": pattern.get("template_name", ""),
                            "Usage Count": pattern.get("usage_count", 0),
                            "Success Rate": f"{pattern.get('success_rate', 0):.1%}",
                            "Avg Generation Time": f"{pattern.get('avg_generation_time', 0):.2f}s",
                            "Last Used": (pattern.get("last_used", "")[:10] if pattern.get("last_used") else ""),
                        }
                    )

                st.dataframe(pattern_data, use_container_width=True)

                # Show template recommendations
                if len(patterns) > 0:
                    st.markdown("#### 💡 Template Recommendations")

                    # Sort by success rate and usage count
                    sorted_patterns = sorted(
                        patterns,
                        key=lambda x: (
                            x.get("success_rate", 0),
                            x.get("usage_count", 0),
                        ),
                        reverse=True,
                    )

                    for i, pattern in enumerate(sorted_patterns[:3], 1):
                        template = pattern.get("template_name", "")
                        success_rate = pattern.get("success_rate", 0)
                        usage_count = pattern.get("usage_count", 0)

                        st.markdown(f"**{i}. {template}**")
                        st.markdown(f"   • Success Rate: {success_rate:.1%}")
                        st.markdown(f"   • Usage Count: {usage_count}")

                        if st.button(f"Use {template}", key=f"use_template_{i}"):
                            st.session_state.selected_template = template
                            st.session_state.page = "generator"
                            st.rerun()
            else:
                st.info("No template patterns found")

        except Exception as e:
            st.error(f"Error loading template patterns: {e}")

    def _display_parameter_patterns(self: Self) -> None:
        """Display parameter combination patterns."""
        st.markdown("### ⚙️ Parameter Combination Patterns")

        try:
            patterns = self.manager.get_patterns_by_type("parameter_combination", limit=15)

            if patterns:
                # Group patterns by entity
                entity_patterns = {}
                for pattern in patterns:
                    entity = pattern.get("entity_name", "Unknown")
                    if entity not in entity_patterns:
                        entity_patterns[entity] = []
                    entity_patterns[entity].append(pattern)

                # Display patterns grouped by entity
                for entity, entity_pattern_list in entity_patterns.items():
                    with st.expander(f"📦 {entity}"):
                        param_data = []
                        for pattern in entity_pattern_list:
                            param_data.append(
                                {
                                    "Parameter": pattern.get("parameter_key", ""),
                                    "Frequency": f"{pattern.get('frequency', 0):.1%}",
                                    "Success Rate": f"{pattern.get('success_rate', 0):.1%}",
                                    "Avg Value Length": pattern.get("avg_value_length", 0),
                                    "Common Values": ", ".join(pattern.get("common_values", [])[:3]),
                                }
                            )

                        st.dataframe(param_data, use_container_width=True)
            else:
                st.info("No parameter patterns found")

        except Exception as e:
            st.error(f"Error loading parameter patterns: {e}")


# Global learning system instance for Streamlit
@st.cache_resource
def get_learning_system() -> LearningSystemUI:
    """Get or create the learning system instance."""
    return LearningSystemUI()


def track_page_visit(page_name: str) -> None:
    """Track page visits in the UI."""
    learning_system = get_learning_system()
    learning_system.track_action("page_visit", {"page": page_name})


def track_script_generation(template: str, config: dict[str, Any], success: bool) -> None:
    """Track script generation actions."""
    learning_system = get_learning_system()
    learning_system.track_action(
        "script_generation",
        {
            "template": template,
            "config_keys": list(config.keys()) if config else [],
            "config_size": len(str(config)) if config else 0,
        },
        success=success,
    )


def track_template_usage(template: str, action: str) -> None:
    """Track template-related actions."""
    learning_system = get_learning_system()
    learning_system.track_action("template_usage", {"template": template, "action": action})


def show_smart_recommendations(current_action: str, container=None) -> None:
    """Show smart recommendations based on current action."""
    learning_system = get_learning_system()
    if learning_system.is_available():
        learning_system.display_recommendations(current_action, container)


def show_learning_status() -> None:
    """Show learning system status."""
    learning_system = get_learning_system()
    return learning_system.display_learning_status()


def show_usage_insights() -> None:
    """Show usage insights dashboard."""
    learning_system = get_learning_system()
    learning_system.display_usage_insights()


def show_learning_dashboard() -> None:
    """Show comprehensive learning dashboard."""
    learning_system = get_learning_system()
    learning_system.display_learning_dashboard()


# Decorators for automatic tracking
def track_ui_action(action_name: str) -> None:
    """Decorator to automatically track UI actions."""

    def decorator(func: Any) -> None:
        def wrapper(*args, **kwargs) -> None:
            learning_system = get_learning_system()

            try:
                result = func(*args, **kwargs)
                learning_system.track_action(action_name, kwargs, success=True)
                return result
            except Exception as e:
                learning_system.track_action(action_name, kwargs, success=False)
                raise e

        return wrapper

    return decorator
