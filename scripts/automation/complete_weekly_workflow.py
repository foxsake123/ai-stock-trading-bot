"""
Complete Weekly Workflow Automation
Processes ChatGPT research through multi-agent consensus
Generates validated trades for both bots
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import requests
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class WeeklyWorkflowOrchestrator:
    """Orchestrates the complete weekly workflow from research to execution"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "scripts-and-data" / "data"
        self.reports_dir = self.data_dir / "reports" / "weekly" / "chatgpt-research"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Telegram configuration
        self.telegram_token = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
        self.telegram_chat_id = "7870288896"

        # Week dates
        self.today = datetime.now()
        self.week_start = self.today - timedelta(days=self.today.weekday())
        self.week_end = self.week_start + timedelta(days=4)

        # Workflow status
        self.workflow_status = {
            'research_received': False,
            'agents_processed': False,
            'consensus_generated': False,
            'trades_validated': False,
            'execution_ready': False
        }

    def send_telegram_message(self, message: str, priority: str = "INFO"):
        """Send status update via Telegram"""
        emoji_map = {
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'INFO': 'ℹ️',
            'CRITICAL': '🚨'
        }

        emoji = emoji_map.get(priority, '📌')
        formatted_message = f"{emoji} {message}"

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            'chat_id': self.telegram_chat_id,
            'text': formatted_message,
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False

    def check_for_chatgpt_research(self) -> Path:
        """Check if ChatGPT research file exists for current week"""
        # Look for files matching current week pattern
        week_str = self.week_start.strftime("%Y-%m-%d")

        patterns = [
            f"CHATGPT_ACTUAL_{week_str}*.md",
            f"chatgpt_weekly_{week_str}*.md",
            f"weekly_research_{week_str}*.md"
        ]

        for pattern in patterns:
            files = list(self.reports_dir.glob(pattern))
            if files:
                # Return most recent file
                return max(files, key=lambda x: x.stat().st_mtime)

        # Check for today's file specifically
        today_str = self.today.strftime("%Y-%m-%d")
        today_file = self.reports_dir / f"CHATGPT_ACTUAL_{today_str}.md"
        if today_file.exists():
            return today_file

        return None

    async def process_through_agents(self, research_file: Path) -> Dict:
        """Process ChatGPT research through multi-agent consensus"""
        print(f"\n{'='*70}")
        print("PROCESSING THROUGH MULTI-AGENT SYSTEM")
        print(f"{'='*70}")

        try:
            # Import the processor
            from scripts_and_data.automation.process_chatgpt_research import ChatGPTResearchProcessor

            # Create processor instance
            processor = ChatGPTResearchProcessor()

            # Load the research file
            with open(research_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse and process
            processor.chatgpt_research = processor.parse_chatgpt_research(content)

            # Run multi-agent consensus
            results = await processor.process_all_trades()

            self.workflow_status['agents_processed'] = True
            self.workflow_status['consensus_generated'] = True

            return results

        except Exception as e:
            print(f"Error in multi-agent processing: {e}")
            self.send_telegram_message(
                f"Multi-agent processing failed: {str(e)[:100]}",
                priority="ERROR"
            )
            return None

    def validate_consensus_trades(self, consensus_results: Dict) -> Dict:
        """Validate consensus trades meet minimum thresholds"""
        validated = {
            'dee_bot': {
                'approved_trades': [],
                'rejected_trades': []
            },
            'shorgan_bot': {
                'approved_trades': [],
                'rejected_trades': []
            }
        }

        # DEE-BOT validation (threshold: 55)
        for trade in consensus_results.get('dee_bot', {}).get('final_trades', []):
            confidence = trade.get('confidence', 0)
            if confidence >= 55:
                validated['dee_bot']['approved_trades'].append(trade)
            else:
                validated['dee_bot']['rejected_trades'].append(trade)

        # SHORGAN-BOT validation (threshold: 60)
        for trade in consensus_results.get('shorgan_bot', {}).get('final_trades', []):
            confidence = trade.get('confidence', 0)
            if confidence >= 60:
                validated['shorgan_bot']['approved_trades'].append(trade)
            else:
                validated['shorgan_bot']['rejected_trades'].append(trade)

        self.workflow_status['trades_validated'] = True

        # Report validation results
        dee_approved = len(validated['dee_bot']['approved_trades'])
        dee_rejected = len(validated['dee_bot']['rejected_trades'])
        shorgan_approved = len(validated['shorgan_bot']['approved_trades'])
        shorgan_rejected = len(validated['shorgan_bot']['rejected_trades'])

        print(f"\nVALIDATION RESULTS:")
        print(f"DEE-BOT: {dee_approved} approved, {dee_rejected} rejected")
        print(f"SHORGAN-BOT: {shorgan_approved} approved, {shorgan_rejected} rejected")

        return validated

    def generate_execution_files(self, validated_trades: Dict):
        """Generate final execution files for daily trading"""

        # Generate TODAYS_TRADES file
        today_str = self.today.strftime("%Y-%m-%d")
        trades_file = self.project_root / f"TODAYS_TRADES_{today_str}.md"

        content = f"""# CONSENSUS-VALIDATED TRADES
## {self.today.strftime('%A, %B %d, %Y')}
### Generated from Multi-Agent Consensus

---

## DEE-BOT TRADES (Defensive S&P 100)
**Strategy**: Beta-neutral, dividend focus, risk-managed
**Minimum Confidence**: 55%

"""

        # Add DEE-BOT trades
        for trade in validated_trades['dee_bot']['approved_trades']:
            content += f"""
### {trade['action']} {trade['symbol']}
- **Shares**: {trade.get('shares', 'TBD')}
- **Price**: ${trade.get('price', 'Market')}
- **Confidence**: {trade['confidence']:.1f}%
"""
            if 'stop' in trade:
                content += f"- **Stop Loss**: ${trade['stop']}\n"

        content += """
---

## SHORGAN-BOT TRADES (Catalyst-Driven)
**Strategy**: Event catalysts, momentum, high risk/reward
**Minimum Confidence**: 60%

"""

        # Add SHORGAN-BOT trades
        for trade in validated_trades['shorgan_bot']['approved_trades']:
            content += f"""
### {trade['action']} {trade['symbol']}
- **Shares**: {trade.get('shares', 'TBD')}
- **Price**: ${trade.get('price', 'Market')}
- **Confidence**: {trade['confidence']:.1f}%
"""
            if 'stop' in trade:
                content += f"- **Stop Loss**: ${trade['stop']}\n"

        content += """
---

## EXECUTION INSTRUCTIONS

1. Execute at 9:30 AM market open
2. Use LIMIT DAY orders only
3. Check pre-market for gaps
4. Honor all stop losses
5. No margin usage

## REJECTED TRADES (Below Threshold)

"""

        # List rejected trades
        if validated_trades['dee_bot']['rejected_trades']:
            content += "**DEE-BOT Rejected**:\n"
            for trade in validated_trades['dee_bot']['rejected_trades']:
                content += f"- {trade['action']} {trade['symbol']} (Confidence: {trade['confidence']:.1f}%)\n"

        if validated_trades['shorgan_bot']['rejected_trades']:
            content += "\n**SHORGAN-BOT Rejected**:\n"
            for trade in validated_trades['shorgan_bot']['rejected_trades']:
                content += f"- {trade['action']} {trade['symbol']} (Confidence: {trade['confidence']:.1f}%)\n"

        content += f"""
---

Generated by Multi-Agent Consensus System
Workflow completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Write file
        with open(trades_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\nExecution file created: {trades_file}")
        self.workflow_status['execution_ready'] = True

        return trades_file

    def generate_summary_report(self):
        """Generate workflow summary report"""
        report = f"""
{'='*70}
WEEKLY WORKFLOW SUMMARY
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

WORKFLOW STATUS:
"""
        for step, status in self.workflow_status.items():
            status_text = "✅ Complete" if status else "❌ Pending"
            report += f"- {step}: {status_text}\n"

        report += f"""
WEEK: {self.week_start.strftime('%B %d')} - {self.week_end.strftime('%B %d, %Y')}

Next Steps:
1. Execute validated trades at market open
2. Monitor positions throughout the day
3. Run post-market report at 4:30 PM
4. Prepare for next day's execution

{'='*70}
"""
        return report

    async def run_complete_workflow(self, research_file_path: str = None):
        """Run the complete weekly workflow"""

        print("="*70)
        print("STARTING WEEKLY WORKFLOW")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # Step 1: Check for ChatGPT research
        if research_file_path:
            research_file = Path(research_file_path)
        else:
            research_file = self.check_for_chatgpt_research()

        if not research_file or not research_file.exists():
            message = "No ChatGPT research file found. Please provide research first."
            print(f"\n❌ {message}")
            self.send_telegram_message(message, priority="WARNING")
            return False

        print(f"\n✅ Found research file: {research_file.name}")
        self.workflow_status['research_received'] = True

        # Step 2: Process through multi-agent system
        print("\n" + "="*50)
        print("STEP 2: Multi-Agent Processing")
        print("="*50)

        consensus_results = await self.process_through_agents(research_file)

        if not consensus_results:
            print("❌ Multi-agent processing failed")
            return False

        # Step 3: Validate trades against thresholds
        print("\n" + "="*50)
        print("STEP 3: Trade Validation")
        print("="*50)

        validated_trades = self.validate_consensus_trades(consensus_results)

        # Step 4: Generate execution files
        print("\n" + "="*50)
        print("STEP 4: Generate Execution Files")
        print("="*50)

        execution_file = self.generate_execution_files(validated_trades)

        # Step 5: Send summary to Telegram
        summary = self.generate_summary_report()
        print(summary)

        # Send Telegram notification
        dee_count = len(validated_trades['dee_bot']['approved_trades'])
        shorgan_count = len(validated_trades['shorgan_bot']['approved_trades'])

        telegram_message = f"""<b>Weekly Workflow Complete!</b>

<b>Validated Trades:</b>
• DEE-BOT: {dee_count} trades approved
• SHORGAN-BOT: {shorgan_count} trades approved

<b>Status:</b>
✅ Research processed
✅ Multi-agent consensus
✅ Trades validated
✅ Execution file ready

Execute at 9:30 AM market open!"""

        self.send_telegram_message(telegram_message, priority="SUCCESS")

        return True

def main():
    """Main execution"""
    orchestrator = WeeklyWorkflowOrchestrator()

    # Check command line arguments
    if len(sys.argv) > 1:
        research_file = sys.argv[1]
        print(f"Using provided research file: {research_file}")
    else:
        research_file = None

    # Run workflow
    success = asyncio.run(orchestrator.run_complete_workflow(research_file))

    if success:
        print("\n✅ WORKFLOW COMPLETE - Ready for trading!")
    else:
        print("\n❌ WORKFLOW INCOMPLETE - Manual intervention required")

if __name__ == "__main__":
    main()