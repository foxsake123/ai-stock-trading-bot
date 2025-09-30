"""
AI Stock Trading Bot - Setup Configuration
Install with: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
def read_requirements(filename):
    """Read requirements from file and return as list"""
    req_file = Path(__file__).parent / filename
    if not req_file.exists():
        return []

    requirements = []
    with open(req_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#') and not line.startswith('-r'):
                requirements.append(line)
    return requirements

setup(
    name="ai-trading-bot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Professional multi-agent AI trading system with dual-bot strategy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/foxsake123/ai-stock-trading-bot",
    project_urls={
        "Bug Reports": "https://github.com/foxsake123/ai-stock-trading-bot/issues",
        "Source": "https://github.com/foxsake123/ai-stock-trading-bot",
        "Documentation": "https://github.com/foxsake123/ai-stock-trading-bot/tree/master/docs",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "*.tests", "*.tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
    entry_points={
        "console_scripts": [
            "trading-bot=main:main",
            "generate-report=scripts-and-data.automation.generate-post-market-report:main",
            "execute-trades=scripts-and-data.automation.execute_daily_trades:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    zip_safe=False,
)
