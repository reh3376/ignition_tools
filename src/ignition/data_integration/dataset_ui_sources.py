"""Dataset UI Data Source Configuration.

This module contains data source configuration methods extracted from
the DatasetCurationUI class to improve maintainability and reduce complexity.
"""

import streamlit as st


class DatasetUISourceConfigurators:
    """Data source configuration methods for dataset UI."""

    @staticmethod
    def render_database_source_config() -> None:
        """Render database source configuration."""
        st.markdown("#### Database Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.selectbox(
                "Database Configuration",
                options=["neo4j_default", "postgres_local", "supabase_prod"],
                help="Select a pre-configured database connection",
            )

            st.text_area(
                "SQL Query",
                placeholder="SELECT * FROM sensor_data WHERE timestamp > NOW() - INTERVAL '24 hours'",
                help="SQL query to extract data",
            )

        with col2:
            st.number_input(
                "Refresh Interval (minutes)",
                min_value=1,
                value=60,
                help="How often to refresh data from this source",
            )

            st.number_input(
                "Row Limit",
                min_value=0,
                value=10000,
                help="Maximum number of rows to extract (0 = no limit)",
            )

    @staticmethod
    def render_file_source_config() -> None:
        """Render file source configuration."""
        st.markdown("#### File Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "File Path",
                placeholder="/path/to/data.csv",
                help="Path to the data file",
            )

            file_type = st.selectbox(
                "File Type",
                options=["csv", "parquet", "json", "xlsx"],
                help="Type of file to read",
            )

        with col2:
            if file_type == "csv":
                st.text_input("Delimiter", value=",")
                st.checkbox("Has Header", value=True)
            elif file_type == "xlsx":
                st.text_input("Sheet Name", value="Sheet1")

    @staticmethod
    def render_historian_source_config() -> None:
        """Render historian source configuration."""
        st.markdown("#### Historian Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.selectbox(
                "Historian Type",
                options=["influxdb", "timescaledb", "ignition"],
                help="Type of historian database",
            )

            st.text_area(
                "Tag Names (one per line)",
                placeholder="Temperature_01\nPressure_02\nFlow_Rate_03",
                help="list of tags to extract",
            )

        with col2:
            st.selectbox(
                "Time Range",
                options=["1h", "6h", "24h", "7d", "30d", "custom"],
                help="Time range for data extraction",
            )

            st.selectbox(
                "Aggregation",
                options=["raw", "avg", "min", "max", "sum"],
                help="Data aggregation method",
            )

    @staticmethod
    def render_opc_source_config() -> None:
        """Render OPC source configuration."""
        st.markdown("#### OPC Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "OPC Server URL",
                placeholder="opc.tcp://localhost:4840",
                help="OPC UA server endpoint",
            )

            st.text_area(
                "Tag Paths (one per line)",
                placeholder="ns=2;s=PLC1.Temperature\nns=2;s=PLC1.Pressure",
                help="OPC tag paths to read",
            )

        with col2:
            st.number_input(
                "Sampling Rate (seconds)",
                min_value=1,
                value=60,
                help="How often to sample tag values",
            )

            st.checkbox(
                "Use Subscription",
                value=True,
                help="Use OPC subscriptions for real-time data",
            )

    @staticmethod
    def render_api_source_config() -> None:
        """Render API source configuration."""
        st.markdown("#### API Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "API URL",
                placeholder="https://api.example.com/data",
                help="REST API endpoint",
            )

            st.selectbox(
                "HTTP Method", options=["GET", "POST"], help="HTTP method to use"
            )

        with col2:
            auth_type = st.selectbox(
                "Authentication",
                options=["none", "api_key", "bearer_token", "basic"],
                help="Authentication method",
            )

            if auth_type != "none":
                st.text_input(
                    "Auth Value", type="password", help="Authentication credential"
                ) 