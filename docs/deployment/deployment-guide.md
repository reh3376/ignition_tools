# Deployment Guide

This guide provides detailed instructions for deploying the MCP and MCP Tools services across different environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Process](#deployment-process)
4. [Environment-Specific Configurations](#environment-specific-configurations)
5. [Monitoring and Verification](#monitoring-and-verification)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedures](#rollback-procedures)

## Prerequisites

Before deploying, ensure you have the following installed and configured:

- Docker and Docker Compose
- GitHub CLI (`gh`)
- Access to GitHub Container Registry
- Required environment variables and secrets
- Sufficient permissions for the target environment

### Required Environment Variables

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

## Environment Setup

### 1. Development Environment

```bash
# Setup development environment
./scripts/setup_dev_env.sh -a

# Run tests
./scripts/run_tests.sh -a -c
```

### 2. Staging Environment

```bash
# Create staging environment
./scripts/deploy.sh -e staging -s all -v 1.0.0
```

### 3. Production Environment

```bash
# Deploy to production
./scripts/deploy.sh -e prod -s all -v 1.0.0
```

## Deployment Process

### 1. Pre-deployment Checks

Before deploying, ensure:

- All tests pass
- Code is reviewed and approved
- Environment variables are properly set
- Database migrations are ready
- Backup of current deployment exists

### 2. Deployment Steps

1. **Build and Push Images**
   ```bash
   # Build and push MCP image
   docker build -t ghcr.io/reh3376/mcp:latest -f mcp/Dockerfile .
   docker push ghcr.io/reh3376/mcp:latest

   # Build and push MCP Tools image
   docker build -t ghcr.io/reh3376/mcp-tools:latest -f mcp-tools/Dockerfile .
   docker push ghcr.io/reh3376/mcp-tools:latest
   ```

2. **Deploy Services**
   ```bash
   # Deploy using the deployment script
   ./scripts/deploy.sh -e <environment> -s <service> -v <version>
   ```

3. **Verify Deployment**
   ```bash
   # Check service health
   curl http://localhost:8000/health
   curl http://localhost:8001/health

   # Check logs
   docker-compose -f docker-compose.<environment>.yml logs -f
   ```

## Environment-Specific Configurations

### Development

- Uses local databases
- Debug mode enabled
- Detailed logging
- Hot reload enabled

### Staging

- Mirrors production setup
- Test data available
- Monitoring enabled
- Performance testing configured

### Production

- High availability setup
- Load balancing configured
- Backup systems in place
- Monitoring and alerting active

## Monitoring and Verification

### Health Checks

```bash
# MCP Service
curl http://localhost:8000/health

# MCP Tools Service
curl http://localhost:8001/health
```

### Log Monitoring

```bash
# View logs
docker-compose -f docker-compose.<environment>.yml logs -f

# Filter logs
docker-compose -f docker-compose.<environment>.yml logs -f | grep "ERROR"
```

### Performance Monitoring

- CPU usage
- Memory consumption
- Response times
- Error rates

## Troubleshooting

### Common Issues

1. **Service Not Starting**
   ```bash
   # Check logs
   docker-compose -f docker-compose.<environment>.yml logs <service>

   # Check container status
   docker-compose -f docker-compose.<environment>.yml ps
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connection
   docker-compose -f docker-compose.<environment>.yml exec db psql -U postgres

   # Verify environment variables
   docker-compose -f docker-compose.<environment>.yml config
   ```

3. **Image Pull Failures**
   ```bash
   # Verify GitHub Container Registry access
   docker login ghcr.io -u USERNAME -p TOKEN

   # Check image existence
   docker pull ghcr.io/reh3376/mcp:latest
   ```

## Rollback Procedures

### Quick Rollback

```bash
# Rollback to previous version
./scripts/deploy.sh -e <environment> -s <service> -v <previous_version>
```

### Database Rollback

```bash
# Restore database backup
docker-compose -f docker-compose.<environment>.yml exec db \
    pg_restore -U postgres -d your_database /backups/backup.dump
```

### Configuration Rollback

```bash
# Restore previous configuration
git checkout <previous_commit> docker-compose.<environment>.yml
./scripts/deploy.sh -e <environment> -s all
```

## Best Practices

1. **Version Control**
   - Tag all releases
   - Document changes
   - Maintain changelog

2. **Security**
   - Rotate credentials regularly
   - Use secrets management
   - Implement access controls

3. **Monitoring**
   - Set up alerts
   - Monitor resource usage
   - Track error rates

4. **Backup**
   - Regular database backups
   - Configuration backups
   - Log retention

## Additional Resources

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neo4j Documentation](https://neo4j.com/docs/) 