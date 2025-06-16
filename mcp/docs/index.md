# MCP Service

Welcome to the Machine Control Program (MCP) service documentation. This service provides a robust API for managing and monitoring machine control operations.

## Features

- Health monitoring and status reporting
- Neo4j integration for data persistence
- RESTful API endpoints
- Docker containerization
- GitHub Container Registry integration

## Quick Start

```bash
# Pull the latest image
docker pull ghcr.io/reh3376/mcp:latest

# Run the container
docker run -d \
  --name mcp \
  -p 8000:8000 \
  -e NEO4J_URI=bolt://localhost:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=your_password \
  ghcr.io/reh3376/mcp:latest
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/reh3376/mcp.git
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
   uvicorn src.main:app --reload
   ```

## API Documentation

Once the service is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j database URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | - |
| `API_PORT` | API server port | `8000` |

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/reh3376/mcp/issues) in our GitHub repository. 