"""
Manual ChatGPT Report Ingestion Tool
Allows copying and pasting ChatGPT reports into the system
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ChatGPTReportSaver:
    """Handles manual ingestion of ChatGPT reports"""
    
    def __init__(self):
        self.research_dir = '02_data/research/reports/pre_market_daily'
        os.makedirs(self.research_dir, exist_ok=True)
        
    def parse_chatgpt_report(self, text: str) -> Dict:
        """Parse ChatGPT report text into structured JSON"""
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'source': 'ChatGPT TradingAgents',
            'trades': [],
            'market_context': '',
            'risk_metrics': {}
        }
        
        # Parse trades (looking for common patterns)
        trade_patterns = [
            r'Symbol:\s*([A-Z]+)',
            r'Action:\s*(Long|Short|Buy|Sell)',
            r'Entry:\s*\$?([\d.]+)',
            r'Stop.*?:\s*\$?([\d.]+)',
            r'Target.*?:\s*\$?([\d.]+)',
        ]
        
        lines = text.split('\n')
        current_trade = {}
        
        for line in lines:
            # Check for symbol
            if 'symbol' in line.lower() or re.match(r'^[A-Z]{1,5}[:\s]', line):
                if current_trade:
                    # Save previous trade
                    if 'symbol' in current_trade:
                        report['trades'].append(current_trade)
                current_trade = {}
                
                # Extract symbol
                symbol_match = re.search(r'\b([A-Z]{1,5})\b', line)
                if symbol_match:
                    current_trade['symbol'] = symbol_match.group(1)
            
            # Extract entry price
            if 'entry' in line.lower():
                price_match = re.search(r'\$?([\d.]+)', line)
                if price_match:
                    current_trade['entry'] = float(price_match.group(1))
            
            # Extract stop loss
            if 'stop' in line.lower():
                price_match = re.search(r'\$?([\d.]+)', line)
                if price_match:
                    current_trade['stop'] = float(price_match.group(1))
            
            # Extract target
            if 'target' in line.lower() or 'profit' in line.lower():
                price_match = re.search(r'\$?([\d.]+)', line)
                if price_match:
                    current_trade['target'] = float(price_match.group(1))
            
            # Extract action
            if 'long' in line.lower():
                current_trade['action'] = 'long'
            elif 'short' in line.lower():
                current_trade['action'] = 'short'
            
            # Extract size
            if 'size' in line.lower() or 'position' in line.lower():
                size_match = re.search(r'(\d+)%', line)
                if size_match:
                    current_trade['size_pct'] = int(size_match.group(1))
                else:
                    current_trade['size_pct'] = 10  # Default
        
        # Don't forget the last trade
        if current_trade and 'symbol' in current_trade:
            report['trades'].append(current_trade)
        
        # Extract market context (everything that's not trade info)
        context_lines = []
        for line in lines:
            if not any(keyword in line.lower() for keyword in 
                      ['symbol', 'entry', 'stop', 'target', 'size', 'action']):
                if line.strip():
                    context_lines.append(line.strip())
        
        report['market_context'] = '\n'.join(context_lines[:10])  # First 10 lines
        
        return report
    
    def validate_report(self, report: Dict) -> tuple[bool, str]:
        """Validate the parsed report"""
        
        # Check date
        if report.get('date') != datetime.now().strftime('%Y-%m-%d'):
            return False, f"Report date {report.get('date')} doesn't match today"
        
        # Check for trades
        if not report.get('trades'):
            return False, "No trades found in report"
        
        # Validate each trade
        for i, trade in enumerate(report['trades']):
            if not trade.get('symbol'):
                return False, f"Trade {i+1} missing symbol"
            
            if not trade.get('entry'):
                # Try to be lenient
                print(f"Warning: Trade {trade['symbol']} missing entry price")
            
            if not trade.get('stop'):
                print(f"Warning: Trade {trade['symbol']} missing stop loss")
        
        return True, "Report validated successfully"
    
    def save_report(self, report: Dict) -> str:
        """Save report to JSON file"""
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"{timestamp}_chatgpt_report.json"
        filepath = os.path.join(self.research_dir, filename)
        
        # Save JSON
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to: {filepath}")
        
        # Also save a backup
        backup_name = f"{timestamp}_chatgpt_report_{datetime.now().strftime('%H%M%S')}.json"
        backup_path = os.path.join(self.research_dir, backup_name)
        with open(backup_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
    
    def interactive_save(self):
        """Interactive mode for saving ChatGPT reports"""
        
        print("="*60)
        print("ChatGPT Report Manual Ingestion Tool")
        print("="*60)
        print("\nPaste your ChatGPT report below.")
        print("When done, type 'END' on a new line and press Enter.\n")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print("\n\nCancelled by user")
                return None
        
        if not lines:
            print("No content provided")
            return None
        
        # Parse the report
        text = '\n'.join(lines)
        print("\nParsing report...")
        report = self.parse_chatgpt_report(text)
        
        # Display what was found
        print(f"\nFound {len(report['trades'])} trades:")
        for trade in report['trades']:
            print(f"  - {trade.get('symbol', 'UNKNOWN')}: "
                  f"{trade.get('action', 'long').upper()} "
                  f"@ ${trade.get('entry', 0):.2f}")
        
        # Validate
        valid, message = self.validate_report(report)
        print(f"\nValidation: {message}")
        
        if not valid:
            response = input("\nReport has issues. Save anyway? (y/n): ")
            if response.lower() != 'y':
                print("Report not saved")
                return None
        
        # Save the report
        filepath = self.save_report(report)
        
        print("\n" + "="*60)
        print("Report saved successfully!")
        print("The daily pipeline will now use this report.")
        print("="*60)
        
        return filepath
    
    def quick_save(self, text: str) -> str:
        """Quick save mode for automated scripts"""
        report = self.parse_chatgpt_report(text)
        return self.save_report(report)


def main():
    """Main entry point"""
    saver = ChatGPTReportSaver()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick mode: read from stdin
        import sys
        text = sys.stdin.read()
        filepath = saver.quick_save(text)
        print(f"Saved to: {filepath}")
    else:
        # Interactive mode
        saver.interactive_save()


if __name__ == "__main__":
    main()