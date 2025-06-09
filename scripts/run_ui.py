#!/usr/bin/env python3
"""Launch script for the IGN Scripts Streamlit UI."""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Path to the Streamlit app
    app_path = project_root / "src" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ Streamlit app not found at: {app_path}")
        sys.exit(1)
    
    print("🚀 Starting IGN Scripts Web UI...")
    print(f"📁 Project root: {project_root}")
    print(f"🎯 App path: {app_path}")
    print()
    print("🌐 The web interface will open in your browser automatically.")
    print("💡 To stop the server, press Ctrl+C")
    print()
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\n👋 IGN Scripts UI stopped.")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 