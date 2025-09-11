#!/usr/bin/env python3
"""
Automated Trade Execution System
Executes trades for dee-bot and shorgan-bot with safety controls
IMPORTANT: Start in PAPER mode for safety
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """Trading execution modes"""
    PAPER = "paper"           # Paper trading only
    MANUAL_APPROVAL = "manual" # Require manual approval for each trade
    SEMI_AUTO = "semi_auto"   # Auto-execute small trades, manual for large
    FULL_AUTO = "full_auto"   # Fully automated (USE WITH EXTREME CAUTION)

class RiskLevel(Enum):
    """Risk levels for trades"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class TradeSignal:
    """Trade signal from AI agents"""
    bot_name: str
    ticker: str
    action: str  # BUY, SELL
    shares: int
    limit_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    confidence: float
    reason: str
    risk_level: RiskLevel
    
@dataclass
class ExecutionResult:
    """Result of trade execution"""
    success: bool
    order_id: Optional[str]
    message: str
    executed_price: Optional[float]
    executed_shares: Optional[int]
    
class SafetyControls:
    """Safety controls and risk limits"""
    
    def __init__(self):
        # Position limits
        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", "50000"))  # $50k max per position
        self.max_portfolio_positions = int(os.getenv("MAX_POSITIONS", "10"))
        
        # Daily limits
        self.max_daily_trades = int(os.getenv("MAX_DAILY_TRADES", "20"))
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", "10000"))  # $10k max daily loss
        
        # Risk limits
        self.max_portfolio_risk = 0.02  # 2% max portfolio risk
        self.position_size_limit = 0.05  # 5% max position size
        
        # Restricted stocks
        self.blacklist = set(os.getenv("BLACKLIST_STOCKS", "").split(","))
        self.whitelist = set(os.getenv("WHITELIST_STOCKS", "").split(",")) if os.getenv("WHITELIST_STOCKS") else None
        
        # Trading hours (ET)
        self.market_open = "09:30"
        self.market_close = "16:00"
        self.allow_premarket = os.getenv("ALLOW_PREMARKET", "false").lower() == "true"
        self.allow_afterhours = os.getenv("ALLOW_AFTERHOURS", "false").lower() == "true"
        
        # Counters
        self.daily_trades = 0
        self.daily_loss = 0.0
        self.last_reset = datetime.now().date()
    
    def check_trade_allowed(self, signal: TradeSignal, portfolio_value: float) -> Tuple[bool, str]:
        """Check if trade passes all safety controls"""
        
        # Reset daily counters if new day
        if datetime.now().date() > self.last_reset:
            self.daily_trades = 0
            self.daily_loss = 0.0
            self.last_reset = datetime.now().date()
        
        # Check blacklist/whitelist
        if signal.ticker in self.blacklist:
            return False, f"Stock {signal.ticker} is blacklisted"
        
        if self.whitelist and signal.ticker not in self.whitelist:
            return False, f"Stock {signal.ticker} not in whitelist"
        
        # Check position size
        position_value = signal.shares * (signal.limit_price or 0)
        if position_value > self.max_position_size:
            return False, f"Position size ${position_value:.2f} exceeds limit ${self.max_position_size:.2f}"
        
        if position_value > portfolio_value * self.position_size_limit:
            return False, f"Position size exceeds {self.position_size_limit*100}% of portfolio"
        
        # Check daily trade limit
        if self.daily_trades >= self.max_daily_trades:
            return False, f"Daily trade limit ({self.max_daily_trades}) reached"
        
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            return False, f"Daily loss limit (${self.max_daily_loss:.2f}) reached"
        
        # Check trading hours
        now = datetime.now()
        market_open = datetime.strptime(self.market_open, "%H:%M").time()
        market_close = datetime.strptime(self.market_close, "%H:%M").time()
        
        if not self.allow_premarket and now.time() < market_open:
            return False, "Pre-market trading not allowed"
        
        if not self.allow_afterhours and now.time() > market_close:
            return False, "After-hours trading not allowed"
        
        # Check risk level
        if signal.risk_level == RiskLevel.EXTREME:
            return False, "Extreme risk trades not allowed"
        
        # Check confidence threshold
        if signal.confidence < 0.6:
            return False, f"Confidence {signal.confidence:.2f} below minimum threshold (0.60)"
        
        return True, "Trade approved"
    
    def update_counters(self, trade_pnl: float = 0):
        """Update daily counters"""
        self.daily_trades += 1
        if trade_pnl < 0:
            self.daily_loss += abs(trade_pnl)

class AlpacaExecutor:
    """Alpaca broker execution handler"""
    
    def __init__(self, paper: bool = True):
        """Initialize Alpaca connection
        
        Args:
            paper: Use paper trading account (default True for safety)
        """
        self.paper = paper
        
        # Get credentials
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found in environment")
        
        # Set base URL based on mode
        if paper:
            self.base_url = "https://paper-api.alpaca.markets"
            logger.info("Alpaca executor initialized in PAPER mode")
        else:
            self.base_url = "https://api.alpaca.markets"
            logger.warning("Alpaca executor initialized in LIVE mode - USE CAUTION!")
        
        # Initialize API
        self.api = tradeapi.REST(
            key_id=self.api_key,
            secret_key=self.secret_key,
            base_url=self.base_url,
            api_version='v2'
        )
        
        # Verify connection
        try:
            self.account = self.api.get_account()
            logger.info(f"Connected to Alpaca. Buying power: ${self.account.buying_power}")
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            raise
    
    async def execute_trade(self, signal: TradeSignal) -> ExecutionResult:
        """Execute a trade through Alpaca"""
        
        try:
            # Prepare order parameters
            order_params = {
                'symbol': signal.ticker,
                'qty': signal.shares,
                'side': signal.action.lower(),
                'type': 'limit' if signal.limit_price else 'market',
                'time_in_force': 'day'
            }
            
            if signal.limit_price:
                order_params['limit_price'] = signal.limit_price
            
            # Add stop loss as OCO (One-Cancels-Other) if provided
            if signal.stop_loss:
                order_params['stop_loss'] = {
                    'stop_price': signal.stop_loss
                }
            
            # Submit order
            order = self.api.submit_order(**order_params)
            
            logger.info(f"Order submitted: {signal.action} {signal.shares} {signal.ticker} @ ${signal.limit_price or 'market'}")
            
            # Wait for order fill (up to 30 seconds for limit orders)
            max_wait = 30 if signal.limit_price else 5
            for _ in range(max_wait):
                await asyncio.sleep(1)
                order = self.api.get_order(order.id)
                
                if order.status == 'filled':
                    return ExecutionResult(
                        success=True,
                        order_id=order.id,
                        message=f"Order filled at ${order.filled_avg_price}",
                        executed_price=float(order.filled_avg_price),
                        executed_shares=int(order.filled_qty)
                    )
                elif order.status in ['canceled', 'rejected', 'expired']:
                    return ExecutionResult(
                        success=False,
                        order_id=order.id,
                        message=f"Order {order.status}",
                        executed_price=None,
                        executed_shares=None
                    )
            
            # Order still pending
            return ExecutionResult(
                success=False,
                order_id=order.id,
                message="Order pending - not filled within timeout",
                executed_price=None,
                executed_shares=None
            )
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return ExecutionResult(
                success=False,
                order_id=None,
                message=str(e),
                executed_price=None,
                executed_shares=None
            )
    
    def get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        try:
            account = self.api.get_account()
            return float(account.portfolio_value)
        except Exception as e:
            logger.error(f"Failed to get portfolio value: {e}")
            return 0.0
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            positions = self.api.list_positions()
            return [
                {
                    'symbol': p.symbol,
                    'qty': int(p.qty),
                    'avg_cost': float(p.avg_entry_price),
                    'market_value': float(p.market_value),
                    'unrealized_pl': float(p.unrealized_pl)
                }
                for p in positions
            ]
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []

class AutomatedTradeExecutor:
    """Main automated trade execution system"""
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.PAPER):
        self.mode = mode
        self.safety = SafetyControls()
        
        # Initialize broker based on mode
        if mode == ExecutionMode.PAPER:
            self.broker = AlpacaExecutor(paper=True)
        else:
            # Even in other modes, start with paper for safety
            # Change to paper=False only when fully tested
            self.broker = AlpacaExecutor(paper=True)
            if mode == ExecutionMode.FULL_AUTO:
                logger.warning("FULL AUTO mode selected - trades will execute automatically!")
        
        # Signal queue
        self.signal_queue: List[TradeSignal] = []
        
        # Execution log
        self.execution_log = Path("data/execution_log.json")
        self.execution_log.parent.mkdir(exist_ok=True)
        
        # Load existing log
        self.execution_history = self._load_execution_log()
    
    def _load_execution_log(self) -> List[Dict]:
        """Load execution history"""
        if self.execution_log.exists():
            with open(self.execution_log, 'r') as f:
                return json.load(f)
        return []
    
    def _save_execution_log(self):
        """Save execution history"""
        with open(self.execution_log, 'w') as f:
            json.dump(self.execution_history, f, indent=2, default=str)
    
    async def add_signal(self, signal: TradeSignal):
        """Add a trade signal to the queue"""
        
        # Check safety controls
        portfolio_value = self.broker.get_portfolio_value()
        allowed, reason = self.safety.check_trade_allowed(signal, portfolio_value)
        
        if not allowed:
            logger.warning(f"Trade rejected: {reason}")
            self._log_execution(signal, None, reason)
            return
        
        # Add to queue based on mode
        if self.mode == ExecutionMode.MANUAL_APPROVAL:
            logger.info(f"Trade pending approval: {signal.action} {signal.shares} {signal.ticker}")
            self.signal_queue.append(signal)
            
        elif self.mode == ExecutionMode.SEMI_AUTO:
            # Auto-execute if low risk and small size
            position_value = signal.shares * (signal.limit_price or 100)
            if signal.risk_level == RiskLevel.LOW and position_value < 10000:
                await self.execute_signal(signal)
            else:
                logger.info(f"Large/risky trade pending approval: {signal.ticker}")
                self.signal_queue.append(signal)
                
        elif self.mode == ExecutionMode.FULL_AUTO:
            # Execute immediately
            await self.execute_signal(signal)
            
        else:  # PAPER mode
            # Execute in paper account
            await self.execute_signal(signal)
    
    async def execute_signal(self, signal: TradeSignal):
        """Execute a trade signal"""
        
        logger.info(f"Executing trade: {signal.bot_name} - {signal.action} {signal.shares} {signal.ticker}")
        
        # Execute through broker
        result = await self.broker.execute_trade(signal)
        
        # Update safety counters
        if result.success:
            self.safety.update_counters()
            logger.info(f"Trade executed successfully: {result.message}")
        else:
            logger.error(f"Trade execution failed: {result.message}")
        
        # Log execution
        self._log_execution(signal, result, "Executed")
        
        return result
    
    def _log_execution(self, signal: TradeSignal, result: Optional[ExecutionResult], status: str):
        """Log trade execution"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'bot_name': signal.bot_name,
            'ticker': signal.ticker,
            'action': signal.action,
            'shares': signal.shares,
            'limit_price': signal.limit_price,
            'confidence': signal.confidence,
            'reason': signal.reason,
            'status': status,
            'success': result.success if result else False,
            'order_id': result.order_id if result else None,
            'executed_price': result.executed_price if result else None,
            'message': result.message if result else status
        }
        
        self.execution_history.append(log_entry)
        self._save_execution_log()
    
    async def approve_pending_trades(self):
        """Manually approve pending trades (for MANUAL_APPROVAL mode)"""
        
        if not self.signal_queue:
            logger.info("No pending trades to approve")
            return
        
        logger.info(f"Pending trades: {len(self.signal_queue)}")
        
        for i, signal in enumerate(self.signal_queue):
            print(f"\n{i+1}. {signal.action} {signal.shares} {signal.ticker}")
            print(f"   Reason: {signal.reason}")
            print(f"   Confidence: {signal.confidence:.2%}")
            print(f"   Risk: {signal.risk_level.value}")
            
            response = input("   Approve? (y/n/skip): ").lower()
            
            if response == 'y':
                await self.execute_signal(signal)
            elif response == 'n':
                self._log_execution(signal, None, "Rejected by user")
            else:
                continue  # Skip for now
        
        # Clear processed signals
        self.signal_queue.clear()
    
    def get_status(self) -> Dict:
        """Get executor status"""
        return {
            'mode': self.mode.value,
            'portfolio_value': self.broker.get_portfolio_value(),
            'positions': self.broker.get_positions(),
            'pending_signals': len(self.signal_queue),
            'daily_trades': self.safety.daily_trades,
            'daily_loss': self.safety.daily_loss,
            'max_daily_trades': self.safety.max_daily_trades,
            'max_daily_loss': self.safety.max_daily_loss
        }

async def main():
    """Main execution loop"""
    
    # Get execution mode from environment or default to PAPER
    mode_str = os.getenv("EXECUTION_MODE", "paper").lower()
    mode_map = {
        'paper': ExecutionMode.PAPER,
        'manual': ExecutionMode.MANUAL_APPROVAL,
        'semi': ExecutionMode.SEMI_AUTO,
        'full': ExecutionMode.FULL_AUTO
    }
    mode = mode_map.get(mode_str, ExecutionMode.PAPER)
    
    # Initialize executor
    executor = AutomatedTradeExecutor(mode)
    
    logger.info(f"Trade Executor Started in {mode.value.upper()} mode")
    logger.info(f"Safety Controls: Max position ${executor.safety.max_position_size:,.0f}")
    logger.info(f"Daily limits: {executor.safety.max_daily_trades} trades, ${executor.safety.max_daily_loss:,.0f} loss")
    
    # Monitor for signals from both bots
    logger.info("Monitoring for trade signals from dee-bot and shorgan-bot...")
    
    # Run continuous monitoring loop
    try:
        while True:
            # Check for new signals from bots (would be integrated with actual bot output)
            # For now, just maintain the executor ready state
            
            if mode == ExecutionMode.MANUAL_APPROVAL and executor.signal_queue:
                await executor.approve_pending_trades()
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        logger.info("Shutting down trade executor...")
    
    # Show status
    status = executor.get_status()
    print(f"\nExecutor Status:")
    print(f"  Portfolio Value: ${status['portfolio_value']:,.2f}")
    print(f"  Open Positions: {len(status['positions'])}")
    print(f"  Daily Trades: {status['daily_trades']}/{status['max_daily_trades']}")
    
if __name__ == "__main__":
    asyncio.run(main())