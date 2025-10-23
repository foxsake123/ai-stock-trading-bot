"""
Portfolio Performance Tracker for Shorgan-Bot
Tracks performance metrics and competitive positioning
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import logging

class PortfolioPerformanceTracker:
    """
    Tracks portfolio performance and competitive metrics
    Designed for shorgan-bot vs dee-bot competition
    """
    
    def __init__(self, initial_capital: float = 100000):
        self.logger = logging.getLogger("portfolio.performance")
        
        # Portfolio initialization
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.closed_trades = []
        self.daily_returns = []
        
        # Competition tracking
        self.competitor_performance = {}
        self.performance_history = []
        
        # Risk metrics
        self.max_drawdown = 0
        self.daily_loss_limit = 0.05  # 5% daily loss limit
        self.position_limit = 0.20     # 20% max per position
        
        # Performance targets
        self.target_return = 0.20      # 20% monthly target
        self.target_sharpe = 2.0        # Target Sharpe ratio
    
    def update_position(self, ticker: str, quantity: int, price: float, 
                       action: str, order_type: str = "market") -> Dict[str, Any]:
        """
        Update position in portfolio
        
        Args:
            ticker: Stock symbol
            quantity: Number of shares
            price: Execution price
            action: 'buy' or 'sell'
            order_type: Type of order
            
        Returns:
            Position update confirmation
        """
        timestamp = datetime.now()
        
        if action.lower() == 'buy':
            # Add to position
            if ticker not in self.positions:
                self.positions[ticker] = {
                    'quantity': 0,
                    'avg_price': 0,
                    'total_cost': 0,
                    'entry_time': timestamp
                }
            
            total_cost = self.positions[ticker]['total_cost'] + (quantity * price)
            total_quantity = self.positions[ticker]['quantity'] + quantity
            
            self.positions[ticker].update({
                'quantity': total_quantity,
                'avg_price': total_cost / total_quantity,
                'total_cost': total_cost,
                'last_update': timestamp
            })
            
            self.current_capital -= (quantity * price)
            
        elif action.lower() == 'sell':
            if ticker not in self.positions:
                self.logger.error(f"Attempting to sell {ticker} without position")
                return {'error': 'No position to sell'}
            
            # Calculate P&L
            avg_cost = self.positions[ticker]['avg_price']
            pnl = (price - avg_cost) * quantity
            pnl_percent = (price - avg_cost) / avg_cost
            
            # Update or close position
            remaining = self.positions[ticker]['quantity'] - quantity
            if remaining <= 0:
                # Close position
                hold_time = (timestamp - self.positions[ticker]['entry_time']).days
                
                self.closed_trades.append({
                    'ticker': ticker,
                    'entry_price': avg_cost,
                    'exit_price': price,
                    'quantity': quantity,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'hold_days': hold_time,
                    'exit_time': timestamp
                })
                
                del self.positions[ticker]
            else:
                # Partial sell
                self.positions[ticker]['quantity'] = remaining
                self.positions[ticker]['total_cost'] = remaining * avg_cost
            
            self.current_capital += (quantity * price)
        
        return {
            'ticker': ticker,
            'action': action,
            'quantity': quantity,
            'price': price,
            'timestamp': timestamp.isoformat(),
            'capital_remaining': self.current_capital
        }
    
    def calculate_portfolio_metrics(self) -> Dict[str, float]:
        """
        Calculate comprehensive portfolio metrics
        
        Returns:
            Dict of performance metrics
        """
        # Calculate total portfolio value
        portfolio_value = self.current_capital
        for ticker, position in self.positions.items():
            # Would need current market price here
            market_value = position['quantity'] * position['avg_price']  # Simplified
            portfolio_value += market_value
        
        # Basic metrics
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital
        
        # Win rate
        winning_trades = [t for t in self.closed_trades if t['pnl'] > 0]
        win_rate = len(winning_trades) / len(self.closed_trades) if self.closed_trades else 0
        
        # Average win/loss
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        losing_trades = [t for t in self.closed_trades if t['pnl'] <= 0]
        avg_loss = np.mean([abs(t['pnl']) for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        total_wins = sum([t['pnl'] for t in winning_trades]) if winning_trades else 0
        total_losses = sum([abs(t['pnl']) for t in losing_trades]) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Calculate Sharpe ratio (simplified)
        if self.daily_returns:
            returns_array = np.array(self.daily_returns)
            sharpe = (np.mean(returns_array) * 252) / (np.std(returns_array) * np.sqrt(252)) if np.std(returns_array) > 0 else 0
        else:
            sharpe = 0
        
        # Max drawdown calculation
        self._calculate_max_drawdown()
        
        return {
            'portfolio_value': portfolio_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe,
            'max_drawdown': self.max_drawdown,
            'trades_count': len(self.closed_trades),
            'open_positions': len(self.positions)
        }
    
    def compare_with_competitor(self, competitor_name: str, competitor_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Compare performance with competitor (dee-bot)
        
        Args:
            competitor_name: Name of competitor
            competitor_metrics: Competitor's performance metrics
            
        Returns:
            Comparison analysis
        """
        our_metrics = self.calculate_portfolio_metrics()
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'our_performance': our_metrics,
            'competitor_performance': competitor_metrics,
            'advantages': [],
            'disadvantages': [],
            'overall_position': 'WINNING' if our_metrics['total_return'] > competitor_metrics.get('total_return', 0) else 'LOSING'
        }
        
        # Detailed comparison
        metrics_to_compare = [
            ('total_return', 'Total Return', True),  # Higher is better
            ('sharpe_ratio', 'Sharpe Ratio', True),
            ('win_rate', 'Win Rate', True),
            ('profit_factor', 'Profit Factor', True),
            ('max_drawdown', 'Max Drawdown', False)  # Lower is better
        ]
        
        for metric, name, higher_better in metrics_to_compare:
            our_value = our_metrics.get(metric, 0)
            their_value = competitor_metrics.get(metric, 0)
            
            if higher_better:
                if our_value > their_value:
                    comparison['advantages'].append(f"Better {name}: {our_value:.2f} vs {their_value:.2f}")
                else:
                    comparison['disadvantages'].append(f"Worse {name}: {our_value:.2f} vs {their_value:.2f}")
            else:
                if our_value < their_value:
                    comparison['advantages'].append(f"Better {name}: {our_value:.2f} vs {their_value:.2f}")
                else:
                    comparison['disadvantages'].append(f"Worse {name}: {our_value:.2f} vs {their_value:.2f}")
        
        # Calculate lead/deficit
        return_diff = our_metrics['total_return'] - competitor_metrics.get('total_return', 0)
        comparison['return_difference'] = return_diff
        comparison['return_difference_pct'] = return_diff * 100
        
        # Store for tracking
        self.competitor_performance[competitor_name] = competitor_metrics
        self.performance_history.append(comparison)
        
        return comparison
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """
        Generate daily performance report
        
        Returns:
            Daily performance summary
        """
        metrics = self.calculate_portfolio_metrics()
        
        # Today's trades
        today = datetime.now().date()
        todays_trades = [
            t for t in self.closed_trades 
            if t['exit_time'].date() == today
        ]
        
        # Calculate daily P&L
        daily_pnl = sum([t['pnl'] for t in todays_trades])
        daily_return = daily_pnl / self.initial_capital if self.initial_capital > 0 else 0
        
        report = {
            'date': today.isoformat(),
            'portfolio_metrics': metrics,
            'daily_statistics': {
                'trades_executed': len(todays_trades),
                'daily_pnl': daily_pnl,
                'daily_return': daily_return,
                'daily_return_pct': daily_return * 100
            },
            'open_positions': self.positions,
            'top_performers': self._get_top_performers(),
            'worst_performers': self._get_worst_performers(),
            'risk_status': self._check_risk_status()
        }
        
        return report
    
    def _calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown
        
        Returns:
            Max drawdown percentage
        """
        if not self.performance_history:
            return 0
        
        # Calculate running maximum
        values = [self.initial_capital]
        for trade in self.closed_trades:
            values.append(values[-1] + trade['pnl'])
        
        if len(values) < 2:
            return 0
        
        running_max = np.maximum.accumulate(values)
        drawdown = (values - running_max) / running_max
        self.max_drawdown = abs(np.min(drawdown))
        
        return self.max_drawdown
    
    def _get_top_performers(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get top performing trades"""
        if not self.closed_trades:
            return []
        
        sorted_trades = sorted(self.closed_trades, key=lambda x: x['pnl_percent'], reverse=True)
        return sorted_trades[:n]
    
    def _get_worst_performers(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get worst performing trades"""
        if not self.closed_trades:
            return []
        
        sorted_trades = sorted(self.closed_trades, key=lambda x: x['pnl_percent'])
        return sorted_trades[:n]
    
    def _check_risk_status(self) -> Dict[str, Any]:
        """
        Check current risk status and limits
        
        Returns:
            Risk status assessment
        """
        metrics = self.calculate_portfolio_metrics()
        
        # Check daily loss limit
        today = datetime.now().date()
        todays_trades = [
            t for t in self.closed_trades 
            if t['exit_time'].date() == today
        ]
        daily_pnl = sum([t['pnl'] for t in todays_trades])
        daily_return = daily_pnl / self.initial_capital if self.initial_capital > 0 else 0
        
        risk_status = {
            'daily_loss_limit_reached': daily_return <= -self.daily_loss_limit,
            'position_concentration_ok': all(
                pos['total_cost'] / self.initial_capital <= self.position_limit 
                for pos in self.positions.values()
            ),
            'drawdown_acceptable': self.max_drawdown < 0.15,  # 15% max drawdown threshold
            'overall_risk': 'LOW'
        }
        
        # Determine overall risk level
        if risk_status['daily_loss_limit_reached']:
            risk_status['overall_risk'] = 'CRITICAL'
        elif not risk_status['position_concentration_ok'] or not risk_status['drawdown_acceptable']:
            risk_status['overall_risk'] = 'HIGH'
        elif self.max_drawdown > 0.10:
            risk_status['overall_risk'] = 'MEDIUM'
        
        return risk_status
    
    def save_performance_history(self, filepath: str) -> None:
        """Save performance history to file"""
        data = {
            'initial_capital': self.initial_capital,
            'current_metrics': self.calculate_portfolio_metrics(),
            'closed_trades': self.closed_trades,
            'performance_history': self.performance_history,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_performance_history(self, filepath: str) -> None:
        """Load performance history from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.initial_capital = data.get('initial_capital', 100000)
        self.closed_trades = data.get('closed_trades', [])
        self.performance_history = data.get('performance_history', [])