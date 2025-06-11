"""OPC-UA Live Client Integration Module.

Provides real OPC-UA client functionality for industrial automation,
integrating with FreeOpcUa libraries for production-grade connectivity.
"""

from .browser import AddressSpaceBrowser
from .client import IgnitionOPCUAClient
from .connection import ConnectionManager
from .security import SecurityManager
from .subscription import SubscriptionManager

__version__ = "0.1.0"
__author__ = "Ignition Tools Project"

__all__ = [
    "AddressSpaceBrowser",
    "ConnectionManager",
    "IgnitionOPCUAClient",
    "SecurityManager",
    "SubscriptionManager",
]
