"""
Options Data Fetcher - Fetches Options Chain and Flow Data

Supports multiple data sources:
- Yahoo Finance (free, limited data)
- Financial Datasets API (paid, real-time flow)
- Alpaca Options API (if available)

Features:
- Fetch complete options chains
- Get real-time options quotes
- Track historical volume/open interest
- Calculate Greeks (delta, gamma, theta, vega)
- Monitor large trades and sweeps
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import aiohttp
import pandas as pd
from enum import Enum

logger = logging.getLogger(__name__)


class OptionType(Enum):
    """Option type enumeration"""
    CALL = "call"
    PUT = "put"


class TradeType(Enum):
    """Options trade type"""
    SWEEP = "sweep"  # Multi-exchange sweep order
    BLOCK = "block"  # Large single order
    SPLIT = "split"  # Order split across multiple exchanges
    NORMAL = "normal"  # Regular trade


@dataclass
class OptionsContract:
    """Represents a single options contract"""
    ticker: str
    expiration: datetime
    strike: float
    option_type: OptionType

    # Pricing
    last_price: float
    bid: float
    ask: float
    mark: float  # (bid + ask) / 2

    # Volume and interest
    volume: int
    open_interest: int

    # Greeks
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    implied_volatility: Optional[float] = None

    # Metadata
    last_trade_time: Optional[datetime] = None

    def __post_init__(self):
        """Calculate mark if not provided"""
        if self.mark == 0 and self.bid > 0 and self.ask > 0:
            self.mark = (self.bid + self.ask) / 2.0


@dataclass
class OptionsFlow:
    """Represents an options trade/flow"""
    ticker: str
    timestamp: datetime
    contract: OptionsContract

    # Trade details
    premium: float  # Total dollar amount (price * size * 100)
    size: int  # Number of contracts
    price: float  # Price per contract

    # Trade characteristics
    trade_type: TradeType
    side: str  # "BUY" or "SELL"
    sentiment: str  # "BULLISH", "BEARISH", "NEUTRAL"

    # Confidence metrics
    is_unusual: bool = False  # Unusual volume
    is_large_trade: bool = False  # >$100k premium
    is_sweep: bool = False  # Multi-exchange sweep

    # Additional context
    spot_price: Optional[float] = None  # Underlying price at trade time
    distance_from_spot: Optional[float] = None  # (strike - spot) / spot
    days_to_expiration: Optional[int] = None

    def __post_init__(self):
        """Calculate derived fields"""
        if self.spot_price and self.contract.strike:
            self.distance_from_spot = (
                (self.contract.strike - self.spot_price) / self.spot_price
            )

        if self.contract.expiration:
            self.days_to_expiration = (
                self.contract.expiration - self.timestamp
            ).days

        # Determine sentiment
        if not self.sentiment:
            self.sentiment = self._determine_sentiment()

        # Check if sweep
        if self.trade_type == TradeType.SWEEP:
            self.is_sweep = True

        # Check if large trade
        if self.premium >= 100000:
            self.is_large_trade = True

    def _determine_sentiment(self) -> str:
        """Determine bullish/bearish sentiment from trade"""
        if self.contract.option_type == OptionType.CALL:
            return "BULLISH" if self.side == "BUY" else "BEARISH"
        else:  # PUT
            return "BEARISH" if self.side == "BUY" else "BULLISH"


class OptionsDataFetcher:
    """
    Fetches options chain data and flow from multiple sources

    Data Sources:
    1. Yahoo Finance (free, delayed)
    2. Financial Datasets API (paid, real-time)
    3. Alpaca Options (if enabled)
    """

    def __init__(
        self,
        yahoo_enabled: bool = True,
        fd_api_key: Optional[str] = None,
        alpaca_enabled: bool = False,
        cache_ttl: int = 60  # Cache TTL in seconds
    ):
        """
        Initialize options data fetcher

        Args:
            yahoo_enabled: Enable Yahoo Finance data
            fd_api_key: Financial Datasets API key
            alpaca_enabled: Enable Alpaca options data
            cache_ttl: Cache time-to-live in seconds
        """
        self.yahoo_enabled = yahoo_enabled
        self.fd_api_key = fd_api_key or os.getenv('FINANCIAL_DATASETS_API_KEY')
        self.alpaca_enabled = alpaca_enabled
        self.cache_ttl = cache_ttl

        # Caches
        self.chain_cache: Dict[str, Tuple[datetime, List[OptionsContract]]] = {}
        self.flow_cache: Dict[str, Tuple[datetime, List[OptionsFlow]]] = {}

        logger.info(
            f"OptionsDataFetcher initialized "
            f"(yahoo={yahoo_enabled}, fd={bool(fd_api_key)}, alpaca={alpaca_enabled})"
        )

    async def fetch_options_chain(
        self,
        ticker: str,
        expiration: Optional[datetime] = None
    ) -> List[OptionsContract]:
        """
        Fetch complete options chain for ticker

        Args:
            ticker: Stock ticker symbol
            expiration: Specific expiration date (None = all expirations)

        Returns:
            List of OptionsContract objects
        """
        # Check cache
        cache_key = f"{ticker}_{expiration or 'all'}"
        if cache_key in self.chain_cache:
            cached_time, cached_data = self.chain_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                logger.debug(f"Using cached options chain for {ticker}")
                return cached_data

        # Try data sources in order of preference
        contracts = []

        # 1. Try Financial Datasets API (most complete)
        if self.fd_api_key:
            try:
                contracts = await self._fetch_from_fd(ticker, expiration)
                if contracts:
                    logger.info(f"Fetched {len(contracts)} contracts from FD API for {ticker}")
            except Exception as e:
                logger.error(f"Error fetching from FD API: {e}")

        # 2. Fallback to Yahoo Finance
        if not contracts and self.yahoo_enabled:
            try:
                contracts = await self._fetch_from_yahoo(ticker, expiration)
                if contracts:
                    logger.info(f"Fetched {len(contracts)} contracts from Yahoo for {ticker}")
            except Exception as e:
                logger.error(f"Error fetching from Yahoo: {e}")

        # Cache results
        if contracts:
            self.chain_cache[cache_key] = (datetime.now(), contracts)

        return contracts

    async def fetch_options_flow(
        self,
        ticker: str,
        minutes_back: int = 60,
        min_premium: float = 0
    ) -> List[OptionsFlow]:
        """
        Fetch recent options flow/trades

        Args:
            ticker: Stock ticker symbol
            minutes_back: How many minutes back to look
            min_premium: Minimum premium to include ($)

        Returns:
            List of OptionsFlow objects
        """
        # Check cache
        cache_key = f"{ticker}_flow_{minutes_back}"
        if cache_key in self.flow_cache:
            cached_time, cached_data = self.flow_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                logger.debug(f"Using cached options flow for {ticker}")
                return [f for f in cached_data if f.premium >= min_premium]

        flows = []

        # Try Financial Datasets API (only source with real-time flow)
        if self.fd_api_key:
            try:
                flows = await self._fetch_flow_from_fd(ticker, minutes_back)
                logger.info(f"Fetched {len(flows)} flow trades for {ticker}")
            except Exception as e:
                logger.error(f"Error fetching flow from FD API: {e}")
        else:
            logger.warning("Options flow requires Financial Datasets API key")

        # Cache results
        if flows:
            self.flow_cache[cache_key] = (datetime.now(), flows)

        # Filter by minimum premium
        return [f for f in flows if f.premium >= min_premium]

    async def get_expirations(self, ticker: str) -> List[datetime]:
        """
        Get available expiration dates for ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of expiration dates
        """
        # Fetch chain to get expirations
        chain = await self.fetch_options_chain(ticker)

        # Extract unique expirations
        expirations = sorted(list(set([c.expiration for c in chain])))

        return expirations

    async def _fetch_from_yahoo(
        self,
        ticker: str,
        expiration: Optional[datetime] = None
    ) -> List[OptionsContract]:
        """Fetch options chain from Yahoo Finance"""
        contracts = []

        try:
            import yfinance as yf

            stock = yf.Ticker(ticker)

            # Get expirations
            if expiration:
                exp_str = expiration.strftime('%Y-%m-%d')
                expirations = [exp_str]
            else:
                expirations = stock.options

            # Fetch chains for each expiration
            for exp_str in expirations:
                try:
                    opt = stock.option_chain(exp_str)
                    exp_date = datetime.strptime(exp_str, '%Y-%m-%d')

                    # Parse calls
                    for _, row in opt.calls.iterrows():
                        contracts.append(OptionsContract(
                            ticker=ticker,
                            expiration=exp_date,
                            strike=float(row['strike']),
                            option_type=OptionType.CALL,
                            last_price=float(row.get('lastPrice', 0)),
                            bid=float(row.get('bid', 0)),
                            ask=float(row.get('ask', 0)),
                            mark=0,  # Will be calculated
                            volume=int(row.get('volume', 0)),
                            open_interest=int(row.get('openInterest', 0)),
                            implied_volatility=float(row.get('impliedVolatility', 0))
                        ))

                    # Parse puts
                    for _, row in opt.puts.iterrows():
                        contracts.append(OptionsContract(
                            ticker=ticker,
                            expiration=exp_date,
                            strike=float(row['strike']),
                            option_type=OptionType.PUT,
                            last_price=float(row.get('lastPrice', 0)),
                            bid=float(row.get('bid', 0)),
                            ask=float(row.get('ask', 0)),
                            mark=0,  # Will be calculated
                            volume=int(row.get('volume', 0)),
                            open_interest=int(row.get('openInterest', 0)),
                            implied_volatility=float(row.get('impliedVolatility', 0))
                        ))

                except Exception as e:
                    logger.error(f"Error fetching {ticker} options for {exp_str}: {e}")

        except ImportError:
            logger.error("yfinance not installed. Install with: pip install yfinance")
        except Exception as e:
            logger.error(f"Error fetching from Yahoo: {e}")

        return contracts

    async def _fetch_from_fd(
        self,
        ticker: str,
        expiration: Optional[datetime] = None
    ) -> List[OptionsContract]:
        """Fetch options chain from Financial Datasets API"""
        contracts = []

        if not self.fd_api_key:
            return contracts

        try:
            url = "https://api.financialdatasets.ai/options/chain"
            params = {
                'ticker': ticker,
                'limit': 1000
            }

            if expiration:
                params['expiration'] = expiration.strftime('%Y-%m-%d')

            headers = {
                'X-API-KEY': self.fd_api_key,
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Parse response
                        for item in data.get('options', []):
                            contracts.append(OptionsContract(
                                ticker=ticker,
                                expiration=datetime.fromisoformat(
                                    item['expiration'].replace('Z', '+00:00')
                                ),
                                strike=float(item['strike']),
                                option_type=OptionType.CALL if item['type'] == 'call' else OptionType.PUT,
                                last_price=float(item.get('last', 0)),
                                bid=float(item.get('bid', 0)),
                                ask=float(item.get('ask', 0)),
                                mark=float(item.get('mark', 0)),
                                volume=int(item.get('volume', 0)),
                                open_interest=int(item.get('openInterest', 0)),
                                delta=float(item.get('delta', 0)),
                                gamma=float(item.get('gamma', 0)),
                                theta=float(item.get('theta', 0)),
                                vega=float(item.get('vega', 0)),
                                implied_volatility=float(item.get('iv', 0))
                            ))

                    else:
                        logger.error(f"FD API error {response.status}: {await response.text()}")

        except Exception as e:
            logger.error(f"Error in FD API request: {e}")

        return contracts

    async def _fetch_flow_from_fd(
        self,
        ticker: str,
        minutes_back: int = 60
    ) -> List[OptionsFlow]:
        """Fetch options flow from Financial Datasets API"""
        flows = []

        if not self.fd_api_key:
            return flows

        try:
            url = "https://api.financialdatasets.ai/options/flow"

            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes_back)

            params = {
                'ticker': ticker,
                'from': start_time.isoformat(),
                'to': end_time.isoformat(),
                'limit': 500
            }

            headers = {
                'X-API-KEY': self.fd_api_key,
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Parse flow trades
                        for item in data.get('trades', []):
                            # Create contract
                            contract = OptionsContract(
                                ticker=ticker,
                                expiration=datetime.fromisoformat(
                                    item['expiration'].replace('Z', '+00:00')
                                ),
                                strike=float(item['strike']),
                                option_type=OptionType.CALL if item['type'] == 'call' else OptionType.PUT,
                                last_price=float(item.get('price', 0)),
                                bid=float(item.get('bid', 0)),
                                ask=float(item.get('ask', 0)),
                                mark=float(item.get('mark', 0)),
                                volume=int(item.get('volume', 0)),
                                open_interest=int(item.get('openInterest', 0)),
                                delta=float(item.get('delta', 0)),
                                implied_volatility=float(item.get('iv', 0))
                            )

                            # Determine trade type
                            trade_type = TradeType.NORMAL
                            if item.get('is_sweep'):
                                trade_type = TradeType.SWEEP
                            elif item.get('is_block'):
                                trade_type = TradeType.BLOCK
                            elif item.get('is_split'):
                                trade_type = TradeType.SPLIT

                            # Create flow
                            flows.append(OptionsFlow(
                                ticker=ticker,
                                timestamp=datetime.fromisoformat(
                                    item['timestamp'].replace('Z', '+00:00')
                                ),
                                contract=contract,
                                premium=float(item.get('premium', 0)),
                                size=int(item.get('size', 0)),
                                price=float(item.get('price', 0)),
                                trade_type=trade_type,
                                side=item.get('side', 'BUY').upper(),
                                sentiment="",  # Will be determined in __post_init__
                                spot_price=float(item.get('spot_price', 0))
                            ))

                    else:
                        logger.error(f"FD API flow error {response.status}: {await response.text()}")

        except Exception as e:
            logger.error(f"Error fetching flow from FD API: {e}")

        return flows

    async def get_spot_price(self, ticker: str) -> float:
        """
        Get current spot price for underlying

        Args:
            ticker: Stock ticker symbol

        Returns:
            Current stock price
        """
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            return float(stock.info.get('currentPrice', 0))
        except Exception as e:
            logger.error(f"Error getting spot price for {ticker}: {e}")
            return 0.0

    def calculate_greeks(
        self,
        contract: OptionsContract,
        spot_price: float,
        risk_free_rate: float = 0.05
    ) -> OptionsContract:
        """
        Calculate Greeks for options contract (simplified Black-Scholes)

        Args:
            contract: OptionsContract to calculate Greeks for
            spot_price: Current underlying price
            risk_free_rate: Risk-free interest rate

        Returns:
            Updated OptionsContract with Greeks
        """
        try:
            from scipy.stats import norm
            import math

            # Time to expiration in years
            t = (contract.expiration - datetime.now()).days / 365.0

            if t <= 0:
                # Expired
                contract.delta = 0
                contract.gamma = 0
                contract.theta = 0
                contract.vega = 0
                return contract

            # Use implied volatility if available
            sigma = contract.implied_volatility or 0.3

            # Calculate d1 and d2
            d1 = (
                math.log(spot_price / contract.strike) +
                (risk_free_rate + 0.5 * sigma ** 2) * t
            ) / (sigma * math.sqrt(t))

            d2 = d1 - sigma * math.sqrt(t)

            # Calculate Greeks
            if contract.option_type == OptionType.CALL:
                contract.delta = norm.cdf(d1)
            else:  # PUT
                contract.delta = norm.cdf(d1) - 1

            # Gamma (same for calls and puts)
            contract.gamma = norm.pdf(d1) / (spot_price * sigma * math.sqrt(t))

            # Theta
            if contract.option_type == OptionType.CALL:
                contract.theta = (
                    -spot_price * norm.pdf(d1) * sigma / (2 * math.sqrt(t)) -
                    risk_free_rate * contract.strike * math.exp(-risk_free_rate * t) * norm.cdf(d2)
                ) / 365
            else:  # PUT
                contract.theta = (
                    -spot_price * norm.pdf(d1) * sigma / (2 * math.sqrt(t)) +
                    risk_free_rate * contract.strike * math.exp(-risk_free_rate * t) * norm.cdf(-d2)
                ) / 365

            # Vega (same for calls and puts)
            contract.vega = spot_price * norm.pdf(d1) * math.sqrt(t) / 100

        except Exception as e:
            logger.error(f"Error calculating Greeks: {e}")

        return contract

    def clear_cache(self):
        """Clear all caches"""
        self.chain_cache.clear()
        self.flow_cache.clear()
        logger.info("Cleared all caches")
