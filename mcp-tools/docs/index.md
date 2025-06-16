# MCP Tools

Welcome to the MCP Tools documentation. This toolkit provides development and testing utilities for the Machine Control Program (MCP) service.

## Features

- Development and testing utilities
- API testing tools
- Performance monitoring
- Debugging capabilities
- Docker containerization
- GitHub Container Registry integration

## Quick Start

```bash
# Pull the latest image
docker pull ghcr.io/reh3376/mcp-tools:latest

# Run the container
docker run -d \
  --name mcp-tools \
  -p 8001:8001 \
  -e MCP_API_URL=http://mcp:8000 \
  ghcr.io/reh3376/mcp-tools:latest
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/reh3376/mcp-tools.git
   cd mcp-tools
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
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_API_URL` | MCP service API URL | `http://localhost:8000` |
| `API_PORT` | API server port | `8001` |
| `DEBUG_MODE` | Enable debug mode | `false` |

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src tests/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/reh3376/mcp-tools/issues) in our GitHub repository. 