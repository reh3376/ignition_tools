"""Ignition Gateway Connection Module.

This module provides functionality for connecting to and managing
Ignition Gateway instances, including authentication, health monitoring,
and API operations.
"""

from .client import GatewayConnectionPool, IgnitionGatewayClient
from .config import GatewayConfig, GatewayConfigManager

__all__ = [
    "GatewayConfig",
    "GatewayConfigManager",
    "GatewayConnectionPool",
    "IgnitionGatewayClient",
]
