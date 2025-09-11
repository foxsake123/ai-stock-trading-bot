"""
Stock Screener for Shorgan-Bot Strategy
Screens for micro-cap to mid-cap stocks with catalyst potential
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import requests
import json

class CatalystStockScreener:
    """
    Screens stocks based on market cap, volume, and catalyst potential
    Optimized for Shorgan-Bot's aggressive short-term strategy
    """
    
    def __init__(self):
        self.logger = logging.getLogger("screener.catalyst")
        
        # Screening criteria
        self.max_market_cap = 20_000_000_000  # $20B
        self.min_market_cap = 100_000_000     # $100M minimum
        self.min_volume = 100_000              # Minimum daily volume
        self.min_price = 1.0                   # Minimum stock price
        self.max_price = 500.0                 # Maximum stock price
        
        # Catalyst screening parameters
        self.volume_surge_threshold = 2.0      # 2x average volume
        self.price_move_threshold = 0.05       # 5% price move
        
    def screen_stocks(self, tickers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Screen stocks for catalyst opportunities
        
        Args:
            tickers: Optional list of tickers to screen. If None, uses default watchlist
            
        Returns:
            List of screened stocks with their metrics
        """
        if tickers is None:
            tickers = self._get_default_watchlist()
        
        screened_stocks = []
        
        for ticker in tickers:
            try:
                stock_data = self._analyze_stock(ticker)
                if stock_data and self._passes_screening(stock_data):
                    screened_stocks.append(stock_data)
                    self.logger.info(f"Stock {ticker} passed screening")
            except Exception as e:
                self.logger.warning(f"Error screening {ticker}: {str(e)}")
                continue
        
        # Sort by catalyst score
        screened_stocks.sort(key=lambda x: x.get('catalyst_score', 0), reverse=True)
        
        return screened_stocks
    
    def _analyze_stock(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Analyze individual stock for screening
        
        Returns:
            Stock data with analysis metrics or None if data unavailable
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get basic metrics
            market_cap = info.get('marketCap', 0)
            if market_cap == 0:
                # Try alternative calculation
                shares = info.get('sharesOutstanding', 0)
                price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                market_cap = shares * price
            
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
            volume = info.get('regularMarketVolume', info.get('volume', 0))
            avg_volume = info.get('averageDailyVolume10Day', info.get('averageVolume', 0))
            
            # Get historical data for additional metrics
            hist = stock.history(period="30d")
            if hist.empty:
                return None
            
            # Calculate technical indicators
            volume_surge = volume / avg_volume if avg_volume > 0 else 0
            price_change_1d = (current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] if len(hist) > 1 else 0
            price_change_5d = (current_price - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] if len(hist) >= 5 else 0
            
            # Calculate volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5) if len(returns) > 0 else 0
            
            # Calculate catalyst score
            catalyst_score = self._calculate_catalyst_score(
                volume_surge=volume_surge,
                price_change_1d=price_change_1d,
                price_change_5d=price_change_5d,
                volatility=volatility
            )
            
            return {
                'ticker': ticker,
                'market_cap': market_cap,
                'price': current_price,
                'volume': volume,
                'avg_volume': avg_volume,
                'volume_surge': volume_surge,
                'price_change_1d': price_change_1d,
                'price_change_5d': price_change_5d,
                'volatility': volatility,
                'catalyst_score': catalyst_score,
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'name': info.get('longName', ticker)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {ticker}: {str(e)}")
            return None
    
    def _passes_screening(self, stock_data: Dict[str, Any]) -> bool:
        """
        Check if stock passes screening criteria
        
        Args:
            stock_data: Stock analysis data
            
        Returns:
            True if stock passes all screening criteria
        """
        # Market cap filter
        if not (self.min_market_cap <= stock_data['market_cap'] <= self.max_market_cap):
            return False
        
        # Price filter
        if not (self.min_price <= stock_data['price'] <= self.max_price):
            return False
        
        # Volume filter
        if stock_data['volume'] < self.min_volume:
            return False
        
        # Catalyst score filter (require minimum score)
        if stock_data['catalyst_score'] < 0.3:
            return False
        
        return True
    
    def _calculate_catalyst_score(self, volume_surge: float, price_change_1d: float, 
                                 price_change_5d: float, volatility: float) -> float:
        """
        Calculate catalyst score based on technical indicators
        
        Returns:
            Catalyst score between 0 and 1
        """
        score = 0.0
        
        # Volume surge component (0-0.3)
        if volume_surge > self.volume_surge_threshold:
            score += min(0.3, (volume_surge - 1) * 0.15)
        
        # Price momentum component (0-0.3)
        if abs(price_change_1d) > self.price_move_threshold:
            score += min(0.3, abs(price_change_1d) * 3)
        
        # 5-day trend component (0-0.2)
        if price_change_5d > 0.1:  # 10% move in 5 days
            score += 0.2
        elif price_change_5d > 0.05:  # 5% move in 5 days
            score += 0.1
        
        # Volatility component (0-0.2)
        # Higher volatility can mean more opportunity
        if 0.3 < volatility < 0.8:
            score += 0.2
        elif 0.2 < volatility <= 0.3:
            score += 0.1
        
        return min(1.0, score)
    
    def _get_default_watchlist(self) -> List[str]:
        """
        Get default watchlist of high-potential micro/mid-cap stocks
        
        Returns:
            List of ticker symbols to screen
        """
        # High-momentum micro/mid-cap stocks
        watchlist = [
            # Technology/AI
            'PLTR', 'AI', 'BIGC', 'STEM', 'IONQ', 'RGTI', 'BBAI',
            
            # Biotech/Healthcare
            'SAVA', 'OCGN', 'BNGO', 'SENS', 'AGEN', 'NVAX', 'MRNA',
            
            # EVs and Clean Energy
            'LCID', 'RIVN', 'FSR', 'GOEV', 'CHPT', 'BLNK', 'PLUG',
            
            # Fintech
            'UPST', 'AFRM', 'HOOD', 'SOFI', 'DAVE', 'ML',
            
            # Consumer/Retail
            'CVNA', 'OPEN', 'WISH', 'REAL', 'APRN', 'BYND',
            
            # Gaming/Entertainment
            'DKNG', 'PENN', 'GENI', 'RSI', 'SKLZ',
            
            # Space/Defense
            'SPCE', 'RKLB', 'ASTR', 'RDW',
            
            # Crypto-related
            'MARA', 'RIOT', 'HIVE', 'BITF', 'HUT', 'COIN',
            
            # High volatility momentum plays
            'AMC', 'GME', 'BBBY', 'FFIE', 'MULN'
        ]
        
        return watchlist
    
    def get_hot_sectors(self) -> Dict[str, List[str]]:
        """
        Get currently hot sectors with momentum
        
        Returns:
            Dict of sector names to list of tickers
        """
        hot_sectors = {
            "AI_Technology": ['PLTR', 'AI', 'BIGC', 'IONQ', 'RGTI', 'BBAI'],
            "Biotech_Catalysts": ['SAVA', 'OCGN', 'BNGO', 'NVAX', 'MRNA'],
            "EV_CleanEnergy": ['LCID', 'RIVN', 'FSR', 'CHPT', 'PLUG'],
            "Fintech_Disruption": ['UPST', 'AFRM', 'HOOD', 'SOFI'],
            "Crypto_Mining": ['MARA', 'RIOT', 'HIVE', 'BITF', 'HUT'],
            "Meme_Momentum": ['AMC', 'GME', 'BBBY', 'FFIE']
        }
        
        return hot_sectors
    
    def screen_sector(self, sector_name: str) -> List[Dict[str, Any]]:
        """
        Screen stocks within a specific sector
        
        Args:
            sector_name: Name of sector to screen
            
        Returns:
            List of screened stocks in that sector
        """
        sectors = self.get_hot_sectors()
        
        if sector_name in sectors:
            return self.screen_stocks(sectors[sector_name])
        else:
            self.logger.warning(f"Unknown sector: {sector_name}")
            return []
    
    def find_volume_surges(self, min_surge: float = 3.0) -> List[Dict[str, Any]]:
        """
        Find stocks with significant volume surges
        
        Args:
            min_surge: Minimum volume surge multiplier
            
        Returns:
            List of stocks with volume surges
        """
        all_stocks = self.screen_stocks()
        
        # Filter for high volume surges
        surge_stocks = [
            stock for stock in all_stocks 
            if stock.get('volume_surge', 0) >= min_surge
        ]
        
        return surge_stocks
    
    def find_breakouts(self, min_move: float = 0.10) -> List[Dict[str, Any]]:
        """
        Find stocks breaking out with strong moves
        
        Args:
            min_move: Minimum price move percentage (e.g., 0.10 for 10%)
            
        Returns:
            List of breakout candidates
        """
        all_stocks = self.screen_stocks()
        
        # Filter for strong price moves
        breakout_stocks = [
            stock for stock in all_stocks
            if abs(stock.get('price_change_1d', 0)) >= min_move
        ]
        
        return breakout_stocks