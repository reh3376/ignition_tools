# MCP Tools Service

A development and testing toolkit for the Machine Control Program (MCP) service, providing additional tools and utilities for IGN Scripts.

## Features

- Development and testing utilities
- API testing tools
- Performance monitoring
- Debugging capabilities
- Docker containerization
- GitHub Container Registry integration

## Quick Start

### Using Docker

```bash
# Pull the latest image
docker pull ghcr.io/github-tools/mcp-tools:latest

# Run the container
docker run -d \
  --name ign-scripts-mcp-tools \
  -p 8082:8082 \
  -e MCP_TOOLS_API_KEY=your_api_key \
  -e MCP_TOOLS_LOG_LEVEL=INFO \
  ghcr.io/github-tools/mcp-tools:latest
```

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/github-tools/mcp-tools.git
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
python src/main.py
```

## API Documentation

Once the service is running, visit:
- API Documentation: http://localhost:8082/docs
- Alternative Documentation: http://localhost:8082/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MCP_TOOLS_API_KEY | API key for authentication | default_tools_key |
| MCP_TOOLS_LOG_LEVEL | Logging level | INFO |

## Testing

Run the test suite:
```bash
pytest tests/
```

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