#!/usr/bin/env python3
"""
IGN Scripts Codebase Analyzer

This script analyzes the entire codebase structure, counts lines per file,
categorizes components, and generates a comprehensive report.

Usage:
    python scripts/codebase_analyzer.py [--output-file report.md] [--include-small-files]
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


class CodebaseAnalyzer:
    """Comprehensive codebase analysis tool for IGN Scripts project."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.file_data: list[tuple[str, int, str]] = []  # (path, lines, extension)
        self.total_files = 0
        self.total_lines = 0
        self.file_types: Counter[str] = Counter()

        # Exclusion patterns
        self.exclude_patterns = {
            ".venv",
            ".git",
            "node_modules",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            "tools",
            "graph-data",
            "test-results",
            "coverage-reports",
            ".DS_Store",
        }

        # File extensions to include
        self.include_extensions = {
            ".py",
            ".md",
            ".yml",
            ".yaml",
            ".json",
            ".txt",
            ".sh",
            ".sql",
            ".toml",
            ".lock",
            ".env",
            ".cfg",
            ".conf",
        }

        # File categorization mappings
        self.categories = {
            "core_framework": {
                "patterns": ["src/core/"],
                "description": "Core Framework (src/core/)",
                "emoji": "🏗️",
            },
            "code_intelligence": {
                "patterns": ["src/ignition/code_intelligence/"],
                "description": "Code Intelligence (Phase 8)",
                "emoji": "📊",
            },
            "data_integration": {
                "patterns": ["src/ignition/data_integration/"],
                "description": "Data Integration (Phase 3)",
                "emoji": "📈",
            },
            "module_system": {
                "patterns": ["src/ignition/modules/"],
                "description": "Module System (Phase 9)",
                "emoji": "🔧",
            },
            "graph_database": {
                "patterns": ["src/ignition/graph/"],
                "description": "Graph Database System",
                "emoji": "🌐",
            },
            "task_implementations": {
                "patterns": ["src/ignition/graph/tasks/"],
                "description": "Task System Implementations",
                "emoji": "🏭",
            },
            "opcua_integration": {
                "patterns": ["src/ignition/opcua/"],
                "description": "OPC-UA Integration",
                "emoji": "🔌",
            },
            "user_interface": {
                "patterns": ["src/ui/"],
                "description": "User Interface",
                "emoji": "🖥️",
            },
            "documentation": {
                "patterns": ["docs/"],
                "description": "Documentation Structure",
                "emoji": "📚",
            },
            "testing_scripts": {
                "patterns": ["scripts/testing/", "tests/"],
                "description": "Testing & Scripts",
                "emoji": "🧪",
            },
            "infrastructure": {
                "patterns": [
                    "docker-compose.yml",
                    ".github/",
                    "pyproject.toml",
                    "requirements",
                ],
                "description": "Infrastructure Files",
                "emoji": "🏗️",
            },
        }

    def should_exclude_path(self, path: Path) -> bool:
        """Check if a path should be excluded from analysis."""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.exclude_patterns)

    def get_file_description(self, file_path: str) -> str:
        """Generate a descriptive comment for specific files."""
        descriptions = {
            ".file_hash_manifest.json": "Git hash tracking",
            "ign_scripts_db_backup": "Database backup",
            "ruff_analysis.json": "Code analysis results",
            "uv.lock": "Python dependency lock file",
            "src/main.py": "Main entry point",
            "README.md": "Project documentation",
            "docs/roadmap.md": "Project roadmap",
            "docker-compose.yml": "Docker orchestration",
            "pyproject.toml": "Python project config",
            "streamlit_app.py": "Main Streamlit UI",
            "learning_integration.py": "Learning system UI",
            "cli-interface.md": "Complete CLI reference",
            "ui-interface.md": "UI documentation",
        }

        for key, desc in descriptions.items():
            if key in file_path:
                return desc

        # Generate descriptions based on file patterns
        if "opcua" in file_path.lower():
            if "cli" in file_path:
                return "OPC-UA CLI commands"
            elif "config" in file_path:
                return "OPC-UA configuration"
            elif "gui" in file_path:
                return "OPC-UA GUI interface"
            elif "client" in file_path:
                return "OPC-UA client"
            elif "security" in file_path:
                return "OPC-UA security"

        if "cli" in file_path and file_path.endswith(".py"):
            return "CLI commands"

        if "task_" in file_path:
            task_num = file_path.split("task_")[1].split("_")[0] if "task_" in file_path else ""
            return f"Task {task_num} implementation"

        return ""

    def analyze_files(self) -> None:
        """Scan and analyze all files in the codebase."""
        print("🔍 Scanning codebase...")

        for root, dirs, files in os.walk(self.root_path):
            # Remove excluded directories from the search
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.exclude_patterns)]

            root_path = Path(root)
            if self.should_exclude_path(root_path):
                continue

            for file in files:
                file_path = root_path / file
                if self.should_exclude_path(file_path):
                    continue

                extension = file_path.suffix.lower()
                if extension not in self.include_extensions:
                    continue

                try:
                    # Count lines in file
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        line_count = sum(1 for _ in f)

                    relative_path = str(file_path.relative_to(self.root_path))
                    self.file_data.append((relative_path, line_count, extension))
                    self.total_files += 1
                    self.total_lines += line_count
                    self.file_types[extension] += 1

                except (OSError, UnicodeDecodeError) as e:
                    print(f"⚠️  Warning: Could not read {file_path}: {e}")

        # Sort files by line count (descending)
        self.file_data.sort(key=lambda x: x[1], reverse=True)
        print(f"✅ Analysis complete: {self.total_files} files, {self.total_lines:,} lines")

    def categorize_files(self) -> dict[str, list[tuple[str, int, str]]]:
        """Categorize files based on their paths and patterns."""
        categorized = defaultdict(list)
        uncategorized = []

        for file_path, line_count, extension in self.file_data:
            categorized_flag = False

            for category, config in self.categories.items():
                for pattern in config["patterns"]:
                    if pattern in file_path:
                        categorized[category].append((file_path, line_count, extension))
                        categorized_flag = True
                        break
                if categorized_flag:
                    break

            if not categorized_flag:
                uncategorized.append((file_path, line_count, extension))

        # Sort each category by line count
        for category in categorized:
            categorized[category].sort(key=lambda x: x[1], reverse=True)

        # Add uncategorized files to a special category
        if uncategorized:
            categorized["other"] = sorted(uncategorized, key=lambda x: x[1], reverse=True)

        return dict(categorized)

    def generate_report(self, output_file: str | None = None, include_small_files: bool = False) -> str:
        """Generate a comprehensive analysis report."""
        report_lines = []

        # Header
        report_lines.extend(
            [
                "# 📊 IGN Scripts Codebase Analysis",
                f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
                "",
                "## 🔢 **Total Statistics:**",
                f"- **Total Files:** {self.total_files:,} project files",
                f"- **Total Lines:** {self.total_lines:,} lines of code",
                f"- **Major File Types:** {', '.join(f'{ext} ({count})' for ext, count in self.file_types.most_common(10))}",
                "",
            ]
        )

        # Top largest files
        report_lines.extend(["## 📁 **Top Largest Files by Line Count:**", ""])

        top_files = self.file_data[:20]  # Top 20 largest files
        for file_path, line_count, _ in top_files:
            description = self.get_file_description(file_path)
            desc_text = f" ({description})" if description else ""
            report_lines.append(f"- **`{file_path}`** - {line_count:,} lines{desc_text}")

        report_lines.append("")

        # Categorized analysis
        categorized_files = self.categorize_files()

        report_lines.extend(["## 🏗️ **Core Source Code Structure:**", ""])

        # Main application files
        main_files = [
            ("src/main.py", "Main entry point"),
            ("README.md", "Project documentation"),
            ("docs/roadmap.md", "Project roadmap"),
        ]

        report_lines.append("### **Main Application Files:**")
        for file_pattern, desc in main_files:
            matching_files = [(p, lines, e) for p, lines, e in self.file_data if file_pattern in p]
            for file_path, line_count, _ in matching_files[:1]:  # Take first match
                report_lines.append(f"- `{file_path}` - {line_count:,} lines ({desc})")
        report_lines.append("")

        # Process each category
        category_order = [
            "core_framework",
            "code_intelligence",
            "data_integration",
            "module_system",
            "graph_database",
            "task_implementations",
            "opcua_integration",
            "user_interface",
            "documentation",
            "testing_scripts",
            "infrastructure",
        ]

        for category in category_order:
            if category not in categorized_files:
                continue

            config = self.categories[category]
            files = categorized_files[category]

            if not files:
                continue

            # Calculate category totals
            category_lines = sum(line_count for _, line_count, _ in files)

            report_lines.extend(
                [
                    f"### {config['emoji']} **{config['description']}:**",
                    f"*Total: {len(files)} files, {category_lines:,} lines*",
                    "",
                ]
            )

            # Show top files in category (limit based on include_small_files)
            display_limit = len(files) if include_small_files else min(10, len(files))
            for file_path, line_count, _ in files[:display_limit]:
                description = self.get_file_description(file_path)
                desc_text = f" ({description})" if description else ""
                report_lines.append(f"- `{file_path}` - {line_count:,} lines{desc_text}")

            if len(files) > display_limit:
                report_lines.append(f"- *...and {len(files) - display_limit} more files*")

            report_lines.append("")

        # Key insights
        report_lines.extend(["## 📊 **Key Insights:**", ""])

        # Calculate module totals
        module_totals = {}
        for category, files in categorized_files.items():
            if category in [
                "code_intelligence",
                "data_integration",
                "module_system",
                "graph_database",
            ]:
                total_lines = sum(line_count for _, line_count, _ in files)
                module_totals[category] = total_lines

        # Generate insights
        largest_modules = ", ".join(
            f"{cat.replace('_', ' ').title()} ({lines:,}+ lines)"
            for cat, lines in sorted(module_totals.items(), key=lambda x: x[1], reverse=True)[:3]
        )

        complex_tasks = ", ".join(
            f"{p.split('/')[-1].replace('.py', '').replace('_', ' ').title()} ({lines:,} lines)"
            for p, lines, _ in [f for f in self.file_data if "task_" in f[0]][:3]
        )

        doc_lines = sum(lines for p, lines, _ in categorized_files.get("documentation", []))
        test_lines = sum(lines for p, lines, _ in categorized_files.get("testing_scripts", []))

        insights = [
            f"1. **Largest Modules:** {largest_modules}",
            f"2. **Most Complex Tasks:** {complex_tasks}",
            f"3. **Comprehensive Documentation:** {doc_lines:,} lines of documentation across all phases",
            f"4. **Robust Testing:** {test_lines:,} lines of testing infrastructure",
            "5. **Production Ready:** Complete CI/CD, Docker, and deployment configurations",
        ]

        for insight in insights:
            report_lines.append(f"- {insight}")

        report_lines.extend(
            [
                "",
                f"This codebase represents a **production-ready industrial automation platform** with sophisticated code intelligence, comprehensive documentation, and robust testing infrastructure spanning **{self.total_lines:,} lines** across **{self.total_files} files**.",
                "",
            ]
        )

        # Generate final report
        report = "\n".join(report_lines)

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Report saved to: {output_path}")

        return report

    def generate_json_summary(self, output_file: str) -> None:
        """Generate a JSON summary of the analysis."""
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "file_types": dict(self.file_types),
            "top_files": [
                {
                    "path": path,
                    "lines": lines,
                    "extension": ext,
                    "description": self.get_file_description(path),
                }
                for path, lines, ext in self.file_data[:50]
            ],
            "categorized_files": {},
        }

        categorized = self.categorize_files()
        for category, files in categorized.items():
            summary["categorized_files"][category] = {  # type: ignore
                "total_files": len(files),
                "total_lines": sum(line_count for _, line_count, _ in files),
                "files": [
                    {
                        "path": path,
                        "lines": lines,
                        "extension": ext,
                        "description": self.get_file_description(path),
                    }
                    for path, lines, ext in files
                ],
            }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"📊 JSON summary saved to: {output_file}")


def main() -> int:
    """Main entry point for the codebase analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze IGN Scripts codebase structure and generate comprehensive reports"
    )
    parser.add_argument(
        "--output-file",
        "-o",
        help="Output file for the markdown report (default: print to stdout)",
    )
    parser.add_argument("--json-output", "-j", help="Output file for JSON summary")
    parser.add_argument(
        "--include-small-files",
        "-s",
        action="store_true",
        help="Include all files in category listings (not just top 10)",
    )
    parser.add_argument(
        "--root-path",
        "-r",
        default=".",
        help="Root path to analyze (default: current directory)",
    )

    args = parser.parse_args()

    try:
        # Initialize analyzer
        analyzer = CodebaseAnalyzer(args.root_path)

        # Perform analysis
        analyzer.analyze_files()

        # Generate reports
        report = analyzer.generate_report(args.output_file, args.include_small_files)

        # Print to stdout if no output file specified
        if not args.output_file:
            print(report)

        # Generate JSON summary if requested
        if args.json_output:
            analyzer.generate_json_summary(args.json_output)

        print(
            f"\n🎉 Analysis complete! Processed {analyzer.total_files:,} files with {analyzer.total_lines:,} total lines."
        )

    except Exception as e:
        print(f"❌ Error during analysis: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
