"""
Earnings Calendar Scanner
Tracks and analyzes upcoming earnings announcements
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict


@dataclass
class EarningsEvent:
    """Earnings event data structure"""
    ticker: str
    company_name: str
    earnings_date: datetime
    earnings_time: str  # BMO (before market open) or AMC (after market close)
    consensus_eps: float
    whisper_eps: Optional[float]
    prior_eps: float
    historical_beat_rate: float
    average_move: float
    implied_move: float
    iv_rank: float
    market_cap: float
    confidence_score: float
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['earnings_date'] = self.earnings_date.isoformat()
        return result


class EarningsScanner:
    """
    Scans for upcoming earnings announcements and analyzes historical performance
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Filters
        self.min_market_cap = self.config.get('min_market_cap', 1e9)
        self.max_market_cap = self.config.get('max_market_cap', 500e9)
        self.min_avg_volume = self.config.get('min_avg_volume', 500000)
        self.min_historical_move = self.config.get('min_historical_move', 0.05)
        
        # Data cache
        self.earnings_cache = {}
        self.historical_data = {}
        
    async def scan_upcoming_earnings(self, 
                                    days_ahead: int = 30,
                                    min_historical_move: float = 0.05,
                                    min_beat_rate: float = 0.60) -> List[Dict]:
        """
        Scan for upcoming earnings with high potential
        
        Args:
            days_ahead: Number of days to look ahead
            min_historical_move: Minimum average historical earnings move
            min_beat_rate: Minimum historical beat rate
        
        Returns:
            List of earnings opportunities
        """
        self.logger.info(f"Scanning earnings for next {days_ahead} days")
        
        # Fetch earnings calendar
        earnings_events = await self._fetch_earnings_calendar(days_ahead)
        
        # Filter and analyze
        opportunities = []
        
        for event in earnings_events:
            # Apply filters
            if event.market_cap < self.min_market_cap or event.market_cap > self.max_market_cap:
                continue
            
            if event.average_move < min_historical_move:
                continue
            
            if event.historical_beat_rate < min_beat_rate:
                continue
            
            # Calculate opportunity score
            score = self._calculate_earnings_score(event)
            
            # Create opportunity dict
            opportunity = {
                'ticker': event.ticker,
                'company_name': event.company_name,
                'catalyst_type': 'earnings',
                'catalyst_date': event.earnings_date.isoformat(),
                'earnings_time': event.earnings_time,
                'days_to_catalyst': (event.earnings_date - datetime.now()).days,
                'market_cap': event.market_cap,
                'confidence_score': score,
                'expected_move': event.implied_move,
                'risk_level': self._assess_earnings_risk(event),
                'supporting_data': {
                    'consensus_eps': event.consensus_eps,
                    'whisper_eps': event.whisper_eps,
                    'prior_eps': event.prior_eps,
                    'beat_rate': event.historical_beat_rate,
                    'avg_move': event.average_move,
                    'implied_move': event.implied_move,
                    'iv_rank': event.iv_rank
                },
                'trade_setup': self._generate_trade_setup(event),
                'historical_analysis': await self._analyze_historical_earnings(event.ticker)
            }
            
            opportunities.append(opportunity)
        
        # Sort by score
        opportunities.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        self.logger.info(f"Found {len(opportunities)} earnings opportunities")
        
        return opportunities
    
    async def _fetch_earnings_calendar(self, days_ahead: int) -> List[EarningsEvent]:
        """
        Fetch earnings calendar data
        In production, this would connect to financial data APIs
        """
        # For demonstration, return mock data
        # In production, use APIs like Alpha Vantage, Yahoo Finance, or Earnings Whispers
        
        mock_events = [
            EarningsEvent(
                ticker="AAPL",
                company_name="Apple Inc",
                earnings_date=datetime.now() + timedelta(days=7),
                earnings_time="AMC",
                consensus_eps=1.50,
                whisper_eps=1.55,
                prior_eps=1.46,
                historical_beat_rate=0.80,
                average_move=0.06,
                implied_move=0.05,
                iv_rank=0.65,
                market_cap=3e12,
                confidence_score=0.75
            ),
            EarningsEvent(
                ticker="NVDA",
                company_name="NVIDIA Corp",
                earnings_date=datetime.now() + timedelta(days=14),
                earnings_time="AMC",
                consensus_eps=0.75,
                whisper_eps=0.78,
                prior_eps=0.68,
                historical_beat_rate=0.85,
                average_move=0.08,
                implied_move=0.07,
                iv_rank=0.72,
                market_cap=1.5e12,
                confidence_score=0.80
            ),
            EarningsEvent(
                ticker="TSLA",
                company_name="Tesla Inc",
                earnings_date=datetime.now() + timedelta(days=21),
                earnings_time="AMC",
                consensus_eps=0.85,
                whisper_eps=0.87,
                prior_eps=0.76,
                historical_beat_rate=0.70,
                average_move=0.09,
                implied_move=0.08,
                iv_rank=0.78,
                market_cap=800e9,
                confidence_score=0.72
            )
        ]
        
        return mock_events
    
    def _calculate_earnings_score(self, event: EarningsEvent) -> float:
        """
        Calculate confidence score for earnings play
        """
        score = 0.5  # Base score
        
        # Historical beat rate factor
        if event.historical_beat_rate > 0.80:
            score += 0.15
        elif event.historical_beat_rate > 0.70:
            score += 0.10
        elif event.historical_beat_rate > 0.60:
            score += 0.05
        
        # Whisper vs consensus factor
        if event.whisper_eps and event.whisper_eps > event.consensus_eps:
            whisper_delta = (event.whisper_eps - event.consensus_eps) / event.consensus_eps
            score += min(whisper_delta * 0.5, 0.10)  # Cap at 0.10
        
        # IV rank factor (prefer moderate IV)
        if 0.30 < event.iv_rank < 0.70:
            score += 0.10
        elif event.iv_rank > 0.85:
            score -= 0.05  # Very high IV is risky
        
        # Historical move vs implied move
        if event.average_move > event.implied_move * 1.2:
            score += 0.10  # Historical moves exceed current expectations
        
        # Market cap factor (prefer liquid names)
        if event.market_cap > 100e9:
            score += 0.05
        
        return min(score, 1.0)
    
    def _assess_earnings_risk(self, event: EarningsEvent) -> str:
        """
        Assess risk level of earnings play
        """
        # High IV = High risk
        if event.iv_rank > 0.80:
            return "HIGH"
        
        # Low beat rate = Higher risk
        if event.historical_beat_rate < 0.60:
            return "HIGH"
        
        # Very high expected move = Higher risk
        if event.implied_move > 0.10:
            return "HIGH"
        
        # Moderate conditions
        if event.iv_rank > 0.50 or event.implied_move > 0.06:
            return "MEDIUM"
        
        return "LOW"
    
    def _generate_trade_setup(self, event: EarningsEvent) -> Dict[str, Any]:
        """
        Generate specific trade setup for earnings play
        """
        setup = {
            'entry_timing': '',
            'position_type': '',
            'options_strategy': '',
            'risk_management': '',
            'profit_targets': []
        }
        
        # Entry timing based on earnings time
        if event.earnings_time == "BMO":
            setup['entry_timing'] = "Enter day before close"
        else:
            setup['entry_timing'] = "Enter 2-3 days before, or day of before close"
        
        # Position type based on IV
        if event.iv_rank > 0.75:
            setup['position_type'] = "Options - sell premium"
            setup['options_strategy'] = "Iron Condor or Short Straddle (if neutral)"
        elif event.iv_rank > 0.50:
            setup['position_type'] = "Options - spreads"
            setup['options_strategy'] = "Call/Put Debit Spreads"
        else:
            setup['position_type'] = "Options - long"
            setup['options_strategy'] = "ATM Straddle or directional calls/puts"
        
        # Risk management
        setup['risk_management'] = f"Position size: {self._calculate_position_size(event)}% of portfolio"
        
        # Profit targets based on historical move
        setup['profit_targets'] = [
            f"Target 1: {event.average_move * 0.5:.1%} (50% of avg move)",
            f"Target 2: {event.average_move:.1%} (full avg move)",
            f"Target 3: {event.average_move * 1.5:.1%} (1.5x avg move)"
        ]
        
        return setup
    
    def _calculate_position_size(self, event: EarningsEvent) -> float:
        """
        Calculate appropriate position size based on risk
        """
        risk_level = self._assess_earnings_risk(event)
        
        if risk_level == "HIGH":
            return 1.0  # 1% of portfolio
        elif risk_level == "MEDIUM":
            return 2.0  # 2% of portfolio
        else:
            return 3.0  # 3% of portfolio
    
    async def _analyze_historical_earnings(self, ticker: str) -> Dict[str, Any]:
        """
        Analyze historical earnings performance
        """
        # In production, fetch actual historical data
        # For now, return mock analysis
        
        return {
            'last_4_quarters': {
                'beats': 3,
                'misses': 1,
                'avg_surprise': 0.05,
                'avg_move': 0.065
            },
            'last_8_quarters': {
                'beats': 6,
                'misses': 2,
                'avg_surprise': 0.04,
                'avg_move': 0.072
            },
            'best_move': {
                'date': '2024-07-25',
                'move': 0.12,
                'surprise': 0.08
            },
            'worst_move': {
                'date': '2024-01-25',
                'move': -0.08,
                'surprise': -0.03
            },
            'seasonality': {
                'Q1_avg': 0.05,
                'Q2_avg': 0.07,
                'Q3_avg': 0.06,
                'Q4_avg': 0.08
            }
        }
    
    async def get_earnings_today(self) -> List[Dict]:
        """
        Get earnings reporting today
        """
        today_events = await self._fetch_earnings_calendar(days_ahead=1)
        
        # Filter for today only
        today = datetime.now().date()
        today_earnings = [
            event for event in today_events 
            if event.earnings_date.date() == today
        ]
        
        opportunities = []
        for event in today_earnings:
            opportunities.append({
                'ticker': event.ticker,
                'company_name': event.company_name,
                'earnings_time': event.earnings_time,
                'consensus_eps': event.consensus_eps,
                'whisper_eps': event.whisper_eps,
                'implied_move': event.implied_move,
                'action': self._get_earnings_action(event)
            })
        
        return opportunities
    
    def _get_earnings_action(self, event: EarningsEvent) -> str:
        """
        Determine action for earnings play
        """
        score = self._calculate_earnings_score(event)
        
        if score > 0.75:
            return "PLAY"
        elif score > 0.60:
            return "CONSIDER"
        else:
            return "AVOID"
    
    async def track_earnings_results(self, ticker: str, 
                                    actual_eps: float,
                                    actual_move: float) -> Dict:
        """
        Track actual earnings results for performance analysis
        """
        # Store results for future analysis
        if ticker not in self.historical_data:
            self.historical_data[ticker] = []
        
        self.historical_data[ticker].append({
            'date': datetime.now().isoformat(),
            'actual_eps': actual_eps,
            'actual_move': actual_move,
            'timestamp': datetime.now().isoformat()
        })
        
        # Calculate performance metrics
        return {
            'ticker': ticker,
            'result': 'beat' if actual_move > 0 else 'miss',
            'move': actual_move,
            'eps': actual_eps,
            'tracked': True
        }
    
    def get_earnings_calendar_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary of upcoming earnings
        """
        # Group by date
        calendar = {}
        
        # In production, fetch real data
        # For demonstration, return structured summary
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            calendar[date] = {
                'BMO': [],  # Before market open
                'AMC': []   # After market close
            }
        
        return {
            'calendar': calendar,
            'total_events': 0,
            'high_impact': [],
            'most_anticipated': []
        }