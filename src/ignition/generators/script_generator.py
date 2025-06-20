"""Script generator for Ignition Jython scripts using templates."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class IgnitionScriptGenerator:
    """Generator for Ignition Jython scripts using Jinja2 templates."""

    def __init__(self, templates_dir: str | Path = "templates") -> None:
        """Initialize the script generator.

        Args:
            templates_dir: Path to the directory containing Jinja2 templates
        """
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters for Jython compatibility
        self.env.filters["tojson"] = self._jython_json_filter

    def _jython_json_filter(self, value: Any) -> str:
        """Convert Python objects to Jython-compatible JSON strings.

        Args:
            value: The value to convert to JSON

        Returns:
            JSON string compatible with Jython 2.7
        """
        # Use simple JSON generation compatible with Jython
        if isinstance(value, dict):
            items = []
            for k, v in value.items():
                key_str = f'"{k}"'
                if isinstance(v, str):
                    val_str = f'"{v}"'
                elif isinstance(v, bool):
                    val_str = "True" if v else "False"
                elif v is None:
                    val_str = "None"
                else:
                    val_str = str(v)
                items.append(f"{key_str}: {val_str}")
            return "{" + ", ".join(items) + "}"
        elif isinstance(value, list):
            items = []
            for item in value:
                if isinstance(item, str):
                    items.append(f'"{item}"')
                elif isinstance(item, bool):
                    items.append("True" if item else "False")
                elif item is None:
                    items.append("None")
                else:
                    items.append(str(item))
            return "[" + ", ".join(items) + "]"
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return "True" if value else "False"
        elif value is None:
            return "None"
        else:
            return str(value)

    def generate_script(
        self,
        template_name: str,
        context: dict[str, Any],
        output_file: str | Path | None = None,
    ) -> str:
        """Generate a Jython script from a template.

        Args:
            template_name: Name of the template file (e.g., "vision/button_click_handler.jinja2")
            context: Dictionary containing template variables
            output_file: Optional path to save the generated script

        Returns:
            Generated script content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
            Exception: If template rendering fails
        """
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            raise FileNotFoundError(f"Template '{template_name}' not found: {e}") from e

        # Add timestamp to context
        context = dict(context)  # Create copy to avoid modifying original
        context.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            script_content = template.render(**context)
        except Exception as e:
            raise Exception(f"Failed to render template '{template_name}': {e}") from e

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(script_content, encoding="utf-8")

        return script_content

    def generate_from_config(self, config: str | Path | dict[str, Any], output_file: str | Path | None = None) -> str:
        """Generate a script from a configuration file or dictionary.

        Args:
            config: Path to JSON config file or config dictionary
            output_file: Optional path to save the generated script

        Returns:
            Generated script content as string
        """
        if isinstance(config, str | Path):
            config_path = Path(config)
            with open(config_path, encoding="utf-8") as f:
                config_dict = json.load(f)
        else:
            config_dict = config

        template_name = config_dict.pop("template")
        if not template_name.endswith(".jinja2"):
            template_name += ".jinja2"

        return self.generate_script(template_name, config_dict, output_file)

    def list_templates(self) -> list[str]:
        """List all available templates.

        Returns:
            List of template names
        """
        templates = []
        for template_file in self.templates_dir.rglob("*.jinja2"):
            relative_path = template_file.relative_to(self.templates_dir)
            templates.append(str(relative_path))
        return sorted(templates)

    def validate_config(self, config: dict[str, Any], template_name: str) -> list[str]:
        """Validate a configuration against template requirements.

        Args:
            config: Configuration dictionary
            template_name: Name of the template

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check if template exists
        if template_name not in self.list_templates():
            errors.append(f"Template '{template_name}' does not exist")
            return errors

        # Basic validation - this could be expanded with schema validation
        if "component_name" not in config:
            errors.append("'component_name' is required")

        # Template-specific validation
        if "vision/button_click_handler" in template_name:
            if config.get("action_type") == "navigation" and "target_window" not in config:
                errors.append("'target_window' is required for navigation actions")
            elif config.get("action_type") == "tag_write" and "target_tag" not in config:
                errors.append("'target_tag' is required for tag write actions")

        return errors
