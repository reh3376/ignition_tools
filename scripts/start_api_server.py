#!/usr/bin/env python3
"""
FastAPI Server Startup Script with Uvicorn
Phase 11.3: SME Agent Integration & Interfaces

This script provides a convenient way to start the FastAPI server
with uvicorn for API testing and documentation.
"""

import argparse
import logging
import sys
from pathlib import Path

import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Start the FastAPI server with uvicorn."""
    parser = argparse.ArgumentParser(
        description="Start SME Agent FastAPI Server with Uvicorn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Development mode with auto-reload
  python scripts/start_api_server.py --dev

  # Production mode
  python scripts/start_api_server.py --host 0.0.0.0 --port 8000

  # Custom configuration
  python scripts/start_api_server.py --host localhost --port 8080 --workers 4

  # With specific log level
  python scripts/start_api_server.py --log-level debug --dev

API Documentation will be available at:
  • Swagger UI: http://localhost:8000/docs
  • ReDoc: http://localhost:8000/redoc
  • OpenAPI JSON: http://localhost:8000/openapi.json
        """,
    )

    # Server configuration
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )

    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")

    # Development options
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode (auto-reload, debug)",
    )

    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")

    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        default="info",
        help="Log level (default: info)",
    )

    parser.add_argument(
        "--access-log",
        action="store_true",
        default=True,
        help="Enable access logging (default: True)",
    )

    # SSL options
    parser.add_argument("--ssl-keyfile", help="SSL key file path")

    parser.add_argument("--ssl-certfile", help="SSL certificate file path")

    # Parse arguments
    args = parser.parse_args()

    # Development mode overrides
    if args.dev:
        args.reload = True
        args.log_level = "debug"
        args.host = "127.0.0.1"
        logger.info("🔧 Development mode enabled")

    # Validate SSL configuration
    if args.ssl_keyfile or args.ssl_certfile:
        if not (args.ssl_keyfile and args.ssl_certfile):
            logger.error("❌ Both --ssl-keyfile and --ssl-certfile must be provided for SSL")
            sys.exit(1)

        if not Path(args.ssl_keyfile).exists():
            logger.error(f"❌ SSL key file not found: {args.ssl_keyfile}")
            sys.exit(1)

        if not Path(args.ssl_certfile).exists():
            logger.error(f"❌ SSL certificate file not found: {args.ssl_certfile}")
            sys.exit(1)

    # Display startup information
    protocol = "https" if args.ssl_keyfile else "http"
    server_url = f"{protocol}://{args.host}:{args.port}"

    print("🚀 Starting SME Agent FastAPI Server")
    print("=" * 50)
    print(f"Server URL: {server_url}")
    print(f"Workers: {args.workers}")
    print(f"Log Level: {args.log_level}")
    print(f"Reload: {args.reload}")
    print(f"Access Log: {args.access_log}")

    if args.ssl_keyfile:
        print(f"SSL Key: {args.ssl_keyfile}")
        print(f"SSL Cert: {args.ssl_certfile}")

    print("\n📖 API Documentation:")
    print(f"  • Swagger UI: {server_url}/docs")
    print(f"  • ReDoc: {server_url}/redoc")
    print(f"  • OpenAPI JSON: {server_url}/openapi.json")

    print("\n🔗 Key Endpoints:")
    print(f"  • Health Check: {server_url}/health")
    print(f"  • Chat: {server_url}/chat")
    print(f"  • Streaming Chat: {server_url}/chat/stream")
    print(f"  • File Analysis: {server_url}/analyze")
    print(f"  • System Status: {server_url}/status")

    print("\n💡 Testing Examples:")
    print("  # Health check")
    print(f"  curl {server_url}/health")
    print("  ")
    print("  # Chat request")
    print(f"  curl -X POST {server_url}/chat \\")
    print("       -H 'Content-Type: application/json' \\")
    print('       -d \'{"question": "What is Ignition?", "complexity": "standard"}\'')

    print("\n" + "=" * 50)

    # Start the server
    try:
        uvicorn.run(
            "src.ignition.modules.sme_agent.web_interface:app",
            host=args.host,
            port=args.port,
            workers=(args.workers if not args.reload else 1),  # Workers > 1 incompatible with reload
            reload=args.reload,
            log_level=args.log_level,
            access_log=args.access_log,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
            # Additional uvicorn configuration
            loop="auto",
            http="auto",
            ws="auto",
            lifespan="on",
            interface="auto",
            app_dir=".",
        )

    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
