# IGN Scripts - Ignition Jython Script Generator

A powerful Python application for generating, validating, and exporting Jython scripts for Ignition SCADA systems.

## 🎯 Project Overview

IGN Scripts is designed to streamline the development of Jython scripts for Ignition SCADA environments. Instead of manually writing scripts within the Ignition Designer, you can use this tool to:

- Generate Jython scripts from templates and configurations
- Validate script syntax and compatibility
- Export scripts in formats compatible with Ignition gateways
- Manage version control for Ignition projects
- Automate deployment to production environments

## 🔧 Target Environment

- **Ignition Version**: 8.1+ (primary), 8.0 (secondary)
- **Jython Version**: 2.7 (as used by Ignition)
- **Development**: Python 3.11+
- **Output**: Jython 2.7 compatible scripts

## 📋 Features (Planned)

### Script Generation
- ✅ CLI framework
- 🔄 Vision component event handlers
- 🔄 Perspective component scripts
- 🔄 Gateway startup/shutdown scripts
- 🔄 Tag event handlers
- 🔄 Timer scripts
- 🔄 Alarm pipeline scripts

### Ignition System Integration
- 🔄 `system.tag.*` wrapper functions
- 🔄 `system.db.*` utilities
- 🔄 `system.gui.*` helpers
- 🔄 `system.nav.*` navigation tools
- 🔄 `system.alarm.*` management

### Resource Management
- 🔄 UDT (User Defined Type) generators
- 🔄 Tag provider configuration
- 🔄 Device connection scripts
- 🔄 User role management
- 🔄 Security configuration

### Export & Deployment
- 🔄 Gateway resource export
- 🔄 Project backup creation
- 🔄 Version control integration
- 🔄 Automated deployment

Legend: ✅ Complete | 🔄 In Progress | ⏳ Planned

## 🚀 Quick Start

### Prerequisites

1. Python 3.11 or higher
2. uv package manager
3. Access to Ignition 8.1+ environment

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd IGN_scripts

# Set up virtual environment with uv
uv venv
source .venv/bin/activate  # On Unix-like systems
# or
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install -r requirements.txt
```

### Basic Usage

```bash
# View available commands
python -m src.core.cli --help

# List available script templates
python -m src.core.cli template list

# Generate a basic tag event script
python -m src.core.cli script generate --type tag-event --output my_script.py

# Validate a Jython script
python -m src.core.cli script validate my_script.py

# Export for Ignition deployment
python -m src.core.cli export --format ignition-project --output my_project.zip
```

## 📁 Project Structure

```
IGN_scripts/
├── src/
│   ├── core/           # Core application logic
│   ├── ignition/       # Ignition-specific modules
│   │   ├── templates/  # Jython script templates
│   │   ├── generators/ # Script generation utilities
│   │   ├── exporters/  # Gateway export tools
│   │   └── validators/ # Script validation
│   ├── api/           # External integrations
│   └── models/        # Data models
├── templates/         # Script templates
│   ├── gateway/       # Gateway script templates
│   ├── vision/        # Vision component templates
│   ├── perspective/   # Perspective script templates
│   ├── tags/          # Tag-related templates
│   └── alarms/        # Alarm system templates
├── tests/             # Test suite
├── scripts/           # Standalone utilities
├── examples/          # Example configurations
├── docs/              # Documentation
└── config/            # Configuration files
```

## 🔨 Development

### Environment Setup

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check --fix .

# Run type checking
mypy .
```

### Development Guidelines

1. **Python for Development**: Use modern Python 3.11+ features for the development environment
2. **Jython for Output**: Generated scripts must be compatible with Jython 2.7
3. **Ignition Compatibility**: All generated code must work within Ignition's scripting environment
4. **Version Control**: Use git for source control, design for Ignition project versioning

## 📚 Ignition Script Contexts

This tool supports script generation for various Ignition contexts:

### Gateway Scripts
- Startup scripts
- Shutdown scripts
- Timer scripts (fixed delay, fixed rate)
- Message handlers
- Database connection scripts

### Vision Client Scripts
- Component event handlers (actionPerformed, mouseClicked, etc.)
- Window event handlers (internalFrameOpened, etc.)
- Property change scripts
- Custom methods

### Perspective Session Scripts
- Component event handlers
- View scripts (onStartup, onShutdown)
- Session event scripts
- Custom properties

### Tag Scripts
- Value change scripts
- Quality change scripts
- Alarm scripts
- UDT parameter scripts

## 🎓 Examples

### Generate a Basic Button Click Handler

```bash
python -m src.core.cli script generate \
  --type vision-button \
  --template basic-navigation \
  --config '{"target_window": "MainMenu", "params": {}}'
```

### Create UDT Definition Scripts

```bash
python -m src.core.cli udt generate \
  --name "MotorControl" \
  --type "Industrial" \
  --parameters speed,temperature,status
```

### Export Project for Gateway

```bash
python -m src.core.cli export project \
  --source ./my_ignition_project \
  --output ./exports/production_v1.2.0.zip \
  --format gateway-import
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- [Ignition Documentation](https://docs.inductiveautomation.com/)
- [Ignition SDK](https://github.com/inductiveautomation/ignition-sdk-examples)
- [Jython Documentation](https://jython.readthedocs.io/)
- [Ignition Community Forum](https://forum.inductiveautomation.com/)

## ⚠️ Disclaimer

This is an independent project and is not affiliated with or endorsed by Inductive Automation. Ignition is a trademark of Inductive Automation.

## 📞 Support

- Check the [Issues](https://github.com/your-repo/issues) page for common problems
- Review the [Wiki](https://github.com/your-repo/wiki) for detailed documentation
- Join discussions in our [Community Forum](https://github.com/your-repo/discussions) 