"""
Enhanced Main orchestration script for AI Trading Bot
Integrates new data providers based on TradingAgents paper
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import json
import sys

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

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

# Import enhanced data providers
from data.enhanced_providers import EnhancedDataHub

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main_enhanced")

class EnhancedTradingSystem:
    """Enhanced trading system with improved data sources"""
    
    def __init__(self):
        self.message_bus = MessageBus()
        self.coordinator = Coordinator(self.message_bus)
        self.agents = {}
        self.data_hub = EnhancedDataHub()  # New enhanced data hub
        self.running = False
        
    async def initialize(self):
        """Initialize the enhanced trading system"""
        logger.info("=" * 60)
        logger.info("Initializing Enhanced AI Trading System...")
        logger.info("=" * 60)
        
        # Start message bus
        await self.message_bus.start()
        
        # Initialize and register agents
        self._initialize_agents()
        
        # Test data sources
        await self._test_data_sources()
        
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
            logger.info(f"✓ Registered agent: {name} ({agent.agent_id})")
            
    async def _test_data_sources(self):
        """Test available data sources"""
        logger.info("\nTesting Data Sources...")
        logger.info("-" * 40)
        
        # Test with a simple ticker
        test_ticker = "MSFT"
        
        try:
            # Test market data
            market_data = await self.data_hub.get_market_data(test_ticker)
            if market_data.get('price', 0) > 0:
                logger.info(f"✓ Market Data: {test_ticker} @ ${market_data['price']:.2f} via {market_data.get('source', 'unknown')}")
            else:
                logger.warning(f"⚠ Market Data: Limited availability")
                
            # Test news
            news = await self.data_hub.get_news(test_ticker, limit=1)
            if news:
                logger.info(f"✓ News Feed: {len(news)} articles available")
            else:
                logger.warning(f"⚠ News Feed: No data available")
                
            # Test sentiment
            sentiment = await self.data_hub.get_social_sentiment(test_ticker)
            logger.info(f"✓ Sentiment: Score {sentiment['overall_score']:.2f} from {len(sentiment.get('sources', []))} sources")
            
        except Exception as e:
            logger.error(f"Data source test failed: {e}")
            
    async def analyze_stock(self, ticker: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a stock using enhanced data
        
        Args:
            ticker: Stock symbol to analyze
            
        Returns:
            Trading decision from coordinator
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting Enhanced Analysis for {ticker}")
        logger.info(f"{'='*60}")
        
        try:
            # Get comprehensive data from enhanced hub
            logger.info("Fetching data from multiple sources...")
            
            # Get all data types
            market_data = await self.data_hub.get_market_data(ticker)
            news_data = await self.data_hub.get_news(ticker, limit=10)
            social_data = await self.data_hub.get_social_sentiment(ticker)
            options_data = await self.data_hub.get_options_flow(ticker)
            economic_data = await self.data_hub.get_economic_indicators()
            
            # Log data availability
            logger.info(f"Data Sources Retrieved:")
            logger.info(f"  - Market: {market_data.get('source', 'N/A')}")
            logger.info(f"  - News: {len(news_data)} articles")
            logger.info(f"  - Sentiment: {len(social_data.get('sources', []))} sources")
            logger.info(f"  - Options: {options_data.get('source', 'N/A')}")
            
            # Prepare catalyst data
            catalyst_data = {
                'news': news_data,
                'social_sentiment': social_data,
                'options_flow': options_data,
                'events': []  # Would fetch from calendar API
            }
            
            # Extract fundamental and technical data
            fundamental_data = self._extract_fundamental_data(market_data)
            technical_data = self._extract_technical_data(market_data)

            logger.info("\nRunning agent analyses...")

            portfolio_data = await self._get_portfolio_data()

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

            # Get final decision
            decisions = self.coordinator.get_decision_history(ticker, limit=1)

            if decisions:
                final_decision = decisions[0]
                logger.info(f"\n{'='*60}")
                logger.info(f"FINAL DECISION for {ticker}: {final_decision.action.value}")
                logger.info(f"Confidence: {final_decision.confidence:.2%}")
                logger.info(f"{'='*60}")
                return final_decision.to_dict()
            else:
                logger.warning(f"No consensus reached for {ticker}")
                return {"error": "No consensus reached"}
                
        except Exception as e:
            logger.error(f"Analysis failed for {ticker}: {e}")
            return {"error": str(e)}
            
    async def _run_agent_analysis(self, agent, ticker: str, 
                                 market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Run analysis for a single agent"""
        try:
            # Filter kwargs to only pass relevant data for each agent
            agent_kwargs = {}
            if agent.agent_type == "fundamental":
                agent_kwargs['fundamental_data'] = kwargs.get('fundamental_data', {})
            elif agent.agent_type == "technical":
                agent_kwargs['technical_data'] = kwargs.get('technical_data', {})
            elif agent.agent_type == "news":
                agent_kwargs['news_data'] = kwargs.get('news_data', [])
            elif agent.agent_type == "sentiment":
                agent_kwargs['social_data'] = kwargs.get('social_data', {})
            elif agent.agent_type in ["bull", "bear"]:
                agent_kwargs = {
                    'fundamental_data': kwargs.get('fundamental_data', {}),
                    'technical_data': kwargs.get('technical_data', {}),
                    'news_data': kwargs.get('news_data', [])
                }
            elif agent.agent_type == "catalyst":
                agent_kwargs['catalyst_data'] = kwargs.get('catalyst_data', {})
            elif agent.agent_type == "options":
                agent_kwargs['catalyst_data'] = kwargs.get('catalyst_data', {})
            elif agent.agent_type == "risk":
                agent_kwargs = {
                    'portfolio_data': kwargs.get('portfolio_data', {}),
                    'agent_reports': kwargs.get('agent_reports', [])
                }
            
            result = agent.analyze(ticker, market_data, **agent_kwargs)
            
            # Publish to message bus
            from communication.protocols import AgentMessage
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
            
            logger.info(f"  ✓ {agent.agent_type}: {result.get('recommendation', {}).get('action', 'N/A')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent.agent_id} failed: {e}")
            return {"error": str(e)}
            
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
        return {
            'pe_ratio': market_data.get('pe_ratio', 0),
            'market_cap': market_data.get('market_cap', 0),
            'price': market_data.get('price', 0)
        }
        
    def _extract_technical_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical data from market data"""
        return {
            'price': market_data.get('price', 0),
            'volume': market_data.get('volume', 0),
            'high': market_data.get('high', 0),
            'low': market_data.get('low', 0)
        }
        
    async def run_batch_analysis(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Run analysis on multiple stocks"""
        logger.info(f"\nRunning batch analysis for {len(tickers)} stocks")
        
        results = []
        for ticker in tickers:
            result = await self.analyze_stock(ticker)
            results.append({
                'ticker': ticker,
                'analysis': result
            })
            
            # Add delay to avoid overwhelming APIs
            await asyncio.sleep(2)
            
        return results
        
    async def shutdown(self):
        """Shutdown the trading system"""
        logger.info("\nShutting down enhanced trading system...")
        await self.message_bus.stop()
        logger.info("Shutdown complete")

async def main():
    """Main entry point for enhanced system"""
    # Create enhanced trading system
    system = EnhancedTradingSystem()
    
    # Initialize
    await system.initialize()
    
    # Example: Analyze a single stock
    print("\n" + "="*60)
    print("EXAMPLE ANALYSIS")
    print("="*60)
    
    result = await system.analyze_stock("NVDA")
    
    # Pretty print result
    print("\nAnalysis Result:")
    print(json.dumps(result, indent=2))
    
    # Example: Batch analysis (commented out to save API calls)
    # print("\n" + "="*60)
    # print("BATCH ANALYSIS")
    # print("="*60)
    # batch_results = await system.run_batch_analysis(["AAPL", "GOOGL", "MSFT"])
    # for result in batch_results:
    #     action = result['analysis'].get('action', 'ERROR')
    #     confidence = result['analysis'].get('confidence', 0)
    #     print(f"{result['ticker']}: {action} (Confidence: {confidence:.2%})")
    
    # Shutdown
    await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())