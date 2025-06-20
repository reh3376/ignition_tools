"""Intelligent Module collections.abc.Generator using Code Intelligence."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from src.ignition.code_intelligence.manager import CodeIntelligenceManager
from src.ignition.graph.client import IgnitionGraphClient

from .sdk_manager import IgnitionSDKManager, ModuleProjectConfig

console = Console()


@dataclass
class ModuleTemplate:
    """Template for generating specific types of modules."""

    name: str
    description: str
    scopes: str  # GCD combination
    required_functions: list[str]
    optional_functions: list[str]
    dependencies: list[str]
    template_files: dict[str, str]  # filename -> template content


@dataclass
class GeneratedModule:
    """Result of module generation."""

    name: str
    path: Path
    config: ModuleProjectConfig
    template: ModuleTemplate
    generated_files: list[Path]
    intelligence_used: dict[str, Any]


class ModuleGenerator:
    """collections.abc.Generator for intelligent Ignition modules using code intelligence."""

    def __init__(
        self,
        sdk_manager: IgnitionSDKManager | None = None,
        code_manager: CodeIntelligenceManager | None = None,
        graph_client: IgnitionGraphClient | None = None,
    ):
        """Initialize the module generator.

        Args:
            sdk_manager: SDK manager for module creation
            code_manager: Code intelligence manager
            graph_client: Graph database client
        """
        self.sdk_manager = sdk_manager or IgnitionSDKManager()
        self.code_manager = code_manager
        self.graph_client = graph_client

        # Load built-in templates
        self.templates = self._load_builtin_templates()

    def _load_builtin_templates(self) -> dict[str, ModuleTemplate]:
        """Load built-in module templates.

        Returns:
            Dictionary mapping template names to ModuleTemplate objects
        """
        templates = {}

        # Scripting Functions Module Template
        templates["scripting-functions"] = ModuleTemplate(
            name="scripting-functions",
            description="Custom scripting functions for Ignition",
            scopes="G",  # Gateway only
            required_functions=[
                "system.util.getLogger",
                "system.util.jsonEncode",
                "system.util.jsonDecode",
            ],
            optional_functions=[
                "system.db.runQuery",
                "system.tag.readBlocking",
                "system.tag.writeBlocking",
            ],
            dependencies=[
                "com.inductiveautomation.ignition:ignition-common",
                "com.inductiveautomation.ignition:ignition-gateway-api",
            ],
            template_files={},  # Will be populated by template methods
        )

        # Vision Component Module Template
        templates["vision-component"] = ModuleTemplate(
            name="vision-component",
            description="Custom Vision components for Ignition",
            scopes="GCD",  # All scopes
            required_functions=["system.gui.getParentWindow", "system.gui.messageBox"],
            optional_functions=["system.tag.readBlocking", "system.db.runQuery"],
            dependencies=[
                "com.inductiveautomation.ignition:ignition-common",
                "com.inductiveautomation.ignition:ignition-gateway-api",
                "com.inductiveautomation.ignition:ignition-designer-api",
                "com.inductiveautomation.ignition:vision-common",
                "com.inductiveautomation.ignition:vision-designer",
            ],
            template_files={
                "GatewayHook.java": self._get_gateway_hook_template(),
                "DesignerHook.java": self._get_designer_hook_template(),
                "ClientHook.java": self._get_client_hook_template(),
                "CustomComponent.java": self._get_vision_component_template(),
            },
        )

        # Data Integration Module Template
        templates["data-integration"] = ModuleTemplate(
            name="data-integration",
            description="Custom data integration and processing module",
            scopes="G",  # Gateway only
            required_functions=[
                "system.db.runQuery",
                "system.db.runUpdateQuery",
                "system.util.getLogger",
            ],
            optional_functions=[
                "system.tag.readBlocking",
                "system.tag.writeBlocking",
                "system.opc.readValue",
                "system.opc.writeValue",
            ],
            dependencies=[
                "com.inductiveautomation.ignition:ignition-common",
                "com.inductiveautomation.ignition:ignition-gateway-api",
            ],
            template_files={
                "GatewayHook.java": self._get_gateway_hook_template(),
                "DataProcessor.java": self._get_data_processor_template(),
                "DatabaseManager.java": self._get_database_manager_template(),
            },
        )

        return templates

    def analyze_requirements(self, requirements: dict[str, Any]) -> dict[str, Any]:
        """Analyze module requirements using code intelligence.

        Args:
            requirements: Dictionary with module requirements

        Returns:
            Analysis results with recommendations
        """
        analysis = {
            "recommended_template": None,
            "required_functions": [],
            "suggested_functions": [],
            "complexity_estimate": "medium",
            "scope_recommendations": "G",
            "intelligence_insights": {},
        }

        if not self.code_manager or not self.graph_client:
            console.print("⚠️ Code intelligence not available - using basic analysis")
            return analysis

        try:
            # Analyze function usage patterns
            if "functions" in requirements:
                function_names = requirements["functions"]

                # Get function context from graph
                for func_name in function_names:
                    try:
                        context = self.code_manager.get_function_context(func_name)
                        if context:
                            analysis["intelligence_insights"][func_name] = context
                    except Exception as e:
                        console.print(f"⚠️ Could not analyze function {func_name}: {e}")

            # Determine recommended template based on requirements
            if "type" in requirements:
                module_type = requirements["type"].lower()
                if module_type in ["scripting", "functions", "script"]:
                    analysis["recommended_template"] = "scripting-functions"
                    analysis["scope_recommendations"] = "G"
                elif module_type in ["vision", "component", "ui"]:
                    analysis["recommended_template"] = "vision-component"
                    analysis["scope_recommendations"] = "GCD"
                elif module_type in ["data", "integration", "database"]:
                    analysis["recommended_template"] = "data-integration"
                    analysis["scope_recommendations"] = "G"

            # Estimate complexity
            function_count = len(requirements.get("functions", []))
            if function_count < 5:
                analysis["complexity_estimate"] = "low"
            elif function_count < 15:
                analysis["complexity_estimate"] = "medium"
            else:
                analysis["complexity_estimate"] = "high"

        except Exception as e:
            console.print(f"⚠️ Error during requirements analysis: {e}")

        return analysis

    def generate_module(
        self, name: str, template_name: str, requirements: dict[str, Any] | None = None
    ) -> GeneratedModule | None:
        """Generate a new Ignition module.

        Args:
            name: Name of the module to create
            template_name: Name of the template to use
            requirements: Additional requirements and customizations

        Returns:
            GeneratedModule object if successful, None otherwise
        """
        if template_name not in self.templates:
            console.print(f"❌ Template not found: {template_name}")
            console.print(f"Available templates: {list(self.templates.keys())}")
            return None

        template = self.templates[template_name]
        requirements = requirements or {}

        # Analyze requirements
        analysis = self.analyze_requirements(requirements)

        # Create module configuration
        config = ModuleProjectConfig(
            name=name,
            scopes=template.scopes,
            root_package=requirements.get("package", "com.ignscripts.modules"),
            language=requirements.get("language", "kotlin"),
            description=requirements.get("description", template.description),
            min_ignition_version=requirements.get("min_version", "8.1.0"),
        )

        # Create the module project
        success = self.sdk_manager.create_module_project(config)
        if not success:
            console.print(f"❌ Failed to create module project: {name}")
            return None

        project_path = self.sdk_manager.workspace_path / name

        # Generate custom files based on template and intelligence
        generated_files = []
        try:
            generated_files = self._generate_custom_files(
                project_path, template, requirements, analysis
            )
        except Exception as e:
            console.print(f"⚠️ Error generating custom files: {e}")

        # Create the generated module result
        result = GeneratedModule(
            name=name,
            path=project_path,
            config=config,
            template=template,
            generated_files=generated_files,
            intelligence_used=analysis["intelligence_insights"],
        )

        # Display generation summary
        self._display_generation_summary(result, analysis)

        return result

    def _generate_custom_files(
        self,
        project_path: Path,
        template: ModuleTemplate,
        requirements: dict[str, Any],
        analysis: dict[str, Any],
    ) -> list[Path]:
        """Generate custom files for the module.

        Args:
            project_path: Path to the module project
            template: Module template
            requirements: Module requirements
            analysis: Intelligence analysis results

        Returns:
            list of generated file paths
        """
        generated_files = []

        # Find the source directories
        src_dirs = list(project_path.rglob("src/main/java"))
        if not src_dirs:
            console.print("⚠️ No Java source directories found")
            return generated_files

        # Generate files based on template
        for filename, content_template in template.template_files.items():
            try:
                # Customize content based on requirements and intelligence
                content = self._customize_template_content(
                    content_template, requirements, analysis
                )

                # Find appropriate location for the file
                target_path = self._find_target_path(project_path, filename)
                if target_path:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_text(content)
                    generated_files.append(target_path)
                    console.print(
                        f"📝 Generated: {target_path.relative_to(project_path)}"
                    )

            except Exception as e:
                console.print(f"⚠️ Error generating {filename}: {e}")

        return generated_files

    def _customize_template_content(
        self,
        template_content: str,
        requirements: dict[str, Any],
        analysis: dict[str, Any],
    ) -> str:
        """Customize template content based on requirements and intelligence.

        Args:
            template_content: Original template content
            requirements: Module requirements
            analysis: Intelligence analysis

        Returns:
            Customized content
        """
        content = template_content

        # Replace placeholders with actual values
        replacements = {
            "{{MODULE_NAME}}": requirements.get("name", "CustomModule"),
            "{{MODULE_DESCRIPTION}}": requirements.get(
                "description", "Custom Ignition Module"
            ),
            "{{PACKAGE_NAME}}": requirements.get("package", "com.ignscripts.modules"),
            "{{MIN_VERSION}}": requirements.get("min_version", "8.1.0"),
            "{{FUNCTIONS}}": self._generate_function_implementations(
                requirements.get("functions", []), analysis
            ),
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))

        return content

    def _generate_function_implementations(
        self, functions: list[str], analysis: dict[str, Any]
    ) -> str:
        """Generate function implementations based on intelligence.

        Args:
            functions: list of function names to implement
            analysis: Intelligence analysis

        Returns:
            Generated function implementations
        """
        implementations = []

        for func_name in functions:
            # Get intelligence insights for this function
            analysis.get("intelligence_insights", {}).get(func_name, {})

            # Generate basic implementation
            impl = f"""
    public static Object {func_name.replace(".", "_")}(Object... args) {{
        // Generated function: {func_name}
        // TODO: Implement custom logic here

        try {{
            // Add your implementation here
            return null;
        }} catch (Exception e) {{
            logger.error("Error in {func_name}: " + e.getMessage(), e);
            throw new RuntimeException(e);
        }}
    }}"""

            implementations.append(impl)

        return "\n".join(implementations)

    def _find_target_path(self, project_path: Path, filename: str) -> Path | None:
        """Find the target path for a generated file.

        Args:
            project_path: Module project path
            filename: Name of the file to place

        Returns:
            Target path if found, None otherwise
        """
        # Look for appropriate directories based on file type
        if filename.endswith(".java"):
            # Find Java source directory
            java_dirs = list(project_path.rglob("src/main/java"))
            if java_dirs:
                # Find package directory
                package_dirs = list(java_dirs[0].rglob("**/gateway"))
                if package_dirs:
                    return package_dirs[0] / filename
                else:
                    return java_dirs[0] / filename

        elif filename == "module.xml":
            # Module XML goes in resources
            resource_dirs = list(project_path.rglob("src/main/resources"))
            if resource_dirs:
                return resource_dirs[0] / filename

        return None

    def _display_generation_summary(
        self, result: GeneratedModule, analysis: dict[str, Any]
    ) -> None:
        """Display a summary of the module generation.

        Args:
            result: Generated module result
            analysis: Intelligence analysis
        """
        # Create summary table
        table = Table(title=f"Module Generation Summary: {result.name}")
        table.add_column("Property", style="bold")
        table.add_column("Value")

        table.add_row("Name", result.name)
        table.add_row("Template", result.template.name)
        table.add_row("Scopes", result.config.scopes)
        table.add_row("Package", result.config.root_package)
        table.add_row("Language", result.config.language)
        table.add_row("Path", str(result.path))
        table.add_row("Files Generated", str(len(result.generated_files)))
        table.add_row("Complexity", analysis.get("complexity_estimate", "unknown"))

        console.print(table)

        # Show intelligence insights if available
        if result.intelligence_used:
            console.print("\n🧠 Code Intelligence Insights:")
            for func_name, insights in result.intelligence_used.items():
                console.print(f"  • {func_name}: {len(insights)} context items")

    def list_templates(self) -> dict[str, ModuleTemplate]:
        """List available module templates.

        Returns:
            Dictionary of available templates
        """
        return self.templates.copy()

    def get_template_info(self, template_name: str) -> ModuleTemplate | None:
        """Get information about a specific template.

        Args:
            template_name: Name of the template

        Returns:
            ModuleTemplate if found, None otherwise
        """
        return self.templates.get(template_name)

    # Template content methods
    def _get_gateway_hook_template(self) -> str:
        """Get the Gateway Hook template."""
        return """package {{PACKAGE_NAME}}.gateway;

import com.inductiveautomation.ignition.common.licensing.LicenseState;
import com.inductiveautomation.ignition.common.script.ScriptManager;
import com.inductiveautomation.ignition.gateway.model.AbstractGatewayModuleHook;
import com.inductiveautomation.ignition.gateway.model.GatewayContext;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GatewayHook extends AbstractGatewayModuleHook {

    private static final Logger logger = LoggerFactory.getLogger(GatewayHook.class);

    private GatewayContext gatewayContext;

    @Override
    public void setup(GatewayContext gatewayContext) {
        this.gatewayContext = gatewayContext;
    }

    @Override
    public void startup(LicenseState activationState) {
        logger.info("{{MODULE_NAME}} module startup");

        // Register scripting functions
        ScriptManager scriptManager = gatewayContext.getScriptManager();
        scriptManager.addScriptModule("system.{{MODULE_NAME}}",
            new {{MODULE_NAME}}ScriptingFunctions(),
            new {{MODULE_NAME}}ScriptingFunctions.Docs());
    }

    @Override
    public void shutdown() {
        logger.info("{{MODULE_NAME}} module shutdown");
    }
}"""

    def _get_designer_hook_template(self) -> str:
        """Get the Designer Hook template."""
        return """package {{PACKAGE_NAME}}.designer;

import com.inductiveautomation.ignition.common.licensing.LicenseState;
import com.inductiveautomation.ignition.designer.model.AbstractDesignerModuleHook;
import com.inductiveautomation.ignition.designer.model.DesignerContext;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DesignerHook extends AbstractDesignerModuleHook {

    private static final Logger logger = LoggerFactory.getLogger(DesignerHook.class);

    @Override
    public void startup(DesignerContext context, LicenseState activationState) {
        logger.info("{{MODULE_NAME}} designer startup");
    }

    @Override
    public void shutdown() {
        logger.info("{{MODULE_NAME}} designer shutdown");
    }
}"""

    def _get_client_hook_template(self) -> str:
        """Get the Client Hook template."""
        return """package {{PACKAGE_NAME}}.client;

import com.inductiveautomation.ignition.client.model.AbstractClientModuleHook;
import com.inductiveautomation.ignition.client.model.ClientContext;
import com.inductiveautomation.ignition.common.licensing.LicenseState;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClientHook extends AbstractClientModuleHook {

    private static final Logger logger = LoggerFactory.getLogger(ClientHook.class);

    @Override
    public void startup(ClientContext context, LicenseState activationState) {
        logger.info("{{MODULE_NAME}} client startup");
    }

    @Override
    public void shutdown() {
        logger.info("{{MODULE_NAME}} client shutdown");
    }
}"""

    def _get_scripting_functions_template(self) -> str:
        """Get the Scripting Functions template."""
        return """package {{PACKAGE_NAME}}.gateway;

import com.inductiveautomation.ignition.common.script.builtin.KeywordArgs;
import com.inductiveautomation.ignition.common.script.builtin.PyArgumentMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class {{MODULE_NAME}}ScriptingFunctions {

    private static final Logger logger = LoggerFactory.getLogger({{MODULE_NAME}}ScriptingFunctions.class);

    {{FUNCTIONS}}

    public static class Docs {
        // Documentation for scripting functions
    }
}"""

    def _get_vision_component_template(self) -> str:
        """Get the Vision Component template."""
        return """package {{PACKAGE_NAME}}.vision;

import com.inductiveautomation.vision.api.client.components.model.AbstractVisionComponent;

import javax.swing.*;
import java.awt.*;

public class Custom{{MODULE_NAME}}Component extends AbstractVisionComponent {

    public static final String COMPONENT_TYPE = "{{MODULE_NAME}}.CustomComponent";

    public Custom{{MODULE_NAME}}Component() {
        super(COMPONENT_TYPE);
        setOpaque(true);
        setBackground(Color.WHITE);
        setPreferredSize(new Dimension(100, 50));
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        // Custom painting logic here
        Graphics2D g2d = (Graphics2D) g.create();
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Draw custom content
        g2d.setColor(Color.BLUE);
        g2d.drawString("{{MODULE_NAME}} Component", 10, 25);

        g2d.dispose();
    }
}"""

    def _get_data_processor_template(self) -> str:
        """Get the Data Processor template."""
        return """package {{PACKAGE_NAME}}.gateway;

import com.inductiveautomation.ignition.gateway.model.GatewayContext;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class DataProcessor {

    private static final Logger logger = LoggerFactory.getLogger(DataProcessor.class);

    private final GatewayContext context;
    private final ScheduledExecutorService scheduler;

    public DataProcessor(GatewayContext context) {
        this.context = context;
        this.scheduler = Executors.newScheduledThreadPool(2);
    }

    public void start() {
        logger.info("Starting data processor");

        // Schedule periodic data processing
        scheduler.scheduleAtFixedRate(this::processData, 0, 60, TimeUnit.SECONDS);
    }

    public void stop() {
        logger.info("Stopping data processor");
        scheduler.shutdown();
    }

    private void processData() {
        try {
            // Custom data processing logic here
            logger.debug("Processing data...");

        } catch (Exception e) {
            logger.error("Error processing data", e);
        }
    }
}"""

    def _get_database_manager_template(self) -> str:
        """Get the Database Manager template."""
        return """package {{PACKAGE_NAME}}.gateway;

import com.inductiveautomation.ignition.gateway.model.GatewayContext;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class DatabaseManager {

    private static final Logger logger = LoggerFactory.getLogger(DatabaseManager.class);

    private final GatewayContext context;

    public DatabaseManager(GatewayContext context) {
        this.context = context;
    }

    public void executeQuery(String sql, Object... params) throws SQLException {
        try (Connection conn = context.getDatabaseManager().getConnection("default")) {
            try (PreparedStatement stmt = conn.prepareStatement(sql)) {

                // set parameters
                for (int i = 0; i < params.length; i++) {
                    stmt.setObject(i + 1, params[i]);
                }

                // Execute query
                try (ResultSet rs = stmt.executeQuery()) {
                    // Process results
                    while (rs.next()) {
                        // Custom result processing
                    }
                }
            }
        }
    }
}"""

    def _get_module_xml_template(self) -> str:
        """Get the module.xml template."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<module>
    <id>{{PACKAGE_NAME}}.{{MODULE_NAME}}</id>
    <name>{{MODULE_NAME}}</name>
    <description>{{MODULE_DESCRIPTION}}</description>
    <version>1.0.0</version>
    <requiredIgnitionVersion>{{MIN_VERSION}}</requiredIgnitionVersion>

    <moduleClasspath>
        <jar>{{MODULE_NAME}}-gateway.jar</jar>
        <jar>{{MODULE_NAME}}-designer.jar</jar>
        <jar>{{MODULE_NAME}}-client.jar</jar>
    </moduleClasspath>

    <hooks>
        <hook scope="G">{{PACKAGE_NAME}}.gateway.GatewayHook</hook>
        <hook scope="D">{{PACKAGE_NAME}}.designer.DesignerHook</hook>
        <hook scope="C">{{PACKAGE_NAME}}.client.ClientHook</hook>
    </hooks>
</module>"""
