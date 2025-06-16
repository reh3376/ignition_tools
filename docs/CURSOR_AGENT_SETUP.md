# Cursor Agent Setup for IGN Scripts Project

## Overview
This document provides the exact configuration needed for Cursor's AI agents to automatically connect to the IGN Scripts project's persistent memory systems.

## Cursor Settings Configuration

### Settings → Indexing & Docs

Add the following to your Cursor settings in the **Indexing & Docs** section:

#### **Project Context Instructions:**
```
This is the IGN Scripts project with a comprehensive Code Intelligence System.
Phase 8.1 has been completed, providing automated refactoring capabilities.

IMPORTANT: All new agents/chat sessions MUST initialize the knowledge discovery system:

```python
# Initialize at start of every new chat/agent session
from ignition.code_intelligence import initialize_agent_knowledge
context = initialize_agent_knowledge()
print(f"✅ Connected to {len(context['knowledge_base_status'])} knowledge bases")
```

Available knowledge bases:
- Neo4j Graph Database (3,691+ nodes) for code structure analysis
- Git History Integration (65+ commits) for evolution tracking
- Refactoring Tracking System for operation documentation
- Vector Embeddings for semantic code search

Key capabilities: automated refactoring, large file detection, git integration,
architecture diagram generation, comprehensive impact analysis.

CLI commands available with 'refactor' prefix (12 total commands).
Current phase: 8.1 (Completed). Project root: /Users/reh3376/repos/IGN_scripts
```

#### **Additional Documentation Paths:**
```
docs/roadmap.md
docs/PHASE_8_1_COMPLETION_SUMMARY.md
docs/AGENT_KNOWLEDGE_SYSTEM.md
src/ignition/code_intelligence/
examples/new_agent_initialization.py
.agent_context.json
```

#### **Ignore Patterns (if needed):**
```
.refactoring_tracking/
.analysis_cache/
.vector_cache/
.agent_context.json
```

## Alternative Configuration Locations

### **1. Settings → AI → System Instructions**
If available, add this as a system-level instruction:
```
For the IGN Scripts project: Always run `from ignition.code_intelligence import initialize_agent_knowledge; context = initialize_agent_knowledge()` at the start of new sessions to connect to project knowledge bases.
```

### **2. Settings → Workspace → AI Instructions**
Project-specific AI instructions:
```
IGN Scripts Code Intelligence System (Phase 8.1 Complete)
- Initialize knowledge discovery: initialize_agent_knowledge()
- Available: Neo4j DB, Git integration, refactoring tools
- CLI: 12 'refactor' commands available
- See docs/AGENT_KNOWLEDGE_SYSTEM.md for details
```

### **3. .cursorrules File (Project Root)**
Create a `.cursorrules` file in the project root:

```
# IGN Scripts Project - Cursor AI Rules

## Initialization Required
Every new agent/chat session must run this initialization:

```python
from ignition.code_intelligence import initialize_agent_knowledge
context = initialize_agent_knowledge()
```

## Project Context
- Name: IGN Scripts - Code Intelligence System
- Phase: 8.1 (Completed)
- Knowledge Bases: Neo4j (3,691+ nodes), Git (65+ commits)
- CLI: 12 refactor commands available
- Key Files: docs/roadmap.md, docs/PHASE_8_1_COMPLETION_SUMMARY.md

## Available Tools
- Automated refactoring with safety guarantees
- Large file detection and intelligent splitting
- Git integration with evolution tracking
- Architecture diagram generation
- Comprehensive impact analysis and reporting

## Quick Commands
- `refactor detect` - Scan for oversized files
- `refactor analyze <file>` - Detailed file analysis
- `refactor statistics` - Show refactoring stats
- See docs/AGENT_KNOWLEDGE_SYSTEM.md for full list

## Important
Always check .agent_context.json for latest project state.
Use knowledge discovery system for consistent project understanding.
```

## Recommended Implementation Steps

### **Step 1: Primary Setup (Indexing & Docs)**
1. Open Cursor Settings
2. Navigate to **Indexing & Docs**
3. Add the project context instructions above
4. Include the documentation paths
5. Save settings

### **Step 2: Create .cursorrules File**
```bash
# Create the .cursorrules file in project root
cat > .cursorrules << 'EOF'
# IGN Scripts Project - Cursor AI Rules
[Content from above]
EOF
```

### **Step 3: Test with New Chat**
1. Start a new chat session in Cursor
2. Verify the agent mentions the knowledge discovery system
3. Test the initialization command
4. Confirm connection to knowledge bases

### **Step 4: Update .gitignore (Optional)**
```bash
# Add to .gitignore if you don't want to track cursor settings
echo ".cursorrules" >> .gitignore  # Only if you want it local
```

## Verification Commands

Test that new agents have proper access:

```python
# Test 1: Basic initialization
from ignition.code_intelligence import initialize_agent_knowledge
context = initialize_agent_knowledge()

# Test 2: Verify knowledge bases
print(f"Knowledge bases: {len(context['knowledge_base_status'])}")
for kb in context['knowledge_base_status']:
    print(f"- {kb['name']}: {kb['status']}")

# Test 3: Check project context
project = context['project_context']
print(f"Project: {project['project_name']}")
print(f"Phase: {project['current_phase']}")
print(f"CLI Commands: {len(project['cli_commands'])}")

# Test 4: Verify Neo4j connection
from ignition.code_intelligence.manager import CodeIntelligenceManager
try:
    manager = CodeIntelligenceManager()
    if manager.client.is_connected():
        print("✅ Neo4j connected")
    else:
        print("⚠️ Neo4j not connected")
except Exception as e:
    print(f"❌ Neo4j error: {e}")
```

## Benefits of This Setup

### **For New Agents:**
- ✅ **Automatic Context** - Immediate project understanding
- ✅ **Knowledge Base Access** - Connected to 3,691+ nodes of data
- ✅ **Consistent Experience** - Same setup across all sessions
- ✅ **Tool Awareness** - Knows about 12 CLI commands

### **For Development Team:**
- ✅ **Reduced Onboarding** - New team members get instant context
- ✅ **Consistent AI Behavior** - All agents have same project knowledge
- ✅ **Improved Productivity** - Less time explaining project structure
- ✅ **Knowledge Preservation** - Project context automatically maintained

## Troubleshooting

### **Agent Not Initializing:**
- Check if `.cursorrules` file exists and is readable
- Verify Cursor settings include the initialization instructions
- Ensure the project path is correct in settings

### **Knowledge Bases Not Found:**
- Run `python examples/new_agent_initialization.py` to test
- Check environment variables (NEO4J_URI, etc.)
- Verify `.agent_context.json` exists and is current

### **CLI Commands Not Working:**
- Test: `python -m src.ignition.code_intelligence.cli_commands refactor --help`
- Check Python path includes `src/` directory
- Verify all dependencies are installed

## Updates and Maintenance

### **When to Update:**
- After completing new project phases
- When adding new knowledge bases
- After major refactoring operations
- When CLI commands change

### **How to Update:**
1. Run knowledge discovery to refresh context
2. Update Cursor settings with new information
3. Regenerate `.cursorrules` if needed
4. Test with new chat session

---

## Quick Setup Commands

```bash
# 1. Create .cursorrules file
cp docs/CURSOR_AGENT_SETUP.md .cursorrules

# 2. Test knowledge discovery
python -c "from ignition.code_intelligence import initialize_agent_knowledge; initialize_agent_knowledge()"

# 3. Verify in new Cursor chat
# Start new chat and check if agent mentions knowledge discovery system
```

This setup ensures every new Cursor agent automatically has access to the project's comprehensive knowledge base! 🚀
