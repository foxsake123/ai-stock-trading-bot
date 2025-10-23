"""
Unusual Options Flow Tracker
Monitors options activity for unusual patterns and whale trades
Uses multiple free data sources
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from bs4 import BeautifulSoup
import json
from pathlib import Path
import logging
import asyncio
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionsFlowTracker:
    """Track unusual options activity and large trades"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Thresholds for unusual activity
        self.unusual_thresholds = {
            'volume_to_oi_ratio': 0.25,  # Volume > 25% of OI is unusual
            'premium_threshold': 50000,  # $50K+ premium is significant
            'volume_spike': 3.0,  # 3x average volume
            'iv_percentile': 80,  # IV in top 20% is high
        }

        # Known whale traders to track (from public disclosures)
        self.whale_indicators = [
            'sweep',
            'block',
            'split',
            'floor',
            'multi-exchange',
            'aggressive'
        ]

    def get_options_chain(self, symbol):
        """Get options chain data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)

            # Get available expiration dates
            expirations = ticker.options

            if not expirations:
                logger.warning(f"No options available for {symbol}")
                return None

            all_options = []

            # Get options for next 3 expirations
            for expiry in expirations[:3]:
                try:
                    # Get calls
                    calls = ticker.option_chain(expiry).calls
                    calls['type'] = 'CALL'
                    calls['expiry'] = expiry

                    # Get puts
                    puts = ticker.option_chain(expiry).puts
                    puts['type'] = 'PUT'
                    puts['expiry'] = expiry

                    all_options.append(calls)
                    all_options.append(puts)

                except Exception as e:
                    logger.error(f"Error getting options for {symbol} exp {expiry}: {e}")
                    continue

            if all_options:
                return pd.concat(all_options, ignore_index=True)
            return None

        except Exception as e:
            logger.error(f"Error getting options chain for {symbol}: {e}")
            return None

    def detect_unusual_activity(self, symbol):
        """Detect unusual options activity for a symbol"""
        options = self.get_options_chain(symbol)

        if options is None or options.empty:
            return []

        unusual_trades = []

        for _, option in options.iterrows():
            # Calculate unusual indicators
            volume = option.get('volume', 0)
            open_interest = option.get('openInterest', 1)
            last_price = option.get('lastPrice', 0)

            if volume == 0 or open_interest == 0:
                continue

            # Volume to Open Interest ratio
            vol_oi_ratio = volume / open_interest if open_interest > 0 else 0

            # Premium calculation
            premium = volume * last_price * 100  # Each contract is 100 shares

            # Check for unusual activity
            is_unusual = False
            reasons = []

            if vol_oi_ratio > self.unusual_thresholds['volume_to_oi_ratio']:
                is_unusual = True
                reasons.append(f"High Vol/OI: {vol_oi_ratio:.2f}")

            if premium > self.unusual_thresholds['premium_threshold']:
                is_unusual = True
                reasons.append(f"Large Premium: ${premium:,.0f}")

            # Check if volume is unusually high
            avg_volume = options['volume'].mean()
            if volume > avg_volume * self.unusual_thresholds['volume_spike']:
                is_unusual = True
                reasons.append(f"Volume Spike: {volume/avg_volume:.1f}x avg")

            # High implied volatility
            iv = option.get('impliedVolatility', 0) * 100
            if iv > self.unusual_thresholds['iv_percentile']:
                is_unusual = True
                reasons.append(f"High IV: {iv:.1f}%")

            if is_unusual:
                # Determine sentiment
                if option['type'] == 'CALL':
                    if option['strike'] > option.get('lastPrice', 0) * 1.05:
                        sentiment = 'VERY_BULLISH'
                    else:
                        sentiment = 'BULLISH'
                else:  # PUT
                    if option['strike'] < option.get('lastPrice', 0) * 0.95:
                        sentiment = 'VERY_BEARISH'
                    else:
                        sentiment = 'BEARISH'

                unusual_trades.append({
                    'symbol': symbol,
                    'type': option['type'],
                    'strike': option['strike'],
                    'expiry': option['expiry'],
                    'volume': volume,
                    'open_interest': open_interest,
                    'vol_oi_ratio': vol_oi_ratio,
                    'last_price': last_price,
                    'premium': premium,
                    'iv': iv,
                    'bid': option.get('bid', 0),
                    'ask': option.get('ask', 0),
                    'sentiment': sentiment,
                    'reasons': ', '.join(reasons),
                    'timestamp': datetime.now()
                })

        return unusual_trades

    def scan_market_flow(self, symbols):
        """Scan multiple symbols for unusual options flow"""
        all_flow = []

        for symbol in symbols:
            logger.info(f"Scanning options flow for {symbol}")
            unusual = self.detect_unusual_activity(symbol)
            all_flow.extend(unusual)

        # Sort by premium (biggest trades first)
        all_flow.sort(key=lambda x: x['premium'], reverse=True)

        return all_flow

    def analyze_flow_sentiment(self, flow_data):
        """Analyze overall market sentiment from options flow"""
        if not flow_data:
            return {
                'sentiment': 'NEUTRAL',
                'call_put_ratio': 1.0,
                'total_premium': 0,
                'confidence': 0
            }

        # Calculate metrics
        call_premium = sum(f['premium'] for f in flow_data if f['type'] == 'CALL')
        put_premium = sum(f['premium'] for f in flow_data if f['type'] == 'PUT')
        total_premium = call_premium + put_premium

        if total_premium == 0:
            return {
                'sentiment': 'NEUTRAL',
                'call_put_ratio': 1.0,
                'total_premium': 0,
                'confidence': 0
            }

        call_put_ratio = call_premium / put_premium if put_premium > 0 else 10

        # Determine sentiment
        if call_put_ratio > 2:
            sentiment = 'VERY_BULLISH'
        elif call_put_ratio > 1.3:
            sentiment = 'BULLISH'
        elif call_put_ratio < 0.5:
            sentiment = 'VERY_BEARISH'
        elif call_put_ratio < 0.77:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'

        # Confidence based on premium size
        confidence = min(1.0, total_premium / 1000000)  # Max confidence at $1M

        return {
            'sentiment': sentiment,
            'call_put_ratio': call_put_ratio,
            'call_premium': call_premium,
            'put_premium': put_premium,
            'total_premium': total_premium,
            'confidence': confidence,
            'trade_count': len(flow_data)
        }

    def get_gamma_levels(self, symbol):
        """Calculate gamma exposure levels (support/resistance)"""
        options = self.get_options_chain(symbol)

        if options is None or options.empty:
            return {}

        try:
            current_price = yf.Ticker(symbol).info.get('currentPrice', 0)

            if not current_price:
                return {}

            # Calculate gamma for each strike
            gamma_exposure = {}

            for strike in options['strike'].unique():
                strike_options = options[options['strike'] == strike]

                # Sum up gamma exposure (simplified)
                call_oi = strike_options[strike_options['type'] == 'CALL']['openInterest'].sum()
                put_oi = strike_options[strike_options['type'] == 'PUT']['openInterest'].sum()

                # Net gamma (calls positive, puts negative for MM)
                net_gamma = (call_oi - put_oi) * 100  # Each contract is 100 shares

                gamma_exposure[strike] = net_gamma

            # Find significant levels
            sorted_strikes = sorted(gamma_exposure.items(), key=lambda x: abs(x[1]), reverse=True)

            # Get top support/resistance levels
            support_levels = [s for s, g in sorted_strikes if g > 0 and s < current_price][:3]
            resistance_levels = [s for s, g in sorted_strikes if g < 0 and s > current_price][:3]

            return {
                'current_price': current_price,
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'max_gamma_strike': sorted_strikes[0][0] if sorted_strikes else None
            }

        except Exception as e:
            logger.error(f"Error calculating gamma levels for {symbol}: {e}")
            return {}

    def find_sweep_orders(self, symbol):
        """Identify potential sweep orders (urgent large trades)"""
        options = self.get_options_chain(symbol)

        if options is None or options.empty:
            return []

        sweeps = []

        for _, option in options.iterrows():
            volume = option.get('volume', 0)
            open_interest = option.get('openInterest', 1)
            bid = option.get('bid', 0)
            ask = option.get('ask', 0)
            last = option.get('lastPrice', 0)

            # Sweep indicators
            # 1. High volume relative to OI
            # 2. Traded at or above ask (for calls) or at/below bid (for puts)
            # 3. Large premium

            if volume < 100:  # Minimum volume threshold
                continue

            premium = volume * last * 100

            is_sweep = False
            sweep_type = None

            # Check if traded aggressively
            if option['type'] == 'CALL' and last >= ask * 0.95:  # Near or above ask
                is_sweep = True
                sweep_type = 'BULLISH_SWEEP'
            elif option['type'] == 'PUT' and last <= bid * 1.05:  # Near or below bid
                is_sweep = True
                sweep_type = 'BEARISH_SWEEP'

            # Additional sweep criteria
            if is_sweep and volume > open_interest * 0.1 and premium > 25000:
                sweeps.append({
                    'symbol': symbol,
                    'type': option['type'],
                    'strike': option['strike'],
                    'expiry': option['expiry'],
                    'volume': volume,
                    'premium': premium,
                    'last_price': last,
                    'bid_ask_spread': ask - bid,
                    'sweep_type': sweep_type,
                    'urgency': 'HIGH' if last > ask or last < bid else 'MEDIUM',
                    'timestamp': datetime.now()
                })

        return sweeps

    def get_put_call_ratio(self, symbol):
        """Calculate put/call ratio for sentiment"""
        options = self.get_options_chain(symbol)

        if options is None or options.empty:
            return None

        call_volume = options[options['type'] == 'CALL']['volume'].sum()
        put_volume = options[options['type'] == 'PUT']['volume'].sum()

        if call_volume == 0:
            return None

        pc_ratio = put_volume / call_volume

        sentiment = 'NEUTRAL'
        if pc_ratio > 1.2:
            sentiment = 'BEARISH'
        elif pc_ratio < 0.6:
            sentiment = 'BULLISH'

        return {
            'symbol': symbol,
            'put_volume': put_volume,
            'call_volume': call_volume,
            'put_call_ratio': pc_ratio,
            'sentiment': sentiment
        }

    def generate_flow_report(self, flow_data):
        """Generate formatted options flow report"""
        if not flow_data:
            return "No unusual options flow detected"

        report = []
        report.append("=" * 70)
        report.append("UNUSUAL OPTIONS FLOW REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")

        # Overall sentiment
        sentiment = self.analyze_flow_sentiment(flow_data)
        report.append(f"MARKET SENTIMENT: {sentiment['sentiment']}")
        report.append(f"Call/Put Ratio: {sentiment['call_put_ratio']:.2f}")
        report.append(f"Total Premium: ${sentiment['total_premium']:,.0f}")
        report.append(f"Confidence: {sentiment['confidence']:.1%}")
        report.append("")

        report.append("TOP UNUSUAL OPTIONS TRADES:")
        report.append("-" * 50)

        for i, trade in enumerate(flow_data[:20], 1):
            report.append(f"{i}. ${trade['symbol']} - {trade['type']} ${trade['strike']} exp {trade['expiry']}")
            report.append(f"   Premium: ${trade['premium']:,.0f}")
            report.append(f"   Volume: {trade['volume']:,} | OI: {trade['open_interest']:,}")
            report.append(f"   Vol/OI: {trade['vol_oi_ratio']:.2f} | IV: {trade['iv']:.1f}%")
            report.append(f"   Sentiment: {trade['sentiment']}")
            report.append(f"   Unusual: {trade['reasons']}")
            report.append("")

        return "\n".join(report)

    def save_flow_data(self, flow_data, filename=None):
        """Save flow data to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"options_flow_{timestamp}.json"

        filepath = Path("scripts-and-data/data/options_flow") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Convert datetime objects to strings
        for trade in flow_data:
            if isinstance(trade.get('timestamp'), datetime):
                trade['timestamp'] = trade['timestamp'].isoformat()

        with open(filepath, 'w') as f:
            json.dump(flow_data, f, indent=2, default=str)

        logger.info(f"Saved options flow data to {filepath}")
        return filepath

class OptionsAlertSystem:
    """Real-time alert system for options flow"""

    def __init__(self, telegram_token=None, chat_id=None):
        self.tracker = OptionsFlowTracker()
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.alerted_trades = set()  # Track what we've already alerted

    async def monitor_symbols(self, symbols, interval_minutes=5):
        """Continuously monitor symbols for unusual options activity"""
        while True:
            try:
                for symbol in symbols:
                    logger.info(f"Checking options flow for {symbol}")

                    # Get unusual activity
                    unusual = self.tracker.detect_unusual_activity(symbol)

                    for trade in unusual:
                        trade_id = f"{symbol}_{trade['strike']}_{trade['expiry']}_{trade['type']}"

                        # Only alert once per unique trade
                        if trade_id not in self.alerted_trades:
                            if trade['premium'] > 100000:  # Only alert on large trades
                                await self.send_alert(trade)
                                self.alerted_trades.add(trade_id)

                    # Get sweep orders
                    sweeps = self.tracker.find_sweep_orders(symbol)
                    for sweep in sweeps:
                        sweep_id = f"{symbol}_sweep_{sweep['strike']}_{sweep['expiry']}"
                        if sweep_id not in self.alerted_trades:
                            await self.send_sweep_alert(sweep)
                            self.alerted_trades.add(sweep_id)

                # Clean old alerts (older than 1 day)
                # This prevents the set from growing indefinitely
                if len(self.alerted_trades) > 1000:
                    self.alerted_trades.clear()

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            await asyncio.sleep(interval_minutes * 60)

    async def send_alert(self, trade):
        """Send alert for unusual options activity"""
        message = f"🔥 UNUSUAL OPTIONS ACTIVITY\n\n"
        message += f"Symbol: ${trade['symbol']}\n"
        message += f"Type: {trade['type']} ${trade['strike']} exp {trade['expiry']}\n"
        message += f"Premium: ${trade['premium']:,.0f}\n"
        message += f"Volume/OI: {trade['vol_oi_ratio']:.2f}\n"
        message += f"Sentiment: {trade['sentiment']}\n"
        message += f"Reasons: {trade['reasons']}"

        if self.telegram_token and self.chat_id:
            await self.send_telegram_message(message)
        else:
            print(message)

    async def send_sweep_alert(self, sweep):
        """Send alert for sweep order"""
        emoji = "🐂" if "BULLISH" in sweep['sweep_type'] else "🐻"

        message = f"{emoji} SWEEP ORDER DETECTED\n\n"
        message += f"Symbol: ${sweep['symbol']}\n"
        message += f"Type: {sweep['type']} ${sweep['strike']}\n"
        message += f"Premium: ${sweep['premium']:,.0f}\n"
        message += f"Volume: {sweep['volume']:,}\n"
        message += f"Urgency: {sweep['urgency']}\n"
        message += f"Type: {sweep['sweep_type']}"

        if self.telegram_token and self.chat_id:
            await self.send_telegram_message(message)
        else:
            print(message)

    async def send_telegram_message(self, message):
        """Send message via Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    logger.info("Alert sent successfully")
                else:
                    logger.error(f"Failed to send alert: {response.status}")

# Example usage
def main():
    """Example usage of options flow tracker"""
    tracker = OptionsFlowTracker()

    # Scan for unusual options on key symbols
    symbols = ['SPY', 'QQQ', 'AAPL', 'NVDA', 'TSLA', 'BBAI', 'SOUN']

    print("Scanning for unusual options activity...")
    flow = tracker.scan_market_flow(symbols)

    # Generate report
    report = tracker.generate_flow_report(flow)
    print(report)

    # Save data
    tracker.save_flow_data(flow)

    # Get gamma levels for SPY
    gamma = tracker.get_gamma_levels('SPY')
    print(f"\nSPY Gamma Levels: {gamma}")

    # Check put/call ratio
    pc_ratio = tracker.get_put_call_ratio('SPY')
    print(f"\nSPY Put/Call Ratio: {pc_ratio}")

if __name__ == "__main__":
    main()