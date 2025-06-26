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

# Import Phase 9.7 deployment commands
try:
    from src.ignition.modules.deployment.cli_commands import deployment_cli

    main.add_command(deployment_cli)
except ImportError as e:
    # Deployment commands not available
    print(f"Deployment commands not available: {e}")
    pass

# Import Phase 9.8 advanced features commands
try:
    from src.ignition.modules.advanced_features.cli_commands import (
        advanced_features_cli,
    )

    main.add_command(advanced_features_cli)
except ImportError as e:
    # Advanced features commands not available
    print(f"Advanced features commands not available: {e}")
    pass

# Import Phase 13.1 LLM Infrastructure commands
try:
    from src.ignition.modules.llm_infrastructure.cli_commands import (
        llm_infrastructure_cli,
    )

    main.add_command(llm_infrastructure_cli)
except ImportError as e:
    # LLM Infrastructure commands not available
    print(f"LLM Infrastructure commands not available: {e}")
    pass

# Import Phase 13.2 Fine-tuning commands
try:
    from src.ignition.modules.llm_infrastructure.fine_tuning_cli import (
        fine_tuning_cli,
    )

    main.add_command(fine_tuning_cli)
except ImportError as e:
    # Fine-tuning commands not available
    print(f"Fine-tuning commands not available: {e}")
    pass

# Import Phase 13.3 Adaptive Learning commands
try:
    from src.ignition.modules.llm_infrastructure.adaptive_learning_cli import (
        adaptive_learning_cli,
    )

    main.add_command(adaptive_learning_cli)
except ImportError as e:
    # Adaptive learning commands not available
    print(f"Adaptive learning commands not available: {e}")
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
