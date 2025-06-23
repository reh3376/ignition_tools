"""Phase 9.8: Advanced Module Features CLI Commands
===============================================

Following crawl_mcp.py methodology for systematic development:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling with User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity
6. Resource Management

This module provides CLI commands for advanced features:
- Analytics module commands
- Security module commands
- Integration hub commands
- Comprehensive testing and validation
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from ignition.modules.advanced_features.analytics_module import (
    AnalyticsConfig,
    RealTimeAnalyticsModule,
)
from ignition.modules.advanced_features.integration_hub import (
    IntegrationConfig,
    IntegrationHubModule,
)
from ignition.modules.advanced_features.security_module import (
    SecurityComplianceModule,
    SecurityConfig,
)

# Initialize console
console = Console()


# Create CLI group for advanced features
@click.group(name="advanced")
@click.pass_context
def advanced_features_cli(ctx):
    """Phase 9.8 Advanced Module Features

    Following crawl_mcp.py methodology for systematic command execution:
    - Environment validation first
    - Comprehensive input validation
    - User-friendly error handling
    - Progressive complexity
    """
    ctx.ensure_object(dict)
    console.print("🚀 Phase 9.8 Advanced Module Features CLI", style="blue bold")


# Analytics Module Commands
@advanced_features_cli.group(name="analytics")
@click.pass_context
def analytics_commands(ctx):
    """Real-time Analytics Module commands."""
    console.print("📊 Analytics Module Commands", style="green")


@analytics_commands.command(name="validate-env")
@click.option(
    "--complexity",
    default="basic",
    type=click.Choice(["basic", "intermediate", "advanced"]),
    help="Analytics complexity level",
)
@click.option("--show-details", is_flag=True, help="Show detailed validation results")
def validate_analytics_environment(complexity: str, show_details: bool):
    """Validate analytics environment following crawl_mcp.py methodology.

    Step 1: Environment Variable Validation First
    """
    try:
        console.print(
            Panel.fit(
                "📊 Analytics Environment Validation\nFollowing crawl_mcp.py methodology",
                style="green",
            )
        )

        # Initialize analytics module
        config = AnalyticsConfig(complexity_level=complexity)
        module = RealTimeAnalyticsModule(config)

        # Display validation results
        if show_details:
            validation_results = module.environment_validation

            table = Table(title="Detailed Analytics Validation")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details", style="dim")

            for component, result in validation_results.items():
                status = "✅ Valid" if result.valid else "❌ Invalid"
                details = result.warning or result.error or "OK"
                table.add_row(component.replace("_", " ").title(), status, details)

            console.print(table)

        # Generate report
        report = module.generate_analytics_report()
        if report["success"]:
            console.print("✅ Analytics environment validation complete", style="green")
            console.print(f"📋 Complexity Level: {complexity}", style="dim")
            console.print(
                f"🔧 Components Active: {sum(report['report']['components'].values())}",
                style="dim",
            )
        else:
            console.print(f"❌ Validation failed: {report['error']}", style="red")
            return

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during analytics validation: {e!s}", style="red")
        console.print(
            "💡 Suggestion: Check Python environment and dependencies", style="yellow"
        )


@analytics_commands.command(name="process-data")
@click.option(
    "--data-file", type=click.Path(exists=True), help="JSON file with data to process"
)
@click.option(
    "--complexity",
    default="basic",
    type=click.Choice(["basic", "intermediate", "advanced"]),
    help="Analytics complexity level",
)
@click.option("--output-file", type=click.Path(), help="Output file for results")
def process_analytics_data(
    data_file: str | None, complexity: str, output_file: str | None
):
    """Process analytics data following crawl_mcp.py methodology.

    Step 2: Comprehensive Input Validation
    """
    try:
        console.print("📊 Processing Analytics Data", style="green")

        # Initialize analytics module
        config = AnalyticsConfig(complexity_level=complexity)
        module = RealTimeAnalyticsModule(config)

        # Load data
        if data_file:
            with open(data_file) as f:
                data = json.load(f)
        else:
            # Use sample data
            data = {
                "timestamp": datetime.now().isoformat(),
                "values": {"temperature": 25.5, "pressure": 101.3, "humidity": 60.2},
            }

        # Process data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing data...", total=None)

            result = module.process_data(data)

            progress.update(task, completed=True)

        if result["success"]:
            console.print("✅ Data processing completed", style="green")

            # Display results
            if "result" in result:
                result_table = Table(title="Processing Results")
                result_table.add_column("Metric", style="cyan")
                result_table.add_column("Value", style="green")

                for key, value in result["result"].items():
                    if isinstance(value, (int, float)):
                        value = f"{value:.2f}"
                    result_table.add_row(key.replace("_", " ").title(), str(value))

                console.print(result_table)

            # Save results if requested
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                console.print(f"💾 Results saved to {output_file}", style="dim")
        else:
            console.print(f"❌ Data processing failed: {result['error']}", style="red")
            if "suggestions" in result:
                for suggestion in result["suggestions"]:
                    console.print(f"💡 {suggestion}", style="yellow")

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during data processing: {e!s}", style="red")


# Security Module Commands
@advanced_features_cli.group(name="security")
@click.pass_context
def security_commands(ctx):
    """Security and Compliance Module commands."""
    console.print("🔒 Security Module Commands", style="red")


@security_commands.command(name="validate-env")
@click.option(
    "--security-level",
    default="standard",
    type=click.Choice(["basic", "standard", "high", "critical"]),
    help="Security level",
)
@click.option("--show-details", is_flag=True, help="Show detailed validation results")
def validate_security_environment(security_level: str, show_details: bool):
    """Validate security environment following crawl_mcp.py methodology.

    Step 1: Environment Variable Validation First
    """
    try:
        console.print(
            Panel.fit(
                "🔒 Security Environment Validation\nFollowing crawl_mcp.py methodology",
                style="red",
            )
        )

        # Initialize security module
        config = SecurityConfig(security_level=security_level)
        module = SecurityComplianceModule(config)

        # Display validation results
        if show_details:
            validation_results = module.environment_validation

            table = Table(title="Detailed Security Validation")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Security Level", style="yellow")
            table.add_column("Details", style="dim")

            for component, result in validation_results.items():
                status = "✅ Valid" if result.valid else "❌ Invalid"
                security_level_display = result.security_level.upper()
                details = result.warning or result.error or "OK"
                table.add_row(
                    component.replace("_", " ").title(),
                    status,
                    security_level_display,
                    details,
                )

            console.print(table)

        # Generate security report
        report = module.generate_security_report()
        if report["success"]:
            console.print("✅ Security environment validation complete", style="green")
            console.print(f"🔒 Security Level: {security_level}", style="dim")
            console.print(
                f"🔧 Components Active: {sum(report['report']['components'].values())}",
                style="dim",
            )
        else:
            console.print(f"❌ Validation failed: {report['error']}", style="red")
            return

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during security validation: {e!s}", style="red")
        console.print(
            "💡 Suggestion: Check security dependencies and permissions", style="yellow"
        )


@security_commands.command(name="log-event")
@click.option("--event-type", required=True, help="Type of security event")
@click.option("--user-id", required=True, help="User ID associated with event")
@click.option("--source-ip", default="127.0.0.1", help="Source IP address")
@click.option(
    "--severity",
    default="info",
    type=click.Choice(["info", "warning", "error", "critical"]),
    help="Event severity",
)
@click.option("--details", help="Additional event details (JSON string)")
def log_security_event(
    event_type: str, user_id: str, source_ip: str, severity: str, details: str | None
):
    """Log security event following crawl_mcp.py methodology.

    Step 2: Comprehensive Input Validation
    """
    try:
        console.print("🔒 Logging Security Event", style="red")

        # Initialize security module
        config = SecurityConfig()
        module = SecurityComplianceModule(config)

        # Prepare event data
        event_data = {
            "event_type": event_type,
            "user_id": user_id,
            "source_ip": source_ip,
            "severity": severity,
        }

        # Parse additional details if provided
        if details:
            try:
                event_data["details"] = json.loads(details)
            except json.JSONDecodeError:
                console.print(
                    "⚠️ Invalid JSON in details, using as string", style="yellow"
                )
                event_data["details"] = {"raw": details}

        # Log event
        result = module.log_security_event(event_data)

        if result["success"]:
            console.print("✅ Security event logged successfully", style="green")
            console.print(
                f"📋 Event ID: {result.get('event_id', 'unknown')}", style="dim"
            )
            console.print(f"⏰ Timestamp: {result['timestamp']}", style="dim")
        else:
            console.print(f"❌ Event logging failed: {result['error']}", style="red")
            if "suggestions" in result:
                for suggestion in result["suggestions"]:
                    console.print(f"💡 {suggestion}", style="yellow")

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during event logging: {e!s}", style="red")


@security_commands.command(name="compliance-check")
@click.option("--standard", default="general", help="Compliance standard to check")
@click.option(
    "--output-file", type=click.Path(), help="Output file for compliance report"
)
def run_compliance_check(standard: str, output_file: str | None):
    """Run compliance check following crawl_mcp.py methodology."""
    try:
        console.print(f"🔒 Running Compliance Check: {standard.upper()}", style="red")

        # Initialize security module
        config = SecurityConfig()
        module = SecurityComplianceModule(config)

        # Run compliance check
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running compliance checks...", total=None)

            result = module.run_compliance_check(standard)

            progress.update(task, completed=True)

        if result["success"]:
            console.print("✅ Compliance check completed", style="green")

            # Display results
            checks = result.get("checks", [])
            if checks:
                compliance_table = Table(
                    title=f"Compliance Check Results: {standard.upper()}"
                )
                compliance_table.add_column("Check", style="cyan")
                compliance_table.add_column("Status", style="green")
                compliance_table.add_column("Details", style="dim")

                for check in checks:
                    status = "✅ Passed" if check["passed"] else "❌ Failed"
                    compliance_table.add_row(check["name"], status, check["details"])

                console.print(compliance_table)

                # Show recommendations for failed checks
                failed_checks = [c for c in checks if not c["passed"]]
                if failed_checks:
                    console.print("\n💡 Recommendations:", style="yellow")
                    for check in failed_checks:
                        for rec in check.get("recommendations", []):
                            console.print(f"  • {rec}", style="yellow")

            # Save results if requested
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                console.print(
                    f"💾 Compliance report saved to {output_file}", style="dim"
                )
        else:
            console.print(f"❌ Compliance check failed: {result['error']}", style="red")

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during compliance check: {e!s}", style="red")


# Integration Hub Commands
@advanced_features_cli.group(name="integration")
@click.pass_context
def integration_commands(ctx):
    """Integration Hub Module commands."""
    console.print("🔌 Integration Hub Commands", style="cyan")


@integration_commands.command(name="validate-env")
@click.option(
    "--integration-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Integration level",
)
@click.option("--show-details", is_flag=True, help="Show detailed validation results")
def validate_integration_environment(integration_level: str, show_details: bool):
    """Validate integration environment following crawl_mcp.py methodology.

    Step 1: Environment Variable Validation First
    """
    try:
        console.print(
            Panel.fit(
                "🔌 Integration Environment Validation\nFollowing crawl_mcp.py methodology",
                style="cyan",
            )
        )

        # Initialize integration module
        config = IntegrationConfig(integration_level=integration_level)
        module = IntegrationHubModule(config)

        # Display validation results
        if show_details:
            validation_results = module.environment_validation

            table = Table(title="Detailed Integration Validation")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Integration Status", style="yellow")
            table.add_column("Details", style="dim")

            for component, result in validation_results.items():
                status = "✅ Valid" if result.valid else "❌ Invalid"
                integration_status = result.integration_status.upper()
                details = result.warning or result.error or "OK"
                table.add_row(
                    component.replace("_", " ").title(),
                    status,
                    integration_status,
                    details,
                )

            console.print(table)

        # Generate integration report
        report = module.generate_integration_report()
        if report["success"]:
            console.print(
                "✅ Integration environment validation complete", style="green"
            )
            console.print(f"🔌 Integration Level: {integration_level}", style="dim")
            console.print(
                f"🔧 Components Active: {sum(report['report']['components'].values())}",
                style="dim",
            )
        else:
            console.print(f"❌ Validation failed: {report['error']}", style="red")
            return

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during integration validation: {e!s}", style="red")
        console.print(
            "💡 Suggestion: Check network connectivity and dependencies", style="yellow"
        )


@integration_commands.command(name="register-endpoint")
@click.option("--name", required=True, help="API endpoint name")
@click.option("--url", required=True, help="API endpoint URL")
@click.option("--method", default="GET", help="HTTP method")
@click.option(
    "--auth-type",
    default="none",
    type=click.Choice(["none", "basic", "bearer", "api_key"]),
    help="Authentication type",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="JSON file with endpoint configuration",
)
def register_api_endpoint(
    name: str, url: str, method: str, auth_type: str, config_file: str | None
):
    """Register API endpoint following crawl_mcp.py methodology.

    Step 2: Comprehensive Input Validation
    """
    try:
        console.print("🔌 Registering API Endpoint", style="cyan")

        # Initialize integration module
        config = IntegrationConfig()
        module = IntegrationHubModule(config)

        # Prepare endpoint configuration
        if config_file:
            with open(config_file) as f:
                endpoint_config = json.load(f)
        else:
            endpoint_config = {
                "name": name,
                "url": url,
                "method": method.upper(),
                "auth_type": auth_type,
            }

        # Register endpoint
        result = module.register_api_endpoint(endpoint_config)

        if result["success"]:
            console.print("✅ API endpoint registered successfully", style="green")
            console.print(f"📋 Endpoint Name: {result['endpoint_name']}", style="dim")
            console.print(f"🌐 Endpoint URL: {result['endpoint_url']}", style="dim")
            console.print(f"⏰ Registered: {result['timestamp']}", style="dim")
        else:
            console.print(
                f"❌ Endpoint registration failed: {result['error']}", style="red"
            )
            if "suggestions" in result:
                for suggestion in result["suggestions"]:
                    console.print(f"💡 {suggestion}", style="yellow")

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during endpoint registration: {e!s}", style="red")


@integration_commands.command(name="process-webhook")
@click.option(
    "--webhook-file", type=click.Path(exists=True), help="JSON file with webhook data"
)
@click.option("--source", default="unknown", help="Webhook source system")
@click.option("--event", help="Event type")
def process_webhook_data(webhook_file: str | None, source: str, event: str | None):
    """Process webhook data following crawl_mcp.py methodology."""
    try:
        console.print("🔌 Processing Webhook Data", style="cyan")

        # Initialize integration module
        config = IntegrationConfig()
        module = IntegrationHubModule(config)

        # Load webhook data
        if webhook_file:
            with open(webhook_file) as f:
                webhook_data = json.load(f)
        else:
            webhook_data = {
                "source": source,
                "event": event or "test_event",
                "timestamp": datetime.now().isoformat(),
                "data": {"message": "Test webhook data"},
            }

        # Process webhook
        result = module.process_webhook(webhook_data)

        if result["success"]:
            console.print("✅ Webhook processed successfully", style="green")
            console.print(
                f"📋 Source: {webhook_data.get('source', 'unknown')}", style="dim"
            )
            console.print(
                f"🔔 Event: {webhook_data.get('event', 'unknown')}", style="dim"
            )
        else:
            console.print(
                f"❌ Webhook processing failed: {result['error']}", style="red"
            )
            if "suggestions" in result:
                for suggestion in result["suggestions"]:
                    console.print(f"💡 {suggestion}", style="yellow")

        # Cleanup
        module.cleanup_resources()

    except Exception as e:
        console.print(f"❌ Error during webhook processing: {e!s}", style="red")


# Comprehensive Testing Commands
@advanced_features_cli.command(name="test-all")
@click.option("--complexity", default="basic", help="Test complexity level")
@click.option("--output-file", type=click.Path(), help="Output file for test results")
@click.option("--verbose", is_flag=True, help="Verbose test output")
def test_all_modules(complexity: str, output_file: str | None, verbose: bool):
    """Test all Phase 9.8 modules following crawl_mcp.py methodology.

    Step 4: Modular Component Testing
    """
    try:
        console.print(
            Panel.fit(
                "🧪 Phase 9.8 Comprehensive Module Testing\nFollowing crawl_mcp.py methodology",
                style="magenta bold",
            )
        )

        test_results = {
            "timestamp": datetime.now().isoformat(),
            "methodology": "crawl_mcp.py systematic approach",
            "test_results": {},
        }

        # Test Analytics Module
        console.print("\n📊 Testing Analytics Module", style="green")
        try:
            analytics_config = AnalyticsConfig(complexity_level=complexity)
            analytics_module = RealTimeAnalyticsModule(analytics_config)

            # Test data processing
            test_data = {
                "timestamp": datetime.now().isoformat(),
                "values": {"temperature": 25.5, "pressure": 101.3},
            }
            analytics_result = analytics_module.process_data(test_data)

            test_results["test_results"]["analytics"] = {
                "environment_validation": all(
                    r.valid for r in analytics_module.environment_validation.values()
                ),
                "data_processing": analytics_result["success"],
                "components_initialized": analytics_module.data_processor is not None,
            }

            analytics_module.cleanup_resources()
            console.print("✅ Analytics module test completed", style="green")

        except Exception as e:
            test_results["test_results"]["analytics"] = {"error": str(e)}
            console.print(f"❌ Analytics module test failed: {e!s}", style="red")

        # Test Security Module
        console.print("\n🔒 Testing Security Module", style="red")
        try:
            security_config = SecurityConfig(security_level=complexity)
            security_module = SecurityComplianceModule(security_config)

            # Test event logging
            test_event = {
                "event_type": "test_event",
                "user_id": "test_user",
                "source_ip": "127.0.0.1",
            }
            security_result = security_module.log_security_event(test_event)

            # Test compliance check
            compliance_result = security_module.run_compliance_check("general")

            test_results["test_results"]["security"] = {
                "environment_validation": all(
                    r.valid for r in security_module.environment_validation.values()
                ),
                "event_logging": security_result["success"],
                "compliance_checking": compliance_result["success"],
                "components_initialized": security_module.audit_logger is not None,
            }

            security_module.cleanup_resources()
            console.print("✅ Security module test completed", style="green")

        except Exception as e:
            test_results["test_results"]["security"] = {"error": str(e)}
            console.print(f"❌ Security module test failed: {e!s}", style="red")

        # Test Integration Hub
        console.print("\n🔌 Testing Integration Hub", style="cyan")
        try:
            integration_config = IntegrationConfig(integration_level=complexity)
            integration_module = IntegrationHubModule(integration_config)

            # Test endpoint registration
            test_endpoint = {
                "name": "test_endpoint",
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "method": "GET",
            }
            endpoint_result = integration_module.register_api_endpoint(test_endpoint)

            # Test webhook processing
            test_webhook = {
                "source": "test_system",
                "event": "test_event",
                "data": {"key": "value"},
            }
            webhook_result = integration_module.process_webhook(test_webhook)

            test_results["test_results"]["integration"] = {
                "environment_validation": all(
                    r.valid for r in integration_module.environment_validation.values()
                ),
                "endpoint_registration": endpoint_result["success"],
                "webhook_processing": webhook_result["success"],
                "components_initialized": integration_module.rest_client is not None,
            }

            integration_module.cleanup_resources()
            console.print("✅ Integration hub test completed", style="green")

        except Exception as e:
            test_results["test_results"]["integration"] = {"error": str(e)}
            console.print(f"❌ Integration hub test failed: {e!s}", style="red")

        # Display summary
        console.print("\n📋 Test Summary", style="magenta bold")
        summary_table = Table(title="Phase 9.8 Test Results")
        summary_table.add_column("Module", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Details", style="dim")

        for module_name, results in test_results["test_results"].items():
            if "error" in results:
                status = "❌ Failed"
                details = f"Error: {results['error'][:50]}..."
            else:
                passed_tests = sum(1 for v in results.values() if v is True)
                total_tests = len(results)
                status = f"✅ {passed_tests}/{total_tests} Passed"
                details = f"Environment: {'✅' if results.get('environment_validation', False) else '❌'}"

            summary_table.add_row(module_name.title(), status, details)

        console.print(summary_table)

        # Save results if requested
        if output_file:
            with open(output_file, "w") as f:
                json.dump(test_results, f, indent=2)
            console.print(f"💾 Test results saved to {output_file}", style="dim")

        console.print(
            "\n✅ Phase 9.8 comprehensive testing complete", style="magenta bold"
        )

    except Exception as e:
        console.print(f"❌ Error during comprehensive testing: {e!s}", style="red")


@advanced_features_cli.command(name="generate-report")
@click.option(
    "--output-file", type=click.Path(), help="Output file for comprehensive report"
)
@click.option(
    "--format",
    default="json",
    type=click.Choice(["json", "markdown"]),
    help="Report format",
)
def generate_comprehensive_report(output_file: str | None, format: str):
    """Generate comprehensive Phase 9.8 report following crawl_mcp.py methodology."""
    try:
        console.print("📋 Generating Phase 9.8 Comprehensive Report", style="magenta")

        # Initialize all modules
        analytics_module = RealTimeAnalyticsModule()
        security_module = SecurityComplianceModule()
        integration_module = IntegrationHubModule()

        # Generate individual reports
        analytics_report = analytics_module.generate_analytics_report()
        security_report = security_module.generate_security_report()
        integration_report = integration_module.generate_integration_report()

        # Combine reports
        comprehensive_report = {
            "timestamp": datetime.now().isoformat(),
            "phase": "9.8",
            "title": "Advanced Module Features Comprehensive Report",
            "methodology": "crawl_mcp.py systematic approach",
            "modules": {
                "analytics": (
                    analytics_report.get("report", {})
                    if analytics_report["success"]
                    else {"error": analytics_report.get("error")}
                ),
                "security": (
                    security_report.get("report", {})
                    if security_report["success"]
                    else {"error": security_report.get("error")}
                ),
                "integration": (
                    integration_report.get("report", {})
                    if integration_report["success"]
                    else {"error": integration_report.get("error")}
                ),
            },
            "summary": {
                "modules_active": sum(
                    [
                        analytics_report["success"],
                        security_report["success"],
                        integration_report["success"],
                    ]
                ),
                "total_modules": 3,
                "overall_status": (
                    "operational"
                    if all(
                        [
                            analytics_report["success"],
                            security_report["success"],
                            integration_report["success"],
                        ]
                    )
                    else "partial"
                ),
            },
        }

        # Save report
        if output_file:
            if format == "json":
                with open(output_file, "w") as f:
                    json.dump(comprehensive_report, f, indent=2)
            elif format == "markdown":
                # Convert to markdown format
                markdown_content = f"""# Phase 9.8 Advanced Module Features Report

**Generated**: {comprehensive_report["timestamp"]}
**Methodology**: {comprehensive_report["methodology"]}
**Overall Status**: {comprehensive_report["summary"]["overall_status"].upper()}

## Summary
- **Modules Active**: {comprehensive_report["summary"]["modules_active"]}/{comprehensive_report["summary"]["total_modules"]}
- **Analytics Module**: {"✅ Active" if analytics_report["success"] else "❌ Error"}
- **Security Module**: {"✅ Active" if security_report["success"] else "❌ Error"}
- **Integration Module**: {"✅ Active" if integration_report["success"] else "❌ Error"}

## Module Details

### Analytics Module
{json.dumps(comprehensive_report["modules"]["analytics"], indent=2)}

### Security Module
{json.dumps(comprehensive_report["modules"]["security"], indent=2)}

### Integration Module
{json.dumps(comprehensive_report["modules"]["integration"], indent=2)}
"""
                with open(output_file, "w") as f:
                    f.write(markdown_content)

            console.print(
                f"💾 Comprehensive report saved to {output_file}", style="green"
            )
        else:
            # Display summary
            console.print(json.dumps(comprehensive_report["summary"], indent=2))

        # Cleanup
        analytics_module.cleanup_resources()
        security_module.cleanup_resources()
        integration_module.cleanup_resources()

        console.print("✅ Comprehensive report generation complete", style="green")

    except Exception as e:
        console.print(f"❌ Error generating comprehensive report: {e!s}", style="red")


# Export the CLI group
__all__ = ["advanced_features_cli"]
