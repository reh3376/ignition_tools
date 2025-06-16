# Troubleshooting Guide

This guide provides detailed solutions for common issues that may arise during development, testing, and deployment of the MCP and MCP Tools services.

## Table of Contents

1. [Service Issues](#service-issues)
2. [Database Issues](#database-issues)
3. [Docker Issues](#docker-issues)
4. [Authentication Issues](#authentication-issues)
5. [Network Issues](#network-issues)
6. [Performance Issues](#performance-issues)
7. [Logging and Monitoring Issues](#logging-and-monitoring-issues)

## Service Issues

### Service Not Starting

#### Symptoms
- Service fails to start
- Container exits immediately
- Health check fails
- Error messages in logs

#### Solutions

1. **Check Container Logs**
   ```bash
   # View all container logs
   docker-compose -f docker-compose.<env>.yml logs -f

   # View specific service logs
   docker-compose -f docker-compose.<env>.yml logs -f mcp
   docker-compose -f docker-compose.<env>.yml logs -f mcp-tools

   # View last 100 lines with timestamps
   docker-compose -f docker-compose.<env>.yml logs --tail=100 -t
   ```

2. **Verify Environment Variables**
   ```bash
   # Check environment variables
   docker-compose -f docker-compose.<env>.yml config

   # Verify .env file
   cat .env

   # Check if variables are properly set
   docker-compose -f docker-compose.<env>.yml exec mcp env
   ```

3. **Check Resource Limits**
   ```bash
   # View container resource usage
   docker stats

   # Check system resources
   top
   htop
   ```

4. **Verify Port Availability**
   ```bash
   # Check if ports are in use
   lsof -i :8000
   lsof -i :8001

   # Check port mappings
   docker-compose -f docker-compose.<env>.yml ps
   ```

### Service Unresponsive

#### Symptoms
- Service is running but not responding
- High latency
- Timeout errors
- 503 Service Unavailable

#### Solutions

1. **Check Service Health**
   ```bash
   # MCP Service
   curl -v http://localhost:8000/health

   # MCP Tools Service
   curl -v http://localhost:8001/health

   # Check MCP connection
   curl -v http://localhost:8001/health/mcp
   ```

2. **Verify Service Dependencies**
   ```bash
   # Check database connection
   docker-compose -f docker-compose.<env>.yml exec mcp python -c "from src.database import check_connection; check_connection()"

   # Check Neo4j connection
   docker-compose -f docker-compose.<env>.yml exec mcp python -c "from src.neo4j_client import check_connection; check_connection()"
   ```

3. **Restart Services**
   ```bash
   # Restart specific service
   docker-compose -f docker-compose.<env>.yml restart mcp

   # Restart all services
   docker-compose -f docker-compose.<env>.yml restart
   ```

## Database Issues

### Connection Failures

#### Symptoms
- Database connection errors
- Connection timeouts
- Authentication failures
- Connection pool exhaustion

#### Solutions

1. **Check Database Status**
   ```bash
   # Connect to PostgreSQL
   docker-compose -f docker-compose.<env>.yml exec db psql -U postgres

   # Check connection pool
   docker-compose -f docker-compose.<env>.yml exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"
   ```

2. **Verify Database Configuration**
   ```bash
   # Check PostgreSQL configuration
   docker-compose -f docker-compose.<env>.yml exec db cat /var/lib/postgresql/data/postgresql.conf

   # Check connection settings
   docker-compose -f docker-compose.<env>.yml exec db psql -U postgres -c "SHOW max_connections;"
   ```

3. **Reset Database Connection**
   ```bash
   # Restart database
   docker-compose -f docker-compose.<env>.yml restart db

   # Clear connection pool
   docker-compose -f docker-compose.<env>.yml exec db psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'your_database';"
   ```

### Data Corruption

#### Symptoms
- Inconsistent data
- Missing records
- Duplicate entries
- Database errors

#### Solutions

1. **Verify Data Integrity**
   ```bash
   # Check database consistency
   docker-compose -f docker-compose.<env>.yml exec db psql -U postgres -d your_database -c "SELECT pg_check_consistency();"

   # Check for corrupted tables
   docker-compose -f docker-compose.<env>.yml exec db psql -U postgres -d your_database -c "SELECT relname, relpages, reltuples FROM pg_class WHERE relkind = 'r';"
   ```

2. **Restore from Backup**
   ```bash
   # List available backups
   ls -l /backups/

   # Restore specific backup
   docker-compose -f docker-compose.<env>.yml exec db \
       pg_restore -U postgres -d your_database /backups/backup.dump
   ```

## Docker Issues

### Image Build Failures

#### Symptoms
- Build process fails
- Missing dependencies
- Permission errors
- Network issues during build

#### Solutions

1. **Check Build Context**
   ```bash
   # Verify Dockerfile location
   ls -la mcp/Dockerfile
   ls -la mcp-tools/Dockerfile

   # Check build context
   docker build -t ghcr.io/reh3376/mcp:latest -f mcp/Dockerfile . --no-cache
   ```

2. **Clear Docker Cache**
   ```bash
   # Remove unused images
   docker system prune -a

   # Remove specific image
   docker rmi ghcr.io/reh3376/mcp:latest
   ```

3. **Verify Registry Access**
   ```bash
   # Login to GitHub Container Registry
   docker login ghcr.io -u USERNAME -p TOKEN

   # Test registry access
   docker pull ghcr.io/reh3376/mcp:latest
   ```

### Container Runtime Issues

#### Symptoms
- Container crashes
- Resource constraints
- Network connectivity issues
- Volume mount problems

#### Solutions

1. **Check Container Status**
   ```bash
   # View container status
   docker-compose -f docker-compose.<env>.yml ps

   # Check container details
   docker inspect ghcr.io/reh3376/mcp:latest
   ```

2. **Verify Resource Limits**
   ```bash
   # Check container resource usage
   docker stats

   # Adjust resource limits in docker-compose.yml
   # Example:
   # services:
   #   mcp:
   #     deploy:
   #       resources:
   #         limits:
   #           cpus: '1'
   #           memory: 1G
   ```

3. **Check Volume Mounts**
   ```bash
   # List volumes
   docker volume ls

   # Inspect volume
   docker volume inspect your_volume_name

   # Check volume permissions
   ls -la /path/to/mounted/volume
   ```

## Authentication Issues

### Token Problems

#### Symptoms
- Authentication failures
- Token expiration
- Invalid credentials
- Permission denied

#### Solutions

1. **Verify Token Validity**
   ```bash
   # Check Snyk token
   snyk auth $SNYK_TOKEN

   # Check Docker token
   docker login ghcr.io -u USERNAME -p $DOCKER_TOKEN
   ```

2. **Rotate Tokens**
   ```bash
   # Rotate Snyk token
   ./scripts/rotate_tokens.sh -t snyk

   # Rotate Docker token
   ./scripts/rotate_tokens.sh -t docker
   ```

3. **Check Token Permissions**
   ```bash
   # Verify GitHub token permissions
   gh auth status

   # Check Docker token permissions
   docker login ghcr.io -u USERNAME -p $DOCKER_TOKEN
   ```

## Network Issues

### Connectivity Problems

#### Symptoms
- Service communication failures
- Timeout errors
- DNS resolution issues
- Port conflicts

#### Solutions

1. **Check Network Configuration**
   ```bash
   # List Docker networks
   docker network ls

   # Inspect network
   docker network inspect your_network_name

   # Check container network settings
   docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name
   ```

2. **Verify Port Availability**
   ```bash
   # Check port usage
   netstat -tulpn | grep LISTEN

   # Test port connectivity
   nc -zv localhost 8000
   nc -zv localhost 8001
   ```

3. **Check DNS Resolution**
   ```bash
   # Test DNS resolution
   nslookup your_domain

   # Check container DNS settings
   docker-compose -f docker-compose.<env>.yml exec mcp cat /etc/resolv.conf
   ```

## Performance Issues

### High Resource Usage

#### Symptoms
- High CPU usage
- Memory exhaustion
- Slow response times
- Service degradation

#### Solutions

1. **Monitor Resource Usage**
   ```bash
   # Check container resource usage
   docker stats

   # Monitor system resources
   top
   htop
   ```

2. **Optimize Resource Allocation**
   ```bash
   # Adjust resource limits in docker-compose.yml
   # Example:
   # services:
   #   mcp:
   #     deploy:
   #       resources:
   #         limits:
   #           cpus: '2'
   #           memory: 2G
   #         reservations:
   #           cpus: '1'
   #           memory: 1G
   ```

3. **Check Application Performance**
   ```bash
   # Monitor application metrics
   curl http://localhost:8000/metrics

   # Check database performance
   docker-compose -f docker-compose.<env>.yml exec db psql -U postgres -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```

## Logging and Monitoring Issues

### Log Collection Problems

#### Symptoms
- Missing logs
- Incomplete log data
- Log rotation issues
- Storage problems

#### Solutions

1. **Check Log Configuration**
   ```bash
   # View log configuration
   docker-compose -f docker-compose.<env>.yml config

   # Check log files
   ls -la /var/log/docker/
   ```

2. **Verify Log Collection**
   ```bash
   # Check log collection service
   docker-compose -f docker-compose.<env>.yml ps log-collector

   # Test log forwarding
   docker-compose -f docker-compose.<env>.yml exec mcp logger "Test log message"
   ```

3. **Manage Log Storage**
   ```bash
   # Configure log rotation
   # Add to docker-compose.yml:
   # logging:
   #   driver: "json-file"
   #   options:
   #     max-size: "10m"
   #     max-file: "3"
   ```

### Monitoring Alerts

#### Symptoms
- Missing alerts
- False positives
- Alert fatigue
- Incomplete monitoring

#### Solutions

1. **Verify Alert Configuration**
   ```bash
   # Check alert rules
   cat monitoring/rules/*.yml

   # Test alert conditions
   curl -X POST http://localhost:8000/test-alert
   ```

2. **Check Monitoring Service**
   ```bash
   # Verify monitoring service status
   docker-compose -f docker-compose.<env>.yml ps monitoring

   # Check monitoring metrics
   curl http://localhost:8000/metrics
   ```

3. **Update Alert Thresholds**
   ```bash
   # Adjust alert thresholds in monitoring/rules/*.yml
   # Example:
   # - alert: HighCPUUsage
   #   expr: container_cpu_usage_seconds_total > 0.8
   #   for: 5m
   #   labels:
   #     severity: warning
   ```

## Best Practices

1. **Regular Maintenance**
   - Schedule regular health checks
   - Monitor system resources
   - Review and rotate logs
   - Update dependencies

2. **Documentation**
   - Keep troubleshooting steps updated
   - Document known issues and solutions
   - Maintain runbooks for common problems
   - Update configuration documentation

3. **Monitoring**
   - Set up comprehensive monitoring
   - Configure meaningful alerts
   - Review alert thresholds regularly
   - Monitor system trends

4. **Backup and Recovery**
   - Regular database backups
   - Test recovery procedures
   - Document rollback steps
   - Maintain backup verification

## Additional Resources

- [Docker Troubleshooting Guide](https://docs.docker.com/config/daemon/#troubleshooting)
- [PostgreSQL Troubleshooting](https://www.postgresql.org/docs/current/runtime-config-logging.html)
- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Snyk Documentation](https://docs.snyk.io/) 