"""Main entry point for IGN Scripts Web UI.

This module provides a standardized entry point for launching the IGN Scripts
Streamlit web application, ensuring consistent UI launch commands across
all documentation.

The web UI provides:
- Interactive script generation with visual templates
- Template browser with previews and filtering
- Function discovery with graph database exploration
- OPC-UA client with real-time monitoring
- Gateway connection management
- Learning analytics dashboard
- Configuration management interface

Usage:
    python -m src.ui.app
    python -c "from src.ui.app import main; main()"
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Launch the IGN Scripts Streamlit web application."""
    print("🚀 Starting IGN Scripts Web UI...")
    print("=" * 50)

    # Get the path to the Streamlit app
    ui_dir = Path(__file__).parent
    app_path = ui_dir / "streamlit_app.py"

    # Verify the Streamlit app exists
    if not app_path.exists():
        print(f"❌ Streamlit app not found at: {app_path}")
        print("\n💡 Expected file structure:")
        print(f"   {ui_dir}/")
        print("   ├── app.py (this file)")
        print("   └── streamlit_app.py (main app)")
        sys.exit(1)

    try:
        # Set up environment for Streamlit
        env = os.environ.copy()

        # Add src to Python path for imports
        src_path = str(ui_dir.parent)
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = src_path

        print("🌐 Launching Streamlit application...")
        print(f"📁 App location: {app_path}")
        print("🔗 URL: http://localhost:8501")
        print("\n💡 The web interface will open automatically in your browser")
        print("   If it doesn't open, manually navigate to: http://localhost:8501")
        print("\n⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)

        # Launch Streamlit with the app
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                "--server.headless",
                "false",
                "--server.enableCORS",
                "false",
                "--server.enableXsrfProtection",
                "false",
            ],
            env=env,
        )

        return result.returncode

    except KeyboardInterrupt:
        print("\n🛑 Web UI stopped by user")
        return 0
    except FileNotFoundError:
        print("❌ Streamlit not found!")
        print("\n💡 Install Streamlit:")
        print("   uv pip install streamlit")
        print("   # or")
        print("   pip install streamlit")
        return 1
    except Exception as e:
        print(f"❌ Error starting web UI: {e}")
        print("\n🔧 Try running Streamlit directly:")
        print(f"   streamlit run {app_path}")
        return 1


def launch_ui():
    """Alternative entry point for backwards compatibility."""
    return main()


if __name__ == "__main__":
    sys.exit(main())
