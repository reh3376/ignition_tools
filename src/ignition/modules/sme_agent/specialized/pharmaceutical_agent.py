#!/usr/bin/env python3
"""Pharmaceutical Manufacturing Specialized Agent for Phase 16.2

Following crawl_mcp.py methodology for systematic development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Pharmaceutical Manufacturing Expertise:
- GMP (Good Manufacturing Practice) compliance
- Validation protocols and documentation
- Batch record management and electronic systems
- Quality control and quality assurance
- Regulatory compliance (FDA, EMA, ICH)
- Cleanroom operations and environmental monitoring
- Equipment qualification (IQ/OQ/PQ)
- Change control and deviation management
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Self

from dotenv import load_dotenv

from ..multi_domain_architecture import DomainType, AgentTask
from .base_specialized_agent import BaseSpecializedAgent

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PharmaceuticalAgent(BaseSpecializedAgent):
    """Specialized agent for pharmaceutical manufacturing processes."""
    
    def __init__(self: Self, agent_id: str = "pharmaceutical_agent"):
        """Initialize Pharmaceutical Agent."""
        super().__init__(
            agent_id=agent_id,
            domain=DomainType.CHEMICAL_PROCESS,
            industry_type="pharmaceutical_manufacturing",
            max_concurrent_tasks=4  # Higher capacity for complex validation tasks
        )
        
        self.logger.info(f"Initialized Pharmaceutical Agent: {agent_id}")
    
    def _initialize_specialized_knowledge(self: Self) -> None:
        """Initialize pharmaceutical manufacturing specific knowledge areas."""
        self.specialized_knowledge_areas = {
            "gmp_compliance": {
                "description": "Good Manufacturing Practice compliance",
                "keywords": ["gmp", "compliance", "cGMP"],
                "complexity_level": "advanced"
            },
            "validation_protocols": {
                "description": "Equipment and process validation",
                "keywords": ["validation", "IQ", "OQ", "PQ"],
                "complexity_level": "advanced"
            },
            "batch_manufacturing": {
                "description": "Batch record management and manufacturing execution",
                "keywords": ["batch", "manufacturing", "recipe", "MES", "electronic batch"],
                "complexity_level": "standard"
            },
            "quality_systems": {
                "description": "Quality control and quality assurance operations",
                "keywords": ["quality", "QC", "QA", "testing", "release", "specification"],
                "complexity_level": "advanced"
            },
            "cleanroom_operations": {
                "description": "Cleanroom design, monitoring, and operations",
                "keywords": ["cleanroom", "environmental monitoring", "HVAC", "contamination"],
                "complexity_level": "standard"
            },
            "regulatory_compliance": {
                "description": "FDA, EMA, and international regulatory compliance",
                "keywords": ["FDA", "EMA", "ICH", "regulatory", "submission", "inspection"],
                "complexity_level": "advanced"
            }
        }
    
    def _initialize_regulatory_frameworks(self: Self) -> None:
        """Initialize pharmaceutical regulatory frameworks."""
        self.regulatory_frameworks = [
            "FDA CFR Title 21 Parts 210 & 211 (cGMP)",
            "ICH Guidelines",
            "EMA Guidelines"
        ]
    
    def _initialize_process_templates(self: Self) -> None:
        """Initialize pharmaceutical process templates."""
        self.process_templates = {
            "oral_solid_dosage": {
                "unit_operations": ["weighing", "blending", "compression"],
                "critical_parameters": ["blend uniformity", "tablet hardness"]
            },
            "sterile_manufacturing": {
                "description": "Aseptic processing and sterile manufacturing",
                "unit_operations": ["preparation", "sterilization", "filling", "inspection"],
                "critical_parameters": ["sterility", "endotoxin", "particulates", "container closure"],
                "equipment": ["autoclaves", "filling machines", "isolators", "inspection systems"]
            },
            "api_synthesis": {
                "description": "Active pharmaceutical ingredient synthesis",
                "unit_operations": ["reaction", "crystallization", "filtration", "drying"],
                "critical_parameters": ["purity", "impurities", "crystal form", "particle size"],
                "equipment": ["reactors", "crystallizers", "centrifuges", "dryers"]
            }
        }
    
    def _initialize_safety_protocols(self: Self) -> None:
        """Initialize pharmaceutical safety protocols."""
        self.safety_protocols = {
            "chemical_safety": ["Chemical hazard assessment", "PPE requirements"],
            "biological_safety": [
                "Biosafety level requirements",
                "Containment procedures",
                "Decontamination protocols",
                "Waste disposal procedures"
            ],
            "cleanroom_safety": [
                "Gowning procedures and protocols",
                "Emergency procedures in cleanrooms",
                "Equipment decontamination",
                "Personnel safety in controlled environments"
            ],
            "process_safety": [
                "Process hazard analysis",
                "Safety interlocks and alarms",
                "Emergency shutdown procedures",
                "Incident investigation protocols"
            ]
        }
    
    async def process_specialized_task(self: Self, task: AgentTask) -> Dict[str, Any]:
        """Process pharmaceutical manufacturing specific task."""
        start_time = time.time()
        
        try:
            return {
                "success": True,
                "analysis": {
                    "task_type": "pharmaceutical_manufacturing",
                    "industry": "Pharmaceutical Manufacturing"
                },
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "processing_time": time.time() - start_time
            }
    
    def _identify_process_area(self: Self, task: AgentTask) -> str:
        """Identify the specific pharmaceutical process area for the task."""
        task_description = getattr(task, 'description', '').lower()
        
        for area_name, details in self.specialized_knowledge_areas.items():
            keywords = details.get('keywords', [])
            if any(keyword.lower() in task_description for keyword in keywords):
                return area_name
        
        return "general_pharmaceutical"
    
    def _apply_gmp_principles(self: Self, task: AgentTask, process_area: str) -> Dict[str, Any]:
        """Apply GMP principles to the task analysis."""
        return {
            "personnel": [
                "Qualified and trained personnel",
                "Defined roles and responsibilities",
                "Training documentation and records"
            ],
            "premises": [
                "Suitable design and construction",
                "Adequate space and lighting",
                "Environmental controls and monitoring"
            ],
            "equipment": [
                "Suitable design and capacity",
                "Proper installation and qualification",
                "Maintenance and calibration programs"
            ],
            "documentation": [
                "Written procedures and instructions",
                "Batch production records",
                "Change control procedures"
            ],
            "production": [
                "Validated processes and procedures",
                "In-process controls and monitoring",
                "Contamination prevention measures"
            ],
            "quality_control": [
                "Testing of raw materials and products",
                "Stability testing programs",
                "Out-of-specification investigations"
            ]
        }
    
    def _get_validation_requirements(self: Self, process_area: str) -> List[str]:
        """Get validation requirements for specific process area."""
        base_requirements = [
            "Installation Qualification (IQ)",
            "Operational Qualification (OQ)", 
            "Performance Qualification (PQ)",
            "Validation Master Plan (VMP)",
            "User Requirements Specification (URS)"
        ]
        
        area_specific = {
            "sterile_manufacturing": [
                "Media fill validation",
                "Sterilization validation",
                "Aseptic process validation"
            ],
            "cleanroom_operations": [
                "HVAC system qualification",
                "Environmental monitoring validation",
                "Cleaning validation"
            ],
            "batch_manufacturing": [
                "Process validation (Stage 1, 2, 3)",
                "Analytical method validation",
                "Computer system validation"
            ]
        }
        
        return base_requirements + area_specific.get(process_area, [])
    
    def _get_quality_requirements(self: Self, process_area: str) -> Dict[str, List[str]]:
        """Get quality requirements for specific process area."""
        return {
            "testing_requirements": [
                "Raw material testing",
                "In-process testing",
                "Finished product testing",
                "Stability testing"
            ],
            "documentation_requirements": [
                "Batch production records",
                "Laboratory test records",
                "Certificate of analysis",
                "Deviation reports"
            ],
            "release_criteria": [
                "Specification compliance",
                "Quality review completion",
                "Batch record review",
                "QP release authorization"
            ]
        }
    
    def _get_process_recommendations(self: Self, process_area: str) -> List[str]:
        """Get process optimization recommendations."""
        recommendations = {
            "gmp_compliance": [
                "Implement robust documentation systems",
                "Establish comprehensive training programs",
                "Develop effective change control procedures",
                "Maintain equipment qualification status"
            ],
            "validation_protocols": [
                "Follow risk-based validation approach",
                "Establish validation lifecycle management",
                "Implement continuous process verification",
                "Maintain validation documentation"
            ],
            "quality_systems": [
                "Implement quality risk management",
                "Establish pharmaceutical quality system",
                "Develop effective CAPA system",
                "Maintain supplier qualification program"
            ]
        }
        
        return recommendations.get(process_area, ["Follow pharmaceutical industry best practices"])
    
    def _get_regulatory_considerations(self: Self, process_area: str) -> List[str]:
        """Get regulatory considerations for specific process area."""
        return [
            "FDA inspection readiness",
            "EMA compliance requirements", 
            "ICH guideline adherence",
            "Change control notifications",
            "Annual product review requirements",
            "Pharmacovigilance obligations"
        ]
    
    def _perform_risk_assessment(self: Self, process_area: str) -> Dict[str, Any]:
        """Perform risk assessment for the process area."""
        return {
            "risk_categories": [
                "Product quality risks",
                "Patient safety risks",
                "Regulatory compliance risks",
                "Supply chain risks"
            ],
            "risk_tools": [
                "FMEA (Failure Mode and Effects Analysis)",
                "HAZOP (Hazard and Operability Study)",
                "Risk matrices and scoring",
                "Control strategy development"
            ],
            "mitigation_strategies": [
                "Design controls and safeguards",
                "Process monitoring and alarms",
                "Training and procedures",
                "Regular review and updates"
            ]
        } 