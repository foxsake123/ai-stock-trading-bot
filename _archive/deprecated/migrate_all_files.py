"""
Comprehensive File Migration Script
Moves all files to the new organized repository structure
"""

import os
import shutil
from pathlib import Path
import sys

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def migrate_files():
    """Migrate all files to new structure"""
    
    print("=" * 70)
    print("FILE MIGRATION TO NEW STRUCTURE")
    print("=" * 70)
    
    # Define comprehensive file migrations
    migrations = {
        "Trading Scripts": [
            ("main.py", "01_Trading_Scripts/main.py"),
            ("main_enhanced.py", "01_Trading_Scripts/main_enhanced.py"),
            ("run_trading_system.py", "01_Trading_Scripts/run_trading_system.py"),
            ("execute_trades_20250110.py", "01_Trading_Scripts/execute_trades.py"),
            ("simulate_trading.py", "01_Trading_Scripts/simulate_trading.py"),
            ("Core_Trading/place_alpaca_orders.py", "01_Trading_Scripts/place_alpaca_orders.py"),
            ("Core_Trading/place_alpaca_orders_enhanced.py", "01_Trading_Scripts/place_alpaca_orders_enhanced.py"),
        ],
        
        "DEE-BOT Files": [
            ("Bot_Strategies/DEE-BOT/place_dee_bot_orders.py", "04_Bot_Strategies/DEE_BOT/place_orders.py"),
            ("Bot_Strategies/DEE-BOT/place_dee_bot_orders_enhanced.py", "04_Bot_Strategies/DEE_BOT/place_orders_enhanced.py"),
            ("Bot_Strategies/DEE-BOT/place_dee_bot_alpaca_orders.py", "04_Bot_Strategies/DEE_BOT/place_alpaca_orders.py"),
            ("Bot_Strategies/DEE-BOT/place_dee_bot_sp100_orders.py", "04_Bot_Strategies/DEE_BOT/place_sp100_orders.py"),
            ("dee_bot_institutional_trades.py", "04_Bot_Strategies/DEE_BOT/institutional_trades.py"),
            ("place_dee_bot_orders.py", "04_Bot_Strategies/DEE_BOT/place_dee_bot_orders.py"),
            ("place_dee_bot_alpaca_orders.py", "04_Bot_Strategies/DEE_BOT/dee_bot_alpaca.py"),
        ],
        
        "SHORGAN-BOT Files": [
            ("Bot_Strategies/SHORGAN-BOT/place_shorgan_bot_orders.py", "04_Bot_Strategies/SHORGAN_BOT/place_orders.py"),
            ("Bot_Strategies/SHORGAN-BOT/place_shorgan_bot_orders_enhanced.py", "04_Bot_Strategies/SHORGAN_BOT/place_orders_enhanced.py"),
            ("shorgan_bot_catalyst_trades.py", "04_Bot_Strategies/SHORGAN_BOT/catalyst_trades.py"),
            ("shorgan_catalyst_simple.py", "04_Bot_Strategies/SHORGAN_BOT/catalyst_simple.py"),
            ("place_shorgan_bot_orders.py", "04_Bot_Strategies/SHORGAN_BOT/place_shorgan_bot_orders.py"),
        ],
        
        "Data Providers": [
            ("data/enhanced_providers.py", "05_Data_Providers/enhanced_providers.py"),
            ("data/data_providers.py", "05_Data_Providers/data_providers.py"),
            ("data/catalyst_detector.py", "05_Data_Providers/catalyst_detector.py"),
            ("data_collection_system.py", "05_Data_Providers/data_collection_system.py"),
        ],
        
        "Portfolio & Performance": [
            ("portfolio_tracker.py", "02_Portfolio_Data/portfolio_tracker.py"),
            ("position_monitor.py", "02_Portfolio_Data/position_monitor.py"),
            ("trading_dashboard.py", "02_Portfolio_Data/trading_dashboard.py"),
        ],
        
        "Risk Management": [
            ("risk_monitor.py", "06_Risk_Management/risk_monitor.py"),
            ("risk_management/portfolio_manager.py", "06_Risk_Management/portfolio_manager.py"),
            ("risk_management/risk_metrics.py", "06_Risk_Management/risk_metrics.py"),
            ("risk_management/position_sizing.py", "06_Risk_Management/position_sizing.py"),
        ],
        
        "Configuration": [
            (".env", "08_Configuration/.env"),
            ("requirements.txt", "08_Configuration/requirements.txt"),
            ("config/api_config.py", "08_Configuration/api_config.py"),
            ("config/sp100_universe.py", "08_Configuration/sp100_universe.py"),
            ("bot_credentials.md", "08_Configuration/bot_credentials.md"),
        ],
        
        "Documentation": [
            ("README.md", "07_Documentation/README_ORIGINAL.md"),
            ("README_NEW.md", "07_Documentation/README.md"),
            ("CLAUDE.md", "07_Documentation/CLAUDE.md"),
            ("LIVE_SESSION_SUMMARY.md", "07_Documentation/Session_Notes/LIVE_SESSION_SUMMARY.md"),
            ("DATA_INTEGRATION_SUMMARY.md", "07_Documentation/Session_Notes/DATA_INTEGRATION_SUMMARY.md"),
            ("SESSION_COMPLETE_SUMMARY.md", "07_Documentation/Session_Notes/SESSION_COMPLETE_SUMMARY.md"),
            ("REORGANIZATION_SUMMARY.md", "07_Documentation/Session_Notes/REORGANIZATION_SUMMARY.md"),
            ("TradingAgents_Multi-Agents LLM Financial Trading.pdf", "07_Documentation/Research_Papers/TradingAgents.pdf"),
            ("20250910_claude-shorgan-bot_am report.pdf", "07_Documentation/Research_Papers/shorgan_bot_report.pdf"),
        ],
        
        "Test Scripts": [
            ("test_alpaca_connection.py", "10_Utils/Tests/test_alpaca_connection.py"),
            ("test_data_sources.py", "10_Utils/Tests/test_data_sources.py"),
            ("test_enhanced_data.py", "10_Utils/Tests/test_enhanced_data.py"),
            ("test_reddit_sentiment.py", "10_Utils/Tests/test_reddit_sentiment.py"),
            ("check_trading_status.py", "10_Utils/Scripts/check_trading_status.py"),
            ("fix_orders.py", "10_Utils/Scripts/fix_orders.py"),
            ("quick_alpaca_order.py", "10_Utils/Scripts/quick_alpaca_order.py"),
        ],
        
        "Reports": [
            ("report_generator.py", "03_Research_Reports/report_generator.py"),
            ("automated_reporting_scheduler.py", "03_Research_Reports/reporting_scheduler.py"),
        ],
    }
    
    # Execute migrations
    success_count = 0
    error_count = 0
    
    for category, file_list in migrations.items():
        print(f"\n📁 Migrating {category}...")
        
        for src, dst in file_list:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if src_path.exists():
                try:
                    # Create destination directory if needed
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file (not move, to preserve originals during testing)
                    shutil.copy2(src_path, dst_path)
                    print(f"  ✓ {src} → {dst}")
                    success_count += 1
                except Exception as e:
                    print(f"  ✗ Error: {src} - {str(e)[:50]}")
                    error_count += 1
            else:
                # Skip if file doesn't exist
                pass
    
    # Create .gitignore for new structure
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
*.csv
*.json
*.pkl
*.db

# Logs
*.log
logs/

# Secrets
.env
.env.*
bot_credentials.md

# MacOS
.DS_Store

# Windows
Thumbs.db
desktop.ini

# Archive
Archive/cache/
"""
    
    with open(".gitignore_new", "w") as f:
        f.write(gitignore_content)
    print("\n✓ Created .gitignore_new")
    
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"✓ Successfully migrated: {success_count} files")
    if error_count > 0:
        print(f"✗ Errors: {error_count} files")
    
    print("\nNext steps:")
    print("1. Review the migrated files in the new structure")
    print("2. Test that imports still work")
    print("3. Delete old directories once confirmed")
    print("4. Rename README_NEW.md to README.md")
    print("5. Commit to git")
    
    return success_count, error_count

if __name__ == "__main__":
    migrate_files()