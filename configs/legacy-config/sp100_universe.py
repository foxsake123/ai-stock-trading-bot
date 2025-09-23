"""
S&P 100 Universe Configuration for DEE-BOT
Updated: January 2025
"""

# S&P 100 constituents - Large-cap, highly liquid stocks
SP100_UNIVERSE = {
    # Technology (24 stocks)
    'AAPL': {'sector': 'Technology', 'name': 'Apple Inc.'},
    'MSFT': {'sector': 'Technology', 'name': 'Microsoft Corporation'},
    'NVDA': {'sector': 'Technology', 'name': 'NVIDIA Corporation'},
    'GOOGL': {'sector': 'Technology', 'name': 'Alphabet Inc. Class A'},
    'GOOG': {'sector': 'Technology', 'name': 'Alphabet Inc. Class C'},
    'META': {'sector': 'Technology', 'name': 'Meta Platforms Inc.'},
    'AVGO': {'sector': 'Technology', 'name': 'Broadcom Inc.'},
    'ORCL': {'sector': 'Technology', 'name': 'Oracle Corporation'},
    'CSCO': {'sector': 'Technology', 'name': 'Cisco Systems Inc.'},
    'ACN': {'sector': 'Technology', 'name': 'Accenture plc'},
    'CRM': {'sector': 'Technology', 'name': 'Salesforce Inc.'},
    'IBM': {'sector': 'Technology', 'name': 'International Business Machines'},
    'INTC': {'sector': 'Technology', 'name': 'Intel Corporation'},
    'AMD': {'sector': 'Technology', 'name': 'Advanced Micro Devices'},
    'QCOM': {'sector': 'Technology', 'name': 'QUALCOMM Inc.'},
    'TXN': {'sector': 'Technology', 'name': 'Texas Instruments'},
    'ADBE': {'sector': 'Technology', 'name': 'Adobe Inc.'},
    
    # Healthcare (14 stocks)
    'LLY': {'sector': 'Healthcare', 'name': 'Eli Lilly and Company'},
    'UNH': {'sector': 'Healthcare', 'name': 'UnitedHealth Group'},
    'JNJ': {'sector': 'Healthcare', 'name': 'Johnson & Johnson'},
    'PFE': {'sector': 'Healthcare', 'name': 'Pfizer Inc.'},
    'ABBV': {'sector': 'Healthcare', 'name': 'AbbVie Inc.'},
    'MRK': {'sector': 'Healthcare', 'name': 'Merck & Co.'},
    'TMO': {'sector': 'Healthcare', 'name': 'Thermo Fisher Scientific'},
    'ABT': {'sector': 'Healthcare', 'name': 'Abbott Laboratories'},
    'DHR': {'sector': 'Healthcare', 'name': 'Danaher Corporation'},
    'AMGN': {'sector': 'Healthcare', 'name': 'Amgen Inc.'},
    'CVS': {'sector': 'Healthcare', 'name': 'CVS Health Corporation'},
    'BMY': {'sector': 'Healthcare', 'name': 'Bristol-Myers Squibb'},
    'GILD': {'sector': 'Healthcare', 'name': 'Gilead Sciences'},
    'MDT': {'sector': 'Healthcare', 'name': 'Medtronic plc'},
    
    # Financials (17 stocks)
    'BRK.B': {'sector': 'Financials', 'name': 'Berkshire Hathaway Class B'},
    'JPM': {'sector': 'Financials', 'name': 'JPMorgan Chase & Co.'},
    'V': {'sector': 'Financials', 'name': 'Visa Inc.'},
    'MA': {'sector': 'Financials', 'name': 'Mastercard Inc.'},
    'BAC': {'sector': 'Financials', 'name': 'Bank of America'},
    'WFC': {'sector': 'Financials', 'name': 'Wells Fargo & Company'},
    'GS': {'sector': 'Financials', 'name': 'Goldman Sachs Group'},
    'MS': {'sector': 'Financials', 'name': 'Morgan Stanley'},
    'BLK': {'sector': 'Financials', 'name': 'BlackRock Inc.'},
    'C': {'sector': 'Financials', 'name': 'Citigroup Inc.'},
    'SCHW': {'sector': 'Financials', 'name': 'Charles Schwab Corporation'},
    'CB': {'sector': 'Financials', 'name': 'Chubb Limited'},
    'PGR': {'sector': 'Financials', 'name': 'Progressive Corporation'},
    'USB': {'sector': 'Financials', 'name': 'U.S. Bancorp'},
    'PNC': {'sector': 'Financials', 'name': 'PNC Financial Services'},
    'AXP': {'sector': 'Financials', 'name': 'American Express'},
    'MET': {'sector': 'Financials', 'name': 'MetLife Inc.'},
    
    # Consumer Discretionary (14 stocks)
    'AMZN': {'sector': 'Consumer Discretionary', 'name': 'Amazon.com Inc.'},
    'TSLA': {'sector': 'Consumer Discretionary', 'name': 'Tesla Inc.'},
    'HD': {'sector': 'Consumer Discretionary', 'name': 'Home Depot Inc.'},
    'MCD': {'sector': 'Consumer Discretionary', 'name': "McDonald's Corporation"},
    'NKE': {'sector': 'Consumer Discretionary', 'name': 'Nike Inc.'},
    'LOW': {'sector': 'Consumer Discretionary', 'name': "Lowe's Companies"},
    'SBUX': {'sector': 'Consumer Discretionary', 'name': 'Starbucks Corporation'},
    'BKNG': {'sector': 'Consumer Discretionary', 'name': 'Booking Holdings'},
    'TJX': {'sector': 'Consumer Discretionary', 'name': 'TJX Companies'},
    'CHTR': {'sector': 'Consumer Discretionary', 'name': 'Charter Communications'},
    'GM': {'sector': 'Consumer Discretionary', 'name': 'General Motors'},
    'F': {'sector': 'Consumer Discretionary', 'name': 'Ford Motor Company'},
    'TGT': {'sector': 'Consumer Discretionary', 'name': 'Target Corporation'},
    
    # Consumer Staples (11 stocks)
    'WMT': {'sector': 'Consumer Staples', 'name': 'Walmart Inc.'},
    'PG': {'sector': 'Consumer Staples', 'name': 'Procter & Gamble'},
    'KO': {'sector': 'Consumer Staples', 'name': 'Coca-Cola Company'},
    'PEP': {'sector': 'Consumer Staples', 'name': 'PepsiCo Inc.'},
    'COST': {'sector': 'Consumer Staples', 'name': 'Costco Wholesale'},
    'PM': {'sector': 'Consumer Staples', 'name': 'Philip Morris International'},
    'MDLZ': {'sector': 'Consumer Staples', 'name': 'Mondelez International'},
    'MO': {'sector': 'Consumer Staples', 'name': 'Altria Group'},
    'CL': {'sector': 'Consumer Staples', 'name': 'Colgate-Palmolive'},
    'GIS': {'sector': 'Consumer Staples', 'name': 'General Mills'},
    
    # Industrials (8 stocks)
    'CAT': {'sector': 'Industrials', 'name': 'Caterpillar Inc.'},
    'RTX': {'sector': 'Industrials', 'name': 'RTX Corporation'},
    'HON': {'sector': 'Industrials', 'name': 'Honeywell International'},
    'UNP': {'sector': 'Industrials', 'name': 'Union Pacific Corporation'},
    'BA': {'sector': 'Industrials', 'name': 'Boeing Company'},
    'UPS': {'sector': 'Industrials', 'name': 'United Parcel Service'},
    'LMT': {'sector': 'Industrials', 'name': 'Lockheed Martin'},
    'GE': {'sector': 'Industrials', 'name': 'GE Aerospace'},
    
    # Energy (5 stocks)
    'XOM': {'sector': 'Energy', 'name': 'Exxon Mobil Corporation'},
    'CVX': {'sector': 'Energy', 'name': 'Chevron Corporation'},
    'COP': {'sector': 'Energy', 'name': 'ConocoPhillips'},
    'SLB': {'sector': 'Energy', 'name': 'Schlumberger Limited'},
    'OXY': {'sector': 'Energy', 'name': 'Occidental Petroleum'},
    
    # Communication Services (4 stocks)
    'DIS': {'sector': 'Communication Services', 'name': 'Walt Disney Company'},
    'CMCSA': {'sector': 'Communication Services', 'name': 'Comcast Corporation'},
    'VZ': {'sector': 'Communication Services', 'name': 'Verizon Communications'},
    'T': {'sector': 'Communication Services', 'name': 'AT&T Inc.'},
    'NFLX': {'sector': 'Communication Services', 'name': 'Netflix Inc.'},
    
    # Utilities (2 stocks)
    'NEE': {'sector': 'Utilities', 'name': 'NextEra Energy'},
    'SO': {'sector': 'Utilities', 'name': 'Southern Company'},
    
    # Real Estate (1 stock)
    'AMT': {'sector': 'Real Estate', 'name': 'American Tower Corporation'},
    
    # Materials (2 stocks)
    'LIN': {'sector': 'Materials', 'name': 'Linde plc'},
    'DOW': {'sector': 'Materials', 'name': 'Dow Inc.'},
    
    # ETFs for market hedging
    'SPY': {'sector': 'ETF', 'name': 'SPDR S&P 500 ETF'},
    'QQQ': {'sector': 'ETF', 'name': 'Invesco QQQ Trust'},
}

def get_sp100_tickers():
    """Get list of all S&P 100 tickers"""
    return list(SP100_UNIVERSE.keys())

def get_sector_stocks(sector):
    """Get all stocks in a specific sector"""
    return [ticker for ticker, info in SP100_UNIVERSE.items() 
            if info['sector'] == sector]

def get_stock_info(ticker):
    """Get information about a specific stock"""
    return SP100_UNIVERSE.get(ticker, None)

def get_sector_distribution():
    """Get count of stocks by sector"""
    distribution = {}
    for ticker, info in SP100_UNIVERSE.items():
        sector = info['sector']
        distribution[sector] = distribution.get(sector, 0) + 1
    return distribution

# Trading filters and criteria
LIQUIDITY_REQUIREMENTS = {
    'min_avg_volume': 1_000_000,  # Minimum 1M shares daily volume
    'min_market_cap': 10_000_000_000,  # Minimum $10B market cap
    'min_price': 5.00,  # Minimum share price
    'max_spread_percent': 0.10,  # Maximum 0.10% bid-ask spread
}

# Sector allocation limits for risk management
SECTOR_LIMITS = {
    'Technology': 0.30,  # Max 30% in tech
    'Healthcare': 0.25,  # Max 25% in healthcare
    'Financials': 0.25,  # Max 25% in financials
    'Consumer Discretionary': 0.20,
    'Consumer Staples': 0.20,
    'Industrials': 0.20,
    'Energy': 0.15,
    'Communication Services': 0.15,
    'Utilities': 0.10,
    'Real Estate': 0.10,
    'Materials': 0.10,
    'ETF': 0.20,  # For hedging positions
}

# Multi-agent screening criteria
SCREENING_CRITERIA = {
    'fundamental_metrics': [
        'pe_ratio', 'peg_ratio', 'debt_to_equity', 
        'roe', 'revenue_growth', 'earnings_growth'
    ],
    'technical_indicators': [
        'rsi', 'macd', 'bollinger_bands', 'moving_averages',
        'volume_profile', 'support_resistance'
    ],
    'sentiment_sources': [
        'news_sentiment', 'social_media', 'analyst_ratings',
        'insider_trading', 'options_flow'
    ],
    'risk_metrics': [
        'beta', 'volatility', 'var', 'sharpe_ratio',
        'max_drawdown', 'correlation'
    ]
}