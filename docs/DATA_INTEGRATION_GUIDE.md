# Data Integration System Guide

## Overview

The IGN Scripts Data Integration system provides comprehensive database connectivity, OPC tag management, historian query generation, and report creation capabilities for industrial automation systems.

## Quick Start

### 1. Installation
```bash
pip install python-dotenv neo4j psycopg2-binary influxdb-client
```

### 2. Environment Configuration
Create a `.env` file in your project root:

```bash
# Neo4j Configuration
NEO4J_HOST=localhost
NEO4J_PORT=7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your-password

# InfluxDB Configuration
INFLUXDB_HOST=localhost
INFLUXDB_PORT=8086
INFLUXDB_TOKEN=your-token
```

### 3. Basic Usage
```bash
# Test database connections
ign data database test-connection --config-name neo4j_default

# Browse OPC tags
ign data tags browse --path PLCs

# Generate production report
ign data reports production --hours 24 --format csv

# Check system status
ign data status
```

## Features

### ✅ Multi-Database Support
- Neo4j (Graph database)
- PostgreSQL/Supabase (Relational database)
- InfluxDB (Time series/historian)
- SQL Server, MySQL, SQLite

### ✅ OPC Tag Management
- Hierarchical tag browsing
- Tag reading/writing operations
- Quality code translation
- Batch tag operations

### ✅ Historian Query Generation
- Raw data queries
- Aggregated queries (avg, min, max, sum)
- Time range filtering
- Performance optimization

### ✅ Report Generation
- Production reports
- Alarm reports
- Multiple formats (CSV, JSON, HTML)
- Time-based analysis

### ✅ Security Features
- Environment variable configuration
- SSL/TLS support
- Connection pooling
- Input validation

## CLI Commands

### Database Operations
```bash
# List available database configurations
ign data database list-configs

# Test database connection
ign data database test-connection --config-name <config_name>
```

### Tag Management
```bash
# Browse tags at root level
ign data tags browse

# Browse specific path
ign data tags browse --path PLCs

# Read tag values
ign data tags read --tag-paths "PLC1/Status,PLC1/Heartbeat"
```

### Report Generation
```bash
# Production report (24 hours, CSV)
ign data reports production --hours 24 --format csv

# Alarm report (8 hours, JSON, save to file)
ign data reports alarms --hours 8 --format json --output alarms.json
```

### System Status
```bash
# Show comprehensive system status
ign data status
```

## Configuration Examples

### Neo4j Setup
```bash
NEO4J_HOST=localhost
NEO4J_PORT=7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j
NEO4J_SSL=false
```

### PostgreSQL/Supabase Setup
```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DATABASE=ignition

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SSL=true
```

### InfluxDB Setup
```bash
INFLUXDB_HOST=localhost
INFLUXDB_PORT=8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=ignition
INFLUXDB_BUCKET=historian
```

## Tag Structure Examples

The system provides mock industrial tag hierarchies:

### PLCs
- `PLC1_Status` (Boolean) - Communication status
- `PLC1_Heartbeat` (Int4) - Heartbeat counter

### Pumps
- `Pump1_Running` (Boolean) - Running status
- `Pump1_Speed` (Float8) - Speed in RPM
- `Pump1_Flow` (Float8) - Flow rate in GPM

### Quality Codes
- `192` → `GOOD`
- `68` → `BAD_NOT_CONNECTED`
- `72` → `BAD_DEVICE_FAILURE`
- `104` → `UNCERTAIN`

## Report Examples

### Production Report (CSV)
```csv
Timestamp,Line,Product,Quantity,Quality,Efficiency
2025-01-28 10:00:00,Line_A,Product_A,120,95.5,95.0
2025-01-28 11:00:00,Line_A,Product_A,115,94.2,92.3
```

### Alarm Report (JSON)
```json
{
  "headers": ["Timestamp", "Source", "Message", "Priority", "Status"],
  "data": [
    ["2025-01-28 10:15:23", "PLC1", "Communication Lost", "High", "Active"],
    ["2025-01-28 10:16:45", "Pump2", "Low Flow Rate", "Medium", "Acknowledged"]
  ]
}
```

## Troubleshooting

### Connection Issues
1. Verify environment variables are set correctly
2. Check database server is running and accessible
3. Test with SSL disabled first
4. Review firewall and network settings

### Missing Dependencies
```bash
# Install database drivers
pip install neo4j psycopg2-binary influxdb-client pyodbc mysql-connector-python

# Install core dependencies
pip install python-dotenv rich click
```

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
ign data status
```

## Integration with Ignition

The system generates Ignition-compatible Jython scripts:

### Database Connection Script
```python
# Generated Ignition database connection script
from system.db import runQuery

def connect_to_database():
    try:
        result = runQuery("SELECT 1 as test", "database_name")
        return result is not None
    except Exception as e:
        print("Connection failed: " + str(e))
        return False
```

### Tag Creation Script
```python
# Generated Ignition tag creation script
def create_tags():
    tag_configs = [
        {
            "name": "PLC1_Status",
            "tagType": "OPC",
            "dataType": "Boolean",
            "opcItemPath": "ns=2;s=PLC1.Status"
        }
    ]
    # Tag creation logic here
```

## Advanced Usage

### Programmatic Access
```python
from src.ignition.data_integration import (
    DatabaseConnectionManager,
    OPCTagManager,
    ReportGenerator
)

# Database operations
manager = DatabaseConnectionManager()
result = manager.test_connection("neo4j_default")

# Tag operations
tag_manager = OPCTagManager()
browse_result = tag_manager.browse_tags("PLCs")

# Report generation
report_gen = ReportGenerator()
report = report_gen.generate_production_report(start_time, end_time, tags)
```

### Custom Configurations
```python
# Add custom database configuration
custom_config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="custom-host.com",
    port=5432,
    database="custom_db",
    username="user",
    password="pass"
)
manager.add_config("custom_postgres", custom_config)
```

## Support

For additional help:
1. Check the completion summary: `docs/completion-summaries/PHASE_3_DATA_INTEGRATION_COMPLETION_SUMMARY.md`
2. Review system logs: `./logs/ignition_scripts.log`
3. Test individual components with debug mode enabled
4. Verify environment configuration matches examples
