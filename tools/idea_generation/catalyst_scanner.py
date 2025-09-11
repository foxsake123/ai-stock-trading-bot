"""
Catalyst Scanner - Main orchestrator for daily idea generation
Coordinates all screening modules to find catalyst-driven opportunities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiohttp
import pandas as pd
import numpy as np


@dataclass
class CatalystAlert:
    """Real-time catalyst alert"""
    ticker: str
    alert_type: str
    urgency: str  # immediate, today, this_week
    message: str
    action_required: str
    confidence: float
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class CatalystScanner:
    """
    Main catalyst scanner that orchestrates all screening modules
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Market filters
        self.min_market_cap = self.config.get('min_market_cap', 1e9)  # $1B
        self.max_market_cap = self.config.get('max_market_cap', 500e9)  # $500B
        self.min_volume = self.config.get('min_volume', 1000000)
        self.min_price = self.config.get('min_price', 5.0)
        
        # Screening modules (to be initialized)
        self.earnings_scanner = None
        self.fda_scanner = None
        self.technical_scanner = None
        self.squeeze_scanner = None
        self.options_scanner = None
        
        # Cache for daily results
        self.daily_cache = {}
        self.last_scan_time = None
        
    async def initialize_scanners(self):
        """Initialize all scanning modules"""
        try:
            from .earnings_calendar import EarningsScanner
            from .fda_calendar import FDAScanner
            from .technical_screener import TechnicalScreener
            from .short_squeeze_scanner import SqueezeScanner
            from .options_flow_analyzer import OptionsFlowAnalyzer
            
            self.earnings_scanner = EarningsScanner(self.config)
            self.fda_scanner = FDAScanner(self.config)
            self.technical_scanner = TechnicalScreener(self.config)
            self.squeeze_scanner = SqueezeScanner(self.config)
            self.options_scanner = OptionsFlowAnalyzer(self.config)
            
            self.logger.info("All scanners initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scanners: {e}")
            raise
    
    async def run_full_scan(self, 
                           scan_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run complete catalyst scan across all modules
        
        Args:
            scan_types: Optional list of scan types to run. If None, runs all.
                       Options: ['earnings', 'fda', 'technical', 'squeeze', 'options']
        
        Returns:
            Dictionary containing all catalyst opportunities found
        """
        start_time = datetime.now()
        
        # Default to all scan types
        if scan_types is None:
            scan_types = ['earnings', 'fda', 'technical', 'squeeze', 'options']
        
        self.logger.info(f"Starting catalyst scan for types: {scan_types}")
        
        # Initialize scanners if needed
        if not self.earnings_scanner:
            await self.initialize_scanners()
        
        # Run scans in parallel
        scan_tasks = []
        
        if 'earnings' in scan_types:
            scan_tasks.append(self._scan_earnings())
        if 'fda' in scan_types:
            scan_tasks.append(self._scan_fda())
        if 'technical' in scan_types:
            scan_tasks.append(self._scan_technical())
        if 'squeeze' in scan_types:
            scan_tasks.append(self._scan_squeeze())
        if 'options' in scan_types:
            scan_tasks.append(self._scan_options())
        
        # Execute all scans
        results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        # Process results
        all_opportunities = []
        scan_results = {}
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Scan failed: {result}")
                continue
            
            scan_type = scan_types[i] if i < len(scan_types) else 'unknown'
            scan_results[scan_type] = result
            
            if isinstance(result, list):
                all_opportunities.extend(result)
        
        # Rank and filter opportunities
        ranked_opportunities = self._rank_opportunities(all_opportunities)
        
        # Generate alerts for high-priority opportunities
        alerts = self._generate_alerts(ranked_opportunities[:10])
        
        # Cache results
        self.daily_cache = {
            'timestamp': datetime.now().isoformat(),
            'opportunities': ranked_opportunities,
            'alerts': alerts,
            'scan_results': scan_results,
            'execution_time': (datetime.now() - start_time).total_seconds()
        }
        
        self.last_scan_time = datetime.now()
        
        # Create summary report
        report = self._create_scan_report(ranked_opportunities, alerts, scan_results)
        
        self.logger.info(f"Scan completed in {self.daily_cache['execution_time']:.2f} seconds")
        self.logger.info(f"Found {len(all_opportunities)} total opportunities")
        
        return report
    
    async def _scan_earnings(self) -> List[Dict]:
        """Scan for earnings catalysts"""
        try:
            opportunities = await self.earnings_scanner.scan_upcoming_earnings(
                days_ahead=30,
                min_historical_move=0.05,  # 5% minimum historical move
                min_beat_rate=0.60  # 60% historical beat rate
            )
            
            self.logger.info(f"Earnings scan found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Earnings scan failed: {e}")
            return []
    
    async def _scan_fda(self) -> List[Dict]:
        """Scan for FDA catalysts"""
        try:
            opportunities = await self.fda_scanner.scan_upcoming_events(
                days_ahead=60,  # Look further out for FDA events
                phases=['Phase 2', 'Phase 3', 'NDA', 'PDUFA']
            )
            
            self.logger.info(f"FDA scan found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"FDA scan failed: {e}")
            return []
    
    async def _scan_technical(self) -> List[Dict]:
        """Scan for technical breakouts"""
        try:
            opportunities = await self.technical_scanner.scan_breakouts(
                min_volume_ratio=2.0,  # 2x average volume
                min_rs_rating=80,  # Relative strength > 80
                patterns=['breakout', 'flag', 'pennant', 'cup_handle']
            )
            
            self.logger.info(f"Technical scan found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Technical scan failed: {e}")
            return []
    
    async def _scan_squeeze(self) -> List[Dict]:
        """Scan for short squeeze candidates"""
        try:
            opportunities = await self.squeeze_scanner.scan_squeeze_candidates(
                min_short_interest=0.20,  # 20% short interest
                min_days_to_cover=3,
                min_borrow_rate=30  # 30% borrow rate
            )
            
            self.logger.info(f"Squeeze scan found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Squeeze scan failed: {e}")
            return []
    
    async def _scan_options(self) -> List[Dict]:
        """Scan for unusual options activity"""
        try:
            opportunities = await self.options_scanner.scan_unusual_activity(
                min_volume_ratio=3.0,  # 3x average options volume
                min_call_put_ratio=2.0,  # Bullish skew
                min_premium_spent=1000000  # $1M+ in premium
            )
            
            self.logger.info(f"Options scan found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Options scan failed: {e}")
            return []
    
    def _rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Rank opportunities by composite score
        """
        for opp in opportunities:
            # Calculate composite score based on multiple factors
            confidence = opp.get('confidence_score', 0.5)
            expected_move = opp.get('expected_move', 0.05)
            days_to_catalyst = opp.get('days_to_catalyst', 30)
            volume_interest = opp.get('volume_ratio', 1.0)
            
            # Time decay factor (urgency)
            time_factor = 1.0 if days_to_catalyst <= 5 else \
                         0.8 if days_to_catalyst <= 10 else \
                         0.6 if days_to_catalyst <= 20 else 0.4
            
            # Volume interest factor
            volume_factor = min(volume_interest / 3.0, 1.0)  # Cap at 1.0
            
            # Risk adjustment
            risk_level = opp.get('risk_level', 'MEDIUM')
            risk_factor = 0.6 if risk_level == 'HIGH' else \
                         0.8 if risk_level == 'MEDIUM' else 1.0
            
            # Composite score
            opp['composite_score'] = (
                confidence * 0.35 +
                expected_move * 10 * 0.25 +  # Scale expected move
                time_factor * 0.20 +
                volume_factor * 0.10 +
                risk_factor * 0.10
            )
            
            # Add ranking metadata
            opp['rank_factors'] = {
                'confidence': confidence,
                'expected_move': expected_move,
                'time_factor': time_factor,
                'volume_factor': volume_factor,
                'risk_factor': risk_factor
            }
        
        # Sort by composite score
        ranked = sorted(opportunities, key=lambda x: x['composite_score'], reverse=True)
        
        # Add rank number
        for i, opp in enumerate(ranked, 1):
            opp['rank'] = i
        
        return ranked
    
    def _generate_alerts(self, top_opportunities: List[Dict]) -> List[CatalystAlert]:
        """
        Generate actionable alerts for top opportunities
        """
        alerts = []
        
        for opp in top_opportunities:
            # Determine urgency
            days_to_catalyst = opp.get('days_to_catalyst', 30)
            if days_to_catalyst <= 1:
                urgency = 'immediate'
            elif days_to_catalyst <= 7:
                urgency = 'this_week'
            else:
                urgency = 'upcoming'
            
            # Create alert message
            ticker = opp.get('ticker', 'UNKNOWN')
            catalyst_type = opp.get('catalyst_type', 'unknown')
            expected_move = opp.get('expected_move', 0.05)
            
            message = f"{ticker}: {catalyst_type.replace('_', ' ').title()} catalyst in {days_to_catalyst} days. " \
                     f"Expected move: {expected_move:.0%}. " \
                     f"Confidence: {opp.get('confidence_score', 0):.0%}"
            
            # Determine action
            if opp.get('composite_score', 0) > 0.7:
                action = f"Consider entering {ticker} position today"
            elif opp.get('composite_score', 0) > 0.5:
                action = f"Add {ticker} to watchlist"
            else:
                action = f"Monitor {ticker} for better entry"
            
            alert = CatalystAlert(
                ticker=ticker,
                alert_type=catalyst_type,
                urgency=urgency,
                message=message,
                action_required=action,
                confidence=opp.get('confidence_score', 0),
                timestamp=datetime.now()
            )
            
            alerts.append(alert)
        
        return alerts
    
    def _create_scan_report(self, opportunities: List[Dict], 
                          alerts: List[CatalystAlert], 
                          scan_results: Dict) -> Dict[str, Any]:
        """
        Create comprehensive scan report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_opportunities': len(opportunities),
                'high_confidence': len([o for o in opportunities if o.get('confidence_score', 0) > 0.7]),
                'immediate_action': len([a for a in alerts if a.urgency == 'immediate']),
                'by_catalyst_type': self._count_by_type(opportunities),
                'by_risk_level': self._count_by_risk(opportunities)
            },
            'top_opportunities': opportunities[:20],
            'alerts': [alert.to_dict() for alert in alerts],
            'scan_details': {
                'earnings_found': len(scan_results.get('earnings', [])),
                'fda_found': len(scan_results.get('fda', [])),
                'technical_found': len(scan_results.get('technical', [])),
                'squeeze_found': len(scan_results.get('squeeze', [])),
                'options_found': len(scan_results.get('options', []))
            },
            'execution_metrics': {
                'scan_time': self.daily_cache.get('execution_time', 0),
                'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None
            }
        }
        
        return report
    
    def _count_by_type(self, opportunities: List[Dict]) -> Dict[str, int]:
        """Count opportunities by catalyst type"""
        counts = {}
        for opp in opportunities:
            catalyst_type = opp.get('catalyst_type', 'unknown')
            counts[catalyst_type] = counts.get(catalyst_type, 0) + 1
        return counts
    
    def _count_by_risk(self, opportunities: List[Dict]) -> Dict[str, int]:
        """Count opportunities by risk level"""
        counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
        for opp in opportunities:
            risk_level = opp.get('risk_level', 'MEDIUM')
            counts[risk_level] = counts.get(risk_level, 0) + 1
        return counts
    
    async def get_real_time_alerts(self, 
                                  ticker: Optional[str] = None) -> List[CatalystAlert]:
        """
        Get real-time alerts for specific ticker or all monitored tickers
        """
        if not self.daily_cache or not self.last_scan_time:
            # Run scan if no cache
            await self.run_full_scan()
        
        # Check if cache is stale (older than 1 hour)
        if self.last_scan_time and (datetime.now() - self.last_scan_time).seconds > 3600:
            self.logger.info("Cache is stale, running new scan")
            await self.run_full_scan()
        
        alerts = self.daily_cache.get('alerts', [])
        
        if ticker:
            # Filter for specific ticker
            alerts = [a for a in alerts if a.ticker == ticker]
        
        return alerts
    
    async def monitor_intraday_changes(self, watchlist: List[str]) -> List[Dict]:
        """
        Monitor intraday changes for watchlist tickers
        """
        changes = []
        
        for ticker in watchlist:
            try:
                # Check for volume surges
                volume_change = await self._check_volume_surge(ticker)
                if volume_change > 2.0:  # 2x normal volume
                    changes.append({
                        'ticker': ticker,
                        'alert_type': 'volume_surge',
                        'value': volume_change,
                        'message': f"{ticker}: Volume surge {volume_change:.1f}x normal"
                    })
                
                # Check for price breakouts
                price_change = await self._check_price_breakout(ticker)
                if abs(price_change) > 0.03:  # 3% move
                    changes.append({
                        'ticker': ticker,
                        'alert_type': 'price_move',
                        'value': price_change,
                        'message': f"{ticker}: Price move {price_change:.1%}"
                    })
                
                # Check for options flow changes
                options_change = await self._check_options_flow(ticker)
                if options_change:
                    changes.append({
                        'ticker': ticker,
                        'alert_type': 'options_flow',
                        'value': options_change,
                        'message': f"{ticker}: Unusual options activity detected"
                    })
                    
            except Exception as e:
                self.logger.error(f"Error monitoring {ticker}: {e}")
        
        return changes
    
    async def _check_volume_surge(self, ticker: str) -> float:
        """Check for volume surge in ticker"""
        # Placeholder - implement with real data
        return 1.0
    
    async def _check_price_breakout(self, ticker: str) -> float:
        """Check for price breakout"""
        # Placeholder - implement with real data
        return 0.0
    
    async def _check_options_flow(self, ticker: str) -> Optional[Dict]:
        """Check for unusual options flow"""
        # Placeholder - implement with real data
        return None
    
    def get_cached_results(self) -> Optional[Dict]:
        """Get cached scan results if available"""
        if self.daily_cache and self.last_scan_time:
            # Check if cache is fresh (less than 1 hour old)
            if (datetime.now() - self.last_scan_time).seconds < 3600:
                return self.daily_cache
        return None
    
    async def export_opportunities(self, 
                                  format: str = 'json',
                                  filepath: Optional[str] = None) -> str:
        """
        Export opportunities to file
        
        Args:
            format: Export format ('json', 'csv', 'html')
            filepath: Optional filepath, auto-generated if None
        
        Returns:
            Path to exported file
        """
        if not self.daily_cache:
            await self.run_full_scan()
        
        opportunities = self.daily_cache.get('opportunities', [])
        
        if not filepath:
            from pathlib import Path
            export_dir = Path('data/exports')
            export_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = export_dir / f"opportunities_{timestamp}.{format}"
        
        if format == 'json':
            import json
            with open(filepath, 'w') as f:
                json.dump(opportunities, f, indent=2, default=str)
                
        elif format == 'csv':
            df = pd.DataFrame(opportunities)
            df.to_csv(filepath, index=False)
            
        elif format == 'html':
            df = pd.DataFrame(opportunities)
            html = df.to_html(index=False, classes='table table-striped')
            with open(filepath, 'w') as f:
                f.write(html)
        
        self.logger.info(f"Exported {len(opportunities)} opportunities to {filepath}")
        return str(filepath)