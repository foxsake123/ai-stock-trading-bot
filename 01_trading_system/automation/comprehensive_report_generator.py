"""
Comprehensive Report Generator
Produces detailed reports with ALL positions, complete P&L analysis,
trade history, market commentary, catalyst tracking, and more
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging
import requests
import yfinance as yf
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Configure logging
log_dir = '09_logs/reports'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/comprehensive_report_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class ComprehensiveReportGenerator:
    """Generates detailed trading reports with complete analysis"""
    
    def __init__(self, report_type='daily'):
        """
        Initialize report generator
        
        Args:
            report_type: 'daily', 'weekly', or 'monthly'
        """
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        self.report_type = report_type
        self.report_dir = f'07_docs/{report_type}_comprehensive_reports'
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Data directories
        self.portfolio_csv = '02_data/portfolio/positions/shorgan_bot_positions.csv'
        self.trades_dir = '08_trading_logs/trades'
        self.research_dir = '02_data/research/reports/pre_market_daily'
        self.catalyst_file = '02_data/research/catalysts/active_catalysts.json'
        
        # Initialize data storage
        self.data = {
            'timestamp': datetime.now(),
            'account': {},
            'positions': [],
            'trades': [],
            'orders': [],
            'pnl': {},
            'performance': {},
            'catalysts': [],
            'commentary': {},
            'risk_metrics': {},
            'market_analysis': {}
        }
    
    def get_all_positions(self) -> List[Dict]:
        """Get ALL positions with complete details"""
        try:
            positions = self.api.list_positions()
            all_positions = []
            
            for pos in positions:
                # Get additional market data
                ticker = yf.Ticker(pos.symbol)
                info = ticker.info
                
                # Get recent price history for technical indicators
                hist = ticker.history(period="1mo")
                
                # Calculate technical indicators
                sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
                rsi = self._calculate_rsi(hist['Close']) if len(hist) >= 14 else None
                
                position_data = {
                    # Basic position data
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'side': pos.side,
                    
                    # Pricing
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price or 0),
                    'last_price': float(pos.lastday_price or 0),
                    
                    # Values
                    'market_value': float(pos.market_value or 0),
                    'cost_basis': float(pos.cost_basis or 0),
                    
                    # P&L
                    'unrealized_pnl': float(pos.unrealized_pl or 0),
                    'unrealized_pnl_pct': float(pos.unrealized_plpc or 0) * 100,
                    'change_today': float(pos.change_today or 0),
                    'change_today_pct': float(getattr(pos, 'change_today_pct', 0) or 0) * 100,
                    
                    # Market data
                    'market_cap': info.get('marketCap', 0),
                    'volume': info.get('volume', 0),
                    'avg_volume': info.get('averageVolume', 0),
                    'pe_ratio': info.get('trailingPE', None),
                    'beta': info.get('beta', None),
                    '52w_high': info.get('fiftyTwoWeekHigh', None),
                    '52w_low': info.get('fiftyTwoWeekLow', None),
                    
                    # Technical indicators
                    'sma_20': sma_20,
                    'rsi': rsi,
                    'above_sma20': (float(pos.current_price) > sma_20) if sma_20 else None,
                    
                    # Position metrics
                    'portfolio_weight': 0,  # Will calculate after
                    'days_held': 0,  # Will calculate from trade history
                    'risk_score': 0,  # Will calculate
                    
                    # Catalyst/News
                    'catalyst': '',  # Will populate from catalyst tracking
                    'last_news': '',  # Will populate from news
                }
                
                all_positions.append(position_data)
            
            # Calculate portfolio weights
            total_value = sum(p['market_value'] for p in all_positions)
            for pos in all_positions:
                pos['portfolio_weight'] = (pos['market_value'] / total_value * 100) if total_value > 0 else 0
            
            return all_positions
            
        except Exception as e:
            logging.error(f"Error fetching positions: {e}")
            return []
    
    def get_complete_trade_history(self, days=30) -> List[Dict]:
        """Get complete trade history with entry/exit pairs"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get all orders
            orders = self.api.list_orders(
                status='all',
                after=f"{start_date}T00:00:00Z",
                direction='asc',
                limit=500
            )
            
            # Process into trade pairs
            trades = []
            trade_pairs = {}  # Track entry/exit pairs
            
            for order in orders:
                if order.status != 'filled':
                    continue
                
                trade_data = {
                    'order_id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': int(order.filled_qty or 0),
                    'price': float(order.filled_avg_price or 0),
                    'value': float(order.filled_qty or 0) * float(order.filled_avg_price or 0),
                    'time': order.filled_at,
                    'order_type': order.order_type,
                    'time_in_force': order.time_in_force,
                    
                    # P&L tracking
                    'realized_pnl': 0,
                    'realized_pnl_pct': 0,
                    'exit_price': None,
                    'exit_time': None,
                    'holding_period': None,
                    'trade_result': 'OPEN',  # OPEN, WIN, LOSS
                }
                
                # Track entry/exit pairs for P&L calculation
                if order.side == 'buy':
                    # This is an entry
                    if order.symbol not in trade_pairs:
                        trade_pairs[order.symbol] = []
                    trade_pairs[order.symbol].append({
                        'entry': trade_data,
                        'exit': None
                    })
                else:  # sell
                    # This is an exit - match with entry
                    if order.symbol in trade_pairs:
                        for pair in trade_pairs[order.symbol]:
                            if pair['exit'] is None:
                                pair['exit'] = trade_data
                                # Calculate P&L
                                entry = pair['entry']
                                exit_value = trade_data['price'] * min(entry['quantity'], trade_data['quantity'])
                                entry_value = entry['price'] * min(entry['quantity'], trade_data['quantity'])
                                
                                realized_pnl = exit_value - entry_value
                                realized_pnl_pct = ((exit_value - entry_value) / entry_value * 100) if entry_value > 0 else 0
                                
                                # Update both trades
                                entry['realized_pnl'] = realized_pnl
                                entry['realized_pnl_pct'] = realized_pnl_pct
                                entry['exit_price'] = trade_data['price']
                                entry['exit_time'] = trade_data['time']
                                entry['holding_period'] = (trade_data['time'] - entry['time']).days if entry['time'] and trade_data['time'] else None
                                entry['trade_result'] = 'WIN' if realized_pnl > 0 else 'LOSS'
                                
                                trade_data['realized_pnl'] = realized_pnl
                                trade_data['realized_pnl_pct'] = realized_pnl_pct
                                trade_data['entry_price'] = entry['price']
                                trade_data['entry_time'] = entry['time']
                                trade_data['trade_result'] = 'WIN' if realized_pnl > 0 else 'LOSS'
                                break
                
                trades.append(trade_data)
            
            return trades
            
        except Exception as e:
            logging.error(f"Error fetching trade history: {e}")
            return []
    
    def calculate_detailed_pnl(self, positions, trades) -> Dict:
        """Calculate comprehensive P&L metrics"""
        
        # Realized P&L from closed trades
        closed_trades = [t for t in trades if t['trade_result'] in ['WIN', 'LOSS']]
        realized_pnl = sum(t['realized_pnl'] for t in closed_trades)
        
        # Unrealized P&L from open positions
        unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)
        
        # Daily P&L
        daily_pnl = sum(p['change_today'] for p in positions)
        
        # Win/Loss statistics
        winning_trades = [t for t in closed_trades if t['trade_result'] == 'WIN']
        losing_trades = [t for t in closed_trades if t['trade_result'] == 'LOSS']
        
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
        
        avg_win = (sum(t['realized_pnl'] for t in winning_trades) / len(winning_trades)) if winning_trades else 0
        avg_loss = (sum(t['realized_pnl'] for t in losing_trades) / len(losing_trades)) if losing_trades else 0
        
        profit_factor = abs(sum(t['realized_pnl'] for t in winning_trades) / sum(t['realized_pnl'] for t in losing_trades)) if losing_trades and sum(t['realized_pnl'] for t in losing_trades) != 0 else 0
        
        # Largest wins/losses
        largest_win = max((t['realized_pnl'] for t in winning_trades), default=0)
        largest_loss = min((t['realized_pnl'] for t in losing_trades), default=0)
        
        # Average holding period
        holding_periods = [t['holding_period'] for t in closed_trades if t.get('holding_period')]
        avg_holding_period = sum(holding_periods) / len(holding_periods) if holding_periods else 0
        
        return {
            # Core P&L
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': realized_pnl + unrealized_pnl,
            'daily_pnl': daily_pnl,
            
            # Trade statistics
            'total_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'open_positions': len(positions),
            
            # Performance metrics
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'avg_holding_period': avg_holding_period,
            
            # Risk/Reward
            'risk_reward_ratio': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            'expectancy': (win_rate/100 * avg_win) - ((100-win_rate)/100 * abs(avg_loss)),
            
            # Streaks
            'current_streak': self._calculate_streak(closed_trades),
            'max_win_streak': self._calculate_max_streak(closed_trades, 'WIN'),
            'max_loss_streak': self._calculate_max_streak(closed_trades, 'LOSS'),
        }
    
    def get_catalysts_and_news(self, symbols) -> Dict:
        """Get active catalysts and recent news for positions"""
        catalysts = {}
        
        try:
            # Load saved catalysts
            if os.path.exists(self.catalyst_file):
                with open(self.catalyst_file, 'r') as f:
                    saved_catalysts = json.load(f)
                    catalysts.update(saved_catalysts)
            
            # Get recent news for each symbol
            for symbol in symbols:
                if symbol not in catalysts:
                    catalysts[symbol] = {
                        'catalyst': '',
                        'catalyst_date': '',
                        'news': [],
                        'upcoming_events': []
                    }
                
                # Get news from yfinance
                try:
                    ticker = yf.Ticker(symbol)
                    news = ticker.news[:3] if hasattr(ticker, 'news') else []
                    
                    catalysts[symbol]['news'] = [
                        {
                            'title': item.get('title', ''),
                            'publisher': item.get('publisher', ''),
                            'link': item.get('link', ''),
                            'time': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
                        }
                        for item in news
                    ]
                    
                    # Check for upcoming earnings
                    if hasattr(ticker, 'calendar'):
                        calendar = ticker.calendar
                        if calendar and 'Earnings Date' in calendar:
                            earnings_date = calendar['Earnings Date'][0] if isinstance(calendar['Earnings Date'], list) else calendar['Earnings Date']
                            catalysts[symbol]['upcoming_events'].append(f"Earnings: {earnings_date}")
                    
                except Exception as e:
                    logging.warning(f"Could not fetch news for {symbol}: {e}")
            
        except Exception as e:
            logging.error(f"Error fetching catalysts: {e}")
        
        return catalysts
    
    def generate_market_commentary(self) -> Dict:
        """Generate market analysis and commentary"""
        commentary = {
            'market_conditions': '',
            'sector_performance': {},
            'trading_opportunities': [],
            'risk_warnings': [],
            'recommended_actions': []
        }
        
        try:
            # Get market indices
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(period='1d')
            spy_change = ((spy_hist['Close'].iloc[-1] - spy_hist['Open'].iloc[0]) / spy_hist['Open'].iloc[0] * 100) if len(spy_hist) > 0 else 0
            
            qqq = yf.Ticker('QQQ')
            qqq_hist = qqq.history(period='1d')
            qqq_change = ((qqq_hist['Close'].iloc[-1] - qqq_hist['Open'].iloc[0]) / qqq_hist['Open'].iloc[0] * 100) if len(qqq_hist) > 0 else 0
            
            # Market conditions
            if spy_change > 1:
                commentary['market_conditions'] = "Strong bullish market conditions with SPY up significantly"
            elif spy_change < -1:
                commentary['market_conditions'] = "Bearish market conditions with major indices declining"
            else:
                commentary['market_conditions'] = "Mixed market conditions with indices showing modest movement"
            
            # VIX for volatility
            vix = yf.Ticker('^VIX')
            vix_hist = vix.history(period='1d')
            vix_level = vix_hist['Close'].iloc[-1] if len(vix_hist) > 0 else 20
            
            if vix_level > 30:
                commentary['risk_warnings'].append("High volatility detected (VIX > 30) - Consider reducing position sizes")
            elif vix_level > 25:
                commentary['risk_warnings'].append("Elevated volatility (VIX > 25) - Monitor positions closely")
            
            # Trading opportunities based on market conditions
            if spy_change > 1.5:
                commentary['trading_opportunities'].append("Strong momentum day - Look for breakout continuations")
                commentary['recommended_actions'].append("Trail stops tighter on winning positions")
            elif spy_change < -1.5:
                commentary['trading_opportunities'].append("Oversold conditions may present buying opportunities")
                commentary['recommended_actions'].append("Consider scaling into quality names on weakness")
            
            # Sector analysis
            sectors = {
                'XLK': 'Technology',
                'XLF': 'Financials',
                'XLE': 'Energy',
                'XLV': 'Healthcare',
                'XLI': 'Industrials'
            }
            
            for ticker, name in sectors.items():
                try:
                    sector = yf.Ticker(ticker)
                    hist = sector.history(period='1d')
                    change = ((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0] * 100) if len(hist) > 0 else 0
                    commentary['sector_performance'][name] = round(change, 2)
                except:
                    pass
            
            # Top performing sector
            if commentary['sector_performance']:
                top_sector = max(commentary['sector_performance'], key=commentary['sector_performance'].get)
                commentary['trading_opportunities'].append(f"{top_sector} showing strength - Consider exposure to this sector")
            
        except Exception as e:
            logging.error(f"Error generating commentary: {e}")
            commentary['market_conditions'] = "Unable to fetch market data"
        
        return commentary
    
    def calculate_risk_metrics(self, positions, trades, account_value) -> Dict:
        """Calculate comprehensive risk metrics"""
        
        # Position concentration risk
        position_values = [p['market_value'] for p in positions]
        max_position = max(position_values) if position_values else 0
        max_position_pct = (max_position / account_value * 100) if account_value > 0 else 0
        
        # Calculate portfolio beta
        portfolio_beta = self._calculate_portfolio_beta(positions)
        
        # Value at Risk (95% confidence)
        returns = [t['realized_pnl_pct'] for t in trades if t.get('realized_pnl_pct')]
        if returns:
            var_95 = np.percentile(returns, 5) if len(returns) > 20 else None
            var_amount = (account_value * abs(var_95) / 100) if var_95 else None
        else:
            var_95 = None
            var_amount = None
        
        # Sharpe Ratio calculation
        if returns and len(returns) > 1:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + np.array(returns)/100) if returns else [1]
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown) * 100 if len(drawdown) > 0 else 0
        
        return {
            # Concentration metrics
            'max_position_size': max_position,
            'max_position_pct': max_position_pct,
            'position_count': len(positions),
            'avg_position_size': account_value / len(positions) if positions else 0,
            
            # Portfolio metrics
            'portfolio_beta': portfolio_beta,
            'portfolio_volatility': np.std(returns) if returns else 0,
            
            # Risk metrics
            'value_at_risk_95': var_95,
            'var_dollar_amount': var_amount,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            
            # Exposure metrics
            'long_exposure': sum(p['market_value'] for p in positions if p.get('side', 'long') == 'long'),
            'short_exposure': sum(p['market_value'] for p in positions if p.get('side', 'long') == 'short'),
            'net_exposure': sum(p['market_value'] for p in positions),
            'gross_exposure': sum(abs(p['market_value']) for p in positions),
            
            # Risk warnings
            'warnings': self._generate_risk_warnings(positions, max_position_pct, portfolio_beta, max_drawdown)
        }
    
    def generate_html_report(self, data) -> str:
        """Generate comprehensive HTML report with charts"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Trading Report - {data['timestamp'].strftime('%Y-%m-%d')}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 5px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-top: 5px;
        }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 14px;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 14px;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .warning-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .success-box {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .commentary {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            line-height: 1.6;
        }}
        .position-row.winner {{ background: #d4edda; }}
        .position-row.loser {{ background: #f8d7da; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Comprehensive Trading Report - SHORGAN-BOT</h1>
        <p style="color: #7f8c8d;">Generated: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S ET')}</p>
        
        <!-- Account Overview -->
        <h2>💰 Account Overview</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">${data['account']['portfolio_value']:,.2f}</div>
                <div class="metric-label">Portfolio Value</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {'' if data['pnl']['daily_pnl'] >= 0 else 'negative'}">${data['pnl']['daily_pnl']:+,.2f}</div>
                <div class="metric-label">Daily P&L</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {'' if data['pnl']['total_pnl'] >= 0 else 'negative'}">${data['pnl']['total_pnl']:+,.2f}</div>
                <div class="metric-label">Total P&L</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['account']['cash']:,.2f}</div>
                <div class="metric-label">Cash Available</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['pnl']['win_rate']:.1f}%</div>
                <div class="metric-label">Win Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['risk_metrics']['sharpe_ratio']:.2f}</div>
                <div class="metric-label">Sharpe Ratio</div>
            </div>
        </div>
        
        <!-- Market Commentary -->
        <h2>📰 Market Commentary & Analysis</h2>
        <div class="commentary">
            <p><strong>Market Conditions:</strong> {data['commentary']['market_conditions']}</p>
            
            <p><strong>Sector Performance:</strong></p>
            <ul>
                {''.join(f"<li>{sector}: <span class='{'positive' if perf >= 0 else 'negative'}'>{perf:+.2f}%</span></li>" for sector, perf in data['commentary']['sector_performance'].items())}
            </ul>
            
            <p><strong>Trading Opportunities:</strong></p>
            <ul>
                {''.join(f"<li>{opp}</li>" for opp in data['commentary']['trading_opportunities'])}
            </ul>
            
            <p><strong>Recommended Actions:</strong></p>
            <ul>
                {''.join(f"<li>{action}</li>" for action in data['commentary']['recommended_actions'])}
            </ul>
        </div>
        
        <!-- Risk Warnings -->
        {''.join(f'<div class="warning-box">⚠️ {warning}</div>' for warning in data['risk_metrics']['warnings'])}
        
        <!-- All Positions Table -->
        <h2>📈 All Current Positions ({len(data['positions'])})</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Qty</th>
                    <th>Side</th>
                    <th>Entry</th>
                    <th>Current</th>
                    <th>Today</th>
                    <th>Total P&L</th>
                    <th>P&L %</th>
                    <th>Value</th>
                    <th>Weight</th>
                    <th>Catalyst/News</th>
                    <th>Technical</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add each position
        for pos in sorted(data['positions'], key=lambda x: x['unrealized_pnl_pct'], reverse=True):
            catalyst_info = data['catalysts'].get(pos['symbol'], {})
            latest_news = catalyst_info.get('news', [{}])[0].get('title', '') if catalyst_info.get('news') else ''
            
            row_class = 'winner' if pos['unrealized_pnl'] > 0 else 'loser'
            
            html += f"""
                <tr class="position-row {row_class}">
                    <td><strong>{pos['symbol']}</strong></td>
                    <td>{pos['quantity']}</td>
                    <td>{pos.get('side', 'long').upper()}</td>
                    <td>${pos['avg_entry_price']:.2f}</td>
                    <td>${pos['current_price']:.2f}</td>
                    <td class="{'positive' if pos['change_today'] >= 0 else 'negative'}">{pos['change_today_pct']:+.2f}%</td>
                    <td class="{'positive' if pos['unrealized_pnl'] >= 0 else 'negative'}">${pos['unrealized_pnl']:,.2f}</td>
                    <td class="{'positive' if pos['unrealized_pnl_pct'] >= 0 else 'negative'}">{pos['unrealized_pnl_pct']:+.2f}%</td>
                    <td>${pos['market_value']:,.2f}</td>
                    <td>{pos['portfolio_weight']:.1f}%</td>
                    <td style="font-size: 12px;">{latest_news[:50]}...</td>
                    <td>RSI: {pos.get('rsi', 'N/A'):.0f if pos.get('rsi') else 'N/A'}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <!-- Recent Trades -->
        <h2>📊 Recent Trade History (Last 30 Days)</h2>
        <table>
            <thead>
                <tr>
                    <th>Date/Time</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Qty</th>
                    <th>Entry</th>
                    <th>Exit</th>
                    <th>P&L</th>
                    <th>P&L %</th>
                    <th>Holding Days</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add recent trades
        for trade in data['trades'][:50]:  # Show last 50 trades
            if trade.get('trade_result') in ['WIN', 'LOSS']:
                result_class = 'positive' if trade['trade_result'] == 'WIN' else 'negative'
                html += f"""
                <tr>
                    <td>{trade['time'].strftime('%m/%d %H:%M') if trade['time'] else 'N/A'}</td>
                    <td><strong>{trade['symbol']}</strong></td>
                    <td>{trade['side'].upper()}</td>
                    <td>{trade['quantity']}</td>
                    <td>${trade.get('entry_price', trade['price']):.2f}</td>
                    <td>${trade.get('exit_price', trade['price']):.2f}</td>
                    <td class="{result_class}">${trade.get('realized_pnl', 0):,.2f}</td>
                    <td class="{result_class}">{trade.get('realized_pnl_pct', 0):+.2f}%</td>
                    <td>{trade.get('holding_period', 'N/A')}</td>
                    <td class="{result_class}">{trade['trade_result']}</td>
                </tr>
"""
        
        html += f"""
            </tbody>
        </table>
        
        <!-- Performance Metrics -->
        <h2>📊 Detailed Performance Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{data['pnl']['total_trades']}</div>
                <div class="metric-label">Total Trades</div>
            </div>
            <div class="metric-card">
                <div class="metric-value positive">{data['pnl']['winning_trades']}</div>
                <div class="metric-label">Winning Trades</div>
            </div>
            <div class="metric-card">
                <div class="metric-value negative">{data['pnl']['losing_trades']}</div>
                <div class="metric-label">Losing Trades</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['pnl']['avg_win']:,.2f}</div>
                <div class="metric-label">Average Win</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['pnl']['avg_loss']:,.2f}</div>
                <div class="metric-label">Average Loss</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['pnl']['profit_factor']:.2f}</div>
                <div class="metric-label">Profit Factor</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['pnl']['largest_win']:,.2f}</div>
                <div class="metric-label">Largest Win</div>
            </div>
            <div class="metric-card">
                <div class="metric-value negative">${data['pnl']['largest_loss']:,.2f}</div>
                <div class="metric-label">Largest Loss</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['pnl']['risk_reward_ratio']:.2f}</div>
                <div class="metric-label">Risk/Reward</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['pnl']['expectancy']:,.2f}</div>
                <div class="metric-label">Expectancy</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['pnl']['avg_holding_period']:.1f} days</div>
                <div class="metric-label">Avg Hold Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['pnl']['current_streak']}</div>
                <div class="metric-label">Current Streak</div>
            </div>
        </div>
        
        <!-- Risk Analysis -->
        <h2>⚠️ Risk Analysis</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{data['risk_metrics']['portfolio_beta']:.2f}</div>
                <div class="metric-label">Portfolio Beta</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['risk_metrics']['max_position_pct']:.1f}%</div>
                <div class="metric-label">Max Position %</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['risk_metrics']['var_dollar_amount']:,.2f if data['risk_metrics']['var_dollar_amount'] else 'N/A'}</div>
                <div class="metric-label">VaR (95%)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['risk_metrics']['max_drawdown']:.2f}%</div>
                <div class="metric-label">Max Drawdown</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['risk_metrics']['long_exposure']:,.0f}</div>
                <div class="metric-label">Long Exposure</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data['risk_metrics']['short_exposure']:,.0f}</div>
                <div class="metric-label">Short Exposure</div>
            </div>
        </div>
        
        <!-- Active Catalysts -->
        <h2>🎯 Active Catalysts & Upcoming Events</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Catalyst</th>
                    <th>Recent News</th>
                    <th>Upcoming Events</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add catalyst information
        for symbol, info in data['catalysts'].items():
            if symbol in [p['symbol'] for p in data['positions']]:
                news_summary = info['news'][0]['title'] if info.get('news') else 'No recent news'
                events = ', '.join(info.get('upcoming_events', [])) or 'None scheduled'
                
                html += f"""
                <tr>
                    <td><strong>{symbol}</strong></td>
                    <td>{info.get('catalyst', 'None identified')}</td>
                    <td>{news_summary[:100]}...</td>
                    <td>{events}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <div style="margin-top: 50px; padding: 20px; background: #ecf0f1; border-radius: 8px;">
            <p style="text-align: center; color: #7f8c8d; margin: 0;">
                Report Generated: {timestamp} | SHORGAN-BOT Trading System | Comprehensive Analysis
            </p>
        </div>
    </div>
</body>
</html>
""".format(timestamp=data['timestamp'].strftime('%Y-%m-%d %H:%M:%S ET'))
        
        return html
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        if len(prices) < period:
            return None
        
        deltas = prices.diff()
        gain = deltas.where(deltas > 0, 0).rolling(window=period).mean()
        loss = -deltas.where(deltas < 0, 0).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None
    
    def _calculate_portfolio_beta(self, positions):
        """Calculate weighted portfolio beta"""
        total_value = sum(p['market_value'] for p in positions)
        if total_value == 0:
            return 1.0
        
        weighted_beta = sum(
            (p['market_value'] / total_value) * (p.get('beta', 1.0) or 1.0)
            for p in positions
        )
        
        return round(weighted_beta, 2)
    
    def _calculate_streak(self, trades):
        """Calculate current win/loss streak"""
        if not trades:
            return 0
        
        streak = 0
        last_result = None
        
        for trade in reversed(trades):
            if trade['trade_result'] not in ['WIN', 'LOSS']:
                continue
            
            if last_result is None:
                last_result = trade['trade_result']
                streak = 1 if trade['trade_result'] == 'WIN' else -1
            elif trade['trade_result'] == last_result:
                streak = streak + 1 if trade['trade_result'] == 'WIN' else streak - 1
            else:
                break
        
        return streak
    
    def _calculate_max_streak(self, trades, result_type):
        """Calculate maximum win or loss streak"""
        if not trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if trade['trade_result'] == result_type:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _generate_risk_warnings(self, positions, max_position_pct, portfolio_beta, max_drawdown):
        """Generate risk warnings based on metrics"""
        warnings = []
        
        if max_position_pct > 20:
            warnings.append(f"Position concentration risk: Largest position is {max_position_pct:.1f}% of portfolio")
        
        if portfolio_beta > 1.5:
            warnings.append(f"High portfolio beta ({portfolio_beta:.2f}) - Portfolio is more volatile than market")
        elif portfolio_beta < 0.5:
            warnings.append(f"Low portfolio beta ({portfolio_beta:.2f}) - Portfolio may underperform in bull markets")
        
        if max_drawdown < -15:
            warnings.append(f"Significant drawdown detected: {max_drawdown:.1f}%")
        
        if len(positions) > 20:
            warnings.append(f"Over-diversification: Managing {len(positions)} positions may reduce focus")
        elif len(positions) < 3:
            warnings.append(f"Under-diversification: Only {len(positions)} positions increases concentration risk")
        
        return warnings
    
    def run(self):
        """Generate comprehensive report"""
        logging.info("="*60)
        logging.info("GENERATING COMPREHENSIVE REPORT")
        logging.info("="*60)
        
        try:
            # Fetch account data
            account = self.api.get_account()
            self.data['account'] = {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity)
            }
            
            # Get all positions with details
            self.data['positions'] = self.get_all_positions()
            logging.info(f"Fetched {len(self.data['positions'])} positions")
            
            # Get complete trade history
            days_history = 30 if self.report_type == 'daily' else 90
            self.data['trades'] = self.get_complete_trade_history(days_history)
            logging.info(f"Fetched {len(self.data['trades'])} trades")
            
            # Calculate P&L metrics
            self.data['pnl'] = self.calculate_detailed_pnl(
                self.data['positions'],
                self.data['trades']
            )
            
            # Get catalysts and news
            symbols = [p['symbol'] for p in self.data['positions']]
            self.data['catalysts'] = self.get_catalysts_and_news(symbols)
            
            # Generate market commentary
            self.data['commentary'] = self.generate_market_commentary()
            
            # Calculate risk metrics
            self.data['risk_metrics'] = self.calculate_risk_metrics(
                self.data['positions'],
                self.data['trades'],
                self.data['account']['portfolio_value']
            )
            
            # Generate HTML report
            html_report = self.generate_html_report(self.data)
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = f"{self.report_dir}/comprehensive_report_{timestamp}.html"
            
            with open(html_file, 'w') as f:
                f.write(html_report)
            
            logging.info(f"Report saved to {html_file}")
            
            # Also save JSON data
            json_file = f"{self.report_dir}/comprehensive_report_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            
            logging.info("="*60)
            logging.info("COMPREHENSIVE REPORT COMPLETE")
            logging.info(f"HTML: {html_file}")
            logging.info(f"JSON: {json_file}")
            logging.info("="*60)
            
            return html_file
            
        except Exception as e:
            logging.error(f"Failed to generate report: {e}")
            raise


if __name__ == "__main__":
    import sys
    
    # Check for report type argument
    report_type = sys.argv[1] if len(sys.argv) > 1 else 'daily'
    
    generator = ComprehensiveReportGenerator(report_type)
    report_file = generator.run()
    
    # Open in browser
    import webbrowser
    if report_file:
        webbrowser.open(f"file:///{os.path.abspath(report_file)}")