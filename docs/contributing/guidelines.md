# Contributing Guidelines

Welcome to the IGN Scripts project! We're excited that you're interested in contributing. This document provides guidelines and information for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation Guidelines](#documentation-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Release Process](#release-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, or identity.

### Expected Behavior

- **Be respectful**: Treat all community members with respect and kindness
- **Be collaborative**: Work together constructively and share knowledge
- **Be inclusive**: Welcome newcomers and help them get started
- **Be professional**: Maintain a professional tone in all interactions

### Unacceptable Behavior

- Harassment, discrimination, or inappropriate comments
- Personal attacks or inflammatory language
- Spam, trolling, or disruptive behavior
- Any behavior that would be inappropriate in a professional setting

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug reports**: Help us identify and fix issues
- **Feature requests**: Suggest new functionality or improvements
- **Code contributions**: Submit bug fixes, new features, or improvements
- **Documentation**: Improve or expand documentation
- **Testing**: Add or improve test coverage
- **Examples**: Contribute script examples and templates

### Before Contributing

1. **Check existing issues**: Look for existing issues or discussions about your topic
2. **Create an issue**: For significant changes, create an issue to discuss the approach
3. **Fork the repository**: Create your own fork to work on changes
4. **Read the documentation**: Familiarize yourself with the project structure and goals

## Development Setup

### Prerequisites

- **Python 3.11+**: Required for development
- **uv**: Python package installer and environment manager
- **Git**: Version control system
- **Docker**: For testing and development environments

### Initial Setup

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ignition_tools.git
   cd ignition_tools
   ```

2. **Set up development environment**:
   ```bash
   # Create virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -r requirements.txt
   uv pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Verify setup**:
   ```bash
   # Run tests
   pytest tests/
   
   # Run linting
   ruff check .
   ruff format --check .
   
   # Run CLI to verify installation
   python -m src.main --help
   
   # Test UI entry point
   python -c "from src.ui.app import main; print('UI entry point ready')"
   ```

### Environment Configuration

Create a `.env` file for local development:

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
# Note: Never commit real credentials to the repository
```

## Coding Standards

### Python Code Standards

- **PEP 8 compliance**: Follow Python style guidelines
- **Type hints**: Use type hints for all function parameters and return values
- **Docstrings**: Include comprehensive docstrings for all public functions and classes
- **Error handling**: Implement proper exception handling with specific error types
- **Logging**: Use structured logging instead of print statements

### Jython-Specific Standards

- **Compatibility**: Ensure generated Jython code works with Jython 2.7
- **Ignition context**: Consider the target Ignition context (Gateway, Vision, Perspective)
- **Error handling**: Include Ignition-appropriate error handling patterns
- **Documentation**: Document Ignition-specific considerations and limitations

### Code Examples

#### Python Function with Type Hints and Docstring

```python
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def generate_tag_script(
    tag_path: str,
    script_type: str,
    parameters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a Jython script for tag operations.
    
    Args:
        tag_path: The OPC tag path for the script
        script_type: Type of script ('read', 'write', 'subscribe')
        parameters: Optional parameters for script configuration
        
    Returns:
        Generated Jython script as string
        
    Raises:
        ValueError: If tag_path is invalid or script_type is unsupported
        TemplateError: If template generation fails
        
    Example:
        >>> script = generate_tag_script(
        ...     tag_path="[PLC]Production/Line1/Speed",
        ...     script_type="read",
        ...     parameters={"polling_rate": 1000}
        ... )
        >>> print(script)
    """
    if not tag_path:
        raise ValueError("tag_path cannot be empty")
    
    if script_type not in ['read', 'write', 'subscribe']:
        raise ValueError(f"Unsupported script_type: {script_type}")
    
    logger.info(f"Generating {script_type} script for tag: {tag_path}")
    
    try:
        # Implementation here
        script = f"# Generated {script_type} script for {tag_path}"
        return script
    except Exception as e:
        logger.error(f"Failed to generate script: {e}")
        raise TemplateError(f"Script generation failed: {e}") from e
```

### File Organization

- **Module structure**: Follow the established `src/` directory structure
- **Import organization**: Use absolute imports and organize import statements
- **File naming**: Use snake_case for Python files, descriptive names
- **Directory structure**: Group related functionality in appropriate subdirectories

## Testing Guidelines

### Testing Requirements

- **Test coverage**: Aim for 80%+ test coverage for new code
- **Test types**: Include unit tests, integration tests, and end-to-end tests
- **Test documentation**: Document test scenarios and expected behavior
- **Mock external dependencies**: Use mocking for external services and APIs

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from src.generators.tag_scripts import TagScriptGenerator

class TestTagScriptGenerator:
    """Test suite for TagScriptGenerator."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.generator = TagScriptGenerator()
        
    def test_generate_read_script_success(self):
        """Test successful generation of tag read script."""
        # Arrange
        tag_path = "[PLC]Production/Line1/Speed"
        expected_content = "system.tag.readBlocking"
        
        # Act
        result = self.generator.generate_read_script(tag_path)
        
        # Assert
        assert expected_content in result
        assert tag_path in result
        
    def test_generate_read_script_invalid_path(self):
        """Test error handling for invalid tag path."""
        # Arrange
        invalid_path = ""
        
        # Act & Assert
        with pytest.raises(ValueError, match="tag_path cannot be empty"):
            self.generator.generate_read_script(invalid_path)
            
    @patch('src.generators.tag_scripts.system_tag_client')
    def test_generate_with_mocked_dependency(self, mock_client):
        """Test script generation with mocked external dependency."""
        # Arrange
        mock_client.validate_path.return_value = True
        tag_path = "[PLC]Test/Tag"
        
        # Act
        result = self.generator.generate_read_script(tag_path)
        
        # Assert
        mock_client.validate_path.assert_called_once_with(tag_path)
        assert result is not None
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tag_scripts.py

# Run tests with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_tag_script"
```

## Documentation Guidelines

### Documentation Standards

- **Clarity**: Write clear, concise documentation that's easy to understand
- **Examples**: Include practical examples and code snippets
- **Completeness**: Document all public APIs, configuration options, and features
- **Maintenance**: Keep documentation updated with code changes

### Documentation Types

1. **API Documentation**: Docstrings in code, generated reference docs
2. **User Guides**: Step-by-step instructions for common tasks
3. **Developer Documentation**: Architecture, design decisions, contribution guides
4. **Examples**: Sample scripts, configuration files, use cases

### Markdown Standards

```markdown
# Main Heading (H1)

Brief introduction or overview.

## Section Heading (H2)

### Subsection (H3)

- Use bullet points for lists
- Include code blocks with language specification
- Add links to related documentation

#### Code Example

```python
# Always include language specification
def example_function():
    """Include docstrings in examples."""
    return "Hello, World!"
```

#### Configuration Example

```yaml
# Include comments in configuration examples
database:
  host: localhost  # Database server hostname
  port: 5432      # Database server port
```
```

## Pull Request Process

### Before Submitting

1. **Update your fork**: Ensure your fork is up to date with the main repository
2. **Create feature branch**: Create a descriptive branch name
3. **Test your changes**: Run the full test suite and ensure all tests pass
4. **Update documentation**: Update relevant documentation for your changes
5. **Check code quality**: Ensure code passes all linting and formatting checks

### Pull Request Checklist

- [ ] **Tests**: All tests pass locally
- [ ] **Linting**: Code passes ruff check and format
- [ ] **Type checking**: Code passes mypy validation
- [ ] **Documentation**: Documentation updated for changes
- [ ] **Changelog**: Added entry to changelog (if applicable)
- [ ] **Backward compatibility**: Changes don't break existing functionality
- [ ] **Performance**: Changes don't significantly impact performance

### Pull Request Template

```markdown
## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Added tests for new functionality
- [ ] All existing tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated
- [ ] Changes generate no new warnings
```

### Review Process

1. **Automated checks**: All CI/CD checks must pass
2. **Code review**: At least one maintainer review required
3. **Testing**: Reviewer will test changes if applicable
4. **Documentation review**: Documentation changes reviewed for clarity
5. **Approval**: Changes approved by maintainer
6. **Merge**: Pull request merged by maintainer

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version**: Update version numbers in relevant files
2. **Update changelog**: Document all changes since last release
3. **Test release**: Run full test suite and manual testing
4. **Create release**: Create GitHub release with notes
5. **Deploy**: Deploy to package repositories if applicable

## Getting Help

### Community Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Check existing documentation first
- **Code Examples**: Review examples in the repository

### Maintainer Contact

For questions about contributing or project direction:

- **GitHub Issues**: Best for public discussion
- **Project Maintainers**: Check MAINTAINERS.md for contact information

## Recognition

Contributors are recognized in several ways:

- **CONTRIBUTORS.md**: Listed in the contributors file
- **Release notes**: Mentioned in release acknowledgments
- **GitHub**: Automatic contributor recognition on GitHub

Thank you for contributing to IGN Scripts! Your contributions help make Ignition automation better for everyone.

---

*Last updated: 2025-01-28* 