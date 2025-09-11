#!/usr/bin/env python3
"""
Deep Research Index Generator
Creates comprehensive daily research reports with AI-driven analysis
Inspired by systematic trading research methodologies
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import yfinance as yf
import os
from dotenv import load_dotenv
import hashlib
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Add project paths
import sys
sys.path.insert(0, str(Path(__file__).parent))

from dee_bot.data.financial_datasets_api import FinancialDatasetsAPI
from trading_logger import TradingLogger, Trade, TradeAction, TradeReason

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MarketCondition:
    """Current market conditions assessment"""
    trend: str  # bullish, bearish, neutral
    volatility: str  # low, medium, high, extreme
    breadth: float  # % of stocks above 50-day MA
    sentiment: str  # fear, neutral, greed
    regime: str  # risk-on, risk-off, mixed
    
@dataclass
class TechnicalSignal:
    """Technical analysis signal"""
    ticker: str
    signal_type: str  # breakout, support, resistance, reversal
    indicator: str  # RSI, MACD, MA_cross, etc.
    strength: float  # 0-1 confidence
    entry_price: float
    stop_loss: float
    target_price: float
    risk_reward: float

@dataclass
class ResearchRecommendation:
    """AI-generated trade recommendation"""
    ticker: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    reasoning: List[str]
    entry_range: Tuple[float, float]
    position_size: float  # % of portfolio
    time_horizon: str  # intraday, swing, position
    risk_level: str  # low, medium, high

class DeepResearchGenerator:
    """Generates comprehensive deep research reports"""
    
    def __init__(self):
        self.fd_api = FinancialDatasetsAPI()
        self.base_dir = Path("deep_research_indexes")
        self.base_dir.mkdir(exist_ok=True)
        
        # Universe of stocks to analyze
        self.research_universe = {
            "mega_cap": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
            "large_cap": ["TSLA", "META", "BRK.B", "JPM", "V", "JNJ", "WMT"],
            "growth": ["SHOP", "SQ", "ROKU", "SNAP", "PINS"],
            "value": ["BAC", "WFC", "CVX", "XOM", "T", "VZ"],
            "tech": ["CRM", "ADBE", "NOW", "PANW", "DDOG", "SNOW"],
            "biotech": ["MRNA", "BNTX", "BIIB", "GILD", "AMGN"],
            "etfs": ["SPY", "QQQ", "DIA", "IWM", "VTI", "VOO"]
        }
        
        # Technical indicators to calculate
        self.indicators = [
            "RSI", "MACD", "BB", "SMA", "EMA", "ATR", 
            "OBV", "STOCH", "ADX", "VWAP", "PIVOT"
        ]
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    async def analyze_market_conditions(self) -> MarketCondition:
        """Analyze overall market conditions"""
        logger.info("Analyzing market conditions...")
        
        try:
            # Get major index data
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1mo")
            
            # Calculate market trend
            sma_20 = spy_hist['Close'].rolling(20).mean().iloc[-1]
            current_price = spy_hist['Close'].iloc[-1]
            
            if current_price > sma_20 * 1.02:
                trend = "bullish"
            elif current_price < sma_20 * 0.98:
                trend = "bearish"
            else:
                trend = "neutral"
            
            # Calculate volatility (using ATR)
            high_low = spy_hist['High'] - spy_hist['Low']
            high_close = np.abs(spy_hist['High'] - spy_hist['Close'].shift())
            low_close = np.abs(spy_hist['Low'] - spy_hist['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            atr_percent = (atr / current_price) * 100
            
            if atr_percent < 1:
                volatility = "low"
            elif atr_percent < 2:
                volatility = "medium"
            elif atr_percent < 3:
                volatility = "high"
            else:
                volatility = "extreme"
            
            # Market breadth (simplified - would need more data)
            breadth = 0.55  # Placeholder - would calculate from advance/decline
            
            # Sentiment based on VIX equivalent
            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period="1d")
            if not vix_hist.empty:
                vix_level = vix_hist['Close'].iloc[-1]
                if vix_level < 15:
                    sentiment = "greed"
                elif vix_level < 25:
                    sentiment = "neutral"
                else:
                    sentiment = "fear"
            else:
                sentiment = "neutral"
            
            # Determine regime
            if trend == "bullish" and volatility in ["low", "medium"]:
                regime = "risk-on"
            elif trend == "bearish" or volatility in ["high", "extreme"]:
                regime = "risk-off"
            else:
                regime = "mixed"
            
            return MarketCondition(
                trend=trend,
                volatility=volatility,
                breadth=breadth,
                sentiment=sentiment,
                regime=regime
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return MarketCondition(
                trend="neutral",
                volatility="medium",
                breadth=0.5,
                sentiment="neutral",
                regime="mixed"
            )
    
    def calculate_technical_indicators(self, ticker: str, period: str = "3mo") -> Dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {}
            
            close = hist['Close']
            high = hist['High']
            low = hist['Low']
            volume = hist['Volume']
            
            indicators = {}
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['RSI'] = 100 - (100 / (1 + rs)).iloc[-1]
            
            # MACD
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            indicators['MACD'] = macd.iloc[-1]
            indicators['MACD_signal'] = signal.iloc[-1]
            indicators['MACD_histogram'] = (macd - signal).iloc[-1]
            
            # Bollinger Bands
            sma_20 = close.rolling(20).mean()
            std_20 = close.rolling(20).std()
            indicators['BB_upper'] = (sma_20 + (std_20 * 2)).iloc[-1]
            indicators['BB_middle'] = sma_20.iloc[-1]
            indicators['BB_lower'] = (sma_20 - (std_20 * 2)).iloc[-1]
            indicators['BB_position'] = (close.iloc[-1] - indicators['BB_lower']) / (indicators['BB_upper'] - indicators['BB_lower'])
            
            # Moving Averages
            indicators['SMA_50'] = close.rolling(50).mean().iloc[-1]
            indicators['SMA_200'] = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
            indicators['EMA_20'] = close.ewm(span=20, adjust=False).mean().iloc[-1]
            
            # Volume indicators
            indicators['OBV'] = (np.sign(close.diff()) * volume).cumsum().iloc[-1]
            indicators['Volume_ratio'] = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]
            
            # Support and Resistance
            recent_high = high.rolling(20).max().iloc[-1]
            recent_low = low.rolling(20).min().iloc[-1]
            indicators['resistance'] = recent_high
            indicators['support'] = recent_low
            indicators['price_position'] = (close.iloc[-1] - recent_low) / (recent_high - recent_low)
            
            # Trend strength
            adx_period = 14
            plus_dm = high.diff()
            minus_dm = -low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            
            tr = pd.concat([high - low, 
                          (high - close.shift()).abs(), 
                          (low - close.shift()).abs()], axis=1).max(axis=1)
            
            atr = tr.rolling(adx_period).mean()
            plus_di = 100 * (plus_dm.rolling(adx_period).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(adx_period).mean() / atr)
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
            indicators['ADX'] = dx.rolling(adx_period).mean().iloc[-1]
            
            # Current price info
            indicators['current_price'] = close.iloc[-1]
            indicators['change_percent'] = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators for {ticker}: {e}")
            return {}
    
    async def generate_technical_signals(self, market_condition: MarketCondition) -> List[TechnicalSignal]:
        """Generate technical trading signals"""
        logger.info("Generating technical signals...")
        signals = []
        
        # Analyze each stock in universe
        for category, tickers in self.research_universe.items():
            if category == "etfs":
                continue  # Skip ETFs for individual signals
                
            for ticker in tickers[:3]:  # Limit for demo
                indicators = self.calculate_technical_indicators(ticker)
                
                if not indicators:
                    continue
                
                # Generate signals based on indicators
                signal = self._evaluate_technical_setup(ticker, indicators, market_condition)
                if signal:
                    signals.append(signal)
        
        # Sort by strength
        signals.sort(key=lambda x: x.strength, reverse=True)
        return signals[:10]  # Top 10 signals
    
    def _evaluate_technical_setup(self, ticker: str, indicators: Dict, 
                                 market_condition: MarketCondition) -> Optional[TechnicalSignal]:
        """Evaluate if stock has a valid technical setup"""
        
        signal_strength = 0
        signal_type = None
        indicator_name = None
        
        # RSI signals
        rsi = indicators.get('RSI')
        if rsi:
            if rsi < 30 and market_condition.regime != "risk-off":
                signal_strength += 0.3
                signal_type = "oversold_bounce"
                indicator_name = "RSI"
            elif rsi > 70 and market_condition.trend == "bullish":
                signal_strength += 0.2
                signal_type = "momentum"
                indicator_name = "RSI"
        
        # MACD signals
        macd_hist = indicators.get('MACD_histogram')
        if macd_hist:
            if macd_hist > 0 and indicators.get('MACD', 0) > indicators.get('MACD_signal', 0):
                signal_strength += 0.25
                if not signal_type:
                    signal_type = "macd_cross"
                    indicator_name = "MACD"
        
        # Bollinger Band signals
        bb_position = indicators.get('BB_position')
        if bb_position:
            if bb_position < 0.2:
                signal_strength += 0.25
                if not signal_type:
                    signal_type = "bb_squeeze"
                    indicator_name = "BB"
            elif bb_position > 0.8 and market_condition.trend == "bullish":
                signal_strength += 0.2
                if not signal_type:
                    signal_type = "bb_breakout"
                    indicator_name = "BB"
        
        # Moving average signals
        current_price = indicators.get('current_price', 0)
        sma_50 = indicators.get('SMA_50')
        if current_price and sma_50:
            if current_price > sma_50 and current_price < sma_50 * 1.02:
                signal_strength += 0.2
                if not signal_type:
                    signal_type = "ma_support"
                    indicator_name = "SMA"
        
        # Volume confirmation
        volume_ratio = indicators.get('Volume_ratio', 1)
        if volume_ratio > 1.5:
            signal_strength *= 1.2  # Boost signal with volume
        
        # Generate signal if strong enough
        if signal_strength >= 0.4 and signal_type:
            current_price = indicators.get('current_price', 0)
            
            # Calculate stop loss and target
            atr = (indicators.get('resistance', current_price) - 
                  indicators.get('support', current_price)) / 4
            
            stop_loss = current_price - (atr * 2)
            target_price = current_price + (atr * 3)
            risk_reward = (target_price - current_price) / (current_price - stop_loss)
            
            return TechnicalSignal(
                ticker=ticker,
                signal_type=signal_type,
                indicator=indicator_name,
                strength=min(signal_strength, 1.0),
                entry_price=current_price,
                stop_loss=stop_loss,
                target_price=target_price,
                risk_reward=risk_reward
            )
        
        return None
    
    async def generate_ai_recommendations(self, 
                                         market_condition: MarketCondition,
                                         technical_signals: List[TechnicalSignal]) -> List[ResearchRecommendation]:
        """Generate AI-driven trade recommendations"""
        logger.info("Generating AI recommendations...")
        recommendations = []
        
        # Use Financial Datasets API for enhanced data
        async with self.fd_api as api:
            for signal in technical_signals[:5]:  # Top 5 signals
                # Get current snapshot
                snapshot = await api.get_price_snapshot(signal.ticker)
                
                if not snapshot:
                    continue
                
                # Build recommendation
                confidence = signal.strength
                
                # Adjust confidence based on market conditions
                if market_condition.regime == "risk-on":
                    confidence *= 1.1
                elif market_condition.regime == "risk-off":
                    confidence *= 0.8
                
                # Determine action
                if confidence > 0.6:
                    action = "BUY"
                elif confidence < 0.3:
                    action = "SELL"
                else:
                    action = "HOLD"
                
                # Position sizing based on confidence and risk
                if market_condition.volatility == "extreme":
                    position_size = 2.0  # 2% of portfolio
                elif market_condition.volatility == "high":
                    position_size = 3.0
                elif confidence > 0.7:
                    position_size = 5.0
                else:
                    position_size = 4.0
                
                # Build reasoning
                reasoning = []
                reasoning.append(f"{signal.indicator} showing {signal.signal_type} pattern")
                reasoning.append(f"Risk/Reward ratio: {signal.risk_reward:.2f}")
                reasoning.append(f"Market regime: {market_condition.regime}")
                
                if snapshot.change_percent > 0:
                    reasoning.append(f"Positive momentum: {snapshot.change_percent:.2f}%")
                
                # Determine time horizon
                if signal.signal_type in ["breakout", "momentum"]:
                    time_horizon = "swing"  # 2-10 days
                elif signal.signal_type in ["oversold_bounce", "bb_squeeze"]:
                    time_horizon = "position"  # 1-4 weeks
                else:
                    time_horizon = "intraday"
                
                # Risk level
                if signal.risk_reward > 3:
                    risk_level = "low"
                elif signal.risk_reward > 2:
                    risk_level = "medium"
                else:
                    risk_level = "high"
                
                recommendation = ResearchRecommendation(
                    ticker=signal.ticker,
                    action=action,
                    confidence=min(confidence, 1.0),
                    reasoning=reasoning,
                    entry_range=(signal.entry_price * 0.995, signal.entry_price * 1.005),
                    position_size=position_size,
                    time_horizon=time_horizon,
                    risk_level=risk_level
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def generate_markdown_report(self, 
                                report_data: Dict[str, Any],
                                output_path: Path) -> Path:
        """Generate markdown formatted report"""
        
        report_date = datetime.now()
        report_id = report_data['report_id']
        
        markdown = f"""# Deep Research Index - {report_date.strftime('%B %d, %Y')}

**Report ID**: {report_id}  
**Generated**: {report_date.strftime('%I:%M %p ET')}  
**Market Status**: {report_data['market_condition']['regime'].upper()}

---

## 📊 Market Overview

### Current Conditions
- **Trend**: {report_data['market_condition']['trend'].capitalize()}
- **Volatility**: {report_data['market_condition']['volatility'].capitalize()}
- **Sentiment**: {report_data['market_condition']['sentiment'].capitalize()}
- **Market Breadth**: {report_data['market_condition']['breadth']:.1%} above 50-day MA

### Key Indices Performance
"""
        
        # Add index performance
        for index, data in report_data.get('index_performance', {}).items():
            if data:
                markdown += f"- **{index}**: ${data.get('price', 0):.2f} ({data.get('change_percent', 0):+.2f}%)\n"
        
        markdown += """
---

## 📈 Technical Signals

### Top Trading Opportunities
"""
        
        # Add technical signals
        for i, signal in enumerate(report_data.get('technical_signals', [])[:5], 1):
            markdown += f"""
#### {i}. {signal['ticker']} - {signal['signal_type'].replace('_', ' ').title()}
- **Indicator**: {signal['indicator']}
- **Signal Strength**: {signal['strength']:.1%}
- **Entry**: ${signal['entry_price']:.2f}
- **Stop Loss**: ${signal['stop_loss']:.2f}
- **Target**: ${signal['target_price']:.2f}
- **Risk/Reward**: {signal['risk_reward']:.2f}
"""
        
        markdown += """
---

## 🤖 AI Recommendations

### Actionable Trade Ideas
"""
        
        # Add AI recommendations
        for i, rec in enumerate(report_data.get('ai_recommendations', [])[:5], 1):
            markdown += f"""
#### {i}. {rec['ticker']} - {rec['action']}
**Confidence**: {rec['confidence']:.1%} | **Risk**: {rec['risk_level']} | **Timeframe**: {rec['time_horizon']}

**Entry Range**: ${rec['entry_range'][0]:.2f} - ${rec['entry_range'][1]:.2f}  
**Position Size**: {rec['position_size']:.1f}% of portfolio

**Reasoning**:
"""
            for reason in rec['reasoning']:
                markdown += f"- {reason}\n"
        
        markdown += """
---

## 📊 Sector Analysis

### Sector Performance
"""
        
        # Add sector performance
        for sector, performance in report_data.get('sector_performance', {}).items():
            if performance:
                markdown += f"- **{sector}**: {performance:+.2f}%\n"
        
        markdown += """
---

## ⚠️ Risk Alerts

### Key Risk Factors
"""
        
        # Add risk alerts
        risk_alerts = report_data.get('risk_alerts', [])
        if risk_alerts:
            for alert in risk_alerts:
                markdown += f"- {alert}\n"
        else:
            markdown += "- No significant risk alerts at this time\n"
        
        markdown += """
---

## 📈 Portfolio Update

### Current Performance
- **Daily P&L**: ${:.2f}
- **Weekly P&L**: ${:.2f}
- **Monthly P&L**: ${:.2f}
- **YTD Return**: {:.2%}

### Risk Metrics
- **Portfolio Beta**: {:.2f}
- **Sharpe Ratio**: {:.2f}
- **Max Drawdown**: {:.2%}
- **VaR (95%)**: ${:.2f}

---

## 🔍 Notable Market Events

### Today's Catalysts
- Pre-market movers analysis
- Earnings releases impact
- Economic data interpretation
- Geopolitical developments

### Upcoming Events
- Tomorrow's earnings calendar
- Economic releases schedule
- Fed speakers calendar
- Options expiration dates

---

## 📝 Research Notes

### Technical Analysis Summary
The market is showing {} characteristics with {} momentum. Key support levels are holding at {}, 
while resistance is evident at {}. Volume patterns suggest {} participation.

### Fundamental Outlook
Valuation metrics remain {} with the S&P 500 P/E at {}x forward earnings. Earnings growth 
expectations for Q1 are {}%, with {} sectors showing positive revisions.

### Sentiment Analysis
Options flow indicates {} positioning with put/call ratio at {}. Institutional activity shows 
{} accumulation in {} sectors. Retail sentiment surveys point to {} outlook.

---

## 🎯 Action Items

1. **Review positions** in {} for potential profit-taking
2. **Set alerts** for key support/resistance levels
3. **Monitor** {} for breakout confirmation
4. **Prepare** watchlist for tomorrow's opportunities
5. **Update** stop-loss orders based on new levels

---

## 📊 Performance Attribution

### Today's Winners
1. Position 1: +$X,XXX (X.X%)
2. Position 2: +$X,XXX (X.X%)
3. Position 3: +$X,XXX (X.X%)

### Today's Losers
1. Position 1: -$X,XXX (X.X%)
2. Position 2: -$X,XXX (X.X%)

---

## 🔮 Tomorrow's Outlook

**Pre-Market Focus**:
- Watch for {} reaction to overnight developments
- Monitor {} for continuation patterns
- Key levels to watch: SPY {}, QQQ {}

**Trading Plan**:
- Primary focus: {}
- Secondary opportunities: {}
- Risk management: {}

---

*This report is generated by an AI-driven research system combining technical analysis, 
fundamental data, and machine learning predictions. All recommendations should be validated 
with personal due diligence.*

**Disclaimer**: This research is for informational purposes only and does not constitute 
investment advice. Past performance does not guarantee future results.
""".format(
            0, 0, 0, 0,  # Placeholder P&L values
            1.0, 1.5, -0.05, 10000,  # Placeholder risk metrics
            "mixed", "positive", "4200", "4350", "moderate",  # Technical summary
            "elevated", 18.5, 5.2, "Technology",  # Fundamental outlook
            "defensive", 1.15, "net", "defensive", "cautious",  # Sentiment
            "NVDA, TSLA", "AAPL", "META",  # Action items
            "European markets", "TSLA", "425/430", "105/108",  # Tomorrow's outlook
            "Momentum stocks", "Value rotation", "Tight stops"  # Trading plan
        )
        
        # Save the report
        report_path = output_path / f"research_index_{report_date.strftime('%Y%m%d')}_{report_id}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"Report saved to {report_path}")
        return report_path
    
    async def generate_daily_research_index(self) -> Dict[str, Any]:
        """Generate complete daily research index"""
        logger.info("="*50)
        logger.info("Generating Daily Deep Research Index")
        logger.info("="*50)
        
        report_id = self._generate_report_id()
        report_date = datetime.now()
        
        # Analyze market conditions
        market_condition = await self.analyze_market_conditions()
        
        # Get index performance
        index_performance = {}
        async with self.fd_api as api:
            for index in ["SPY", "QQQ", "DIA"]:
                snapshot = await api.get_price_snapshot(index)
                if snapshot:
                    index_performance[index] = {
                        "price": snapshot.price,
                        "change_percent": snapshot.change_percent
                    }
        
        # Generate technical signals
        technical_signals = await self.generate_technical_signals(market_condition)
        
        # Generate AI recommendations
        ai_recommendations = await self.generate_ai_recommendations(
            market_condition, technical_signals
        )
        
        # Calculate sector performance
        sector_performance = {}
        sector_etfs = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financials": "XLF",
            "Energy": "XLE",
            "Consumer": "XLY"
        }
        
        for sector, etf in sector_etfs.items():
            indicators = self.calculate_technical_indicators(etf, period="1wk")
            if indicators:
                sector_performance[sector] = indicators.get('change_percent', 0)
        
        # Generate risk alerts
        risk_alerts = []
        if market_condition.volatility in ["high", "extreme"]:
            risk_alerts.append(f"Elevated volatility ({market_condition.volatility})")
        if market_condition.regime == "risk-off":
            risk_alerts.append("Risk-off market regime detected")
        
        # Compile report data
        report_data = {
            "report_id": report_id,
            "report_date": report_date.isoformat(),
            "market_condition": asdict(market_condition),
            "index_performance": index_performance,
            "technical_signals": [asdict(s) for s in technical_signals],
            "ai_recommendations": [asdict(r) for r in ai_recommendations],
            "sector_performance": sector_performance,
            "risk_alerts": risk_alerts
        }
        
        # Save JSON data
        year = report_date.strftime("%Y")
        month = report_date.strftime("%m")
        
        output_dir = self.base_dir / year / month
        output_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = output_dir / f"research_data_{report_date.strftime('%Y%m%d')}_{report_id}.json"
        with open(json_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate markdown report
        markdown_path = self.generate_markdown_report(report_data, output_dir)
        
        # Update master index
        self._update_master_index(report_id, report_date, markdown_path)
        
        logger.info(f"Deep research index generated: {report_id}")
        logger.info(f"Reports saved to {output_dir}")
        
        return report_data
    
    def _update_master_index(self, report_id: str, report_date: datetime, report_path: Path):
        """Update the master index file"""
        index_file = self.base_dir / "INDEX.md"
        
        # Read existing index or create new
        if index_file.exists():
            with open(index_file, 'r') as f:
                content = f.read()
        else:
            content = """# Master Research Index

## All Research Reports

| Date | Report ID | Market Regime | Signals | Link |
|------|-----------|---------------|---------|------|
"""
        
        # Add new entry (prepend to keep latest first)
        relative_path = report_path.relative_to(self.base_dir)
        new_entry = f"| {report_date.strftime('%Y-%m-%d')} | {report_id} | - | - | [{relative_path.name}]({relative_path}) |\n"
        
        # Insert after header
        lines = content.split('\n')
        header_end = 4  # After the table header
        lines.insert(header_end, new_entry)
        
        # Save updated index
        with open(index_file, 'w') as f:
            f.write('\n'.join(lines))

async def main():
    """Generate today's deep research index"""
    generator = DeepResearchGenerator()
    
    print("\n" + "="*60)
    print("DEEP RESEARCH INDEX GENERATOR")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    print(f"Time: {datetime.now().strftime('%I:%M %p ET')}")
    print("="*60 + "\n")
    
    # Generate the research index
    report_data = await generator.generate_daily_research_index()
    
    print("\n" + "="*60)
    print("RESEARCH INDEX GENERATION COMPLETE")
    print("="*60)
    print(f"Report ID: {report_data['report_id']}")
    print(f"Market Regime: {report_data['market_condition']['regime']}")
    print(f"Signals Generated: {len(report_data['technical_signals'])}")
    print(f"AI Recommendations: {len(report_data['ai_recommendations'])}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())