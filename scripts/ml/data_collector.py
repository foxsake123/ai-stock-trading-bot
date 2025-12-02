"""
ML Data Collection Infrastructure
Collects training data for future ML models.

Data collected:
- Trade recommendations (approved/rejected)
- Agent confidence scores
- Market conditions at trade time
- Actual outcomes (P&L after X days)

Usage:
    from scripts.ml.data_collector import MLDataCollector
    collector = MLDataCollector()
    collector.log_trade_recommendation(trade_data)
    collector.update_trade_outcome(symbol, entry_date, exit_price, exit_date)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import yfinance as yf

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "ml_training"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class MLDataCollector:
    """Collects and manages ML training data"""

    def __init__(self):
        self.trades_file = DATA_DIR / "trade_outcomes.json"
        self.features_file = DATA_DIR / "trade_features.json"
        self.sentiment_file = DATA_DIR / "sentiment_data.json"

        # Initialize files if they don't exist
        self._init_files()

    def _init_files(self):
        """Initialize data files if they don't exist"""
        for file_path in [self.trades_file, self.features_file, self.sentiment_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump({"records": [], "metadata": {"created": datetime.now().isoformat()}}, f, indent=2)

    def _load_data(self, file_path: Path) -> Dict:
        """Load data from JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)

    def _save_data(self, file_path: Path, data: Dict):
        """Save data to JSON file"""
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def log_trade_recommendation(self, trade_data: Dict):
        """
        Log a trade recommendation with all features.

        Args:
            trade_data: Dict containing:
                - symbol: str
                - action: str (BUY/SELL)
                - source: str (CLAUDE/DEE-BOT/SHORGAN)
                - conviction: str (HIGH/MEDIUM/LOW)
                - external_confidence: float
                - agent_scores: Dict[str, float]
                - internal_confidence: float
                - final_score: float
                - approved: bool
                - entry_price: float (optional)
                - limit_price: float (optional)
                - shares: int
                - catalyst: str (optional)
                - rationale: str (optional)
        """
        data = self._load_data(self.trades_file)

        # Create record
        record = {
            "id": f"{trade_data['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime('%Y-%m-%d'),

            # Trade info
            "symbol": trade_data.get("symbol"),
            "action": trade_data.get("action"),
            "source": trade_data.get("source"),
            "shares": trade_data.get("shares"),
            "entry_price": trade_data.get("entry_price") or trade_data.get("limit_price"),

            # Validation scores
            "conviction": trade_data.get("conviction"),
            "external_confidence": trade_data.get("external_confidence"),
            "agent_scores": trade_data.get("agent_scores", {}),
            "internal_confidence": trade_data.get("internal_confidence"),
            "final_score": trade_data.get("final_score"),
            "approved": trade_data.get("approved"),

            # Context
            "catalyst": trade_data.get("catalyst"),
            "rationale": trade_data.get("rationale"),

            # Outcome (to be filled later)
            "outcome": {
                "filled": None,
                "fill_price": None,
                "exit_price": None,
                "exit_date": None,
                "pnl_dollars": None,
                "pnl_percent": None,
                "days_held": None,
                "win": None
            }
        }

        data["records"].append(record)
        self._save_data(self.trades_file, data)

        print(f"[ML] Logged trade: {record['symbol']} {record['action']} (approved={record['approved']})")
        return record["id"]

    def update_trade_outcome(self, trade_id: str = None, symbol: str = None,
                            entry_date: str = None, fill_price: float = None,
                            exit_price: float = None, exit_date: str = None):
        """
        Update a trade record with its outcome.

        Args:
            trade_id: Unique trade ID (or use symbol + entry_date)
            symbol: Stock symbol
            entry_date: Date trade was entered (YYYY-MM-DD)
            fill_price: Actual fill price
            exit_price: Exit price
            exit_date: Date position was closed
        """
        data = self._load_data(self.trades_file)

        # Find the record
        record = None
        for r in data["records"]:
            if trade_id and r["id"] == trade_id:
                record = r
                break
            elif symbol and entry_date and r["symbol"] == symbol and r["date"] == entry_date:
                record = r
                break

        if not record:
            print(f"[ML] Trade not found: {trade_id or f'{symbol} on {entry_date}'}")
            return False

        # Update outcome
        entry = fill_price or record["entry_price"]
        if entry and exit_price:
            pnl_dollars = (exit_price - entry) * record.get("shares", 1)
            pnl_percent = ((exit_price / entry) - 1) * 100

            if record["action"] == "SELL":  # Short position
                pnl_dollars = -pnl_dollars
                pnl_percent = -pnl_percent

            record["outcome"] = {
                "filled": True,
                "fill_price": fill_price,
                "exit_price": exit_price,
                "exit_date": exit_date,
                "pnl_dollars": round(pnl_dollars, 2),
                "pnl_percent": round(pnl_percent, 2),
                "days_held": self._calculate_days_held(record["date"], exit_date),
                "win": pnl_percent > 0
            }

            self._save_data(self.trades_file, data)
            print(f"[ML] Updated outcome: {symbol} -> {pnl_percent:+.2f}%")
            return True

        return False

    def _calculate_days_held(self, entry_date: str, exit_date: str) -> int:
        """Calculate trading days between dates"""
        try:
            entry = datetime.strptime(entry_date, '%Y-%m-%d')
            exit = datetime.strptime(exit_date, '%Y-%m-%d')
            return (exit - entry).days
        except:
            return None

    def log_market_features(self, symbol: str, features: Dict):
        """
        Log market features at trade time for ML training.

        Args:
            symbol: Stock symbol
            features: Dict containing:
                - price: float
                - volume: int
                - avg_volume: int
                - rsi: float (optional)
                - macd: float (optional)
                - bb_position: float (optional)
                - sector: str
                - market_cap: float
                - pe_ratio: float
                - sentiment_score: float (optional)
                - vix: float (optional)
                - spy_return: float (optional)
        """
        data = self._load_data(self.features_file)

        record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime('%Y-%m-%d'),
            "symbol": symbol,
            **features
        }

        data["records"].append(record)
        self._save_data(self.features_file, data)

    def log_sentiment(self, symbol: str, sentiment_data: Dict):
        """
        Log sentiment data for ML training.

        Args:
            symbol: Stock symbol
            sentiment_data: Dict containing:
                - news_sentiment: float (-1 to 1)
                - social_sentiment: float (-1 to 1)
                - analyst_rating: str (BUY/HOLD/SELL)
                - insider_activity: str (BUYING/SELLING/NEUTRAL)
                - options_flow: str (BULLISH/BEARISH/NEUTRAL)
                - wsb_mentions: int
                - news_volume: int
        """
        data = self._load_data(self.sentiment_file)

        record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime('%Y-%m-%d'),
            "symbol": symbol,
            **sentiment_data
        }

        data["records"].append(record)
        self._save_data(self.sentiment_file, data)

    def get_training_data(self, min_date: str = None) -> List[Dict]:
        """
        Get completed trades with outcomes for ML training.

        Returns list of records with known outcomes.
        """
        data = self._load_data(self.trades_file)

        training_records = []
        for record in data["records"]:
            # Only include trades with outcomes
            if record["outcome"]["win"] is not None:
                if min_date and record["date"] < min_date:
                    continue
                training_records.append(record)

        return training_records

    def get_statistics(self) -> Dict:
        """Get statistics on collected data"""
        trades = self._load_data(self.trades_file)
        features = self._load_data(self.features_file)
        sentiment = self._load_data(self.sentiment_file)

        total_trades = len(trades["records"])
        completed_trades = sum(1 for r in trades["records"] if r["outcome"]["win"] is not None)
        approved_trades = sum(1 for r in trades["records"] if r["approved"])

        wins = sum(1 for r in trades["records"] if r["outcome"]["win"] == True)
        losses = sum(1 for r in trades["records"] if r["outcome"]["win"] == False)

        return {
            "total_trades_logged": total_trades,
            "completed_with_outcome": completed_trades,
            "approved_trades": approved_trades,
            "rejected_trades": total_trades - approved_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": f"{(wins / completed_trades * 100):.1f}%" if completed_trades > 0 else "N/A",
            "feature_records": len(features["records"]),
            "sentiment_records": len(sentiment["records"]),
            "ready_for_training": completed_trades >= 50
        }


def fetch_market_features(symbol: str) -> Dict:
    """Fetch current market features for a symbol"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5d")

        if hist.empty:
            return {}

        current_price = hist['Close'].iloc[-1]
        volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].mean()

        # Calculate simple RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).mean()
        loss = (-delta.where(delta < 0, 0)).mean()
        rs = gain / loss if loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))

        return {
            "price": round(current_price, 2),
            "volume": int(volume),
            "avg_volume": int(avg_volume),
            "volume_ratio": round(volume / avg_volume, 2) if avg_volume > 0 else 1.0,
            "rsi": round(rsi, 1),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "sector": info.get("sector"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "pct_from_high": round((current_price / info.get("fiftyTwoWeekHigh", current_price) - 1) * 100, 1) if info.get("fiftyTwoWeekHigh") else None
        }
    except Exception as e:
        print(f"[ML] Error fetching features for {symbol}: {e}")
        return {}


# CLI for testing
if __name__ == "__main__":
    collector = MLDataCollector()

    print("\n" + "=" * 60)
    print("ML DATA COLLECTION - Statistics")
    print("=" * 60)

    stats = collector.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nData files:")
    print(f"  Trades: {collector.trades_file}")
    print(f"  Features: {collector.features_file}")
    print(f"  Sentiment: {collector.sentiment_file}")
