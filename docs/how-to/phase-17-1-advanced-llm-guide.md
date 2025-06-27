# Phase 17.1: Advanced LLM Integration - How-To Guide

## Overview

This guide provides step-by-step instructions for using Phase 17.1's Advanced LLM Integration capabilities, including multi-modal understanding, context-aware processing, and Ignition version compatibility features.

## Table of Contents

1. [Prerequisites & Setup](#prerequisites--setup)
2. [Environment Configuration](#environment-configuration)
3. [Basic Usage](#basic-usage)
4. [Multi-Modal Processing](#multi-modal-processing)
5. [Context-Aware Features](#context-aware-features)
6. [Ignition Version Compatibility](#ignition-version-compatibility)
7. [Progressive Complexity Levels](#progressive-complexity-levels)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Advanced Usage](#advanced-usage)

## Prerequisites & Setup

### System Requirements

- **Python**: 3.12+ (required for modern union syntax)
- **Memory**: 8GB+ RAM recommended
- **Storage**: 2GB+ free space for models and cache
- **Network**: Internet connection for model downloads

### Installation Verification

```bash
# Verify Python version
python --version  # Should show 3.12+

# Check IGN Scripts installation
ign --version

# Verify Phase 17.1 availability
ign module sme validate-env
```

## Environment Configuration

### Required Environment Variables

Create or update your `.env` file with the following variables:

```bash
# Phase 17.1 Core Configuration
PHASE_17_LLM_ENABLED=true
PHASE_17_MULTIMODAL_ENABLED=true
PHASE_17_CONTEXT_AWARE_ENABLED=true

# LLM Configuration
SME_AGENT_MODEL=llama3.1-8b
SME_AGENT_QUANTIZATION=4bit
SME_AGENT_GPU_ENABLED=true

# Neo4j Configuration (for context-aware features)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Multi-Modal Configuration
VISION_MODEL_ENABLED=true
SCREENSHOT_ANALYSIS_ENABLED=true
DIAGRAM_INTERPRETATION_ENABLED=true

# Context Configuration
CONVERSATION_MEMORY_ENABLED=true
USER_PREFERENCE_LEARNING=true
PROJECT_CONTEXT_LOADING=true
```

### Environment Validation

```bash
# Validate complete environment setup
ign module sme phase17 validate-env

# Check specific components
ign module sme phase17 status --component=multimodal
ign module sme phase17 status --component=context-aware
ign module sme phase17 status --component=version-detector
```

## Basic Usage

### 1. Initialize Phase 17.1 System

```bash
# Initialize with basic complexity
ign module sme phase17 initialize --complexity=basic

# Initialize with full features (enterprise)
ign module sme phase17 initialize --complexity=enterprise
```

### 2. Basic Question Processing

```bash
# Ask a simple question
ign module sme phase17 ask "How do I create a tag in Ignition?"

# Ask with context file
ign module sme phase17 ask "Optimize this script" --context-file=my_script.py

# Ask with specific Ignition version
ign module sme phase17 ask "What Perspective components are available?" --ignition-version=8.1.25
```

### 3. Check System Status

```bash
# Overall system status
ign module sme phase17 status

# Detailed component status
ign module sme phase17 status --detailed

# Performance metrics
ign module sme phase17 status --metrics
```

## Multi-Modal Processing

### Screenshot Analysis

The multi-modal processor can analyze Ignition Designer screenshots and provide insights.

#### Step 1: Capture Screenshot

```bash
# Take a screenshot of your Ignition Designer
# Save as PNG or JPG format
```

#### Step 2: Analyze Screenshot

```bash
# Analyze a Designer screenshot
ign module sme phase17 ask "What can be improved in this design?" --screenshot=designer_screen.png

# Analyze with specific focus
ign module sme phase17 ask "Check for performance issues" --screenshot=perspective_view.png --focus=performance

# Analyze multiple screenshots
ign module sme phase17 ask "Compare these two designs" --screenshot=design1.png,design2.png
```

### Tag Browser Analysis

```bash
# Analyze tag structure from screenshot
ign module sme phase17 ask "Review my tag organization" --screenshot=tag_browser.png --analysis-type=structure

# Get naming convention suggestions
ign module sme phase17 ask "Suggest better tag names" --screenshot=tag_browser.png --analysis-type=naming
```

### Diagram Interpretation

```bash
# Analyze P&ID diagrams
ign module sme phase17 ask "Explain this process flow" --diagram=pid_diagram.png

# Analyze electrical schematics
ign module sme phase17 ask "Check this wiring diagram" --diagram=electrical_schematic.png --focus=safety
```

## Context-Aware Features

### Project Context Loading

#### Step 1: Set Project Context

```bash
# Load project context from directory
ign module sme phase17 set-context --project-path=/path/to/ignition/project

# Load from exported project file
ign module sme phase17 set-context --project-file=MyProject.proj
```

#### Step 2: Use Context-Aware Queries

```bash
# Ask questions with project context
ign module sme phase17 ask "How can I optimize the HMI performance?" --use-context=true

# Get project-specific recommendations
ign module sme phase17 ask "What security improvements are needed?" --use-context=true --focus=security
```

### Conversation Memory

```bash
# Enable conversation memory
ign module sme phase17 configure --conversation-memory=true

# Ask follow-up questions (memory will be used automatically)
ign module sme phase17 ask "How do I create a UDT?"
ign module sme phase17 ask "Can you show me an example?"  # Remembers previous question

# View conversation history
ign module sme phase17 history --sessions=5
```

### User Preference Learning

```bash
# Set user preferences
ign module sme phase17 configure --user-role=developer --experience-level=intermediate

# The system will adapt responses based on your preferences
ign module sme phase17 ask "Explain tag events"  # Will provide intermediate-level explanation
```

## Ignition Version Compatibility

### Version Detection

```bash
# Detect Ignition version automatically
ign module sme phase17 version-info --auto-detect

# Set specific version
ign module sme phase17 version-info --set-version=8.1.25

# Check version compatibility
ign module sme phase17 version-info --check-compatibility
```

### Version-Specific Features

```bash
# Get features available in your version
ign module sme phase17 ask "What's new in Ignition 8.1.25?"

# Check if feature is available
ign module sme phase17 ask "Can I use Perspective Workstation?" --ignition-version=8.1.20

# Get version-specific advice
ign module sme phase17 ask "Best practices for Vision to Perspective migration" --source-version=7.9 --target-version=8.1
```

## Progressive Complexity Levels

### Basic Level

```bash
# Initialize basic level (minimal features)
ign module sme phase17 initialize --complexity=basic

# Basic features available:
# - Simple question answering
# - Basic context loading
# - Standard Ignition knowledge
```

### Standard Level

```bash
# Initialize standard level (common features)
ign module sme phase17 initialize --complexity=standard

# Standard features include:
# - Multi-modal processing
# - Project context awareness
# - Version compatibility
# - Conversation memory
```

### Advanced Level

```bash
# Initialize advanced level (comprehensive features)
ign module sme phase17 initialize --complexity=advanced

# Advanced features include:
# - All standard features
# - User preference learning
# - Advanced analytics
# - Performance optimization
```

### Enterprise Level

```bash
# Initialize enterprise level (all features)
ign module sme phase17 initialize --complexity=enterprise

# Enterprise features include:
# - All advanced features
# - Multi-session context
# - Advanced security features
# - Custom model fine-tuning
```

## Troubleshooting

### Common Issues

#### Issue 1: Environment Validation Fails

```bash
# Check detailed validation
ign module sme phase17 validate-env --verbose

# Common solutions:
# 1. Update Python to 3.12+
# 2. Install missing dependencies
# 3. Configure environment variables
```

#### Issue 2: Multi-Modal Processing Not Working

```bash
# Check vision model status
ign module sme phase17 status --component=vision

# Solutions:
# 1. Enable vision model: VISION_MODEL_ENABLED=true
# 2. Install vision dependencies
# 3. Check GPU availability
```

#### Issue 3: Context Loading Fails

```bash
# Check Neo4j connection
ign module sme phase17 status --component=neo4j

# Solutions:
# 1. Verify Neo4j is running
# 2. Check connection credentials
# 3. Validate database permissions
```

### Diagnostic Commands

```bash
# Run comprehensive diagnostics
ign module sme phase17 test --comprehensive

# Test specific components
ign module sme phase17 test --component=multimodal
ign module sme phase17 test --component=context-aware
ign module sme phase17 test --component=version-detector

# Generate diagnostic report
ign module sme phase17 test --generate-report
```

## Best Practices

### 1. Environment Setup

- **Always validate environment** before first use
- **Use virtual environments** to avoid conflicts
- **Keep dependencies updated** for best performance
- **Configure GPU acceleration** if available

### 2. Multi-Modal Usage

- **Use high-quality screenshots** (PNG preferred)
- **Crop to relevant areas** for better analysis
- **Provide context** in your questions
- **Use specific analysis types** for targeted results

### 3. Context Management

- **Load project context** before asking project-specific questions
- **Update context** when project changes
- **Use conversation memory** for follow-up questions
- **Clear context** when switching projects

### 4. Performance Optimization

- **Use appropriate complexity level** for your needs
- **Enable GPU acceleration** for faster processing
- **Cache frequently used contexts**
- **Monitor system resources**

## Advanced Usage

### Custom Model Configuration

```bash
# Configure custom LLM model
ign module sme phase17 configure --model=custom-model --model-path=/path/to/model

# Fine-tune model for specific domain
ign module sme phase17 fine-tune --domain=distillery --training-data=/path/to/data
```

### Batch Processing

```bash
# Process multiple questions from file
ign module sme phase17 batch-process --input-file=questions.txt --output-file=answers.txt

# Analyze multiple screenshots
ign module sme phase17 batch-analyze --screenshot-dir=/path/to/screenshots --output-dir=/path/to/results
```

### Integration with External Tools

```bash
# Export context for external tools
ign module sme phase17 export-context --format=json --output=context.json

# Import external knowledge
ign module sme phase17 import-knowledge --source=external_docs.json --format=json
```

### API Usage

```python
# Python API example
from ignition.modules.sme_agent.phase_17_1_advanced_llm_integration import AdvancedLLMIntegration

# Initialize system
llm = AdvancedLLMIntegration(complexity_level="enterprise")
await llm.initialize()

# Process question with context
response = await llm.process_request(
    question="How do I optimize this HMI?",
    context_file="hmi_design.py",
    screenshot="hmi_screenshot.png"
)

print(response.answer)
```

## Examples

### Example 1: HMI Design Review

```bash
# Step 1: Take screenshot of HMI
# Step 2: Analyze design
ign module sme phase17 ask "Review this HMI design for usability" --screenshot=hmi_design.png

# Step 3: Get specific recommendations
ign module sme phase17 ask "What colors should I use for better visibility?" --screenshot=hmi_design.png --focus=accessibility
```

### Example 2: Script Optimization

```bash
# Step 1: Load project context
ign module sme phase17 set-context --project-path=/my/ignition/project

# Step 2: Analyze script
ign module sme phase17 ask "Optimize this gateway script" --context-file=gateway_script.py

# Step 3: Get performance insights
ign module sme phase17 ask "What are the performance bottlenecks?" --context-file=gateway_script.py --focus=performance
```

### Example 3: Version Migration

```bash
# Step 1: Set source and target versions
ign module sme phase17 version-info --source-version=7.9 --target-version=8.1

# Step 2: Get migration advice
ign module sme phase17 ask "How do I migrate this Vision window to Perspective?" --context-file=vision_window.py

# Step 3: Check compatibility
ign module sme phase17 ask "What features need to be replaced?" --context-file=vision_window.py --migration-check=true
```

## Support and Resources

### Documentation Links

- **Implementation Guide**: [docs/PHASE_17_1_ADVANCED_LLM_INTEGRATION.md](../PHASE_17_1_ADVANCED_LLM_INTEGRATION.md)
- **Test Documentation**: [tests/phase_17_1_comprehensive_test_report.md](../../tests/phase_17_1_comprehensive_test_report.md)
- **API Reference**: [docs/api/phase-17-1-api.md](../api/phase-17-1-api.md)

### Getting Help

```bash
# Get help for specific command
ign module sme phase17 ask --help

# View available commands
ign module sme phase17 --help

# Get system information
ign module sme phase17 info
```

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and examples
- **Community Forum**: Ask questions and share experiences

---

*This guide covers the essential usage patterns for Phase 17.1 Advanced LLM Integration. For more advanced use cases and detailed API documentation, refer to the complete implementation guide.*
