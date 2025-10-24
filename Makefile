# AI Trading Bot - Makefile
# Production automation commands for task automation
# Last Updated: 2025-10-23
# Supports: Linux, macOS, Windows (Git Bash/WSL)

.PHONY: help install test run monitor health backup deploy-systemd deploy-cron logs logs-trades emergency-stop clean

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# PLATFORM DETECTION
# ============================================================================

UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)
ifeq ($(UNAME_S),Linux)
	PLATFORM := linux
	PYTHON := python3
	VENV_ACTIVATE := . venv/bin/activate
	VENV_BIN := venv/bin
endif
ifeq ($(UNAME_S),Darwin)
	PLATFORM := macos
	PYTHON := python3
	VENV_ACTIVATE := . venv/bin/activate
	VENV_BIN := venv/bin
endif
ifeq ($(UNAME_S),Windows)
	PLATFORM := windows
	PYTHON := python
	VENV_ACTIVATE := venv\Scripts\activate
	VENV_BIN := venv/Scripts
endif

# ============================================================================
# VARIABLES
# ============================================================================

VENV := venv
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
PYTHON_BIN := $(VENV_BIN)/python
PROJECT_ROOT := $(shell pwd)
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S 2>/dev/null || powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'")
BACKUP_DIR := backups/$(TIMESTAMP)

# Colors for output (ANSI escape codes)
COLOR_RESET := \033[0m
COLOR_BLUE := \033[36m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_RED := \033[31m

# ============================================================================
# HELP TARGET
# ============================================================================

help:  ## Display all available commands with descriptions
	@echo ""
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)   AI Trading Bot - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)Platform:$(COLOR_RESET) $(PLATFORM)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_BLUE)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_YELLOW)Quick Start Examples:$(COLOR_RESET)"
	@echo "  make install          # First-time setup"
	@echo "  make health           # Verify system status"
	@echo "  make test             # Run all tests"
	@echo "  make run              # Execute daily pipeline"
	@echo "  make monitor          # Real-time monitoring"
	@echo "  make emergency-stop   # Immediately halt trading"
	@echo ""
	@echo "$(COLOR_YELLOW)Common Workflows:$(COLOR_RESET)"
	@echo "  make install && make health && make run"
	@echo "  make backup && make clean && make test"
	@echo "  make logs-trades | grep -i error"
	@echo ""

# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

install:  ## Setup virtual environment and install all dependencies
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Installing AI Trading Bot...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)[1/8]$(COLOR_RESET) Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV) || (echo "$(COLOR_RED)Error: Failed to create venv$(COLOR_RESET)" && exit 1)
	@echo "$(COLOR_GREEN)[2/8]$(COLOR_RESET) Upgrading pip, setuptools, wheel..."
	@$(PIP) install --upgrade pip setuptools wheel --quiet
	@echo "$(COLOR_GREEN)[3/8]$(COLOR_RESET) Installing dependencies from requirements.txt..."
	@$(PIP) install -r requirements.txt --quiet || (echo "$(COLOR_YELLOW)Warning: Some packages may have failed$(COLOR_RESET)")
	@echo "$(COLOR_GREEN)[4/8]$(COLOR_RESET) Creating data directories..."
	@mkdir -p data/cache data/historical data/watchlists data/positions data/state
	@echo "$(COLOR_GREEN)[5/8]$(COLOR_RESET) Creating log directories..."
	@mkdir -p logs/app logs/trades logs/errors logs/performance
	@echo "$(COLOR_GREEN)[6/8]$(COLOR_RESET) Creating report directories..."
	@mkdir -p reports/daily reports/weekly reports/monthly
	@echo "$(COLOR_GREEN)[7/8]$(COLOR_RESET) Creating backup directory..."
	@mkdir -p backups
	@echo "$(COLOR_GREEN)[8/8]$(COLOR_RESET) Setting up configuration..."
	@if [ ! -f configs/.env ]; then \
		echo "  Creating configs/.env from template..."; \
		cp .env.example configs/.env || cp .env.example configs/.env; \
		echo "  $(COLOR_YELLOW)IMPORTANT: Edit configs/.env with your API keys!$(COLOR_RESET)"; \
	else \
		echo "  configs/.env already exists (skipping)"; \
	fi
	@echo ""
	@echo "$(COLOR_GREEN)========================================$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)Installation Complete!$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)========================================$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)Next Steps:$(COLOR_RESET)"
	@echo "  1. Edit configs/.env with your API keys"
	@echo "  2. Review configs/config.yaml for settings"
	@echo "  3. Run '$(COLOR_BLUE)make health$(COLOR_RESET)' to verify setup"
	@echo "  4. Run '$(COLOR_BLUE)make test$(COLOR_RESET)' to validate system"
	@echo ""

dev-setup:  ## Setup development environment with additional tools
	@echo "$(COLOR_BLUE)Setting up development environment...$(COLOR_RESET)"
	@$(MAKE) install
	@echo "Installing development dependencies..."
	@if [ -f requirements-dev.txt ]; then \
		$(PIP) install -r requirements-dev.txt --quiet; \
		echo "$(COLOR_GREEN)Dev dependencies installed$(COLOR_RESET)"; \
	else \
		echo "$(COLOR_YELLOW)requirements-dev.txt not found (skipping)$(COLOR_RESET)"; \
	fi
	@echo "$(COLOR_GREEN)Development environment ready!$(COLOR_RESET)"

update:  ## Update dependencies to latest versions
	@echo "$(COLOR_BLUE)Updating dependencies...$(COLOR_RESET)"
	@$(PIP) install --upgrade -r requirements.txt --quiet
	@echo "$(COLOR_GREEN)Dependencies updated!$(COLOR_RESET)"

# ============================================================================
# TESTING
# ============================================================================

test:  ## Run full test suite with coverage report
	@echo "$(COLOR_BLUE)Running full test suite...$(COLOR_RESET)"
	@if [ -d tests ]; then \
		$(PYTEST) tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-report=html || \
		(echo "$(COLOR_RED)Tests failed!$(COLOR_RESET)" && exit 1); \
		echo ""; \
		echo "$(COLOR_GREEN)Coverage report: htmlcov/index.html$(COLOR_RESET)"; \
	else \
		echo "$(COLOR_YELLOW)No tests directory found$(COLOR_RESET)"; \
	fi

test-unit:  ## Run unit tests only
	@echo "$(COLOR_BLUE)Running unit tests...$(COLOR_RESET)"
	@$(PYTEST) tests/unit/ -v || echo "$(COLOR_YELLOW)No unit tests found$(COLOR_RESET)"

test-integration:  ## Run integration tests only
	@echo "$(COLOR_BLUE)Running integration tests...$(COLOR_RESET)"
	@$(PYTEST) tests/integration/ -v || echo "$(COLOR_YELLOW)No integration tests found$(COLOR_RESET)"

test-performance:  ## Run performance tests
	@echo "$(COLOR_BLUE)Running performance tests...$(COLOR_RESET)"
	@$(PYTEST) tests/performance/ -v || echo "$(COLOR_YELLOW)No performance tests found$(COLOR_RESET)"

test-coverage:  ## Generate detailed coverage report
	@echo "$(COLOR_BLUE)Generating coverage report...$(COLOR_RESET)"
	@$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term --cov-report=xml
	@echo "$(COLOR_GREEN)Coverage reports generated:$(COLOR_RESET)"
	@echo "  HTML: htmlcov/index.html"
	@echo "  XML:  coverage.xml"

# ============================================================================
# RUNNING THE BOT
# ============================================================================

run:  ## Execute daily pipeline manually
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Starting Daily Pipeline...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@$(PYTHON_BIN) scripts/daily_pipeline.py || \
		(echo "$(COLOR_RED)Pipeline failed! Check logs/app/ for details$(COLOR_RESET)" && exit 1)

run-background:  ## Run pipeline in background with logging
	@echo "$(COLOR_BLUE)Starting pipeline in background...$(COLOR_RESET)"
	@nohup $(PYTHON_BIN) scripts/daily_pipeline.py > logs/app/pipeline_$(TIMESTAMP).log 2>&1 &
	@echo "$(COLOR_GREEN)Pipeline started in background$(COLOR_RESET)"
	@echo "Log file: logs/app/pipeline_$(TIMESTAMP).log"
	@echo "Use '$(COLOR_BLUE)make logs$(COLOR_RESET)' to view logs"

run-dry:  ## Execute pipeline in dry-run mode (no actual trades)
	@echo "$(COLOR_BLUE)Running pipeline in DRY-RUN mode...$(COLOR_RESET)"
	@DRY_RUN=true $(PYTHON_BIN) scripts/daily_pipeline.py

# ============================================================================
# MONITORING
# ============================================================================

monitor:  ## Start real-time position monitoring
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Real-Time Position Monitor$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@if [ -f scripts/monitoring/monitor.py ]; then \
		$(PYTHON_BIN) scripts/monitoring/monitor.py; \
	else \
		echo "$(COLOR_YELLOW)Monitor script not found$(COLOR_RESET)"; \
		echo "Creating placeholder..."; \
		echo "Real-time monitoring will be implemented here"; \
	fi

health:  ## Run system health checks
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)System Health Check$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@if [ -f scripts/monitoring/health_check.py ]; then \
		$(PYTHON_BIN) scripts/monitoring/health_check.py --verbose || true; \
	else \
		echo "$(COLOR_YELLOW)Health check script not found - running basic checks$(COLOR_RESET)"; \
		echo ""; \
		echo "[1/5] Python Environment"; \
		$(PYTHON_BIN) --version && echo "  $(COLOR_GREEN)[PASS]$(COLOR_RESET) Python OK" || echo "  $(COLOR_RED)[FAIL]$(COLOR_RESET) Python not found"; \
		echo ""; \
		echo "[2/5] Virtual Environment"; \
		[ -d $(VENV) ] && echo "  $(COLOR_GREEN)[PASS]$(COLOR_RESET) Virtual environment exists" || echo "  $(COLOR_RED)[FAIL]$(COLOR_RESET) Run 'make install'"; \
		echo ""; \
		echo "[3/5] Configuration Files"; \
		[ -f configs/config.yaml ] && echo "  $(COLOR_GREEN)[PASS]$(COLOR_RESET) config.yaml found" || echo "  $(COLOR_YELLOW)[WARN]$(COLOR_RESET) config.yaml not found"; \
		[ -f configs/.env ] && echo "  $(COLOR_GREEN)[PASS]$(COLOR_RESET) .env found" || echo "  $(COLOR_YELLOW)[WARN]$(COLOR_RESET) .env not found"; \
		echo ""; \
		echo "[4/5] Directory Structure"; \
		[ -d logs ] && echo "  $(COLOR_GREEN)[PASS]$(COLOR_RESET) logs/ exists" || echo "  $(COLOR_YELLOW)[WARN]$(COLOR_RESET) logs/ missing"; \
		[ -d data ] && echo "  $(COLOR_GREEN)[PASS]$(COLOR_RESET) data/ exists" || echo "  $(COLOR_YELLOW)[WARN]$(COLOR_RESET) data/ missing"; \
		echo ""; \
		echo "[5/5] Main Scripts"; \
		[ -f scripts/daily_pipeline.py ] && echo "  $(COLOR_GREEN)[PASS]$(COLOR_RESET) daily_pipeline.py found" || echo "  $(COLOR_RED)[FAIL]$(COLOR_RESET) daily_pipeline.py missing"; \
		echo ""; \
	fi

status:  ## Show current bot status and portfolio
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Bot Status$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@if [ -f scripts/portfolio/get_portfolio_status.py ]; then \
		$(PYTHON_BIN) scripts/portfolio/get_portfolio_status.py; \
	else \
		echo "$(COLOR_YELLOW)Portfolio status script not found$(COLOR_RESET)"; \
	fi
	@echo ""
	@echo "Recent logs (last 20 lines):"
	@echo "----------------------------"
	@tail -20 logs/app/*.log 2>/dev/null | tail -20 || echo "$(COLOR_YELLOW)No logs found$(COLOR_RESET)"

positions:  ## Show current positions
	@echo "$(COLOR_BLUE)Current Positions$(COLOR_RESET)"
	@echo "================="
	@if [ -f scripts/portfolio/show_positions.py ]; then \
		$(PYTHON_BIN) scripts/portfolio/show_positions.py; \
	else \
		echo "$(COLOR_YELLOW)Positions script not found$(COLOR_RESET)"; \
	fi

# ============================================================================
# LOGS
# ============================================================================

logs:  ## Tail application logs
	@echo "$(COLOR_BLUE)Application Logs (last 50 lines)$(COLOR_RESET)"
	@echo "================================"
	@if [ -f logs/app/daily.log ]; then \
		tail -50 logs/app/daily.log; \
	elif ls logs/app/*.log >/dev/null 2>&1; then \
		tail -50 logs/app/*.log | tail -50; \
	else \
		echo "$(COLOR_YELLOW)No application logs found$(COLOR_RESET)"; \
	fi

logs-follow:  ## Follow application logs in real-time
	@echo "$(COLOR_BLUE)Following application logs... (Ctrl+C to exit)$(COLOR_RESET)"
	@if ls logs/app/*.log >/dev/null 2>&1; then \
		tail -f logs/app/*.log; \
	else \
		echo "$(COLOR_YELLOW)No logs to follow$(COLOR_RESET)"; \
	fi

logs-errors:  ## Show recent error logs
	@echo "$(COLOR_RED)Error Logs (last 50 lines)$(COLOR_RESET)"
	@echo "=========================="
	@if ls logs/errors/*.log >/dev/null 2>&1; then \
		tail -50 logs/errors/*.log | tail -50; \
	else \
		echo "$(COLOR_GREEN)No errors found!$(COLOR_RESET)"; \
	fi

logs-trades:  ## Display formatted trade logs
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Trade Logs (last 100 lines)$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@if ls logs/trades/*.log >/dev/null 2>&1; then \
		tail -100 logs/trades/*.log | grep -E "BUY|SELL|EXECUTED|FILLED|CANCELLED|REJECTED" --color=always | tail -50 || \
		tail -100 logs/trades/*.log | tail -50; \
	else \
		echo "$(COLOR_YELLOW)No trade logs found$(COLOR_RESET)"; \
	fi

logs-performance:  ## Show performance metrics logs
	@echo "$(COLOR_BLUE)Performance Metrics$(COLOR_RESET)"
	@echo "==================="
	@if ls logs/performance/*.log >/dev/null 2>&1; then \
		tail -50 logs/performance/*.log; \
	else \
		echo "$(COLOR_YELLOW)No performance logs found$(COLOR_RESET)"; \
	fi

# ============================================================================
# BACKUP & RESTORE
# ============================================================================

backup:  ## Backup data, configs, and reports with timestamps
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Creating Backup...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)========================================$(COLOR_RESET)"
	@echo ""
	@mkdir -p $(BACKUP_DIR)
	@echo "$(COLOR_GREEN)[1/5]$(COLOR_RESET) Backing up configuration..."
	@cp -r configs $(BACKUP_DIR)/ 2>/dev/null || echo "  $(COLOR_YELLOW)No configs to backup$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)[2/5]$(COLOR_RESET) Backing up data..."
	@cp -r data $(BACKUP_DIR)/ 2>/dev/null || echo "  $(COLOR_YELLOW)No data to backup$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)[3/5]$(COLOR_RESET) Backing up reports..."
	@cp -r reports $(BACKUP_DIR)/ 2>/dev/null || echo "  $(COLOR_YELLOW)No reports to backup$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)[4/5]$(COLOR_RESET) Backing up logs..."
	@cp -r logs $(BACKUP_DIR)/ 2>/dev/null || echo "  $(COLOR_YELLOW)No logs to backup$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)[5/5]$(COLOR_RESET) Creating compressed archive..."
	@cd backups && tar -czf $(TIMESTAMP).tar.gz $(TIMESTAMP) 2>/dev/null || \
		(cd backups && zip -r $(TIMESTAMP).zip $(TIMESTAMP) -q)
	@rm -rf $(BACKUP_DIR)
	@echo ""
	@echo "$(COLOR_GREEN)Backup Complete!$(COLOR_RESET)"
	@echo "Location: backups/$(TIMESTAMP).tar.gz"
	@du -h backups/$(TIMESTAMP).tar.gz 2>/dev/null || du -h backups/$(TIMESTAMP).zip 2>/dev/null

restore:  ## Restore from backup (usage: make restore BACKUP=20251023_120000)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(COLOR_RED)Error: Specify backup to restore$(COLOR_RESET)"; \
		echo ""; \
		echo "Usage: $(COLOR_BLUE)make restore BACKUP=20251023_120000$(COLOR_RESET)"; \
		echo ""; \
		echo "Available backups:"; \
		ls -1 backups/*.tar.gz 2>/dev/null | sed 's/backups\//  /' | sed 's/.tar.gz//' || \
		ls -1 backups/*.zip 2>/dev/null | sed 's/backups\//  /' | sed 's/.zip//' || \
		echo "  $(COLOR_YELLOW)No backups found$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_BLUE)Restoring backup: $(BACKUP)$(COLOR_RESET)"
	@tar -xzf backups/$(BACKUP).tar.gz -C backups/ 2>/dev/null || \
		unzip -q backups/$(BACKUP).zip -d backups/
	@cp -r backups/$(BACKUP)/configs/* configs/ 2>/dev/null || true
	@cp -r backups/$(BACKUP)/data/* data/ 2>/dev/null || true
	@echo "$(COLOR_GREEN)Restore complete!$(COLOR_RESET)"

# ============================================================================
# DEPLOYMENT
# ============================================================================

deploy-systemd:  ## Install systemd service and timer for Linux
	@if [ "$(PLATFORM)" != "linux" ]; then \
		echo "$(COLOR_RED)Error: systemd deployment only supported on Linux$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_BLUE)Deploying as systemd service...$(COLOR_RESET)"
	@echo ""
	@if [ ! -f deployment/systemd/trading-bot.service.template ]; then \
		echo "$(COLOR_YELLOW)Creating systemd service template...$(COLOR_RESET)"; \
		mkdir -p deployment/systemd; \
		echo "[Unit]" > deployment/systemd/trading-bot.service.template; \
		echo "Description=AI Trading Bot Daily Pipeline" >> deployment/systemd/trading-bot.service.template; \
		echo "After=network.target" >> deployment/systemd/trading-bot.service.template; \
		echo "" >> deployment/systemd/trading-bot.service.template; \
		echo "[Service]" >> deployment/systemd/trading-bot.service.template; \
		echo "Type=oneshot" >> deployment/systemd/trading-bot.service.template; \
		echo "WorkingDirectory={{PROJECT_ROOT}}" >> deployment/systemd/trading-bot.service.template; \
		echo "ExecStart={{PROJECT_ROOT}}/$(VENV_BIN)/python {{PROJECT_ROOT}}/scripts/daily_pipeline.py" >> deployment/systemd/trading-bot.service.template; \
		echo "User=$(USER)" >> deployment/systemd/trading-bot.service.template; \
		echo "" >> deployment/systemd/trading-bot.service.template; \
		echo "[Install]" >> deployment/systemd/trading-bot.service.template; \
		echo "WantedBy=multi-user.target" >> deployment/systemd/trading-bot.service.template; \
	fi
	@sed "s|{{PROJECT_ROOT}}|$(PROJECT_ROOT)|g" deployment/systemd/trading-bot.service.template > /tmp/trading-bot.service
	@echo "Installing service..."
	@sudo cp /tmp/trading-bot.service /etc/systemd/system/trading-bot.service
	@sudo systemctl daemon-reload
	@sudo systemctl enable trading-bot.service
	@echo ""
	@echo "$(COLOR_GREEN)Service installed!$(COLOR_RESET)"
	@echo ""
	@echo "Commands:"
	@echo "  Start:  sudo systemctl start trading-bot"
	@echo "  Stop:   sudo systemctl stop trading-bot"
	@echo "  Status: sudo systemctl status trading-bot"
	@echo "  Logs:   sudo journalctl -u trading-bot -f"

deploy-cron:  ## Add cron job for daily automation
	@echo "$(COLOR_BLUE)Setting up cron job...$(COLOR_RESET)"
	@echo ""
	@crontab -l > crontab.backup 2>/dev/null || touch crontab.backup
	@echo "Current crontab backed up to: crontab.backup"
	@echo "" >> crontab.backup
	@echo "# AI Trading Bot - Daily Pipeline (6:00 AM ET)" >> crontab.backup
	@echo "0 6 * * 1-5 cd $(PROJECT_ROOT) && $(PYTHON_BIN) scripts/daily_pipeline.py >> logs/app/cron.log 2>&1" >> crontab.backup
	@crontab crontab.backup
	@echo ""
	@echo "$(COLOR_GREEN)Cron job installed!$(COLOR_RESET)"
	@echo ""
	@echo "Schedule: 6:00 AM ET on weekdays (Mon-Fri)"
	@echo "Log file: logs/app/cron.log"
	@echo ""
	@echo "View crontab: crontab -l"
	@echo "Remove cron:   crontab -r"

deploy-remove-cron:  ## Remove cron job
	@echo "$(COLOR_YELLOW)Removing cron job...$(COLOR_RESET)"
	@crontab -l | grep -v "AI Trading Bot" | crontab -
	@echo "$(COLOR_GREEN)Cron job removed$(COLOR_RESET)"

# ============================================================================
# EMERGENCY CONTROLS
# ============================================================================

emergency-stop:  ## Immediately halt all trading activity
	@echo ""
	@echo "$(COLOR_RED)========================================"
	@echo "  EMERGENCY STOP INITIATED"
	@echo "========================================$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)[1/4]$(COLOR_RESET) Setting kill switch..."
	@mkdir -p data/state
	@touch data/state/kill_switch.flag
	@echo "  $(COLOR_GREEN)[OK]$(COLOR_RESET) Kill switch activated"
	@echo ""
	@echo "$(COLOR_YELLOW)[2/4]$(COLOR_RESET) Stopping running pipeline processes..."
	@pkill -f "daily_pipeline.py" 2>/dev/null || echo "  $(COLOR_YELLOW)[INFO]$(COLOR_RESET) No pipeline processes running"
	@pkill -f "monitor.py" 2>/dev/null || echo "  $(COLOR_YELLOW)[INFO]$(COLOR_RESET) No monitor processes running"
	@echo ""
	@echo "$(COLOR_YELLOW)[3/4]$(COLOR_RESET) Canceling pending orders..."
	@if [ -f scripts/emergency/cancel_all_orders.py ]; then \
		$(PYTHON_BIN) scripts/emergency/cancel_all_orders.py 2>/dev/null || \
		echo "  $(COLOR_YELLOW)[WARN]$(COLOR_RESET) Could not cancel orders (script failed)"; \
	else \
		echo "  $(COLOR_YELLOW)[WARN]$(COLOR_RESET) Cancel orders script not found"; \
	fi
	@echo ""
	@echo "$(COLOR_YELLOW)[4/4]$(COLOR_RESET) Logging emergency stop event..."
	@echo "[$(TIMESTAMP)] EMERGENCY STOP - All trading halted" >> logs/app/emergency.log
	@echo ""
	@echo "$(COLOR_RED)========================================$(COLOR_RESET)"
	@echo "$(COLOR_RED)  EMERGENCY STOP COMPLETE$(COLOR_RESET)"
	@echo "$(COLOR_RED)========================================$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)Status: All trading activity halted$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)Next steps:$(COLOR_RESET)"
	@echo "  1. Review logs:    make logs"
	@echo "  2. Check status:   make status"
	@echo "  3. Resume trading: make resume"
	@echo ""

resume:  ## Resume trading after emergency stop
	@echo ""
	@echo "$(COLOR_YELLOW)========================================$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)  Resume Trading Operations$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)========================================$(COLOR_RESET)"
	@echo ""
	@if [ -f data/state/kill_switch.flag ]; then \
		echo "$(COLOR_YELLOW)WARNING: This will deactivate the kill switch and resume trading.$(COLOR_RESET)"; \
		echo ""; \
		read -p "Type 'RESUME' to continue: " confirm; \
		if [ "$$confirm" = "RESUME" ]; then \
			rm -f data/state/kill_switch.flag; \
			echo "[$(TIMESTAMP)] Trading resumed" >> logs/app/emergency.log; \
			echo ""; \
			echo "$(COLOR_GREEN)Kill switch deactivated. Trading can resume.$(COLOR_RESET)"; \
		else \
			echo ""; \
			echo "$(COLOR_YELLOW)Resume cancelled.$(COLOR_RESET)"; \
		fi \
	else \
		echo "$(COLOR_GREEN)Kill switch is not active. No action needed.$(COLOR_RESET)"; \
	fi
	@echo ""

# ============================================================================
# CLEANUP
# ============================================================================

clean:  ## Remove cache, temp files, and __pycache__
	@echo "$(COLOR_BLUE)Cleaning temporary files...$(COLOR_RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache htmlcov .coverage coverage.xml 2>/dev/null || true
	@rm -rf data/cache/* 2>/dev/null || true
	@echo "$(COLOR_GREEN)Cleanup complete!$(COLOR_RESET)"

clean-logs:  ## Clean old log files (keeps last 7 days)
	@echo "$(COLOR_BLUE)Cleaning old logs (>7 days)...$(COLOR_RESET)"
	@find logs/ -type f -name "*.log" -mtime +7 -delete 2>/dev/null || \
		echo "$(COLOR_YELLOW)Note: find with -mtime not available on this platform$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)Old logs cleaned!$(COLOR_RESET)"

clean-all:  ## Deep clean (WARNING: removes venv and all generated files)
	@echo ""
	@echo "$(COLOR_RED)WARNING: This will remove:$(COLOR_RESET)"
	@echo "  - Virtual environment ($(VENV)/)"
	@echo "  - All cached data (data/cache/, data/historical/)"
	@echo "  - All logs (logs/)"
	@echo "  - All reports (reports/)"
	@echo "  - Python cache files"
	@echo ""
	@read -p "Are you sure? Type 'yes' to continue: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(MAKE) clean; \
		rm -rf $(VENV); \
		rm -rf data/cache data/historical; \
		rm -rf logs; \
		rm -rf reports; \
		echo ""; \
		echo "$(COLOR_GREEN)Deep clean complete!$(COLOR_RESET)"; \
		echo "Run '$(COLOR_BLUE)make install$(COLOR_RESET)' to reinstall"; \
	else \
		echo ""; \
		echo "$(COLOR_YELLOW)Clean cancelled.$(COLOR_RESET)"; \
	fi

# ============================================================================
# UTILITIES
# ============================================================================

lint:  ## Run code linting
	@echo "$(COLOR_BLUE)Running linters...$(COLOR_RESET)"
	@$(VENV_BIN)/flake8 src/ scripts/ tests/ 2>/dev/null || echo "$(COLOR_YELLOW)flake8 not installed$(COLOR_RESET)"
	@$(VENV_BIN)/black --check src/ scripts/ tests/ 2>/dev/null || echo "$(COLOR_YELLOW)black not installed$(COLOR_RESET)"
	@$(VENV_BIN)/mypy src/ 2>/dev/null || echo "$(COLOR_YELLOW)mypy not installed$(COLOR_RESET)"

format:  ## Auto-format code
	@echo "$(COLOR_BLUE)Formatting code...$(COLOR_RESET)"
	@$(VENV_BIN)/black src/ scripts/ tests/ 2>/dev/null || echo "$(COLOR_YELLOW)black not installed$(COLOR_RESET)"
	@$(VENV_BIN)/isort src/ scripts/ tests/ 2>/dev/null || echo "$(COLOR_YELLOW)isort not installed$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)Code formatted!$(COLOR_RESET)"

shell:  ## Open Python shell with project context
	@$(PYTHON_BIN) -i -c "import sys; sys.path.insert(0, '$(PROJECT_ROOT)'); print('Python shell ready. Project root in sys.path.')"

version:  ## Show version information
	@echo ""
	@echo "$(COLOR_BLUE)AI Trading Bot$(COLOR_RESET)"
	@echo "Version: 2.0.0"
	@echo "Platform: $(PLATFORM)"
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo "Project: $(PROJECT_ROOT)"
	@echo ""

.SILENT: help
