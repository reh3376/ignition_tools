"""Ignition Data Integration Scripts.

This module provides comprehensive data integration capabilities for Ignition SCADA systems,
including database connections, historian queries, OPC tag operations, and report generation.

Key Features:
- Multi-database support (Neo4j, PostgreSQL/Supabase, SQL Server, MySQL, etc.)
- Historian/time series database integration
- OPC tag browsing and creation scripts
- Report generation with multiple output formats
- Environment-based configuration management
- Production-ready error handling and logging

Usage:
    from ignition.data_integration import (
        DatabaseConnectionManager,
        HistorianQueryGenerator,
        OPCTagManager,
        ReportGenerator
    )
"""

from .database_connections import DatabaseConnectionManager, DatabaseType
from .historian_queries import HistorianQueryGenerator, HistorianType
from .opc_tag_manager import OPCTagManager, TagOperation
from .report_generator import ReportFormat, ReportGenerator

__all__ = [
    "DatabaseConnectionManager",
    "DatabaseType",
    "HistorianQueryGenerator",
    "HistorianType",
    "OPCTagManager",
    "ReportFormat",
    "ReportGenerator",
    "TagOperation",
]

__version__ = "1.0.0"
