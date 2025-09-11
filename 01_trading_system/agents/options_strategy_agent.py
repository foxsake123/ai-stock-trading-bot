"""
Options Strategy Agent for Shorgan-Bot
Implements options strategies including debit spreads for catalyst plays
"""

from .base_agent import BaseAgent
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import yfinance as yf
import numpy as np
from scipy.stats import norm
import logging

class OptionsStrategyAgent(BaseAgent):
    """
    Specialized agent for options trading strategies
    Focus on debit spreads and other defined-risk strategies
    """
    
    def __init__(self):
        super().__init__(
            agent_id="shorgan_options_001",
            agent_type="options_trader"
        )
        
        # Strategy parameters
        self.max_debit_per_spread = 500  # Maximum debit per spread
        self.min_profit_ratio = 2.0      # Minimum profit/risk ratio
        self.max_days_to_expiry = 30     # Maximum DTE for catalyst plays
        self.min_days_to_expiry = 7      # Minimum DTE to avoid gamma risk
        
        # Greeks thresholds
        self.max_theta_decay = -0.10     # Maximum daily theta decay
        self.min_delta = 0.30             # Minimum delta for long options
        self.max_iv_percentile = 80      # Maximum IV percentile to buy
    
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze options opportunities for the given stock
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            catalyst_data: Catalyst information for timing
            
        Returns:
            Options strategy recommendation
        """
        try:
            catalyst_data = kwargs.get('catalyst_data', {})
            
            # Get options chain
            options_chain = self._get_options_chain(ticker)
            if not options_chain:
                return self._generate_no_options_result("No options available")
            
            # Determine strategy based on catalyst
            strategy = self._select_strategy(ticker, market_data, catalyst_data)
            
            # Find optimal strikes and expiration
            if strategy['type'] == 'bull_call_spread':
                trade_setup = self._setup_bull_call_spread(ticker, options_chain, market_data)
            elif strategy['type'] == 'bear_put_spread':
                trade_setup = self._setup_bear_put_spread(ticker, options_chain, market_data)
            elif strategy['type'] == 'long_straddle':
                trade_setup = self._setup_straddle(ticker, options_chain, market_data)
            else:
                trade_setup = None
            
            if not trade_setup:
                return self._generate_no_options_result("No suitable options setup found")
            
            # Calculate risk metrics
            risk_metrics = self._calculate_options_risk(trade_setup)
            
            # Generate recommendation
            recommendation = self._generate_options_recommendation(
                strategy, 
                trade_setup, 
                risk_metrics,
                catalyst_data
            )
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "strategy": strategy,
                    "trade_setup": trade_setup,
                    "greeks": self._calculate_greeks(trade_setup),
                    "catalyst_alignment": self._check_catalyst_alignment(trade_setup, catalyst_data)
                },
                "risk_assessment": risk_metrics,
                "confidence": self._calculate_options_confidence(trade_setup, risk_metrics, catalyst_data)
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Options analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Options analysis error: {str(e)}")
    
    def _get_options_chain(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get options chain data for the ticker
        
        Returns:
            Options chain data or None if unavailable
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get available expiration dates
            expirations = stock.options
            if not expirations:
                return None
            
            # Filter expirations within our timeframe
            valid_expirations = []
            for exp_date in expirations:
                exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                days_to_expiry = (exp_datetime - datetime.now()).days
                
                if self.min_days_to_expiry <= days_to_expiry <= self.max_days_to_expiry:
                    valid_expirations.append(exp_date)
            
            if not valid_expirations:
                return None
            
            # Get options data for valid expirations
            options_data = {}
            for exp_date in valid_expirations[:3]:  # Limit to 3 nearest expirations
                opt = stock.option_chain(exp_date)
                options_data[exp_date] = {
                    'calls': opt.calls,
                    'puts': opt.puts,
                    'expiration': exp_date
                }
            
            return options_data
            
        except Exception as e:
            self.logger.warning(f"Failed to get options chain for {ticker}: {str(e)}")
            return None
    
    def _select_strategy(self, ticker: str, market_data: Dict[str, Any], catalyst_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select appropriate options strategy based on market conditions and catalysts
        
        Returns:
            Strategy configuration
        """
        # Determine directional bias from catalyst
        catalyst_score = catalyst_data.get('total_score', 0)
        catalyst_type = catalyst_data.get('detected_catalysts', [{}])[0].get('type', '') if catalyst_data.get('detected_catalysts') else ''
        
        # Get current IV percentile
        iv_percentile = self._get_iv_percentile(ticker)
        
        # Binary event (earnings, FDA) = straddle/strangle
        if catalyst_type in ['earnings_announcement', 'fda_approval']:
            return {
                'type': 'long_straddle',
                'reasoning': f"Binary event catalyst: {catalyst_type}",
                'direction': 'neutral',
                'max_risk': self.max_debit_per_spread * 2
            }
        
        # High conviction bullish catalyst = bull call spread
        elif catalyst_score > 0.7:
            return {
                'type': 'bull_call_spread',
                'reasoning': f"Strong bullish catalyst (score: {catalyst_score:.2f})",
                'direction': 'bullish',
                'max_risk': self.max_debit_per_spread
            }
        
        # Bearish signals = bear put spread
        elif catalyst_type in ['analyst_downgrade', 'negative_news'] or catalyst_score < 0.3:
            return {
                'type': 'bear_put_spread',
                'reasoning': "Bearish catalyst detected",
                'direction': 'bearish',
                'max_risk': self.max_debit_per_spread
            }
        
        # Default to bull call spread for moderate bullish
        else:
            return {
                'type': 'bull_call_spread',
                'reasoning': "Moderate bullish outlook",
                'direction': 'bullish',
                'max_risk': self.max_debit_per_spread
            }
    
    def _setup_bull_call_spread(self, ticker: str, options_chain: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Setup a bull call spread (debit spread)
        
        Returns:
            Trade setup details or None
        """
        current_price = market_data.get('price', 0)
        
        best_spread = None
        best_score = 0
        
        for exp_date, chain_data in options_chain.items():
            calls = chain_data['calls']
            
            # Filter for liquid options
            liquid_calls = calls[calls['volume'] > 10]
            if liquid_calls.empty:
                continue
            
            # Find ATM and OTM strikes
            atm_strike = liquid_calls.iloc[(liquid_calls['strike'] - current_price).abs().argsort()[:1]]['strike'].values[0]
            otm_strikes = liquid_calls[liquid_calls['strike'] > atm_strike]['strike'].values[:3]  # Next 3 OTM strikes
            
            for otm_strike in otm_strikes:
                # Get option prices
                long_call = liquid_calls[liquid_calls['strike'] == atm_strike].iloc[0]
                short_call = liquid_calls[liquid_calls['strike'] == otm_strike].iloc[0]
                
                # Calculate spread metrics
                debit = long_call['lastPrice'] - short_call['lastPrice']
                max_profit = otm_strike - atm_strike - debit
                
                if debit <= 0 or debit > self.max_debit_per_spread:
                    continue
                
                profit_ratio = max_profit / debit if debit > 0 else 0
                
                # Score the spread
                score = self._score_spread(profit_ratio, debit, long_call['impliedVolatility'])
                
                if score > best_score:
                    best_score = score
                    best_spread = {
                        'type': 'bull_call_spread',
                        'expiration': exp_date,
                        'long_strike': atm_strike,
                        'short_strike': otm_strike,
                        'long_price': long_call['lastPrice'],
                        'short_price': short_call['lastPrice'],
                        'debit': debit,
                        'max_profit': max_profit,
                        'max_loss': debit,
                        'profit_ratio': profit_ratio,
                        'breakeven': atm_strike + debit,
                        'days_to_expiry': (datetime.strptime(exp_date, '%Y-%m-%d') - datetime.now()).days
                    }
        
        return best_spread
    
    def _setup_bear_put_spread(self, ticker: str, options_chain: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Setup a bear put spread (debit spread)
        
        Returns:
            Trade setup details or None
        """
        current_price = market_data.get('price', 0)
        
        best_spread = None
        best_score = 0
        
        for exp_date, chain_data in options_chain.items():
            puts = chain_data['puts']
            
            # Filter for liquid options
            liquid_puts = puts[puts['volume'] > 10]
            if liquid_puts.empty:
                continue
            
            # Find ATM and OTM strikes
            atm_strike = liquid_puts.iloc[(liquid_puts['strike'] - current_price).abs().argsort()[:1]]['strike'].values[0]
            otm_strikes = liquid_puts[liquid_puts['strike'] < atm_strike]['strike'].values[-3:]  # Next 3 OTM strikes
            
            for otm_strike in otm_strikes:
                # Get option prices
                long_put = liquid_puts[liquid_puts['strike'] == atm_strike].iloc[0]
                short_put = liquid_puts[liquid_puts['strike'] == otm_strike].iloc[0]
                
                # Calculate spread metrics
                debit = long_put['lastPrice'] - short_put['lastPrice']
                max_profit = atm_strike - otm_strike - debit
                
                if debit <= 0 or debit > self.max_debit_per_spread:
                    continue
                
                profit_ratio = max_profit / debit if debit > 0 else 0
                
                # Score the spread
                score = self._score_spread(profit_ratio, debit, long_put['impliedVolatility'])
                
                if score > best_score:
                    best_score = score
                    best_spread = {
                        'type': 'bear_put_spread',
                        'expiration': exp_date,
                        'long_strike': atm_strike,
                        'short_strike': otm_strike,
                        'long_price': long_put['lastPrice'],
                        'short_price': short_put['lastPrice'],
                        'debit': debit,
                        'max_profit': max_profit,
                        'max_loss': debit,
                        'profit_ratio': profit_ratio,
                        'breakeven': atm_strike - debit,
                        'days_to_expiry': (datetime.strptime(exp_date, '%Y-%m-%d') - datetime.now()).days
                    }
        
        return best_spread
    
    def _setup_straddle(self, ticker: str, options_chain: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Setup a long straddle for binary events
        
        Returns:
            Trade setup details or None
        """
        current_price = market_data.get('price', 0)
        
        best_straddle = None
        best_score = 0
        
        for exp_date, chain_data in options_chain.items():
            calls = chain_data['calls']
            puts = chain_data['puts']
            
            # Find ATM strike
            atm_strike = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:1]]['strike'].values[0]
            
            # Get ATM call and put
            atm_call = calls[calls['strike'] == atm_strike]
            atm_put = puts[puts['strike'] == atm_strike]
            
            if atm_call.empty or atm_put.empty:
                continue
            
            call_price = atm_call.iloc[0]['lastPrice']
            put_price = atm_put.iloc[0]['lastPrice']
            total_debit = call_price + put_price
            
            if total_debit > self.max_debit_per_spread * 2:
                continue
            
            # Calculate breakevens
            upper_breakeven = atm_strike + total_debit
            lower_breakeven = atm_strike - total_debit
            
            # Score based on expected move vs cost
            expected_move = self._calculate_expected_move(ticker, exp_date)
            score = expected_move / total_debit if total_debit > 0 else 0
            
            if score > best_score:
                best_score = score
                best_straddle = {
                    'type': 'long_straddle',
                    'expiration': exp_date,
                    'strike': atm_strike,
                    'call_price': call_price,
                    'put_price': put_price,
                    'total_debit': total_debit,
                    'upper_breakeven': upper_breakeven,
                    'lower_breakeven': lower_breakeven,
                    'max_loss': total_debit,
                    'expected_move': expected_move,
                    'days_to_expiry': (datetime.strptime(exp_date, '%Y-%m-%d') - datetime.now()).days
                }
        
        return best_straddle
    
    def _calculate_greeks(self, trade_setup: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate approximate Greeks for the position
        
        Returns:
            Dict of Greek values
        """
        # Simplified Greeks calculation
        days_to_expiry = trade_setup.get('days_to_expiry', 30)
        
        if trade_setup['type'] in ['bull_call_spread', 'bear_put_spread']:
            # Debit spread Greeks
            return {
                'delta': 0.40,  # Approximate for ATM spread
                'gamma': 0.02,
                'theta': -trade_setup.get('debit', 0) / days_to_expiry,
                'vega': 0.10
            }
        elif trade_setup['type'] == 'long_straddle':
            # Straddle Greeks
            return {
                'delta': 0.0,   # Delta neutral at inception
                'gamma': 0.05,  # High gamma
                'theta': -trade_setup.get('total_debit', 0) / days_to_expiry * 2,
                'vega': 0.20    # High vega
            }
        else:
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    
    def _calculate_options_risk(self, trade_setup: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk metrics for the options trade
        
        Returns:
            Risk assessment
        """
        max_loss = trade_setup.get('max_loss', trade_setup.get('debit', 0))
        max_profit = trade_setup.get('max_profit', 0)
        profit_ratio = max_profit / max_loss if max_loss > 0 else 0
        
        # Risk level based on position type and metrics
        if trade_setup['type'] == 'long_straddle':
            risk_level = "HIGH"  # Binary outcome trade
        elif profit_ratio >= 3:
            risk_level = "LOW"
        elif profit_ratio >= 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            'risk_level': risk_level,
            'max_loss': max_loss,
            'max_profit': max_profit,
            'profit_ratio': profit_ratio,
            'breakeven': trade_setup.get('breakeven', 0),
            'position_size': self._calculate_position_size(max_loss),
            'days_to_expiry': trade_setup.get('days_to_expiry', 0)
        }
    
    def _calculate_position_size(self, max_loss: float) -> int:
        """
        Calculate appropriate position size based on risk
        
        Args:
            max_loss: Maximum loss per contract
            
        Returns:
            Number of contracts to trade
        """
        # Risk 2% of portfolio per trade, assuming $100k portfolio
        portfolio_value = 100000
        risk_per_trade = portfolio_value * 0.02
        
        contracts = int(risk_per_trade / (max_loss * 100))  # Options are 100 shares per contract
        return max(1, min(contracts, 10))  # Between 1 and 10 contracts
    
    def _check_catalyst_alignment(self, trade_setup: Dict[str, Any], catalyst_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if options expiration aligns with catalyst timing
        
        Returns:
            Alignment assessment
        """
        days_to_expiry = trade_setup.get('days_to_expiry', 30)
        
        # Check catalyst timing
        catalyst_timing = "unknown"
        urgency = catalyst_data.get('urgency', 'LOW')
        
        for catalyst in catalyst_data.get('detected_catalysts', []):
            if 'days_until' in catalyst:
                catalyst_days = catalyst['days_until']
                if catalyst_days <= days_to_expiry:
                    catalyst_timing = "before_expiry"
                else:
                    catalyst_timing = "after_expiry"
                break
        
        # Determine alignment quality
        if catalyst_timing == "before_expiry" and urgency in ['IMMEDIATE', 'HIGH']:
            alignment = "EXCELLENT"
        elif catalyst_timing == "before_expiry":
            alignment = "GOOD"
        elif catalyst_timing == "after_expiry":
            alignment = "POOR"
        else:
            alignment = "UNCERTAIN"
        
        return {
            'alignment': alignment,
            'catalyst_timing': catalyst_timing,
            'days_to_expiry': days_to_expiry,
            'urgency': urgency
        }
    
    def _generate_options_recommendation(self, strategy: Dict, trade_setup: Dict, 
                                        risk_metrics: Dict, catalyst_data: Dict) -> Dict[str, Any]:
        """
        Generate final options trading recommendation
        
        Returns:
            Trading recommendation
        """
        # Determine action based on setup quality
        if trade_setup and risk_metrics['profit_ratio'] >= self.min_profit_ratio:
            action = "EXECUTE"
            confidence = min(0.9, risk_metrics['profit_ratio'] / 3)
        elif trade_setup:
            action = "CONSIDER"
            confidence = 0.5
        else:
            action = "SKIP"
            confidence = 0.0
        
        return {
            'action': action,
            'strategy_type': strategy['type'],
            'confidence': confidence,
            'trade_details': trade_setup,
            'contracts': risk_metrics.get('position_size', 1),
            'reasoning': self._generate_options_reasoning(strategy, trade_setup, risk_metrics, catalyst_data)
        }
    
    def _generate_options_reasoning(self, strategy: Dict, trade_setup: Dict, 
                                   risk_metrics: Dict, catalyst_data: Dict) -> str:
        """Generate reasoning for options recommendation"""
        reasons = []
        
        reasons.append(f"{strategy['type'].replace('_', ' ').title()} strategy")
        
        if trade_setup:
            reasons.append(f"{risk_metrics['profit_ratio']:.1f}:1 profit/risk ratio")
            reasons.append(f"{trade_setup['days_to_expiry']} days to expiry")
        
        if catalyst_data.get('urgency') == 'IMMEDIATE':
            reasons.append("immediate catalyst trigger")
        
        return f"Options play: {', '.join(reasons)}"
    
    def _score_spread(self, profit_ratio: float, debit: float, iv: float) -> float:
        """Score a debit spread based on metrics"""
        # Higher profit ratio is better
        profit_score = min(1.0, profit_ratio / 3)
        
        # Lower debit relative to max is better
        debit_score = 1.0 - (debit / self.max_debit_per_spread)
        
        # Moderate IV is optimal (not too high, not too low)
        if 0.3 <= iv <= 0.6:
            iv_score = 1.0
        elif iv < 0.3:
            iv_score = iv / 0.3
        else:
            iv_score = max(0.3, 1.0 - (iv - 0.6))
        
        return (profit_score * 0.5 + debit_score * 0.3 + iv_score * 0.2)
    
    def _calculate_expected_move(self, ticker: str, expiration: str) -> float:
        """Calculate expected move based on IV"""
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            # Use ATM IV as proxy
            opt = stock.option_chain(expiration)
            atm_iv = opt.calls.iloc[0]['impliedVolatility']  # Simplified
            
            days_to_expiry = (datetime.strptime(expiration, '%Y-%m-%d') - datetime.now()).days
            
            # Expected move = price * IV * sqrt(days/365)
            expected_move = current_price * atm_iv * np.sqrt(days_to_expiry / 365)
            
            return expected_move
            
        except:
            return 0
    
    def _get_iv_percentile(self, ticker: str) -> float:
        """Get current IV percentile for the ticker"""
        # Simplified - would need historical IV data for accurate calculation
        return 50.0  # Default to 50th percentile
    
    def _generate_no_options_result(self, reason: str) -> Dict[str, Any]:
        """Generate result when no options trade is available"""
        return {
            "recommendation": {"action": "SKIP", "confidence": 0.0, "strategy_type": "none"},
            "analysis": {"reason": reason},
            "risk_assessment": {"risk_level": "N/A"},
            "confidence": 0.0
        }