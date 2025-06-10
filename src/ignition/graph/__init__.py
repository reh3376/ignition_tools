"""Ignition Graph Database Package

Provides graph database functionality for storing and querying Ignition
system functions, contexts, templates, and their relationships.

This serves as the AI Assistant's persistent long-term memory system.
"""

from .client import IgnitionGraphClient
from .populator import IgnitionGraphPopulator
from .schema import IgnitionGraphSchema

# from .queries import IgnitionGraphQueries      # Will create next

__all__ = [
    "IgnitionGraphSchema",
    "IgnitionGraphClient",
    "IgnitionGraphPopulator",
    # 'IgnitionGraphQueries'
]
