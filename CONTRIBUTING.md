# Contributing to AI Research Framework

Thank you for your interest in contributing to the AI Research Framework! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- UV package manager
- Git
- Basic knowledge of FastAPI, async Python, and historical research

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/ai-research-framework.git
   cd ai-research-framework
   ```

2. **Install UV package manager**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run tests to verify setup**:
   ```bash
   uv run pytest
   ```

## 🛠️ Development Workflow

### Using Claude Code

This project is optimized for development with Claude Code. We provide specialized agent configurations:

- **Research Agent**: For historical research and source validation
- **Data Processing Agent**: For document processing and OCR improvements
- **API Integration Agent**: For API development and external service integration
- **Testing Agent**: For test development and quality assurance
- **Deployment Agent**: For deployment and infrastructure management
- **Documentation Agent**: For documentation updates and maintenance

To use Claude Code effectively:

1. Read the `CLAUDE.md` file for general instructions
2. Use the appropriate agent from `.claude/agents/` for specific tasks
3. Follow the agent's specialized guidelines and best practices

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical production fixes

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Run tests and linting**:
   ```bash
   uv run pytest
   uv run black .
   uv run isort .
   uv run flake8
   uv run mypy src/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use Black for code formatting (line length: 88)
- Use isort for import sorting
- Use type hints for all functions and methods
- Write docstrings for all public functions, classes, and modules

### Code Organization

```python
"""Module docstring describing the purpose."""

import standard_library_imports
import third_party_imports

from local_imports import something
from ..relative_imports import something_else

# Constants
CONSTANT_VALUE = "value"

class ExampleClass:
    """Class docstring."""
    
    def __init__(self, param: str) -> None:
        """Initialize the class."""
        self.param = param
    
    def public_method(self, arg: int) -> str:
        """Public method with type hints and docstring."""
        return self._private_method(arg)
    
    def _private_method(self, arg: int) -> str:
        """Private method."""
        return f"{self.param}: {arg}"

async def async_function(param: str) -> dict:
    """Async function example."""
    return {"result": param}
```

### Documentation

- Use Google-style docstrings
- Include type information in docstrings
- Provide examples for complex functions
- Update README.md for significant changes

### Testing

- Write unit tests for all new functionality
- Use pytest for testing framework
- Aim for >90% code coverage
- Include integration tests for API endpoints
- Mock external dependencies

Example test structure:
```python
import pytest
from unittest.mock import Mock, patch

from ai_research_framework.module import function_to_test

class TestFunctionToTest:
    """Test class for function_to_test."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = function_to_test("input")
        assert result == "expected_output"
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality."""
        result = await async_function_to_test("input")
        assert result["key"] == "value"
    
    @patch('ai_research_framework.module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependency."""
        mock_dependency.return_value = "mocked_result"
        result = function_to_test("input")
        assert result == "expected_with_mock"
```

## 🧪 Testing Guidelines

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Performance Tests**: Test performance characteristics
- **End-to-End Tests**: Test complete workflows

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "not slow"

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run performance tests
uv run pytest -m performance --benchmark-only
```

### Test Data

- Use fixtures for test data
- Store test files in `tests/fixtures/`
- Use factories for creating test objects
- Clean up test data after tests

## 📚 Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings and inline comments
2. **API Documentation**: Automatically generated from code
3. **User Documentation**: Guides and tutorials
4. **Developer Documentation**: Architecture and design decisions

### Documentation Standards

- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include examples and use cases
- Provide troubleshooting information

## 🔍 Code Review Process

### Before Submitting

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No sensitive information in code
- [ ] Performance impact considered

### Review Criteria

- **Functionality**: Does the code work as intended?
- **Design**: Is the code well-structured and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security implications?

## 🐛 Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, package versions
- **Logs**: Relevant log messages or error traces

Use the bug report template:

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.0]
- Package Version: [e.g., 0.1.0]

## Additional Context
Any additional information, logs, or screenshots
```

## 💡 Feature Requests

For feature requests, please include:

- **Use Case**: Why is this feature needed?
- **Description**: Detailed description of the feature
- **Alternatives**: Alternative solutions considered
- **Implementation**: Suggested implementation approach

## 🏛️ Historical Research Guidelines

### Source Evaluation

When contributing historical research features:

- **Primary Sources**: Prioritize inscriptions, manuscripts, archaeological evidence
- **Secondary Sources**: Use peer-reviewed academic publications
- **Credibility Assessment**: Implement bias detection and source verification
- **Citation Standards**: Follow academic citation formats
- **Cultural Sensitivity**: Respect cultural and religious sensitivities

### Language Support

- **Sanskrit**: Support Devanagari script and transliteration
- **Regional Languages**: Support major Indian languages
- **Translation**: Provide accurate translations with context
- **Terminology**: Maintain consistent terminology across the system

## 📞 Getting Help

- **Documentation**: Check the docs/ directory
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Claude Code**: Use the specialized agents for development help

## 🙏 Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes for significant contributions
- Documentation acknowledgments

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the AI Research Framework! Your efforts help preserve and share the rich history of ancient India.

