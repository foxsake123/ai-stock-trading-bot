#!/usr/bin/env python3
"""
Main trading system runner - executes at 9:30 AM ET
"""
import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
sys.path.append('.')

from automated_trade_executor import AutomatedTradeExecutor, ExecutionMode
from trade_signal_generator import SignalRouter

# Configure logging
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_morning_trading():
    """Main trading execution for market open"""
    
    logger.info("="*50)
    logger.info(f"Starting Trading System at {datetime.now()}")
    logger.info("="*50)
    
    # Get execution mode from environment
    mode_str = os.getenv("EXECUTION_MODE", "paper").lower()
    mode_map = {
        'paper': ExecutionMode.PAPER,
        'manual': ExecutionMode.MANUAL_APPROVAL,
        'semi': ExecutionMode.SEMI_AUTO,
        'full': ExecutionMode.FULL_AUTO
    }
    mode = mode_map.get(mode_str, ExecutionMode.PAPER)
    
    logger.info(f"Execution Mode: {mode.value.upper()}")
    
    # Initialize signal router with executor
    router = SignalRouter(mode)
    
    # Check if we have morning recommendations from bots
    dee_bot_file = Path("dee_bot/data/morning_recommendations.json")
    shorgan_bot_file = Path("shorgan-bot/data/morning_recommendations.json")
    
    # Process dee-bot recommendations if available
    if dee_bot_file.exists():
        import json
        with open(dee_bot_file, 'r') as f:
            dee_recommendations = json.load(f)
        logger.info(f"Processing {len(dee_recommendations.get('recommendations', []))} dee-bot signals")
        await router.route_dee_bot_signals(dee_recommendations)
    else:
        logger.info("No dee-bot recommendations found")
    
    # Process shorgan-bot recommendations if available
    if shorgan_bot_file.exists():
        import json
        with open(shorgan_bot_file, 'r') as f:
            shorgan_recommendations = json.load(f)
        logger.info(f"Processing {len(shorgan_recommendations.get('recommendations', []))} shorgan-bot signals")
        await router.route_shorgan_bot_signals(shorgan_recommendations)
    else:
        logger.info("No shorgan-bot recommendations found")
    
    # Get status
    status = router.get_status()
    logger.info(f"Trading System Status:")
    logger.info(f"  Portfolio Value: ${status['executor_status']['portfolio_value']:,.2f}")
    logger.info(f"  Open Positions: {len(status['executor_status']['positions'])}")
    logger.info(f"  Pending Signals: {status['pending_signals']}")
    
    # If manual approval mode, handle approvals
    if mode == ExecutionMode.MANUAL_APPROVAL and status['pending_signals'] > 0:
        logger.info("Manual approval required for pending trades")
        await router.executor.approve_pending_trades()
    
    logger.info("Trading system execution complete")

if __name__ == "__main__":
    asyncio.run(run_morning_trading())