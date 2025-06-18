# Supabase Connection Guide for IGN Scripts

## Supabase Connection Information for IGN Scripts

### Database Connection Settings
Based on the `.env.supabase` configuration file:

- **Host**: localhost
- **Port**: 5432
- **Database**: ignition
- **User**: postgres
- **Password**: ignition-supabase
- **Connection String**: postgresql://postgres:ignition-supabase@localhost:5432/ignition

### Service Endpoints

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Main API | 3000 | http://localhost:3000 | Base Supabase REST API |
| Auth API | 8000 | http://localhost:8000/auth/v1/ | Authentication service |
| Real-time | 4000 | ws://localhost:4000/socket | WebSocket subscriptions |
| Studio | 3001 | http://localhost:3001 | Database management UI |
| Meta API | 8080 | http://localhost:8080/ | Database metadata |

### Authentication Keys

**Anonymous Key (Public Access):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJle
HAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
```

**Service Role Key (Administrative):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2
Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU
```

**JWT Secret:**
```
super-secret-jwt-token-with-at-least-32-characters-long
```

### Complete Environment Configuration

The `.env.supabase` file contains:

```bash
# Database Configuration
SUPABASE_DB_NAME=ignition
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=ignition-supabase
SUPABASE_DB_HOST=localhost
SUPABASE_DB_PORT=5432

# API Configuration
SUPABASE_URL=http://localhost:3000
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=super-secret-jwt-token-with-at-least-32-characters-long
SUPABASE_SITE_URL=http://localhost:3000

# Project Configuration
SUPABASE_PROJECT_NAME=IGN Scripts Development
SUPABASE_ORG_NAME=IGN Scripts

# Security Configuration
SUPABASE_URI_ALLOW_LIST=http://localhost:3000,http://localhost:8501,http://localhost:8502

# Optional Services
LOGFLARE_API_KEY=your-logflare-api-key
LOGFLARE_URL=http://localhost:4000
```

### CLI Commands

```bash
# Setup Supabase infrastructure
ign data supabase setup

# Service management
ign data supabase start          # Start all Docker services
ign data supabase stop           # Stop all Docker services

# Health monitoring
ign data supabase status         # Check service status
ign data supabase health         # Database health check

# Backup management
ign data supabase backup         # Create database backup
ign data supabase backups        # List available backups
ign data supabase cleanup        # Remove old backups

# Configuration
ign data supabase config         # Show configuration summary
```

### Docker Services

The system runs 6 Docker services:
- **supabase-db** (5432): PostgreSQL 15-alpine database
- **supabase-api** (8000): GoTrue authentication API
- **supabase-rest** (3000): PostgREST auto-generated API
- **supabase-realtime** (4000): Real-time WebSocket service
- **supabase-studio** (3001): Database management dashboard
- **supabase-meta** (8080): Database metadata and migrations

### Usage Examples

**Python Connection:**
```python
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.supabase')
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(url, key)
```

**Direct PostgreSQL:**
```python
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="ignition",
    user="postgres",
    password="ignition-supabase"
)
```

---

*IGN Scripts Supabase Integration Documentation*
*Generated: 2025-06-18*
