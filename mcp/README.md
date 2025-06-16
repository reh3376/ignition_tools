# MCP (Machine Control Program) Service

A FastAPI-based service that provides machine control and automation capabilities for IGN Scripts.

## Features

- Health monitoring and status reporting
- Neo4j integration for persistent memory
- RESTful API endpoints
- Docker containerization
- GitHub Container Registry integration

## Quick Start

### Using Docker

```bash
# Pull the latest image
docker pull ghcr.io/github-tools/mcp:latest

# Run the container
docker run -d \
  --name ign-scripts-mcp \
  -p 8080:8080 \
  -p 8081:8081 \
  -e MCP_API_KEY=your_api_key \
  -e MCP_ADMIN_USER=admin \
  -e MCP_ADMIN_PASSWORD=admin \
  -e MCP_LOG_LEVEL=INFO \
  ghcr.io/github-tools/mcp:latest
```

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/github-tools/mcp.git
cd mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
python src/main.py
```

## API Documentation

Once the service is running, visit:
- API Documentation: http://localhost:8080/docs
- Alternative Documentation: http://localhost:8080/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MCP_API_KEY | API key for authentication | default_key |
| MCP_ADMIN_USER | Admin username | admin |
| MCP_ADMIN_PASSWORD | Admin password | admin |
| MCP_LOG_LEVEL | Logging level | INFO |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository. 