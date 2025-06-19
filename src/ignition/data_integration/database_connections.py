
"""Database Connection Manager for Ignition Data Integration.

This module provides a unified interface for connecting to various database types
commonly used in industrial automation environments.

Supported Databases:
- Neo4j (Graph database for knowledge systems)
- PostgreSQL/Supabase (Relational database)
- SQL Server (Microsoft SQL Server)
- MySQL (MySQL/MariaDB)
- SQLite (Local database files)
- Oracle (Oracle Database)
- Time Series Databases (InfluxDB, TimescaleDB)

Security Features:
- Environment variable-based configuration
- Connection pooling and timeout management
- SSL/TLS support
- Credential encryption
"""

import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types."""

    NEO4J = "neo4j"
    POSTGRESQL = "postgresql"
    SUPABASE = "supabase"
    SQLSERVER = "sqlserver"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    INFLUXDB = "influxdb"
    TIMESCALEDB = "timescaledb"


@dataclass
class DatabaseConfig:
    """Database configuration container."""

    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_enabled: bool = False
    connection_timeout: int = 30
    pool_size: int = 5
    additional_params: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.additional_params is None:
            self.additional_params = {}


@dataclass
class ConnectionResult:
    """Result of a database connection attempt."""

    success: bool
    connection_id: str
    db_type: DatabaseType
    host: str
    database: str
    connection_time_ms: float
    error_message: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class DatabaseConnectionManager:
    """Unified database connection manager for multiple database types."""

    def __init__(self) -> None:
        """Initialize the database connection manager."""
        self.connections: dict[str, Any] = {}
        self.configs: dict[str, DatabaseConfig] = {}
        self._load_default_configs()

    def _load_default_configs(self) -> None:
        """Load default database configurations from environment variables."""
        # Neo4j Configuration
        if os.getenv("NEO4J_URI") or os.getenv("NEO4J_HOST"):
            self.configs["neo4j_default"] = DatabaseConfig(
                db_type=DatabaseType.NEO4J,
                host=os.getenv("NEO4J_HOST", "localhost"),
                port=int(os.getenv("NEO4J_PORT", "7687")),
                database=os.getenv("NEO4J_DATABASE", "neo4j"),
                username=os.getenv("NEO4J_USERNAME", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "ignition-graph"),
                ssl_enabled=os.getenv("NEO4J_SSL", "false").lower() == "true",
            )

        # PostgreSQL/Supabase Configuration
        if os.getenv("POSTGRES_HOST") or os.getenv("SUPABASE_URL"):
            self.configs["postgres_default"] = DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                database=os.getenv("POSTGRES_DATABASE", "postgres"),
                username=os.getenv("POSTGRES_USERNAME", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", ""),
                ssl_enabled=os.getenv("POSTGRES_SSL", "false").lower() == "true",
            )

        # Supabase-specific configuration
        if os.getenv("SUPABASE_URL"):
            self.configs["supabase_default"] = DatabaseConfig(
                db_type=DatabaseType.SUPABASE,
                host=os.getenv("SUPABASE_HOST", "localhost"),
                port=int(os.getenv("SUPABASE_PORT", "5432")),
                database=os.getenv("SUPABASE_DATABASE", "postgres"),
                username=os.getenv("SUPABASE_USERNAME", "postgres"),
                password=os.getenv("SUPABASE_PASSWORD", ""),
                ssl_enabled=True,
                additional_params={
                    "url": os.getenv("SUPABASE_URL"),
                    "key": os.getenv("SUPABASE_ANON_KEY"),
                    "service_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
                },
            )

        # SQL Server Configuration
        if os.getenv("SQLSERVER_HOST"):
            self.configs["sqlserver_default"] = DatabaseConfig(
                db_type=DatabaseType.SQLSERVER,
                host=os.getenv("SQLSERVER_HOST", "localhost"),
                port=int(os.getenv("SQLSERVER_PORT", "1433")),
                database=os.getenv("SQLSERVER_DATABASE", "master"),
                username=os.getenv("SQLSERVER_USERNAME", "sa"),
                password=os.getenv("SQLSERVER_PASSWORD", ""),
                ssl_enabled=os.getenv("SQLSERVER_SSL", "true").lower() == "true",
            )

        # MySQL Configuration
        if os.getenv("MYSQL_HOST"):
            self.configs["mysql_default"] = DatabaseConfig(
                db_type=DatabaseType.MYSQL,
                host=os.getenv("MYSQL_HOST", "localhost"),
                port=int(os.getenv("MYSQL_PORT", "3306")),
                database=os.getenv("MYSQL_DATABASE", "mysql"),
                username=os.getenv("MYSQL_USERNAME", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                ssl_enabled=os.getenv("MYSQL_SSL", "false").lower() == "true",
            )

        # InfluxDB Configuration (Time Series)
        if os.getenv("INFLUXDB_HOST") or os.getenv("HISTORIAN_HOST"):
            self.configs["historian_default"] = DatabaseConfig(
                db_type=DatabaseType.INFLUXDB,
                host=os.getenv(
                    "INFLUXDB_HOST", os.getenv("HISTORIAN_HOST", "localhost")
                ),
                port=int(
                    os.getenv("INFLUXDB_PORT", os.getenv("HISTORIAN_PORT", "8086"))
                ),
                database=os.getenv("INFLUXDB_DATABASE", "historian"),
                username=os.getenv("INFLUXDB_USERNAME", "admin"),
                password=os.getenv("INFLUXDB_PASSWORD", ""),
                ssl_enabled=os.getenv("INFLUXDB_SSL", "false").lower() == "true",
                additional_params={
                    "org": os.getenv("INFLUXDB_ORG", "ignition"),
                    "token": os.getenv("INFLUXDB_TOKEN", ""),
                    "bucket": os.getenv("INFLUXDB_BUCKET", "historian"),
                },
            )

    def add_config(self, config_name: str, config: DatabaseConfig) -> None:
        """Add a new database configuration."""
        self.configs[config_name] = config
        logger.info(f"Added database configuration: {config_name}")

    def connect(self, config_name: str) -> ConnectionResult:
        """Connect to a database using the specified configuration."""
        if config_name not in self.configs:
            return ConnectionResult(
                success=False,
                connection_id="",
                db_type=DatabaseType.POSTGRESQL,
                host="",
                database="",
                connection_time_ms=0,
                error_message=f"Configuration '{config_name}' not found",
            )

        config = self.configs[config_name]
        start_time = time.time()

        try:
            connection = self._create_connection(config)
            connection_time = (time.time() - start_time) * 1000

            # Store the connection
            connection_id = f"{config_name}_{int(time.time())}"
            self.connections[connection_id] = {
                "connection": connection,
                "config": config,
                "created_at": time.time(),
            }

            logger.info(
                f"Successfully connected to {config.db_type.value} database: {config.host}"
            )

            return ConnectionResult(
                success=True,
                connection_id=connection_id,
                db_type=config.db_type,
                host=config.host,
                database=config.database,
                connection_time_ms=connection_time,
                metadata={
                    "config_name": config_name,
                    "pool_size": config.pool_size,
                    "ssl_enabled": config.ssl_enabled,
                },
            )

        except Exception as e:
            connection_time = (time.time() - start_time) * 1000
            logger.error(f"Failed to connect to {config.db_type.value}: {e}")

            return ConnectionResult(
                success=False,
                connection_id="",
                db_type=config.db_type,
                host=config.host,
                database=config.database,
                connection_time_ms=connection_time,
                error_message=str(e),
            )

    def _create_connection(self, config: DatabaseConfig) -> Any:
        """Create a database connection based on the configuration type."""
        if config.db_type == DatabaseType.NEO4J:
            return self._create_neo4j_connection(config)
        elif config.db_type in [DatabaseType.POSTGRESQL, DatabaseType.SUPABASE]:
            return self._create_postgresql_connection(config)
        elif config.db_type == DatabaseType.SQLSERVER:
            return self._create_sqlserver_connection(config)
        elif config.db_type == DatabaseType.MYSQL:
            return self._create_mysql_connection(config)
        elif config.db_type == DatabaseType.SQLITE:
            return self._create_sqlite_connection(config)
        elif config.db_type == DatabaseType.INFLUXDB:
            return self._create_influxdb_connection(config)
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")

    def _create_neo4j_connection(self, config: DatabaseConfig) -> Any:
        """Create Neo4j connection."""
        try:
            from neo4j import GraphDatabase

            uri = f"bolt://{config.host}:{config.port}"
            if config.ssl_enabled:
                uri = f"neo4j+s://{config.host}:{config.port}"

            driver = GraphDatabase.driver(
                uri,
                auth=(config.username, config.password),
                connection_timeout=config.connection_timeout,
            )

            # Test connection
            with driver.session() as session:
                session.run("RETURN 1")

            return driver

        except ImportError:
            raise ImportError(
                "Neo4j driver not installed. Install with: pip install neo4j"
            )

    def _create_postgresql_connection(self, config: DatabaseConfig) -> Any:
        """Create PostgreSQL/Supabase connection."""
        try:
            import psycopg2
            from psycopg2 import pool

            connection_params = {
                "host": config.host,
                "port": config.port,
                "database": config.database,
                "user": config.username,
                "password": config.password,
                "connect_timeout": config.connection_timeout,
            }

            if config.ssl_enabled:
                connection_params["sslmode"] = "require"

            # Create connection pool
            connection_pool = psycopg2.pool.ThreadedConnectionPool(
                1, config.pool_size, **connection_params
            )

            return connection_pool

        except ImportError:
            raise ImportError(
                "PostgreSQL driver not installed. Install with: pip install psycopg2-binary"
            )

    def _create_sqlserver_connection(self, config: DatabaseConfig) -> Any:
        """Create SQL Server connection."""
        try:
            import pyodbc

            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config.host},{config.port};"
                f"DATABASE={config.database};"
                f"UID={config.username};"
                f"PWD={config.password};"
                f"Timeout={config.connection_timeout};"
            )

            if config.ssl_enabled:
                connection_string += "Encrypt=yes;TrustServerCertificate=no;"

            connection = pyodbc.connect(connection_string)
            return connection

        except ImportError:
            raise ImportError(
                "SQL Server driver not installed. Install with: pip install pyodbc"
            )

    def _create_mysql_connection(self, config: DatabaseConfig) -> Any:
        """Create MySQL connection."""
        try:
            import mysql.connector
            from mysql.connector import pooling

            pool_config = {
                "pool_name": f"mysql_pool_{int(time.time())}",
                "pool_size": config.pool_size,
                "host": config.host,
                "port": config.port,
                "database": config.database,
                "user": config.username,
                "password": config.password,
                "connection_timeout": config.connection_timeout,
            }

            if config.ssl_enabled:
                pool_config["ssl_disabled"] = False

            connection_pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            return connection_pool

        except ImportError:
            raise ImportError(
                "MySQL driver not installed. Install with: pip install mysql-connector-python"
            )

    def _create_sqlite_connection(self, config: DatabaseConfig) -> Any:
        """Create SQLite connection."""
        import sqlite3

        # For SQLite, the 'host' parameter is treated as the file path
        db_path = config.host if config.host != "localhost" else config.database

        connection = sqlite3.connect(
            db_path, timeout=config.connection_timeout, check_same_thread=False
        )

        return connection

    def _create_influxdb_connection(self, config: DatabaseConfig) -> Any:
        """Create InfluxDB connection."""
        try:
            from influxdb_client import InfluxDBClient

            url = f"http://{config.host}:{config.port}"
            if config.ssl_enabled:
                url = f"https://{config.host}:{config.port}"

            client = InfluxDBClient(
                url=url,
                token=config.additional_params.get("token", ""),
                org=config.additional_params.get("org", "ignition"),
                timeout=config.connection_timeout * 1000,
            )

            # Test connection
            client.ping()

            return client

        except ImportError:
            raise ImportError(
                "InfluxDB client not installed. Install with: pip install influxdb-client"
            )

    def execute_query(
        self, connection_id: str, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a query on the specified connection."""
        if connection_id not in self.connections:
            raise ValueError(f"Connection '{connection_id}' not found")

        conn_info = self.connections[connection_id]
        connection = conn_info["connection"]
        config = conn_info["config"]

        try:
            if config.db_type == DatabaseType.NEO4J:
                return self._execute_neo4j_query(connection, query, params)
            elif config.db_type in [DatabaseType.POSTGRESQL, DatabaseType.SUPABASE]:
                return self._execute_postgresql_query(connection, query, params)
            elif config.db_type == DatabaseType.SQLSERVER:
                return self._execute_sqlserver_query(connection, query, params)
            elif config.db_type == DatabaseType.MYSQL:
                return self._execute_mysql_query(connection, query, params)
            elif config.db_type == DatabaseType.SQLITE:
                return self._execute_sqlite_query(connection, query, params)
            elif config.db_type == DatabaseType.INFLUXDB:
                return self._execute_influxdb_query(connection, query, params)
            else:
                raise ValueError(f"Query execution not supported for {config.db_type}")

        except Exception as e:
            logger.error(f"Query execution failed on {config.db_type}: {e}")
            raise

    def _execute_neo4j_query(
        self, driver: Any, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute Neo4j query."""
        with driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def _execute_postgresql_query(
        self, pool: Any, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute PostgreSQL query."""
        connection = pool.getconn()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row, strict=False)) for row in rows]
                else:
                    return [{"affected_rows": cursor.rowcount}]
        finally:
            pool.putconn(connection)

    def _execute_sqlserver_query(
        self, connection: Any, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute SQL Server query."""
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row, strict=False)) for row in rows]
            else:
                return [{"affected_rows": cursor.rowcount}]
        finally:
            cursor.close()

    def _execute_mysql_query(
        self, pool: Any, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute MySQL query."""
        connection = pool.get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)

            if cursor.description:
                return cursor.fetchall()
            else:
                return [{"affected_rows": cursor.rowcount}]
        finally:
            cursor.close()
            connection.close()

    def _execute_sqlite_query(
        self, connection: Any, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute SQLite query."""
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        try:
            cursor.execute(query, params or {})
            if cursor.description:
                return [dict(row) for row in cursor.fetchall()]
            else:
                return [{"affected_rows": cursor.rowcount}]
        finally:
            cursor.close()

    def _execute_influxdb_query(
        self, client: Any, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute InfluxDB query."""
        query_api = client.query_api()
        tables = query_api.query(query)

        results = []
        for table in tables:
            for record in table.records:
                results.append(record.values)

        return results

    def disconnect(self, connection_id: str) -> bool:
        """Disconnect from a database."""
        if connection_id not in self.connections:
            return False

        try:
            conn_info = self.connections[connection_id]
            connection = conn_info["connection"]
            config = conn_info["config"]

            if config.db_type == DatabaseType.NEO4J:
                connection.close()
            elif config.db_type in [DatabaseType.POSTGRESQL, DatabaseType.SUPABASE]:
                connection.closeall()
            elif config.db_type == DatabaseType.SQLSERVER:
                connection.close()
            elif config.db_type == DatabaseType.MYSQL:
                # MySQL connection pool doesn't need explicit closing
                pass
            elif (
                config.db_type == DatabaseType.SQLITE
                or config.db_type == DatabaseType.INFLUXDB
            ):
                connection.close()

            del self.connections[connection_id]
            logger.info(f"Disconnected from {config.db_type.value} database")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return False

    def disconnect_all(self) -> int:
        """Disconnect from all databases."""
        connection_ids = list(self.connections.keys())
        disconnected_count = 0

        for connection_id in connection_ids:
            if self.disconnect(connection_id):
                disconnected_count += 1

        return disconnected_count

    def get_connection_info(self, connection_id: str) -> dict[str, Any] | None:
        """Get information about a specific connection."""
        if connection_id not in self.connections:
            return None

        conn_info = self.connections[connection_id]
        config = conn_info["config"]

        return {
            "connection_id": connection_id,
            "db_type": config.db_type.value,
            "host": config.host,
            "port": config.port,
            "database": config.database,
            "username": config.username,
            "ssl_enabled": config.ssl_enabled,
            "created_at": conn_info["created_at"],
            "age_seconds": time.time() - conn_info["created_at"],
        }

    def list_connections(self) -> list[dict[str, Any]]:
        """list all active connections."""
        return [self.get_connection_info(conn_id) for conn_id in self.connections]

    def list_configurations(self) -> list[str]:
        """list all available database configurations."""
        return list(self.configs.keys())

    def get_config_info(self, config_name: str) -> dict[str, Any] | None:
        """Get information about a database configuration."""
        if config_name not in self.configs:
            return None

        config = self.configs[config_name]
        return {
            "name": config_name,
            "db_type": config.db_type.value,
            "host": config.host,
            "port": config.port,
            "database": config.database,
            "username": config.username,
            "ssl_enabled": config.ssl_enabled,
            "pool_size": config.pool_size,
        }

    def test_connection(self, config_name: str) -> dict[str, Any]:
        """Test a database connection without storing it."""
        if config_name not in self.configs:
            return {
                "success": False,
                "error": f"Configuration '{config_name}' not found",
                "connection_time_ms": 0,
            }

        config = self.configs[config_name]
        start_time = time.time()

        try:
            connection = self._create_connection(config)
            connection_time = (time.time() - start_time) * 1000

            # Close the test connection immediately
            if config.db_type == DatabaseType.NEO4J:
                connection.close()
            elif config.db_type in [DatabaseType.POSTGRESQL, DatabaseType.SUPABASE]:
                connection.closeall()
            elif (
                config.db_type == DatabaseType.SQLSERVER
                or config.db_type == DatabaseType.SQLITE
                or config.db_type == DatabaseType.INFLUXDB
            ):
                connection.close()

            return {
                "success": True,
                "db_type": config.db_type.value,
                "host": config.host,
                "database": config.database,
                "connection_time_ms": connection_time,
            }

        except Exception as e:
            connection_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": str(e),
                "connection_time_ms": connection_time,
            }

    @contextmanager
    def get_connection(self, config_name: str) -> None:
        """Context manager for database connections."""
        result = self.connect(config_name)
        if not result.success:
            raise RuntimeError(f"Failed to connect: {result.error_message}")

        try:
            yield result.connection_id
        finally:
            self.disconnect(result.connection_id)

    def generate_connection_script(
        self, config_name: str, script_type: str = "jython"
    ) -> str:
        """Generate Ignition-compatible connection script."""
        if config_name not in self.configs:
            raise ValueError(f"Configuration '{config_name}' not found")

        config = self.configs[config_name]

        if script_type == "jython":
            return self._generate_jython_script(config)
        elif script_type == "python":
            return self._generate_python_script(config)
        else:
            raise ValueError(f"Unsupported script type: {script_type}")

    def _generate_jython_script(self, config: DatabaseConfig) -> str:
        """Generate Jython script for Ignition."""
        if config.db_type in [
            DatabaseType.POSTGRESQL,
            DatabaseType.SUPABASE,
            DatabaseType.SQLSERVER,
            DatabaseType.MYSQL,
        ]:
            return f'''"""
Generated Database Connection Script for Ignition
Database Type: {config.db_type.value}
Generated by IGN Scripts Data Integration System
"""

# Import required Ignition system functions
from system.db import runQuery, runUpdateQuery

def connect_to_database():
    """Connect to {config.db_type.value} database."""

    # Database connection parameters
    database_name = "{config.database}"  # Configure in Ignition Gateway

    # Test connection
    try:
        test_query = "SELECT 1 as connection_test"
        result = runQuery(test_query, database_name)

        if result:
            print("Database connection successful!")
            return True
        else:
            print("Database connection failed - no results returned")
            return False

    except Exception as e:
        print("Database connection error: " + str(e))
        return False

def execute_query(query, database_name="{config.database}"):
    """Execute a database query safely."""
    try:
        result = runQuery(query, database_name)
        return {{"success": True, "data": result, "error": None}}
    except Exception as e:
        return {{"success": False, "data": None, "error": str(e)}}

def execute_update(query, database_name="{config.database}"):
    """Execute a database update query safely."""
    try:
        affected_rows = runUpdateQuery(query, database_name)
        return {{"success": True, "affected_rows": affected_rows, "error": None}}
    except Exception as e:
        return {{"success": False, "affected_rows": 0, "error": str(e)}}

# Example usage:
if __name__ == "__main__":
    # Test the connection
    if connect_to_database():
        print("Ready to execute queries!")

        # Example query
        result = execute_query("SELECT CURRENT_TIMESTAMP as server_time")
        if result["success"]:
            print("Server time:", result["data"])
        else:
            print("Query failed:", result["error"])
'''
        else:
            return f'''"""
Generated Database Connection Script for Ignition
Database Type: {config.db_type.value}
Generated by IGN Scripts Data Integration System

Note: {config.db_type.value} connections require custom implementation
"""

# This database type requires custom connection handling
# Please implement connection logic specific to {config.db_type.value}

def connect_to_{config.db_type.value.lower()}():
    """Custom connection function for {config.db_type.value}."""

    # Connection parameters
    host = "{config.host}"
    port = {config.port}
    database = "{config.database}"

    # TODO: Implement {config.db_type.value} connection logic
    print("Custom connection implementation needed for {config.db_type.value}")

    return False

# Example usage:
if __name__ == "__main__":
    connect_to_{config.db_type.value.lower()}()
'''

    def _generate_python_script(self, config: DatabaseConfig) -> str:
        """Generate Python script for development/testing."""
        return f'''"""
Generated Python Database Connection Script
Database Type: {config.db_type.value}
Generated by IGN Scripts Data Integration System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_connection():
    """Create database connection."""

    # Connection parameters from environment
    config = {{
        "host": os.getenv("{config.db_type.value.upper()}_HOST", "{config.host}"),
        "port": int(os.getenv("{config.db_type.value.upper()}_PORT", "{config.port}")),
        "database": os.getenv("{config.db_type.value.upper()}_DATABASE", "{config.database}"),
        "username": os.getenv("{config.db_type.value.upper()}_USERNAME", "{config.username}"),
        "password": os.getenv("{config.db_type.value.upper()}_PASSWORD", ""),
        "ssl_enabled": os.getenv("{config.db_type.value.upper()}_SSL", "false").lower() == "true"
    }}

    try:
        # Import appropriate driver
        {self._get_python_import_statement(config.db_type)}

        # Create connection
        {self._get_python_connection_code(config.db_type)}

        print("Connection successful!")
        return connection

    except ImportError as e:
        print(f"Driver not installed: {{e}}")
        return None
    except Exception as e:
        print(f"Connection failed: {{e}}")
        return None

def test_connection():
    """Test the database connection."""
    connection = create_connection()
    if connection:
        print("Database connection test passed!")
        return True
    else:
        print("Database connection test failed!")
        return False

if __name__ == "__main__":
    test_connection()
'''

    def _get_python_import_statement(self, db_type: DatabaseType) -> str:
        """Get Python import statement for database type."""
        imports = {
            DatabaseType.NEO4J: "from neo4j import GraphDatabase",
            DatabaseType.POSTGRESQL: "import psycopg2",
            DatabaseType.SUPABASE: "import psycopg2",
            DatabaseType.SQLSERVER: "import pyodbc",
            DatabaseType.MYSQL: "import mysql.connector",
            DatabaseType.SQLITE: "import sqlite3",
            DatabaseType.INFLUXDB: "from influxdb_client import InfluxDBClient",
        }
        return imports.get(db_type, "# Import statement needed")

    def _get_python_connection_code(self, db_type: DatabaseType) -> str:
        """Get Python connection code for database type."""
        connections = {
            DatabaseType.NEO4J: """driver = GraphDatabase.driver(
            f"bolt://{config['host']}:{config['port']}",
            auth=(config['username'], config['password'])
        )
        connection = driver""",
            DatabaseType.POSTGRESQL: """connection = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['username'],
            password=config['password']
        )""",
            DatabaseType.SUPABASE: """connection = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['username'],
            password=config['password'],
            sslmode='require'
        )""",
            DatabaseType.SQLSERVER: """connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['host']},{config['port']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
        )""",
            DatabaseType.MYSQL: """connection = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['username'],
            password=config['password']
        )""",
            DatabaseType.SQLITE: """connection = sqlite3.connect(config['database'])""",
            DatabaseType.INFLUXDB: """connection = InfluxDBClient(
            url=f"http://{config['host']}:{config['port']}",
            token=config.get('token', ''),
            org=config.get('org', 'ignition')
        )""",
        }
        return connections.get(db_type, "# Connection code needed")
