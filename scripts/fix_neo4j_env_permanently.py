#!/usr/bin/env python3
"""Permanently fix Neo4j environment variable inconsistencies.

This script follows the systematic approach from crawl_mcp.py to:
1. Standardize all Neo4j environment variable names
2. Update .env file with correct values
3. Update all Python files to use consistent variable names
4. Verify the fix works across all modules

Usage:
    python scripts/fix_neo4j_env_permanently.py
"""

import os
import re
import shutil
from pathlib import Path


class Neo4jEnvironmentFixer:
    """Systematically fix Neo4j environment variable issues."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.env_file = self.project_root / ".env"
        self.backup_dir = self.project_root / ".env_backups"

        # Standard Neo4j environment variables
        self.standard_vars = {
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_USER": "neo4j",  # Keep both for compatibility
            "NEO4J_PASSWORD": "ignition-graph"
        }

    def step_1_backup_current_state(self) -> None:
        """Step 1: Backup current .env file and create restore point."""
        print("🔄 Step 1: Creating backup of current state...")

        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)

        # Backup .env file with timestamp
        if self.env_file.exists():
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f".env.backup.{timestamp}"
            shutil.copy2(self.env_file, backup_file)
            print(f"✅ Backed up .env to {backup_file}")
        else:
            print("⚠️  No .env file found - will create new one")

    def step_2_analyze_current_env(self) -> dict[str, str]:
        """Step 2: Analyze current .env file for issues."""
        print("🔍 Step 2: Analyzing current .env file...")

        current_vars = {}
        duplicates = []

        if self.env_file.exists():
            with open(self.env_file) as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key in current_vars:
                        duplicates.append((key, i, value))
                        print(f"⚠️  Duplicate found: {key} on line {i}")
                    current_vars[key] = value

        print(f"📊 Found {len(current_vars)} environment variables")
        if duplicates:
            print(f"🚨 Found {len(duplicates)} duplicate variables")

        return current_vars

    def step_3_fix_env_file(self, current_vars: dict[str, str]) -> None:
        """Step 3: Fix .env file with correct Neo4j variables."""
        print("🔧 Step 3: Fixing .env file...")

        # Read existing .env content
        existing_lines = []
        if self.env_file.exists():
            with open(self.env_file) as f:
                existing_lines = f.readlines()

        # Process lines and fix Neo4j variables
        new_lines = []
        neo4j_vars_added = set()

        for line in existing_lines:
            stripped = line.strip()

            # Skip empty lines and comments as-is
            if not stripped or stripped.startswith("#"):
                new_lines.append(line)
                continue

            # Process variable lines
            if "=" in stripped:
                key, value = stripped.split("=", 1)

                # Handle Neo4j variables
                if key.startswith("NEO4J_"):
                    if key in self.standard_vars and key not in neo4j_vars_added:
                        # Use correct value for this Neo4j variable
                        correct_value = self.standard_vars[key]
                        new_lines.append(f"{key}={correct_value}\n")
                        neo4j_vars_added.add(key)
                        print(f"✅ Fixed {key}={correct_value}")
                    # Skip duplicates and incorrect variables
                else:
                    # Keep non-Neo4j variables as-is
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Add any missing Neo4j variables
        for key, value in self.standard_vars.items():
            if key not in neo4j_vars_added:
                new_lines.append(f"{key}={value}\n")
                print(f"➕ Added missing {key}={value}")

        # Write fixed .env file
        with open(self.env_file, "w") as f:
            f.writelines(new_lines)

        print(f"✅ Updated .env file with {len(self.standard_vars)} Neo4j variables")

    def step_4_find_inconsistent_files(self) -> list[tuple[Path, list[str]]]:
        """Step 4: Find Python files with inconsistent Neo4j variable usage."""
        print("🔍 Step 4: Finding files with inconsistent Neo4j variables...")

        inconsistent_files = []
        python_files = list(self.project_root.rglob("*.py"))

        # Patterns to look for
        patterns = [
            r'os\.getenv\(["\']NEO4J_USER["\']',
            r'os\.environ\.get\(["\']NEO4J_USER["\']',
            r'NEO4J_USER["\']',
        ]

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                issues = []
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        issues.extend(matches)

                if issues:
                    inconsistent_files.append((py_file, issues))

            except Exception as e:
                print(f"⚠️  Could not read {py_file}: {e}")

        print(f"📊 Found {len(inconsistent_files)} files with inconsistent variables")
        return inconsistent_files

    def step_5_update_python_files(self, inconsistent_files: list[tuple[Path, list[str]]]) -> None:
        """Step 5: Update Python files to support both variable names."""
        print("🔧 Step 5: Updating Python files for consistency...")

        for py_file, issues in inconsistent_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Create backup
                backup_file = py_file.with_suffix(py_file.suffix + ".backup")
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(content)

                # Update content to support both variable names
                original_content = content

                # Replace NEO4J_USER with fallback to NEO4J_USERNAME
                patterns_replacements = [
                    (
                        r'os\.getenv\(["\']NEO4J_USER["\']\s*,\s*([^)]+)\)',
                        r'os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME", os.getenv("NEO4J_USERNAME", \1)))'
                    ),
                    (
                        r'os\.environ\.get\(["\']NEO4J_USER["\']\s*,\s*([^)]+)\)',
                        r'os.environ.get("NEO4J_USER", os.environ.get("NEO4J_USERNAME", os.environ.get("NEO4J_USERNAME", \1)))'
                    ),
                ]

                for pattern, replacement in patterns_replacements:
                    content = re.sub(pattern, replacement, content)

                # Only write if content changed
                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ Updated {py_file.relative_to(self.project_root)}")
                else:
                    # Remove backup if no changes
                    backup_file.unlink()

            except Exception as e:
                print(f"❌ Failed to update {py_file}: {e}")

    def step_6_verify_fix(self) -> bool:
        """Step 6: Verify the fix works by testing connections."""
        print("🧪 Step 6: Verifying the fix...")

        try:
            # Test environment variable loading
            from dotenv import load_dotenv
            load_dotenv(self.env_file, override=True)

            # Check all required variables are present
            required_vars = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
            missing_vars = []

            for var in required_vars:
                value = os.getenv(var)
                if not value:
                    missing_vars.append(var)
                else:
                    print(f"✅ {var} = {value}")

            if missing_vars:
                print(f"❌ Missing variables: {missing_vars}")
                return False

            # Test Neo4j connection
            print("🔗 Testing Neo4j connection...")

            # Import and test the main client
            import sys
            sys.path.append(str(self.project_root / "src"))

            from ignition.graph.client import IgnitionGraphClient

            client = IgnitionGraphClient()
            client.connect()

            # Test a simple query
            result = client.execute_query("RETURN 1 as test")
            test_value = result[0]["test"] if result else None

            client.disconnect()

            if test_value == 1:
                print("✅ Neo4j connection test successful!")
                return True
            else:
                print("❌ Neo4j connection test failed!")
                return False

        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

    def step_7_create_validation_script(self) -> None:
        """Step 7: Create a validation script for future use."""
        print("📝 Step 7: Creating validation script...")

        validation_script = self.project_root / "scripts" / "validate_neo4j_env.py"

        script_content = '''#!/usr/bin/env python3
"""Validate Neo4j environment variables are properly configured.

This script checks that all Neo4j environment variables are properly set
and that connections work correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Validate Neo4j environment configuration."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    print("🔍 Validating Neo4j Environment Configuration...")
    
    # Load environment variables
    load_dotenv(env_file, override=True)
    
    # Check required variables
    required_vars = {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j", 
        "NEO4J_PASSWORD": "ignition-graph"
    }
    
    all_good = True
    
    for var, expected in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ Missing: {var}")
            all_good = False
        elif value != expected:
            print(f"⚠️  {var} = {value} (expected: {expected})")
        else:
            print(f"✅ {var} = {value}")
    
    # Test connection if all variables present
    if all_good:
        try:
            sys.path.append(str(project_root / "src"))
            from ignition.graph.client import IgnitionGraphClient
            
            client = IgnitionGraphClient()
            client.connect()
            result = client.execute_query("RETURN 1 as test")
            client.disconnect()
            
            if result and result[0]["test"] == 1:
                print("✅ Neo4j connection successful!")
            else:
                print("❌ Neo4j connection failed!")
                all_good = False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            all_good = False
    
    if all_good:
        print("\n🎉 All Neo4j environment variables are properly configured!")
    else:
        print("\n❌ Neo4j environment configuration has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open(validation_script, "w") as f:
            f.write(script_content)

        # Make it executable
        validation_script.chmod(0o755)

        print(f"✅ Created validation script: {validation_script}")

    def run_complete_fix(self) -> bool:
        """Run the complete systematic fix process."""
        print("🚀 Starting systematic Neo4j environment fix...")
        print("=" * 60)

        try:
            self.step_1_backup_current_state()
            current_vars = self.step_2_analyze_current_env()
            self.step_3_fix_env_file(current_vars)
            inconsistent_files = self.step_4_find_inconsistent_files()
            self.step_5_update_python_files(inconsistent_files)
            success = self.step_6_verify_fix()
            self.step_7_create_validation_script()

            print("=" * 60)
            if success:
                print("🎉 Neo4j environment fix completed successfully!")
                print("✅ All environment variables are properly configured")
                print("✅ Neo4j connection verified")
                print("✅ Validation script created for future use")
                return True
            else:
                print("❌ Fix completed but verification failed")
                print("💡 Check Neo4j server status and credentials")
                return False

        except Exception as e:
            print(f"❌ Fix process failed: {e}")
            return False


def main():
    """Main function."""
    fixer = Neo4jEnvironmentFixer()
    success = fixer.run_complete_fix()

    if success:
        print("\n🔄 Run this to verify anytime:")
        print("python scripts/validate_neo4j_env.py")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
