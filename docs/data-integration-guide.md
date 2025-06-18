# Data Integration System Configuration Guide

This guide covers the configuration of the IGN Scripts Data Integration system, including database connections, OPC tag management, and report generation.

## Environment Variables Setup

The data integration system uses environment variables for secure configuration management. Create a `.env` file in your project root with the following configuration:

### Database Configurations

#### Neo4j Graph Database
```bash
NEO4J_HOST=localhost
NEO4J_PORT=7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j
NEO4J_SSL=false
NEO4J_POOL_SIZE=5
NEO4J_TIMEOUT=30
```

#### PostgreSQL/Supabase
```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DATABASE=ignition
POSTGRES_SSL=false
POSTGRES_POOL_SIZE=10
POSTGRES_TIMEOUT=30

# Supabase (PostgreSQL-based)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_SSL=true
```

#### InfluxDB (Time Series/Historian)
```bash
INFLUXDB_HOST=localhost
INFLUXDB_PORT=8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=ignition
INFLUXDB_BUCKET=historian
INFLUXDB_SSL=false
INFLUXDB_TIMEOUT=30
```

## Quick Start Guide

### 1. Install Dependencies
```bash
pip install python-dotenv neo4j psycopg2-binary influxdb-client pyodbc mysql-connector-python
```

### 2. Configure Environment
Create a `.env` file with your database credentials using the examples above.

### 3. Test Database Connections
```bash
# Test Neo4j connection
python -m src.core.enhanced_cli data database test-connection --config-name neo4j_default

# List all available configurations
python -m src.core.enhanced_cli data database list-configs

# Show system status
python -m src.core.enhanced_cli data status
```

### 4. Browse OPC Tags
```bash
# Browse root level
python -m src.core.enhanced_cli data tags browse

# Browse specific path
python -m src.core.enhanced_cli data tags browse --path PLCs

# Browse with specific provider
python -m src.core.enhanced_cli data tags browse --path Pumps --provider production
```

### 5. Generate Reports
```bash
# Production report (last 24 hours, CSV format)
python -m src.core.enhanced_cli data reports production --hours 24 --format csv

# Alarm report (last 8 hours, JSON format)
python -m src.core.enhanced_cli data reports alarms --hours 8 --format json

# Save report to file
python -m src.core.enhanced_cli data reports production --hours 12 --format csv --output production_report.csv
```

## Supported Database Types

### 1. Neo4j (Graph Database)
- **Use Case**: Knowledge graphs, relationship mapping, code intelligence
- **Connection Type**: Bolt protocol
- **Features**: ACID transactions, graph queries (Cypher)

### 2. PostgreSQL/Supabase (Relational Database)
- **Use Case**: Structured data, reporting, analytics
- **Connection Type**: TCP/IP with optional SSL
- **Features**: Full SQL support, JSON columns, connection pooling

### 3. InfluxDB (Time Series Database)
- **Use Case**: Historian data, metrics, time-based analytics
- **Connection Type**: HTTP/HTTPS API
- **Features**: Time-based queries, aggregations, retention policies

## CLI Commands Reference

### Database Commands
```bash
# Test database connection
ign data database test-connection --config-name <config_name>

# List all database configurations
ign data database list-configs
```

### Tag Management Commands
```bash
# Browse tags
ign data tags browse [--path <path>] [--provider <provider>]

# Read tag values
ign data tags read --tag-paths "tag1,tag2,tag3"
```

### Report Generation Commands
```bash
# Production reports
ign data reports production --hours <hours> --format <format> [--output <file>]

# Alarm reports
ign data reports alarms --hours <hours> --format <format> [--output <file>]
```

### System Status
```bash
# Show data integration system status
ign data status
```

## Security Best Practices

### 1. Environment Variables
- Never hardcode credentials in source code
- Use `.env` files for local development
- Use secure environment variable management in production

### 2. SSL/TLS Configuration
- Enable SSL for production database connections
- Use certificate validation for secure connections
- Configure appropriate cipher suites

### 3. Connection Management
- Use connection pooling to limit resource usage
- Set appropriate connection timeouts
- Implement retry logic for transient failures

## Troubleshooting

### Common Issues

#### Database Connection Failures
```bash
# Test specific database connection
ign data database test-connection --config-name your_config

# Check system status
ign data status
```

#### Missing Dependencies
```bash
# Install all required database drivers
pip install neo4j psycopg2-binary influxdb-client pyodbc mysql-connector-python

# For development dependencies
pip install python-dotenv rich click
```

#### Environment Variable Issues
- Verify `.env` file exists in project root
- Check variable names match expected format
- Ensure no trailing spaces in values
- Use quotes for values with special characters

### Debug Mode
Enable detailed logging for troubleshooting:
```bash
export LOG_LEVEL=DEBUG
ign data status
```
