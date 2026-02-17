"""
Advanced Position Sizing Module
Implements Kelly Criterion with risk constraints

This module provides sophisticated position sizing algorithms:
- Kelly Criterion (full and fractional)
- Volatility-adjusted sizing
- Risk parity weights
- Portfolio concentration limits
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SizingMethod(Enum):
    """Available position sizing methods"""
    FIXED_PERCENT = "fixed_percent"
    KELLY = "kelly"
    HALF_KELLY = "half_kelly"
    QUARTER_KELLY = "quarter_kelly"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    RISK_PARITY = "risk_parity"


@dataclass
class TradeStats:
    """Historical trade statistics for a strategy/symbol"""
    win_rate: float = 0.5
    avg_win_pct: float = 0.08  # 8% average win
    avg_loss_pct: float = 0.05  # 5% average loss
    sample_size: int = 0
    profit_factor: float = 1.0
    max_consecutive_losses: int = 3
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def win_loss_ratio(self) -> float:
        """Win/Loss ratio (reward to risk)"""
        if self.avg_loss_pct == 0:
            return 10.0  # Cap at 10:1
        return min(10.0, self.avg_win_pct / self.avg_loss_pct)
    
    @property
    def expectancy(self) -> float:
        """Expected value per trade"""
        return (self.win_rate * self.avg_win_pct) - ((1 - self.win_rate) * self.avg_loss_pct)


@dataclass
class PositionSizeResult:
    """Result of position sizing calculation"""
    shares: int
    dollar_amount: float
    percent_of_portfolio: float
    method_used: SizingMethod
    kelly_optimal: Optional[float] = None
    kelly_used: Optional[float] = None
    rationale: str = ""
    constraints_applied: List[str] = field(default_factory=list)
    stop_loss_price: Optional[float] = None
    risk_per_trade: Optional[float] = None


class AdvancedPositionSizer:
    """
    Advanced position sizing using Kelly Criterion and risk constraints
    
    Features:
    - Full Kelly, Half Kelly, Quarter Kelly options
    - Volatility-adjusted position sizing
    - Portfolio concentration limits
    - Risk parity weight calculation
    - Dynamic adjustment based on recent performance
    """
    
    def __init__(
        self,
        max_position_pct: float = 0.08,
        max_portfolio_risk: float = 0.15,
        kelly_fraction: float = 0.5,  # Half-Kelly by default
        min_win_rate: float = 0.45,
        min_sample_size: int = 20,
        target_daily_volatility: float = 0.02,  # 2% daily vol target
        max_correlation: float = 0.7,
        max_sector_exposure: float = 0.30
    ):
        """
        Initialize position sizer
        
        Args:
            max_position_pct: Maximum position size as % of portfolio
            max_portfolio_risk: Maximum total portfolio risk
            kelly_fraction: Fraction of Kelly to use (0.5 = half-Kelly)
            min_win_rate: Minimum win rate to size up
            min_sample_size: Minimum trades for full Kelly confidence
            target_daily_volatility: Target volatility contribution per position
            max_correlation: Maximum correlation allowed between positions
            max_sector_exposure: Maximum sector concentration
        """
        self.max_position_pct = max_position_pct
        self.max_portfolio_risk = max_portfolio_risk
        self.kelly_fraction = kelly_fraction
        self.min_win_rate = min_win_rate
        self.min_sample_size = min_sample_size
        self.target_daily_volatility = target_daily_volatility
        self.max_correlation = max_correlation
        self.max_sector_exposure = max_sector_exposure
        
        # Trade history for statistics
        self._trade_history: Dict[str, List[Dict]] = {}
        
    def calculate_position_size(
        self,
        ticker: str,
        current_price: float,
        portfolio_value: float,
        signal_confidence: float,
        volatility: float,
        trade_stats: Optional[TradeStats] = None,
        existing_positions: Optional[Dict[str, Dict]] = None,
        sector: Optional[str] = None,
        method: SizingMethod = SizingMethod.HALF_KELLY
    ) -> PositionSizeResult:
        """
        Calculate optimal position size using multiple methods and constraints
        
        Args:
            ticker: Stock symbol
            current_price: Current stock price
            portfolio_value: Total portfolio value
            signal_confidence: Confidence from agent consensus (0-1)
            volatility: Annualized volatility of the stock
            trade_stats: Historical trade statistics
            existing_positions: Current portfolio positions
            sector: Stock sector for concentration checks
            method: Sizing method to use
            
        Returns:
            PositionSizeResult with recommended sizing
        """
        constraints_applied = []
        
        # Use default stats if none provided
        if trade_stats is None:
            trade_stats = self._get_default_stats(signal_confidence)
        
        # 1. Calculate Kelly-optimal size
        kelly_optimal = self._calculate_kelly(trade_stats)
        constraints_applied.append(f"Kelly optimal: {kelly_optimal:.1%}")
        
        # 2. Apply Kelly fraction based on method
        if method == SizingMethod.KELLY:
            kelly_used = kelly_optimal
        elif method == SizingMethod.HALF_KELLY:
            kelly_used = kelly_optimal * 0.5
        elif method == SizingMethod.QUARTER_KELLY:
            kelly_used = kelly_optimal * 0.25
        else:
            kelly_used = kelly_optimal * self.kelly_fraction
        
        constraints_applied.append(f"{method.value} applied: {kelly_used:.1%}")
        
        # 3. Confidence adjustment
        confidence_adj = self._confidence_adjust(kelly_used, signal_confidence, trade_stats)
        if confidence_adj != kelly_used:
            constraints_applied.append(f"Confidence adjusted ({signal_confidence:.0%}): {confidence_adj:.1%}")
        
        # 4. Volatility adjustment
        vol_adjusted = self._volatility_adjust(confidence_adj, volatility)
        if vol_adjusted != confidence_adj:
            constraints_applied.append(f"Volatility adjusted ({volatility:.1%} vol): {vol_adjusted:.1%}")
        
        # 5. Apply position size cap
        capped = min(vol_adjusted, self.max_position_pct)
        if capped < vol_adjusted:
            constraints_applied.append(f"Position cap ({self.max_position_pct:.0%}): {capped:.1%}")
        
        # 6. Portfolio concentration check
        final_pct = self._check_concentration(
            capped, ticker, sector, existing_positions or {}
        )
        if final_pct != capped:
            constraints_applied.append(f"Concentration limit: {final_pct:.1%}")
        
        # 7. Calculate dollar amount and shares
        dollar_amount = portfolio_value * final_pct
        shares = int(dollar_amount / current_price) if current_price > 0 else 0
        
        # 8. Minimum position check
        if shares < 1:
            return PositionSizeResult(
                shares=0,
                dollar_amount=0,
                percent_of_portfolio=0,
                method_used=method,
                kelly_optimal=kelly_optimal,
                kelly_used=kelly_used,
                rationale="Position too small after constraints",
                constraints_applied=constraints_applied
            )
        
        # Actual percentage (after share rounding)
        actual_pct = (shares * current_price) / portfolio_value
        
        # Calculate stop loss and risk per trade
        stop_loss_pct = min(0.15, volatility * 2)  # 2x daily vol or 15% max
        stop_loss_price = current_price * (1 - stop_loss_pct)
        risk_per_trade = actual_pct * stop_loss_pct
        
        return PositionSizeResult(
            shares=shares,
            dollar_amount=shares * current_price,
            percent_of_portfolio=actual_pct,
            method_used=method,
            kelly_optimal=kelly_optimal,
            kelly_used=kelly_used,
            rationale=self._build_rationale(kelly_optimal, actual_pct, signal_confidence),
            constraints_applied=constraints_applied,
            stop_loss_price=stop_loss_price,
            risk_per_trade=risk_per_trade
        )
    
    def _calculate_kelly(self, stats: TradeStats) -> float:
        """
        Calculate Kelly Criterion position size
        
        Kelly % = (p × b - q) / b
        where:
            p = probability of winning
            b = win/loss ratio
            q = probability of losing (1 - p)
        """
        p = stats.win_rate
        q = 1 - p
        b = stats.win_loss_ratio
        
        # Kelly formula
        kelly = (p * b - q) / b if b > 0 else 0
        
        # Don't bet if negative expectancy
        if kelly <= 0:
            return 0.0
        
        # Reduce confidence for small sample sizes
        if stats.sample_size < self.min_sample_size:
            sample_factor = stats.sample_size / self.min_sample_size
            kelly = kelly * sample_factor
        
        # Cap at reasonable maximum (25%)
        kelly = min(0.25, kelly)
        
        return kelly
    
    def _confidence_adjust(
        self, 
        position_pct: float, 
        signal_confidence: float,
        stats: TradeStats
    ) -> float:
        """
        Adjust position size based on signal confidence
        
        Low confidence = reduce size
        High confidence = maintain or slightly increase
        """
        # Scale factor: 0.5 at 50% confidence, 1.0 at 80%+ confidence
        if signal_confidence >= 0.8:
            scale = 1.0
        elif signal_confidence >= 0.6:
            scale = 0.8 + (signal_confidence - 0.6) * 1.0  # 0.8 to 1.0
        else:
            scale = 0.5 + (signal_confidence - 0.3) * 1.0  # 0.5 to 0.8
        
        scale = max(0.3, min(1.0, scale))
        
        return position_pct * scale
    
    def _volatility_adjust(self, position_pct: float, volatility: float) -> float:
        """
        Adjust position size to target a consistent volatility contribution
        
        Higher volatility stocks get smaller positions
        Target: each position contributes ~2% daily volatility to portfolio
        """
        if volatility <= 0:
            return position_pct
        
        # Convert annual vol to daily
        daily_vol = volatility / np.sqrt(252)
        
        # Calculate max position for target vol contribution
        if daily_vol > 0:
            max_for_vol = self.target_daily_volatility / daily_vol
        else:
            max_for_vol = position_pct
        
        # Use the smaller of Kelly-derived and vol-adjusted
        return min(position_pct, max_for_vol)
    
    def _check_concentration(
        self, 
        position_pct: float, 
        ticker: str,
        sector: Optional[str],
        existing_positions: Dict[str, Dict]
    ) -> float:
        """
        Check and limit portfolio concentration
        
        - Single position limit
        - Sector concentration limit
        - Correlation limit (simplified)
        """
        # Check if we already have this position
        if ticker in existing_positions:
            existing_pct = existing_positions[ticker].get('percent', 0)
            max_additional = self.max_position_pct - existing_pct
            position_pct = min(position_pct, max_additional)
        
        # Check sector concentration
        if sector:
            sector_exposure = sum(
                pos.get('percent', 0) 
                for sym, pos in existing_positions.items()
                if pos.get('sector') == sector
            )
            max_sector_additional = self.max_sector_exposure - sector_exposure
            position_pct = min(position_pct, max(0, max_sector_additional))
        
        return max(0, position_pct)
    
    def _get_default_stats(self, confidence: float) -> TradeStats:
        """Generate default stats based on signal confidence"""
        # Use confidence as a proxy for win rate (with bounds)
        estimated_win_rate = 0.45 + (confidence - 0.5) * 0.3  # 45% to 75%
        estimated_win_rate = max(0.45, min(0.65, estimated_win_rate))
        
        return TradeStats(
            win_rate=estimated_win_rate,
            avg_win_pct=0.08,
            avg_loss_pct=0.05,
            sample_size=10,  # Low sample = conservative sizing
            profit_factor=estimated_win_rate * 0.08 / ((1 - estimated_win_rate) * 0.05)
        )
    
    def _build_rationale(
        self, 
        kelly_pct: float, 
        final_pct: float,
        confidence: float
    ) -> str:
        """Build human-readable rationale"""
        parts = []
        parts.append(f"Signal confidence: {confidence:.0%}")
        parts.append(f"Kelly optimal: {kelly_pct:.1%}")
        parts.append(f"Final size: {final_pct:.1%}")
        
        reduction = (kelly_pct - final_pct) / kelly_pct if kelly_pct > 0 else 0
        if reduction > 0.5:
            parts.append("(heavily constrained)")
        elif reduction > 0.2:
            parts.append("(moderately constrained)")
        
        return " | ".join(parts)
    
    def calculate_risk_parity_weights(
        self,
        tickers: List[str],
        volatilities: Dict[str, float],
        correlations: Optional[np.ndarray] = None,
        target_volatility: float = 0.10
    ) -> Dict[str, float]:
        """
        Calculate risk parity weights for portfolio rebalancing
        
        Each position contributes equal risk to the portfolio
        
        Args:
            tickers: List of stock symbols
            volatilities: Dict of ticker -> annualized volatility
            correlations: Correlation matrix (optional)
            target_volatility: Target portfolio volatility
            
        Returns:
            Dict of ticker -> weight
        """
        if not tickers or not volatilities:
            return {}
        
        # Simple inverse-volatility weighting (risk parity without correlations)
        inv_vols = {}
        for t in tickers:
            vol = volatilities.get(t, 0.30)  # Default 30% if missing
            if vol > 0:
                inv_vols[t] = 1.0 / vol
            else:
                inv_vols[t] = 0
        
        total = sum(inv_vols.values())
        
        if total == 0:
            # Equal weight if no volatility data
            return {t: 1.0 / len(tickers) for t in tickers}
        
        # Normalize weights
        weights = {t: v / total for t, v in inv_vols.items()}
        
        # Scale to target volatility (simplified)
        if correlations is not None and len(correlations) == len(tickers):
            # Full risk parity with correlations
            weights = self._optimize_risk_parity(
                np.array([volatilities.get(t, 0.30) for t in tickers]),
                correlations,
                target_volatility
            )
            return dict(zip(tickers, weights))
        
        return weights
    
    def _optimize_risk_parity(
        self,
        volatilities: np.ndarray,
        correlations: np.ndarray,
        target_vol: float
    ) -> np.ndarray:
        """
        Optimize for risk parity using iterative method
        
        This is a simplified implementation - production would use
        scipy.optimize or cvxpy
        """
        n = len(volatilities)
        weights = np.ones(n) / n  # Start with equal weights
        
        # Covariance matrix
        std_matrix = np.diag(volatilities)
        cov_matrix = std_matrix @ correlations @ std_matrix
        
        # Iterative adjustment (simplified Spinu algorithm)
        for _ in range(100):
            # Calculate marginal risk contributions
            portfolio_var = weights @ cov_matrix @ weights
            marginal_risk = cov_matrix @ weights
            risk_contrib = weights * marginal_risk / np.sqrt(portfolio_var)
            
            # Target: equal risk contribution
            target_contrib = np.sqrt(portfolio_var) / n
            
            # Adjust weights
            adjustment = target_contrib / (risk_contrib + 1e-10)
            weights = weights * adjustment
            weights = weights / weights.sum()  # Normalize
        
        return weights
    
    def update_trade_stats(
        self,
        ticker: str,
        entry_price: float,
        exit_price: float,
        is_win: bool
    ):
        """Update trade statistics with new trade result"""
        if ticker not in self._trade_history:
            self._trade_history[ticker] = []
        
        pct_change = (exit_price - entry_price) / entry_price
        
        self._trade_history[ticker].append({
            'entry': entry_price,
            'exit': exit_price,
            'pct_change': pct_change,
            'is_win': is_win,
            'timestamp': datetime.now()
        })
        
        # Keep last 100 trades
        self._trade_history[ticker] = self._trade_history[ticker][-100:]
    
    def get_trade_stats(self, ticker: str) -> Optional[TradeStats]:
        """Get trade statistics for a ticker"""
        history = self._trade_history.get(ticker, [])
        
        if len(history) < 5:
            return None
        
        wins = [t for t in history if t['is_win']]
        losses = [t for t in history if not t['is_win']]
        
        win_rate = len(wins) / len(history)
        avg_win = np.mean([t['pct_change'] for t in wins]) if wins else 0.05
        avg_loss = abs(np.mean([t['pct_change'] for t in losses])) if losses else 0.03
        
        return TradeStats(
            win_rate=win_rate,
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss,
            sample_size=len(history),
            profit_factor=(win_rate * avg_win) / ((1 - win_rate) * avg_loss + 0.001),
            last_updated=datetime.now()
        )


# Test function
def test_position_sizer():
    """Test the position sizer"""
    sizer = AdvancedPositionSizer(
        max_position_pct=0.08,
        kelly_fraction=0.5
    )
    
    print("=" * 60)
    print("Testing Advanced Position Sizer")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {"ticker": "AAPL", "price": 185.0, "confidence": 0.75, "volatility": 0.25},
        {"ticker": "NVDA", "price": 480.0, "confidence": 0.85, "volatility": 0.45},
        {"ticker": "T", "price": 17.0, "confidence": 0.60, "volatility": 0.18},
        {"ticker": "TSLA", "price": 240.0, "confidence": 0.50, "volatility": 0.55},
    ]
    
    portfolio_value = 100000
    
    for scenario in scenarios:
        result = sizer.calculate_position_size(
            ticker=scenario["ticker"],
            current_price=scenario["price"],
            portfolio_value=portfolio_value,
            signal_confidence=scenario["confidence"],
            volatility=scenario["volatility"]
        )
        
        print(f"\n{scenario['ticker']}:")
        print(f"  Price: ${scenario['price']:.2f}")
        print(f"  Confidence: {scenario['confidence']:.0%}")
        print(f"  Volatility: {scenario['volatility']:.0%}")
        print(f"  ---")
        print(f"  Kelly Optimal: {result.kelly_optimal:.1%}")
        print(f"  Final Size: {result.percent_of_portfolio:.1%}")
        print(f"  Shares: {result.shares}")
        print(f"  Dollar Amount: ${result.dollar_amount:,.0f}")
        print(f"  Stop Loss: ${result.stop_loss_price:.2f}")
        print(f"  Risk Per Trade: {result.risk_per_trade:.2%}")
        print(f"  Constraints: {len(result.constraints_applied)}")


if __name__ == "__main__":
    test_position_sizer()
