# Contributing to AI Stock Trading Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)

---

## Getting Started

### Prerequisites
- Python 3.13 or higher
- Git
- Alpaca Markets API account (paper trading)
- Financial Datasets API key (optional but recommended)

### First Steps
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ai-stock-trading-bot.git`
3. Add upstream remote: `git remote add upstream https://github.com/foxsake123/ai-stock-trading-bot.git`

---

## Development Setup

### 1. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes testing, linting, etc.)
pip install -r requirements-dev.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:

```bash
# Alpaca API (Paper Trading)
ALPACA_API_KEY_DEE=your_dee_api_key
ALPACA_SECRET_KEY_DEE=your_dee_secret_key
ALPACA_API_KEY_SHORGAN=your_shorgan_api_key
ALPACA_SECRET_KEY_SHORGAN=your_shorgan_secret_key

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id

# Financial Datasets API (Optional)
FINANCIAL_DATASETS_API_KEY=your_fd_api_key

# Alpha Vantage (For S&P 500 benchmark)
ALPHA_VANTAGE_API_KEY=your_av_api_key
```

**IMPORTANT**: Never commit the `.env` file! It's already in `.gitignore`.

### 4. Verify Installation
```bash
# Run tests
pytest

# Check code style
black --check .
flake8 .

# Type checking
mypy agents/ scripts-and-data/automation/
```

---

## Project Structure

```
ai-stock-trading-bot/
├── agents/                    # Multi-agent trading system
│   ├── core/                 # Core agent implementations
│   ├── dee-bot/              # Defensive strategy agent
│   ├── shorgan-bot/          # Catalyst strategy agent
│   └── execution/            # Order execution logic
├── scripts-and-data/         # Automation and data management
│   ├── automation/           # Daily execution scripts
│   ├── backtesting/          # Backtesting engine
│   └── data/                 # Market data and reports
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── utils/                    # Utility functions
├── docs/                     # Documentation
├── configs/                  # Configuration files
└── risk/                     # Risk management
```

---

## Coding Standards

### Python Style Guide
We follow [PEP 8](https://pep8.org/) with the following tools:

**Code Formatting:**
```bash
# Auto-format code
black .

# Sort imports
isort .
```

**Linting:**
```bash
# Check for issues
flake8 .
pylint agents/ scripts-and-data/automation/
```

**Type Hints:**
- Use type hints for all function parameters and return values
- Run mypy to verify: `mypy agents/`

**Example:**
```python
from typing import Dict, List, Optional

def calculate_position_size(
    capital: float,
    risk_pct: float,
    stop_distance: float
) -> int:
    """
    Calculate position size based on risk parameters.

    Args:
        capital: Available trading capital in USD
        risk_pct: Risk percentage (0.01 = 1%)
        stop_distance: Distance to stop loss in USD

    Returns:
        Number of shares to purchase

    Raises:
        ValueError: If any parameter is negative or zero
    """
    if capital <= 0 or risk_pct <= 0 or stop_distance <= 0:
        raise ValueError("All parameters must be positive")

    shares = (capital * risk_pct) / stop_distance
    return int(shares)
```

### Docstring Format
Use Google-style docstrings:

```python
def process_trade(symbol: str, quantity: int, side: str) -> Dict:
    """
    Process a trade order through the execution engine.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        quantity: Number of shares to trade
        side: Order side ('buy', 'sell', 'short')

    Returns:
        Dictionary containing order execution details:
            - order_id: Alpaca order ID
            - filled_price: Execution price
            - status: Order status

    Raises:
        ValidationError: If parameters fail validation
        ExecutionError: If order submission fails
    """
    pass
```

### Naming Conventions
- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

---

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_risk_manager.py

# Run with coverage report
pytest --cov=agents --cov-report=html

# Run only fast tests (skip slow/integration)
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

### Writing Tests
Create tests in `tests/unit/` or `tests/integration/`:

```python
# tests/unit/agents/test_risk_manager.py
import pytest
from agents.risk_manager import RiskManager

class TestRiskManager:
    """Test suite for RiskManager class."""

    def test_calculate_position_size_valid(self):
        """Test position sizing with valid parameters."""
        rm = RiskManager(capital=100000, risk_per_trade=0.01)
        position_size = rm.calculate_position_size(stop_distance=2.0)

        assert position_size == 500  # (100000 * 0.01) / 2.0

    def test_calculate_position_size_invalid(self):
        """Test position sizing with invalid parameters."""
        rm = RiskManager(capital=100000, risk_per_trade=0.01)

        with pytest.raises(ValueError):
            rm.calculate_position_size(stop_distance=-2.0)

    @pytest.mark.integration
    def test_alpaca_connection(self):
        """Test connection to Alpaca API (requires credentials)."""
        # Only runs when -m integration is specified
        pass
```

### Test Coverage
- Aim for 80%+ overall coverage
- 90%+ for critical trading logic
- 100% for risk management

---

## Git Workflow

### Branch Naming
```bash
feature/add-performance-tracking
fix/margin-calculation-bug
docs/update-installation-guide
refactor/extract-trade-executor
```

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Good commit messages
feat: Add CSV export to post-market reports
fix: Resolve DEE-BOT margin calculation error
docs: Update README with new installation steps
refactor: Extract trade execution into shared module
test: Add unit tests for position sizing

# Bad commit messages
update stuff
fixes
wip
changes
```

### Workflow
1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

3. **Keep your branch updated**:
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

4. **Run tests before pushing**:
   ```bash
   pytest
   black --check .
   mypy agents/
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

---

## Pull Request Process

### Before Submitting
- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black .`
- [ ] No linting errors: `flake8 .`
- [ ] Type hints verified: `mypy agents/`
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated

### PR Template
When creating a PR, include:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process
1. Automated checks run (tests, linting, coverage)
2. Code review by maintainer
3. Address feedback
4. Approval and merge

---

## Code Review Guidelines

### As a Reviewer
- Be constructive and respectful
- Focus on code quality, not coding style (that's automated)
- Ask questions rather than making demands
- Approve if the code is better than before (perfection not required)

### As a Contributor
- Respond to all comments
- Don't take feedback personally
- Ask for clarification if needed
- Be open to suggestions

---

## Development Best Practices

### Security
- **Never commit credentials** (API keys, passwords, tokens)
- Use environment variables for all secrets
- Rotate API keys if accidentally committed
- Review `.gitignore` before committing

### Performance
- Profile code before optimizing
- Use appropriate data structures
- Avoid premature optimization
- Cache expensive operations

### Documentation
- Update docstrings when changing function signatures
- Keep README.md current
- Add comments for complex logic only
- Use descriptive variable names (reduces need for comments)

---

## Getting Help

### Resources
- **Documentation**: Check the `docs/` folder
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Repository Review**: See `REPOSITORY_REVIEW.md` for detailed analysis

### Questions?
- Open a GitHub issue with the `question` label
- Check existing documentation first
- Be specific and provide context

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort!
