"""
Process ChatGPT Trades Through Multi-Agent Analysis
"""

import json
import os
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradeProcessor:
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
    def analyze_trade(self, trade):
        """Simulate multi-agent analysis"""
        symbol = trade['symbol']
        
        # Get current price from Alpaca
        try:
            quote = self.api.get_latest_quote(symbol)
            current_price = float(quote.ask_price) if quote and quote.ask_price > 0 else float(quote.bid_price)
            logging.info(f"Got price for {symbol}: ${current_price:.2f}")
        except Exception as e:
            logging.warning(f"Could not get quote for {symbol}: {e}")
            # Try to get last trade price as fallback
            try:
                trade_data = self.api.get_latest_trade(symbol)
                current_price = float(trade_data.price) if trade_data else 0
                logging.info(f"Using last trade price for {symbol}: ${current_price:.2f}")
            except:
                current_price = 0
                logging.error(f"No price data available for {symbol}")
            
        # Simulate agent scores based on trade confidence and risk
        confidence_map = {'low': 5, 'low-medium': 6, 'medium': 7, 'medium-high': 8, 'high': 9}
        base_score = confidence_map.get(trade.get('confidence', 'medium'), 7)
        
        risk_adjustment = {'low': 1, 'medium': 0, 'high': -0.5, 'very high': -1, 'very_high': -1}
        risk_adj = risk_adjustment.get(trade.get('risk', 'medium'), 0)
        
        # Generate agent scores
        scores = {
            'fundamental': base_score + 0.5,  # Catalyst-driven trades have good fundamentals
            'technical': base_score - 0.2,    # Technical varies
            'news': base_score + 1.0,         # Strong news catalysts
            'sentiment': base_score,          # Neutral sentiment
            'bull': base_score + 0.8,         # Bullish on catalysts
            'bear': 5 - risk_adj,             # Bears see risk
            'risk': base_score + risk_adj     # Risk manager adjusts for risk level
        }
        
        # Calculate consensus
        weights = {
            'fundamental': 0.20,
            'technical': 0.20,
            'news': 0.15,
            'sentiment': 0.10,
            'bull': 0.15,
            'bear': 0.15,
            'risk': 0.05
        }
        
        consensus = sum(scores[agent] * weights[agent] for agent in scores)
        
        # Risk manager decision
        approved = consensus > 6.5 and scores['risk'] > 5
        
        # Calculate position size
        account = self.api.get_account()
        portfolio_value = float(account.portfolio_value)
        position_size_pct = trade.get('size_pct', 5)
        
        if trade.get('risk') in ['very high', 'very_high']:
            position_size_pct = min(position_size_pct, 3)
        elif trade.get('risk') == 'high':
            position_size_pct = min(position_size_pct, 4)
            
        position_value = portfolio_value * (position_size_pct / 100)
        shares = int(position_value / current_price) if current_price > 0 else 0
        
        return {
            'symbol': symbol,
            'approved': approved,
            'consensus_score': round(consensus, 2),
            'agent_scores': scores,
            'position_size_pct': position_size_pct,
            'position_size_shares': shares,
            'current_price': current_price,
            'stop_price': round(current_price * (1 - trade.get('stop_pct', 8) / 100), 2) if current_price > 0 else 0,
            'target_price': round(trade.get('target', current_price * 1.2), 2) if current_price > 0 else 0,
            'catalyst': trade.get('catalyst', 'N/A')
        }
    
    def execute_trade(self, analysis):
        """Execute approved trades"""
        if not analysis['approved'] or analysis['position_size_shares'] == 0:
            return None
            
        try:
            # Submit market order
            order = self.api.submit_order(
                symbol=analysis['symbol'],
                qty=analysis['position_size_shares'],
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            logging.info(f"Executed: BUY {analysis['position_size_shares']} shares of {analysis['symbol']}")
            
            # Set stop loss order (after main order fills)
            import time
            time.sleep(3)
            
            if analysis['stop_price'] > 0:
                stop_order = self.api.submit_order(
                    symbol=analysis['symbol'],
                    qty=analysis['position_size_shares'],
                    side='sell',
                    type='stop',
                    time_in_force='gtc',
                    stop_price=analysis['stop_price']
                )
                logging.info(f"Stop loss set for {analysis['symbol']} at ${analysis['stop_price']:.2f}")
            
            return {
                'order_id': order.id,
                'symbol': analysis['symbol'],
                'qty': analysis['position_size_shares'],
                'side': 'buy',
                'status': 'submitted'
            }
            
        except Exception as e:
            logging.error(f"Failed to execute trade for {analysis['symbol']}: {e}")
            return None
    
    def process_all_trades(self):
        """Process all trades from ChatGPT report"""
        
        # Load report - check multiple paths
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        # Try multiple paths
        report_paths = [
            f'../daily-json/chatgpt/chatgpt_report_{today}.json',
            '../daily-json/chatgpt/chatgpt_report_2025-09-18.json',
            '../../02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_report.json'
        ]

        report_path = None
        for path in report_paths:
            if os.path.exists(path):
                report_path = path
                break

        if not report_path:
            logging.error("No ChatGPT report found!")
            return {'analyses': [], 'executed': [], 'rejected': []}
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        logging.info(f"Processing {len(report['trades'])} trade recommendations...")
        
        results = {
            'analyses': [],
            'executed': [],
            'rejected': []
        }
        
        for trade in report['trades']:
            # Analyze trade
            analysis = self.analyze_trade(trade)
            results['analyses'].append(analysis)
            
            # Log analysis
            logging.info(f"\n{analysis['symbol']}:")
            logging.info(f"  Consensus: {analysis['consensus_score']}/10")
            logging.info(f"  Decision: {'APPROVED' if analysis['approved'] else 'REJECTED'}")
            logging.info(f"  Position: {analysis['position_size_pct']}% ({analysis['position_size_shares']} shares)")
            
            if analysis['approved']:
                # Execute trade
                execution = self.execute_trade(analysis)
                if execution:
                    results['executed'].append(execution)
                else:
                    results['rejected'].append(analysis['symbol'])
            else:
                results['rejected'].append(analysis['symbol'])
        
        # Save results
        results_path = f"02_data/reports/execution/execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results

def main():
    processor = TradeProcessor()
    results = processor.process_all_trades()
    
    print("\n" + "="*60)
    print("TRADE PROCESSING COMPLETE")
    print("="*60)
    print(f"Analyzed: {len(results['analyses'])} trades")
    print(f"Executed: {len(results['executed'])} trades")
    print(f"Rejected: {len(results['rejected'])} trades")
    
    if results['executed']:
        print("\nEXECUTED TRADES:")
        for trade in results['executed']:
            print(f"  - {trade['symbol']}: {trade['qty']} shares")
    
    if results['rejected']:
        print("\nREJECTED TRADES:")
        for symbol in results['rejected']:
            print(f"  - {symbol}")

if __name__ == "__main__":
    main()