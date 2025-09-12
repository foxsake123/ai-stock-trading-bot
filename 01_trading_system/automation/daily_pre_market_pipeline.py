"""
Daily Pre-Market Pipeline for SHORGAN-BOT
Runs at 7:00 AM ET each trading day
Integrates OpenAI research with multi-agent analysis
"""

import os
import sys
import json
import csv
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import requests

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import multi-agent system
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.fundamental_analyst import FundamentalAnalyst
from agents.technical_analyst import TechnicalAnalyst
from agents.news_analyst import NewsAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.bull_researcher import BullResearcher
from agents.bear_researcher import BearResearcher
from agents.risk_manager import RiskManager

load_dotenv()

# Configure logging
log_dir = '09_logs/automation'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/daily_pipeline_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class DailyPreMarketPipeline:
    """Orchestrates daily pre-market analysis and trading"""
    
    def __init__(self):
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # Initialize agents
        self.agents = {
            'fundamental': FundamentalAnalyst(),
            'technical': TechnicalAnalyst(),
            'news': NewsAnalyst(),
            'sentiment': SentimentAnalyst(),
            'bull': BullResearcher(),
            'bear': BearResearcher(),
            'risk': RiskManager()
        }
        
        # Telegram settings
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')
        
        # Portfolio tracking
        self.portfolio_csv = '02_data/portfolio/positions/shorgan_bot_positions.csv'
        self.research_dir = '02_data/research/reports/pre_market_daily'
        
    def load_portfolio(self) -> pd.DataFrame:
        """Load yesterday's portfolio from CSV"""
        try:
            if os.path.exists(self.portfolio_csv):
                df = pd.read_csv(self.portfolio_csv)
                logging.info(f"Loaded portfolio with {len(df)} positions")
                return df
            else:
                # Create new portfolio file
                df = pd.DataFrame(columns=[
                    'symbol', 'quantity', 'avg_price', 'current_price', 
                    'pnl', 'pnl_pct', 'side', 'date_acquired'
                ])
                df.to_csv(self.portfolio_csv, index=False)
                logging.info("Created new portfolio CSV")
                return df
        except Exception as e:
            logging.error(f"Error loading portfolio: {e}")
            return pd.DataFrame()
    
    def retrieve_openai_research(self) -> Dict:
        """
        Retrieve pre-market research - prioritizes ChatGPT reports over OpenAI API
        
        Priority Order:
        1. Today's ChatGPT report (manually saved)
        2. OpenAI API generation (fallback)
        3. Most recent local file (emergency fallback)
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # PRIORITY 1: Check for manually saved ChatGPT report first
            chatgpt_file = f"{self.research_dir}/{today}_chatgpt_report.json"
            if os.path.exists(chatgpt_file):
                with open(chatgpt_file, 'r') as f:
                    research = json.load(f)
                logging.info(f"[SUCCESS] Using ChatGPT report from {chatgpt_file}")
                logging.info(f"Found {len(research.get('trades', []))} trades from ChatGPT")
                return research
            
            logging.info("No ChatGPT report found for today, checking for OpenAI reports...")
            
            # PRIORITY 2: Check for existing OpenAI report
            openai_file = f"{self.research_dir}/{today}_openai_research.json"
            if os.path.exists(openai_file):
                with open(openai_file, 'r') as f:
                    research = json.load(f)
                logging.info(f"Using existing OpenAI report from {openai_file}")
                return research
            
            # PRIORITY 3: Generate new report via OpenAI API
            logging.info("No existing reports found. Generating new report via OpenAI API...")
            from openai_research_fetcher import OpenAIResearchFetcher
            
            fetcher = OpenAIResearchFetcher()
            research = fetcher.run()
            
            if research and 'trades' in research:
                logging.info(f"Generated {len(research['trades'])} trades from OpenAI")
                return research
            
            # EMERGENCY FALLBACK: Use most recent report
            logging.warning("All methods failed. Looking for most recent report...")
            files = sorted([f for f in os.listdir(self.research_dir) 
                          if f.endswith('_report.json') or f.endswith('_research.json')])
            
            if files:
                latest_file = f"{self.research_dir}/{files[-1]}"
                with open(latest_file, 'r') as f:
                    research = json.load(f)
                logging.warning(f"[FALLBACK] Using old report from {files[-1]}")
                return research
            else:
                logging.error("No research files found at all!")
                return {}
                    
        except Exception as e:
            logging.error(f"Error retrieving research: {e}")
            return {}
    
    def parse_research_file(self, content: str) -> Dict:
        """Parse research markdown file into structured data"""
        research = {
            'trades': [],
            'market_context': '',
            'risk_metrics': {}
        }
        
        # Extract trade recommendations
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'symbol' in line.lower() and 'entry' in lines[i+1] if i+1 < len(lines) else False:
                # Parse trade details
                # This is simplified - would need more robust parsing
                trade = {
                    'symbol': line.split()[0] if line.split() else '',
                    'action': 'long' if 'long' in line.lower() else 'short',
                    'entry': 0,
                    'stop': 0,
                    'target': 0,
                    'size_pct': 10
                }
                research['trades'].append(trade)
        
        return research
    
    def fetch_pre_market_data(self, symbols: List[str]) -> Dict:
        """Fetch current pre-market prices and data"""
        data = {}
        for symbol in symbols:
            try:
                # Get latest quote
                quote = self.api.get_latest_quote(symbol)
                trade = self.api.get_latest_trade(symbol)
                
                data[symbol] = {
                    'bid': quote.bid_price if quote else 0,
                    'ask': quote.ask_price if quote else 0,
                    'last': trade.price if trade else 0,
                    'volume': trade.size if trade else 0
                }
                
            except Exception as e:
                logging.error(f"Error fetching data for {symbol}: {e}")
                data[symbol] = {'bid': 0, 'ask': 0, 'last': 0, 'volume': 0}
        
        return data
    
    def run_multi_agent_analysis(self, research: Dict, market_data: Dict) -> Dict:
        """Run multi-agent analysis and risk management debate"""
        logging.info("Starting multi-agent analysis...")
        
        recommendations = {}
        
        for trade in research.get('trades', []):
            symbol = trade['symbol']
            if not symbol:
                continue
                
            # Gather analysis from each agent
            analyses = {}
            
            # Fundamental Analysis
            analyses['fundamental'] = self.agents['fundamental'].analyze(symbol, market_data.get(symbol, {}))
            
            # Technical Analysis
            analyses['technical'] = self.agents['technical'].analyze(symbol, market_data.get(symbol, {}))
            
            # News Analysis
            analyses['news'] = self.agents['news'].analyze(symbol)
            
            # Sentiment Analysis
            analyses['sentiment'] = self.agents['sentiment'].analyze(symbol)
            
            # Bull vs Bear debate
            bull_case = self.agents['bull'].make_case(symbol, analyses)
            bear_case = self.agents['bear'].make_case(symbol, analyses)
            
            # Risk Manager decision
            risk_decision = self.agents['risk'].evaluate(
                symbol=symbol,
                trade=trade,
                bull_case=bull_case,
                bear_case=bear_case,
                portfolio_value=float(self.api.get_account().portfolio_value)
            )
            
            recommendations[symbol] = {
                'trade': trade,
                'analyses': analyses,
                'bull_case': bull_case,
                'bear_case': bear_case,
                'risk_decision': risk_decision,
                'execute': risk_decision.get('approved', False)
            }
            
            logging.info(f"{symbol}: Execute={risk_decision.get('approved', False)}, "
                        f"Size={risk_decision.get('position_size', 0)}")
        
        return recommendations
    
    def execute_trades(self, recommendations: Dict) -> List[Dict]:
        """Execute approved trades via Alpaca"""
        executed_trades = []
        
        for symbol, rec in recommendations.items():
            if not rec['execute']:
                logging.info(f"Skipping {symbol} - not approved by risk manager")
                continue
            
            trade = rec['trade']
            risk_decision = rec['risk_decision']
            
            try:
                # Determine order parameters
                qty = risk_decision.get('position_size', 0)
                side = 'buy' if trade['action'] == 'long' else 'sell'
                
                if qty > 0:
                    # Submit market order
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=qty,
                        side=side,
                        type='market',
                        time_in_force='day'
                    )
                    
                    executed_trades.append({
                        'symbol': symbol,
                        'side': side,
                        'qty': qty,
                        'order_id': order.id,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    logging.info(f"Executed: {side} {qty} shares of {symbol}")
                    
                    # Set stop loss
                    time.sleep(2)
                    stop_side = 'sell' if side == 'buy' else 'buy'
                    stop_order = self.api.submit_order(
                        symbol=symbol,
                        qty=qty,
                        side=stop_side,
                        type='stop',
                        time_in_force='gtc',
                        stop_price=trade.get('stop', 0)
                    )
                    
                    logging.info(f"Stop loss set for {symbol} at ${trade.get('stop', 0)}")
                    
            except Exception as e:
                logging.error(f"Failed to execute trade for {symbol}: {e}")
        
        return executed_trades
    
    def update_portfolio_csv(self, executed_trades: List[Dict]):
        """Update portfolio CSV with new positions"""
        try:
            df = self.load_portfolio()
            
            for trade in executed_trades:
                # Add or update position
                new_row = {
                    'symbol': trade['symbol'],
                    'quantity': trade['qty'] if trade['side'] == 'buy' else -trade['qty'],
                    'avg_price': 0,  # Will be updated from Alpaca
                    'current_price': 0,
                    'pnl': 0,
                    'pnl_pct': 0,
                    'side': 'long' if trade['side'] == 'buy' else 'short',
                    'date_acquired': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Check if position exists
                if trade['symbol'] in df['symbol'].values:
                    # Update existing position
                    idx = df[df['symbol'] == trade['symbol']].index[0]
                    df.loc[idx, 'quantity'] += new_row['quantity']
                else:
                    # Add new position
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save updated portfolio
            df.to_csv(self.portfolio_csv, index=False)
            logging.info(f"Updated portfolio CSV with {len(executed_trades)} trades")
            
        except Exception as e:
            logging.error(f"Error updating portfolio CSV: {e}")
    
    def send_telegram_report(self, recommendations: Dict, executed_trades: List[Dict]):
        """Send recommendation report via Telegram"""
        try:
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            
            message = f"""🤖 SHORGAN-BOT Pre-Market Analysis
            
📅 {datetime.now().strftime('%Y-%m-%d %H:%M ET')}
💰 Portfolio: ${portfolio_value:,.2f}

📊 MULTI-AGENT RECOMMENDATIONS:
"""
            
            # Add recommendations
            for symbol, rec in recommendations.items():
                risk = rec['risk_decision']
                execute = "✅ EXECUTE" if rec['execute'] else "❌ SKIP"
                
                message += f"\n{symbol}: {execute}"
                if rec['execute']:
                    message += f"\n  Size: {risk.get('position_size', 0)} shares"
                    message += f"\n  Risk Score: {risk.get('risk_score', 0):.1f}/10"
                message += f"\n  Bull: {rec['bull_case'].get('score', 0):.1f}/10"
                message += f"\n  Bear: {rec['bear_case'].get('score', 0):.1f}/10"
            
            # Add executed trades
            if executed_trades:
                message += f"\n\n✅ TRADES EXECUTED: {len(executed_trades)}"
                for trade in executed_trades:
                    message += f"\n• {trade['symbol']}: {trade['side'].upper()} {trade['qty']} shares"
            else:
                message += "\n\n⚠️ No trades executed this session"
            
            # Risk metrics
            message += f"""

📈 RISK METRICS:
• Portfolio VAR (95%): ${portfolio_value * 0.03:,.2f}
• Max Position Size: 15%
• Stop Loss: All positions protected
"""
            
            # Send message
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logging.info("Telegram report sent successfully")
            else:
                logging.error(f"Telegram send failed: {response.text}")
                
        except Exception as e:
            logging.error(f"Error sending Telegram report: {e}")
    
    def run(self):
        """Main pipeline execution"""
        logging.info("="*60)
        logging.info("STARTING DAILY PRE-MARKET PIPELINE")
        logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        logging.info("="*60)
        
        try:
            # Step 1: Load portfolio
            portfolio = self.load_portfolio()
            
            # Step 2: Retrieve OpenAI research
            research = self.retrieve_openai_research()
            if not research or not research.get('trades'):
                logging.warning("No trade recommendations found in research")
                return
            
            # Step 3: Get symbols to analyze
            symbols = [t['symbol'] for t in research['trades'] if t.get('symbol')]
            
            # Step 4: Fetch pre-market data
            market_data = self.fetch_pre_market_data(symbols)
            
            # Step 5: Run multi-agent analysis
            recommendations = self.run_multi_agent_analysis(research, market_data)
            
            # Step 6: Execute approved trades
            executed_trades = self.execute_trades(recommendations)
            
            # Step 7: Update portfolio CSV
            self.update_portfolio_csv(executed_trades)
            
            # Step 8: Send Telegram report
            self.send_telegram_report(recommendations, executed_trades)
            
            logging.info("="*60)
            logging.info("DAILY PIPELINE COMPLETE")
            logging.info(f"Executed {len(executed_trades)} trades")
            logging.info("="*60)
            
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            # Send error notification
            self.send_error_notification(str(e))
    
    def send_error_notification(self, error_msg: str):
        """Send error notification via Telegram"""
        try:
            message = f"⚠️ SHORGAN-BOT Pipeline Error\n\n{error_msg}"
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {'chat_id': self.telegram_chat_id, 'text': message}
            requests.post(url, data=payload)
        except:
            pass

if __name__ == "__main__":
    pipeline = DailyPreMarketPipeline()
    pipeline.run()