"""
Quick report generator - handles missing data gracefully
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def generate_simple_report():
    """Generate a simple but comprehensive report"""
    
    # Initialize Alpaca API
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        'https://paper-api.alpaca.markets',
        api_version='v2'
    )
    
    print("Fetching account data...")
    account = api.get_account()
    
    print("Fetching positions...")
    positions = api.list_positions()
    
    print("Fetching recent orders...")
    orders = api.list_orders(
        status='all',
        after=(datetime.now() - timedelta(days=30)).isoformat() + 'Z',
        limit=100
    )
    
    # Generate HTML report
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Trading Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
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
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px; }}
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
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 SHORGAN-BOT Trading Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}</p>
        
        <h2>💰 Account Overview</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">${float(account.portfolio_value):,.2f}</div>
                <div class="metric-label">Portfolio Value</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${float(account.cash):,.2f}</div>
                <div class="metric-label">Cash Balance</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${float(account.buying_power):,.2f}</div>
                <div class="metric-label">Buying Power</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(positions)}</div>
                <div class="metric-label">Open Positions</div>
            </div>
        </div>
        
        <h2>📈 All Current Positions</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Qty</th>
                    <th>Side</th>
                    <th>Avg Entry</th>
                    <th>Current Price</th>
                    <th>Market Value</th>
                    <th>Unrealized P&L</th>
                    <th>P&L %</th>
                    <th>Today's Change</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add positions
    total_unrealized = 0
    total_daily_change = 0
    
    for pos in positions:
        unrealized_pnl = float(pos.unrealized_pl or 0)
        unrealized_pct = float(pos.unrealized_plpc or 0) * 100
        change_today = float(pos.change_today or 0)
        
        total_unrealized += unrealized_pnl
        total_daily_change += change_today
        
        pnl_class = 'positive' if unrealized_pnl >= 0 else 'negative'
        change_class = 'positive' if change_today >= 0 else 'negative'
        
        html += f"""
                <tr>
                    <td><strong>{pos.symbol}</strong></td>
                    <td>{pos.qty}</td>
                    <td>{pos.side.upper()}</td>
                    <td>${float(pos.avg_entry_price):.2f}</td>
                    <td>${float(pos.current_price or 0):.2f}</td>
                    <td>${float(pos.market_value or 0):,.2f}</td>
                    <td class="{pnl_class}">${unrealized_pnl:,.2f}</td>
                    <td class="{pnl_class}">{unrealized_pct:+.2f}%</td>
                    <td class="{change_class}">${change_today:,.2f}</td>
                </tr>
"""
    
    html += f"""
            </tbody>
        </table>
        
        <h2>📊 P&L Summary</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value {'positive' if total_unrealized >= 0 else 'negative'}">${total_unrealized:,.2f}</div>
                <div class="metric-label">Total Unrealized P&L</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {'positive' if total_daily_change >= 0 else 'negative'}">${total_daily_change:,.2f}</div>
                <div class="metric-label">Today's Change</div>
            </div>
        </div>
        
        <h2>📋 Recent Orders (Last 30 Days)</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Qty</th>
                    <th>Type</th>
                    <th>Price</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add recent orders
    for order in list(orders)[:50]:  # Show last 50 orders
        order_time = order.created_at.strftime('%m/%d %H:%M') if order.created_at else 'N/A'
        price = f"${float(order.filled_avg_price):.2f}" if order.filled_avg_price else order.limit_price or 'Market'
        
        html += f"""
                <tr>
                    <td>{order_time}</td>
                    <td><strong>{order.symbol}</strong></td>
                    <td>{order.side.upper()}</td>
                    <td>{order.qty}</td>
                    <td>{order.order_type.upper()}</td>
                    <td>{price}</td>
                    <td>{order.status.upper()}</td>
                </tr>
"""
    
    # Calculate some basic stats
    filled_orders = [o for o in orders if o.status == 'filled']
    buy_orders = [o for o in filled_orders if o.side == 'buy']
    sell_orders = [o for o in filled_orders if o.side == 'sell']
    
    html += f"""
            </tbody>
        </table>
        
        <h2>📊 Trading Statistics (Last 30 Days)</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{len(filled_orders)}</div>
                <div class="metric-label">Total Trades</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(buy_orders)}</div>
                <div class="metric-label">Buy Orders</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(sell_orders)}</div>
                <div class="metric-label">Sell Orders</div>
            </div>
        </div>
        
        <div style="margin-top: 50px; padding: 20px; background: #ecf0f1; border-radius: 8px;">
            <p style="text-align: center; color: #7f8c8d; margin: 0;">
                SHORGAN-BOT Trading System | Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save report
    report_dir = '07_docs/daily_comprehensive_reports'
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{report_dir}/report_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n[SUCCESS] Report saved to: {filename}")
    print(f"\nSummary:")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"  Positions: {len(positions)}")
    print(f"  Unrealized P&L: ${total_unrealized:,.2f}")
    print(f"  Today's Change: ${total_daily_change:,.2f}")
    
    # Open in browser
    import webbrowser
    webbrowser.open(f"file:///{os.path.abspath(filename)}")
    
    return filename

if __name__ == "__main__":
    generate_simple_report()