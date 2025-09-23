#!/usr/bin/env python3
"""
Trade Signal Generator for Bot Integration
Converts bot recommendations to trade signals for automated executor
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys
sys.path.append('.')

from automated_trade_executor import TradeSignal, RiskLevel, AutomatedTradeExecutor, ExecutionMode

logger = logging.getLogger(__name__)

class BotSignalGenerator:
    """Converts bot analysis to trade signals"""
    
    def __init__(self, bot_name: str, executor: Optional[AutomatedTradeExecutor] = None):
        """Initialize signal generator
        
        Args:
            bot_name: Name of the bot (dee-bot or shorgan-bot)
            executor: Optional automated trade executor instance
        """
        self.bot_name = bot_name
        self.executor = executor
        
        # Signal generation thresholds
        self.min_confidence = 0.65
        self.max_signals_per_day = 5
        
        # Track signals
        self.signals_today = 0
        self.last_signal_date = datetime.now().date()
    
    def parse_bot_recommendation(self, recommendation: Dict) -> Optional[TradeSignal]:
        """Parse bot recommendation into trade signal
        
        Args:
            recommendation: Bot recommendation dict
            
        Returns:
            TradeSignal if valid, None otherwise
        """
        try:
            # Reset daily counter if new day
            if datetime.now().date() > self.last_signal_date:
                self.signals_today = 0
                self.last_signal_date = datetime.now().date()
            
            # Check daily limit
            if self.signals_today >= self.max_signals_per_day:
                logger.warning(f"{self.bot_name}: Daily signal limit reached")
                return None
            
            # Extract recommendation details
            action = recommendation.get('action', '').upper()
            if action not in ['BUY', 'SELL']:
                return None
            
            ticker = recommendation.get('ticker')
            confidence = recommendation.get('confidence', 0)
            
            # Check confidence threshold
            if confidence < self.min_confidence:
                logger.info(f"{self.bot_name}: Confidence {confidence:.2f} below threshold for {ticker}")
                return None
            
            # Calculate position size based on confidence
            base_shares = 100  # Base position size
            shares = int(base_shares * (confidence / 0.8))  # Scale with confidence
            
            # Determine risk level
            risk_score = recommendation.get('risk_score', 0.5)
            if risk_score < 0.3:
                risk_level = RiskLevel.LOW
            elif risk_score < 0.6:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.HIGH
            
            # Get price targets
            current_price = recommendation.get('current_price', 0)
            stop_loss = recommendation.get('stop_loss', current_price * 0.98)  # 2% stop loss default
            take_profit = recommendation.get('take_profit', current_price * 1.05)  # 5% profit target default
            
            # Create trade signal
            signal = TradeSignal(
                bot_name=self.bot_name,
                ticker=ticker,
                action=action,
                shares=shares,
                limit_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                reason=recommendation.get('reason', 'AI analysis'),
                risk_level=risk_level
            )
            
            self.signals_today += 1
            logger.info(f"{self.bot_name}: Generated signal for {ticker} - {action} {shares} shares")
            
            return signal
            
        except Exception as e:
            logger.error(f"Failed to parse recommendation: {e}")
            return None
    
    async def process_recommendations(self, recommendations: List[Dict]):
        """Process multiple recommendations
        
        Args:
            recommendations: List of bot recommendations
        """
        for rec in recommendations:
            signal = self.parse_bot_recommendation(rec)
            
            if signal and self.executor:
                await self.executor.add_signal(signal)
                await asyncio.sleep(1)  # Rate limit

class DeeBot SignalGenerator(BotSignalGenerator):
    """Signal generator for dee-bot"""
    
    def __init__(self, executor: Optional[AutomatedTradeExecutor] = None):
        super().__init__("dee-bot", executor)
        
        # Dee-bot specific settings
        self.focus_sectors = ['technology', 'healthcare', 'finance']
        self.preferred_market_cap = 'large'  # large, mid, small
    
    def enhance_signal(self, signal: TradeSignal, market_data: Dict) -> TradeSignal:
        """Enhance signal with dee-bot specific analysis
        
        Args:
            signal: Base trade signal
            market_data: Additional market data
            
        Returns:
            Enhanced trade signal
        """
        # Add dee-bot's deep research analysis
        if market_data.get('sector') in self.focus_sectors:
            signal.confidence *= 1.1  # Boost confidence for focus sectors
        
        # Adjust for market cap preference
        market_cap = market_data.get('market_cap', 'unknown')
        if market_cap == self.preferred_market_cap:
            signal.confidence *= 1.05
        
        # Cap confidence at 1.0
        signal.confidence = min(signal.confidence, 1.0)
        
        return signal

class ShorganBotSignalGenerator(BotSignalGenerator):
    """Signal generator for shorgan-bot"""
    
    def __init__(self, executor: Optional[AutomatedTradeExecutor] = None):
        super().__init__("shorgan-bot", executor)
        
        # Shorgan-bot specific settings
        self.momentum_weight = 0.3
        self.value_weight = 0.3
        self.sentiment_weight = 0.4
    
    def calculate_composite_score(self, metrics: Dict) -> float:
        """Calculate composite score for shorgan-bot
        
        Args:
            metrics: Bot analysis metrics
            
        Returns:
            Composite score 0-1
        """
        momentum_score = metrics.get('momentum_score', 0.5)
        value_score = metrics.get('value_score', 0.5)
        sentiment_score = metrics.get('sentiment_score', 0.5)
        
        composite = (
            momentum_score * self.momentum_weight +
            value_score * self.value_weight +
            sentiment_score * self.sentiment_weight
        )
        
        return composite

class SignalRouter:
    """Routes signals from multiple bots to executor"""
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.PAPER):
        """Initialize signal router
        
        Args:
            mode: Execution mode for automated executor
        """
        self.executor = AutomatedTradeExecutor(mode)
        
        # Initialize bot signal generators
        self.dee_generator = DeeBotSignalGenerator(self.executor)
        self.shorgan_generator = ShorganBotSignalGenerator(self.executor)
        
        # Signal log
        self.signal_log = Path("data/signal_log.json")
        self.signal_log.parent.mkdir(exist_ok=True)
    
    async def route_dee_bot_signals(self, analysis_results: Dict):
        """Route dee-bot analysis to signals
        
        Args:
            analysis_results: Dee-bot analysis results
        """
        recommendations = analysis_results.get('recommendations', [])
        await self.dee_generator.process_recommendations(recommendations)
        self._log_signals("dee-bot", recommendations)
    
    async def route_shorgan_bot_signals(self, analysis_results: Dict):
        """Route shorgan-bot analysis to signals
        
        Args:
            analysis_results: Shorgan-bot analysis results
        """
        recommendations = analysis_results.get('recommendations', [])
        await self.shorgan_generator.process_recommendations(recommendations)
        self._log_signals("shorgan-bot", recommendations)
    
    def _log_signals(self, bot_name: str, recommendations: List[Dict]):
        """Log signals to file
        
        Args:
            bot_name: Name of the bot
            recommendations: List of recommendations
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'bot': bot_name,
            'recommendations': recommendations,
            'count': len(recommendations)
        }
        
        # Append to log
        existing = []
        if self.signal_log.exists():
            with open(self.signal_log, 'r') as f:
                existing = json.load(f)
        
        existing.append(log_entry)
        
        # Keep last 1000 entries
        if len(existing) > 1000:
            existing = existing[-1000:]
        
        with open(self.signal_log, 'w') as f:
            json.dump(existing, f, indent=2, default=str)
    
    def get_status(self) -> Dict:
        """Get router and executor status"""
        return {
            'executor_status': self.executor.get_status(),
            'dee_bot_signals_today': self.dee_generator.signals_today,
            'shorgan_bot_signals_today': self.shorgan_generator.signals_today,
            'pending_signals': len(self.executor.signal_queue)
        }

async def test_signal_generation():
    """Test signal generation and routing"""
    
    # Initialize router in paper mode
    router = SignalRouter(ExecutionMode.PAPER)
    
    # Test dee-bot recommendations
    dee_bot_analysis = {
        'recommendations': [
            {
                'ticker': 'AAPL',
                'action': 'BUY',
                'confidence': 0.75,
                'current_price': 234.50,
                'stop_loss': 230.00,
                'take_profit': 245.00,
                'reason': 'Strong technical breakout with increasing volume',
                'risk_score': 0.3
            },
            {
                'ticker': 'TSLA',
                'action': 'SELL',
                'confidence': 0.68,
                'current_price': 890.00,
                'stop_loss': 920.00,
                'take_profit': 850.00,
                'reason': 'Overbought conditions with weakening momentum',
                'risk_score': 0.5
            }
        ]
    }
    
    # Test shorgan-bot recommendations
    shorgan_bot_analysis = {
        'recommendations': [
            {
                'ticker': 'NVDA',
                'action': 'BUY',
                'confidence': 0.82,
                'current_price': 520.00,
                'stop_loss': 505.00,
                'take_profit': 550.00,
                'reason': 'AI sector momentum with positive sentiment',
                'risk_score': 0.4
            }
        ]
    }
    
    # Route signals
    print("Routing dee-bot signals...")
    await router.route_dee_bot_signals(dee_bot_analysis)
    
    print("Routing shorgan-bot signals...")
    await router.route_shorgan_bot_signals(shorgan_bot_analysis)
    
    # Get status
    status = router.get_status()
    print(f"\nRouter Status:")
    print(f"  Dee-bot signals today: {status['dee_bot_signals_today']}")
    print(f"  Shorgan-bot signals today: {status['shorgan_bot_signals_today']}")
    print(f"  Pending signals: {status['pending_signals']}")
    print(f"  Portfolio value: ${status['executor_status']['portfolio_value']:,.2f}")

if __name__ == "__main__":
    # Test the signal generation
    asyncio.run(test_signal_generation())