"""OPC-UA CLI Module

Command-line interface components for OPC-UA client operations.
Provides safe, read-only access to OPC-UA servers through rich CLI commands.
"""

from .commands import opcua

__all__ = ["opcua"]
