"""
Execute Trades with OpenAI Research Integration
Combines AI-generated research with automated trading execution
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import asyncio

# Add necessary paths
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / '03_Research_Reports'))
sys.path.append(str(Path(__file__).parent.parent / '04_Bot_Strategies'))

from openai_research_analyzer import OpenAIResearchAnalyzer
from automated_research_pipeline import AutomatedResearchPipeline, ResearchExecutor

# Import trading modules
sys.path.append(str(Path(__file__).parent.parent / '01_Trading_Scripts'))
from place_alpaca_orders_enhanced import AlpacaBotTrader

class AITradingOrchestrator:
    """
    Orchestrates AI research generation and trade execution
    """
    
    def __init__(self):
        self.research_pipeline = AutomatedResearchPipeline()
        self.executor = ResearchExecutor()
        self.dee_trader = AlpacaBotTrader("DEE")
        self.shorgan_trader = AlpacaBotTrader("SHORGAN")
        
    def run_complete_workflow(self):
        """Run complete workflow: Research -> Analysis -> Execution"""
        
        print("=" * 70)
        print("AI-POWERED TRADING WORKFLOW")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)
        
        # Step 1: Generate AI Research
        print("\n📊 STEP 1: GENERATING AI RESEARCH")
        print("-" * 50)
        
        try:
            research = self.research_pipeline.generate_daily_research()
            
            if not research:
                print("❌ Failed to generate research")
                return False
                
            print("✅ Research generated successfully")
            
        except Exception as e:
            print(f"❌ Research generation error: {e}")
            return False
        
        # Step 2: Review and Validate Recommendations
        print("\n🔍 STEP 2: VALIDATING RECOMMENDATIONS")
        print("-" * 50)
        
        valid_trades = self.validate_recommendations(research)
        
        # Step 3: Execute DEE-BOT Trades
        print("\n🏛️ STEP 3: EXECUTING DEE-BOT TRADES")
        print("-" * 50)
        
        dee_success = self.execute_dee_bot_trades(valid_trades.get('dee_bot', []))
        
        # Step 4: Execute SHORGAN-BOT Trades
        print("\n🚀 STEP 4: EXECUTING SHORGAN-BOT TRADES")
        print("-" * 50)
        
        shorgan_success = self.execute_shorgan_bot_trades(valid_trades.get('shorgan_bot', []))
        
        # Step 5: Generate Summary Report
        print("\n📄 STEP 5: GENERATING SUMMARY")
        print("-" * 50)
        
        self.generate_execution_summary(research, valid_trades, dee_success, shorgan_success)
        
        print("\n" + "=" * 70)
        print("✅ WORKFLOW COMPLETE")
        print("=" * 70)
        
        return True
    
    def validate_recommendations(self, research: dict) -> dict:
        """Validate AI recommendations against risk rules"""
        
        validated = {
            'dee_bot': [],
            'shorgan_bot': []
        }
        
        if not research.get('morning_brief'):
            return validated
        
        # Validate DEE-BOT trades
        for trade in research['morning_brief'].get('dee_bot_trades', []):
            # Check risk/reward ratio
            entry = trade.get('entry', 0)
            stop = trade.get('stop', 0)
            target = trade.get('target', 0)
            
            if entry > 0 and stop > 0 and target > 0:
                risk = abs(entry - stop)
                reward = abs(target - entry)
                
                if reward / risk >= 2:  # Minimum 2:1 risk/reward
                    validated['dee_bot'].append(trade)
                    print(f"  ✓ {trade['ticker']}: R/R {reward/risk:.1f}:1 - APPROVED")
                else:
                    print(f"  ✗ {trade['ticker']}: R/R {reward/risk:.1f}:1 - REJECTED (< 2:1)")
        
        # Validate SHORGAN-BOT trades
        for trade in research['morning_brief'].get('shorgan_bot_trades', []):
            # Check catalyst strength (simplified)
            if trade.get('catalyst') and len(trade['catalyst']) > 10:
                validated['shorgan_bot'].append(trade)
                print(f"  ✓ {trade['ticker']}: Catalyst confirmed - APPROVED")
            else:
                print(f"  ✗ {trade['ticker']}: Weak catalyst - REJECTED")
        
        return validated
    
    def execute_dee_bot_trades(self, trades: list) -> bool:
        """Execute DEE-BOT institutional trades"""
        
        if not trades:
            print("  No validated DEE-BOT trades to execute")
            return True
        
        # Connect to Alpaca
        if not self.dee_trader.connect_to_alpaca():
            print("  ❌ Failed to connect to DEE-BOT Alpaca account")
            return False
        
        executed = 0
        for trade in trades:
            try:
                # Calculate position size (simplified)
                qty = 100  # Default 100 shares for institutional trades
                
                print(f"\n  Placing order: {trade['ticker']}")
                print(f"    Entry: ${trade['entry']:.2f}")
                print(f"    Stop: ${trade['stop']:.2f}")
                print(f"    Target: ${trade['target']:.2f}")
                print(f"    Reasoning: {trade['reasoning'][:50]}...")
                
                # Place market order (simplified - should use limit orders in production)
                order = self.dee_trader.place_order(
                    symbol=trade['ticker'],
                    qty=qty,
                    side='buy'
                )
                
                if order:
                    executed += 1
                    print(f"    ✅ Order placed successfully")
                else:
                    print(f"    ⚠️ Order failed")
                    
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:50]}")
        
        print(f"\n  Summary: {executed}/{len(trades)} trades executed")
        return executed > 0
    
    def execute_shorgan_bot_trades(self, trades: list) -> bool:
        """Execute SHORGAN-BOT catalyst trades"""
        
        if not trades:
            print("  No validated SHORGAN-BOT trades to execute")
            return True
        
        # Connect to Alpaca
        if not self.shorgan_trader.connect_to_alpaca():
            print("  ❌ Failed to connect to SHORGAN-BOT Alpaca account")
            return False
        
        executed = 0
        for trade in trades:
            try:
                # Calculate position size (more aggressive for catalysts)
                qty = 50  # Smaller positions for higher risk
                
                print(f"\n  Placing catalyst trade: {trade['ticker']}")
                print(f"    Entry: ${trade['entry']:.2f}")
                print(f"    Stop: ${trade['stop']:.2f}")
                print(f"    Target: ${trade['target']:.2f}")
                print(f"    Catalyst: {trade['catalyst'][:50]}...")
                
                # Place market order
                order = self.shorgan_trader.place_order(
                    symbol=trade['ticker'],
                    qty=qty,
                    side='buy'
                )
                
                if order:
                    executed += 1
                    print(f"    ✅ Order placed successfully")
                else:
                    print(f"    ⚠️ Order failed")
                    
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:50]}")
        
        print(f"\n  Summary: {executed}/{len(trades)} trades executed")
        return executed > 0
    
    def generate_execution_summary(self, research, valid_trades, dee_success, shorgan_success):
        """Generate execution summary report"""
        
        summary = {
            'execution_date': datetime.now().isoformat(),
            'research_generated': bool(research),
            'dee_bot': {
                'recommendations': len(research.get('morning_brief', {}).get('dee_bot_trades', [])),
                'validated': len(valid_trades.get('dee_bot', [])),
                'executed': dee_success
            },
            'shorgan_bot': {
                'recommendations': len(research.get('morning_brief', {}).get('shorgan_bot_trades', [])),
                'validated': len(valid_trades.get('shorgan_bot', [])),
                'executed': shorgan_success
            },
            'market_outlook': research.get('morning_brief', {}).get('market_outlook', 'N/A')
        }
        
        # Save summary
        summary_dir = Path("03_Research_Reports/Daily/execution_summaries")
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        filename = summary_dir / f"execution_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Execution Summary:")
        print(f"  DEE-BOT: {summary['dee_bot']['validated']} trades validated, execution {'✅' if dee_success else '❌'}")
        print(f"  SHORGAN-BOT: {summary['shorgan_bot']['validated']} trades validated, execution {'✅' if shorgan_success else '❌'}")
        print(f"  Market Outlook: {summary['market_outlook']}")
        print(f"\n  Summary saved to: {filename}")


def main():
    """Main entry point"""
    
    print("\n" + "=" * 70)
    print("OpenAI-POWERED TRADING SYSTEM")
    print("=" * 70)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("\n⚠️  OpenAI API key not configured!")
        print("\nTo use this system:")
        print("1. Sign up at: https://platform.openai.com/")
        print("2. Create API key: https://platform.openai.com/api-keys")
        print("3. Add to 08_Configuration/.env:")
        print("   OPENAI_API_KEY=sk-...")
        print("\n💡 OpenAI pricing: ~$0.01-0.03 per analysis")
        return
    
    # Run orchestrator
    orchestrator = AITradingOrchestrator()
    
    import argparse
    parser = argparse.ArgumentParser(description='AI Trading Orchestrator')
    parser.add_argument('--full', action='store_true', help='Run full workflow')
    parser.add_argument('--research-only', action='store_true', help='Generate research only')
    parser.add_argument('--execute-only', action='store_true', help='Execute existing research')
    
    args = parser.parse_args()
    
    if args.full:
        orchestrator.run_complete_workflow()
    elif args.research_only:
        research = orchestrator.research_pipeline.generate_daily_research()
        if research:
            print("\n✅ Research generated successfully!")
            print(f"   Market outlook: {research.get('morning_brief', {}).get('market_outlook', 'N/A')}")
    elif args.execute_only:
        # Load today's research and execute
        today = datetime.now().strftime('%Y%m%d')
        research_files = list(Path("03_Research_Reports/Daily").glob(f"research_{today}*.json"))
        if research_files:
            with open(research_files[-1], 'r') as f:
                research = json.load(f)
            valid_trades = orchestrator.validate_recommendations(research)
            orchestrator.execute_dee_bot_trades(valid_trades.get('dee_bot', []))
            orchestrator.execute_shorgan_bot_trades(valid_trades.get('shorgan_bot', []))
        else:
            print("No research found for today")
    else:
        print("\nUsage:")
        print("  --full           Run complete workflow (research + execution)")
        print("  --research-only  Generate AI research only")
        print("  --execute-only   Execute today's research")
        print("\nExample:")
        print("  python execute_with_ai_research.py --full")


if __name__ == "__main__":
    main()