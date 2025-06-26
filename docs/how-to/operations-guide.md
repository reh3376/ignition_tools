# How to Operate IGN Scripts

## Overview
This guide covers day-to-day operations for IGN Scripts.

## Service Management
- Starting and stopping services
- Checking service status
- Viewing logs
- Restarting services

## Monitoring
- Health checks
- Performance metrics
- Log analysis
- Alert configuration

## Maintenance
- Updates and upgrades
- Backup procedures
- Database maintenance
- Certificate renewal

## Common Operations
1. Service restart: `systemctl restart ign-scripts`
2. View logs: `journalctl -u ign-scripts -f`
3. Check health: `curl http://localhost:8000/health`
