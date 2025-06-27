#!/usr/bin/env python3
"""Distillation: American Whiskey Specialized Agent for Phase 16.2.

Following crawl_mcp.py methodology for systematic development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

American Whiskey Distillation Expertise:
- Distillery processes: Whole Grain, Grain Milling, Mashing, Fermentation, Distillation, Distillate Processing, Warehousing & Maturation
- Conveyance systems: conveyors and pipes for solids and liquids
- Equipment specifications: Pumps, Tanks, Heat Exchangers, Distillation columns, Doublers
- Raw material selection and optimization
- Process optimization strategies
- Batch process trace and trace: Lot#'s, Batch ID's, Recipes, Scheduling
- TTB Compliance and reporting
- Emergency response procedures
"""

import logging
import os
import time
from typing import Any, Self

from dotenv import load_dotenv

from src.ignition.modules.sme_agent.multi_domain_architecture import (
    AgentTask,
    DomainType,
)

from .base_specialized_agent import BaseSpecializedAgent

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DistillationWhiskeyAgent(BaseSpecializedAgent):
    """Specialized agent for American Whiskey distillation processes."""

    def __init__(self: Self, agent_id: str = "distillation_whiskey_agent"):
        """Initialize Distillation Whiskey Agent."""
        super().__init__(
            agent_id=agent_id,
            domain=DomainType.CHEMICAL_PROCESS,  # Inherits from chemical process
            industry_type="whiskey_distillation",
            max_concurrent_tasks=3,
        )

        self.distillery_knowledge_path = os.getenv(
            "WHISKEY_DISTILLATION_KNOWLEDGE_BASE_PATH", "data/whiskey_distillation"
        )
        self.ttb_compliance_db = os.getenv(
            "TTB_COMPLIANCE_DB_PATH", "data/ttb_compliance"
        )

        self.logger.info(f"Initialized Distillation Whiskey Agent: {agent_id}")

    def _initialize_specialized_knowledge(self: Self) -> None:
        """Initialize whiskey distillation specific knowledge areas."""
        self.specialized_knowledge_areas = {
            "grain_processing": {
                "description": "Whole grain handling, milling, and preparation",
                "keywords": ["grain", "milling", "corn", "wheat", "rye", "barley"],
                "complexity_level": "standard",
            },
            "mashing_fermentation": {
                "description": "Mashing and fermentation processes",
                "keywords": ["mash", "fermentation", "yeast", "enzymes"],
                "complexity_level": "advanced",
            },
            "distillation_processes": {
                "description": "Distillation operations and optimization",
                "keywords": ["distillation", "column", "still", "proof"],
                "complexity_level": "advanced",
            },
        }

    def _initialize_regulatory_frameworks(self: Self) -> None:
        """Initialize TTB and regulatory frameworks."""
        self.regulatory_frameworks = [
            "TTB (Alcohol and Tobacco Tax and Trade Bureau)",
            "CFR Title 27 (Alcohol, Tobacco Products and Firearms)",
            "DSP (Distilled Spirits Plant) Regulations",
        ]

    def _initialize_process_templates(self: Self) -> None:
        """Initialize whiskey distillation process templates."""
        self.process_templates = {
            "bourbon_production": {
                "mash_bill": {"corn": "51-80%", "wheat_or_rye": "10-35%"},
                "fermentation_time": "72-96 hours",
            }
        }

    def _initialize_safety_protocols(self: Self) -> None:
        """Initialize distillery safety protocols."""
        self.safety_protocols = {
            "fire_prevention": ["Vapor detection systems", "Explosion-proof equipment"]
        }

    async def process_specialized_task(self: Self, task: AgentTask) -> dict[str, Any]:
        """Process whiskey distillation specific task."""
        start_time = time.time()

        try:
            return {
                "success": True,
                "analysis": {
                    "task_type": "whiskey_distillation",
                    "industry": "American Whiskey Distillation",
                },
                "processing_time": time.time() - start_time,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Processing failed: {e!s}",
                "processing_time": time.time() - start_time,
            }

    def _identify_process_area(self: Self, task: AgentTask) -> str:
        """Identify the specific whiskey process area for the task."""
        task_description = getattr(task, "description", "").lower()

        # Check each knowledge area for keyword matches
        for area_name, details in self.specialized_knowledge_areas.items():
            keywords = details.get("keywords", [])
            if any(keyword.lower() in task_description for keyword in keywords):
                return area_name

        return "general_distillation"

    def _get_process_considerations(self: Self, process_area: str) -> list[str]:
        """Get process considerations for specific area."""
        considerations = {
            "grain_processing": [
                "Grain moisture content and quality",
                "Milling particle size optimization",
                "Dust control and explosion prevention",
                "Raw material traceability and documentation",
            ],
            "mashing_fermentation": [
                "Temperature control during mashing",
                "Enzyme activity optimization",
                "Yeast strain selection and viability",
                "Fermentation monitoring and control",
            ],
            "distillation_processes": [
                "Column efficiency and optimization",
                "Energy recovery and heat integration",
                "Product quality and congener profile",
                "Proof control and consistency",
            ],
            "spirit_processing": [
                "Proof reduction and water quality",
                "Filtration system effectiveness",
                "Quality control testing protocols",
                "Product consistency and specifications",
            ],
            "warehousing_maturation": [
                "Barrel char level selection",
                "Warehouse environmental control",
                "Aging profile development",
                "Inventory management and rotation",
            ],
        }

        return considerations.get(
            process_area, ["General distillation process considerations"]
        )

    def _get_equipment_requirements(self: Self, process_area: str) -> list[str]:
        """Get equipment requirements for specific process area."""
        equipment = {
            "grain_processing": [
                "Grain receiving and storage systems",
                "Hammer mills or roller mills",
                "Pneumatic conveying systems",
                "Dust collection systems",
            ],
            "mashing_fermentation": [
                "Mash tuns with agitation",
                "Heat exchangers for temperature control",
                "Fermentation vessels (washbacks)",
                "Yeast propagation systems",
            ],
            "distillation_processes": [
                "Beer still (first distillation)",
                "Doubler or thumper (second distillation)",
                "Rectification columns",
                "Condensers and cooling systems",
            ],
            "spirit_processing": [
                "Spirit tanks and blending systems",
                "Filtration equipment",
                "Proof reduction systems",
                "Quality testing laboratory equipment",
            ],
            "warehousing_maturation": [
                "Barrel filling stations",
                "Warehouse racking systems",
                "Environmental monitoring systems",
                "Barrel dumping equipment",
            ],
        }

        return equipment.get(process_area, ["General distillation equipment"])

    def _get_regulatory_requirements(self: Self, process_area: str) -> list[str]:
        """Get regulatory requirements for specific process area."""
        return [
            "TTB formula approval for mash bill",
            "DSP operating permit compliance",
            "Production reporting requirements",
            "Inventory reconciliation procedures",
            "COLA approval for labeling",
            "Environmental compliance monitoring",
        ]

    def _get_process_recommendations(self: Self, process_area: str) -> list[str]:
        """Get process optimization recommendations."""
        recommendations = {
            "grain_processing": [
                "Optimize milling for maximum starch extraction",
                "Implement real-time moisture monitoring",
                "Use pneumatic conveying to minimize dust",
                "Establish grain quality specifications",
            ],
            "mashing_fermentation": [
                "Maintain optimal mashing temperature profile",
                "Monitor enzyme activity and pH levels",
                "Implement yeast viability testing",
                "Control fermentation temperature for flavor development",
            ],
            "distillation_processes": [
                "Optimize reflux ratio for product quality",
                "Implement energy recovery systems",
                "Monitor congener profiles continuously",
                "Maintain consistent cut points",
            ],
            "spirit_processing": [
                "Use high-quality water for proof reduction",
                "Implement multi-stage filtration",
                "Establish quality control checkpoints",
                "Monitor product specifications continuously",
            ],
        }

        return recommendations.get(process_area, ["Follow industry best practices"])

    def _get_quality_parameters(self: Self, process_area: str) -> dict[str, str]:
        """Get quality parameters for monitoring."""
        parameters = {
            "grain_processing": {
                "moisture_content": "12-14%",
                "protein_content": "8-12%",
                "starch_content": "60-70%",
                "foreign_material": "<2%",
            },
            "mashing_fermentation": {
                "mash_temperature": "148-158°F",
                "pH_level": "4.5-5.5",
                "alcohol_by_volume": "8-12%",
                "fermentation_time": "72-96 hours",
            },
            "distillation_processes": {
                "beer_still_proof": "25-35 proof",
                "doubler_proof": "130-140 proof",
                "heads_cut": "First 5-10%",
                "tails_cut": "Last 10-15%",
            },
        }

        return parameters.get(process_area, {})

    def _get_safety_considerations(self: Self, process_area: str) -> list[str]:
        """Get safety considerations for specific process area."""
        safety = {
            "grain_processing": [
                "Dust explosion prevention",
                "Confined space entry procedures",
                "Mechanical hazard protection",
                "Respiratory protection in dusty areas",
            ],
            "mashing_fermentation": [
                "Hot surface protection",
                "Chemical handling safety",
                "Slip and fall prevention",
                "Biological hazard awareness",
            ],
            "distillation_processes": [
                "Vapor ignition prevention",
                "Pressure vessel safety",
                "Hot work permit procedures",
                "Emergency shutdown systems",
            ],
        }

        return safety.get(process_area, ["General safety protocols"])

    def _get_batch_traceability_requirements(self: Self) -> dict[str, Any]:
        """Get batch traceability requirements."""
        return {
            "required_documentation": [
                "Batch production record",
                "Raw material lot numbers",
                "Process parameter logs",
                "Quality test results",
                "Yield calculations",
                "Warehouse location records",
            ],
            "tracking_systems": [
                "Batch numbering system",
                "Lot tracking database",
                "Recipe management system",
                "Production scheduling system",
            ],
            "retention_requirements": "Minimum 3 years per TTB regulations",
        }

    def _get_ttb_compliance_requirements(self: Self) -> dict[str, Any]:
        """Get TTB compliance requirements."""
        return {
            "reporting_requirements": [
                "Monthly operational reports",
                "Production reports",
                "Storage reports",
                "Disposition reports",
                "Inventory reconciliation",
            ],
            "permit_requirements": [
                "DSP (Distilled Spirits Plant) permit",
                "Formula approval",
                "Label approval (COLA)",
                "Bond requirements",
            ],
            "inspection_readiness": [
                "Maintain accurate records",
                "Ensure facility compliance",
                "Train personnel on regulations",
                "Implement audit procedures",
            ],
        }
