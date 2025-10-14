# Contributing to AI Stock Trading Bot

Thank you for your interest in contributing to the AI Stock Trading Bot project! This document provides guidelines and instructions for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Reporting Bugs](#reporting-bugs)
5. [Requesting Features](#requesting-features)
6. [Submitting Pull Requests](#submitting-pull-requests)
7. [Development Setup](#development-setup)
8. [Code Style Guidelines](#code-style-guidelines)
9. [Testing Requirements](#testing-requirements)
10. [Documentation Standards](#documentation-standards)
11. [Commit Message Guidelines](#commit-message-guidelines)
12. [Review Process](#review-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity
- Sexual orientation
- Disability
- Personal appearance
- Race or ethnicity
- Age
- Religion

### Expected Behavior

- Be respectful and considerate in all interactions
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the project
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory language
- Personal attacks or political discussions
- Publishing others' private information
- Spam or excessive self-promotion
- Any conduct that disrupts the project

**Enforcement**: Violations may result in temporary or permanent bans from the project.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.13+ installed
- Git installed and configured
- GitHub account set up
- Basic understanding of:
  - Python programming
  - Git/GitHub workflow
  - Trading concepts (optional but helpful)

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork:
   git clone https://github.com/YOUR_USERNAME/ai-stock-trading-bot.git
   cd ai-stock-trading-bot
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/foxsake123/ai-stock-trading-bot.git
   git fetch upstream
   ```

3. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Linux/Mac:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

5. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

6. **Run Tests**
   ```bash
   pytest tests/ -v
   # Ensure all tests pass before making changes
   ```

---

## How to Contribute

### Types of Contributions

We welcome contributions in these areas:

**1. Bug Fixes**
- Fix identified bugs in existing code
- Improve error handling
- Address edge cases

**2. New Features**
- Implement requested features from Issues
- Add new trading strategies
- Enhance reporting capabilities
- Improve performance

**3. Documentation**
- Fix typos or unclear documentation
- Add examples and tutorials
- Improve code comments
- Update README and guides

**4. Testing**
- Write new tests for uncovered code
- Improve existing tests
- Add integration tests
- Performance testing

**5. Code Quality**
- Refactor code for clarity
- Optimize performance
- Fix code style violations
- Improve type hints

---

## Reporting Bugs

### Before Reporting

1. **Search Existing Issues**: Check if bug already reported
2. **Update to Latest**: Verify bug exists in latest version
3. **Reproduce Consistently**: Ensure bug is repeatable
4. **Check Documentation**: Verify it's not expected behavior

### Bug Report Template

Create a new issue with this information:

```markdown
## Bug Description
[Clear, concise description of the bug]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- OS: [Windows 11 / Ubuntu 22.04 / macOS 13]
- Python Version: [3.13.3]
- Branch/Commit: [master / commit hash]
- Dependencies: [Output of `pip freeze`]

## Error Messages
```
[Paste full error message and traceback]
```

## Screenshots
[If applicable, add screenshots]

## Additional Context
[Any other relevant information]

## Possible Solution
[If you have ideas for fixing it]
```

### Severity Labels

Use these labels when reporting:
- `critical`: System crash, data loss, security issue
- `high`: Major feature broken, impacts many users
- `medium`: Minor feature broken, workaround exists
- `low`: Cosmetic issue, minor inconvenience

---

## Requesting Features

### Before Requesting

1. **Check Existing Requests**: Search issues for similar requests
2. **Consider Scope**: Is this appropriate for the project?
3. **Think Through Requirements**: What exactly do you need?

### Feature Request Template

```markdown
## Feature Description
[Clear, concise description of the feature]

## Problem Statement
[What problem does this solve?]

## Proposed Solution
[How would you implement this?]

## Alternatives Considered
[What other approaches did you consider?]

## Use Cases
1. Use case one
2. Use case two

## Benefits
- Benefit one
- Benefit two

## Implementation Complexity
[Easy / Medium / Hard]

## Additional Context
[Mockups, examples, references]

## Willing to Implement?
[Yes / No / With guidance]
```

### Feature Prioritization

Features are prioritized based on:
- Alignment with project goals
- Number of users affected
- Implementation complexity
- Available resources

---

## Submitting Pull Requests

### Before You Start

1. **Open an Issue First**: Discuss major changes before coding
2. **Get Assignment**: Wait for maintainer to assign issue
3. **Check for Duplicates**: Ensure no one else is working on it

### PR Workflow

**1. Create a Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-123-description
```

**Branch Naming Convention:**
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions

**2. Make Your Changes**
```bash
# Edit files
# Follow code style guidelines (see below)
```

**3. Write/Update Tests**
```bash
# Add tests for new code
pytest tests/ -v

# Check coverage
pytest tests/ --cov=. --cov-report=html
```

**4. Update Documentation**
```bash
# Update README.md if needed
# Add docstrings to new functions
# Update CHANGELOG.md
```

**5. Commit Your Changes**
```bash
git add .
git commit -m "feat: add new feature description"
# See commit guidelines below
```

**6. Push to Your Fork**
```bash
git push origin feature/your-feature-name
```

**7. Create Pull Request**
- Go to GitHub and click "New Pull Request"
- Fill out PR template (see below)
- Link related issue(s)
- Request review from maintainers

### Pull Request Template

```markdown
## Description
[Clear description of changes]

## Related Issue
Fixes #123
Closes #456

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Changes Made
- Change one
- Change two
- Change three

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for changes
- [ ] Manual testing completed
- [ ] Coverage maintained or improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] CHANGELOG.md updated

## Screenshots
[If applicable]

## Additional Notes
[Any other information for reviewers]
```

---

## Development Setup

### Directory Structure

```
ai-stock-trading-bot/
├── agents/                 # Multi-agent system
│   ├── base_agent.py
│   ├── bull_researcher.py
│   ├── bear_researcher.py
│   └── ...
├── scripts/
│   ├── automation/        # Trading automation
│   ├── utilities/         # Helper scripts
│   └── windows/           # Windows batch files
├── tests/                 # Test suite
│   ├── conftest.py
│   ├── test_schedule_config.py
│   └── ...
├── docs/                  # Documentation
├── examples/              # Example files
├── data/                  # Data storage
├── reports/               # Generated reports
└── main.py               # Entry point
```

### Development Dependencies

```bash
# Install all development dependencies
pip install -r requirements-dev.txt

# Includes:
# - pytest: Testing framework
# - pytest-cov: Coverage reporting
# - pytest-mock: Mocking utilities
# - black: Code formatting
# - flake8: Linting
# - mypy: Type checking
# - pre-commit: Git hooks
```

### Pre-Commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks run automatically on `git commit`:
- black (code formatting)
- flake8 (linting)
- mypy (type checking)
- trailing-whitespace check
- end-of-file-fixer

### Running the System

```bash
# Generate test report
python daily_premarket_report.py --test

# Execute trades (paper trading only!)
python scripts/automation/execute_daily_trades.py

# Start web dashboard
python web_dashboard.py

# Run health check
python health_check.py --verbose
```

---

## Code Style Guidelines

### Python Style Guide

Follow [PEP 8](https://peps.python.org/pep-0008/) with these specifics:

**1. Formatting**
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **88 characters** (black default)
- Use **double quotes** for strings
- One import per line

**2. Naming Conventions**
```python
# Classes: PascalCase
class TradingAgent:
    pass

# Functions/variables: snake_case
def calculate_position_size(portfolio_value):
    max_risk = 0.02
    return portfolio_value * max_risk

# Constants: UPPER_SNAKE_CASE
MAX_POSITION_SIZE = 0.15
API_TIMEOUT = 30

# Private: prefix with underscore
def _internal_helper():
    pass
```

**3. Docstrings**
```python
def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio for a series of returns.

    Args:
        returns: List of period returns (decimal form)
        risk_free_rate: Annual risk-free rate (default: 0.02 = 2%)

    Returns:
        Sharpe ratio as a float

    Raises:
        ValueError: If returns list is empty

    Example:
        >>> returns = [0.05, 0.03, -0.02, 0.07]
        >>> sharpe = calculate_sharpe_ratio(returns)
        >>> print(f"Sharpe: {sharpe:.2f}")
        Sharpe: 1.45
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")

    # Implementation...
```

**4. Type Hints**
```python
from typing import List, Dict, Optional, Union

def fetch_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Union[float, str]]:
    """Fetch stock data with type hints."""
    pass
```

**5. Imports**
```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import pandas as pd
import numpy as np
from anthropic import Anthropic

# Local
from agents.base_agent import BaseAgent
from utils.helpers import calculate_returns
```

### Code Formatting

**Use black for automatic formatting:**
```bash
# Format single file
black daily_premarket_report.py

# Format entire project
black .

# Check without modifying
black --check .
```

### Linting

**Use flake8 for linting:**
```bash
# Lint entire project
flake8 .

# Lint specific file
flake8 agents/bull_researcher.py

# Configuration in .flake8 or setup.cfg
```

### Type Checking

**Use mypy for type checking:**
```bash
# Check entire project
mypy .

# Check specific file
mypy agents/risk_manager.py

# Ignore specific errors
# type: ignore
```

---

## Testing Requirements

### Test Coverage Requirements

- **Minimum Coverage**: 50% overall
- **New Code**: 80% coverage required
- **Critical Functions**: 100% coverage required

### Writing Tests

**1. Test File Structure**
```python
"""
Tests for module_name.py
Brief description of what is tested.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import module to test
from module_name import function_to_test


class TestClassName:
    """Test specific class or functionality."""

    @pytest.mark.unit
    def test_function_with_valid_input(self, fixture_name):
        """Test that function works with valid input."""
        # Arrange
        input_value = "test"

        # Act
        result = function_to_test(input_value)

        # Assert
        assert result == expected_value
```

**2. Test Markers**
```python
@pytest.mark.unit        # Fast unit tests
@pytest.mark.integration # Integration tests
@pytest.mark.slow        # Slow tests
@pytest.mark.requires_api # Requires API keys
```

**3. Fixtures**
```python
# In conftest.py
@pytest.fixture
def mock_market_data():
    """Provide mock market data for tests."""
    return {
        "VIX": {"price": 15.23, "change": -0.45},
        "SPY": {"price": 450.25, "change": 0.15}
    }
```

**4. Running Tests**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_schedule_config.py -v

# Run tests by marker
pytest tests/ -m unit -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_file.py::TestClass::test_method -v
```

---

## Documentation Standards

### Code Documentation

**1. Module Docstrings**
```python
"""
Module: agents/bull_researcher.py

This module contains the Bull Researcher agent responsible for
analyzing stocks from an optimistic perspective.

Classes:
    BullResearcher: Main agent class

Functions:
    analyze_growth_potential: Evaluate stock upside
"""
```

**2. Function Docstrings**
- Use Google-style docstrings
- Include Args, Returns, Raises
- Add examples when helpful

**3. Inline Comments**
```python
# Good: Explain WHY, not WHAT
# Calculate position size based on 2% risk per trade
position_size = portfolio * 0.02

# Bad: State the obvious
# Set x to 10
x = 10
```

### README Updates

Update README.md when:
- Adding new features
- Changing installation steps
- Updating dependencies
- Modifying configuration

### CHANGELOG Updates

Add entry to CHANGELOG.md for:
- New features (`### Added`)
- Bug fixes (`### Fixed`)
- Breaking changes (`### Changed`)
- Deprecated features (`### Deprecated`)

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build/config changes

### Examples

**Simple commit:**
```
feat: add Slack notification support
```

**With scope:**
```
fix(schedule): handle holiday edge cases correctly
```

**With body:**
```
feat: add performance benchmarking

Implement comprehensive benchmarking system to compare
strategy performance against S&P 500 and calculate alpha.

Includes:
- Daily performance tracking
- Alpha calculation
- Sharpe ratio comparison
```

**Breaking change:**
```
feat!: change API response format

BREAKING CHANGE: API now returns dict instead of tuple.
Update all callers to use new format.
```

---

## Review Process

### What Reviewers Look For

1. **Correctness**: Does code work as intended?
2. **Tests**: Adequate test coverage?
3. **Style**: Follows code style guidelines?
4. **Documentation**: Properly documented?
5. **Performance**: No obvious inefficiencies?
6. **Security**: No security vulnerabilities?

### Response Time

- **Initial Review**: Within 3 business days
- **Follow-up**: Within 1 business day
- **Approval**: When all requirements met

### Addressing Feedback

```bash
# Make requested changes
git add .
git commit -m "fix: address review feedback"
git push origin feature/your-feature
# PR automatically updates
```

### Merge Criteria

PR will be merged when:
- [ ] All tests pass
- [ ] Code review approved by maintainer
- [ ] CI/CD checks pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] No merge conflicts

---

## Getting Help

### Resources

- **Documentation**: Check `/docs` folder first
- **Examples**: See `/examples` folder
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions

### Contact

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a GitHub Issue
- **Security**: Email security concerns privately (see SECURITY.md)

---

## Recognition

### Contributors

All contributors are recognized in:
- GitHub Contributors page
- CONTRIBUTORS.md file
- Release notes

### Hall of Fame

Outstanding contributors may be featured in project README.

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

**Thank you for contributing to AI Stock Trading Bot!** 🚀📈

Your contributions help make automated trading more accessible and transparent.

---

*Last Updated: October 13, 2025*
*Version: 2.0*
