"""
Main orchestration script for AI Trading Bot
Coordinates all agents and manages trading decisions
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import yfinance as yf
import json

# Import communication components
from communication.message_bus import MessageBus
from communication.coordinator import Coordinator

# Import all agents
from agents.fundamental_analyst import FundamentalAnalystAgent
from agents.technical_analyst import TechnicalAnalystAgent
from agents.news_analyst import NewsAnalystAgent
from agents.sentiment_analyst import SentimentAnalystAgent
from agents.bull_researcher import BullResearcherAgent
from agents.bear_researcher import BearResearcherAgent
from agents.risk_manager import RiskManagerAgent
from agents.shorgan_catalyst_agent import ShorganCatalystAgent
from agents.options_strategy_agent import OptionsStrategyAgent

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
            
            # Prepare data packages for agents
            catalyst_data = {
                'news': news_data,
                'events': []  # Would fetch from calendar API
            }
            
            fundamental_data = self._extract_fundamental_data(market_data)
            technical_data = self._extract_technical_data(market_data)
            
            # Run all agent analyses in parallel
            tasks = []
            
            # Fundamental analyst
            tasks.append(self._run_agent_analysis(
                self.agents['fundamental'], ticker, market_data,
                fundamental_data=fundamental_data
            ))
            
            # Technical analyst
            tasks.append(self._run_agent_analysis(
                self.agents['technical'], ticker, market_data,
                technical_data=technical_data
            ))
            
            # News analyst
            tasks.append(self._run_agent_analysis(
                self.agents['news'], ticker, market_data,
                news_data=news_data
            ))
            
            # Sentiment analyst
            tasks.append(self._run_agent_analysis(
                self.agents['sentiment'], ticker, market_data,
                social_data=social_data
            ))
            
            # Bull researcher
            tasks.append(self._run_agent_analysis(
                self.agents['bull'], ticker, market_data,
                fundamental_data=fundamental_data,
                technical_data=technical_data,
                news_data=news_data
            ))
            
            # Bear researcher
            tasks.append(self._run_agent_analysis(
                self.agents['bear'], ticker, market_data,
                fundamental_data=fundamental_data,
                technical_data=technical_data,
                news_data=news_data
            ))
            
            # Catalyst trader
            tasks.append(self._run_agent_analysis(
                self.agents['catalyst'], ticker, market_data,
                catalyst_data=catalyst_data
            ))
            
            # Options trader
            tasks.append(self._run_agent_analysis(
                self.agents['options'], ticker, market_data,
                catalyst_data=catalyst_data
            ))
            
            # Wait for all analyses to complete
            agent_results = await asyncio.gather(*tasks)
            
            # Risk manager analyzes last with all other results
            portfolio_data = await self._get_portfolio_data()
            risk_result = await self._run_agent_analysis(
                self.agents['risk'], ticker, market_data,
                portfolio_data=portfolio_data,
                agent_reports=agent_results
            )
            
            # Add risk result to agent results
            agent_results.append(risk_result)
            
            # Let coordinator make final decision
            await self.coordinator.request_analysis(ticker, market_data, catalyst_data)
            
            # Wait for coordinator decision
            await asyncio.sleep(2)  # Give time for consensus
            
            # Get final decision
            decisions = self.coordinator.get_decision_history(ticker, limit=1)
            
            if decisions:
                final_decision = decisions[0]
                logger.info(f"Final decision for {ticker}: {final_decision.action.value}")
                return final_decision.to_dict()
            else:
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
            topic = "agent.analysis"
            message = {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "timestamp": datetime.now().isoformat(),
                "ticker": ticker,
                "message_type": "analysis",
                "payload": result,
                "priority": 1,
            }
            await self.message_bus.publish(topic, message)
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent.agent_id} failed: {e}")
            return {"error": str(e)}
            
    async def _get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch current market data"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")
            
            return {
                'price': info.get('regularMarketPrice', hist['Close'].iloc[-1] if not hist.empty else 0),
                'volume': info.get('regularMarketVolume', hist['Volume'].iloc[-1] if not hist.empty else 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'beta': info.get('beta', 1),
                'volatility': hist['Close'].pct_change().std() * (252 ** 0.5) if not hist.empty else 0.3,
                'sector': info.get('sector', 'Unknown'),
                'avg_volume': info.get('averageVolume', 0),
                'support_level': hist['Low'].min() if not hist.empty else 0,
                'info': info
            }
        except Exception as e:
            logger.error(f"Failed to get market data for {ticker}: {e}")
            return {}
            
    async def _get_news_data(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch news data (placeholder)"""
        # In production, would connect to news API
        return [
            {
                'title': f"Sample news for {ticker}",
                'content': "Placeholder news content",
                'source': 'reuters',
                'published_date': datetime.now().isoformat()
            }
        ]
        
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