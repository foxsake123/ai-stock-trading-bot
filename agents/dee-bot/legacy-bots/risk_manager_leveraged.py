"""
Leveraged Trading Risk Management Module for DEE-BOT
Implements strict risk controls for 2X leverage beta-neutral strategy
"""

import alpaca_trade_api as tradeapi
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
from pathlib import Path

class LeveragedRiskManager:
    """Risk management for leveraged beta-neutral trading"""
    
    def __init__(self, api, leverage: float = 2.0):
        self.api = api
        self.leverage = leverage
        
        # Risk Parameters (more conservative for leverage)
        self.max_portfolio_risk = 0.10  # Max 10% portfolio risk
        self.max_position_risk = 0.02  # Max 2% risk per position
        self.max_daily_loss = 0.05  # Max 5% daily loss
        self.max_correlation = 0.7  # Max correlation between positions
        self.margin_buffer = 0.25  # Keep 25% margin buffer
        
        # Volatility thresholds
        self.max_vix = 30  # Don't trade if VIX > 30
        self.max_position_volatility = 0.4  # Max 40% annualized volatility
        
        # Leverage-specific controls
        self.max_leverage_ratio = 2.0
        self.deleverage_threshold = 0.03  # Deleverage if down 3%
        self.force_close_threshold = 0.07  # Force close all if down 7%
        
    def calculate_position_risk(self, symbol: str, shares: int, entry_price: float, stop_price: float) -> Dict:
        """Calculate risk metrics for a position"""
        position_value = shares * entry_price
        potential_loss = shares * (entry_price - stop_price)
        risk_percentage = potential_loss / position_value
        
        return {
            'symbol': symbol,
            'position_value': position_value,
            'potential_loss': potential_loss,
            'risk_percentage': risk_percentage,
            'leveraged_value': position_value * self.leverage,
            'leveraged_loss': potential_loss * self.leverage
        }
    
    def check_margin_requirements(self) -> Dict:
        """Check if margin requirements are met"""
        try:
            account = self.api.get_account()
            
            equity = float(account.equity)
            margin_used = float(account.initial_margin) if hasattr(account, 'initial_margin') else 0
            buying_power = float(account.buying_power)
            
            # Calculate margin utilization
            margin_available = equity - margin_used
            margin_utilization = margin_used / equity if equity > 0 else 0
            
            # Check if we have sufficient margin buffer
            has_buffer = margin_utilization < (1 - self.margin_buffer)
            
            return {
                'equity': equity,
                'margin_used': margin_used,
                'margin_available': margin_available,
                'margin_utilization': margin_utilization,
                'buying_power': buying_power,
                'has_sufficient_buffer': has_buffer,
                'can_use_leverage': has_buffer and margin_utilization < 0.5
            }
            
        except Exception as e:
            print(f"[ERROR] Margin check failed: {str(e)}")
            return {'can_use_leverage': False}
    
    def calculate_portfolio_var(self, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk for the portfolio"""
        try:
            positions = self.api.list_positions()
            if not positions:
                return 0.0
            
            # Simplified VaR calculation
            total_value = sum(float(p.market_value) for p in positions)
            
            # Assume 2% daily volatility for leveraged portfolio
            daily_volatility = 0.02 * self.leverage
            
            # Calculate VaR using normal distribution
            z_score = 1.645 if confidence_level == 0.95 else 2.326
            var = total_value * daily_volatility * z_score
            
            return var
            
        except Exception as e:
            print(f"[ERROR] VaR calculation failed: {str(e)}")
            return 0.0
    
    def check_correlation_risk(self, new_positions: List[str]) -> bool:
        """Check if new positions are too correlated"""
        # Simplified correlation check
        # In production, would calculate actual correlation matrix
        
        # High correlation groups
        tech_stocks = {'AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD'}
        financials = {'JPM', 'BAC', 'GS', 'MS', 'C', 'WFC'}
        
        # Check concentration in sectors
        tech_count = sum(1 for p in new_positions if p in tech_stocks)
        financial_count = sum(1 for p in new_positions if p in financials)
        
        # Don't allow more than 3 positions in same sector with leverage
        if tech_count > 3 or financial_count > 3:
            return False
            
        return True
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        if avg_loss == 0:
            return 0.0
            
        # Kelly formula: f = (p*b - q) / b
        # where p = win probability, q = loss probability, b = win/loss ratio
        b = avg_win / abs(avg_loss)
        q = 1 - win_rate
        
        kelly_percentage = (win_rate * b - q) / b
        
        # Apply Kelly fraction (use 25% of Kelly for safety with leverage)
        safe_kelly = kelly_percentage * 0.25
        
        # Cap at maximum position size
        return min(safe_kelly, self.max_position_risk)
    
    def monitor_drawdown(self) -> Dict:
        """Monitor current drawdown and trigger risk actions"""
        try:
            account = self.api.get_account()
            
            equity = float(account.equity)
            last_equity = float(account.last_equity) if hasattr(account, 'last_equity') else equity
            
            # Calculate daily P&L
            daily_pnl = equity - last_equity
            daily_return = daily_pnl / last_equity if last_equity > 0 else 0
            
            risk_actions = {
                'current_equity': equity,
                'daily_pnl': daily_pnl,
                'daily_return': daily_return,
                'action_required': 'NONE'
            }
            
            # Check risk thresholds
            if daily_return <= -self.force_close_threshold:
                risk_actions['action_required'] = 'FORCE_CLOSE_ALL'
                risk_actions['reason'] = f'Daily loss exceeded {self.force_close_threshold:.1%}'
                
            elif daily_return <= -self.deleverage_threshold:
                risk_actions['action_required'] = 'DELEVERAGE'
                risk_actions['reason'] = f'Daily loss exceeded {self.deleverage_threshold:.1%}'
                
            elif daily_return <= -self.max_position_risk:
                risk_actions['action_required'] = 'STOP_NEW_TRADES'
                risk_actions['reason'] = 'Daily loss approaching limit'
            
            return risk_actions
            
        except Exception as e:
            print(f"[ERROR] Drawdown monitoring failed: {str(e)}")
            return {'action_required': 'STOP_NEW_TRADES'}
    
    def set_dynamic_stops(self, symbol: str, entry_price: float, volatility: float) -> Tuple[float, float]:
        """Calculate dynamic stop loss and take profit based on volatility"""
        # Tighter stops for leveraged positions
        stop_multiplier = 1.5  # 1.5x daily volatility
        profit_multiplier = 2.5  # 2.5x daily volatility
        
        # Calculate stop and target
        stop_distance = entry_price * volatility * stop_multiplier / self.leverage
        profit_distance = entry_price * volatility * profit_multiplier
        
        stop_loss = entry_price - stop_distance
        take_profit = entry_price + profit_distance
        
        return round(stop_loss, 2), round(take_profit, 2)
    
    def validate_trade(self, symbol: str, shares: int, side: str) -> Dict:
        """Validate if a trade meets risk requirements"""
        validation = {
            'symbol': symbol,
            'shares': shares,
            'side': side,
            'approved': False,
            'reasons': []
        }
        
        # Check margin requirements
        margin_check = self.check_margin_requirements()
        if not margin_check.get('can_use_leverage', False):
            validation['reasons'].append('Insufficient margin for leverage')
            return validation
        
        # Check drawdown
        drawdown_check = self.monitor_drawdown()
        if drawdown_check['action_required'] != 'NONE':
            validation['reasons'].append(f"Risk action: {drawdown_check['action_required']}")
            return validation
        
        # Check position size
        try:
            barset = self.api.get_latest_bar(symbol)
            price = barset.c
            position_value = shares * price
            
            account = self.api.get_account()
            equity = float(account.equity)
            
            position_pct = position_value / equity
            
            if position_pct > self.max_position_risk * self.leverage:
                validation['reasons'].append(f'Position too large: {position_pct:.1%} of equity')
                return validation
                
        except Exception as e:
            validation['reasons'].append(f'Price check failed: {str(e)}')
            return validation
        
        # All checks passed
        validation['approved'] = True
        validation['reasons'].append('All risk checks passed')
        
        return validation
    
    def generate_risk_report(self) -> Dict:
        """Generate comprehensive risk report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'leverage_used': self.leverage,
            'risk_metrics': {},
            'warnings': [],
            'recommendations': []
        }
        
        # Get current positions
        positions = self.api.list_positions()
        
        if positions:
            # Calculate portfolio metrics
            total_value = sum(float(p.market_value) for p in positions)
            total_pnl = sum(float(p.unrealized_pl) for p in positions)
            
            report['risk_metrics']['total_exposure'] = total_value * self.leverage
            report['risk_metrics']['unrealized_pnl'] = total_pnl
            report['risk_metrics']['position_count'] = len(positions)
            
            # Calculate VaR
            var_95 = self.calculate_portfolio_var(0.95)
            report['risk_metrics']['var_95'] = var_95
            report['risk_metrics']['var_as_pct'] = var_95 / total_value if total_value > 0 else 0
            
            # Check margin
            margin_status = self.check_margin_requirements()
            report['risk_metrics']['margin_utilization'] = margin_status.get('margin_utilization', 0)
            
            # Add warnings
            if margin_status.get('margin_utilization', 0) > 0.7:
                report['warnings'].append('High margin utilization - consider reducing positions')
                
            if abs(total_pnl) > total_value * 0.05:
                report['warnings'].append('Significant unrealized P&L - consider taking profits/losses')
                
            # Recommendations
            if self.leverage > 1.5 and margin_status.get('margin_utilization', 0) > 0.5:
                report['recommendations'].append('Reduce leverage to improve margin safety')
                
        return report

def main():
    """Test risk management system"""
    # Connect to Alpaca
    API_KEY = "PK6FZK4DAQVTD7DYVH78"
    SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
    BASE_URL = "https://paper-api.alpaca.markets"
    
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    
    # Initialize risk manager
    risk_manager = LeveragedRiskManager(api, leverage=2.0)
    
    print("=" * 80)
    print("LEVERAGED TRADING RISK MANAGEMENT SYSTEM")
    print("=" * 80)
    
    # Check margin requirements
    print("\n--- MARGIN STATUS ---")
    margin_status = risk_manager.check_margin_requirements()
    print(f"Equity: ${margin_status.get('equity', 0):,.2f}")
    print(f"Margin Utilization: {margin_status.get('margin_utilization', 0):.1%}")
    print(f"Can Use Leverage: {margin_status.get('can_use_leverage', False)}")
    
    # Monitor drawdown
    print("\n--- DRAWDOWN MONITORING ---")
    drawdown = risk_manager.monitor_drawdown()
    print(f"Daily P&L: ${drawdown.get('daily_pnl', 0):,.2f}")
    print(f"Daily Return: {drawdown.get('daily_return', 0):.2%}")
    print(f"Action Required: {drawdown.get('action_required', 'NONE')}")
    
    # Generate risk report
    print("\n--- RISK REPORT ---")
    report = risk_manager.generate_risk_report()
    
    print(f"Total Exposure: ${report['risk_metrics'].get('total_exposure', 0):,.2f}")
    print(f"VaR (95%): ${report['risk_metrics'].get('var_95', 0):,.2f}")
    
    if report['warnings']:
        print("\nWarnings:")
        for warning in report['warnings']:
            print(f"  - {warning}")
            
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
    
    # Save report
    log_dir = Path("C:/Users/shorg/ai-stock-trading-bot/04_risk/reports")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = log_dir / f"leveraged_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nRisk report saved: {report_file}")

if __name__ == "__main__":
    main()