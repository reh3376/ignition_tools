# Deployment Quick Reference

This guide provides quick access to common deployment commands and procedures.

## Common Commands

### Environment Setup

```bash
# Setup all environments
./scripts/setup_dev_env.sh -a

# Setup specific environment
./scripts/setup_dev_env.sh -p  # Python only
./scripts/setup_dev_env.sh -n  # Node.js only
./scripts/setup_dev_env.sh -d  # Docker only
```

### Running Tests

```bash
# Run all tests with coverage
./scripts/run_tests.sh -a -c

# Run specific tests
./scripts/run_tests.sh -p  # Python tests
./scripts/run_tests.sh -n  # Node.js tests

# Run with verbose output
./scripts/run_tests.sh -a -v
```

### Deployment

```bash
# Deploy to development
./scripts/deploy.sh -e dev -s all

# Deploy to staging
./scripts/deploy.sh -e staging -s all -v 1.0.0

# Deploy to production
./scripts/deploy.sh -e prod -s all -v 1.0.0

# Deploy specific service
./scripts/deploy.sh -e prod -s mcp -v 1.0.0
./scripts/deploy.sh -e prod -s mcp-tools -v 1.0.0
```

### Docker Commands

```bash
# Build images
docker build -t ghcr.io/reh3376/mcp:latest -f mcp/Dockerfile .
docker build -t ghcr.io/reh3376/mcp-tools:latest -f mcp-tools/Dockerfile .

# Push images
docker push ghcr.io/reh3376/mcp:latest
docker push ghcr.io/reh3376/mcp-tools:latest

# Pull images
docker pull ghcr.io/reh3376/mcp:latest
docker pull ghcr.io/reh3376/mcp-tools:latest
```

### Docker Compose Commands

```bash
# Start services
docker-compose -f docker-compose.<env>.yml up -d

# Stop services
docker-compose -f docker-compose.<env>.yml down

# View logs
docker-compose -f docker-compose.<env>.yml logs -f

# Restart services
docker-compose -f docker-compose.<env>.yml restart
```

### Health Checks

```bash
# MCP Service
curl http://localhost:8000/health

# MCP Tools Service
curl http://localhost:8001/health

# MCP Connection Check
curl http://localhost:8001/health/mcp
```

### Database Commands

```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.<env>.yml exec db psql -U postgres

# Backup database
docker-compose -f docker-compose.<env>.yml exec db \
    pg_dump -U postgres -d your_database > backup.dump

# Restore database
docker-compose -f docker-compose.<env>.yml exec db \
    pg_restore -U postgres -d your_database /backups/backup.dump
```

### Logging Commands

```bash
# View all logs
docker-compose -f docker-compose.<env>.yml logs -f

# View specific service logs
docker-compose -f docker-compose.<env>.yml logs -f mcp
docker-compose -f docker-compose.<env>.yml logs -f mcp-tools

# Filter logs
docker-compose -f docker-compose.<env>.yml logs -f | grep "ERROR"
docker-compose -f docker-compose.<env>.yml logs -f | grep "WARNING"
```

### Token Management

```bash
# Rotate Snyk token
./scripts/rotate_tokens.sh -t snyk

# Rotate Docker token
./scripts/rotate_tokens.sh -t docker

# Rotate all tokens
./scripts/rotate_tokens.sh -t all
```

## Environment Variables

### Required Variables

```bash
# GitHub Container Registry
GITHUB_TOKEN=your_github_token
DOCKER_TOKEN=your_docker_token

# Database
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db

# Neo4j
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_neo4j_user
NEO4J_PASSWORD=your_neo4j_password

# API Configuration
API_PORT=8000
LOG_LEVEL=INFO
```

### Environment-Specific Variables

```bash
# Development
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Staging
DEBUG_MODE=false
LOG_LEVEL=INFO

# Production
DEBUG_MODE=false
LOG_LEVEL=WARNING
```

## Common Issues and Solutions

### Service Not Starting

```bash
# Check logs
docker-compose -f docker-compose.<env>.yml logs <service>

# Check container status
docker-compose -f docker-compose.<env>.yml ps

# Restart service
docker-compose -f docker-compose.<env>.yml restart <service>
```

### Database Connection Issues

```bash
# Check database connection
docker-compose -f docker-compose.<env>.yml exec db psql -U postgres

# Verify environment variables
docker-compose -f docker-compose.<env>.yml config

# Check database logs
docker-compose -f docker-compose.<env>.yml logs db
```

### Image Pull Failures

```bash
# Verify GitHub Container Registry access
docker login ghcr.io -u USERNAME -p TOKEN

# Check image existence
docker pull ghcr.io/reh3376/mcp:latest

# Clear Docker cache
docker system prune -a
```

## Rollback Procedures

### Quick Rollback

```bash
# Rollback to previous version
./scripts/deploy.sh -e <env> -s <service> -v <previous_version>
```

### Database Rollback

```bash
# Restore database backup
docker-compose -f docker-compose.<env>.yml exec db \
    pg_restore -U postgres -d your_database /backups/backup.dump
```

### Configuration Rollback

```bash
# Restore previous configuration
git checkout <previous_commit> docker-compose.<env>.yml
./scripts/deploy.sh -e <env> -s all
``` 