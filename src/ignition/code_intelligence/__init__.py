"""
IGN Scripts Code Intelligence System

This module provides comprehensive code intelligence capabilities including:
- Automated refactoring with safety guarantees
- Large file detection and intelligent splitting  
- Git integration with evolution tracking
- Architecture diagram generation
- Comprehensive impact analysis and reporting

For new agents/chat sessions, use the knowledge discovery system:

    from ignition.code_intelligence import initialize_agent_knowledge
    context = initialize_agent_knowledge()

This will automatically discover and connect to all available knowledge bases.
"""

# Import key components for easy access
try:
    from .knowledge_discovery import initialize_agent_knowledge, KnowledgeDiscoverySystem
    from .manager import CodeIntelligenceManager
    from .cli_commands import refactor_commands
    
    # Make these available at package level
    __all__ = [
        'initialize_agent_knowledge',
        'KnowledgeDiscoverySystem', 
        'CodeIntelligenceManager',
        'refactor_commands'
    ]
    
    # Package metadata
    __version__ = "8.1.0"
    __author__ = "IGN Scripts Team"
    __description__ = "Comprehensive Code Intelligence System with automated refactoring"
    
    # Quick access function for new agents
    def quick_start():
        """
        Quick start function for new agents.
        Returns project context and connection information.
        """
        return initialize_agent_knowledge()
    
except ImportError as e:
    # Graceful fallback if dependencies aren't available
    print(f"⚠️ Some code intelligence features unavailable: {e}")
    
    def initialize_agent_knowledge():
        return {
            "error": "Knowledge discovery system not available",
            "message": "Some dependencies may be missing"
        }
    
    def quick_start():
        return initialize_agent_knowledge()
    
    __all__ = ['initialize_agent_knowledge', 'quick_start'] 