"""
Technical Analyst Agent
Performs technical analysis using indicators and chart patterns
"""

from .base_agent import BaseAgent
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import logging
import sys
import os

# Import Financial Datasets API (primary data source)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'automation'))
try:
    from financial_datasets_integration import FinancialDatasetsAPI
    FD_API_AVAILABLE = True
except ImportError:
    FD_API_AVAILABLE = False

class TechnicalAnalystAgent(BaseAgent):
    """
    Analyzes technical indicators and chart patterns for trading signals
    """
    
    def __init__(self):
        super().__init__(
            agent_id="technical_analyst_001",
            agent_type="technical_analyst"
        )
        
        # Initialize Financial Datasets API
        if FD_API_AVAILABLE:
            self.fd_api = FinancialDatasetsAPI()
        else:
            self.fd_api = None
            self.logger.warning("Financial Datasets API not available")
        
        # Indicator thresholds
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.volume_surge_threshold = 2.0  # 2x average volume
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Perform technical analysis on the stock
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            
        Returns:
            Technical analysis and recommendation
        """
        try:
            # Get historical data from Financial Datasets API
            if self.fd_api:
                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                hist = self.fd_api.get_historical_prices(ticker, interval='day', start_date=start_date, end_date=end_date)
                
                # Normalize column names to match expected format (capitalize for consistency)
                if not hist.empty:
                    hist.columns = [col.capitalize() for col in hist.columns]
            else:
                hist = pd.DataFrame()
            
            if hist.empty:
                return self._generate_error_result("No historical data available from Financial Datasets API")
            
            # Calculate technical indicators
            indicators = self._calculate_indicators(hist)
            
            # Detect chart patterns
            patterns = self._detect_patterns(hist)
            
            # Analyze trend
            trend_analysis = self._analyze_trend(hist, indicators)
            
            # Generate signals
            signals = self._generate_signals(indicators, patterns, trend_analysis)
            
            # Calculate technical score
            technical_score = self._calculate_technical_score(signals, indicators)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(technical_score, signals, trend_analysis)
            
            # Risk assessment
            risk_assessment = self._assess_technical_risk(hist, indicators)
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "technical_score": technical_score,
                    "indicators": self._format_indicators(indicators),
                    "patterns": patterns,
                    "trend": trend_analysis,
                    "signals": signals,
                    "key_factors": self._identify_key_factors(signals, indicators, patterns)
                },
                "risk_assessment": risk_assessment,
                "confidence": self._calculate_confidence(technical_score, signals)
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Technical analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _calculate_indicators(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        indicators = {}
        
        # Simple Moving Averages
        indicators['sma_20'] = hist['Close'].rolling(window=20).mean().iloc[-1]
        indicators['sma_50'] = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
        indicators['sma_200'] = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None
        
        # Exponential Moving Averages
        indicators['ema_12'] = hist['Close'].ewm(span=12, adjust=False).mean().iloc[-1]
        indicators['ema_26'] = hist['Close'].ewm(span=26, adjust=False).mean().iloc[-1]
        
        # MACD
        macd_line = hist['Close'].ewm(span=12, adjust=False).mean() - hist['Close'].ewm(span=26, adjust=False).mean()
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        indicators['macd'] = macd_line.iloc[-1]
        indicators['macd_signal'] = signal_line.iloc[-1]
        indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
        
        # RSI
        indicators['rsi'] = self._calculate_rsi(hist['Close'])
        
        # Bollinger Bands
        bb_sma = hist['Close'].rolling(window=20).mean()
        bb_std = hist['Close'].rolling(window=20).std()
        indicators['bb_upper'] = (bb_sma + (bb_std * 2)).iloc[-1]
        indicators['bb_middle'] = bb_sma.iloc[-1]
        indicators['bb_lower'] = (bb_sma - (bb_std * 2)).iloc[-1]
        indicators['bb_position'] = (hist['Close'].iloc[-1] - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
        
        # Stochastic Oscillator
        indicators['stoch_k'], indicators['stoch_d'] = self._calculate_stochastic(hist)
        
        # Volume indicators
        indicators['volume_sma'] = hist['Volume'].rolling(window=20).mean().iloc[-1]
        indicators['volume_ratio'] = hist['Volume'].iloc[-1] / indicators['volume_sma']
        indicators['obv'] = self._calculate_obv(hist)
        
        # ATR (Average True Range)
        indicators['atr'] = self._calculate_atr(hist)
        
        # Current price relative to indicators
        current_price = hist['Close'].iloc[-1]
        indicators['current_price'] = current_price
        indicators['price_vs_sma20'] = (current_price - indicators['sma_20']) / indicators['sma_20']
        
        return indicators
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_stochastic(self, hist: pd.DataFrame, period: int = 14) -> Tuple[float, float]:
        """Calculate Stochastic Oscillator"""
        low_min = hist['Low'].rolling(window=period).min()
        high_max = hist['High'].rolling(window=period).max()
        
        k = 100 * ((hist['Close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=3).mean()
        
        return k.iloc[-1], d.iloc[-1]
    
    def _calculate_obv(self, hist: pd.DataFrame) -> float:
        """Calculate On-Balance Volume"""
        obv = (np.sign(hist['Close'].diff()) * hist['Volume']).fillna(0).cumsum()
        return obv.iloc[-1]
    
    def _calculate_atr(self, hist: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high_low = hist['High'] - hist['Low']
        high_close = np.abs(hist['High'] - hist['Close'].shift())
        low_close = np.abs(hist['Low'] - hist['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr.iloc[-1]
    
    def _detect_patterns(self, hist: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect chart patterns"""
        patterns = []
        
        # Golden Cross / Death Cross
        if len(hist) >= 50:
            sma_50 = hist['Close'].rolling(window=50).mean()
            sma_200 = hist['Close'].rolling(window=200).mean() if len(hist) >= 200 else None
            
            if sma_200 is not None:
                # Check for crosses in last 5 days
                for i in range(-5, 0):
                    if i-1 >= -len(hist):
                        if sma_50.iloc[i-1] < sma_200.iloc[i-1] and sma_50.iloc[i] > sma_200.iloc[i]:
                            patterns.append({"type": "golden_cross", "strength": "strong", "days_ago": abs(i)})
                        elif sma_50.iloc[i-1] > sma_200.iloc[i-1] and sma_50.iloc[i] < sma_200.iloc[i]:
                            patterns.append({"type": "death_cross", "strength": "strong", "days_ago": abs(i)})
        
        # Support/Resistance breaks
        recent_high = hist['High'].rolling(window=20).max().iloc[-1]
        recent_low = hist['Low'].rolling(window=20).min().iloc[-1]
        current_price = hist['Close'].iloc[-1]
        
        if current_price > recent_high * 0.98:
            patterns.append({"type": "resistance_break", "strength": "medium", "level": recent_high})
        elif current_price < recent_low * 1.02:
            patterns.append({"type": "support_break", "strength": "medium", "level": recent_low})
            
        # Double top/bottom (simplified)
        peaks = self._find_peaks(hist['High'], window=10)
        troughs = self._find_troughs(hist['Low'], window=10)
        
        if len(peaks) >= 2 and abs(peaks[-1] - peaks[-2]) / peaks[-1] < 0.03:
            patterns.append({"type": "double_top", "strength": "medium"})
        if len(troughs) >= 2 and abs(troughs[-1] - troughs[-2]) / troughs[-1] < 0.03:
            patterns.append({"type": "double_bottom", "strength": "medium"})
            
        return patterns
    
    def _find_peaks(self, series: pd.Series, window: int = 10) -> List[float]:
        """Find local peaks in price series"""
        peaks = []
        for i in range(window, len(series) - window):
            if series.iloc[i] == series.iloc[i-window:i+window+1].max():
                peaks.append(series.iloc[i])
        return peaks[-5:] if peaks else []  # Return last 5 peaks
    
    def _find_troughs(self, series: pd.Series, window: int = 10) -> List[float]:
        """Find local troughs in price series"""
        troughs = []
        for i in range(window, len(series) - window):
            if series.iloc[i] == series.iloc[i-window:i+window+1].min():
                troughs.append(series.iloc[i])
        return troughs[-5:] if troughs else []  # Return last 5 troughs
    
    def _analyze_trend(self, hist: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price trend"""
        current_price = hist['Close'].iloc[-1]
        
        # Short-term trend (20 days)
        price_20d_ago = hist['Close'].iloc[-20] if len(hist) >= 20 else hist['Close'].iloc[0]
        short_trend = (current_price - price_20d_ago) / price_20d_ago
        
        # Medium-term trend (50 days)
        price_50d_ago = hist['Close'].iloc[-50] if len(hist) >= 50 else hist['Close'].iloc[0]
        medium_trend = (current_price - price_50d_ago) / price_50d_ago
        
        # Trend strength based on moving averages
        if indicators.get('sma_20') and indicators.get('sma_50'):
            if current_price > indicators['sma_20'] > indicators.get('sma_50', indicators['sma_20']):
                trend_strength = "strong_uptrend"
            elif current_price < indicators['sma_20'] < indicators.get('sma_50', indicators['sma_20']):
                trend_strength = "strong_downtrend"
            elif current_price > indicators['sma_20']:
                trend_strength = "uptrend"
            elif current_price < indicators['sma_20']:
                trend_strength = "downtrend"
            else:
                trend_strength = "sideways"
        else:
            trend_strength = "unknown"
            
        return {
            "short_term": short_trend,
            "medium_term": medium_trend,
            "strength": trend_strength,
            "momentum": indicators.get('macd_histogram', 0)
        }
    
    def _generate_signals(self, indicators: Dict[str, Any], patterns: List[Dict], 
                         trend: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals from indicators and patterns"""
        signals = {
            "bullish": [],
            "bearish": [],
            "neutral": []
        }
        
        # RSI signals
        rsi = indicators.get('rsi', 50)
        if rsi < self.rsi_oversold:
            signals["bullish"].append({"indicator": "RSI", "value": rsi, "signal": "oversold"})
        elif rsi > self.rsi_overbought:
            signals["bearish"].append({"indicator": "RSI", "value": rsi, "signal": "overbought"})
            
        # MACD signals
        if indicators.get('macd_histogram', 0) > 0:
            signals["bullish"].append({"indicator": "MACD", "value": indicators['macd_histogram'], "signal": "positive"})
        elif indicators.get('macd_histogram', 0) < 0:
            signals["bearish"].append({"indicator": "MACD", "value": indicators['macd_histogram'], "signal": "negative"})
            
        # Bollinger Band signals
        bb_position = indicators.get('bb_position', 0.5)
        if bb_position < 0.2:
            signals["bullish"].append({"indicator": "BB", "value": bb_position, "signal": "near_lower_band"})
        elif bb_position > 0.8:
            signals["bearish"].append({"indicator": "BB", "value": bb_position, "signal": "near_upper_band"})
            
        # Volume signals
        if indicators.get('volume_ratio', 1) > self.volume_surge_threshold:
            if trend['short_term'] > 0:
                signals["bullish"].append({"indicator": "Volume", "value": indicators['volume_ratio'], "signal": "surge_up"})
            else:
                signals["bearish"].append({"indicator": "Volume", "value": indicators['volume_ratio'], "signal": "surge_down"})
                
        # Pattern signals
        for pattern in patterns:
            if pattern['type'] in ['golden_cross', 'double_bottom', 'resistance_break']:
                signals["bullish"].append({"indicator": "Pattern", "value": pattern['type'], "signal": pattern['strength']})
            elif pattern['type'] in ['death_cross', 'double_top', 'support_break']:
                signals["bearish"].append({"indicator": "Pattern", "value": pattern['type'], "signal": pattern['strength']})
                
        return signals
    
    def _calculate_technical_score(self, signals: Dict[str, Any], indicators: Dict[str, Any]) -> float:
        """Calculate overall technical score"""
        bullish_count = len(signals.get("bullish", []))
        bearish_count = len(signals.get("bearish", []))
        
        # Base score from signal balance
        if bullish_count + bearish_count > 0:
            signal_score = bullish_count / (bullish_count + bearish_count)
        else:
            signal_score = 0.5
            
        # Adjust for trend alignment
        trend_adjustment = 0
        if indicators.get('price_vs_sma20', 0) > 0:
            trend_adjustment += 0.1
        if indicators.get('macd_histogram', 0) > 0:
            trend_adjustment += 0.1
            
        return min(1.0, max(0.0, signal_score + trend_adjustment))
    
    def _generate_recommendation(self, technical_score: float, signals: Dict[str, Any], 
                                trend: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading recommendation based on technical analysis"""
        
        bullish_signals = len(signals.get("bullish", []))
        bearish_signals = len(signals.get("bearish", []))
        
        # Determine action
        if technical_score > 0.65 and bullish_signals >= 3:
            action = "BUY"
            confidence = min(0.9, technical_score)
            timeframe = "short"  # Technical signals are short-term
        elif technical_score < 0.35 and bearish_signals >= 3:
            action = "SELL"
            confidence = min(0.9, 1 - technical_score)
            timeframe = "short"
        else:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
            
        # Adjust for strong trends
        if trend['strength'] == "strong_uptrend" and action != "SELL":
            action = "BUY"
            confidence = min(0.9, confidence + 0.1)
        elif trend['strength'] == "strong_downtrend" and action != "BUY":
            action = "SELL"
            confidence = min(0.9, confidence + 0.1)
            
        reasoning = self._generate_reasoning(technical_score, signals, trend)
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "reasoning": reasoning
        }
    
    def _assess_technical_risk(self, hist: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk based on technical indicators"""
        
        # Use ATR for volatility-based risk
        atr = indicators.get('atr', 0)
        current_price = hist['Close'].iloc[-1]
        
        if atr > 0:
            volatility_pct = atr / current_price
        else:
            volatility_pct = 0.02  # Default 2%
            
        # Risk level based on volatility
        if volatility_pct > 0.05:
            risk_level = "HIGH"
            stop_loss_multiplier = 2.5
        elif volatility_pct > 0.03:
            risk_level = "MEDIUM"
            stop_loss_multiplier = 2.0
        else:
            risk_level = "LOW"
            stop_loss_multiplier = 1.5
            
        stop_loss = current_price - (atr * stop_loss_multiplier)
        take_profit = current_price + (atr * stop_loss_multiplier * 1.5)
        
        # Position sizing based on volatility
        position_size = min(0.05, 0.02 / volatility_pct)
        
        return {
            "risk_level": risk_level,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size_pct": position_size,
            "volatility": volatility_pct
        }
    
    def _identify_key_factors(self, signals: Dict[str, Any], indicators: Dict[str, Any], 
                             patterns: List[Dict]) -> List[str]:
        """Identify key technical factors"""
        factors = []
        
        # Signal-based factors
        if len(signals.get("bullish", [])) >= 3:
            factors.append(f"{len(signals['bullish'])} bullish signals")
        if len(signals.get("bearish", [])) >= 3:
            factors.append(f"{len(signals['bearish'])} bearish signals")
            
        # Specific indicator callouts
        if indicators.get('rsi', 50) < 30:
            factors.append(f"RSI oversold ({indicators['rsi']:.1f})")
        elif indicators.get('rsi', 50) > 70:
            factors.append(f"RSI overbought ({indicators['rsi']:.1f})")
            
        # Pattern callouts
        for pattern in patterns[:2]:  # Top 2 patterns
            factors.append(f"{pattern['type'].replace('_', ' ').title()}")
            
        # Volume surge
        if indicators.get('volume_ratio', 1) > 2:
            factors.append(f"Volume surge ({indicators['volume_ratio']:.1f}x)")
            
        return factors
    
    def _calculate_confidence(self, technical_score: float, signals: Dict[str, Any]) -> float:
        """Calculate confidence in technical analysis"""
        total_signals = len(signals.get("bullish", [])) + len(signals.get("bearish", []))
        
        # More signals = higher confidence
        signal_confidence = min(1.0, total_signals / 5)
        
        # Combine with technical score
        return min(0.95, technical_score * 0.7 + signal_confidence * 0.3)
    
    def _generate_reasoning(self, score: float, signals: Dict[str, Any], trend: Dict[str, Any]) -> str:
        """Generate reasoning for recommendation"""
        reasons = []
        
        if score > 0.65:
            reasons.append("Strong technical setup")
        elif score > 0.35:
            reasons.append("Mixed technical signals")
        else:
            reasons.append("Weak technical setup")
            
        if trend['strength'] != "unknown":
            reasons.append(trend['strength'].replace('_', ' '))
            
        bullish_count = len(signals.get("bullish", []))
        bearish_count = len(signals.get("bearish", []))
        
        if bullish_count > bearish_count:
            reasons.append(f"{bullish_count} bullish indicators")
        elif bearish_count > bullish_count:
            reasons.append(f"{bearish_count} bearish indicators")
            
        return ", ".join(reasons)
    
    def _format_indicators(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Format indicators for output"""
        return {
            "rsi": indicators.get('rsi'),
            "macd": {
                "line": indicators.get('macd'),
                "signal": indicators.get('macd_signal'),
                "histogram": indicators.get('macd_histogram')
            },
            "moving_averages": {
                "sma_20": indicators.get('sma_20'),
                "sma_50": indicators.get('sma_50'),
                "sma_200": indicators.get('sma_200')
            },
            "bollinger_bands": {
                "upper": indicators.get('bb_upper'),
                "middle": indicators.get('bb_middle'),
                "lower": indicators.get('bb_lower'),
                "position": indicators.get('bb_position')
            },
            "volume": {
                "current": indicators.get('volume_ratio'),
                "obv": indicators.get('obv')
            },
            "volatility": {
                "atr": indicators.get('atr')
            }
        }
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "short"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "HIGH"},
            "confidence": 0.0
        }