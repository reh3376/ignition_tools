"""Main entry point for IGN Scripts CLI.

This module provides the primary command-line interface for IGN Scripts,
wrapping the enhanced CLI functionality to match documentation references.

The main CLI provides:
- Script generation with intelligent recommendations
- Template management and browsing
- Graph database exploration (400+ Ignition functions)
- OPC-UA client integration
- Gateway connection testing
- Learning system analytics
- Database backup/restore operations

Usage:
    python -m src.main --help
    python -m src.main generate --template tag_read --context gateway
    python -m src.main template list
    python -m src.main opcua connect --url opc.tcp://localhost:4840
"""

import sys
from pathlib import Path

# Ensure src is in the Python path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    # Import the main CLI function from enhanced_cli
    from core.enhanced_cli import main
    
    # Make the main function available for direct import
    __all__ = ["main"]
    
    if __name__ == "__main__":
        # Execute the enhanced CLI when run as a module
        main()
        
except ImportError as e:
    print(f"❌ Error importing enhanced CLI: {e}")
    print("\n💡 Ensure all dependencies are installed:")
    print("   uv pip install -r requirements.txt")
    print("\n🔧 If the issue persists, try:")
    print("   python -m src.core.enhanced_cli")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error starting IGN Scripts CLI: {e}")
    print("\n🔧 Try running the enhanced CLI directly:")
    print("   python -m src.core.enhanced_cli")
    sys.exit(1) 