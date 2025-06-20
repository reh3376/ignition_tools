# Neo4j Backup & Restore Guide

## 📋 Overview

This directory contains backup files and tools for the IGN Scripts Neo4j database, which serves as the AI assistant's persistent memory for the Ignition Learning System.

## 🗂️ Current Backup Status

### Latest Complete Backup
- **File**: `ign_scripts_db_backup_20250616_161526.json`
- **Date**: 2025-06-16T16:15:27
- **Content**: Complete system with 3,601 nodes and 2,957 relationships
- **Includes**:
  - Original Ignition Learning System data (Functions, Patterns, Categories, etc.)
  - Deployment Pattern Learning System data (DeploymentPatterns, Metrics, etc.)
  - All relationships and metadata

## 🔄 Backup Procedures

### Automatic Backups
The system automatically creates backups when significant changes are detected:
- More than 50 new nodes
- More than 100 new relationships
- 10% increase in data volume

### Manual Backup Creation
```bash
# Create a manual backup
PYTHONPATH=/path/to/IGN_scripts python -c "
from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.backup_manager import Neo4jBackupManager
client = IgnitionGraphClient()
client.connect()
backup_manager = Neo4jBackupManager(client)
success, message = backup_manager.create_full_backup('Manual backup - your reason here')
print(f'Backup result: {message}')
client.disconnect()
"
```

### Backup via CLI (if available)
```bash
# Using the enhanced CLI
ign backup create --reason "Manual backup description"
```

## 🔧 Restore Procedures

### Full Restore (Recommended)
Use this when you want to completely replace the database with backup data:

```bash
# Run the full restore script
python scripts/full_restore_backup.py
```

**What it does:**
- Lists all available backups
- Shows current database statistics
- Requires confirmation before proceeding
- Completely replaces all data with backup data
- Provides detailed progress and final statistics

### Selective Restore (Advanced)
Use this when you want to preserve some existing data while restoring missing data:

```bash
# Run the selective restore script
python scripts/selective_restore_backup.py
```

**What it does:**
- Preserves specified node types (e.g., DeploymentPattern, DeploymentMetric)
- Restores missing data from backup
- Merges data intelligently to avoid duplicates

## 📊 Database Statistics

### Current Database Content (as of latest backup)
```
Node Types:
  DeploymentMetric: 1,080    ← Deployment performance data
  Pattern: 745               ← Learning patterns
  Parameter: 649             ← Function parameters
  Function: 408              ← Ignition system functions
  UsageEvent: 353            ← Usage tracking
  UserSession: 145           ← Session data
  PatternAnalysis: 91        ← Analysis results
  Subcategory: 32            ← Function subcategories
  DeploymentExecution: 27    ← Deployment records
  Category: 23               ← Function categories
  DeploymentPattern: 4       ← Learned deployment patterns
  RollbackScenario: 4        ← Rollback procedures
  EnvironmentAdaptation: 3   ← Environment adaptations
  [... and more]

Total: 3,601 nodes, 2,957 relationships
```

## 🛡️ Data Persistence

### Docker Volume Mounting
The Neo4j container uses persistent volumes:
```yaml
volumes:
  - ./graph-data/data:/data           # Database files
  - ./graph-data/logs:/logs           # Log files
  - ./graph-data/import:/var/lib/neo4j/import  # Import directory
  - ./graph-data/plugins:/plugins     # Plugin files
```

### Physical Storage
Database files are stored in: `./graph-data/data/databases/neo4j/`

## 🚨 Emergency Recovery

### If Database is Lost/Corrupted
1. **Stop the Neo4j container**: `docker-compose stop neo4j`
2. **Clear corrupted data**: `rm -rf ./graph-data/data/*`
3. **Start Neo4j**: `docker-compose up -d neo4j`
4. **Wait for startup**: `sleep 15`
5. **Run full restore**: `python scripts/full_restore_backup.py`

### If Container Won't Start
1. **Check logs**: `docker-compose logs neo4j`
2. **Check disk space**: `df -h`
3. **Check file permissions**: `ls -la ./graph-data/`
4. **Restart Docker**: `docker-compose down && docker-compose up -d`

## 📝 Best Practices

### Regular Backups
- Automatic backups occur on significant changes
- Manual backups before major system changes
- Keep multiple backup versions for safety

### Testing Restores
- Periodically test restore procedures
- Verify data integrity after restore
- Document any issues or improvements

### Monitoring
- Check backup file sizes for consistency
- Monitor database growth trends
- Watch for backup failures in logs

## 🔗 Related Files

- `backup_manager.py` - Core backup/restore functionality
- `scripts/full_restore_backup.py` - Full restore script
- `scripts/selective_restore_backup.py` - Selective restore script
- `backup_metadata.json` - Backup metadata and history

## 📞 Support

If you encounter issues with backup/restore:
1. Check the logs: `docker-compose logs neo4j`
2. Verify Neo4j is running: `docker ps | grep neo4j`
3. Test connection: `python -c "from src.ignition.graph.client import IgnitionGraphClient; c = IgnitionGraphClient(); print('Connected:', c.connect())"`
4. Check backup file integrity: Ensure JSON files are valid

---

**Last Updated**: 2025-06-16
**Database Version**: Neo4j 5.15-community
**Backup Format**: JSON with metadata
