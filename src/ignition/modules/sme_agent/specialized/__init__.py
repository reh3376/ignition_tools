#!/usr/bin/env python3
"""Specialized Expertise Modules for Phase 16.2 Multi-Domain Architecture.

Following crawl_mcp.py methodology for systematic development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

This package contains industry-specific SME agents with specialized knowledge:
- Distillation: American Whiskey manufacturing processes
- Pharmaceutical: GMP compliance and manufacturing
- Power Generation: Thermal and renewable power systems
"""

from .base_specialized_agent import BaseSpecializedAgent
from .distillation_whiskey_agent import DistillationWhiskeyAgent
from .pharmaceutical_agent import PharmaceuticalAgent
from .power_generation_agent import PowerGenerationAgent

__all__ = [
    "BaseSpecializedAgent",
    "DistillationWhiskeyAgent",
    "PharmaceuticalAgent",
    "PowerGenerationAgent",
]

__version__ = "16.2.0"
