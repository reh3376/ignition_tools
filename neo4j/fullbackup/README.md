# Neo4j Database Backup Directory

This directory contains full database backups for the IGN Scripts learning system. The backup system ensures data persistence and enables easy restoration for new installations or disaster recovery.

## 📁 Directory Structure

```
neo4j/fullbackup/
├── README.md                           # This file
├── backup_metadata.json               # Backup index and metadata
├── ign_scripts_db_backup_YYYYMMDD_HHMMSS.json  # Backup files (only latest kept)
└── .gitkeep                           # Ensures directory exists in git
```

## 🗄️ Backup Files

### File Naming Convention
- Pattern: `ign_scripts_db_backup_{timestamp}.json`
- Timestamp format: `YYYYMMDD_HHMMSS`
- Example: `ign_scripts_db_backup_20250128_143022.json`

### File Content Structure
```json
{
  "metadata": {
    "timestamp": "20250128_143022",
    "datetime": "2025-01-28T14:30:22.123456",
    "reason": "Manual backup",
    "node_count": 1245,
    "relationship_count": 3487,
    "version": "1.0.0",
    "backup_type": "full",
    "source": "IGN Scripts Learning System"
  },
  "data": {
    "nodes": [...],           # All graph nodes with properties and labels
    "relationships": [...],   # All relationships with properties
    "statistics": {...}       # Database statistics at backup time
  }
}
```

## 🔧 Usage

### Command Line Interface

**Create a backup:**
```bash
# Manual backup
python -m src.ignition.graph.backup_manager backup --reason "Before major update"

# Auto backup (only if significant changes)
python -m src.ignition.graph.backup_manager backup --auto

# Via enhanced CLI
ign backup create --reason "Manual backup"
ign backup create --auto
```

**Restore from backup:**
```bash
# Restore from latest backup
python -m src.ignition.graph.backup_manager restore

# Restore from specific backup
python -m src.ignition.graph.backup_manager restore --file backup_file.json

# Via enhanced CLI
ign backup restore
ign backup restore --file backup_file.json --confirm
```

**List available backups:**
```bash
# Simple list
python -m src.ignition.graph.backup_manager list

# Detailed list
ign backup list --detailed
```

**Check backup status:**
```bash
ign backup status
```

### Programmatic Usage

```python
from src.ignition.graph.backup_manager import Neo4jBackupManager

# Create backup manager
manager = Neo4jBackupManager()

# Create backup
success, path = manager.create_full_backup("My backup reason")

# Auto backup if needed
if manager.auto_backup_on_significant_changes():
    print("Backup created due to significant changes")

# Restore from backup
success, message = manager.restore_from_backup()

# List backups
backups = manager.list_backups()
```

## ⚙️ Configuration

### Auto-Backup Thresholds

The system automatically creates backups when significant changes are detected:

- **Node threshold**: 50+ new nodes
- **Relationship threshold**: 100+ new relationships
- **Percentage threshold**: 10%+ increase in data

### Retention Policy

- **Maximum backups**: 1 (only the most recent is kept)
- **Cleanup**: Automatic removal of older backups
- **Distribution**: Latest backup is included with application releases

## 🚀 Integration Points

### Application Installation/Upgrade

1. **New Installation**:
   - Check for bundled backup in this directory
   - If found, offer to restore initial data
   - Useful for pre-populated function libraries and patterns

2. **Application Upgrade**:
   - Create backup before upgrade
   - Restore if upgrade fails
   - Migrate data structure if needed

### Automated Workflows

```python
# In your application code
from src.ignition.graph.backup_manager import Neo4jBackupManager

# Before major operations
manager = Neo4jBackupManager()
manager.create_full_backup("Before bulk data import")

# Periodic checks (can be scheduled)
manager.auto_backup_on_significant_changes()

# During application startup
if not manager.list_backups():
    # No backups exist, check for bundled backup
    bundled_backup = manager.backup_dir / "initial_backup.json"
    if bundled_backup.exists():
        manager.restore_from_backup("initial_backup.json")
```

## 🔒 Security Considerations

- **Data Sensitivity**: Backups contain learning patterns and usage data
- **Access Control**: Ensure appropriate file permissions
- **Encryption**: Consider encrypting backups for production deployments
- **Network Transfer**: Use secure methods when transferring backups

## 🐛 Troubleshooting

### Common Issues

**Backup Creation Fails**:
1. Check Neo4j connection
2. Verify write permissions to backup directory
3. Ensure sufficient disk space

**Restore Fails**:
1. Verify backup file integrity (valid JSON)
2. Check Neo4j database is accessible
3. Ensure target database can be cleared

**Auto-backup Not Triggering**:
1. Check threshold configurations
2. Verify database statistics collection
3. Review previous backup metadata

### Recovery Procedures

**Corrupted Backup File**:
1. Check backup_metadata.json for alternative files
2. Look for manual backups in the directory
3. Recreate from source system if available

**Database Connection Issues**:
1. Verify Neo4j service is running
2. Check connection credentials in .env
3. Test connection manually before backup operations

## 📊 Monitoring

### Backup Health Checks

```bash
# Check backup status
ign backup status

# Verify backup integrity
ign backup info backup_file.json

# Monitor backup size growth
ls -lah neo4j/fullbackup/
```

### Integration with Monitoring Systems

- Monitor backup file timestamps
- Alert on backup size anomalies
- Track restore operation success rates
- Monitor auto-backup trigger frequency

## 🔄 Best Practices

1. **Regular Testing**: Periodically test restore procedures
2. **Documentation**: Document custom backup reasons
3. **Monitoring**: Set up alerts for backup failures
4. **Validation**: Verify restored data integrity
5. **Scheduling**: Consider scheduled backups for production

## 📚 Related Documentation

- [Learning System Architecture](../docs/LEARNING_SYSTEM_INTEGRATION_SUMMARY.md)
- [Neo4j Client Documentation](../src/ignition/graph/client.py)
- [Database Schema](../src/ignition/graph/schema.py)
- [Enhanced CLI Guide](../docs/cli_readme.md)
