"""Enhanced CLI interface for IGN Scripts with Learning System Integration.

This module provides a rich, interactive command-line interface with:
- Learning system integration and usage tracking
- Smart recommendations based on usage patterns
- Beautiful terminal UI with rich formatting
- Interactive pattern exploration
- Real-time analytics and insights
"""

# Import the main CLI group and enhanced_cli instance from core
from .cli_core import enhanced_cli, main

# Import all command modules to register them with the main group
from .cli_script_commands import script
from .cli_template_commands import template

# Import refactor commands
try:
    from src.ignition.code_intelligence.cli_commands import refactor_commands

    main.add_command(refactor_commands)
except ImportError as e:
    print(f"Refactor commands not available: {e}")
    pass

# Import module development commands
try:
    from src.ignition.modules.module_cli import module_group

    main.add_command(module_group)
except ImportError as e:
    # Module development commands not available
    print(f"Module development commands not available: {e}")
    pass

# Register command groups with main CLI
main.add_command(script)
main.add_command(template)

# TODO: Additional command modules will be imported here as they are created:
# from .cli_learning_commands import learning
# from .cli_gateway_commands import gateway_mgmt, backup, opcua
# from .cli_export_commands import export_group
# from .cli_import_commands import import_group
# from .cli_version_commands import version
# from .cli_code_commands import code
# from .cli_wrapper_commands import wrapper_group
# from .cli_data_commands import data_integration

# TODO: Register additional command groups as they are created:
# main.add_command(learning)
# main.add_command(gateway_mgmt)
# main.add_command(backup)
# main.add_command(opcua)
# main.add_command(export_group)
# main.add_command(import_group)
# main.add_command(version)
# main.add_command(code)
# main.add_command(wrapper_group)
# main.add_command(data_integration)

# Export the main CLI group and enhanced_cli for external imports
__all__ = ["enhanced_cli", "main"]
