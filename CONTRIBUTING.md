# Contributing to ChromaSpec

Thank you for your interest in contributing to ChromaSpec! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of color theory (helpful but not required)

### Areas for Contribution

We welcome contributions in these areas:

1. **Bug Fixes**: See issues labeled `bug`
2. **New Features**: See issues labeled `enhancement`
3. **Documentation**: See issues labeled `documentation`
4. **Tests**: Improving test coverage
5. **Performance**: Optimization opportunities
6. **Security**: Security enhancements
7. **Educational**: Learning materials and examples

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/chromaspec.git
cd chromaspec

# Add upstream remote
git remote add upstream https://github.com/MichailSemoglou/chromaspec.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install package in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
chromaspec --help
```

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files (optional)
pre-commit run --all-files
```

## Development Workflow

### 1. Create a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions/improvements
- `refactor/` - Code refactoring
- `perf/` - Performance improvements

### 2. Make Changes

Follow the [Code Style Guidelines](#code-style-guidelines) below.

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chromaspec --cov-report=html

# Run specific test file
pytest tests/test_converters.py

# Run specific test
pytest tests/test_converters.py::TestRGBToHex::test_basic_rgb

# Run without slow tests
pytest -m "not slow"
```

### 4. Check Code Quality

```bash
# Format code
black chromaspec tests

# Sort imports
isort chromaspec tests

# Lint
flake8 chromaspec tests

# Type check
mypy chromaspec --ignore-missing-imports

# Security scan
bandit -r chromaspec

# Check dependency vulnerabilities
safety check
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: describe your changes"
```

**Commit Message Guidelines**:

```
<type>: <subject>

<body>

<footer>
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Example**:

```
feat: add complementary color palette generator

Implements a new function to generate complementary color palettes
with WCAG accessibility compliance. The generator ensures proper
contrast ratios between generated colors.

Closes #123
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style Guidelines

### General Principles

- **Readability**: Code is read more often than written
- **Simplicity**: Prefer simple, clear solutions
- **Consistency**: Follow existing patterns
- **Documentation**: Document the "why", not just the "what"

### Python Style

Follow **PEP 8** with these specifics:

```python
# ✅ Good: Clear, typed, documented
def calculate_contrast_ratio(
    foreground: str,
    background: str,
    round_precision: int = 2
) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Args:
        foreground: HEX color string for text.
        background: HEX color string for background.
        round_precision: Decimal places for rounding.

    Returns:
        Contrast ratio between 1.0 and 21.0.

    Example:
        >>> calculate_contrast_ratio("#000000", "#FFFFFF")
        21.0
    """
    # Calculate luminance values
    lum1 = calculate_luminance(hex_to_rgb(foreground))
    lum2 = calculate_luminance(hex_to_rgb(background))

    # Apply WCAG formula
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    ratio = (lighter + 0.05) / (darker + 0.05)

    return round(ratio, round_precision)


# ❌ Bad: No types, unclear, undocumented
def calc(c1, c2):
    l1 = lum(c1)
    l2 = lum(c2)
    return (max(l1,l2)+0.05)/(min(l1,l2)+0.05)
```

### Formatting

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Prefer double quotes for strings
- **Imports**: Organized with isort

  ```python
  # Standard library
  import logging
  from pathlib import Path

  # Third-party
  from PIL import Image
  import numpy as np

  # Local
  from chromaspec.exceptions import ValidationError
  from chromaspec.utils import validate_hex_color
  ```

### Type Hints

**Required** for all public functions:

```python
from typing import Dict, List, Tuple, Optional

def process_colors(
    colors: Dict[str, float],
    threshold: float = 0.01,
    max_colors: Optional[int] = None
) -> List[Tuple[str, float]]:
    """Process color dictionary."""
    # Implementation
```

Use TypedDict for complex dictionaries:

```python
from typing import TypedDict

class ColorInfo(TypedDict):
    hex: str
    rgb: Tuple[int, int, int]
    frequency: float
    category: str

def analyze_color(color: str) -> ColorInfo:
    # Implementation
```

### Docstrings

Use **Google style** docstrings:

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief one-line description.

    More detailed description explaining what the function does,
    when to use it, and any important considerations.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ErrorType: When this error occurs.

    Example:
        >>> function_name("value1", "value2")
        expected_result

    Note:
        Additional information or caveats.
    """
```

### Naming Conventions

```python
# Classes: PascalCase
class ColorExtractor:
    pass

# Functions and variables: snake_case
def extract_colors(file_path: Path) -> Dict[str, float]:
    hex_colors = {}
    return hex_colors

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024
DEFAULT_TIMEOUT = 30

# Private: _leading_underscore
def _internal_helper():
    pass

class MyClass:
    def __init__(self):
        self._private_attribute = None
```

## Testing Requirements

### Test Coverage

- **Minimum**: 90% coverage for new code
- **Target**: 95%+ overall coverage
- **Required**: All public functions must have tests

### Test Structure

```python
class TestFeatureName:
    """Test suite for FeatureName."""

    def test_basic_functionality(self):
        """Test basic use case."""
        # Arrange
        input_data = create_test_data()

        # Act
        result = function_under_test(input_data)

        # Assert
        assert result == expected_value

    def test_edge_case_empty_input(self):
        """Test handling of empty input."""
        result = function_under_test([])
        assert result == []

    def test_error_handling_invalid_input(self):
        """Test error handling for invalid input."""
        with pytest.raises(ValidationError) as exc_info:
            function_under_test("invalid")

        assert "expected error message" in str(exc_info.value)

    @pytest.mark.parametrize("input_val,expected", [
        ("#FF0000", (255, 0, 0)),
        ("#00FF00", (0, 255, 0)),
        ("#0000FF", (0, 0, 255)),
    ])
    def test_multiple_inputs(self, input_val, expected):
        """Test with multiple input combinations."""
        assert hex_to_rgb(input_val) == expected
```

### Test Types Required

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component interactions
3. **Edge Cases**: Empty inputs, boundaries, extremes
4. **Error Cases**: Invalid inputs, exceptions
5. **Regression Tests**: Prevent known bugs from returning

### Fixtures

Use pytest fixtures for reusable test data:

```python
@pytest.fixture
def sample_svg_file(tmp_path):
    """Create a temporary SVG file for testing."""
    svg_content = '''
        <svg>
            <rect fill="#FF0000" width="100" height="100"/>
        </svg>
    '''
    svg_file = tmp_path / "test.svg"
    svg_file.write_text(svg_content)
    return svg_file

def test_extract_from_svg(sample_svg_file):
    """Test color extraction from SVG."""
    colors = extract_colors(sample_svg_file)
    assert "#FF0000" in colors
```

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Include examples in docstrings
- Document complex algorithms
- Explain "why", not just "what"

### User Documentation

When adding features, update:

1. **README.md**: Add usage examples
2. **API docs**: Add to appropriate section
3. **CHANGELOG.md**: Document changes
4. **Examples**: Add example scripts if applicable

### Documentation Style

- Use clear, concise language
- Include code examples
- Explain prerequisites
- Link to related documentation

## Pull Request Process

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (Black, isort)
- [ ] Type checking passes (mypy)
- [ ] Linting passes (flake8)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commits are well-written

### PR Template

When creating a PR, include:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe testing performed

## Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Code follows style guidelines
- [ ] No new warnings or errors
```

### Review Process

1. **Automated Checks**: CI/CD must pass
2. **Code Review**: At least one maintainer approval
3. **Testing**: Reviewer may test locally
4. **Discussion**: Address feedback and questions
5. **Approval**: Maintainer approves and merges

### After Merge

- Delete your feature branch
- Update local main branch
- Close related issues

## Release Process

Maintainers follow this process for releases:

### 1. Prepare Release

```bash
# Update version
# Edit pyproject.toml and chromaspec/__init__.py

# Update CHANGELOG.md with release date

# Commit changes
git commit -am "Bump version to X.Y.Z"
```

### 2. Create Tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### 3. Build and Deploy

```bash
# Build package
python -m build

# Test upload to TestPyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Upload to PyPI
twine upload dist/*
```

### 4. GitHub Release

Create release on GitHub:

- Copy CHANGELOG.md entry
- Attach wheel and source distribution
- Mark as release or pre-release

## Getting Help

### Questions?

- **Documentation**: Check README.md and docs/
- **Examples**: See examples/ directory
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions

### Stuck?

Open an issue with:

- Clear description of problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Relevant code snippets or logs

### Want to Help?

Great! Check:

- Issues labeled `good first issue`
- Issues labeled `help wanted`
- TODO items in code
- Test coverage gaps

## Recognition

Contributors are recognized in:

- CHANGELOG.md (per release)
- GitHub contributors page
- Special thanks in README.md

---

**Thank you for contributing to ChromaSpec!** Your work helps make color analysis more accessible and easier for everyone.
