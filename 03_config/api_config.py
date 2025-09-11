"""
API Configuration for Enhanced Data Sources
Based on TradingAgents paper recommendations
"""

import os
from dotenv import load_dotenv

load_dotenv()

class APIConfig:
    """Centralized API configuration"""
    
    # Market Data APIs (Priority 1)
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')  # Real-time data
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')  # Backup
    IEX_CLOUD_TOKEN = os.getenv('IEX_CLOUD_TOKEN')  # Alternative
    
    # News APIs (Priority 2)
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')  # General news
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')  # Financial news
    BENZINGA_API_KEY = os.getenv('BENZINGA_API_KEY')  # Market news
    
    # Social Sentiment APIs (Priority 3)
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    STOCKTWITS_TOKEN = os.getenv('STOCKTWITS_TOKEN')
    
    # Economic Data (Priority 4)
    FRED_API_KEY = os.getenv('FRED_API_KEY')  # Federal Reserve data
    
    # Options Data (Priority 5)
    TRADIER_API_KEY = os.getenv('TRADIER_API_KEY')  # Options flow
    
    # Existing Broker APIs
    ALPACA_API_KEY_DEE = os.getenv('ALPACA_API_KEY_DEE')
    ALPACA_SECRET_KEY_DEE = os.getenv('ALPACA_SECRET_KEY_DEE')
    ALPACA_API_KEY_SHORGAN = os.getenv('ALPACA_API_KEY_SHORGAN')
    ALPACA_SECRET_KEY_SHORGAN = os.getenv('ALPACA_SECRET_KEY_SHORGAN')
    
    @classmethod
    def get_required_apis(cls):
        """Check which APIs are configured"""
        configured = []
        missing = []
        
        api_list = {
            'Polygon': cls.POLYGON_API_KEY,
            'NewsAPI': cls.NEWSAPI_KEY,
            'Reddit': cls.REDDIT_CLIENT_ID,
            'FRED': cls.FRED_API_KEY,
            'Alpaca': cls.ALPACA_API_KEY_DEE
        }
        
        for name, key in api_list.items():
            if key:
                configured.append(name)
            else:
                missing.append(name)
                
        return configured, missing
    
    @classmethod
    def validate_apis(cls):
        """Validate API configuration"""
        configured, missing = cls.get_required_apis()
        
        print("✅ Configured APIs:", configured)
        if missing:
            print("⚠️ Missing APIs (recommended):", missing)
            print("   Add these to your .env file for full functionality")
        
        return len(missing) == 0