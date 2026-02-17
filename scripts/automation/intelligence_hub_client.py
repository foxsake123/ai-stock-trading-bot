"""
Intelligence Hub Client
=======================
Fetches real-time signals from the Trading Intelligence Hub
for integration into Claude research generation.

Hub Endpoints:
- /signals - Recent trading signals
- /sentiment/{ticker} - Multi-source sentiment
- /events - Upcoming catalyst events
- /api/grok/analyze - Grok sentiment analysis
- /api/options/flow - Options flow data
- /api/whale/alerts - Whale activity alerts
"""

import aiohttp
import asyncio
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json


class IntelligenceHubClient:
    """
    Client for fetching data from the Trading Intelligence Hub.
    Designed to be used by the Claude Research Generator.
    """
    
    def __init__(self, hub_url: str = "http://localhost:8000"):
        self.hub_url = hub_url
        self.timeout = 10  # seconds
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache:
            return False
        cached_time, _ = self._cache[key]
        return (datetime.now() - cached_time).seconds < self._cache_ttl
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(key):
            return self._cache[key][1]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Cache data with timestamp"""
        self._cache[key] = (datetime.now(), data)
    
    def check_health(self) -> bool:
        """Check if Intelligence Hub is running"""
        try:
            resp = requests.get(f"{self.hub_url}/health", timeout=3)
            return resp.status_code == 200
        except:
            return False
    
    def get_recent_signals(self, limit: int = 50) -> List[Dict]:
        """
        Fetch recent trading signals from Hub.
        
        Returns:
            List of signal dicts with: source, signal_type, symbol, direction, confidence, etc.
        """
        cache_key = f"signals_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            resp = requests.get(
                f"{self.hub_url}/signals",
                params={"limit": limit},
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                self._set_cache(cache_key, data)
                return data
        except Exception as e:
            print(f"[!] Hub signals fetch failed: {e}")
        return []
    
    def get_sentiment(self, ticker: str) -> Dict:
        """
        Fetch multi-source sentiment for a ticker.
        
        Returns:
            Dict with sentiment scores from multiple sources
        """
        cache_key = f"sentiment_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            resp = requests.get(
                f"{self.hub_url}/sentiment/{ticker}",
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                self._set_cache(cache_key, data)
                return data
        except Exception as e:
            print(f"[!] Hub sentiment fetch failed for {ticker}: {e}")
        return {}
    
    def get_upcoming_events(self, hours: int = 48) -> List[Dict]:
        """
        Fetch upcoming catalyst events.
        
        Returns:
            List of event dicts with: symbol, event_type, datetime, impact, etc.
        """
        cache_key = f"events_{hours}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            resp = requests.get(
                f"{self.hub_url}/events",
                params={"hours": hours},
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                self._set_cache(cache_key, data)
                return data
        except Exception as e:
            print(f"[!] Hub events fetch failed: {e}")
        return []
    
    def get_grok_analysis(self, topic: str) -> Dict:
        """
        Get Grok's real-time market analysis.
        
        Args:
            topic: Topic to analyze (e.g., "market sentiment", "sector rotation", ticker)
            
        Returns:
            Dict with Grok's analysis and sentiment score
        """
        try:
            resp = requests.post(
                f"{self.hub_url}/api/grok/analyze",
                json={"topic": topic},
                timeout=30  # Grok can take longer
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[!] Grok analysis failed: {e}")
        return {}
    
    def get_options_flow(self, ticker: Optional[str] = None) -> List[Dict]:
        """
        Get unusual options flow activity.
        
        Returns:
            List of unusual options activity with: ticker, strike, expiry, volume, oi, direction
        """
        cache_key = f"options_{ticker or 'all'}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            params = {"ticker": ticker} if ticker else {}
            resp = requests.get(
                f"{self.hub_url}/api/options/flow",
                params=params,
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                self._set_cache(cache_key, data)
                return data
        except Exception as e:
            print(f"[!] Options flow fetch failed: {e}")
        return []
    
    def get_whale_alerts(self, hours: int = 24) -> List[Dict]:
        """
        Get recent whale activity alerts.
        
        Returns:
            List of whale alerts with: ticker, action, size, price, confidence
        """
        cache_key = f"whales_{hours}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            resp = requests.get(
                f"{self.hub_url}/api/whale/alerts",
                params={"hours": hours},
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                self._set_cache(cache_key, data)
                return data
        except Exception as e:
            print(f"[!] Whale alerts fetch failed: {e}")
        return []
    
    def get_market_summary(self) -> Dict:
        """
        Get comprehensive market summary from Hub.
        Combines multiple data sources into a single summary.
        
        Returns:
            Dict with: signals, sentiment, events, options_flow, whale_activity
        """
        hub_available = self.check_health()
        
        summary = {
            "hub_status": "connected" if hub_available else "disconnected",
            "timestamp": datetime.now().isoformat(),
            "signals": [],
            "top_bullish": [],
            "top_bearish": [],
            "upcoming_events": [],
            "options_flow": [],
            "whale_alerts": [],
            "grok_sentiment": {}
        }
        
        if not hub_available:
            print("[!] Intelligence Hub not available - research will use limited data")
            return summary
            
        print("[+] Intelligence Hub connected - fetching real-time data...")
        
        # Fetch all data
        signals = self.get_recent_signals(100)
        events = self.get_upcoming_events(72)
        options = self.get_options_flow()
        whales = self.get_whale_alerts(48)
        
        # Process signals into bullish/bearish
        bullish = [s for s in signals if s.get("direction") == "bullish"]
        bearish = [s for s in signals if s.get("direction") == "bearish"]
        
        summary["signals"] = signals[:20]
        summary["top_bullish"] = sorted(bullish, key=lambda x: x.get("confidence", 0), reverse=True)[:10]
        summary["top_bearish"] = sorted(bearish, key=lambda x: x.get("confidence", 0), reverse=True)[:10]
        summary["upcoming_events"] = events[:15]
        summary["options_flow"] = options[:15]
        summary["whale_alerts"] = whales[:10]
        
        # Get Grok market sentiment
        grok = self.get_grok_analysis("overall market sentiment and sector rotation signals")
        summary["grok_sentiment"] = grok
        
        print(f"    - {len(signals)} signals, {len(events)} events, {len(options)} options flow, {len(whales)} whale alerts")
        
        return summary
    
    def format_for_prompt(self, summary: Dict) -> str:
        """
        Format Hub data as a prompt section for Claude.
        
        Args:
            summary: Market summary from get_market_summary()
            
        Returns:
            Formatted string to inject into Claude prompt
        """
        if summary.get("hub_status") == "disconnected":
            return "\n[INTELLIGENCE HUB OFFLINE - Using limited data sources]\n"
        
        lines = [
            "\n## INTELLIGENCE HUB REAL-TIME DATA",
            f"### Retrieved: {summary.get('timestamp', 'N/A')}",
            ""
        ]
        
        # Top Bullish Signals
        if summary.get("top_bullish"):
            lines.append("### 🟢 TOP BULLISH SIGNALS")
            for sig in summary["top_bullish"][:5]:
                ticker = sig.get("symbol", "???")
                source = sig.get("source", "unknown")
                conf = sig.get("confidence", 0) * 100
                reason = sig.get("reason", "")[:100]
                lines.append(f"- **{ticker}** ({source}, {conf:.0f}%): {reason}")
            lines.append("")
        
        # Top Bearish Signals
        if summary.get("top_bearish"):
            lines.append("### 🔴 TOP BEARISH SIGNALS")
            for sig in summary["top_bearish"][:5]:
                ticker = sig.get("symbol", "???")
                source = sig.get("source", "unknown")
                conf = sig.get("confidence", 0) * 100
                reason = sig.get("reason", "")[:100]
                lines.append(f"- **{ticker}** ({source}, {conf:.0f}%): {reason}")
            lines.append("")
        
        # Upcoming Events
        if summary.get("upcoming_events"):
            lines.append("### 📅 UPCOMING CATALYSTS (Next 72h)")
            for evt in summary["upcoming_events"][:8]:
                ticker = evt.get("symbol", "???")
                event_type = evt.get("event_type", "event")
                dt = evt.get("datetime", "TBD")
                impact = evt.get("impact", "medium")
                lines.append(f"- **{ticker}** - {event_type} @ {dt} (Impact: {impact})")
            lines.append("")
        
        # Options Flow
        if summary.get("options_flow"):
            lines.append("### 📊 UNUSUAL OPTIONS ACTIVITY")
            for opt in summary["options_flow"][:5]:
                ticker = opt.get("ticker", "???")
                direction = opt.get("direction", "neutral")
                volume = opt.get("volume", 0)
                premium = opt.get("premium", 0)
                lines.append(f"- **{ticker}** {direction.upper()} - Vol: {volume:,}, Premium: ${premium:,.0f}")
            lines.append("")
        
        # Whale Alerts
        if summary.get("whale_alerts"):
            lines.append("### 🐋 WHALE ACTIVITY")
            for whale in summary["whale_alerts"][:5]:
                ticker = whale.get("ticker", "???")
                action = whale.get("action", "unknown")
                size = whale.get("size", 0)
                lines.append(f"- **{ticker}** - {action} ${size:,.0f}")
            lines.append("")
        
        # Grok Sentiment
        if summary.get("grok_sentiment"):
            grok = summary["grok_sentiment"]
            if grok.get("analysis"):
                lines.append("### 🤖 GROK MARKET ANALYSIS")
                lines.append(grok.get("analysis", "")[:500])
                lines.append("")
        
        lines.append("---\n")
        return "\n".join(lines)


# Singleton instance for easy import
_hub_client = None

def get_hub_client(hub_url: str = "http://localhost:8000") -> IntelligenceHubClient:
    """Get or create singleton Hub client"""
    global _hub_client
    if _hub_client is None:
        _hub_client = IntelligenceHubClient(hub_url)
    return _hub_client


if __name__ == "__main__":
    # Test the client
    client = IntelligenceHubClient()
    
    print("Testing Intelligence Hub Client...")
    print(f"Hub Status: {'Connected' if client.check_health() else 'Disconnected'}")
    
    summary = client.get_market_summary()
    print("\nMarket Summary:")
    print(f"  - Signals: {len(summary.get('signals', []))}")
    print(f"  - Events: {len(summary.get('upcoming_events', []))}")
    print(f"  - Options Flow: {len(summary.get('options_flow', []))}")
    print(f"  - Whale Alerts: {len(summary.get('whale_alerts', []))}")
    
    print("\nFormatted for Claude prompt:")
    print(client.format_for_prompt(summary))
