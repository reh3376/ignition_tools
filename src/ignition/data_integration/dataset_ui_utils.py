"""Dataset UI Utility Functions.

This module contains utility functions and helper methods extracted from
the DatasetCurationUI class to improve maintainability and reduce complexity.
"""

from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .dataset_manager_models import DataQuality


class DatasetUIUtils:
    """Utility functions for dataset UI operations."""

    def __init__(self, manager):
        """Initialize with dataset manager reference."""
        self.manager = manager

    def process_dataset_action(self, dataset_id: str) -> None:
        """Process a dataset and show progress."""
        try:
            with st.spinner("Processing dataset..."):
                processed_data = self.manager.process_dataset(dataset_id)

            st.success(
                f"✅ Dataset processed successfully! Generated {len(processed_data)} rows."
            )

            # Show preview of processed data
            if not processed_data.empty:
                st.markdown("### 👀 Data Preview")
                st.dataframe(processed_data.head(10), use_container_width=True)

            st.rerun()

        except Exception as e:
            st.error(f"Processing failed: {e}")

    def show_quality_report(self, report) -> None:
        """Show detailed quality report."""
        with st.expander("📊 Detailed Quality Report", expanded=True):
            st.json(
                {
                    "report_id": report.report_id,
                    "overall_quality": report.overall_quality.value,
                    "scores": {
                        "completeness": report.completeness_score,
                        "consistency": report.consistency_score,
                        "accuracy": report.accuracy_score,
                        "uniqueness": report.uniqueness_score,
                        "timeliness": report.timeliness_score,
                    },
                    "generated_at": report.generated_at.isoformat(),
                }
            )

    def delete_dataset_confirmation(self) -> None:
        """Show dataset deletion confirmation."""
        if st.session_state.selected_dataset_id:
            dataset = self.manager.get_dataset(st.session_state.selected_dataset_id)
            if dataset:
                st.warning(f"⚠️ Are you sure you want to delete '{dataset.name}'?")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🗑️ Yes, Delete", type="primary"):
                        if self.manager.delete_dataset(dataset.dataset_id):
                            st.success("Dataset deleted successfully!")
                            st.session_state.selected_dataset_id = None
                            st.rerun()
                        else:
                            st.error("Failed to delete dataset!")

                with col2:
                    if st.button("❌ Cancel"):
                        st.info("Deletion cancelled.")

    @staticmethod
    def calculate_average_quality(datasets: list[dict[str, Any]]) -> float:
        """Calculate average quality score across datasets."""
        quality_scores = []
        for ds in datasets:
            if ds["quality"] == "excellent":
                quality_scores.append(95)
            elif ds["quality"] == "good":
                quality_scores.append(85)
            elif ds["quality"] == "fair":
                quality_scores.append(75)
            elif ds["quality"] == "poor":
                quality_scores.append(65)
            elif ds["quality"] == "critical":
                quality_scores.append(50)

        return sum(quality_scores) / len(quality_scores) if quality_scores else 0

    @staticmethod
    def get_quality_color(quality: DataQuality) -> str:
        """Get color for quality level."""
        colors = {
            DataQuality.EXCELLENT: "#28a745",
            DataQuality.GOOD: "#17a2b8",
            DataQuality.FAIR: "#ffc107",
            DataQuality.POOR: "#fd7e14",
            DataQuality.CRITICAL: "#dc3545",
        }
        return colors.get(quality, "#6c757d")

    @staticmethod
    def render_status_chart(datasets: list[dict[str, Any]]) -> None:
        """Render dataset status distribution chart."""
        st.markdown("#### Dataset Status Distribution")

        status_counts = {}
        for ds in datasets:
            status = ds["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Dataset Status",
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_type_chart(datasets: list[dict[str, Any]]) -> None:
        """Render dataset type distribution chart."""
        st.markdown("#### Dataset Type Distribution")

        type_counts = {}
        for ds in datasets:
            ds_type = ds["type"]
            type_counts[ds_type] = type_counts.get(ds_type, 0) + 1

        if type_counts:
            fig = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Dataset Types",
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_quality_radar_chart(report) -> None:
        """Render quality metrics radar chart."""
        st.markdown("### 🎯 Quality Metrics Radar")

        categories = [
            "Completeness",
            "Consistency",
            "Accuracy",
            "Uniqueness",
            "Timeliness",
        ]
        values = [
            report.completeness_score,
            report.consistency_score,
            report.accuracy_score,
            report.uniqueness_score,
            report.timeliness_score,
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=values, theta=categories, fill="toself", name="Quality Scores"
            )
        )

        fig.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 100]}},
            showlegend=True,
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True) 