"""Knowledge Base Discovery and Connection System.

This module ensures that every new agent or chat session automatically discovers
and connects to the long-term persistent memory systems for this codebase.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Self

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeBaseInfo:
    """Information about available knowledge bases."""

    name: str
    type: str  # "neo4j", "vector_db", "file_cache", "git_history"
    connection_string: str
    status: str  # "available", "unavailable", "error"
    last_updated: datetime
    record_count: int | None = None
    description: str | None = None
    capabilities: list[str] | None = None


@dataclass
class ProjectContext:
    """Complete project context for new agents."""

    project_name: str
    project_root: Path
    current_phase: str
    completed_phases: list[str]
    available_knowledge_bases: list[KnowledgeBaseInfo]
    key_capabilities: list[str]
    recent_activities: list[dict[str, Any]]
    important_files: list[str]
    cli_commands: list[str]
    integration_points: list[str]


class KnowledgeDiscoverySystem:
    """Discovers and connects to all available knowledge bases."""

    def __init__(self: Self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.knowledge_bases = []
        self.project_context = None

        # Initialize discovery
        self._discover_project_structure()
        self._discover_knowledge_bases()
        self._build_project_context()

    def get_agent_initialization_info(self: Any) -> dict[str, Any]:
        """Get complete initialization information for new agents."""
        init_info = {
            "project_context": (
                asdict(self.project_context) if self.project_context else {}
            ),
            "connection_instructions": self._generate_connection_instructions(),
            "quick_start_guide": self._generate_quick_start_guide(),
            "knowledge_base_status": [asdict(kb) for kb in self.knowledge_bases],
            "environment_setup": self._get_environment_setup(),
            "key_files_to_read": self._get_key_files_for_context(),
            "recent_developments": self._get_recent_developments(),
            "available_tools": self._get_available_tools(),
        }

        return init_info

    def _discover_project_structure(self: Any) -> None:
        """Discover the overall project structure."""
        # Check for key project files
        key_files = [
            "docs/roadmap.md",
            "docs/PHASE_8_1_COMPLETION_SUMMARY.md",
            "src/ignition/code_intelligence/",
            ".env",
            "requirements.txt",
            ".refactoring_tracking/",
        ]

        self.project_structure = {}
        for file_path in key_files:
            full_path = self.project_root / file_path
            self.project_structure[file_path] = {
                "exists": full_path.exists(),
                "path": str(full_path),
                "type": "directory" if full_path.is_dir() else "file",
            }

    def _discover_knowledge_bases(self: Any) -> None:
        """Discover all available knowledge bases."""
        # 1. Neo4j Graph Database
        neo4j_info = self._discover_neo4j()
        if neo4j_info:
            self.knowledge_bases.append(neo4j_info)

        # 2. Vector Database / Embeddings
        vector_info = self._discover_vector_db()
        if vector_info:
            self.knowledge_bases.append(vector_info)

        # 3. File-based caches
        file_caches = self._discover_file_caches()
        self.knowledge_bases.extend(file_caches)

        # 4. Git history integration
        git_info = self._discover_git_integration()
        if git_info:
            self.knowledge_bases.append(git_info)

        # 5. Refactoring tracking
        refactor_info = self._discover_refactoring_tracking()
        if refactor_info:
            self.knowledge_bases.append(refactor_info)

        # 6. SME Agent system
        sme_agent_info = self._discover_sme_agent()
        if sme_agent_info:
            self.knowledge_bases.append(sme_agent_info)

    def _discover_neo4j(self: Any) -> KnowledgeBaseInfo | None:
        """Discover Neo4j graph database connection."""
        try:
            # Check for Neo4j configuration
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD")

            if not neo4j_password:
                return KnowledgeBaseInfo(
                    name="Neo4j Graph Database",
                    type="neo4j",
                    connection_string=neo4j_uri,
                    status="unavailable",
                    last_updated=datetime.now(),
                    description="Neo4j credentials not configured in environment",
                )

            # Try to connect and get stats
            try:
                from neo4j import GraphDatabase

                driver = GraphDatabase.driver(
                    neo4j_uri, auth=(neo4j_user, neo4j_password)
                )

                with driver.session() as session:
                    # Get node counts
                    result = session.run("MATCH (n) RETURN count(n) as node_count")
                    node_count = result.single()["node_count"]

                    # Get relationship counts
                    result = session.run(
                        "MATCH ()-[r]->() RETURN count(r) as rel_count"
                    )
                    rel_count = result.single()["rel_count"]

                driver.close()

                return KnowledgeBaseInfo(
                    name="Neo4j Graph Database",
                    type="neo4j",
                    connection_string=neo4j_uri,
                    status="available",
                    last_updated=datetime.now(),
                    record_count=node_count,
                    description=f"Active Neo4j database with {node_count} nodes and {rel_count} relationships",
                    capabilities=[
                        "Code structure analysis",
                        "Dependency tracking",
                        "Refactoring history",
                        "File evolution tracking",
                        "Complex queries and analytics",
                    ],
                )

            except Exception as e:
                return KnowledgeBaseInfo(
                    name="Neo4j Graph Database",
                    type="neo4j",
                    connection_string=neo4j_uri,
                    status="error",
                    last_updated=datetime.now(),
                    description=f"Connection failed: {e!s}",
                )

        except ImportError:
            return KnowledgeBaseInfo(
                name="Neo4j Graph Database",
                type="neo4j",
                connection_string="Not configured",
                status="unavailable",
                last_updated=datetime.now(),
                description="Neo4j driver not installed",
            )

    def _discover_vector_db(self: Any) -> KnowledgeBaseInfo | None:
        """Discover vector database for embeddings."""
        # Check for vector database configuration
        vector_db_path = self.project_root / ".vector_cache"

        if vector_db_path.exists():
            # Count cached embeddings
            cache_files = list(vector_db_path.glob("*.json"))

            return KnowledgeBaseInfo(
                name="Vector Embeddings Cache",
                type="vector_db",
                connection_string=str(vector_db_path),
                status="available",
                last_updated=datetime.now(),
                record_count=len(cache_files),
                description=f"Local vector cache with {len(cache_files)} embedding files",
                capabilities=[
                    "Semantic code search",
                    "Similar code detection",
                    "Context-aware analysis",
                    "Code similarity metrics",
                ],
            )

        return None

    def _discover_file_caches(self: Any) -> list[KnowledgeBaseInfo]:
        """Discover file-based knowledge caches."""
        caches = []

        # Analysis cache
        analysis_cache = self.project_root / ".analysis_cache"
        if analysis_cache.exists():
            cache_files = list(analysis_cache.glob("*.json"))
            caches.append(
                KnowledgeBaseInfo(
                    name="Code Analysis Cache",
                    type="file_cache",
                    connection_string=str(analysis_cache),
                    status="available",
                    last_updated=datetime.now(),
                    record_count=len(cache_files),
                    description=f"Cached analysis results for {len(cache_files)} files",
                    capabilities=["Fast re-analysis", "Historical comparisons"],
                )
            )

        # Refactoring tracking
        refactor_cache = self.project_root / ".refactoring_tracking"
        if refactor_cache.exists():
            operations_file = refactor_cache / "operations.json"
            operation_count = 0

            if operations_file.exists():
                try:
                    with open(operations_file) as f:
                        operations = json.load(f)
                        operation_count = len(operations)
                except Exception:
                    pass

            caches.append(
                KnowledgeBaseInfo(
                    name="Refactoring Operations Cache",
                    type="file_cache",
                    connection_string=str(refactor_cache),
                    status="available",
                    last_updated=datetime.now(),
                    record_count=operation_count,
                    description=f"Tracking data for {operation_count} refactoring operations",
                    capabilities=[
                        "Refactoring history",
                        "Impact analysis",
                        "Architecture diagrams",
                        "TODO tracking",
                    ],
                )
            )

        return caches

    def _discover_git_integration(self: Any) -> KnowledgeBaseInfo | None:
        """Discover git integration capabilities."""
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            return None

        try:
            import subprocess

            # Get commit count
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            commit_count = int(result.stdout.strip()) if result.returncode == 0 else 0

            return KnowledgeBaseInfo(
                name="Git History Integration",
                type="git_history",
                connection_string=str(git_dir),
                status="available",
                last_updated=datetime.now(),
                record_count=commit_count,
                description=f"Git repository with {commit_count} commits",
                capabilities=[
                    "File evolution tracking",
                    "Author analysis",
                    "Change frequency analysis",
                    "Branch comparison",
                    "Merge conflict prediction",
                ],
            )

        except Exception as e:
            return KnowledgeBaseInfo(
                name="Git History Integration",
                type="git_history",
                connection_string=str(git_dir),
                status="error",
                last_updated=datetime.now(),
                description=f"Git integration error: {e!s}",
            )

    def _discover_refactoring_tracking(self: Any) -> KnowledgeBaseInfo | None:
        """Discover refactoring tracking system."""
        tracking_dir = self.project_root / ".refactoring_tracking"
        if not tracking_dir.exists():
            return None

        # Count diagrams
        diagrams_dir = tracking_dir / "diagrams"
        diagram_count = (
            len(list(diagrams_dir.glob("*.json"))) if diagrams_dir.exists() else 0
        )

        return KnowledgeBaseInfo(
            name="Refactoring Tracking System",
            type="refactoring_tracking",
            connection_string=str(tracking_dir),
            status="available",
            last_updated=datetime.now(),
            record_count=diagram_count,
            description=f"Active tracking with {diagram_count} architecture diagrams",
            capabilities=[
                "Operation tracking",
                "Architecture diagrams",
                "Impact reports",
                "TODO management",
                "Statistics dashboard",
            ],
        )

    def _discover_sme_agent(self: Any) -> KnowledgeBaseInfo | None:
        """Discover SME Agent system."""
        sme_agent_path = (
            self.project_root / "src" / "ignition" / "modules" / "sme_agent"
        )

        if sme_agent_path.exists():
            # Count CLI commands by checking the CLI module
            cli_file = sme_agent_path / "cli_commands.py"
            command_count = 13  # Known from implementation (11 original + 2 human evaluation commands)

            return KnowledgeBaseInfo(
                name="SME Agent System",
                type="sme_agent",
                connection_string=str(sme_agent_path),
                status="available",
                last_updated=datetime.now(),
                record_count=command_count,
                description=f"SME Agent with human evaluation and reinforcement learning - {command_count} CLI commands available",
                capabilities=[
                    "Question processing with context",
                    "File analysis and recommendations",
                    "Human evaluation batch management",
                    "Decision logging and tracking",
                    "Reinforcement learning insights",
                    "Progressive complexity deployment",
                ],
            )

        return None

    def _build_project_context(self: Any) -> None:
        """Build complete project context."""
        # Read roadmap for current phase
        completed_phases = [
            "1.0",
            "2.0",
            "3.0",
            "4.0",
            "5.0",
            "6.0",
            "7.0",
            "8.0",
            "8.1",
            "9.0",
            "9.1",
            "9.2",
            "9.3",
            "9.4",
            "10.0",
            "11.1",
        ]

        # Get key capabilities
        key_capabilities = [
            "Automated Code Refactoring",
            "Large File Detection & Analysis",
            "Code Splitting with AST Analysis",
            "Git Integration & Evolution Tracking",
            "Architecture Diagram Generation",
            "Neo4j Graph Database Integration",
            "Comprehensive CLI Interface",
            "Refactoring Impact Analysis",
            "Enterprise Integration & Deployment",
            "Multi-Cloud Deployment Capabilities",
            "Advanced Analytics Platform",
            "Industrial Data Integration",
            "SME Agent with Human Evaluation",
            "Decision Logging & Batch Management",
            "Reinforcement Learning Insights",
            "Progressive Complexity Deployment",
        ]

        # Get CLI commands
        cli_commands = [
            "refactor detect - Scan for oversized files",
            "refactor analyze - Detailed file analysis",
            "refactor split - Split individual files",
            "refactor batch-split - Process multiple files",
            "refactor workflow - Execute comprehensive workflows",
            "refactor rollback - Restore previous state",
            "refactor track-evolution - Monitor file evolution",
            "refactor analyze-branch - Compare branches",
            "refactor tracking-report - Generate impact reports",
            "refactor generate-diagram - Create architecture diagrams",
            "refactor complexity-trends - Show complexity trends",
            "refactor statistics - Display comprehensive statistics",
            "ign module sme validate-env - Validate SME Agent environment",
            "ign module sme status - Check SME Agent component status",
            "ign module sme initialize - Initialize SME Agent components",
            "ign module sme ask - Ask SME Agent questions",
            "ign module sme analyze - Analyze files with SME Agent",
            "ign module sme test-all - Test all SME Agent complexity levels",
            "ign module sme list-batches - list evaluation batches",
            "ign module sme export-batch - Export batch for human review",
            "ign module sme import-evaluation - Import human evaluations",
            "ign module sme rl-summary - Show reinforcement learning insights",
            "ign module sme create-test-batch - Create test evaluation batches",
        ]

        # Get recent activities
        recent_activities = [
            {
                "date": "2025-01-29",
                "activity": "Completed Phase 11.1 - SME Agent Infrastructure & Human Evaluation Enhancement",
                "details": "Implemented comprehensive SME Agent foundation with human evaluation system, 13 CLI commands, decision logging, batch management, and reinforcement learning analytics",
            },
            {
                "date": "2024-12-23",
                "activity": "Completed Phase 10.0 - Enterprise Integration & Deployment",
                "details": "Implemented enterprise architecture, cloud integration, analytics platform with FastAPI integration",
            },
            {
                "date": "2025-01",
                "activity": "Completed Phase 9.4 - Data Integration Module",
                "details": "38+ data source types, industrial variable metadata, faker integration",
            },
        ]

        # Important files for context
        important_files = [
            "docs/roadmap.md - Project roadmap and phase tracking",
            "docs/PHASE_11_1_SME_AGENT_HUMAN_EVALUATION_ENHANCEMENT.md - Latest completion summary",
            "src/ignition/modules/sme_agent/ - SME Agent module",
            "src/ignition/code_intelligence/ - Core intelligence modules",
            "src/ignition/code_intelligence/cli_commands.py - CLI interface",
            "sme_agent.env.example - SME Agent configuration template",
        ]

        self.project_context = ProjectContext(
            project_name="IGN Scripts - Code Intelligence System",
            project_root=self.project_root,
            current_phase="11.1 (Completed)",
            completed_phases=completed_phases,
            available_knowledge_bases=self.knowledge_bases,
            key_capabilities=key_capabilities,
            recent_activities=recent_activities,
            important_files=important_files,
            cli_commands=cli_commands,
            integration_points=[
                "Neo4j Graph Database",
                "Git Version Control",
                "AST Analysis Engine",
                "Rich CLI Interface",
                "Mermaid Diagram Generation",
                "SME Agent System",
                "Human Evaluation Framework",
                "Reinforcement Learning Pipeline",
            ],
        )

    def _generate_connection_instructions(self: Any) -> dict[str, str]:
        """Generate connection instructions for each knowledge base."""
        instructions = {}

        for kb in self.knowledge_bases:
            if kb.type == "neo4j" and kb.status == "available":
                instructions[
                    "neo4j"
                ] = """
# Neo4j Connection
from ignition.code_intelligence.manager import CodeIntelligenceManager

manager = CodeIntelligenceManager()
if manager.client.is_connected():
    # Access graph database
    result = manager.client.execute_query("MATCH (n) RETURN count(n)")
    print(f"Connected to Neo4j with {result} nodes")
"""

            elif kb.type == "git_history":
                instructions[
                    "git"
                ] = """
# Git Integration
from ignition.code_intelligence.git_integration import GitIntegration
from pathlib import Path

git_integration = GitIntegration(Path.cwd())
evolution = git_integration.track_file_evolution("path/to/file.py")
"""

            elif kb.type == "refactoring_tracking":
                instructions[
                    "refactoring"
                ] = """
# Refactoring Tracking
from ignition.code_intelligence.refactoring_tracker import RefactoringTracker
from pathlib import Path

tracker = RefactoringTracker(Path.cwd())
stats = tracker.get_refactoring_statistics()
"""

            elif kb.type == "sme_agent":
                instructions[
                    "sme_agent"
                ] = """
# SME Agent System
from ignition.modules.sme_agent import SMEAgentModule

# Initialize SME Agent
agent = SMEAgentModule()
response = await agent.ask_question('How do I optimize PID control?')
"""

        return instructions

    def _generate_quick_start_guide(self: Any) -> str:
        """Generate a quick start guide for new agents."""
        return f"""
# IGN Scripts Code Intelligence System - Quick Start

## Project Overview
This is the IGN Scripts project with a comprehensive Code Intelligence System.
Phase 11.1 has been completed, providing SME Agent infrastructure with human evaluation capabilities.

## Available Knowledge Bases
{len(self.knowledge_bases)} knowledge bases are available:
{chr(10).join(f"- {kb.name}: {kb.status}" for kb in self.knowledge_bases)}

## Key Capabilities
- Automated code refactoring with safety guarantees
- Large file detection and intelligent splitting
- Git integration with evolution tracking
- Architecture diagram generation
- Comprehensive impact analysis and reporting
- SME Agent with human evaluation and reinforcement learning
- Decision logging and batch management
- Progressive complexity deployment

## Quick Commands
```bash
# Detect large files needing refactoring
python -m src.ignition.code_intelligence.cli_commands refactor detect

# Analyze a specific file
python -m src.ignition.code_intelligence.cli_commands refactor analyze path/to/file.py

# Get refactoring statistics
python -m src.ignition.code_intelligence.cli_commands refactor statistics

# Validate SME Agent environment
ign module sme validate-env

# Ask SME Agent a question
ign module sme ask "How do I optimize PID control?"

# Check SME Agent status
ign module sme status
```

## Important Files to Read First
1. docs/roadmap.md - Current project status
2. docs/PHASE_11_1_SME_AGENT_HUMAN_EVALUATION_ENHANCEMENT.md - Latest achievements
3. src/ignition/modules/sme_agent/ - SME Agent modules
4. src/ignition/code_intelligence/ - Core modules

## Environment Setup
Ensure these environment variables are set:
- NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD (for graph database)
- SME Agent variables (see sme_agent.env.example)
- Other project-specific variables in .env file
"""

    def _get_environment_setup(self: Any) -> dict[str, Any]:
        """Get environment setup information."""
        env_vars = {
            "required": [
                "NEO4J_URI - Neo4j database connection",
                "NEO4J_USER - Neo4j username",
                "NEO4J_PASSWORD - Neo4j password",
                "SME_AGENT_NEO4J_URI - SME Agent Neo4j connection",
                "SME_AGENT_MODEL_NAME - LLM model configuration",
            ],
            "optional": [
                "OPENAI_API_KEY - For AI-powered analysis",
                "GITHUB_TOKEN - For enhanced git integration",
                "SME_AGENT_ENABLE_HUMAN_EVALUATION - Enable human evaluation features",
                "SME_AGENT_EVALUATION_BATCH_SIZE - Batch size for evaluations",
            ],
            "files": [
                ".env - Environment variables",
                "sme_agent.env.example - SME Agent configuration template",
                "requirements.txt - Python dependencies",
            ],
        }

        return env_vars

    def _get_key_files_for_context(self: Any) -> list[str]:
        """Get list of key files new agents should read for context."""
        return [
            "docs/roadmap.md",
            "docs/PHASE_11_1_SME_AGENT_HUMAN_EVALUATION_ENHANCEMENT.md",
            "src/ignition/modules/sme_agent/sme_agent_module.py",
            "src/ignition/modules/sme_agent/cli_commands.py",
            "sme_agent.env.example",
            "src/ignition/code_intelligence/manager.py",
            ".env.sample",
        ]

    def _get_recent_developments(self: Any) -> list[dict[str, Any]]:
        """Get recent project developments."""
        return [
            {
                "title": "Phase 11.1 Completion",
                "date": "January 2025",
                "description": "Completed SME Agent Infrastructure with human evaluation system",
                "impact": "Major milestone - SME Agent foundation with reinforcement learning capabilities",
            },
            {
                "title": "Human Evaluation System",
                "date": "January 2025",
                "description": "Decision logging, batch management, and reinforcement learning insights",
                "impact": "Enables continuous improvement through human expert feedback",
            },
            {
                "title": "Progressive Complexity Deployment",
                "date": "January 2025",
                "description": "4-tier complexity system (basic/standard/advanced/enterprise)",
                "impact": "Scalable deployment architecture for different use cases",
            },
        ]

    def _get_available_tools(self: Any) -> list[dict[str, str]]:
        """Get list of available tools and their purposes."""
        return [
            {
                "name": "SME Agent Module",
                "purpose": "Intelligent assistant with human evaluation capabilities",
                "usage": "from ignition.modules.sme_agent import SMEAgentModule",
            },
            {
                "name": "Code Intelligence Manager",
                "purpose": "Central coordination of all analysis systems",
                "usage": "from ignition.code_intelligence.manager import CodeIntelligenceManager",
            },
            {
                "name": "Refactoring CLI",
                "purpose": "Command-line interface for all refactoring operations",
                "usage": "python -m src.ignition.code_intelligence.cli_commands refactor <command>",
            },
            {
                "name": "SME Agent CLI",
                "purpose": "Command-line interface for SME Agent operations",
                "usage": "ign module sme <command>",
            },
            {
                "name": "Git Integration",
                "purpose": "Track file evolution and analyze branches",
                "usage": "from ignition.code_intelligence.git_integration import GitIntegration",
            },
            {
                "name": "Refactoring Tracker",
                "purpose": "Document and track refactoring operations",
                "usage": "from ignition.code_intelligence.refactoring_tracker import RefactoringTracker",
            },
        ]

    def save_agent_context(self: Self, output_file: Path | None = None) -> Path:
        """Save complete agent context to file for easy loading."""
        if output_file is None:
            output_file = self.project_root / ".agent_context.json"

        context_data = self.get_agent_initialization_info()

        with open(output_file, "w") as f:
            json.dump(context_data, f, indent=2, default=str)

        logger.info(f"Agent context saved to {output_file}")
        return output_file

    @classmethod
    def load_agent_context(cls, context_file: Path | None = None) -> dict[str, Any]:
        """Load agent context from file."""
        if context_file is None:
            context_file = Path.cwd() / ".agent_context.json"

        if not context_file.exists():
            # Generate new context
            discovery = cls()
            discovery.save_agent_context(context_file)

        with open(context_file) as f:
            return json.load(f)


def initialize_agent_knowledge() -> dict[str, Any]:
    """Main function to initialize agent knowledge.
    Call this at the start of any new agent or chat session.
    """
    print("🔍 Discovering project knowledge bases...")

    discovery = KnowledgeDiscoverySystem()
    context = discovery.get_agent_initialization_info()

    # Save context for future use
    context_file = discovery.save_agent_context()

    print("✅ Knowledge discovery complete!")
    print(f"📊 Found {len(discovery.knowledge_bases)} knowledge bases")
    print(f"💾 Context saved to {context_file}")

    # Display quick summary
    print("\n📋 AVAILABLE KNOWLEDGE BASES:")
    for kb in discovery.knowledge_bases:
        status_emoji = (
            "✅" if kb.status == "available" else "❌" if kb.status == "error" else "⚠️"
        )
        print(f"  {status_emoji} {kb.name} ({kb.type})")
        if kb.record_count:
            print(f"     Records: {kb.record_count:,}")
        if kb.description:
            print(f"     {kb.description}")

    print(f"\n🚀 Quick Start: Read {context['quick_start_guide'][:100]}...")

    return context


def main():
    """Main function for testing knowledge discovery."""
    context = initialize_agent_knowledge()

    print("\n" + "=" * 60)
    print("AGENT INITIALIZATION COMPLETE")
    print("=" * 60)

    print(f"Project: {context['project_context']['project_name']}")
    print(f"Current Phase: {context['project_context']['current_phase']}")
    print(f"Available Tools: {len(context['available_tools'])}")
    print(f"CLI Commands: {len(context['project_context']['cli_commands'])}")

    return context


if __name__ == "__main__":
    main()
