# Agent Knowledge Discovery System

## Overview

The **Agent Knowledge Discovery System** ensures that every new agent or chat session automatically discovers and connects to all available long-term persistent memory systems for this codebase. This eliminates the need for manual setup and ensures consistent access to project knowledge.

## 🎯 Purpose

When a new agent or chat session is created, it needs to:
1. **Discover** what knowledge bases are available
2. **Connect** to persistent memory systems (Neo4j, file caches, git history)
3. **Load** project context and recent developments
4. **Access** CLI tools and integration points
5. **Understand** the current project state and capabilities

## 🏗️ System Architecture

```mermaid
graph TD
    A[New Agent/Chat] --> B[Knowledge Discovery System]
    B --> C[Scan Project Structure]
    B --> D[Test Knowledge Base Connections]
    B --> E[Build Project Context]

    C --> F[Find Key Files]
    C --> G[Check Directories]

    D --> H[Neo4j Graph DB]
    D --> I[Vector Embeddings]
    D --> J[File Caches]
    D --> K[Git History]
    D --> L[Refactoring Tracking]

    E --> M[Generate Agent Context]
    M --> N[Save Context File]
    M --> O[Provide Connection Instructions]
```

## 🚀 Quick Start for New Agents

### Automatic Initialization

```python
# Add this to the start of any new agent or chat session
from src.ignition.code_intelligence.knowledge_discovery import initialize_agent_knowledge

# This will automatically discover and connect to all available knowledge bases
context = initialize_agent_knowledge()

print(f"✅ Connected to {len(context['knowledge_base_status'])} knowledge bases")
print(f"🎯 Project: {context['project_context']['project_name']}")
print(f"📊 Current Phase: {context['project_context']['current_phase']}")
```

### Manual Discovery

```python
from src.ignition.code_intelligence.knowledge_discovery import KnowledgeDiscoverySystem
from pathlib import Path

# Create discovery system
discovery = KnowledgeDiscoverySystem(Path.cwd())

# Get complete initialization info
init_info = discovery.get_agent_initialization_info()

# Save context for future use
context_file = discovery.save_agent_context()
```

## 📊 Available Knowledge Bases

The system automatically discovers and connects to:

### 1. **Neo4j Graph Database**
- **Type:** `neo4j`
- **Purpose:** Code structure analysis, dependency tracking, refactoring history
- **Connection:** Automatic via environment variables
- **Capabilities:**
  - Code structure analysis
  - Dependency tracking
  - Refactoring history
  - File evolution tracking
  - Complex queries and analytics

### 2. **Vector Embeddings Cache**
- **Type:** `vector_db`
- **Purpose:** Semantic code search and similarity analysis
- **Location:** `.vector_cache/` directory
- **Capabilities:**
  - Semantic code search
  - Similar code detection
  - Context-aware analysis
  - Code similarity metrics

### 3. **Code Analysis Cache**
- **Type:** `file_cache`
- **Purpose:** Cached analysis results for fast re-analysis
- **Location:** `.analysis_cache/` directory
- **Capabilities:**
  - Fast re-analysis
  - Historical comparisons

### 4. **Git History Integration**
- **Type:** `git_history`
- **Purpose:** File evolution and branch analysis
- **Connection:** Automatic via `.git/` directory
- **Capabilities:**
  - File evolution tracking
  - Author analysis
  - Change frequency analysis
  - Branch comparison
  - Merge conflict prediction

### 5. **Refactoring Tracking System**
- **Type:** `refactoring_tracking`
- **Purpose:** Document and track refactoring operations
- **Location:** `.refactoring_tracking/` directory
- **Capabilities:**
  - Operation tracking
  - Architecture diagrams
  - Impact reports
  - TODO management
  - Statistics dashboard

### 6. **SME Agent System**
- **Type:** `sme_agent`
- **Purpose:** Subject Matter Expert Agent with human evaluation and reinforcement learning
- **Location:** `src/ignition/modules/sme_agent/`
- **Capabilities:**
  - Question processing with context
  - File analysis and recommendations
  - Human evaluation batch management
  - Decision logging and tracking
  - Reinforcement learning insights
  - Progressive complexity deployment

### 7. **LLM Fine-tuning Infrastructure**
- **Type:** `llm_fine_tuning`
- **Purpose:** 8B parameter LLM fine-tuning with Neo4j knowledge graph integration
- **Location:** `src/ignition/modules/llm_infrastructure/`
- **Capabilities:**
  - Extract training data from Neo4j knowledge graph (11,608+ nodes)
  - Quality-controlled data pipeline with configurable thresholds
  - Parameter-efficient fine-tuning (LoRA/QLoRA)
  - Data augmentation with instruction variations
  - Auto-detecting GPU support (Apple Silicon MPS, CUDA, CPU)
  - Comprehensive CLI interface (extract-data, train, status)
  - Resource management with async context managers
  - Training data format: Instruction-tuning with Input/Output structure

## 🔧 Connection Instructions

### Neo4j Graph Database
```python
from ignition.code_intelligence.manager import CodeIntelligenceManager

manager = CodeIntelligenceManager()
if manager.client.is_connected():
    # Access graph database
    result = manager.client.execute_query("MATCH (n) RETURN count(n)")
    print(f"Connected to Neo4j with {result} nodes")
```

### Git Integration
```python
from ignition.code_intelligence.git_integration import GitIntegration
from pathlib import Path

git_integration = GitIntegration(Path.cwd())
evolution = git_integration.track_file_evolution("path/to/file.py")
```

### Refactoring Tracking
```python
from ignition.code_intelligence.refactoring_tracker import RefactoringTracker
from pathlib import Path

tracker = RefactoringTracker(Path.cwd())
stats = tracker.get_refactoring_statistics()
```

### SME Agent System
```python
from ignition.modules.sme_agent import SMEAgentModule

# Initialize SME Agent
agent = SMEAgentModule()
response = await agent.ask_question('How do I optimize PID control?')
```

### LLM Fine-tuning Infrastructure
```python
from src.ignition.modules.llm_infrastructure.fine_tuning_manager import FineTuningManager

# Initialize fine-tuning manager
manager = FineTuningManager()

# Extract training data from Neo4j
async with manager.create_fine_tuning_context() as context:
    dataset = await manager.extract_training_data(
        dataset_name="ignition_knowledge",
        extraction_types=["Method", "Class", "Function"],
        max_records=1000,
        quality_threshold=0.8
    )

# CLI Usage
# python -m src.main fine-tuning extract-data --dataset-name test --max-records 100
# python -m src.main fine-tuning status --show-datasets
# python -m src.main fine-tuning train --dataset-name test --lora-rank 16
```

## 📋 Project Context Information

The system provides comprehensive project context including:

### Current Project State
- **Project Name:** IGN Scripts - Code Intelligence System
- **Current Phase:** 13.2 (Completed) - Model Fine-tuning & Specialization
- **Completed Phases:** 1.0 through 13.2

### Key Capabilities
- Automated Code Refactoring
- Large File Detection & Analysis
- Code Splitting with AST Analysis
- Git Integration & Evolution Tracking
- Architecture Diagram Generation
- Neo4j Graph Database Integration (11,608+ nodes)
- Comprehensive CLI Interface
- Refactoring Impact Analysis
- Enterprise Integration & Deployment
- Multi-Cloud Deployment Capabilities
- Advanced Analytics Platform
- Industrial Data Integration
- SME Agent with Human Evaluation
- **LLM Fine-tuning Infrastructure** (Phase 13.2)
- **Parameter-Efficient Fine-tuning** (LoRA/QLoRA)
- **Knowledge Graph Training Data Extraction**
- **Quality-Controlled Data Pipeline**
- **Auto-Detecting GPU Support** (Apple Silicon MPS, CUDA, CPU)

### Available CLI Commands
```bash
# Core refactoring commands
refactor detect                 # Scan for oversized files
refactor analyze               # Detailed file analysis
refactor split                 # Split individual files
refactor batch-split           # Process multiple files
refactor workflow              # Execute comprehensive workflows
refactor rollback              # Restore previous state

# Advanced tracking commands
refactor track-evolution       # Monitor file evolution
refactor analyze-branch        # Compare branches
refactor tracking-report       # Generate impact reports
refactor generate-diagram      # Create architecture diagrams
refactor complexity-trends     # Show complexity trends
refactor statistics           # Display comprehensive statistics

# SME Agent commands
ign module sme validate-env      # Validate SME Agent environment
ign module sme status           # Check SME Agent component status
ign module sme initialize       # Initialize SME Agent components
ign module sme ask             # Ask SME Agent questions
ign module sme analyze         # Analyze files with SME Agent
ign module sme test-all        # Test all SME Agent complexity levels
ign module sme list-batches    # List evaluation batches
ign module sme export-batch    # Export batch for human review
ign module sme import-evaluation # Import human evaluations
ign module sme rl-summary      # Show reinforcement learning insights
ign module sme create-test-batch # Create test evaluation batches

# LLM Fine-tuning Commands (Phase 13.2)
ign fine-tuning extract-data   # Extract training data from Neo4j knowledge graph
ign fine-tuning train          # Execute fine-tuning training process
ign fine-tuning status         # Show system status, datasets, and configuration
```

### Recent Developments
- **Phase 13.2 Completion** (June 2025) - Model Fine-tuning & Specialization
- **LLM Fine-tuning Infrastructure** - Complete 8B parameter LLM fine-tuning system
- **Neo4j Knowledge Graph Integration** - Extract training data from 11,608+ nodes
- **Parameter-Efficient Fine-tuning** - LoRA/QLoRA with auto-detecting GPU support
- **Quality-Controlled Data Pipeline** - Configurable thresholds and data augmentation
- **Phase 11.1 Completion** (January 2025) - SME Agent Infrastructure & Human Evaluation Enhancement
- **SME Agent System** - Complete infrastructure with human evaluation and reinforcement learning
- **Progressive Complexity** - Support for basic/standard/advanced/enterprise deployment levels
- **Human-in-the-Loop** - Comprehensive evaluation system for continuous improvement
- **Phase 10.0 Completion** (December 2024) - Enterprise Integration & Deployment
- **Phase 8.1 Completion** (January 2025) - Completed Code Intelligence System
- **Git Integration Added** - File evolution tracking and branch analysis
- **Documentation System** - Architecture diagrams and TODO generation

## 🔍 Environment Setup

### Required Environment Variables
```bash
# Neo4j Database Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Optional enhancements
OPENAI_API_KEY=your_openai_key      # For AI-powered analysis
GITHUB_TOKEN=your_github_token      # For enhanced git integration
```

### Key Files to Read
1. `docs/roadmap.md` - Current project status and roadmap
2. `docs/PHASE_8_1_COMPLETION_SUMMARY.md` - Latest achievements
3. `src/ignition/code_intelligence/` - Core intelligence modules
4. `.env.sample` - Environment variable examples

## 💾 Context Persistence

### Automatic Context Saving
The system automatically saves agent context to `.agent_context.json`:

```json
{
  "project_context": {
    "project_name": "IGN Scripts - Code Intelligence System",
    "current_phase": "13.2 (Completed) - Model Fine-tuning & Specialization",
    "key_capabilities": [...],
    "cli_commands": [...]
  },
  "knowledge_base_status": [...],
  "connection_instructions": {...},
  "quick_start_guide": "...",
  "available_tools": [...]
}
```

### Loading Existing Context
```python
from src.ignition.code_intelligence.knowledge_discovery import KnowledgeDiscoverySystem

# Load existing context
context = KnowledgeDiscoverySystem.load_agent_context()

# Or specify custom location
context = KnowledgeDiscoverySystem.load_agent_context(Path("custom_context.json"))
```

## 🎯 Integration with New Agents

### For AI Assistants/Agents
Add this initialization code at the start of any new session:

```python
# Initialize knowledge discovery
from src.ignition.code_intelligence.knowledge_discovery import initialize_agent_knowledge

try:
    context = initialize_agent_knowledge()

    # Now you have access to:
    # - context['project_context'] - Full project information
    # - context['knowledge_base_status'] - Available databases
    # - context['connection_instructions'] - How to connect
    # - context['available_tools'] - Tools and their usage

    print("🎉 Agent successfully connected to project knowledge bases!")

except Exception as e:
    print(f"⚠️ Knowledge discovery failed: {e}")
    print("Continuing with limited context...")
```

### For Chat Systems
Include this in your system prompt or initialization:

```
SYSTEM CONTEXT: This is the IGN Scripts project with a comprehensive Code Intelligence System.
Phase 13.2 has been completed, providing Model Fine-tuning & Specialization capabilities.

Available knowledge bases have been discovered and connected:
- Neo4j Graph Database for code structure analysis (11,608+ nodes)
- Git History Integration for evolution tracking
- Refactoring Tracking System for operation documentation
- Vector Embeddings for semantic code search
- LLM Fine-tuning Infrastructure for specialized model training

Key capabilities include automated refactoring, large file detection, git integration,
architecture diagram generation, comprehensive impact analysis, SME Agent with human evaluation,
and 8B parameter LLM fine-tuning with Neo4j knowledge graph integration.

Use the CLI commands starting with 'refactor', 'module sme', and 'fine-tuning' to access system functionality.
```

## 🔄 Automatic Updates

The knowledge discovery system automatically:
- **Refreshes** knowledge base connections on each initialization
- **Updates** project context with latest developments
- **Saves** updated context for future sessions
- **Validates** connection status for all knowledge bases

## 🛠️ Troubleshooting

### Common Issues

**Neo4j Connection Failed**
```bash
# Check environment variables
echo $NEO4J_URI $NEO4J_USER $NEO4J_PASSWORD

# Test connection manually
python -c "from neo4j import GraphDatabase; print('Neo4j driver available')"
```

**Git Integration Error**
```bash
# Ensure you're in a git repository
git status

# Check git command availability
which git
```

**Missing Knowledge Bases**
```python
# Run discovery to see what's available
from src.ignition.code_intelligence.knowledge_discovery import KnowledgeDiscoverySystem

discovery = KnowledgeDiscoverySystem()
for kb in discovery.knowledge_bases:
    print(f"{kb.name}: {kb.status} - {kb.description}")
```

## 📈 Benefits

### For New Agents
- **Instant Context** - Immediate access to project knowledge
- **Automatic Discovery** - No manual configuration required
- **Consistent Experience** - Same knowledge base access across sessions
- **Up-to-date Information** - Always current project state

### For Development Team
- **Reduced Onboarding** - New team members get instant context
- **Knowledge Preservation** - Project knowledge is automatically accessible
- **Consistent Documentation** - Standardized project information
- **Improved Productivity** - Less time spent explaining project context

---

## 🚀 Getting Started

To use this system with a new agent or chat session:

1. **Import the system:**
   ```python
   from src.ignition.code_intelligence.knowledge_discovery import initialize_agent_knowledge
   ```

2. **Initialize knowledge:**
   ```python
   context = initialize_agent_knowledge()
   ```

3. **Access project information:**
   ```python
   print(f"Project: {context['project_context']['project_name']}")
   print(f"Phase: {context['project_context']['current_phase']}")
   print(f"Available tools: {len(context['available_tools'])}")
   ```

4. **Connect to knowledge bases:**
   ```python
   # Follow connection instructions in context['connection_instructions']
   ```

The system will handle the rest automatically! 🎉
