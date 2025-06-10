"""Ignition Gateway Connection Module.

This module provides functionality for connecting to and managing
Ignition Gateway instances, including authentication, health monitoring,
and API operations.
"""

from .config import GatewayConfig, GatewayConfigManager
from .client import IgnitionGatewayClient, GatewayConnectionPool

__all__ = [
    "GatewayConfig", 
    "GatewayConfigManager",
    "IgnitionGatewayClient",
    "GatewayConnectionPool"
] 