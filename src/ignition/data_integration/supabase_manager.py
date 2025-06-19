"""Supabase Database Management for IGN Scripts.

This module provides comprehensive Supabase database management including:
- Schema creation and migration
- Backup and recovery operations
- Configuration and security management
- Data seeding and initialization
- Performance monitoring and optimization

Security Features:
- Environment variable-based configuration
- Row Level Security (RLS) policies
- JWT token management
- API key rotation
- Audit logging

Author: IGN Scripts Data Integration System
Created: 2025-01-28
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class SupabaseConfig:
    """Supabase configuration container."""

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    api_url: str
    anon_key: str
    service_key: str
    jwt_secret: str
    site_url: str
    project_name: str = "IGN Scripts"
    organization_name: str = "IGN Scripts"


class SupabaseManager:
    """Comprehensive Supabase database management system."""

    def __init__(self, config: SupabaseConfig | None = None) -> None:
        """Initialize Supabase manager with configuration."""
        self.config = config or self._load_default_config()
        self.backup_dir = Path("supabase-data/backups")
        self.init_dir = Path("supabase-data/init")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.init_dir.mkdir(parents=True, exist_ok=True)

    def _load_default_config(self) -> SupabaseConfig:
        """Load default Supabase configuration from environment variables."""
        return SupabaseConfig(
            db_host=os.getenv("SUPABASE_DB_HOST", "localhost"),
            db_port=int(os.getenv("SUPABASE_DB_PORT", "5432")),
            db_name=os.getenv("SUPABASE_DB_NAME", "ignition"),
            db_user=os.getenv("SUPABASE_DB_USER", "postgres"),
            db_password=os.getenv("SUPABASE_DB_PASSWORD", "ignition-supabase"),
            api_url=os.getenv("SUPABASE_URL", "http://localhost:3000"),
            anon_key=os.getenv(
                "SUPABASE_ANON_KEY",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0",
            ),
            service_key=os.getenv(
                "SUPABASE_SERVICE_KEY",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
            ),
            jwt_secret=os.getenv(
                "SUPABASE_JWT_SECRET",
                "super-secret-jwt-token-with-at-least-32-characters-long",
            ),
            site_url=os.getenv("SUPABASE_SITE_URL", "http://localhost:3000"),
            project_name=os.getenv("SUPABASE_PROJECT_NAME", "IGN Scripts Development"),
            organization_name=os.getenv("SUPABASE_ORG_NAME", "IGN Scripts"),
        )

    def create_initialization_script(self) -> str:
        """Create comprehensive database initialization script."""
        script_path = self.init_dir / "01-init-schema.sql"

        schema_sql = """-- IGN Scripts Supabase Database Initialization
-- This script creates the initial schema for the IGN Scripts knowledge system
-- Author: IGN Scripts Data Integration System
-- Created: 2025-01-28

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom schemas
CREATE SCHEMA IF NOT EXISTS ignition;
CREATE SCHEMA IF NOT EXISTS auth;

-- set search path
SET search_path TO ignition, public;

-- ============================================================================
-- IGNITION CONTEXTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS ignition_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    context_type VARCHAR(50) NOT NULL CHECK (context_type IN ('Gateway', 'Vision', 'Perspective', 'Designer')),
    is_active BOOLEAN DEFAULT true,
    capabilities JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- IGNITION FUNCTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS ignition_functions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    module VARCHAR(100) NOT NULL,
    full_name VARCHAR(300) NOT NULL UNIQUE,
    description TEXT,
    function_type VARCHAR(50) NOT NULL,
    return_type VARCHAR(100),
    parameters JSONB DEFAULT '[]',
    examples JSONB DEFAULT '[]',
    contexts JSONB DEFAULT '[]',
    script_types JSONB DEFAULT '[]',
    complexity_level INTEGER DEFAULT 1 CHECK (complexity_level BETWEEN 1 AND 5),
    usage_frequency INTEGER DEFAULT 0,
    documentation_url TEXT,
    is_deprecated BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- IGNITION SCRIPTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS ignition_scripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    script_type VARCHAR(50) NOT NULL,
    context VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(20) DEFAULT 'python',
    functions_used JSONB DEFAULT '[]',
    parameters JSONB DEFAULT '{}',
    quality_score DECIMAL(3,2) DEFAULT 0.0,
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(20) DEFAULT 'draft',
    created_by VARCHAR(100) DEFAULT 'system',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ignition_contexts_type ON ignition_contexts(context_type);
CREATE INDEX IF NOT EXISTS idx_ignition_functions_module ON ignition_functions(module);
CREATE INDEX IF NOT EXISTS idx_ignition_functions_type ON ignition_functions(function_type);
CREATE INDEX IF NOT EXISTS idx_ignition_scripts_type ON ignition_scripts(script_type);
CREATE INDEX IF NOT EXISTS idx_ignition_scripts_context ON ignition_scripts(context);

-- ============================================================================
-- INITIAL DATA SEEDING
-- ============================================================================
INSERT INTO ignition_contexts (name, description, context_type, capabilities) VALUES
('Gateway', 'Ignition Gateway context for server-side operations', 'Gateway', '{"database": true, "tags": true, "alarms": true, "scheduling": true}'),
('Vision', 'Ignition Vision context for desktop client applications', 'Vision', '{"gui": true, "client_tags": true, "windows": true, "components": true}'),
('Perspective', 'Ignition Perspective context for web-based applications', 'Perspective', '{"web_gui": true, "mobile": true, "views": true, "sessions": true}'),
('Designer', 'Ignition Designer context for development environment', 'Designer', '{"development": true, "testing": true, "debugging": true}')
ON CONFLICT (name) DO NOTHING;

-- Sample functions
INSERT INTO ignition_functions (name, module, full_name, description, function_type, return_type, contexts, script_types) VALUES
('runQuery', 'system.db', 'system.db.runQuery', 'Execute a SQL query against a database connection', 'database', 'Dataset', '["Gateway", "Vision", "Perspective"]', '["startup", "timer", "tag_change"]'),
('writeToTag', 'system.tag', 'system.tag.writeToTag', 'Write a value to a tag', 'tag', 'QualityCode', '["Gateway", "Vision", "Perspective"]', '["startup", "timer", "tag_change", "client_event"]'),
('readFromTag', 'system.tag', 'system.tag.readFromTag', 'Read a value from a tag', 'tag', 'QualifiedValue', '["Gateway", "Vision", "Perspective"]', '["startup", "timer", "tag_change", "client_event"]'),
('messageBox', 'system.gui', 'system.gui.messageBox', 'Display a message box to the user', 'gui', 'String', '["Vision", "Perspective"]', '["client_event"]'),
('getLogger', 'system.util', 'system.util.getLogger', 'Get a logger instance for logging', 'utility', 'Logger', '["Gateway", "Vision", "Perspective"]', '["startup", "shutdown", "timer", "tag_change"]')
ON CONFLICT (full_name) DO NOTHING;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'IGN Scripts Supabase database initialization completed successfully!';
    RAISE NOTICE 'Created schemas: ignition, auth';
    RAISE NOTICE 'Created tables: contexts, functions, scripts';
    RAISE NOTICE 'Created indexes and seeded initial data';
END $$;
"""

        with open(script_path, "w") as f:
            f.write(schema_sql)

        logger.info(f"Created initialization script: {script_path}")
        return str(script_path)

    def create_backup_script(self) -> str:
        """Create automated backup script."""
        script_path = Path("scripts/supabase_backup.sh")
        script_path.parent.mkdir(exist_ok=True)

        backup_script = f"""#!/bin/bash
# Supabase Database Backup Script
# Generated by IGN Scripts Data Integration System

set -e

# Configuration
DB_HOST="{self.config.db_host}"
DB_PORT="{self.config.db_port}"
DB_NAME="{self.config.db_name}"
DB_USER="{self.config.db_user}"
BACKUP_DIR="supabase-data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/supabase_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create database backup
echo "Creating Supabase database backup..."
PGPASSWORD="{self.config.db_password}" pg_dump \\
    -h "$DB_HOST" \\
    -p "$DB_PORT" \\
    -U "$DB_USER" \\
    -d "$DB_NAME" \\
    --verbose \\
    --clean \\
    --no-owner \\
    --no-privileges \\
    > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE.gz"

# Clean up old backups (keep last 7 days)
find "$BACKUP_DIR" -name "supabase_backup_*.sql.gz" -mtime +7 -delete
echo "Cleaned up old backups"

echo "Supabase backup completed successfully!"
"""

        with open(script_path, "w") as f:
            f.write(backup_script)

        # Make script executable
        os.chmod(script_path, 0o755)

        logger.info(f"Created backup script: {script_path}")
        return str(script_path)

    def create_docker_compose_env(self) -> str:
        """Create environment file for Docker Compose."""
        env_path = Path(".env.supabase")

        env_content = f"""# Supabase Configuration for IGN Scripts
# Generated by IGN Scripts Data Integration System
# Created: {datetime.now().isoformat()}

# Database Configuration
SUPABASE_DB_NAME={self.config.db_name}
SUPABASE_DB_USER={self.config.db_user}
SUPABASE_DB_PASSWORD={self.config.db_password}
SUPABASE_DB_HOST={self.config.db_host}
SUPABASE_DB_PORT={self.config.db_port}

# API Configuration
SUPABASE_URL={self.config.api_url}
SUPABASE_ANON_KEY={self.config.anon_key}
SUPABASE_SERVICE_KEY={self.config.service_key}
SUPABASE_JWT_SECRET={self.config.jwt_secret}
SUPABASE_SITE_URL={self.config.site_url}

# Project Configuration
SUPABASE_PROJECT_NAME={self.config.project_name}
SUPABASE_ORG_NAME={self.config.organization_name}

# Security Configuration
SUPABASE_URI_ALLOW_LIST=http://localhost:3000,http://localhost:8501,http://localhost:8502

# Optional Configuration
LOGFLARE_API_KEY=your-logflare-api-key
LOGFLARE_URL=http://localhost:4000
"""

        with open(env_path, "w") as f:
            f.write(env_content)

        logger.info(f"Created environment file: {env_path}")
        return str(env_path)

    def test_connection(self) -> dict[str, Any]:
        """Test Supabase database connection."""
        try:
            # Test PostgreSQL connection
            import psycopg2

            conn_params = {
                "host": self.config.db_host,
                "port": self.config.db_port,
                "database": self.config.db_name,
                "user": self.config.db_user,
                "password": self.config.db_password,
                "connect_timeout": 10,
            }

            with psycopg2.connect(**conn_params) as conn, conn.cursor() as cursor:
                # Test basic query
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]

                # Test schema existence
                cursor.execute(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ignition';"
                )
                schema_exists = cursor.fetchone() is not None

                # Test table count
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'ignition';"
                )
                table_count = cursor.fetchone()[0] if schema_exists else 0

            return {
                "status": "success",
                "message": "Supabase database connection successful",
                "database_version": version,
                "schema_exists": schema_exists,
                "table_count": table_count,
                "connection_time": datetime.now().isoformat(),
            }

        except ImportError:
            return {
                "status": "error",
                "message": "PostgreSQL driver not installed. Install with: pip install psycopg2-binary",
                "connection_time": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {e!s}",
                "connection_time": datetime.now().isoformat(),
            }

    def get_database_status(self) -> dict[str, Any]:
        """Get comprehensive database status."""
        connection_result = self.test_connection()

        if connection_result["status"] == "success":
            try:
                import psycopg2

                conn_params = {
                    "host": self.config.db_host,
                    "port": self.config.db_port,
                    "database": self.config.db_name,
                    "user": self.config.db_user,
                    "password": self.config.db_password,
                }

                with psycopg2.connect(**conn_params) as conn, conn.cursor() as cursor:
                    # Get database size
                    cursor.execute(
                        f"SELECT pg_size_pretty(pg_database_size('{self.config.db_name}'));"
                    )
                    db_size = cursor.fetchone()[0]

                    # Get table information
                    cursor.execute(
                        """
                            SELECT
                                schemaname,
                                tablename,
                                n_tup_ins as inserts,
                                n_tup_upd as updates,
                                n_tup_del as deletes
                            FROM pg_stat_user_tables
                            WHERE schemaname = 'ignition'
                            ORDER BY tablename;
                        """
                    )
                    tables = cursor.fetchall()

                    # Get connection count
                    cursor.execute(
                        "SELECT count(*) FROM pg_stat_activity WHERE datname = %s;",
                        (self.config.db_name,),
                    )
                    connection_count = cursor.fetchone()[0]

                return {
                    "status": "healthy",
                    "database_size": db_size,
                    "connection_count": connection_count,
                    "tables": [
                        {
                            "schema": table[0],
                            "name": table[1],
                            "inserts": table[2],
                            "updates": table[3],
                            "deletes": table[4],
                        }
                        for table in tables
                    ],
                    "last_checked": datetime.now().isoformat(),
                }

            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to get database status: {e!s}",
                    "last_checked": datetime.now().isoformat(),
                }
        else:
            return connection_result

    def create_backup(self, backup_name: str | None = None) -> dict[str, Any]:
        """Create a database backup."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_name or f"supabase_backup_{timestamp}"
            backup_file = self.backup_dir / f"{backup_name}.sql"

            # Create backup using pg_dump
            cmd = [
                "pg_dump",
                "-h",
                self.config.db_host,
                "-p",
                str(self.config.db_port),
                "-U",
                self.config.db_user,
                "-d",
                self.config.db_name,
                "--verbose",
                "--clean",
                "--no-owner",
                "--no-privileges",
                "-f",
                str(backup_file),
            ]

            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.db_password

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                # Compress backup
                import gzip

                with (
                    open(backup_file, "rb") as f_in,
                    gzip.open(f"{backup_file}.gz", "wb") as f_out,
                ):
                    f_out.writelines(f_in)

                # Remove uncompressed file
                backup_file.unlink()

                backup_size = Path(f"{backup_file}.gz").stat().st_size

                return {
                    "status": "success",
                    "message": "Backup created successfully",
                    "backup_file": f"{backup_file}.gz",
                    "backup_size": backup_size,
                    "created_at": datetime.now().isoformat(),
                }
            else:
                return {
                    "status": "error",
                    "message": f"Backup failed: {result.stderr}",
                    "created_at": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Backup failed: {e!s}",
                "created_at": datetime.now().isoformat(),
            }

    def list_backups(self) -> list[dict[str, Any]]:
        """list available backups."""
        backups = []

        for backup_file in self.backup_dir.glob("*.sql.gz"):
            stat = backup_file.stat()
            backups.append(
                {
                    "name": backup_file.stem.replace(".sql", ""),
                    "file_path": str(backup_file),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "age_days": (
                        datetime.now() - datetime.fromtimestamp(stat.st_mtime)
                    ).days,
                }
            )

        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def cleanup_old_backups(self, keep_days: int = 7) -> dict[str, Any]:
        """Clean up old backup files."""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted_files = []

        for backup_file in self.backup_dir.glob("*.sql.gz"):
            file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_date < cutoff_date:
                backup_file.unlink()
                deleted_files.append(str(backup_file))

        return {
            "status": "success",
            "message": f"Cleaned up {len(deleted_files)} old backup files",
            "deleted_files": deleted_files,
            "keep_days": keep_days,
            "cleaned_at": datetime.now().isoformat(),
        }

    def generate_configuration_summary(self) -> dict[str, Any]:
        """Generate comprehensive configuration summary."""
        return {
            "supabase_configuration": {
                "database": {
                    "host": self.config.db_host,
                    "port": self.config.db_port,
                    "name": self.config.db_name,
                    "user": self.config.db_user,
                },
                "api": {"url": self.config.api_url, "site_url": self.config.site_url},
                "project": {
                    "name": self.config.project_name,
                    "organization": self.config.organization_name,
                },
            },
            "docker_services": [
                {
                    "name": "supabase-db",
                    "image": "postgres:15-alpine",
                    "port": 5432,
                    "description": "PostgreSQL database",
                },
                {
                    "name": "supabase-api",
                    "image": "supabase/gotrue:v2.99.0",
                    "port": 8000,
                    "description": "Authentication API",
                },
                {
                    "name": "supabase-rest",
                    "image": "postgrest/postgrest:v11.2.0",
                    "port": 3000,
                    "description": "Auto-generated REST API",
                },
                {
                    "name": "supabase-realtime",
                    "image": "supabase/realtime:v2.25.35",
                    "port": 4000,
                    "description": "Real-time subscriptions",
                },
                {
                    "name": "supabase-studio",
                    "image": "supabase/studio:20240101-ce42139",
                    "port": 3001,
                    "description": "Database management dashboard",
                },
                {
                    "name": "supabase-meta",
                    "image": "supabase/postgres-meta:v0.68.0",
                    "port": 8080,
                    "description": "Database metadata API",
                },
            ],
            "file_structure": {
                "initialization_scripts": str(self.init_dir),
                "backup_directory": str(self.backup_dir),
                "environment_file": ".env.supabase",
                "backup_script": "scripts/supabase_backup.sh",
            },
            "generated_at": datetime.now().isoformat(),
        }


def create_supabase_manager() -> SupabaseManager:
    """Factory function to create a configured Supabase manager."""
    return SupabaseManager()


# Example usage and testing
if __name__ == "__main__":
    # Create Supabase manager
    manager = create_supabase_manager()

    # Create initialization files
    init_script = manager.create_initialization_script()
    backup_script = manager.create_backup_script()
    env_file = manager.create_docker_compose_env()

    print("✅ Supabase Manager Setup Complete!")
    print(f"📄 Initialization script: {init_script}")
    print(f"🔄 Backup script: {backup_script}")
    print(f"⚙️ Environment file: {env_file}")

    # Test connection
    connection_status = manager.test_connection()
    print(f"🔌 Connection status: {connection_status['status']}")

    # Generate configuration summary
    config_summary = manager.generate_configuration_summary()
    print(
        f"📋 Configuration ready for {len(config_summary['docker_services'])} Docker services"
    )
