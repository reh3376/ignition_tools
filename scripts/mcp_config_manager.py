#!/usr/bin/env python3
"""MCP Configuration Manager.

This script manages MCP server configurations, allowing easy addition
of new MCP Docker configurations as they are provided.
"""

import json
from pathlib import Path


class MCPConfigManager:
    """Manages MCP server configurations."""

    def __init__(self) -> None:
        """Initialize the config manager."""
        self.project_root = Path(__file__).parent.parent
        self.configs_dir = self.project_root / "mcp_configs"
        self.configs_dir.mkdir(exist_ok=True)

        # Known configurations that need to be added
        self.pending_configs = {
            "desktop_commander": "Desktop Commander",
            "docker": "Docker",
            "github_official": "GitHub Official",
            "neo4j_cypher": "Neo4j Cypher",
            "neo4j_memory": "Neo4j Memory",
            "memory": "Memory",
            "nodejs_sandbox": "Node.js sandbox",
            "curl": "curl",
        }

        # Configurations already provided
        self.received_configs = {}

    def add_config(self, config_name: str, config_data: dict) -> None:
        """Add a new MCP configuration."""
        # Save to individual file
        config_file = self.configs_dir / f"{config_name}.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

        # Add to received configs
        self.received_configs[config_name] = config_data

        print(f"✅ Added configuration: {config_name}")

    def load_all_configs(self) -> dict:
        """Load all available configurations."""
        all_configs = {}

        # Load from individual files
        for config_file in self.configs_dir.glob("*.json"):
            config_name = config_file.stem
            with open(config_file) as f:
                all_configs[config_name] = json.load(f)

        return all_configs

    def update_test_script(self) -> None:
        """Update the comprehensive test script with new configurations."""
        test_script = self.project_root / "scripts" / "comprehensive_mcp_server_test.py"

        # Read current script
        with open(test_script) as f:
            content = f.read()

        # Generate new config loading code
        all_configs = self.load_all_configs()
        config_code = "        configs = {}\n"

        for config_name, config_data in all_configs.items():
            config_code += f"        # {config_name.replace('_', ' ').title()}\n"
            config_code += f"        configs['{config_name}'] = {json.dumps(config_data, indent=8)[1:-1].replace('        ', '            ')}\n\n"

        # Replace the load_mcp_docker_configs method
        start_marker = "    def load_mcp_docker_configs(self) -> Dict:"

        start_idx = content.find(start_marker)
        if start_idx != -1:
            # Find the end of the method
            in_method = False
            end_idx = start_idx

            for i, char in enumerate(content[start_idx:]):
                if char == ":" and not in_method:
                    in_method = True
                elif in_method and char == "\n":
                    # Look for the return statement
                    remaining = content[start_idx + i :]
                    return_idx = remaining.find("        return configs")
                    if return_idx != -1:
                        end_idx = (
                            start_idx + i + return_idx + len("        return configs")
                        )
                        break

            # Replace the method
            new_method = f"""    def load_mcp_docker_configs(self) -> Dict:
        \"\"\"Load MCP Docker configurations.\"\"\"
{config_code.rstrip()}

        return configs"""

            new_content = content[:start_idx] + new_method + content[end_idx:]

            with open(test_script, "w") as f:
                f.write(new_content)

            print(f"✅ Updated test script with {len(all_configs)} configurations")

    def show_status(self) -> None:
        """Show the status of all MCP configurations."""
        print("🔧 MCP Configuration Status")
        print("=" * 50)

        all_configs = self.load_all_configs()

        print(f"\n📦 Configured Servers: {len(all_configs)}")
        for config_name in all_configs:
            print(f"   ✅ {config_name.replace('_', ' ').title()}")

        pending = set(self.pending_configs.keys()) - set(all_configs.keys())
        if pending:
            print(f"\n⏳ Pending Configurations: {len(pending)}")
            for config_name in pending:
                display_name = self.pending_configs[config_name]
                print(f"   ⏳ {display_name}")

        print(
            f"\n📊 Progress: {len(all_configs)}/{len(self.pending_configs)} ({len(all_configs) / len(self.pending_configs) * 100:.1f}%)"
        )


def add_context7_config():
    """Add the Context7 configuration as provided."""
    manager = MCPConfigManager()

    context7_config = {
        "mcpServers": {
            "context7": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "mcp/context7"],
            }
        }
    }

    manager.add_config("context7", context7_config)
    return manager


def main():
    """Main function to manage MCP configurations."""
    # Initialize with Context7 config
    manager = add_context7_config()

    # Show current status
    manager.show_status()

    # Update test script
    manager.update_test_script()

    print("\n🎯 Ready to receive additional MCP configurations!")
    print("   Please provide the configurations for:")

    all_configs = manager.load_all_configs()
    pending = set(manager.pending_configs.keys()) - set(all_configs.keys())

    for config_name in sorted(pending):
        display_name = manager.pending_configs[config_name]
        print(f"   • {display_name}")


if __name__ == "__main__":
    main()
