# Configuration Guide

This guide explains how to configure the MCP service for different environments and use cases.

## Environment Variables

The MCP service can be configured using environment variables. Here's a complete list of available options:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEO4J_URI` | Neo4j database URI | `bolt://localhost:7687` | Yes |
| `NEO4J_USER` | Neo4j username | `neo4j` | Yes |
| `NEO4J_PASSWORD` | Neo4j password | - | Yes |
| `API_PORT` | API server port | `8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `DEBUG_MODE` | Enable debug mode | `false` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | No |
| `API_PREFIX` | API URL prefix | `/api/v1` | No |

## Configuration Methods

### 1. Environment Variables

Set environment variables directly:

```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=your_password
```

### 2. .env File

Create a `.env` file in the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
API_PORT=8000
LOG_LEVEL=INFO
DEBUG_MODE=false
CORS_ORIGINS=*
API_PREFIX=/api/v1
```

### 3. Docker Environment

When using Docker, pass environment variables:

```bash
docker run -d \
  --name mcp \
  -p 8000:8000 \
  -e NEO4J_URI=bolt://localhost:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=your_password \
  -e LOG_LEVEL=DEBUG \
  ghcr.io/reh3376/mcp:latest
```

## Logging Configuration

The service uses Python's built-in logging module. Configure logging levels:

- `DEBUG`: Detailed information for debugging
- `INFO`: General operational information
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical errors that may prevent operation

Example logging configuration:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Security Considerations

### 1. Neo4j Authentication

- Use strong passwords
- Enable SSL/TLS for Neo4j connections
- Restrict database access to necessary IPs

### 2. API Security

- Enable CORS restrictions in production
- Use HTTPS in production
- Implement rate limiting
- Add authentication for API endpoints

### 3. Environment Variables

- Never commit `.env` files to version control
- Use secrets management in production
- Rotate credentials regularly

## Production Configuration

For production environments, consider these additional settings:

```env
# Production settings
LOG_LEVEL=WARNING
DEBUG_MODE=false
CORS_ORIGINS=https://your-domain.com
API_PREFIX=/api/v1

# Security
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Development Configuration

For development environments:

```env
# Development settings
LOG_LEVEL=DEBUG
DEBUG_MODE=true
CORS_ORIGINS=*
API_PREFIX=/api/v1

# Testing
ENABLE_TEST_MODE=true
MOCK_NEO4J=true
```

## Configuration Validation

The service validates configuration on startup. Common validation errors:

1. **Missing Required Variables**
   - Ensure all required variables are set
   - Check for typos in variable names

2. **Invalid Values**
   - Verify Neo4j URI format
   - Check port number range
   - Validate log level values

3. **Connection Issues**
   - Test Neo4j connection
   - Verify network access
   - Check firewall settings

## Best Practices

1. **Environment Separation**
   - Use different configurations for dev/staging/prod
   - Never use production credentials in development

2. **Security**
   - Use secrets management
   - Implement least privilege
   - Regular security audits

3. **Monitoring**
   - Enable metrics collection
   - Set up logging aggregation
   - Configure alerts

4. **Maintenance**
   - Document all configuration changes
   - Version control configuration templates
   - Regular configuration reviews 