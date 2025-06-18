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

#### SQL Server
```bash
SQLSERVER_HOST=localhost
SQLSERVER_PORT=1433
SQLSERVER_USERNAME=sa
SQLSERVER_PASSWORD=your-sqlserver-password
SQLSERVER_DATABASE=ignition
SQLSERVER_SSL=false
SQLSERVER_POOL_SIZE=5
SQLSERVER_TIMEOUT=30
```

#### MySQL
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=ignition
MYSQL_SSL=false
MYSQL_POOL_SIZE=10
MYSQL_TIMEOUT=30
```

#### SQLite
```bash
SQLITE_DATABASE=./data/ignition.db
```

### OPC-UA Configuration
```bash
OPCUA_SERVER_URL=opc.tcp://localhost:4840
OPCUA_USERNAME=admin
OPCUA_PASSWORD=your-opcua-password
OPCUA_SECURITY_POLICY=None
OPCUA_SECURITY_MODE=None
```

### Ignition Gateway Configuration
```bash
IGNITION_GATEWAY_URL=http://localhost:8088
IGNITION_GATEWAY_USERNAME=admin
IGNITION_GATEWAY_PASSWORD=your-gateway-password
```

### Report Configuration
```bash
REPORTS_OUTPUT_PATH=./reports
REPORTS_DEFAULT_FORMAT=csv
REPORTS_TIMEZONE=America/New_York
```

### Logging Configuration
```bash
LOG_LEVEL=INFO
LOG_FILE=./logs/ignition_scripts.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5
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

### 4. SQL Server (Enterprise Database)
- **Use Case**: Enterprise data, stored procedures, reporting
- **Connection Type**: ODBC/TCP
- **Features**: T-SQL support, Windows authentication

### 5. MySQL (Open Source Database)
- **Use Case**: Web applications, general purpose
- **Connection Type**: TCP/IP
- **Features**: Full SQL support, replication

### 6. SQLite (Embedded Database)
- **Use Case**: Local development, testing, embedded applications
- **Connection Type**: File-based
- **Features**: Zero configuration, portable

## OPC Tag Management

### Tag Browsing
The system provides hierarchical tag browsing with mock industrial data:

- **PLCs**: PLC communication status and heartbeat counters
- **Pumps**: Running status, speed (RPM), and flow rate (GPM)
- **Tanks**: Level measurements, temperature, and pressure
- **Conveyor**: Speed, load status, and fault indicators
- **HVAC**: Temperature setpoints, fan status, and damper positions
- **Alarms**: Active alarms, alarm history, and acknowledgments

### Tag Operations
- **Browse**: Navigate tag hierarchies
- **Read**: Read current tag values with quality codes
- **Write**: Write values to tags (development mode)
- **Create**: Create new tag definitions
- **Monitor**: Real-time tag monitoring

### Quality Codes
The system translates numeric quality codes to human-readable names:
- `192` → `GOOD`
- `68` → `BAD_NOT_CONNECTED`
- `72` → `BAD_DEVICE_FAILURE`
- `76` → `BAD_SENSOR_FAILURE`
- `80` → `BAD_LAST_KNOWN_VALUE`
- `84` → `BAD_COMM_FAILURE`
- `88` → `BAD_OUT_OF_SERVICE`
- `104` → `UNCERTAIN`

## Report Generation

### Supported Report Types
1. **Production Reports**: Manufacturing output, efficiency metrics
2. **Alarm Reports**: Alarm history, acknowledgment status
3. **Trend Reports**: Historical data trends and analysis
4. **Summary Reports**: Aggregated data summaries

### Output Formats
- **CSV**: Comma-separated values for Excel compatibility
- **JSON**: Structured data for API consumption
- **HTML**: Web-ready formatted reports
- **PDF**: Print-ready formatted reports (planned)

### Time Range Configuration
Reports support flexible time range specifications:
- **Hours**: `--hours 24` (last 24 hours)
- **Days**: `--days 7` (last 7 days)
- **Custom**: Specify start and end timestamps

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

### 4. Access Control
- Use least-privilege database accounts
- Implement role-based access control
- Audit database access and modifications

## Troubleshooting

### Common Issues

#### Database Connection Failures
```bash
# Test specific database connection
python -m src.core.enhanced_cli data database test-connection --config-name your_config

# Check system status
python -m src.core.enhanced_cli data status
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

#### SSL/TLS Issues
- Verify SSL certificates are valid
- Check firewall and network connectivity
- Test with SSL disabled first, then enable
- Review database server SSL configuration

### Debug Mode
Enable detailed logging for troubleshooting:
```bash
export LOG_LEVEL=DEBUG
python -m src.core.enhanced_cli data status
```

### Support
For additional support:
1. Check the main project documentation
2. Review error logs in `./logs/ignition_scripts.log`
3. Test individual components separately
4. Verify environment configuration

## Advanced Configuration

### Custom Database Configurations
You can add custom database configurations programmatically:

```python
from src.ignition.data_integration import DatabaseConnectionManager, DatabaseConfig, DatabaseType

manager = DatabaseConnectionManager()

# Add custom configuration
custom_config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="custom-host.example.com",
    port=5432,
    database="custom_db",
    username="custom_user",
    password="custom_password",
    ssl_enabled=True,
    pool_size=15
)

manager.add_config("custom_postgres", custom_config)
```

### Custom Report Templates
Extend the report generator with custom templates:

```python
from src.ignition.data_integration import ReportGenerator

generator = ReportGenerator()

# Add custom report logic
def generate_custom_report(start_time, end_time, parameters):
    # Custom report implementation
    pass
```

### Integration with Ignition
The system generates Ignition-compatible Jython scripts:

```python
# Generate connection script for Ignition
script = manager.generate_connection_script("neo4j_default", "jython")

# Generate tag creation script
tag_script = tag_manager.generate_tag_creation_script(tag_definitions, "jython")
```

This guide provides comprehensive coverage of the data integration system configuration and usage. For specific use cases or advanced configurations, refer to the individual module documentation.
