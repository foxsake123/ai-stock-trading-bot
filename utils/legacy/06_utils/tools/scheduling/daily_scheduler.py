"""
Daily Scheduler for 7am Automation
Orchestrates daily catalyst screening and recommendation generation
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, time, timedelta
import pytz
from dataclasses import dataclass, asdict
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path

# Import agent modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agents.analysts.catalyst_screener import CatalystScreener
from agents.trader.options_strategist import OptionsStrategist
from agents.researchers.debate_engine import DebateEngine
from communication.daily_briefing import DailyBriefing
from config.settings import Config


@dataclass
class DailyRunResult:
    """Results from daily screening run"""
    run_date: datetime
    opportunities_found: int
    recommendations_made: int
    top_picks: List[Dict]
    execution_time: float
    errors: List[str]
    status: str
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['run_date'] = self.run_date.isoformat()
        return result


class DailyScheduler:
    """
    Automated daily screening and analysis system.
    Runs every trading day at 7am EST to discover and analyze catalyst opportunities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the daily scheduler"""
        self.config = Config(config_path) if config_path else Config()
        self.logger = self._setup_logging()
        
        # Set timezone
        self.timezone = pytz.timezone('US/Eastern')
        self.run_time = time(7, 0)  # 7:00 AM
        
        # Initialize components
        self.catalyst_screener = None
        self.options_strategist = None
        self.debate_engine = None
        self.daily_briefing = None
        
        # Email configuration
        self.email_enabled = self.config.get('email.enabled', False)
        self.email_recipients = self.config.get('email.recipients', [])
        
        # Performance tracking
        self.run_history = []
        self.max_history = 30  # Keep 30 days of history
        
        # State management
        self.is_running = False
        self.last_run = None
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration"""
        log_dir = Path('logs/scheduler')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)
    
    async def initialize_agents(self):
        """Initialize all required agents"""
        try:
            self.logger.info("Initializing agents...")
            
            # Initialize catalyst screener
            self.catalyst_screener = CatalystScreener(self.config.get('agents.catalyst_screener', {}))
            
            # Initialize options strategist
            self.options_strategist = OptionsStrategist(self.config.get('agents.options_strategist', {}))
            
            # Initialize debate engine
            self.debate_engine = DebateEngine(self.config.get('agents.debate_engine', {}))
            
            # Initialize daily briefing generator
            self.daily_briefing = DailyBriefing(self.config.get('communication.daily_briefing', {}))
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def schedule_daily_screening(self):
        """Schedule the daily screening task"""
        # Schedule for weekdays only
        schedule.every().monday.at(self.run_time.strftime("%H:%M")).do(self.run_daily_analysis)
        schedule.every().tuesday.at(self.run_time.strftime("%H:%M")).do(self.run_daily_analysis)
        schedule.every().wednesday.at(self.run_time.strftime("%H:%M")).do(self.run_daily_analysis)
        schedule.every().thursday.at(self.run_time.strftime("%H:%M")).do(self.run_daily_analysis)
        schedule.every().friday.at(self.run_time.strftime("%H:%M")).do(self.run_daily_analysis)
        
        self.logger.info(f"Daily screening scheduled for {self.run_time.strftime('%H:%M')} EST on weekdays")
    
    def run_daily_analysis(self):
        """Wrapper to run async analysis in sync context"""
        if self.is_running:
            self.logger.warning("Analysis already running, skipping...")
            return
        
        try:
            # Run the async function
            asyncio.run(self.execute_full_analysis_cycle())
        except Exception as e:
            self.logger.error(f"Daily analysis failed: {e}")
            self._send_error_notification(str(e))
    
    async def execute_full_analysis_cycle(self):
        """
        Execute the complete daily analysis cycle:
        1. Catalyst discovery
        2. Analysis by all agents
        3. Debate and consensus
        4. Strategy selection
        5. Briefing generation
        """
        self.is_running = True
        start_time = datetime.now()
        errors = []
        
        try:
            self.logger.info("=" * 80)
            self.logger.info(f"Starting daily analysis cycle at {start_time}")
            self.logger.info("=" * 80)
            
            # Check if market is open
            if not self._is_market_day():
                self.logger.info("Market is closed today, skipping analysis")
                return
            
            # Initialize agents if needed
            if not self.catalyst_screener:
                await self.initialize_agents()
            
            # Phase 1: Catalyst Discovery (7:00-7:05)
            self.logger.info("\n>>> PHASE 1: CATALYST DISCOVERY")
            catalysts = await self._run_catalyst_discovery()
            
            if not catalysts:
                self.logger.warning("No catalyst opportunities found today")
                await self._send_no_opportunities_briefing()
                return
            
            # Phase 2: Analysis Cycle (7:05-7:15)
            self.logger.info("\n>>> PHASE 2: ANALYSIS CYCLE")
            analyzed_opportunities = await self._run_analysis_cycle(catalysts)
            
            # Phase 3: Debate Phase (7:15-7:25)
            self.logger.info("\n>>> PHASE 3: DEBATE PHASE")
            debated_opportunities = await self._run_debate_phase(analyzed_opportunities)
            
            # Phase 4: Strategy Selection (7:25-7:30)
            self.logger.info("\n>>> PHASE 4: STRATEGY SELECTION")
            final_recommendations = await self._run_strategy_selection(debated_opportunities)
            
            # Phase 5: Briefing Generation (7:30-7:35)
            self.logger.info("\n>>> PHASE 5: BRIEFING GENERATION")
            briefing = await self._generate_morning_briefing(final_recommendations)
            
            # Send recommendations
            await self.send_recommendations(briefing)
            
            # Log performance
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_daily_performance(
                opportunities_found=len(catalysts),
                recommendations_made=len(final_recommendations),
                top_picks=final_recommendations[:5],
                execution_time=execution_time,
                errors=errors
            )
            
            self.logger.info(f"\n✓ Daily analysis completed in {execution_time:.1f} seconds")
            self.logger.info(f"  - Opportunities found: {len(catalysts)}")
            self.logger.info(f"  - Recommendations made: {len(final_recommendations)}")
            
        except Exception as e:
            self.logger.error(f"Analysis cycle failed: {e}")
            errors.append(str(e))
            self._send_error_notification(str(e))
            
        finally:
            self.is_running = False
            self.last_run = datetime.now()
    
    async def _run_catalyst_discovery(self) -> List[Dict]:
        """Run catalyst discovery phase"""
        try:
            self.logger.info("Scanning for catalyst opportunities...")
            
            # Get market data (mock for now)
            market_data = await self._fetch_market_data()
            
            # Run catalyst screener
            catalyst_report = await self.catalyst_screener.analyze(market_data)
            
            # Extract opportunities
            opportunities = catalyst_report.get('top_opportunities', [])
            
            self.logger.info(f"Found {len(opportunities)} catalyst opportunities")
            
            # Log summary by type
            by_type = catalyst_report.get('summary', {}).get('by_type', {})
            for catalyst_type, count in by_type.items():
                self.logger.info(f"  - {catalyst_type}: {count}")
            
            return opportunities[:20]  # Limit to top 20
            
        except Exception as e:
            self.logger.error(f"Catalyst discovery failed: {e}")
            return []
    
    async def _run_analysis_cycle(self, catalysts: List[Dict]) -> List[Dict]:
        """Run analysis on discovered catalysts"""
        analyzed = []
        
        for catalyst in catalysts:
            try:
                self.logger.info(f"Analyzing {catalyst['ticker']} ({catalyst['catalyst_type']})")
                
                # Run multiple analyses in parallel
                tasks = [
                    self._analyze_fundamentals(catalyst),
                    self._analyze_technicals(catalyst),
                    self._analyze_sentiment(catalyst),
                    self._analyze_news(catalyst)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Combine analysis results
                combined_analysis = {
                    **catalyst,
                    'fundamental_analysis': results[0] if not isinstance(results[0], Exception) else None,
                    'technical_analysis': results[1] if not isinstance(results[1], Exception) else None,
                    'sentiment_analysis': results[2] if not isinstance(results[2], Exception) else None,
                    'news_analysis': results[3] if not isinstance(results[3], Exception) else None
                }
                
                analyzed.append(combined_analysis)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze {catalyst.get('ticker')}: {e}")
        
        return analyzed
    
    async def _run_debate_phase(self, opportunities: List[Dict]) -> List[Dict]:
        """Run debate phase on analyzed opportunities"""
        debated = []
        
        # Sort by confidence and take top 10 for debate
        sorted_opps = sorted(opportunities, 
                           key=lambda x: x.get('confidence_score', 0), 
                           reverse=True)[:10]
        
        for opp in sorted_opps:
            try:
                self.logger.info(f"Debating {opp['ticker']} opportunity...")
                
                # Run debate
                debate_result = await self.debate_engine.analyze(opp)
                
                # Add debate outcome to opportunity
                opp['debate_result'] = debate_result
                opp['consensus_action'] = debate_result.get('recommendation', {}).get('action')
                opp['debate_confidence'] = debate_result.get('recommendation', {}).get('confidence')
                
                debated.append(opp)
                
            except Exception as e:
                self.logger.error(f"Debate failed for {opp.get('ticker')}: {e}")
        
        return debated
    
    async def _run_strategy_selection(self, opportunities: List[Dict]) -> List[Dict]:
        """Select optimal strategies for opportunities"""
        final_recommendations = []
        
        for opp in opportunities:
            # Skip if debate said AVOID
            if opp.get('consensus_action') == 'AVOID':
                continue
            
            try:
                self.logger.info(f"Selecting strategy for {opp['ticker']}...")
                
                # Get options strategy recommendation
                options_strategy = await self.options_strategist.analyze(opp)
                
                # Combine with risk management
                position_size = self._calculate_position_size(opp)
                
                # Create final recommendation
                recommendation = {
                    'ticker': opp['ticker'],
                    'catalyst_type': opp['catalyst_type'],
                    'catalyst_date': opp['catalyst_date'],
                    'action': opp.get('consensus_action', 'CONSIDER'),
                    'confidence': opp.get('debate_confidence', 0.5),
                    'expected_move': opp.get('expected_move', 0.1),
                    'options_strategy': options_strategy,
                    'position_size': position_size,
                    'entry_strategy': self._define_entry_strategy(opp),
                    'exit_strategy': self._define_exit_strategy(opp),
                    'stop_loss': -0.15,  # 15% stop loss
                    'risk_level': opp.get('risk_level', 'MEDIUM'),
                    'key_risks': opp.get('debate_result', {}).get('risk_assessment', {}).get('top_risks', [])
                }
                
                final_recommendations.append(recommendation)
                
            except Exception as e:
                self.logger.error(f"Strategy selection failed for {opp.get('ticker')}: {e}")
        
        # Sort by confidence
        final_recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return final_recommendations
    
    async def _generate_morning_briefing(self, recommendations: List[Dict]) -> Dict:
        """Generate the morning briefing"""
        try:
            briefing = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'market_conditions': await self._assess_market_conditions(),
                'total_recommendations': len(recommendations),
                'top_picks': recommendations[:5],
                'by_catalyst_type': self._group_by_catalyst_type(recommendations),
                'risk_summary': self._summarize_risk(recommendations),
                'execution_notes': self._generate_execution_notes(recommendations)
            }
            
            # Use daily briefing generator if available
            if self.daily_briefing:
                formatted_briefing = await self.daily_briefing.generate(briefing)
                return formatted_briefing
            
            return briefing
            
        except Exception as e:
            self.logger.error(f"Failed to generate briefing: {e}")
            return {'error': str(e), 'recommendations': recommendations}
    
    async def send_recommendations(self, briefing: Dict):
        """Send recommendations via configured channels"""
        try:
            # Save to file
            await self._save_briefing_to_file(briefing)
            
            # Send email if configured
            if self.email_enabled and self.email_recipients:
                await self._send_email_briefing(briefing)
            
            # Send to webhook if configured
            webhook_url = self.config.get('notifications.webhook_url')
            if webhook_url:
                await self._send_webhook_notification(briefing, webhook_url)
            
            # Log to console
            self._log_briefing_summary(briefing)
            
        except Exception as e:
            self.logger.error(f"Failed to send recommendations: {e}")
    
    def _log_daily_performance(self, opportunities_found: int, recommendations_made: int,
                              top_picks: List[Dict], execution_time: float, errors: List[str]):
        """Log daily performance metrics"""
        result = DailyRunResult(
            run_date=datetime.now(),
            opportunities_found=opportunities_found,
            recommendations_made=recommendations_made,
            top_picks=top_picks,
            execution_time=execution_time,
            errors=errors,
            status='success' if not errors else 'partial'
        )
        
        # Add to history
        self.run_history.append(result)
        
        # Trim history
        if len(self.run_history) > self.max_history:
            self.run_history = self.run_history[-self.max_history:]
        
        # Save to file
        self._save_performance_history()
        
    def _save_performance_history(self):
        """Save performance history to file"""
        try:
            history_file = Path('data/scheduler/performance_history.json')
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            history_data = [r.to_dict() for r in self.run_history]
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save performance history: {e}")
    
    # Helper methods
    def _is_market_day(self) -> bool:
        """Check if today is a trading day"""
        # This should integrate with market calendar
        # For now, check if weekday
        today = datetime.now().weekday()
        return today < 5  # Monday = 0, Friday = 4
    
    async def _fetch_market_data(self) -> Dict:
        """Fetch current market data"""
        # Mock implementation - integrate with real data sources
        return {
            'timestamp': datetime.now().isoformat(),
            'vix': 15.5,
            'spy_price': 450.0,
            'market_breadth': 0.65
        }
    
    async def _analyze_fundamentals(self, catalyst: Dict) -> Dict:
        """Run fundamental analysis on catalyst"""
        # Mock implementation - integrate with fundamental analyst agent
        return {
            'pe_ratio': 25.5,
            'earnings_growth': 0.15,
            'debt_to_equity': 0.8
        }
    
    async def _analyze_technicals(self, catalyst: Dict) -> Dict:
        """Run technical analysis on catalyst"""
        # Mock implementation - integrate with technical analyst agent
        return {
            'rsi': 65,
            'macd_signal': 'bullish',
            'support_level': 95.0,
            'resistance_level': 105.0
        }
    
    async def _analyze_sentiment(self, catalyst: Dict) -> Dict:
        """Run sentiment analysis on catalyst"""
        # Mock implementation - integrate with sentiment analyst agent
        return {
            'social_sentiment': 0.7,
            'options_sentiment': 'bullish',
            'analyst_sentiment': 'neutral'
        }
    
    async def _analyze_news(self, catalyst: Dict) -> Dict:
        """Run news analysis on catalyst"""
        # Mock implementation - integrate with news analyst agent
        return {
            'recent_news_sentiment': 'positive',
            'news_volume': 'high',
            'key_headlines': []
        }
    
    def _calculate_position_size(self, opportunity: Dict) -> str:
        """Calculate appropriate position size"""
        risk_level = opportunity.get('risk_level', 'MEDIUM')
        confidence = opportunity.get('debate_confidence', 0.5)
        
        if risk_level == 'HIGH':
            base_size = 0.005  # 0.5%
        elif risk_level == 'MEDIUM':
            base_size = 0.01   # 1%
        else:
            base_size = 0.02   # 2%
        
        # Adjust for confidence
        adjusted_size = base_size * confidence
        
        return f"{adjusted_size:.1%} of portfolio"
    
    def _define_entry_strategy(self, opportunity: Dict) -> str:
        """Define entry strategy for opportunity"""
        catalyst_type = opportunity.get('catalyst_type')
        
        strategies = {
            'earnings': 'Scale in 2-3 days before announcement',
            'fda_event': 'Full position 1 week before PDUFA',
            'technical_breakout': 'Enter on confirmed breakout with volume',
            'short_squeeze': 'Enter on first signs of squeeze (volume + price)',
            'options_flow': 'Follow smart money timing'
        }
        
        return strategies.get(catalyst_type, 'Enter on weakness/support')
    
    def _define_exit_strategy(self, opportunity: Dict) -> str:
        """Define exit strategy for opportunity"""
        catalyst_type = opportunity.get('catalyst_type')
        
        strategies = {
            'earnings': 'Exit before announcement or trail stop after',
            'fda_event': 'Hold through binary event',
            'technical_breakout': 'Trail stop at 10% or target resistance',
            'short_squeeze': 'Scale out into strength, trail stop',
            'options_flow': 'Exit when flow reverses or target hit'
        }
        
        return strategies.get(catalyst_type, 'Stop loss at -15%, target at +20%')
    
    async def _assess_market_conditions(self) -> Dict:
        """Assess overall market conditions"""
        # Mock implementation
        return {
            'trend': 'bullish',
            'volatility': 'moderate',
            'breadth': 'positive',
            'risk_on_off': 'risk_on'
        }
    
    def _group_by_catalyst_type(self, recommendations: List[Dict]) -> Dict[str, int]:
        """Group recommendations by catalyst type"""
        groups = {}
        for rec in recommendations:
            catalyst_type = rec.get('catalyst_type', 'unknown')
            groups[catalyst_type] = groups.get(catalyst_type, 0) + 1
        return groups
    
    def _summarize_risk(self, recommendations: List[Dict]) -> Dict:
        """Summarize risk across recommendations"""
        risk_levels = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
        
        for rec in recommendations:
            risk_level = rec.get('risk_level', 'MEDIUM')
            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        return {
            'distribution': risk_levels,
            'average_confidence': sum(r.get('confidence', 0) for r in recommendations) / max(len(recommendations), 1),
            'high_risk_percentage': risk_levels['HIGH'] / max(len(recommendations), 1)
        }
    
    def _generate_execution_notes(self, recommendations: List[Dict]) -> List[str]:
        """Generate execution notes for the day"""
        notes = []
        
        if not recommendations:
            notes.append("No actionable recommendations today")
            return notes
        
        # General market notes
        notes.append(f"Total opportunities: {len(recommendations)}")
        notes.append("Focus on top 3-5 picks with highest confidence")
        notes.append("Use stop losses on all positions")
        
        # Catalyst-specific notes
        catalyst_types = set(r.get('catalyst_type') for r in recommendations)
        if 'earnings' in catalyst_types:
            notes.append("Earnings plays: Consider IV crush risk")
        if 'fda_event' in catalyst_types:
            notes.append("FDA events: Binary outcomes - size appropriately")
        if 'short_squeeze' in catalyst_types:
            notes.append("Squeeze plays: Monitor borrow availability")
        
        return notes
    
    async def _save_briefing_to_file(self, briefing: Dict):
        """Save briefing to file"""
        try:
            briefing_dir = Path('data/briefings')
            briefing_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = briefing_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(briefing, f, indent=2, default=str)
            
            self.logger.info(f"Briefing saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save briefing: {e}")
    
    async def _send_email_briefing(self, briefing: Dict):
        """Send email briefing"""
        try:
            # Email configuration from config
            smtp_server = self.config.get('email.smtp_server')
            smtp_port = self.config.get('email.smtp_port', 587)
            sender_email = self.config.get('email.sender')
            sender_password = self.config.get('email.password')
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Daily Trading Briefing - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = sender_email
            msg['To'] = ', '.join(self.email_recipients)
            
            # Create email body
            html_body = self._format_email_body(briefing)
            
            # Attach HTML
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Email briefing sent to {len(self.email_recipients)} recipients")
            
        except Exception as e:
            self.logger.error(f"Failed to send email briefing: {e}")
    
    def _format_email_body(self, briefing: Dict) -> str:
        """Format briefing as HTML for email"""
        top_picks = briefing.get('top_picks', [])
        
        html = f"""
        <html>
        <body>
        <h2>Daily Trading Briefing - {briefing.get('date')}</h2>
        
        <h3>Market Conditions</h3>
        <ul>
            <li>Trend: {briefing.get('market_conditions', {}).get('trend')}</li>
            <li>Volatility: {briefing.get('market_conditions', {}).get('volatility')}</li>
        </ul>
        
        <h3>Top {len(top_picks)} Recommendations</h3>
        <table border="1" cellpadding="5">
            <tr>
                <th>Ticker</th>
                <th>Catalyst</th>
                <th>Action</th>
                <th>Confidence</th>
                <th>Position Size</th>
            </tr>
        """
        
        for pick in top_picks:
            html += f"""
            <tr>
                <td><b>{pick.get('ticker')}</b></td>
                <td>{pick.get('catalyst_type')}</td>
                <td>{pick.get('action')}</td>
                <td>{pick.get('confidence', 0):.1%}</td>
                <td>{pick.get('position_size')}</td>
            </tr>
            """
        
        html += """
        </table>
        
        <h3>Execution Notes</h3>
        <ul>
        """
        
        for note in briefing.get('execution_notes', []):
            html += f"<li>{note}</li>"
        
        html += """
        </ul>
        
        <p><i>This is an automated briefing. Please review all recommendations carefully before trading.</i></p>
        </body>
        </html>
        """
        
        return html
    
    async def _send_webhook_notification(self, briefing: Dict, webhook_url: str):
        """Send notification to webhook"""
        # Implementation for webhook notification
        pass
    
    def _log_briefing_summary(self, briefing: Dict):
        """Log briefing summary to console"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("DAILY BRIEFING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Date: {briefing.get('date')}")
        self.logger.info(f"Total Recommendations: {briefing.get('total_recommendations')}")
        
        self.logger.info("\nTOP PICKS:")
        for i, pick in enumerate(briefing.get('top_picks', [])[:5], 1):
            self.logger.info(f"{i}. {pick.get('ticker')} - {pick.get('catalyst_type')} "
                           f"({pick.get('confidence', 0):.1%} confidence)")
        
        self.logger.info("\nRISK SUMMARY:")
        risk_summary = briefing.get('risk_summary', {})
        self.logger.info(f"  Average Confidence: {risk_summary.get('average_confidence', 0):.1%}")
        self.logger.info(f"  High Risk Positions: {risk_summary.get('high_risk_percentage', 0):.1%}")
        
        self.logger.info("=" * 80 + "\n")
    
    async def _send_no_opportunities_briefing(self):
        """Send briefing when no opportunities found"""
        briefing = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'message': 'No catalyst opportunities found today',
            'recommendation': 'Stay in cash or focus on existing positions'
        }
        await self.send_recommendations(briefing)
    
    def _send_error_notification(self, error: str):
        """Send error notification"""
        self.logger.error(f"Sending error notification: {error}")
        # Implementation for error notification
    
    def start(self):
        """Start the scheduler"""
        self.logger.info("Starting daily scheduler...")
        
        # Initialize agents
        asyncio.run(self.initialize_agents())
        
        # Schedule daily task
        self.schedule_daily_screening()
        
        # Run scheduler loop
        self.logger.info("Scheduler started. Waiting for scheduled time...")
        
        try:
            while True:
                schedule.run_pending()
                asyncio.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
            raise
    
    def run_once(self):
        """Run analysis once immediately (for testing)"""
        self.logger.info("Running one-time analysis...")
        asyncio.run(self.execute_full_analysis_cycle())


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Trading Bot Scheduler')
    parser.add_argument('--once', action='store_true', help='Run once immediately')
    parser.add_argument('--config', type=str, help='Path to config file')
    
    args = parser.parse_args()
    
    scheduler = DailyScheduler(args.config)
    
    if args.once:
        scheduler.run_once()
    else:
        scheduler.start()


if __name__ == '__main__':
    main()