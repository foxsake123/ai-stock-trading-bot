"""
Main orchestration script for AI Trading Bot
Coordinates all agents and manages trading decisions
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import json
# Import Financial Datasets integration instead of yfinance
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts-and-data', 'automation'))
from financial_datasets_integration import FinancialDatasetsAPI

# Import communication components
from communication.message_bus import MessageBus
from communication.coordinator import Coordinator
from communication.protocols import AgentMessage

# Import all agents
from src.agents.fundamental_analyst import FundamentalAnalystAgent
from src.agents.technical_analyst import TechnicalAnalystAgent
from src.agents.news_analyst import NewsAnalystAgent
from src.agents.sentiment_analyst import SentimentAnalystAgent
from src.agents.bull_researcher import BullResearcherAgent
from src.agents.bear_researcher import BearResearcherAgent
from src.agents.risk_manager import RiskManagerAgent
from src.agents.shorgan_catalyst_agent import ShorganCatalystAgent
from src.agents.options_strategy_agent import OptionsStrategyAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

class TradingSystem:
    """Main trading system orchestrator"""
    
    def __init__(self):
        self.message_bus = MessageBus()
        self.coordinator = Coordinator(self.message_bus)
        self.agents = {}
        self.running = False
        # Initialize Financial Datasets API
        self.fd_api = FinancialDatasetsAPI()
        
    async def initialize(self):
        """Initialize the trading system"""
        logger.info("Initializing AI Trading System...")
        
        # Start message bus
        await self.message_bus.start()
        
        # Initialize and register agents
        self._initialize_agents()
        
        logger.info("System initialization complete")
        
    def _initialize_agents(self):
        """Initialize all trading agents"""
        # Core analysis agents
        self.agents['fundamental'] = FundamentalAnalystAgent()
        self.agents['technical'] = TechnicalAnalystAgent()
        self.agents['news'] = NewsAnalystAgent()
        self.agents['sentiment'] = SentimentAnalystAgent()
        
        # Research agents
        self.agents['bull'] = BullResearcherAgent()
        self.agents['bear'] = BearResearcherAgent()
        
        # Risk management (with veto power)
        self.agents['risk'] = RiskManagerAgent()
        
        # Specialized trading agents
        self.agents['catalyst'] = ShorganCatalystAgent()
        self.agents['options'] = OptionsStrategyAgent()
        
        # Register all agents with coordinator
        for name, agent in self.agents.items():
            self.coordinator.register_agent(agent.agent_id, agent)
            logger.info(f"Registered agent: {name} ({agent.agent_id})")
            
    async def analyze_stock(self, ticker: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a stock
        
        Args:
            ticker: Stock symbol to analyze
            
        Returns:
            Trading decision from coordinator
        """
        logger.info(f"Starting analysis for {ticker}")
        
        try:
            # Get market data
            market_data = await self._get_market_data(ticker)

            # Get supplementary data
            news_data = await self._get_news_data(ticker)
            social_data = await self._get_social_data(ticker)
            portfolio_data = await self._get_portfolio_data()

            # Prepare data packages for agents
            catalyst_data = {
                'news': news_data,
                'events': []  # Would fetch from calendar API
            }

            fundamental_data = self._extract_fundamental_data(market_data)
            technical_data = self._extract_technical_data(market_data)

            supplemental_data = {}

            def _register_context(agent_key: str, context: Dict[str, Any]) -> None:
                agent = self.agents[agent_key]
                supplemental_data[agent.agent_type] = context
                supplemental_data[agent.agent_id] = context

            _register_context('fundamental', {'fundamental_data': fundamental_data})
            _register_context('technical', {'technical_data': technical_data})
            _register_context('news', {'news_data': news_data})
            _register_context('sentiment', {'social_data': social_data})
            bull_context = {
                'fundamental_data': fundamental_data,
                'technical_data': technical_data,
                'news_data': news_data
            }
            _register_context('bull', bull_context)
            _register_context('bear', bull_context)
            _register_context('catalyst', {'catalyst_data': catalyst_data})
            _register_context('options', {'catalyst_data': catalyst_data})
            _register_context('risk', {'portfolio_data': portfolio_data})

            analyses = self.coordinator.request_analysis(
                ticker,
                market_data,
                supplemental_data=supplemental_data
            )

            self.coordinator.make_decision(ticker, analyses)
            decisions = self.coordinator.get_decision_history(ticker, limit=1)

            if decisions:
                final_decision = decisions[0]
                logger.info(f"Final decision for {ticker}: {final_decision.action.value}")
                return final_decision.to_dict()

            logger.warning(f"No decision reached for {ticker}")
            return {"error": "No consensus reached"}
                
        except Exception as e:
            logger.error(f"Analysis failed for {ticker}: {e}")
            return {"error": str(e)}
            
    async def _run_agent_analysis(self, agent, ticker: str, 
                                 market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Run analysis for a single agent"""
        try:
            result = agent.analyze(ticker, market_data, **kwargs)
            
            # Publish to message bus
            message = AgentMessage(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                timestamp=datetime.now(),
                ticker=ticker,
                message_type="analysis",
                payload=result,
                priority=1
            )
            await self.message_bus.publish(message)
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent.agent_id} failed: {e}")
            return {"error": str(e)}
            
    async def _get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch current market data using Financial Datasets API"""
        try:
            # Get snapshot data
            snapshot = self.fd_api.get_snapshot_price(ticker)

            # Get historical data for volatility calculation
            hist_df = self.fd_api.get_historical_prices(ticker, interval='day', limit=30)

            # Get financial metrics
            metrics = self.fd_api.get_financial_metrics(ticker)

            # Calculate volatility if historical data available
            volatility = 0.3  # Default
            support_level = 0
            if not hist_df.empty:
                volatility = hist_df['close'].pct_change().std() * (252 ** 0.5)
                support_level = hist_df['low'].min()

            return {
                'price': snapshot.get('price', 0),
                'volume': snapshot.get('volume', 0),
                'market_cap': snapshot.get('market_cap', 0),
                'pe_ratio': metrics.get('pe_ratio', 0),
                'beta': metrics.get('beta', 1),
                'volatility': volatility,
                'sector': 'Technology',  # Would need to fetch from company info
                'avg_volume': snapshot.get('volume', 0),  # Using current as proxy
                'support_level': support_level,
                'info': {**snapshot, **metrics}  # Combine all data
            }
        except Exception as e:
            logger.error(f"Failed to get market data for {ticker}: {e}")
            return {}
            
    async def _get_news_data(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch news data from Financial Datasets API"""
        try:
            # Get real news from Financial Datasets
            news_articles = self.fd_api.get_news(ticker, limit=10)

            if news_articles:
                return news_articles
            else:
                # Fallback to placeholder if no news
                return [
                    {
                        'title': f"No recent news for {ticker}",
                        'content': "No news articles found",
                        'source': 'none',
                        'published_date': datetime.now().isoformat()
                    }
                ]
        except Exception as e:
            logger.error(f"Failed to get news data: {e}")
            return []
        
    async def _get_social_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch social media data (placeholder)"""
        # In production, would connect to social media APIs
        return {
            'twitter': [],
            'reddit': [],
            'recent_mentions': 100,
            'historical_avg_mentions': 50
        }
        
    async def _get_portfolio_data(self) -> Dict[str, Any]:
        """Get current portfolio data"""
        # In production, would connect to broker API
        return {
            'positions': [],
            'total_value': 100000,
            'portfolio_volatility': 0.15,
            'max_drawdown': 0.1
        }
        
    def _extract_fundamental_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fundamental data from market data"""
        info = market_data.get('info', {})
        return {
            'revenue_growth': info.get('revenueGrowth', 0),
            'earnings_growth': info.get('earningsGrowth', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'return_on_equity': info.get('returnOnEquity', 0),
            'gross_margin': info.get('grossMargins', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'free_cash_flow': info.get('freeCashflow', 0)
        }
        
    def _extract_technical_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical data from market data"""
        # Simplified technical data
        return {
            'price_change_30d': 0.05,  # Placeholder
            'volume_ratio': 1.2,
            'above_resistance': False,
            'ma_alignment': 'neutral'
        }
        
    async def run_batch_analysis(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Run analysis on multiple stocks"""
        logger.info(f"Running batch analysis for {len(tickers)} stocks")
        
        results = []
        for ticker in tickers:
            result = await self.analyze_stock(ticker)
            results.append({
                'ticker': ticker,
                'analysis': result
            })
            
            # Add delay to avoid overwhelming APIs
            await asyncio.sleep(1)
            
        return results
        
    async def start_monitoring(self, tickers: List[str], interval: int = 300):
        """Start continuous monitoring of stocks"""
        logger.info(f"Starting monitoring for {tickers} every {interval} seconds")
        
        self.running = True
        while self.running:
            for ticker in tickers:
                await self.analyze_stock(ticker)
            
            await asyncio.sleep(interval)
            
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.running = False
        logger.info("Monitoring stopped")
        
    async def shutdown(self):
        """Shutdown the trading system"""
        logger.info("Shutting down trading system...")
        await self.message_bus.stop()
        logger.info("Shutdown complete")

async def main():
    """Main entry point"""
    # Create trading system
    system = TradingSystem()
    
    # Initialize
    await system.initialize()
    
    # Example: Analyze a single stock
    result = await system.analyze_stock("AAPL")
    print(json.dumps(result, indent=2))
    
    # Example: Batch analysis
    # batch_results = await system.run_batch_analysis(["AAPL", "GOOGL", "MSFT"])
    # for result in batch_results:
    #     print(f"{result['ticker']}: {result['analysis'].get('action', 'ERROR')}")
    
    # Shutdown
    await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())