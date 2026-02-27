"""
Intelligence Hub Signal Agent
Consumes real-time signals from the Trading Intelligence Hub

This agent integrates the Intelligence Hub's 15+ data sources into
the multi-agent trading decision system.

Sources via Hub:
- Grok/X real-time sentiment
- Multi-source sentiment (Twitter, News, Reddit, Kalshi)
- Options flow analysis
- Whale activity alerts
- Upcoming catalyst events
- Financial Datasets API data
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Import base agent
try:
    from .base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HubSignalAgent(BaseAgent):
    """
    Agent that integrates Intelligence Hub signals into trading decisions
    
    Provides:
    - Multi-source sentiment (Grok, Twitter, Reddit, News, Kalshi)
    - Options flow analysis
    - Whale activity alerts
    - Upcoming catalyst events
    - Real-time signal aggregation
    """
    
    def __init__(self, hub_url: str = None):
        super().__init__(
            agent_id="hub_signal_001",
            agent_type="hub_signal"
        )
        
        # Hub configuration
        self.hub_url = hub_url or os.getenv('INTELLIGENCE_HUB_URL', 'http://localhost:8000')
        self.timeout = aiohttp.ClientTimeout(total=5)
        
        # Cache for reducing API calls
        self.cache: Dict[str, tuple] = {}  # ticker -> (data, timestamp)
        self.cache_ttl = 60  # seconds
        
        # Signal weights (tuned for stock trading)
        self.signal_weights = {
            "sentiment": 0.30,
            "options_flow": 0.35,
            "events": 0.20,
            "recent_signals": 0.15
        }
        
        logger.info(f"HubSignalAgent initialized with hub at {self.hub_url}")
    
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Synchronous wrapper for async analysis
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self._analyze_async(ticker, market_data, **kwargs))
                    return future.result(timeout=10)
            else:
                return asyncio.run(self._analyze_async(ticker, market_data, **kwargs))
        except Exception as e:
            logger.error(f"Hub signal analysis failed for {ticker}: {e}")
            return self._get_fallback_result(ticker, str(e))
    
    async def _analyze_async(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze ticker using Intelligence Hub data
        """
        logger.info(f"Analyzing {ticker} via Intelligence Hub")
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Check hub health first
                if not await self._check_hub_health(session):
                    return self._get_fallback_result(ticker, "Hub not available")
                
                # Fetch all signals concurrently
                results = await asyncio.gather(
                    self._fetch_sentiment(session, ticker),
                    self._fetch_options_flow(session, ticker),
                    self._fetch_events(session, ticker),
                    self._fetch_recent_signals(session, ticker),
                    return_exceptions=True
                )
            
            # Process results
            sentiment_data = results[0] if not isinstance(results[0], Exception) else {}
            options_data = results[1] if not isinstance(results[1], Exception) else {}
            events_data = results[2] if not isinstance(results[2], Exception) else []
            signals_data = results[3] if not isinstance(results[3], Exception) else []
            
            # Calculate composite score
            composite_score = self._calculate_composite_score(
                sentiment_data, options_data, events_data, signals_data
            )
            
            # Determine recommendation
            recommendation = self._generate_recommendation(
                ticker, composite_score, sentiment_data, options_data, events_data
            )
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "composite_score": composite_score,
                    "sentiment": self._format_sentiment(sentiment_data),
                    "options_flow": self._format_options(options_data),
                    "upcoming_events": events_data[:3] if events_data else [],
                    "recent_signals_count": len(signals_data),
                    "hub_status": "connected",
                    "data_freshness": "real-time"
                },
                "confidence": self._calculate_confidence(composite_score, sentiment_data, options_data)
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            logger.error(f"Hub signal analysis failed for {ticker}: {e}")
            return self._get_fallback_result(ticker, str(e))
    
    async def _check_hub_health(self, session: aiohttp.ClientSession) -> bool:
        """Check if Hub is available"""
        try:
            async with session.get(f"{self.hub_url}/health") as resp:
                return resp.status == 200
        except:
            return False
    
    async def _fetch_sentiment(self, session: aiohttp.ClientSession, ticker: str) -> Dict:
        """Fetch multi-source sentiment from Hub"""
        try:
            async with session.get(f"{self.hub_url}/sentiment/{ticker}") as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.debug(f"Sentiment fetch failed for {ticker}: {e}")
        return {}
    
    async def _fetch_options_flow(self, session: aiohttp.ClientSession, ticker: str) -> Dict:
        """Fetch options flow data"""
        # Get from recent signals filtered by ticker and type
        try:
            async with session.get(
                f"{self.hub_url}/signals",
                params={"limit": 50}
            ) as resp:
                if resp.status == 200:
                    signals = await resp.json()
                    # Filter for options signals for this ticker
                    options_signals = [
                        s for s in signals 
                        if s.get('symbol') == ticker and s.get('signal_type') == 'options'
                    ]
                    
                    if options_signals:
                        # Aggregate options signals
                        bullish = sum(1 for s in options_signals if s.get('action') == 'BUY')
                        bearish = sum(1 for s in options_signals if s.get('action') == 'SELL')
                        total = bullish + bearish
                        
                        return {
                            'symbol': ticker,
                            'bullish_flow': bullish,
                            'bearish_flow': bearish,
                            'net_sentiment': (bullish - bearish) / total if total > 0 else 0,
                            'signal_count': len(options_signals),
                            'signals': options_signals[:5]  # Top 5
                        }
        except Exception as e:
            logger.debug(f"Options flow fetch failed for {ticker}: {e}")
        return {}
    
    async def _fetch_events(self, session: aiohttp.ClientSession, ticker: str) -> List:
        """Fetch upcoming events relevant to ticker"""
        try:
            async with session.get(
                f"{self.hub_url}/events",
                params={"hours": 48}
            ) as resp:
                if resp.status == 200:
                    events = await resp.json()
                    # Filter for this ticker
                    ticker_events = [e for e in events if e.get("symbol") == ticker]
                    return ticker_events
        except Exception as e:
            logger.debug(f"Events fetch failed for {ticker}: {e}")
        return []
    
    async def _fetch_recent_signals(self, session: aiohttp.ClientSession, ticker: str) -> List:
        """Fetch recent signals for ticker"""
        try:
            async with session.get(
                f"{self.hub_url}/signals",
                params={"limit": 100}
            ) as resp:
                if resp.status == 200:
                    signals = await resp.json()
                    return [s for s in signals if s.get("symbol") == ticker]
        except Exception as e:
            logger.debug(f"Signals fetch failed for {ticker}: {e}")
        return []
    
    def _calculate_composite_score(
        self, 
        sentiment: Dict, 
        options: Dict, 
        events: List,
        signals: List
    ) -> float:
        """
        Calculate weighted composite score from all sources
        Returns -1 (strong sell) to +1 (strong buy)
        """
        score = 0.0
        weights_used = 0.0
        
        # Sentiment contribution
        if sentiment:
            sent_score = sentiment.get("score", 0)
            sent_conf = sentiment.get("overall_confidence", sentiment.get("confidence", 0.5))
            score += sent_score * sent_conf * self.signal_weights["sentiment"]
            weights_used += self.signal_weights["sentiment"]
        
        # Options flow contribution
        if options and options.get('net_sentiment') is not None:
            opt_sentiment = options.get("net_sentiment", 0)
            score += opt_sentiment * self.signal_weights["options_flow"]
            weights_used += self.signal_weights["options_flow"]
        
        # Events contribution (upcoming high-impact catalysts = slightly bullish bias)
        if events:
            high_impact_events = sum(1 for e in events if e.get("impact") == "high")
            event_score = min(0.3, high_impact_events * 0.1)  # Cap at 0.3
            score += event_score * self.signal_weights["events"]
            weights_used += self.signal_weights["events"]
        
        # Recent signals contribution
        if signals:
            buy_signals = sum(1 for s in signals if s.get("action") == "BUY")
            sell_signals = sum(1 for s in signals if s.get("action") == "SELL")
            total_directional = buy_signals + sell_signals
            
            if total_directional > 0:
                signal_score = (buy_signals - sell_signals) / total_directional
                score += signal_score * self.signal_weights["recent_signals"]
                weights_used += self.signal_weights["recent_signals"]
        
        # Normalize by weights used
        if weights_used > 0:
            score = score / weights_used
        
        return max(-1.0, min(1.0, score))
    
    def _calculate_confidence(
        self,
        composite_score: float,
        sentiment: Dict,
        options: Dict
    ) -> float:
        """Calculate confidence in the signal"""
        base_confidence = abs(composite_score)
        
        # Boost confidence if we have multiple sources agreeing
        sources = 0
        if sentiment:
            sources += 1
        if options and options.get('signal_count', 0) > 0:
            sources += 1
        
        # Multi-source boost
        if sources >= 2:
            base_confidence *= 1.2
        
        # Sentiment confidence integration
        if sentiment:
            sent_conf = sentiment.get('overall_confidence', sentiment.get('confidence', 0.5))
            base_confidence = (base_confidence + sent_conf) / 2
        
        return min(1.0, base_confidence)
    
    def _generate_recommendation(
        self,
        ticker: str,
        composite_score: float,
        sentiment: Dict,
        options: Dict,
        events: List
    ) -> Dict:
        """Generate trading recommendation"""
        
        # Determine action based on score
        if composite_score > 0.4:
            action = "BUY"
        elif composite_score < -0.4:
            action = "SELL"
        else:
            action = "HOLD"
        
        # Build reasoning
        reasons = []
        
        if sentiment:
            sig = sentiment.get("signal", "NEUTRAL")
            sources = sentiment.get("sources", [])
            if sources:
                reasons.append(f"Multi-source sentiment ({len(sources)} sources): {sig}")
            else:
                reasons.append(f"Sentiment: {sig}")
        
        if options and options.get('signal_count', 0) > 0:
            net = options.get('net_sentiment', 0)
            flow_signal = "BULLISH" if net > 0.2 else "BEARISH" if net < -0.2 else "NEUTRAL"
            reasons.append(f"Options flow: {flow_signal} ({options['signal_count']} signals)")
        
        if events:
            high_impact = sum(1 for e in events if e.get("impact") == "high")
            if high_impact > 0:
                reasons.append(f"{high_impact} high-impact events in next 48h")
            elif events:
                reasons.append(f"{len(events)} upcoming events")
        
        # Timeframe based on event proximity
        if events and any(e.get('hours_until', 999) < 24 for e in events):
            timeframe = "short"
        else:
            timeframe = "medium"
        
        return {
            "action": action,
            "confidence": abs(composite_score),
            "timeframe": timeframe,
            "reasoning": "; ".join(reasons) if reasons else "Hub data aggregation",
            "composite_score": composite_score
        }
    
    def _format_sentiment(self, sentiment: Dict) -> Dict:
        """Format sentiment data for report"""
        if not sentiment:
            return {"status": "unavailable"}
        
        return {
            "score": sentiment.get("score", 0),
            "signal": sentiment.get("signal", "NEUTRAL"),
            "confidence": sentiment.get("overall_confidence", sentiment.get("confidence", 0.5)),
            "sources": sentiment.get("sources", []),
            "agreement": sentiment.get("agreement", 0)
        }
    
    def _format_options(self, options: Dict) -> Dict:
        """Format options data for report"""
        if not options:
            return {"status": "unavailable"}
        
        return {
            "net_sentiment": options.get("net_sentiment", 0),
            "bullish_count": options.get("bullish_flow", 0),
            "bearish_count": options.get("bearish_flow", 0),
            "signal_count": options.get("signal_count", 0)
        }
    
    def _get_fallback_result(self, ticker: str, error: str) -> Dict:
        """Generate fallback result when Hub is unavailable"""
        return {
            "recommendation": {
                "action": "HOLD",
                "confidence": 0.3,
                "timeframe": "medium",
                "reasoning": f"Hub unavailable: {error}"
            },
            "analysis": {
                "error": error,
                "hub_status": "disconnected",
                "composite_score": 0
            },
            "confidence": 0.3
        }


# Test function
async def test_hub_agent():
    """Test the Hub Signal Agent"""
    agent = HubSignalAgent()
    
    print("=" * 60)
    print("Testing Hub Signal Agent")
    print("=" * 60)
    
    for ticker in ["NVDA", "TSLA", "AAPL"]:
        print(f"\nAnalyzing {ticker}...")
        result = await agent._analyze_async(ticker, {})
        
        rec = result.get('recommendation', {})
        analysis = result.get('analysis', {})
        
        print(f"  Action: {rec.get('action', 'N/A')}")
        print(f"  Confidence: {rec.get('confidence', 0):.2f}")
        print(f"  Reasoning: {rec.get('reasoning', 'N/A')}")
        print(f"  Hub Status: {analysis.get('hub_status', 'unknown')}")
        print(f"  Composite Score: {analysis.get('composite_score', 0):.2f}")


if __name__ == "__main__":
    asyncio.run(test_hub_agent())
