"""
Repository Reorganization Script
Restructures the AI Trading Bot repository to match professional organization
Based on ChatGPT-Micro-Cap-Experiment structure
"""

import os
import sys
import shutil
from pathlib import Path
import json

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def create_new_structure():
    """Create the new organized directory structure"""
    
    base_path = Path(".")
    
    # Define new structure
    new_structure = {
        "01_Trading_Scripts": "Core trading engines and bots",
        "02_Portfolio_Data": "Daily portfolio tracking and CSVs",
        "03_Research_Reports": "Weekly/Daily research and analysis",
        "04_Bot_Strategies": "DEE-BOT and SHORGAN-BOT strategies",
        "05_Data_Providers": "Market data, news, and sentiment providers",
        "06_Risk_Management": "Risk controls and position sizing",
        "07_Documentation": "Project documentation and guides",
        "08_Configuration": "Settings, API configs, and environment",
        "09_Backtesting": "Historical testing and performance analysis",
        "10_Utils": "Helper scripts and tools",
        "Archive": "Old versions and deprecated code"
    }
    
    print("=" * 70)
    print("REPOSITORY REORGANIZATION PLAN")
    print("=" * 70)
    
    # Create new directories
    for dir_name, description in new_structure.items():
        dir_path = base_path / dir_name
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✓ Created: {dir_name}/")
            print(f"  Purpose: {description}")
    
    return new_structure

def create_file_mapping():
    """Map existing files to new locations"""
    
    mapping = {
        # Trading Scripts
        "Core_Trading/*.py": "01_Trading_Scripts/",
        "place_*.py": "01_Trading_Scripts/",
        "execute_trades*.py": "01_Trading_Scripts/",
        "run_trading_system.py": "01_Trading_Scripts/",
        "main.py": "01_Trading_Scripts/",
        "main_enhanced.py": "01_Trading_Scripts/",
        
        # Portfolio Data
        "Portfolio Data/*": "02_Portfolio_Data/",
        "portfolio_tracker.py": "02_Portfolio_Data/",
        "position_monitor.py": "02_Portfolio_Data/",
        
        # Research Reports
        "Research_Reports/*": "03_Research_Reports/Weekly/",
        "deep_research_indexes/*": "03_Research_Reports/Deep_Research/",
        "Trading Reports/*": "03_Research_Reports/Daily/",
        "*_SUMMARY.md": "03_Research_Reports/Session_Summaries/",
        
        # Bot Strategies
        "Bot_Strategies/DEE-BOT/*": "04_Bot_Strategies/DEE_BOT/",
        "Bot_Strategies/SHORGAN-BOT/*": "04_Bot_Strategies/SHORGAN_BOT/",
        "agents/*": "04_Bot_Strategies/AI_Agents/",
        
        # Data Providers
        "data/*.py": "05_Data_Providers/",
        "Market_Data/*": "05_Data_Providers/Market_Data/",
        "communication/*": "05_Data_Providers/Communication/",
        
        # Risk Management
        "risk_management/*": "06_Risk_Management/",
        "risk_monitor.py": "06_Risk_Management/",
        
        # Documentation
        "Documentation/*": "07_Documentation/",
        "docs/*": "07_Documentation/",
        "*.md": "07_Documentation/",
        "TradingAgents*.pdf": "07_Documentation/Research_Papers/",
        
        # Configuration
        "config/*": "08_Configuration/",
        "Configuration/*": "08_Configuration/",
        ".env*": "08_Configuration/",
        "requirements.txt": "08_Configuration/",
        
        # Backtesting
        "Backtesting/*": "09_Backtesting/",
        "Performance_Tracking/*": "09_Backtesting/Performance/",
        
        # Utils
        "tools/*": "10_Utils/",
        "test_*.py": "10_Utils/Tests/",
        "check_*.py": "10_Utils/Scripts/",
        
        # Archive
        "archive/*": "Archive/",
        "__pycache__/*": "Archive/cache/",
    }
    
    return mapping

def reorganize_repository():
    """Execute the reorganization"""
    
    print("\n" + "=" * 70)
    print("STARTING REPOSITORY REORGANIZATION")
    print("=" * 70)
    
    # Create new structure
    new_structure = create_new_structure()
    
    # Create subdirectories
    subdirs = {
        "01_Trading_Scripts": ["Live", "Paper", "Modules"],
        "02_Portfolio_Data": ["Daily_Snapshots", "Trade_History", "Performance"],
        "03_Research_Reports": ["Weekly", "Daily", "Deep_Research", "Session_Summaries"],
        "04_Bot_Strategies": ["DEE_BOT", "SHORGAN_BOT", "AI_Agents", "Common"],
        "05_Data_Providers": ["Market_Data", "News", "Sentiment", "Economic", "Communication"],
        "06_Risk_Management": ["Models", "Reports", "Alerts"],
        "07_Documentation": ["Guides", "API_Docs", "Research_Papers", "Session_Notes"],
        "08_Configuration": ["API_Keys", "Trading_Rules", "Environment"],
        "09_Backtesting": ["Results", "Performance", "Strategies"],
        "10_Utils": ["Tests", "Scripts", "Helpers"]
    }
    
    print("\n📁 Creating subdirectories...")
    for parent, subs in subdirs.items():
        for sub in subs:
            subdir_path = Path(parent) / sub
            subdir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {parent}/{sub}/")
    
    # Create README for each main directory
    print("\n📝 Creating README files...")
    for dir_name, description in new_structure.items():
        readme_path = Path(dir_name) / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(f"# {dir_name.replace('_', ' ')}\n\n")
                f.write(f"{description}\n\n")
                f.write("## Contents\n\n")
                if dir_name in subdirs:
                    for sub in subdirs[dir_name]:
                        f.write(f"- **{sub}/**: \n")
            print(f"  ✓ {dir_name}/README.md")
    
    print("\n✅ Repository structure created successfully!")
    print("\nNext steps:")
    print("1. Review the new structure")
    print("2. Run move_files.py to migrate existing files")
    print("3. Update import paths in Python scripts")
    print("4. Commit changes to git")
    
    return True

def create_move_script():
    """Create a script to move files to new locations"""
    
    move_script = '''"""
File Migration Script
Moves files to the new organized structure
"""

import os
import shutil
from pathlib import Path

def move_files():
    """Move files to new organized locations"""
    
    # Priority files to move
    moves = [
        # Trading Scripts
        ("main.py", "01_Trading_Scripts/main.py"),
        ("main_enhanced.py", "01_Trading_Scripts/main_enhanced.py"),
        ("run_trading_system.py", "01_Trading_Scripts/run_trading_system.py"),
        
        # Bot-specific
        ("place_dee_bot_orders.py", "04_Bot_Strategies/DEE_BOT/place_orders.py"),
        ("place_shorgan_bot_orders.py", "04_Bot_Strategies/SHORGAN_BOT/place_orders.py"),
        
        # Data providers
        ("data/enhanced_providers.py", "05_Data_Providers/enhanced_providers.py"),
        ("data/catalyst_detector.py", "05_Data_Providers/catalyst_detector.py"),
        
        # Configuration
        (".env", "08_Configuration/.env"),
        ("requirements.txt", "08_Configuration/requirements.txt"),
        
        # Documentation
        ("README.md", "07_Documentation/README.md"),
        ("CLAUDE.md", "07_Documentation/CLAUDE.md"),
    ]
    
    print("Moving files to new locations...")
    
    for src, dst in moves:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"  ✓ {src} -> {dst}")
    
    print("\\nFile migration complete!")

if __name__ == "__main__":
    move_files()
'''
    
    with open("move_files.py", "w", encoding="utf-8") as f:
        f.write(move_script)
    
    print("\n📄 Created move_files.py script")

def create_main_readme():
    """Create a professional README for the repository"""
    
    readme_content = '''# AI Stock Trading Bot System

## 📊 Multi-Agent AI Trading Platform

An advanced trading system using multiple AI agents for institutional and catalyst-based trading strategies.

## 🏗️ Repository Structure

```
ai-stock-trading-bot/
├── 01_Trading_Scripts/     # Core trading engines and execution
├── 02_Portfolio_Data/      # Daily tracking and performance data
├── 03_Research_Reports/    # AI-generated research and analysis
├── 04_Bot_Strategies/      # DEE-BOT and SHORGAN-BOT strategies
├── 05_Data_Providers/      # Market data, news, and sentiment
├── 06_Risk_Management/     # Risk controls and position sizing
├── 07_Documentation/       # Guides and documentation
├── 08_Configuration/       # Settings and API configurations
├── 09_Backtesting/        # Historical testing and validation
├── 10_Utils/              # Helper scripts and utilities
└── Archive/               # Deprecated code and old versions
```

## 🤖 Trading Bots

### DEE-BOT (Institutional Strategy)
- Focus: S&P 100 stocks
- Strategy: Institutional accumulation patterns
- Timeframe: Medium to long-term positions

### SHORGAN-BOT (Catalyst Strategy)
- Focus: High-momentum stocks
- Strategy: Catalyst-driven short-term trades
- Timeframe: 1-7 day positions

## 📈 Performance

- **Combined Portfolio**: ~$204,210
- **YTD Return**: +4.6%
- **Active Positions**: 14 stocks

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   cd 08_Configuration
   pip install -r requirements.txt
   cp .env.example .env
   # Add your API keys to .env
   ```

2. **Run Trading Bots**
   ```bash
   # DEE-BOT
   python 04_Bot_Strategies/DEE_BOT/place_orders.py
   
   # SHORGAN-BOT
   python 04_Bot_Strategies/SHORGAN_BOT/place_orders.py
   ```

3. **Monitor Performance**
   ```bash
   python 02_Portfolio_Data/portfolio_tracker.py
   ```

## 📊 Data Sources

- **Market Data**: Alpha Vantage, Yahoo Finance
- **News**: NewsAPI
- **Social Sentiment**: Reddit (r/wallstreetbets)
- **Economic Data**: FRED API
- **Trading**: Alpaca Markets (Paper Trading)

## 🛡️ Risk Management

- Position sizing: Max 20% per position
- Daily loss limit: 5% circuit breaker
- Stop-loss: Mandatory on all positions
- Portfolio heat: Maximum 10 concurrent positions

## 📝 Documentation

See `/07_Documentation/` for detailed guides:
- [Setup Guide](07_Documentation/Guides/SETUP.md)
- [API Configuration](07_Documentation/API_Docs/APIs.md)
- [Trading Strategies](07_Documentation/Guides/STRATEGIES.md)

## 🔧 Development

Based on the TradingAgents research paper implementing 7 specialized AI agents with consensus-based decision making.

## ⚠️ Disclaimer

This is a paper trading system for educational purposes. Not financial advice.

## 📄 License

MIT License - See LICENSE file for details
'''
    
    with open("README_NEW.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📄 Created README_NEW.md")

if __name__ == "__main__":
    # Execute reorganization
    reorganize_repository()
    create_move_script()
    create_main_readme()
    
    print("\n" + "=" * 70)
    print("REORGANIZATION COMPLETE!")
    print("=" * 70)
    print("\nYour repository now has a professional structure similar to")
    print("the ChatGPT-Micro-Cap-Experiment repository.")
    print("\n✅ New directories created")
    print("✅ README files generated")
    print("✅ Move script prepared")
    print("\nNext: Run 'python move_files.py' to migrate your files")