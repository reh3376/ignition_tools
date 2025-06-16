# Environment Variables Configuration Guide

This document provides comprehensive information about environment variables used in the IGN Scripts project.

## 🔒 Security Requirements

**CRITICAL**: All sensitive information (credentials, IPs, certificates, API keys, passwords) must be stored in environment variables using the `.env` file approach. Never hardcode sensitive information in source code.

## Required Dependencies

- `python-dotenv>=1.0.0` (already included in requirements.txt)
- Environment variables loaded using `load_dotenv()` at script startup

## Configuration Setup

1. Copy the template: `cp docs/env_template.txt .env`
2. Edit `.env` with your specific values
3. Ensure `.env` is in your `.gitignore` (already configured)

## Environment Variable Categories

### OPC-UA Configuration

Essential variables for OPC-UA client functionality:

```bash
# Server Connection
OPCUA_SERVER_URL=opc.tcp://localhost:4840
OPCUA_USERNAME=admin
OPCUA_PASSWORD=your_password

# Application Identity
OPCUA_APPLICATION_NAME=IGN-Scripts
OPCUA_APPLICATION_URI=urn:IGN-Scripts:Client
OPCUA_ORGANIZATION_NAME=IGN-Scripts

# Security Configuration
OPCUA_SECURITY_POLICY=Basic256Sha256
OPCUA_SECURITY_MODE=SignAndEncrypt
OPCUA_CERTIFICATE_PATH=~/.ignition/opcua/certificates/client-certificate.der
OPCUA_PRIVATE_KEY_PATH=~/.ignition/opcua/certificates/client-private-key.pem

# Connection Options
OPCUA_SESSION_TIMEOUT=60000
OPCUA_REQUEST_TIMEOUT=10000
```

### Neo4j Graph Database

Configuration for the AI assistant memory system:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=ignition-graph
NEO4J_DATABASE=neo4j
```

### Ignition Gateway Configuration

Multi-gateway support configuration:

```bash
# Define available gateways
IGN_GATEWAYS=local_dev,staging,production

# Local Development Gateway
IGN_LOCAL_DEV_HOST=localhost
IGN_LOCAL_DEV_PORT=8088
IGN_LOCAL_DEV_HTTPS=false
IGN_LOCAL_DEV_USERNAME=admin
IGN_LOCAL_DEV_PASSWORD=password
IGN_LOCAL_DEV_VERIFY_SSL=false

# Production Gateway
IGN_PRODUCTION_HOST=production.ignition.local
IGN_PRODUCTION_PORT=8043
IGN_PRODUCTION_HTTPS=true
IGN_PRODUCTION_USERNAME=admin
IGN_PRODUCTION_PASSWORD=production_password
IGN_PRODUCTION_VERIFY_SSL=true
```

### Application Settings

General application configuration:

```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/ignition_scripts.log

# UI Configuration
UI_PORT=8501
UI_HOST=localhost
UI_DEBUG=false

# Development
DEVELOPMENT_MODE=true
ENABLE_DEBUG_LOGGING=false
```

## Usage in Code

### Required Imports

```python
import os
from dotenv import load_dotenv

# Load environment variables at script startup
load_dotenv()
```

### Accessing Environment Variables

```python
# Good - using environment variables with defaults
server_url = os.getenv('OPCUA_SERVER_URL', 'opc.tcp://localhost:4840')
username = os.getenv('OPCUA_USERNAME', 'admin')
password = os.getenv('OPCUA_PASSWORD')

# Check for required variables
if not password:
    raise ValueError("OPCUA_PASSWORD environment variable is required")

# Bad - hardcoded values (NEVER do this)
# server_url = "opc.tcp://10.4.8.15:62541"
# username = "opcuauser"
```

### Example Implementation

```python
from dotenv import load_dotenv
import os

# Load environment at module level
load_dotenv()

class OPCUAConfig:
    def __init__(self):
        self.server_url = os.getenv('OPCUA_SERVER_URL', 'opc.tcp://localhost:4840')
        self.username = os.getenv('OPCUA_USERNAME', 'admin')
        self.password = os.getenv('OPCUA_PASSWORD')
        self.application_name = os.getenv('OPCUA_APPLICATION_NAME', 'IGN-Scripts')

        # Validate required variables
        if not self.password:
            raise ValueError("OPCUA_PASSWORD environment variable is required")
```

## Security Best Practices

1. **Never commit `.env` files** - they are already in `.gitignore`
2. **Use strong, unique passwords** for each environment
3. **Use different credentials** for development, staging, and production
4. **Rotate passwords regularly** especially for production systems
5. **Use secure defaults** where possible
6. **Validate required variables** at startup

## Environment-Specific Configuration

### Development Environment
```bash
OPCUA_SERVER_URL=opc.tcp://localhost:4840
OPCUA_USERNAME=admin
OPCUA_PASSWORD=dev_password
DEVELOPMENT_MODE=true
LOG_LEVEL=DEBUG
```

### Production Environment
```bash
OPCUA_SERVER_URL=opc.tcp://production.server.com:4840
OPCUA_USERNAME=production_user
OPCUA_PASSWORD=strong_production_password
DEVELOPMENT_MODE=false
LOG_LEVEL=INFO
OPCUA_SECURITY_MODE=SignAndEncrypt
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'dotenv'**
   - Solution: `pip install python-dotenv`

2. **Environment variables not loading**
   - Ensure `load_dotenv()` is called at script startup
   - Check `.env` file exists and has correct format
   - Verify no syntax errors in `.env` file

3. **Connection failures**
   - Verify environment variables are set correctly
   - Check network connectivity to servers
   - Validate credentials

### Debug Environment Variables

```python
# Debug script to check environment variables
from dotenv import load_dotenv
import os

load_dotenv()

print("Environment Variables:")
for key in ['OPCUA_SERVER_URL', 'OPCUA_USERNAME', 'NEO4J_URI']:
    value = os.getenv(key)
    print(f"{key}: {'SET' if value else 'NOT SET'}")
```

## Integration with Cursor Rules

The project includes comprehensive cursor rules (`.cursorrules`) that enforce:
- Mandatory use of environment variables for sensitive data
- Required `python-dotenv` imports
- Proper error handling for missing variables
- Security-first development practices

All AI assistants and developers must follow these security requirements when working on the project.
