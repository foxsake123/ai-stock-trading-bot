#!/usr/bin/env python3
"""
AI Trading Bot - Interactive Setup Script
Handles complete system setup with interactive configuration
"""

import sys
import os
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================================
# ANSI COLOR CODES
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text: str):
    """Print a formatted header"""
    line = "=" * 80
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{line}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{line}{Colors.RESET}\n")


def print_section(text: str):
    """Print a section header"""
    print(f"\n{Colors.BRIGHT_BLUE}{Colors.BOLD}▶ {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'─' * 78}{Colors.RESET}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.BRIGHT_GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.BRIGHT_RED}✗ {text}{Colors.RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.BRIGHT_YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BRIGHT_CYAN}ℹ {text}{Colors.RESET}")


def print_step(step: int, total: int, text: str):
    """Print step progress"""
    print(f"\n{Colors.BOLD}[{step}/{total}] {text}{Colors.RESET}")


def prompt_input(question: str, default: str = None, required: bool = False) -> str:
    """Prompt user for input with optional default"""
    if default:
        prompt = f"{Colors.BRIGHT_YELLOW}? {question} [{default}]: {Colors.RESET}"
    else:
        prompt = f"{Colors.BRIGHT_YELLOW}? {question}: {Colors.RESET}"

    while True:
        response = input(prompt).strip()

        if response:
            return response
        elif default:
            return default
        elif not required:
            return ""
        else:
            print_error("This field is required. Please enter a value.")


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user for yes/no answer"""
    default_str = "Y/n" if default else "y/N"
    prompt = f"{Colors.BRIGHT_YELLOW}? {question} [{default_str}]: {Colors.RESET}"

    while True:
        response = input(prompt).strip().lower()

        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        elif response == '':
            return default
        else:
            print_error("Please answer 'y' or 'n'")


def prompt_choice(question: str, choices: List[str], default: int = 0) -> str:
    """Prompt user to choose from a list"""
    print(f"\n{Colors.BRIGHT_YELLOW}? {question}{Colors.RESET}")

    for i, choice in enumerate(choices, 1):
        if i - 1 == default:
            print(f"  {Colors.BRIGHT_GREEN}{i}) {choice} (default){Colors.RESET}")
        else:
            print(f"  {i}) {choice}")

    while True:
        response = input(f"{Colors.BRIGHT_YELLOW}  Select [1-{len(choices)}]: {Colors.RESET}").strip()

        if response == '':
            return choices[default]

        try:
            choice_idx = int(response) - 1
            if 0 <= choice_idx < len(choices):
                return choices[choice_idx]
            else:
                print_error(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print_error("Please enter a valid number")


def run_command(cmd: str, description: str = None, capture_output: bool = True) -> Tuple[bool, str]:
    """Run a shell command and return success status and output"""
    try:
        if description:
            print(f"{Colors.DIM}  Running: {description}...{Colors.RESET}", end=" ", flush=True)

        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
        else:
            result = subprocess.run(cmd, shell=True, timeout=300)
            result.stdout = ""
            result.stderr = ""

        success = result.returncode == 0

        if description:
            if success:
                print(f"{Colors.BRIGHT_GREEN}✓{Colors.RESET}")
            else:
                print(f"{Colors.BRIGHT_RED}✗{Colors.RESET}")

        return success, result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        if description:
            print(f"{Colors.BRIGHT_RED}✗ (timeout){Colors.RESET}")
        return False, "Command timed out"
    except Exception as e:
        if description:
            print(f"{Colors.BRIGHT_RED}✗{Colors.RESET}")
        return False, str(e)


# ============================================================================
# SETUP STATE MANAGEMENT
# ============================================================================

class SetupState:
    """Manages setup state for rollback on failure"""

    def __init__(self):
        self.created_dirs: List[Path] = []
        self.created_files: List[Path] = []
        self.installed_packages: List[str] = []
        self.config: Dict = {}
        self.errors: List[str] = []

    def rollback(self):
        """Rollback all changes made during setup"""
        print_warning("\nRolling back changes...")

        # Remove created files
        for file_path in reversed(self.created_files):
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"  Removed file: {file_path}")
                except Exception as e:
                    print_error(f"  Failed to remove {file_path}: {e}")

        # Remove created directories (only if empty)
        for dir_path in reversed(self.created_dirs):
            if dir_path.exists() and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    print(f"  Removed directory: {dir_path}")
                except Exception as e:
                    print_error(f"  Failed to remove {dir_path}: {e}")

        print_warning("Rollback complete.")


# ============================================================================
# SETUP STEPS
# ============================================================================

class SetupManager:
    """Manages the complete setup process"""

    def __init__(self):
        self.state = SetupState()
        self.project_root = PROJECT_ROOT
        self.platform = platform.system()

    def run(self):
        """Run the complete setup process"""
        print_header("AI TRADING BOT - INTERACTIVE SETUP")
        print(f"{Colors.BRIGHT_CYAN}Welcome! This script will guide you through setting up the AI Trading Bot.{Colors.RESET}")
        print(f"{Colors.DIM}Platform: {self.platform} | Python: {sys.version.split()[0]}{Colors.RESET}\n")

        if not prompt_yes_no("Ready to begin setup?", default=True):
            print_info("Setup cancelled.")
            return

        try:
            # Step 1: Check system requirements
            self.check_requirements()

            # Step 2: Create directory structure
            self.create_directories()

            # Step 3: Install dependencies
            self.install_dependencies()

            # Step 4: Configure environment
            self.setup_environment()

            # Step 5: Initialize configuration files
            self.initialize_configs()

            # Step 6: Create initial watchlists
            self.create_watchlists()

            # Step 7: Set up logging
            self.setup_logging()

            # Step 8: Test API connections
            self.test_api_connections()

            # Step 9: Set up automation (optional)
            self.setup_automation()

            # Step 10: Run health check
            self.run_health_check()

            # Generate setup report
            self.generate_report()

            print_header("SETUP COMPLETE! 🎉")
            print_success("Your AI Trading Bot is ready to use!")
            print_info("\nNext steps:")
            print(f"  1. Review your configuration in: {Colors.CYAN}.env{Colors.RESET}")
            print(f"  2. Check the setup report: {Colors.CYAN}setup_report.txt{Colors.RESET}")
            print(f"  3. Start the bot: {Colors.CYAN}python scripts/daily_pipeline.py{Colors.RESET}")
            print(f"  4. View the dashboard: {Colors.CYAN}python web_dashboard.py{Colors.RESET}")

        except KeyboardInterrupt:
            print_error("\n\nSetup interrupted by user.")
            self.state.rollback()
            sys.exit(1)

        except Exception as e:
            print_error(f"\n\nSetup failed: {e}")
            self.state.errors.append(str(e))
            self.state.rollback()
            sys.exit(1)

    # ------------------------------------------------------------------------
    # STEP 1: Check System Requirements
    # ------------------------------------------------------------------------

    def check_requirements(self):
        """Check system requirements"""
        print_step(1, 10, "Checking System Requirements")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 9):
            raise RuntimeError(
                f"Python 3.9+ is required (found {python_version.major}.{python_version.minor})"
            )
        print_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

        # Check pip
        success, _ = run_command("pip --version", "Checking pip")
        if not success:
            raise RuntimeError("pip is not installed")

        # Check git
        success, output = run_command("git --version", "Checking git")
        if success:
            print_success(f"Git: {output.strip()}")
        else:
            print_warning("Git not found (optional, but recommended)")

        # Check disk space
        disk_usage = shutil.disk_usage(self.project_root)
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 1:
            print_warning(f"Low disk space: {free_gb:.1f} GB free")
        else:
            print_success(f"Disk space: {free_gb:.1f} GB free")

        # Check network connectivity
        print(f"{Colors.DIM}  Testing network connectivity...{Colors.RESET}", end=" ", flush=True)
        try:
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=5)
            print(f"{Colors.BRIGHT_GREEN}✓{Colors.RESET}")
        except:
            print(f"{Colors.BRIGHT_YELLOW}⚠{Colors.RESET}")
            print_warning("Network connectivity issue detected")

    # ------------------------------------------------------------------------
    # STEP 2: Create Directory Structure
    # ------------------------------------------------------------------------

    def create_directories(self):
        """Create all required directories"""
        print_step(2, 10, "Creating Directory Structure")

        directories = [
            # Data directories
            'data/cache',
            'data/database',
            'data/backups',

            # Log directories
            'logs/app',
            'logs/trades',
            'logs/errors',
            'logs/performance',
            'logs/alerts',

            # Report directories
            'reports/premarket',
            'reports/execution',
            'reports/performance',
            'reports/archive',

            # Configuration directories
            'configs',

            # Script directories (execution, monitoring, utilities already exist)
            'scripts/emergency',

            # Source directories (most already exist)
            'src/alerts/channels',
            'src/monitors',

            # Test directories
            'tests/integration',
            'tests/unit',
            'tests/agents',
            'tests/exploratory',

            # Documentation directories
            'docs/session-summaries',
            'docs/api',
        ]

        created_count = 0
        for dir_path in directories:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                self.state.created_dirs.append(full_path)
                created_count += 1

        print_success(f"Created {created_count} directories")
        print_info(f"Total directories: {len(directories)}")

    # ------------------------------------------------------------------------
    # STEP 3: Install Dependencies
    # ------------------------------------------------------------------------

    def install_dependencies(self):
        """Install Python dependencies"""
        print_step(3, 10, "Installing Dependencies")

        requirements_file = self.project_root / 'requirements.txt'

        if not requirements_file.exists():
            print_warning("requirements.txt not found, skipping dependency installation")
            return

        if not prompt_yes_no("Install Python dependencies from requirements.txt?", default=True):
            print_info("Skipping dependency installation")
            return

        print_info("This may take a few minutes...")

        # Upgrade pip first
        run_command(
            f"{sys.executable} -m pip install --upgrade pip",
            "Upgrading pip",
            capture_output=True
        )

        # Install requirements
        success, output = run_command(
            f"{sys.executable} -m pip install -r {requirements_file}",
            "Installing requirements",
            capture_output=True
        )

        if success:
            print_success("Dependencies installed successfully")

            # Parse installed packages
            with open(requirements_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0]
                        self.state.installed_packages.append(pkg_name)
        else:
            print_error("Failed to install some dependencies")
            print(f"{Colors.DIM}{output}{Colors.RESET}")
            if not prompt_yes_no("Continue anyway?", default=False):
                raise RuntimeError("Dependency installation failed")

    # ------------------------------------------------------------------------
    # STEP 4: Setup Environment
    # ------------------------------------------------------------------------

    def setup_environment(self):
        """Configure environment variables"""
        print_step(4, 10, "Configuring Environment")

        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'

        # Copy .env.example if .env doesn't exist
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            self.state.created_files.append(env_file)
            print_success("Created .env from .env.example")
        elif env_file.exists():
            print_info(".env already exists")
            if not prompt_yes_no("Update existing .env file?", default=False):
                print_info("Keeping existing .env")
                return
        else:
            # Create new .env file
            env_file.touch()
            self.state.created_files.append(env_file)
            print_success("Created new .env file")

        # Interactive API key configuration
        print_section("API Key Configuration")

        api_keys = {}

        # Anthropic API Key (required for Claude)
        print_info("\n🤖 Anthropic API Key (Required for Claude Deep Research)")
        print(f"{Colors.DIM}Get your key at: https://console.anthropic.com/settings/keys{Colors.RESET}")
        api_keys['ANTHROPIC_API_KEY'] = prompt_input(
            "Enter Anthropic API key",
            required=True
        )

        # Alpaca API Keys (required for trading)
        print_info("\n📈 Alpaca API Keys (Required for trading execution)")
        print(f"{Colors.DIM}Get your keys at: https://app.alpaca.markets/paper/dashboard/overview{Colors.RESET}")
        api_keys['ALPACA_API_KEY'] = prompt_input("Enter Alpaca API key", required=True)
        api_keys['ALPACA_SECRET_KEY'] = prompt_input("Enter Alpaca secret key", required=True)

        # Financial Datasets API Key (required for data)
        print_info("\n💹 Financial Datasets API Key (Required for market data)")
        print(f"{Colors.DIM}Get your key at: https://financialdatasets.ai{Colors.RESET}")
        api_keys['FINANCIAL_DATASETS_API_KEY'] = prompt_input(
            "Enter Financial Datasets API key",
            required=True
        )

        # Telegram Bot (optional)
        if prompt_yes_no("\n📱 Configure Telegram notifications?", default=True):
            print(f"{Colors.DIM}Create a bot with @BotFather and get your chat ID{Colors.RESET}")
            api_keys['TELEGRAM_BOT_TOKEN'] = prompt_input("Enter Telegram bot token")
            api_keys['TELEGRAM_CHAT_ID'] = prompt_input("Enter Telegram chat ID")

        # Email (optional)
        if prompt_yes_no("\n📧 Configure email notifications?", default=False):
            api_keys['SMTP_HOST'] = prompt_input("SMTP host", default="smtp.gmail.com")
            api_keys['SMTP_PORT'] = prompt_input("SMTP port", default="587")
            api_keys['SMTP_USERNAME'] = prompt_input("SMTP username")
            api_keys['SMTP_PASSWORD'] = prompt_input("SMTP password")
            api_keys['EMAIL_FROM'] = prompt_input("From email address")
            api_keys['EMAIL_TO'] = prompt_input("To email address")

        # Write to .env
        env_content = []

        # Read existing content
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    # Keep comments and empty lines
                    if not line or line.startswith('#'):
                        env_content.append(line)
                    # Update existing keys
                    else:
                        key = line.split('=')[0]
                        if key in api_keys:
                            env_content.append(f"{key}={api_keys[key]}")
                            del api_keys[key]
                        else:
                            env_content.append(line)

        # Add new keys
        if api_keys:
            env_content.append("\n# Added by setup.py")
            for key, value in api_keys.items():
                env_content.append(f"{key}={value}")

        # Write to file
        with open(env_file, 'w') as f:
            f.write('\n'.join(env_content))

        self.state.config['api_keys'] = list(api_keys.keys())
        print_success(f"Configured {len(api_keys)} API keys in .env")

    # ------------------------------------------------------------------------
    # STEP 5: Initialize Configuration Files
    # ------------------------------------------------------------------------

    def initialize_configs(self):
        """Initialize YAML configuration files"""
        print_step(5, 10, "Initializing Configuration Files")

        configs_dir = self.project_root / 'configs'

        # Check existing configs
        existing_configs = list(configs_dir.glob('*.yaml'))

        if existing_configs:
            print_info(f"Found {len(existing_configs)} existing configuration files")
            if not prompt_yes_no("Update configuration with your preferences?", default=True):
                print_info("Keeping existing configurations")
                return

        # Portfolio configuration
        print_section("Portfolio Configuration")

        portfolio_size = prompt_input(
            "Enter total portfolio size (USD)",
            default="200000"
        )

        # Strategy selection
        print_section("Strategy Selection")

        dee_bot_enabled = prompt_yes_no(
            "Enable DEE-BOT (Beta-Neutral, Defensive)?",
            default=True
        )

        shorgan_bot_enabled = prompt_yes_no(
            "Enable SHORGAN-BOT (Catalyst-Driven, Aggressive)?",
            default=True
        )

        if dee_bot_enabled and shorgan_bot_enabled:
            dee_allocation = prompt_input(
                "DEE-BOT allocation (% of portfolio)",
                default="50"
            )
            shorgan_allocation = str(100 - int(dee_allocation))
        elif dee_bot_enabled:
            dee_allocation = "100"
            shorgan_allocation = "0"
        elif shorgan_bot_enabled:
            dee_allocation = "0"
            shorgan_allocation = "100"
        else:
            print_error("At least one strategy must be enabled")
            dee_allocation = "50"
            shorgan_allocation = "50"

        # Update config.yaml
        config_file = configs_dir / 'config.yaml'
        if config_file.exists():
            import yaml

            with open(config_file) as f:
                config = yaml.safe_load(f)

            # Update portfolio settings
            if 'trading' not in config:
                config['trading'] = {}

            config['trading']['portfolio_size'] = int(portfolio_size)
            config['trading']['bots'] = {
                'dee_bot': {
                    'enabled': dee_bot_enabled,
                    'allocation_pct': int(dee_allocation),
                },
                'shorgan_bot': {
                    'enabled': shorgan_bot_enabled,
                    'allocation_pct': int(shorgan_allocation),
                }
            }

            # Write back
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            print_success("Updated config.yaml")

            self.state.config['portfolio_size'] = portfolio_size
            self.state.config['dee_bot_enabled'] = dee_bot_enabled
            self.state.config['shorgan_bot_enabled'] = shorgan_bot_enabled
        else:
            print_warning("config.yaml not found, skipping configuration update")

    # ------------------------------------------------------------------------
    # STEP 6: Create Initial Watchlists
    # ------------------------------------------------------------------------

    def create_watchlists(self):
        """Create initial watchlists"""
        print_step(6, 10, "Creating Initial Watchlists")

        watchlists_dir = self.project_root / 'data' / 'watchlists'
        watchlists_dir.mkdir(parents=True, exist_ok=True)

        # Default watchlists
        default_watchlists = {
            'dee_bot_defensive.txt': [
                '# DEE-BOT Defensive Watchlist',
                '# Ultra-defensive, high-dividend, beta < 0.6 stocks',
                'JNJ',
                'PG',
                'KO',
                'PEP',
                'WMT',
                'COST',
                'VZ',
                'T',
                'DUK',
                'NEE',
                'SO',
                'D',
            ],
            'shorgan_bot_catalysts.txt': [
                '# SHORGAN-BOT Catalyst Watchlist',
                '# High-catalyst biotech and small-caps',
                'PTGX',
                'SMMT',
                'VKTX',
                'ARQT',
                'GKOS',
                'SNDX',
                'RKLB',
                'ACAD',
            ],
            'sp500_top50.txt': [
                '# S&P 500 Top 50 by Market Cap',
                'AAPL',
                'MSFT',
                'GOOGL',
                'AMZN',
                'NVDA',
                'META',
                'TSLA',
                'BRK.B',
                'V',
                'UNH',
            ]
        }

        created_count = 0
        for filename, tickers in default_watchlists.items():
            watchlist_file = watchlists_dir / filename

            if not watchlist_file.exists():
                with open(watchlist_file, 'w') as f:
                    f.write('\n'.join(tickers))

                self.state.created_files.append(watchlist_file)
                created_count += 1

        print_success(f"Created {created_count} watchlist files")

    # ------------------------------------------------------------------------
    # STEP 7: Setup Logging
    # ------------------------------------------------------------------------

    def setup_logging(self):
        """Set up logging system"""
        print_step(7, 10, "Setting Up Logging")

        try:
            from src.utils import setup_logging

            # Initialize logging
            setup_logging(
                level='INFO',
                log_to_file=True,
                log_to_console=False,
                rotation='daily',
                backup_count=30
            )

            print_success("Logging system initialized")

            # Test logging
            from src.utils import get_logger
            logger = get_logger('setup')
            logger.info("Setup script - logging test")

            print_success("Logging test passed")

        except Exception as e:
            print_warning(f"Could not initialize logging: {e}")

    # ------------------------------------------------------------------------
    # STEP 8: Test API Connections
    # ------------------------------------------------------------------------

    def test_api_connections(self):
        """Test API connections"""
        print_step(8, 10, "Testing API Connections")

        # Load environment
        from dotenv import load_dotenv
        load_dotenv(self.project_root / '.env')

        api_tests = []

        # Test Anthropic API
        print(f"{Colors.DIM}  Testing Anthropic API...{Colors.RESET}", end=" ", flush=True)
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                client = anthropic.Anthropic(api_key=api_key)
                # Simple test - just check if we can create a client
                print(f"{Colors.BRIGHT_GREEN}✓{Colors.RESET}")
                api_tests.append(('Anthropic', True, None))
            else:
                print(f"{Colors.BRIGHT_YELLOW}⚠ (no key){Colors.RESET}")
                api_tests.append(('Anthropic', False, "No API key"))
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗{Colors.RESET}")
            api_tests.append(('Anthropic', False, str(e)))

        # Test Alpaca API
        print(f"{Colors.DIM}  Testing Alpaca API...{Colors.RESET}", end=" ", flush=True)
        try:
            from alpaca.trading.client import TradingClient
            api_key = os.getenv('ALPACA_API_KEY')
            secret_key = os.getenv('ALPACA_SECRET_KEY')

            if api_key and secret_key:
                client = TradingClient(api_key, secret_key, paper=True)
                account = client.get_account()
                print(f"{Colors.BRIGHT_GREEN}✓{Colors.RESET}")
                api_tests.append(('Alpaca', True, None))
            else:
                print(f"{Colors.BRIGHT_YELLOW}⚠ (no keys){Colors.RESET}")
                api_tests.append(('Alpaca', False, "No API keys"))
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗{Colors.RESET}")
            api_tests.append(('Alpaca', False, str(e)))

        # Test Financial Datasets API
        print(f"{Colors.DIM}  Testing Financial Datasets API...{Colors.RESET}", end=" ", flush=True)
        try:
            import requests
            api_key = os.getenv('FINANCIAL_DATASETS_API_KEY')

            if api_key:
                headers = {'X-API-KEY': api_key}
                response = requests.get(
                    'https://api.financialdatasets.ai/prices/snapshot?ticker=AAPL',
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    print(f"{Colors.BRIGHT_GREEN}✓{Colors.RESET}")
                    api_tests.append(('Financial Datasets', True, None))
                else:
                    print(f"{Colors.BRIGHT_RED}✗ ({response.status_code}){Colors.RESET}")
                    api_tests.append(('Financial Datasets', False, f"HTTP {response.status_code}"))
            else:
                print(f"{Colors.BRIGHT_YELLOW}⚠ (no key){Colors.RESET}")
                api_tests.append(('Financial Datasets', False, "No API key"))
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗{Colors.RESET}")
            api_tests.append(('Financial Datasets', False, str(e)))

        # Summary
        passed = sum(1 for _, success, _ in api_tests if success)
        total = len(api_tests)

        if passed == total:
            print_success(f"All {total} API connections successful")
        elif passed > 0:
            print_warning(f"{passed}/{total} API connections successful")
        else:
            print_error("All API connection tests failed")

            if not prompt_yes_no("Continue anyway?", default=False):
                raise RuntimeError("API connection tests failed")

        self.state.config['api_tests'] = api_tests

    # ------------------------------------------------------------------------
    # STEP 9: Setup Automation
    # ------------------------------------------------------------------------

    def setup_automation(self):
        """Set up automation (systemd/Task Scheduler)"""
        print_step(9, 10, "Setting Up Automation (Optional)")

        if not prompt_yes_no("Set up automated daily execution?", default=False):
            print_info("Skipping automation setup")
            return

        if self.platform == 'Linux':
            self.setup_systemd()
        elif self.platform == 'Windows':
            self.setup_task_scheduler()
        else:
            print_warning(f"Automated setup not supported on {self.platform}")
            print_info("Please refer to docs/DEPLOYMENT.md for manual setup")

    def setup_systemd(self):
        """Set up systemd service and timer (Linux)"""
        print_info("Setting up systemd service and timer...")

        service_file = self.project_root / 'deployment' / 'systemd' / 'ai-trading-bot.service'
        timer_file = self.project_root / 'deployment' / 'systemd' / 'ai-trading-bot.timer'

        if not service_file.exists() or not timer_file.exists():
            print_warning("Systemd files not found in deployment/systemd/")
            return

        # Copy to /etc/systemd/system/
        print_info("This requires sudo privileges...")

        success1, _ = run_command(
            f"sudo cp {service_file} /etc/systemd/system/",
            "Installing service file"
        )

        success2, _ = run_command(
            f"sudo cp {timer_file} /etc/systemd/system/",
            "Installing timer file"
        )

        if success1 and success2:
            # Reload systemd
            run_command("sudo systemctl daemon-reload", "Reloading systemd")

            # Enable timer
            run_command(
                "sudo systemctl enable ai-trading-bot.timer",
                "Enabling timer"
            )

            # Start timer
            run_command(
                "sudo systemctl start ai-trading-bot.timer",
                "Starting timer"
            )

            print_success("Systemd automation configured")
            print_info("Daily execution scheduled for 6:00 AM ET")
        else:
            print_error("Failed to install systemd files")

    def setup_task_scheduler(self):
        """Set up Windows Task Scheduler"""
        print_info("Setting up Windows Task Scheduler...")

        batch_file = self.project_root / 'scripts' / 'automation' / 'setup_task_scheduler.bat'

        if not batch_file.exists():
            print_warning("Task Scheduler setup script not found")
            return

        print_info("Running Task Scheduler setup script...")
        print_warning("You may be prompted for administrator privileges")

        success, output = run_command(
            str(batch_file),
            "Creating scheduled task",
            capture_output=True
        )

        if success:
            print_success("Task Scheduler configured")
            print_info("Daily execution scheduled for 6:00 AM ET")
        else:
            print_error("Failed to create scheduled task")
            print(f"{Colors.DIM}{output}{Colors.RESET}")

    # ------------------------------------------------------------------------
    # STEP 10: Run Health Check
    # ------------------------------------------------------------------------

    def run_health_check(self):
        """Run system health check"""
        print_step(10, 10, "Running Health Check")

        health_script = self.project_root / 'scripts' / 'health_check.py'

        if not health_script.exists():
            print_warning("Health check script not found")
            return

        print_info("Running comprehensive health check...")

        success, output = run_command(
            f"{sys.executable} {health_script}",
            description=None,
            capture_output=True
        )

        # Display health check output
        print(output)

        if success:
            print_success("Health check passed")
        else:
            print_warning("Health check found issues (see above)")

    # ------------------------------------------------------------------------
    # Generate Setup Report
    # ------------------------------------------------------------------------

    def generate_report(self):
        """Generate setup completion report"""
        report_file = self.project_root / 'setup_report.txt'

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report_lines = [
            "=" * 80,
            "AI TRADING BOT - SETUP REPORT".center(80),
            "=" * 80,
            f"\nSetup completed: {timestamp}",
            f"Platform: {self.platform}",
            f"Python: {sys.version.split()[0]}",
            f"Project root: {self.project_root}",
            "\n" + "-" * 80,
            "CONFIGURATION",
            "-" * 80,
        ]

        # Portfolio settings
        if 'portfolio_size' in self.state.config:
            report_lines.append(f"\nPortfolio size: ${self.state.config['portfolio_size']}")
            report_lines.append(f"DEE-BOT enabled: {self.state.config.get('dee_bot_enabled', False)}")
            report_lines.append(f"SHORGAN-BOT enabled: {self.state.config.get('shorgan_bot_enabled', False)}")

        # API keys
        if 'api_keys' in self.state.config:
            report_lines.append(f"\nConfigured API keys: {len(self.state.config['api_keys'])}")
            for key in self.state.config['api_keys']:
                report_lines.append(f"  - {key}")

        # API test results
        if 'api_tests' in self.state.config:
            report_lines.append("\n" + "-" * 80)
            report_lines.append("API CONNECTION TESTS")
            report_lines.append("-" * 80)

            for api, success, error in self.state.config['api_tests']:
                status = "✓ PASS" if success else "✗ FAIL"
                report_lines.append(f"\n{api}: {status}")
                if error:
                    report_lines.append(f"  Error: {error}")

        # Directories created
        if self.state.created_dirs:
            report_lines.append("\n" + "-" * 80)
            report_lines.append("DIRECTORIES CREATED")
            report_lines.append("-" * 80)
            report_lines.append(f"\nTotal: {len(self.state.created_dirs)}")

        # Files created
        if self.state.created_files:
            report_lines.append("\n" + "-" * 80)
            report_lines.append("FILES CREATED")
            report_lines.append("-" * 80)
            for file_path in self.state.created_files:
                report_lines.append(f"  - {file_path.relative_to(self.project_root)}")

        # Dependencies installed
        if self.state.installed_packages:
            report_lines.append("\n" + "-" * 80)
            report_lines.append("DEPENDENCIES INSTALLED")
            report_lines.append("-" * 80)
            report_lines.append(f"\nTotal packages: {len(self.state.installed_packages)}")

        # Next steps
        report_lines.extend([
            "\n" + "=" * 80,
            "NEXT STEPS",
            "=" * 80,
            "\n1. Review your .env file and ensure all API keys are correct",
            "2. Review configuration files in configs/",
            "3. Run a test: python scripts/daily_pipeline.py --test",
            "4. Start the dashboard: python web_dashboard.py",
            "5. Read the documentation in docs/",
            "\n" + "=" * 80,
            "USEFUL COMMANDS",
            "=" * 80,
            "\n# Generate daily report",
            "python scripts/daily_pipeline.py",
            "\n# Run health check",
            "python scripts/health_check.py",
            "\n# Start web dashboard",
            "python web_dashboard.py",
            "\n# View portfolio status",
            "python scripts/performance/get_portfolio_status.py",
            "\n# Run tests",
            "pytest tests/",
            "\n" + "=" * 80,
        ])

        # Write report
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))

        print_success(f"Setup report saved to: {report_file}")

        # Display summary
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}Setup Summary:{Colors.RESET}")
        if 'api_tests' in self.state.config:
            passed = sum(1 for _, success, _ in self.state.config['api_tests'] if success)
            total = len(self.state.config['api_tests'])
            print(f"  API Tests: {passed}/{total} passed")

        print(f"  Directories: {len(self.state.created_dirs)} created")
        print(f"  Files: {len(self.state.created_files)} created")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    try:
        setup = SetupManager()
        setup.run()
    except Exception as e:
        print_error(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
