# 📊 IGN Scripts Codebase Analyzer

A comprehensive Python script that analyzes the entire IGN Scripts codebase structure, counts lines per file, categorizes components, and generates detailed reports with insights.

## 🚀 Features

- **Comprehensive File Analysis**: Scans all project files and counts lines
- **Smart Categorization**: Automatically categorizes files by functionality (Core Framework, Code Intelligence, Data Integration, etc.)
- **Multiple Output Formats**: Generate both Markdown reports and JSON summaries
- **Detailed Insights**: Provides key statistics and project insights
- **Configurable Output**: Control detail level and output destinations
- **Production Ready**: Handles large codebases efficiently with proper error handling

## 📋 Usage

### Basic Usage
```bash
# Generate report to stdout
python scripts/codebase_analyzer.py

# Save report to file
python scripts/codebase_analyzer.py --output-file reports/analysis.md

# Generate both markdown and JSON reports
python scripts/codebase_analyzer.py --output-file reports/analysis.md --json-output reports/analysis.json
```

### Advanced Options
```bash
# Include all files in category listings (not just top 10)
python scripts/codebase_analyzer.py --include-small-files

# Analyze a different directory
python scripts/codebase_analyzer.py --root-path /path/to/project

# Full example with all options
python scripts/codebase_analyzer.py \
    --output-file reports/full_analysis.md \
    --json-output reports/full_analysis.json \
    --include-small-files \
    --root-path .
```

## 🎯 Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output-file` | `-o` | Output file for the markdown report (default: print to stdout) |
| `--json-output` | `-j` | Output file for JSON summary |
| `--include-small-files` | `-s` | Include all files in category listings (not just top 10) |
| `--root-path` | `-r` | Root path to analyze (default: current directory) |
| `--help` | `-h` | Show help message and exit |

## 📁 File Categories

The analyzer automatically categorizes files into the following groups:

### 🏗️ Core Framework
- `src/core/` - Core CLI and framework components

### 📊 Code Intelligence (Phase 8)
- `src/ignition/code_intelligence/` - AI-powered code analysis and refactoring

### 📈 Data Integration (Phase 3)
- `src/ignition/data_integration/` - Database connections and data management

### 🔧 Module System (Phase 9)
- `src/ignition/modules/` - Ignition module development framework

### 🌐 Graph Database System
- `src/ignition/graph/` - Neo4j integration and graph operations

### 🏭 Task System Implementations
- `src/ignition/graph/tasks/` - Individual task implementations

### 🔌 OPC-UA Integration
- `src/ignition/opcua/` - OPC-UA client and server functionality

### 🖥️ User Interface
- `src/ui/` - Streamlit and web interfaces

### 📚 Documentation Structure
- `docs/` - All project documentation

### 🧪 Testing & Scripts
- `scripts/testing/`, `tests/` - Testing infrastructure and utilities

### 🏗️ Infrastructure Files
- Configuration files, Docker, CI/CD, and requirements

## 📊 Sample Output

```
📊 IGN Scripts Codebase Analysis
🔢 Total Statistics:
- Total Files: 403 project files
- Total Lines: 478,143 lines of code
- Major File Types: .py (222), .md (110), .json (45), .txt (10), .sh (10)

📁 Top Largest Files by Line Count:
- .file_hash_manifest.json - 233,834 lines (Git hash tracking)
- neo4j/fullbackup/ign_scripts_db_backup_20250617_145940.json - 112,188 lines (Database backup)
- ruff_analysis.json - 15,993 lines (Code analysis results)

🏗️ Core Source Code Structure:
### 📊 Code Intelligence (Phase 8):
Total: 20 files, 11,354 lines
- src/ignition/code_intelligence/cli_commands.py - 924 lines (CLI commands)
- src/ignition/code_intelligence/refactoring_tracker.py - 878 lines
...

📊 Key Insights:
- Largest Modules: Graph Database (25,889+ lines), Code Intelligence (11,354+ lines)
- Most Complex Tasks: Task 6 Utility System Backup (1,735 lines)
- Comprehensive Documentation: 26,379 lines of documentation
- Robust Testing: 5,365 lines of testing infrastructure
```

## 🔧 Technical Details

### File Filtering
The analyzer includes these file types:
- `.py` - Python source files
- `.md` - Markdown documentation
- `.yml`, `.yaml` - YAML configuration files
- `.json` - JSON data and configuration files
- `.txt` - Text files
- `.sh` - Shell scripts
- `.sql` - SQL files
- `.toml` - TOML configuration files
- `.lock` - Dependency lock files
- `.env`, `.cfg`, `.conf` - Configuration files

### Exclusion Patterns
The following directories are automatically excluded:
- `.venv` - Virtual environment
- `.git` - Git repository data
- `node_modules` - Node.js dependencies
- `__pycache__` - Python cache files
- `.mypy_cache`, `.pytest_cache` - Tool cache directories
- `tools`, `graph-data`, `test-results`, `coverage-reports` - Generated data

## 📈 JSON Output Structure

The JSON output includes:
```json
{
  "analysis_date": "2025-06-19T16:01:00.222216",
  "total_files": 403,
  "total_lines": 478143,
  "file_types": {".py": 222, ".md": 110, ...},
  "top_files": [
    {
      "path": "file.py",
      "lines": 1000,
      "extension": ".py",
      "description": "File description"
    }
  ],
  "categorized_files": {
    "category_name": {
      "total_files": 10,
      "total_lines": 5000,
      "files": [...]
    }
  }
}
```

## 🎯 Use Cases

1. **Project Overview**: Get a comprehensive view of codebase structure and size
2. **Technical Documentation**: Generate reports for documentation and presentations
3. **Code Review**: Identify largest files and modules for refactoring priorities
4. **Project Planning**: Understand the scope and complexity of different components
5. **Compliance Reporting**: Generate detailed metrics for project stakeholders
6. **Maintenance Planning**: Identify areas with high line counts that may need attention

## 🔍 Examples

### Generate Weekly Report
```bash
# Create weekly codebase analysis report
python scripts/codebase_analyzer.py \
    --output-file "reports/weekly_analysis_$(date +%Y%m%d).md" \
    --json-output "reports/weekly_analysis_$(date +%Y%m%d).json"
```

### Compare Project Sizes
```bash
# Analyze different project phases
python scripts/codebase_analyzer.py --root-path src/ignition/code_intelligence
python scripts/codebase_analyzer.py --root-path src/ignition/data_integration
```

### Full Detailed Analysis
```bash
# Generate comprehensive analysis with all files included
python scripts/codebase_analyzer.py \
    --output-file reports/comprehensive_analysis.md \
    --json-output reports/comprehensive_analysis.json \
    --include-small-files
```

## 🐛 Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the script has read permissions for all directories
2. **Encoding Issues**: The script handles UTF-8 encoding errors gracefully
3. **Large Files**: Very large files are processed efficiently with streaming

### Performance Notes

- Processing 400+ files with 475K+ lines typically takes 2-3 seconds
- JSON output generation adds minimal overhead
- Memory usage scales with the number of files, not total line count

## 🤝 Contributing

To extend the analyzer:

1. **Add New Categories**: Update the `categories` dictionary in the `CodebaseAnalyzer` class
2. **Custom Descriptions**: Extend the `get_file_description()` method
3. **New File Types**: Add extensions to `include_extensions` set
4. **Custom Insights**: Modify the insights generation in `generate_report()`

## 📝 License

This script is part of the IGN Scripts project and follows the same licensing terms.
