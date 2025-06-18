"""Ignition System Function Wrappers Package.

This package provides enhanced wrappers around Ignition system functions with:
- Comprehensive error handling and logging
- Input validation and type checking
- Consistent return value formatting
- Performance monitoring and metrics
- Context-aware behavior based on Ignition environment
"""

from .system_alarm import SystemAlarmWrapper
from .system_db import SystemDbWrapper
from .system_gui import SystemGuiWrapper
from .system_nav import SystemNavWrapper
from .system_tag import SystemTagWrapper
from .system_util import SystemUtilWrapper
from .wrapper_base import IgnitionWrapperBase, WrapperConfig, WrapperError

__all__ = [
    "IgnitionWrapperBase",
    "SystemAlarmWrapper",
    "SystemDbWrapper",
    "SystemGuiWrapper",
    "SystemNavWrapper",
    "SystemTagWrapper",
    "SystemUtilWrapper",
    "WrapperConfig",
    "WrapperError",
]

__version__ = "1.0.0"
