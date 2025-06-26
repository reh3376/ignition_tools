"""Dataset Curation UI - Interactive Streamlit Interface.

This module provides a comprehensive web-based interface for dataset creation,
curation, and preparation for AI/ML models using Streamlit.
"""

import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.ignition.data_integration.dataset_core import (
        DataQuality,
        Dataset,
        DatasetSchema,
        DatasetType,
        DataSource,
        FeatureDefinition,
        ProcessingStatus,
    )
    from src.ignition.data_integration.dataset_manager import DatasetManager
    from src.ignition.data_integration.dataset_ui_sources import (
        DatasetUISourceConfigurators,
    )
    from src.ignition.data_integration.dataset_ui_utils import DatasetUIUtils
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Dataset Curation Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e8b57;
        border-bottom: 2px solid #2e8b57;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .quality-excellent { border-left-color: #28a745; }
    .quality-good { border-left-color: #17a2b8; }
    .quality-fair { border-left-color: #ffc107; }
    .quality-poor { border-left-color: #fd7e14; }
    .quality-critical { border-left-color: #dc3545; }
    .status-ready { color: #28a745; font-weight: bold; }
    .status-validated { color: #17a2b8; font-weight: bold; }
    .status-in-progress { color: #ffc107; font-weight: bold; }
    .status-draft { color: #6c757d; font-weight: bold; }
</style>
""",
    unsafe_allow_html=True,
)


class DatasetCurationUI:
    """Main UI class for dataset curation."""

    def __init__(self) -> None:
        """Initialize the UI."""
        self.manager = DatasetManager()
        self.utils = DatasetUIUtils(self.manager)
        self.source_configs = DatasetUISourceConfigurators()

        # Initialize session state
        if "selected_dataset_id" not in st.session_state:
            st.session_state.selected_dataset_id = None
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Overview"
        if "refresh_data" not in st.session_state:
            st.session_state.refresh_data = False

    def run(self) -> None:
        """Run the main UI application."""
        # Header
        st.markdown(
            '<div class="main-header">🧠 Dataset Curation Studio</div>',
            unsafe_allow_html=True,
        )
        st.markdown("**Build and curate datasets for AI/ML model training**")

        # Sidebar navigation
        self.render_sidebar()

        # Main content
        if st.session_state.current_page == "Overview":
            self.render_overview()
        elif st.session_state.current_page == "Create Dataset":
            self.render_create_dataset()
        elif st.session_state.current_page == "Dataset Details":
            self.render_dataset_details()
        elif st.session_state.current_page == "Data Sources":
            self.render_data_sources()
        elif st.session_state.current_page == "Feature Engineering":
            self.render_feature_engineering()
        elif st.session_state.current_page == "Data Quality":
            self.render_data_quality()
        elif st.session_state.current_page == "Export & Deploy":
            self.render_export_deploy()

    def render_sidebar(self) -> None:
        """Render the sidebar navigation."""
        with st.sidebar:
            st.markdown("### 📊 Navigation")

            # Main navigation
            pages = [
                "Overview",
                "Create Dataset",
                "Dataset Details",
                "Data Sources",
                "Feature Engineering",
                "Data Quality",
                "Export & Deploy",
            ]

            for page in pages:
                if st.button(page, key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()

            st.divider()

            # Dataset selector
            st.markdown("### 📁 Select Dataset")
            datasets = self.manager.list_datasets()

            if datasets:
                dataset_options = {f"{ds['name']} ({ds['status']})": ds["dataset_id"] for ds in datasets}

                selected_name = st.selectbox(
                    "Choose a dataset:",
                    options=list(dataset_options.keys()),
                    key="dataset_selector",
                )

                if selected_name:
                    st.session_state.selected_dataset_id = dataset_options[selected_name]
            else:
                st.info("No datasets available. Create one to get started!")

            st.divider()

            # Quick actions
            st.markdown("### ⚡ Quick Actions")

            if st.button("🔄 Refresh Data", use_container_width=True):
                st.session_state.refresh_data = True
                st.rerun()

            if st.button("📥 Import Dataset", use_container_width=True):
                st.info("Import functionality coming soon!")

            if datasets and st.button("🗑️ Delete Selected", use_container_width=True):
                if st.session_state.selected_dataset_id:
                    self.delete_dataset_confirmation()

    def render_overview(self) -> None:
        """Render the overview page."""
        st.markdown(
            '<div class="section-header">📊 Dataset Overview</div>',
            unsafe_allow_html=True,
        )

        datasets = self.manager.list_datasets()

        if not datasets:
            st.info("👋 Welcome to Dataset Curation Studio! Create your first dataset to get started.")
            if st.button("➕ Create Your First Dataset", type="primary"):
                st.session_state.current_page = "Create Dataset"
                st.rerun()
            return

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Datasets", len(datasets))

        with col2:
            ready_count = sum(1 for ds in datasets if ds["status"] == "ready")
            st.metric("Ready for Training", ready_count)

        with col3:
            total_rows = sum(ds["row_count"] for ds in datasets)
            st.metric("Total Records", f"{total_rows:,}")

        with col4:
            avg_quality = self.calculate_average_quality(datasets)
            st.metric("Avg Quality Score", f"{avg_quality:.1f}%")

        # Dataset table
        st.markdown("### 📋 All Datasets")

        if datasets:
            df = pd.DataFrame(datasets)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%Y-%m-%d %H:%M")

            # Format the display
            display_df = df[["name", "type", "status", "row_count", "quality", "created_at"]].copy()
            display_df.columns = [
                "Name",
                "Type",
                "Status",
                "Rows",
                "Quality",
                "Created",
            ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", help="Current processing status"),
                    "Quality": st.column_config.TextColumn("Quality", help="Data quality assessment"),
                    "Rows": st.column_config.NumberColumn("Rows", format="%d"),
                },
            )

        # Visualizations
        col1, col2 = st.columns(2)

        with col1:
            self.render_status_chart(datasets)

        with col2:
            self.render_type_chart(datasets)

    def render_create_dataset(self) -> None:
        """Render the create dataset page."""
        st.markdown(
            '<div class="section-header">➕ Create New Dataset</div>',
            unsafe_allow_html=True,
        )

        with st.form("create_dataset_form"):
            st.markdown("### Basic Information")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "Dataset Name *",
                    placeholder="e.g., Industrial_Process_Data",
                    help="Choose a descriptive name for your dataset",
                )

                dataset_type = st.selectbox(
                    "Dataset Type *",
                    options=[dt.value for dt in DatasetType],
                    help="Select the type of ML problem this dataset will solve",
                )

            with col2:
                tags = st.text_input(
                    "Tags (comma-separated)",
                    placeholder="e.g., industrial, temperature, pressure",
                    help="Add tags to help organize and find your dataset",
                )

                description = st.text_area(
                    "Description",
                    placeholder="Describe the purpose and contents of this dataset...",
                    help="Provide details about what this dataset contains and its intended use",
                )

            st.markdown("### Initial Configuration")

            col1, col2 = st.columns(2)

            with col1:
                st.checkbox(
                    "Auto-extract data after creation",
                    value=True,
                    help="Automatically extract data from sources after creating the dataset",
                )

            with col2:
                st.checkbox(
                    "Run quality validation",
                    value=True,
                    help="Run data quality checks immediately after extraction",
                )

            submitted = st.form_submit_button("🚀 Create Dataset", type="primary")

            if submitted:
                if not name:
                    st.error("Dataset name is required!")
                    return

                try:
                    # Parse tags
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

                    # Create dataset
                    dataset = self.manager.create_dataset(
                        name=name,
                        dataset_type=DatasetType(dataset_type),
                        description=description,
                        tags=tag_list,
                    )

                    st.success(f"✅ Dataset '{name}' created successfully!")
                    st.session_state.selected_dataset_id = dataset.dataset_id
                    st.session_state.current_page = "Data Sources"

                    # Show next steps
                    st.info("🎯 Next: Add data sources to your dataset")

                    if st.button("➡️ Add Data Sources"):
                        st.rerun()

                except Exception as e:
                    st.error(f"Failed to create dataset: {e}")

    def render_dataset_details(self) -> None:
        """Render the dataset details page."""
        if not st.session_state.selected_dataset_id:
            st.warning("Please select a dataset from the sidebar.")
            return

        dataset = self.manager.get_dataset(st.session_state.selected_dataset_id)
        if not dataset:
            st.error("Dataset not found!")
            return

        st.markdown(
            '<div class="section-header">📋 Dataset Details</div>',
            unsafe_allow_html=True,
        )

        # Basic information
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Basic Information")
            st.write(f"**Name:** {dataset.name}")
            st.write(f"**Type:** {dataset.schema.dataset_type.value}")
            st.write(f"**Status:** {dataset.status.value}")
            st.write(f"**Created:** {dataset.created_at.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Updated:** {dataset.updated_at.strftime('%Y-%m-%d %H:%M')}")

            if dataset.tags:
                st.write(f"**Tags:** {', '.join(dataset.tags)}")

        with col2:
            st.markdown("### 📈 Statistics")
            st.metric("Rows", f"{dataset.row_count:,}")
            st.metric("Columns", dataset.column_count)
            st.metric("File Size", f"{dataset.file_size_mb:.2f} MB")

            if dataset.quality_report:
                quality_color = self.get_quality_color(dataset.quality_report.overall_quality)
                st.markdown(
                    f"**Quality:** <span style='color: {quality_color}'>{dataset.quality_report.overall_quality.value}</span>",  # noqa: E501
                    unsafe_allow_html=True,
                )

        # Description
        if dataset.schema.description:
            st.markdown("### 📝 Description")
            st.write(dataset.schema.description)

        # Data sources summary
        st.markdown("### 🔗 Data Sources")
        if dataset.data_sources:
            for i, source in enumerate(dataset.data_sources):
                with st.expander(f"Source {i + 1}: {source.source_type}"):
                    st.json(source.connection_config)
        else:
            st.info("No data sources configured. Add sources to extract data.")

        # Features summary
        st.markdown("### 🎯 Features")
        if dataset.schema.features:
            features_df = pd.DataFrame(
                [
                    {
                        "Feature": f.name,
                        "Type": f.data_type,
                        "Source": f.source_column,
                        "Target": "✅" if f.is_target else "",
                        "Transform": f.transformation or "None",
                    }
                    for f in dataset.schema.features
                ]
            )
            st.dataframe(features_df, use_container_width=True, hide_index=True)
        else:
            st.info("No features defined. Configure features for data processing.")

        # Actions
        st.markdown("### ⚡ Actions")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Process Dataset"):
                self.process_dataset_action(dataset.dataset_id)

        with col2:
            if st.button("📊 View Quality Report"):
                if dataset.quality_report:
                    self.show_quality_report(dataset.quality_report)
                else:
                    st.info("No quality report available. Process the dataset first.")

        with col3:
            if st.button("📥 Export Dataset"):
                st.session_state.current_page = "Export & Deploy"
                st.rerun()

        with col4:
            if st.button("🗑️ Delete Dataset"):
                self.delete_dataset_confirmation()

    def render_data_sources(self) -> None:
        """Render the data sources configuration page."""
        if not st.session_state.selected_dataset_id:
            st.warning("Please select a dataset from the sidebar.")
            return

        dataset = self.manager.get_dataset(st.session_state.selected_dataset_id)
        if not dataset:
            st.error("Dataset not found!")
            return

        st.markdown('<div class="section-header">🔗 Data Sources</div>', unsafe_allow_html=True)

        # Existing sources
        if dataset.data_sources:
            st.markdown("### 📋 Configured Sources")
            for i, source in enumerate(dataset.data_sources):
                with st.expander(f"Source {i + 1}: {source.source_type} ({'Active' if source.active else 'Inactive'})"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.json(source.connection_config)
                        if source.query_config:
                            st.markdown("**Query Configuration:**")
                            st.json(source.query_config)

                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_source_{i}"):
                            # Remove source logic would go here
                            st.info("Remove functionality coming soon!")

        # Add new source
        st.markdown("### ➕ Add New Data Source")

        with st.form("add_data_source"):
            source_type = st.selectbox(
                "Source Type",
                options=["database", "file", "historian", "opc", "api"],
                help="Select the type of data source",
            )

            if source_type == "database":
                self.render_database_source_config()
            elif source_type == "file":
                self.render_file_source_config()
            elif source_type == "historian":
                self.render_historian_source_config()
            elif source_type == "opc":
                self.render_opc_source_config()
            elif source_type == "api":
                self.render_api_source_config()

            if st.form_submit_button("➕ Add Source", type="primary"):
                st.success("Source configuration saved! (Demo mode)")

    def render_feature_engineering(self) -> None:
        """Render the feature engineering page."""
        if not st.session_state.selected_dataset_id:
            st.warning("Please select a dataset from the sidebar.")
            return

        dataset = self.manager.get_dataset(st.session_state.selected_dataset_id)
        if not dataset:
            st.error("Dataset not found!")
            return

        st.markdown(
            '<div class="section-header">🎯 Feature Engineering</div>',
            unsafe_allow_html=True,
        )

        # Existing features
        if dataset.schema.features:
            st.markdown("### 📋 Configured Features")

            features_data = []
            for feature in dataset.schema.features:
                features_data.append(
                    {
                        "Name": feature.name,
                        "Type": feature.data_type,
                        "Source": feature.source_column,
                        "Target": "✅" if feature.is_target else "",
                        "Transform": feature.transformation or "None",
                        "Missing Strategy": feature.missing_value_strategy,
                    }
                )

            features_df = pd.DataFrame(features_data)
            st.dataframe(features_df, use_container_width=True, hide_index=True)

        # Add new feature
        st.markdown("### ➕ Add New Feature")

        with st.form("add_feature"):
            col1, col2 = st.columns(2)

            with col1:
                feature_name = st.text_input(
                    "Feature Name *",
                    placeholder="e.g., temperature_normalized",
                    help="Name for the new feature",
                )

                data_type = st.selectbox(
                    "Data Type *",
                    options=["numeric", "categorical", "datetime", "text", "boolean"],
                    help="Type of data this feature contains",
                )

                source_column = st.text_input(
                    "Source Column *",
                    placeholder="e.g., temp_sensor_1",
                    help="Original column name in the source data",
                )

            with col2:
                is_target = st.checkbox(
                    "Target Variable",
                    help="Is this the target variable for prediction?",
                )

                transformation = st.selectbox(
                    "Transformation",
                    options=[
                        "none",
                        "standard_scaling",
                        "min_max_scaling",
                        "log_transform",
                        "one_hot_encoding",
                    ],
                    help="Transformation to apply to this feature",
                )

                st.selectbox(
                    "Missing Value Strategy",
                    options=["drop", "fill_mean", "fill_median", "fill_mode", "custom"],
                    help="How to handle missing values",
                )

            description = st.text_area(
                "Description",
                placeholder="Describe this feature and its purpose...",
                help="Optional description of the feature",
            )

            if st.form_submit_button("➕ Add Feature", type="primary"):
                if feature_name and data_type and source_column:
                    try:
                        self.manager.define_feature(
                            dataset.dataset_id,
                            name=feature_name,
                            data_type=data_type,
                            source_column=source_column,
                            is_target=is_target,
                            transformation=(transformation if transformation != "none" else None),
                            description=description,
                        )
                        st.success(f"✅ Feature '{feature_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add feature: {e}")
                else:
                    st.error("Please fill in all required fields!")

    def render_data_quality(self) -> None:
        """Render the data quality page."""
        if not st.session_state.selected_dataset_id:
            st.warning("Please select a dataset from the sidebar.")
            return

        dataset = self.manager.get_dataset(st.session_state.selected_dataset_id)
        if not dataset:
            st.error("Dataset not found!")
            return

        st.markdown(
            '<div class="section-header">📊 Data Quality Assessment</div>',
            unsafe_allow_html=True,
        )

        if not dataset.quality_report:
            st.info("No quality report available. Process the dataset to generate a quality assessment.")
            if st.button("🔄 Process Dataset and Generate Report"):
                self.process_dataset_action(dataset.dataset_id)
            return

        report = dataset.quality_report

        # Overall quality score
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            quality_color = self.get_quality_color(report.overall_quality)
            st.markdown(
                f"### Overall Quality: <span style='color: {quality_color}'>{report.overall_quality.value.title()}</span>",  # noqa: E501
                unsafe_allow_html=True,
            )

        with col2:
            avg_score = (
                report.completeness_score
                + report.consistency_score
                + report.accuracy_score
                + report.uniqueness_score
                + report.timeliness_score
            ) / 5
            st.metric("Average Score", f"{avg_score:.1f}%")

        with col3:
            st.metric("Issues Found", len(report.issues))

        # Quality metrics
        st.markdown("### 📈 Quality Metrics")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Completeness", f"{report.completeness_score:.1f}%")
        with col2:
            st.metric("Consistency", f"{report.consistency_score:.1f}%")
        with col3:
            st.metric("Accuracy", f"{report.accuracy_score:.1f}%")
        with col4:
            st.metric("Uniqueness", f"{report.uniqueness_score:.1f}%")
        with col5:
            st.metric("Timeliness", f"{report.timeliness_score:.1f}%")

        # Quality visualization
        self.render_quality_radar_chart(report)

        # Issues and recommendations
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ⚠️ Issues Found")
            if report.issues:
                for issue in report.issues:
                    severity_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                    st.write(
                        f"{severity_color.get(issue['severity'], '🔵')} **{issue['type'].title()}**: {issue['description']}"  # noqa: E501
                    )
            else:
                st.success("No issues found!")

        with col2:
            st.markdown("### 💡 Recommendations")
            if report.recommendations:
                for rec in report.recommendations:
                    st.write(f"• {rec}")
            else:
                st.success("No recommendations needed!")

    def render_export_deploy(self) -> None:
        """Render the export and deployment page."""
        if not st.session_state.selected_dataset_id:
            st.warning("Please select a dataset from the sidebar.")
            return

        dataset = self.manager.get_dataset(st.session_state.selected_dataset_id)
        if not dataset:
            st.error("Dataset not found!")
            return

        st.markdown(
            '<div class="section-header">📥 Export & Deploy</div>',
            unsafe_allow_html=True,
        )

        # Export options
        st.markdown("### 📦 Export Options")

        col1, col2 = st.columns(2)

        with col1:
            export_format = st.selectbox(
                "Export Format",
                options=["csv", "parquet", "json"],
                help="Choose the format for exporting your dataset",
            )

            include_metadata = st.checkbox(
                "Include Metadata",
                value=True,
                help="Include dataset schema and quality report",
            )

        with col2:
            export_split = st.selectbox(
                "Data Split",
                options=["full", "train_test", "train_val_test"],
                help="How to split the data for ML training",
            )

            if export_split != "full":
                st.slider(
                    "Test set Size (%)",
                    min_value=10,
                    max_value=50,
                    value=20,
                    help="Percentage of data for testing",
                )

        # Export action
        if st.button("📥 Export Dataset", type="primary"):
            try:
                export_path = self.manager.export_dataset(
                    dataset.dataset_id,
                    format_type=export_format,
                    include_metadata=include_metadata,
                )
                st.success(f"✅ Dataset exported successfully to: {export_path}")

                # Show download link (in a real app, this would be a downloadable file)
                st.info("💾 Export completed! In a production environment, you would see download links here.")

            except Exception as e:
                st.error(f"Export failed: {e}")

        # Deployment options
        st.markdown("### 🚀 Deployment Options")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ML Platform Integration")
            platform = st.selectbox(
                "Target Platform",
                options=[
                    "local",
                    "aws_sagemaker",
                    "azure_ml",
                    "gcp_vertex",
                    "databricks",
                ],
                help="Choose the ML platform for deployment",
            )

            if st.button("🚀 Deploy to Platform"):
                st.info(f"Deployment to {platform} would be initiated here!")

        with col2:
            st.markdown("#### API Endpoint")
            if st.button("🔗 Create API Endpoint"):
                st.info("API endpoint creation would be handled here!")

            st.markdown("#### Schedule Updates")
            if st.button("⏰ Schedule Data Refresh"):
                st.info("Data refresh scheduling would be configured here!")

    def process_dataset_action(self, dataset_id: str) -> None:
        """Process a dataset and show progress."""
        self.utils.process_dataset_action(dataset_id)

    def show_quality_report(self, report) -> None:
        """Show detailed quality report."""
        self.utils.show_quality_report(report)

    def delete_dataset_confirmation(self) -> None:
        """Show dataset deletion confirmation."""
        self.utils.delete_dataset_confirmation()

    def render_database_source_config(self) -> None:
        """Render database source configuration."""
        self.source_configs.render_database_source_config()

    def render_file_source_config(self) -> None:
        """Render file source configuration."""
        self.source_configs.render_file_source_config()

    def render_historian_source_config(self) -> None:
        """Render historian source configuration."""
        self.source_configs.render_historian_source_config()

    def render_opc_source_config(self) -> None:
        """Render OPC source configuration."""
        self.source_configs.render_opc_source_config()

    def render_api_source_config(self) -> None:
        """Render API source configuration."""
        self.source_configs.render_api_source_config()

    def calculate_average_quality(self, datasets: list[dict[str, Any]]) -> float:
        """Calculate average quality score across datasets."""
        return DatasetUIUtils.calculate_average_quality(datasets)

    def get_quality_color(self, quality: DataQuality) -> str:
        """Get color for quality level."""
        return DatasetUIUtils.get_quality_color(quality)

    def render_status_chart(self, datasets: list[dict[str, Any]]) -> None:
        """Render dataset status distribution chart."""
        DatasetUIUtils.render_status_chart(datasets)

    def render_type_chart(self, datasets: list[dict[str, Any]]) -> None:
        """Render dataset type distribution chart."""
        DatasetUIUtils.render_type_chart(datasets)

    def render_quality_radar_chart(self, report) -> None:
        """Render quality metrics radar chart."""
        DatasetUIUtils.render_quality_radar_chart(report)


def main() -> None:
    """Main function to run the Streamlit app."""
    try:
        ui = DatasetCurationUI()
        ui.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
