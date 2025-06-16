# Configuration Guide

This section provides comprehensive configuration documentation for the IGN Scripts project, covering environment setup, connection management, and security configuration.

## 📋 Configuration Overview

IGN Scripts uses environment variables for all configuration to ensure security and flexibility across different deployment environments. All sensitive information must be stored in `.env` files and never hardcoded in source code.

## 🔐 Security Requirements

**CRITICAL**: Follow these security requirements:
- ✅ **Never hardcode sensitive information** (credentials, IPs, certificates, API keys, passwords)
- ✅ **Always use `.env` files** for storing sensitive configuration data  
- ✅ **Always use python-dotenv** library to load environment variables
- ✅ **Always import and use** `os.getenv()` in scripts
- ❌ **Never commit** `.env` files to version control

## 📚 Configuration Documentation

### Core Configuration
- **[Environment Variables](./environment-variables.md)** - Complete guide to all environment variables
- **[Environment Template](./env-template.txt)** - Template for .env file setup
- **[Application Settings](./application-settings.md)** - General application configuration
- **[Security Configuration](./security-config.md)** - Security and authentication setup

### Connection Configuration  
- **[OPC-UA Configuration](./opcua-config.md)** - OPC-UA server connection setup
- **[Gateway Configuration](./gateway-config.md)** - Ignition Gateway connection management
- **[Database Configuration](./database-config.md)** - Neo4j graph database setup

### Advanced Configuration
- **[Development Setup](./development-setup.md)** - Development environment configuration
- **[Production Deployment](./production-config.md)** - Production environment setup
- **[Docker Configuration](./docker-config.md)** - Container deployment configuration

## 🚀 Quick Setup Guide

### 1. Environment File Setup
```bash
# Copy the template
cp docs/configuration/env-template.txt .env

# Edit with your configuration
nano .env  # or your preferred editor
```

### 2. Required Imports in Python
```python
import os
from dotenv import load_dotenv

# Load environment variables at script startup
load_dotenv()
```

### 3. Basic Configuration Example
```python
# Good - using environment variables with defaults
server_url = os.getenv('OPCUA_SERVER_URL', 'opc.tcp://localhost:4840')
username = os.getenv('OPCUA_USERNAME', 'admin')
password = os.getenv('OPCUA_PASSWORD')

# Validate required variables
if not password:
    raise ValueError("OPCUA_PASSWORD environment variable is required")

# Bad - hardcoded values (NEVER do this)
# server_url = "opc.tcp://10.4.8.15:62541"
# username = "opcuauser"
```

## 📝 Configuration Categories

### Essential Configuration
These variables are required for basic functionality:

| Category | Variables | Required |
|----------|-----------|----------|
| **Neo4j Database** | `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` | ✅ Required |
| **OPC-UA Connection** | `OPCUA_SERVER_URL`, `OPCUA_USERNAME`, `OPCUA_PASSWORD` | 🔄 Optional |
| **Gateway Connection** | `IGN_GATEWAYS`, gateway-specific variables | 🔄 Optional |

### Security Configuration
Variables for authentication and certificates:

| Category | Purpose | Examples |
|----------|---------|----------|
| **OPC-UA Security** | Certificate paths, security policies | `OPCUA_CERTIFICATE_PATH`, `OPCUA_SECURITY_POLICY` |
| **Gateway Auth** | Authentication credentials | `IGN_*_USERNAME`, `IGN_*_PASSWORD` |
| **API Keys** | External service authentication | `MCP_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN` |

### Application Settings
General application behavior:

| Category | Purpose | Examples |
|----------|---------|----------|
| **Logging** | Log levels and file paths | `LOG_LEVEL`, `LOG_FILE_PATH` |
| **UI Settings** | Streamlit configuration | `UI_PORT`, `UI_HOST` |
| **Development** | Development mode settings | `DEVELOPMENT_MODE`, `DEBUG` |

## 🔧 Configuration Templates

### Minimal Development Setup
```env
# Minimal .env for development
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
LOG_LEVEL=INFO
DEVELOPMENT_MODE=true
```

### Complete Production Setup
```env
# Production .env example
NEO4J_URI=bolt://prod-neo4j:7687
NEO4J_USERNAME=ignition_user
NEO4J_PASSWORD=secure_production_password

OPCUA_SERVER_URL=opc.tcp://prod-server:4840
OPCUA_USERNAME=opcua_service
OPCUA_PASSWORD=secure_opcua_password
OPCUA_SECURITY_POLICY=Basic256Sha256
OPCUA_SECURITY_MODE=SignAndEncrypt

IGN_GATEWAYS=production
IGN_PRODUCTION_HOST=ignition.company.com
IGN_PRODUCTION_PORT=8043
IGN_PRODUCTION_HTTPS=true
IGN_PRODUCTION_USERNAME=service_account
IGN_PRODUCTION_PASSWORD=secure_gateway_password

LOG_LEVEL=WARNING
DEVELOPMENT_MODE=false
```

## 🛠️ Configuration Management Tools

### CLI Configuration Commands
```bash
# List available templates
python -m src.main template list

# Generate gateway configuration
python -m src.main gateway config --name production

# Test OPC-UA connection
python -m src.main opcua test-connection

# Validate configuration
python -m src.main config validate
```

### Configuration Validation
IGN Scripts includes built-in configuration validation:

```python
from src.ignition.core.config_validator import ConfigValidator

# Validate current configuration
validator = ConfigValidator()
result = validator.validate_all()

if result.is_valid:
    print("✅ Configuration is valid")
else:
    print("❌ Configuration errors:")
    for error in result.errors:
        print(f"  - {error}")
```

## 📖 Best Practices

### Security Best Practices
1. **Use strong, unique passwords** for each environment
2. **Enable SSL/TLS** for all production connections
3. **Rotate credentials regularly** (quarterly recommended)
4. **Use dedicated service accounts** with minimal permissions
5. **Never share credentials** between environments

### Environment Separation
1. **Use different `.env` files** for development/staging/production
2. **Use environment-specific variable prefixes** where needed
3. **Document environment differences** in configuration files
4. **Test configuration** in staging before production deployment

### Maintenance Guidelines
1. **Document all configuration changes** in git commit messages
2. **Use configuration templates** for new environments
3. **Validate configuration** before deployment
4. **Monitor configuration drift** between environments

## 🚨 Common Issues

### Missing Environment Variables
```bash
# Error: Environment variable not found
ValueError: OPCUA_PASSWORD environment variable is required

# Solution: Add to .env file
echo "OPCUA_PASSWORD=your_password" >> .env
```

### Invalid Connection Configuration
```bash
# Error: Connection refused
ConnectionError: Failed to connect to opc.tcp://localhost:4840

# Solution: Check server URL and credentials in .env
OPCUA_SERVER_URL=opc.tcp://correct-server:4840
```

### Certificate Issues
```bash
# Error: Certificate verification failed
SecurityError: Server certificate not trusted

# Solution: Configure certificate paths
OPCUA_CERTIFICATE_PATH=path/to/cert.der
OPCUA_PRIVATE_KEY_PATH=path/to/key.pem
```

## 🔗 Related Documentation

- [Environment Variables Reference](./environment-variables.md)
- [Security Configuration Guide](./security-config.md)
- [Development Setup Guide](../development/setup.md)
- [Deployment Guide](../deployment/deployment-guide.md)
- [Troubleshooting Guide](../troubleshooting/troubleshooting-guide.md)

## 📞 Support

For configuration assistance:
1. Check the [Troubleshooting Guide](../troubleshooting/troubleshooting-guide.md)
2. Review [Common Issues](#-common-issues) above
3. Use CLI validation commands for diagnostics
4. Refer to [Environment Variables Reference](./environment-variables.md) for details 