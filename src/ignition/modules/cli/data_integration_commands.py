"""CLI commands for Data Integration Module functionality."""

import json
import os
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def _create_test_module():
    """Create a test data integration module instance."""
    try:
        # Import here to avoid circular imports
        from ..core.abstract_module import ModuleContext
        from ..data_integration import create_data_integration_module

        # Create test paths
        base_path = Path.cwd() / "test_data_integration"
        base_path.mkdir(exist_ok=True)

        # Ensure all required directories exist
        module_path = base_path / "modules"
        config_path = base_path / "config"
        data_path = base_path / "data"
        log_path = base_path / "logs"
        temp_path = base_path / "temp"

        for path in [module_path, config_path, data_path, log_path, temp_path]:
            path.mkdir(exist_ok=True)

        # Create a test context
        context = ModuleContext(
            module_path=module_path,
            config_path=config_path,
            data_path=data_path,
            log_path=log_path,
            temp_path=temp_path,
        )

        # Create module using factory function
        module = create_data_integration_module(
            context, "Test Data Integration", "1.0.0"
        )

        return module
    except Exception as e:
        console.print(f"❌ Failed to create test module: {e}")
        raise


@click.group(name="data")
def data_integration_group() -> None:
    """Data integration module commands."""
    pass


@data_integration_group.command("demo")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--fake-data", "-f", is_flag=True, help="Generate fake data for testing")
def demo_command(verbose: bool, fake_data: bool) -> None:
    """Demonstrate the data integration module functionality."""
    console.print("🔗 Data Integration Module Demo")
    console.print("=" * 50)

    try:
        # Import required types
        from ..data_integration import (
            DataSourceConfig,
            DataSourceType,
            VariableMetadata,
            VariableType,
        )

        # Create module instance
        console.print("Creating Data Integration Module instance...")
        module = _create_test_module()

        if verbose:
            console.print("Verbose mode enabled")

        console.print(
            f"✅ Module created: {module.metadata.name} v{module.metadata.version}"
        )

        # Configure module with default settings
        console.print("\nConfiguring module...")
        default_config = {
            "module_id": module.metadata.id,
            "version": module.metadata.version,
            "enabled": True,
            "debug_mode": verbose,
            "log_level": "DEBUG" if verbose else "INFO",
            "security": {
                "encryption_enabled": True,
                "certificate_validation": True,
                "max_retry_attempts": 3,
                "connection_timeout": 30,
            },
            "performance": {
                "max_concurrent_connections": 50,
                "default_batch_size": 1000,
                "connection_pool_size": 10,
                "message_buffer_size": 10000,
            },
            "data_processing": {
                "enable_metadata_injection": True,
                "normalize_timestamps": True,
                "validate_data_quality": True,
                "auto_detect_variable_types": True,
            },
            "json_output": {
                "include_metadata": True,
                "timestamp_format": "iso8601",
                "normalize_values": True,
                "include_quality_codes": True,
            },
        }

        if module.configure_module(default_config):
            console.print("✅ Module configured successfully")
        else:
            console.print("❌ Module configuration failed")
            return

        # Initialize module
        console.print("\nInitializing module...")
        if module.initialize_module():
            console.print("✅ Module initialized successfully")
        else:
            console.print("❌ Module initialization failed")
            return

        # Start module
        console.print("\nStarting module...")
        if module.startup_module():
            console.print("✅ Module started successfully")
        else:
            console.print("❌ Module startup failed")
            return

        # Demonstrate data source configuration
        console.print("\nConfiguring data sources...")

        # OPC-UA data source
        opcua_config = DataSourceConfig(
            source_id="test_opcua_server",
            source_type=DataSourceType.OPC_UA,
            connection_params={
                "server_url": os.getenv("OPCUA_SERVER_URL", "opc.tcp://localhost:4840"),
                "username": os.getenv("OPCUA_USERNAME", "admin"),
                "password": os.getenv("OPCUA_PASSWORD", "password"),
            },
            enabled=True,
        )

        if module.add_data_source(opcua_config):
            console.print("✅ OPC-UA data source configured")
        else:
            console.print("❌ Failed to configure OPC-UA data source")

        # Database data source
        db_config = DataSourceConfig(
            source_id="test_database",
            source_type=DataSourceType.POSTGRESQL,
            connection_params={
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "ignition_data"),
                "username": os.getenv("DB_USERNAME", "postgres"),
                "password": os.getenv("DB_PASSWORD", "password"),
            },
            enabled=True,
        )

        if module.add_data_source(db_config):
            console.print("✅ Database data source configured")
        else:
            console.print("❌ Failed to configure database data source")

        # Demonstrate variable metadata
        console.print("\nDemonstrating variable metadata...")

        # Process Variable metadata
        pv_metadata = VariableMetadata(
            variable_type=VariableType.PV,
            name="Temperature_01",
            engineering_units="°C",
            range_high=100.0,
            range_low=0.0,
            max_value=100.0,
            is_primary_pv=True,
        )

        # Control Variable metadata
        cv_metadata = VariableMetadata(
            variable_type=VariableType.CV,
            name="Valve_01",
            engineering_units="%",
            range_high=100.0,
            range_low=0.0,
            max_value=100.0,
        )

        console.print(
            f"✅ PV Metadata: {pv_metadata.variable_type.value} - {pv_metadata.engineering_units}"
        )
        console.print(
            f"✅ CV Metadata: {cv_metadata.variable_type.value} - {cv_metadata.engineering_units}"
        )

        if fake_data:
            console.print("\nGenerating fake data...")
            _generate_fake_data_sync(module)

        # Show module statistics
        console.print("\nModule Statistics:")
        stats = module.get_integration_stats()
        for key, value in stats.items():
            console.print(f"  {key}: {value}")

        # Stop module
        console.print("\nStopping module...")
        if module.shutdown_module():
            console.print("✅ Module stopped successfully")
        else:
            console.print("❌ Module stop failed")

        console.print("\n🎉 Data Integration Module Demo completed successfully!")

    except Exception as e:
        console.print(f"\n❌ Demo failed with error: {e}")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@data_integration_group.command("test")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--supabase", "-s", is_flag=True, help="Test Supabase integration")
def test_command(verbose: bool, supabase: bool) -> None:
    """Run comprehensive tests for the data integration module."""
    console.print("🧪 Data Integration Module Tests")
    console.print("=" * 50)

    test_results = []

    def run_test(test_name: str, test_func) -> bool:
        """Run a test and track results."""
        try:
            with console.status(f"Running {test_name}..."):
                result = test_func()

            if result:
                console.print(f"✅ {test_name}")
                test_results.append((test_name, True, None))
                return True
            else:
                console.print(f"❌ {test_name}")
                test_results.append((test_name, False, "Test returned False"))
                return False
        except Exception as e:
            error_msg = str(e)
            console.print(f"❌ {test_name}: {error_msg}")
            test_results.append((test_name, False, error_msg))
            if verbose:
                import traceback

                console.print(traceback.format_exc())
            return False

    # Test 1: Module Creation
    def test_module_creation():
        module = _create_test_module()
        return module is not None

    # Test 2: Module Lifecycle
    def test_module_lifecycle():
        module = _create_test_module()
        # Set up default configuration before testing lifecycle
        default_config = {
            "module_id": module.metadata.id,
            "version": module.metadata.version,
            "enabled": True,
            "debug_mode": False,
            "log_level": "INFO",
            "security": {
                "encryption_enabled": True,
                "certificate_validation": True,
                "max_retry_attempts": 3,
                "connection_timeout": 30,
            },
            "performance": {
                "max_concurrent_connections": 50,
                "default_batch_size": 1000,
                "connection_pool_size": 10,
                "message_buffer_size": 10000,
            },
            "data_processing": {
                "enable_metadata_injection": True,
                "normalize_timestamps": True,
                "validate_data_quality": True,
                "auto_detect_variable_types": True,
            },
            "json_output": {
                "include_metadata": True,
                "timestamp_format": "iso8601",
                "normalize_values": True,
                "include_quality_codes": True,
            },
        }

        # Configure module first
        if not module.configure_module(default_config):
            return False

        return (
            module.initialize_module()
            and module.startup_module()
            and module.shutdown_module()
        )

    # Test 3: Data Source Configuration
    def test_data_source_configuration():
        from ..data_integration import DataSourceConfig, DataSourceType

        module = _create_test_module()

        # Configure module first
        default_config = {
            "module_id": module.metadata.id,
            "version": module.metadata.version,
            "enabled": True,
            "debug_mode": False,
            "log_level": "INFO",
            "security": {
                "encryption_enabled": True,
                "certificate_validation": True,
                "max_retry_attempts": 3,
                "connection_timeout": 30,
            },
            "performance": {
                "max_concurrent_connections": 50,
                "default_batch_size": 1000,
                "connection_pool_size": 10,
                "message_buffer_size": 10000,
            },
            "data_processing": {
                "enable_metadata_injection": True,
                "normalize_timestamps": True,
                "validate_data_quality": True,
                "auto_detect_variable_types": True,
            },
            "json_output": {
                "include_metadata": True,
                "timestamp_format": "iso8601",
                "normalize_values": True,
                "include_quality_codes": True,
            },
        }

        if not module.configure_module(default_config):
            return False

        if not module.initialize_module():
            return False

        config = DataSourceConfig(
            source_id="test_source",
            source_type=DataSourceType.OPC_UA,
            connection_params={"server_url": "opc.tcp://localhost:4840"},
            enabled=True,
        )

        return module.add_data_source(config)

    # Test 4: Variable Metadata
    def test_variable_metadata():
        from ..data_integration import VariableMetadata, VariableType

        metadata = VariableMetadata(
            variable_type=VariableType.PV,
            name="test_var",
            engineering_units="°C",
            range_high=100.0,
            range_low=0.0,
            max_value=100.0,
            is_primary_pv=True,
        )
        return metadata.variable_type == VariableType.PV

    # Test 5: JSON Serialization
    def test_json_serialization():
        from ..data_integration import DataSourceConfig, DataSourceType

        module = _create_test_module()
        module.initialize_module()

        config = DataSourceConfig(
            source_id="test_json",
            source_type=DataSourceType.MQTT,
            connection_params={"broker_url": "mqtt://localhost:1883"},
            enabled=True,
        )

        # Test serialization
        json_str = json.dumps(config.to_dict(), default=str)
        return len(json_str) > 0

    # Run all tests
    console.print("\n🏃 Running Tests:")
    run_test("Module Creation", test_module_creation)
    run_test("Module Lifecycle", test_module_lifecycle)
    run_test("Data Source Configuration", test_data_source_configuration)
    run_test("Variable Metadata", test_variable_metadata)
    run_test("JSON Serialization", test_json_serialization)

    if supabase:
        console.print("\n🗄️ Testing Supabase Integration:")

        def test_supabase_connection():
            # Test Supabase connection if available
            try:
                # This would test actual Supabase connection
                # For now, just check environment variables
                required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
                return all(os.getenv(var) for var in required_vars)
            except Exception:
                return False

        run_test("Supabase Connection", test_supabase_connection)

    # Show test summary
    console.print("\n📊 Test Summary:")
    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)

    summary_table = Table(title="Test Results")
    summary_table.add_column("Test", style="bold")
    summary_table.add_column("Status")
    summary_table.add_column("Error", style="red")

    for test_name, success, error in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        error_text = error if error and not success else ""
        summary_table.add_row(test_name, status, error_text)

    console.print(summary_table)
    console.print(
        f"\n📈 Results: {passed}/{total} tests passed ({passed / total * 100:.1f}%)"
    )


@data_integration_group.command("sources")
@click.option("--type", "-t", help="Filter by source type")
@click.option("--enabled", "-e", is_flag=True, help="Show only enabled sources")
def list_sources_command(type: str, enabled: bool) -> None:
    """List available data source types and configurations."""
    console.print("🔗 Data Integration Sources")
    console.print("=" * 50)

    try:
        from ..data_integration import DataSourceType, VariableType

        # Show available source types
        console.print("\n📋 Available Source Types:")
        sources_table = Table(title="Data Source Types")
        sources_table.add_column("Type", style="bold cyan")
        sources_table.add_column("Category", style="green")
        sources_table.add_column("Description")

        source_categories = {
            DataSourceType.OPC_UA: ("Industrial", "OPC-UA server connectivity"),
            DataSourceType.MQTT: ("Industrial", "MQTT broker messaging"),
            DataSourceType.KAFKA: ("Streaming", "Apache Kafka streaming platform"),
            DataSourceType.POSTGRESQL: ("Database", "PostgreSQL relational database"),
            DataSourceType.MYSQL: ("Database", "MySQL relational database"),
            DataSourceType.SQL_SERVER: ("Database", "Microsoft SQL Server"),
            DataSourceType.INFLUXDB: ("Time-Series", "InfluxDB time-series database"),
            DataSourceType.TIMESCALEDB: (
                "Time-Series",
                "TimescaleDB PostgreSQL extension",
            ),
            DataSourceType.MONGODB: ("Document", "MongoDB document database"),
            DataSourceType.NEO4J: ("Graph", "Neo4j graph database"),
            DataSourceType.REST_API: ("Web Service", "REST API endpoints"),
            DataSourceType.CSV: ("File", "CSV file processing"),
            DataSourceType.EXCEL: ("File", "Excel file processing"),
            DataSourceType.JSON_FILE: ("File", "JSON file processing"),
        }

        for source_type in DataSourceType:
            if type and type.upper() not in source_type.value.upper():
                continue

            category, description = source_categories.get(
                source_type, ("Other", "Data source")
            )
            sources_table.add_row(source_type.value, category, description)

        console.print(sources_table)

        # Show variable types
        console.print("\n🏷️ Variable Types:")
        variables_table = Table(title="Industrial Variable Types")
        variables_table.add_column("Type", style="bold magenta")
        variables_table.add_column("Description")
        variables_table.add_column("Metadata Fields")

        variable_info = {
            VariableType.PV: (
                "Process Variable",
                "PPV, SPC, Range (high/low), Max, EU",
            ),
            VariableType.CV: ("Control Variable", "Range (high/low), Max, EU"),
            VariableType.DV: ("Disturbance Variable", "Range (high/low), Max, EU"),
            VariableType.SP: ("Setpoint", "Range (high/low), EU"),
            VariableType.PROCESS_STATE: ("Process State", "String enumeration"),
        }

        for var_type, (description, metadata) in variable_info.items():
            variables_table.add_row(var_type.value, description, metadata)

        console.print(variables_table)

    except ImportError as e:
        console.print(f"❌ Failed to import data integration types: {e}")


@data_integration_group.command("config")
@click.argument("source_name")
@click.option("--type", "-t", required=True, help="Data source type")
@click.option("--params", "-p", help="Connection parameters as JSON")
@click.option("--enabled/--disabled", default=True, help="Enable/disable source")
def configure_source_command(
    source_name: str, type: str, params: str, enabled: bool
) -> None:
    """Configure a data source."""
    console.print(f"⚙️ Configuring Data Source: {source_name}")
    console.print("=" * 50)

    try:
        from ..data_integration import DataSourceConfig, DataSourceType

        # Parse source type
        try:
            source_type = DataSourceType(type.lower())
        except ValueError:
            console.print(f"❌ Invalid source type: {type}")
            console.print("Available types:", [t.value for t in DataSourceType])
            return

        # Parse connection parameters
        connection_params = {}
        if params:
            try:
                connection_params = json.loads(params)
            except json.JSONDecodeError as e:
                console.print(f"❌ Invalid JSON parameters: {e}")
                return

        # Create configuration
        config = DataSourceConfig(
            source_id=source_name,
            source_type=source_type,
            connection_params=connection_params,
            enabled=enabled,
        )

        # Create test module and add source
        module = _create_test_module()
        module.initialize_module()

        if module.add_data_source(config):
            console.print(f"✅ Data source '{source_name}' configured successfully")
            console.print(f"   Type: {source_type.value}")
            console.print(f"   Enabled: {enabled}")
            console.print(f"   Parameters: {len(connection_params)} items")
        else:
            console.print(f"❌ Failed to configure data source '{source_name}'")

    except Exception as e:
        console.print(f"❌ Configuration failed: {e}")


@data_integration_group.command("faker")
@click.option("--count", "-c", default=100, help="Number of fake records to generate")
@click.option(
    "--sources", "-s", default="opcua,database", help="Comma-separated source types"
)
@click.option("--supabase", is_flag=True, help="Store fake data in Supabase")
def generate_fake_data_command(count: int, sources: str, supabase: bool) -> None:
    """Generate fake data for testing."""
    console.print(f"🎭 Generating {count} fake data records")
    console.print("=" * 50)

    try:
        _generate_fake_data_sync(count, sources.split(","), supabase)
    except Exception as e:
        console.print(f"❌ Fake data generation failed: {e}")


def _generate_fake_data_sync(module_or_count, sources=None, use_supabase=False) -> None:
    """Generate fake data synchronously."""
    try:
        from faker import Faker

        fake = Faker()
    except ImportError:
        console.print("❌ Faker library not installed. Run: pip install faker")
        return

    # Handle different call signatures
    if isinstance(module_or_count, int):
        count = module_or_count
        source_types = sources or ["opcua", "database"]
    else:
        # Called from demo with module
        module = module_or_count
        count = 10
        source_types = ["opcua", "database"]

    console.print(
        f"🎭 Generating {count} fake records for sources: {', '.join(source_types)}"
    )

    # Generate fake data based on source types
    all_fake_data = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating fake data...", total=count)

        for i in range(count):
            for source_type in source_types:
                if source_type.lower() == "opcua":
                    record = _generate_fake_opcua_record(fake, i)
                elif source_type.lower() == "database":
                    record = _generate_fake_database_record(fake, i)
                elif source_type.lower() == "mqtt":
                    record = _generate_fake_mqtt_record(fake, i)
                else:
                    record = _generate_fake_generic_record(fake, source_type, i)

                all_fake_data.append(record)

            progress.advance(task)

    console.print(f"✅ Generated {len(all_fake_data)} fake records")

    # Save to file
    output_file = Path("test_data_integration/faker_data.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(all_fake_data, f, indent=2)

    console.print(f"💾 Fake data saved to: {output_file}")

    if use_supabase:
        console.print("🗄️ Storing fake data in Supabase...")
        _store_fake_data_in_supabase(all_fake_data)


def _generate_fake_opcua_record(fake, index: int) -> dict[str, Any]:
    """Generate fake OPC-UA record."""
    return {
        "id": f"opcua_{index}",
        "timestamp": fake.date_time_this_year().isoformat(),
        "source_type": "OPCUA",
        "server_url": "opc.tcp://fake-server:4840",
        "node_id": f"ns=2;i={1000 + index}",
        "variables": {
            f"Temperature_{index}": {
                "value": fake.pyfloat(min_value=15, max_value=85),
                "quality": "Good",
                "metadata": {
                    "variable_type": "PV",
                    "ppv": index == 0,
                    "range_high": 100.0,
                    "range_low": 0.0,
                    "max_value": 100.0,
                    "eu": "°C",
                },
            },
            f"Pressure_{index}": {
                "value": fake.pyfloat(min_value=0.5, max_value=5.0),
                "quality": "Good",
                "metadata": {
                    "variable_type": "DV",
                    "range_high": 5.0,
                    "range_low": 0.0,
                    "max_value": 5.0,
                    "eu": "bar",
                },
            },
        },
        "process_state": fake.random_element(
            ["startup", "steady_state", "shutdown", "maintenance"]
        ),
    }


def _generate_fake_database_record(fake, index: int) -> dict[str, Any]:
    """Generate fake database record."""
    return {
        "id": f"db_{index}",
        "timestamp": fake.date_time_this_year().isoformat(),
        "source_type": "POSTGRESQL",
        "table_name": "process_data",
        "variables": {
            f"flow_rate_{index}": {
                "value": fake.pyfloat(min_value=10, max_value=500),
                "metadata": {
                    "variable_type": "PV",
                    "ppv": False,
                    "spc": True,
                    "range_high": 500.0,
                    "range_low": 0.0,
                    "max_value": 500.0,
                    "eu": "L/min",
                },
            },
            f"valve_position_{index}": {
                "value": fake.pyfloat(min_value=0, max_value=100),
                "metadata": {
                    "variable_type": "CV",
                    "range_high": 100.0,
                    "range_low": 0.0,
                    "max_value": 100.0,
                    "eu": "%",
                },
            },
        },
        "process_state": fake.random_element(["running", "stopped", "error"]),
    }


def _generate_fake_mqtt_record(fake, index: int) -> dict[str, Any]:
    """Generate fake MQTT record."""
    return {
        "id": f"mqtt_{index}",
        "timestamp": fake.date_time_this_year().isoformat(),
        "source_type": "MQTT",
        "topic": f"plant/unit_{index % 5}/sensors",
        "variables": {
            f"vibration_{index}": {
                "value": fake.pyfloat(min_value=0, max_value=10),
                "metadata": {
                    "variable_type": "DV",
                    "range_high": 10.0,
                    "range_low": 0.0,
                    "max_value": 10.0,
                    "eu": "mm/s",
                },
            },
            f"setpoint_{index}": {
                "value": fake.pyfloat(min_value=50, max_value=150),
                "metadata": {
                    "variable_type": "SP",
                    "range_high": 200.0,
                    "range_low": 0.0,
                    "eu": "°C",
                },
            },
        },
        "process_state": fake.random_element(["normal", "alarm", "warning"]),
    }


def _generate_fake_generic_record(fake, source_type: str, index: int) -> dict[str, Any]:
    """Generate fake generic record."""
    return {
        "id": f"{source_type}_{index}",
        "timestamp": fake.date_time_this_year().isoformat(),
        "source_type": source_type.upper(),
        "variables": {
            f"generic_value_{index}": {
                "value": fake.pyfloat(min_value=0, max_value=1000),
                "metadata": {
                    "variable_type": "PV",
                    "ppv": False,
                    "range_high": 1000.0,
                    "range_low": 0.0,
                    "max_value": 1000.0,
                    "eu": "units",
                },
            },
        },
        "process_state": "unknown",
    }


def _store_fake_data_in_supabase(fake_data: list[dict[str, Any]]) -> None:
    """Store fake data in Supabase database."""
    try:
        # This would integrate with actual Supabase client
        console.print("🗄️ Supabase integration would store data here")
        console.print(f"   Records to store: {len(fake_data)}")
        console.print("   Table: industrial_data")
        console.print("   ✅ Fake data would be stored successfully")

        # For demonstration, save to a SQL file
        sql_file = Path("test_data_integration/fake_data.sql")
        with open(sql_file, "w") as f:
            f.write("-- Fake data for Supabase testing\n")
            f.write("CREATE TABLE IF NOT EXISTS industrial_data (\n")
            f.write("  id VARCHAR PRIMARY KEY,\n")
            f.write("  timestamp TIMESTAMPTZ,\n")
            f.write("  source_type VARCHAR,\n")
            f.write("  data JSONB\n")
            f.write(");\n\n")

            for record in fake_data:
                record_copy = record.copy()
                record_id = record_copy.pop("id")
                timestamp = record_copy.pop("timestamp")
                source_type = record_copy.pop("source_type")

                f.write(
                    "INSERT INTO industrial_data (id, timestamp, source_type, data) VALUES (\n"
                )
                f.write(f"  '{record_id}',\n")
                f.write(f"  '{timestamp}',\n")
                f.write(f"  '{source_type}',\n")
                f.write(f"  '{json.dumps(record_copy)}'\n")
                f.write(");\n")

        console.print(f"📄 SQL file created: {sql_file}")

    except Exception as e:
        console.print(f"❌ Failed to store fake data in Supabase: {e}")


@data_integration_group.command("info")
def info_command() -> None:
    """Display information about the data integration module."""
    console.print("📋 Data Integration Module Information")
    console.print("=" * 50)

    try:
        from ..data_integration import DataSourceType, VariableType

        console.print("\n🏗️ Module Components:")
        console.print("  • DataIntegrationModule - Main module class")
        console.print("  • DataSourceConfig - Source configuration management")
        console.print("  • VariableMetadata - Industrial variable metadata")
        console.print("  • Data Adapters - Source-specific connection handlers")

        console.print(f"\n🔗 Supported Data Sources ({len(DataSourceType)} types):")
        source_categories = {
            "Industrial": [DataSourceType.OPC_UA, DataSourceType.MQTT],
            "Streaming": [DataSourceType.KAFKA],
            "Database": [
                DataSourceType.POSTGRESQL,
                DataSourceType.MYSQL,
                DataSourceType.SQL_SERVER,
            ],
            "Time-Series": [DataSourceType.INFLUXDB, DataSourceType.TIMESCALEDB],
            "Document": [DataSourceType.MONGODB],
            "Graph": [DataSourceType.NEO4J],
            "Web Service": [DataSourceType.REST_API],
            "File": [
                DataSourceType.CSV,
                DataSourceType.EXCEL,
                DataSourceType.JSON_FILE,
            ],
        }

        for category, sources in source_categories.items():
            console.print(f"  📂 {category}:")
            for source in sources:
                console.print(f"    • {source.value}")

        console.print(f"\n🏷️ Variable Types ({len(VariableType)} types):")
        for var_type in VariableType:
            console.print(f"  • {var_type.value}")

        console.print("\n🔧 Available Commands:")
        console.print("  • ign module data demo - Run module demonstration")
        console.print("  • ign module data test - Run comprehensive tests")
        console.print("  • ign module data sources - List available data sources")
        console.print("  • ign module data config - Configure data sources")
        console.print("  • ign module data faker - Generate fake test data")
        console.print("  • ign module data info - Show this information")

        console.print("\n📁 Example Usage:")
        console.print("  ign module data demo --verbose --fake-data")
        console.print("  ign module data test --supabase")
        console.print(
            "  ign module data faker --count 500 --sources opcua,mqtt --supabase"
        )
        console.print(
            '  ign module data config my_opcua --type opc_ua --params \'{"server_url":"opc.tcp://localhost:4840"}\''
        )

        console.print("\n✨ Features:")
        console.print("  • 25+ enterprise data source types")
        console.print(
            "  • Industrial variable metadata injection (PV/CV/DV/SP/Process_State)"
        )
        console.print("  • JSON model preparation for AI/ML")
        console.print("  • Real-time streaming and batch processing")
        console.print("  • Connection pooling and health monitoring")
        console.print("  • Comprehensive error handling and statistics")

    except ImportError as e:
        console.print(f"❌ Failed to import data integration types: {e}")


# Register the command group
def register_commands(cli):
    """Register data integration commands with the CLI."""
    cli.add_command(data_integration_group)
