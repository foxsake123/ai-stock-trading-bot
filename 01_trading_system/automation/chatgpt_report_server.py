"""
Local server to receive ChatGPT reports from browser extension
Runs on port 8888 and saves reports automatically
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ReportProcessor:
    def __init__(self):
        self.research_dir = '02_data/research/reports/pre_market_daily'
        os.makedirs(self.research_dir, exist_ok=True)
        
    def parse_report_text(self, text: str) -> dict:
        """Parse ChatGPT report text into structured format"""
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'source': 'ChatGPT TradingAgents (Auto-captured)',
            'trades': [],
            'market_context': '',
            'raw_text': text
        }
        
        lines = text.split('\n')
        current_trade = {}
        
        for line in lines:
            line_lower = line.lower()
            
            # Look for symbol patterns
            if any(keyword in line_lower for keyword in ['symbol', 'ticker', 'stock']):
                # Extract uppercase symbols
                import re
                symbols = re.findall(r'\b[A-Z]{1,5}\b', line)
                if symbols and symbols[0] not in ['USD', 'ET', 'AM', 'PM']:
                    if current_trade and 'symbol' in current_trade:
                        report['trades'].append(current_trade)
                    current_trade = {'symbol': symbols[0]}
            
            # Extract prices
            if current_trade:
                if 'entry' in line_lower:
                    import re
                    price = re.search(r'\$?([\d.]+)', line)
                    if price:
                        current_trade['entry'] = float(price.group(1))
                
                if 'stop' in line_lower:
                    import re
                    price = re.search(r'\$?([\d.]+)', line)
                    if price:
                        current_trade['stop'] = float(price.group(1))
                
                if 'target' in line_lower or 'profit' in line_lower:
                    import re
                    price = re.search(r'\$?([\d.]+)', line)
                    if price:
                        current_trade['target'] = float(price.group(1))
                
                if 'long' in line_lower:
                    current_trade['action'] = 'long'
                elif 'short' in line_lower:
                    current_trade['action'] = 'short'
                
                # Default size
                if 'size' not in current_trade:
                    current_trade['size_pct'] = 10
        
        # Add last trade
        if current_trade and 'symbol' in current_trade:
            report['trades'].append(current_trade)
        
        # Extract market context
        context_lines = []
        for line in lines[:20]:  # First 20 lines for context
            if line.strip() and not any(kw in line.lower() for kw in 
                ['entry', 'stop', 'target', 'symbol']):
                context_lines.append(line.strip())
        
        report['market_context'] = '\n'.join(context_lines[:5])
        
        return report
    
    def save_report(self, report: dict) -> str:
        """Save report to JSON file"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # Primary file (overwrites daily)
        primary_file = f"{timestamp}_chatgpt_report.json"
        primary_path = os.path.join(self.research_dir, primary_file)
        
        with open(primary_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Backup file (unique timestamp)
        backup_file = f"{timestamp}_chatgpt_report_{datetime.now().strftime('%H%M%S')}.json"
        backup_path = os.path.join(self.research_dir, backup_file)
        
        with open(backup_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info(f"Report saved to {primary_path}")
        return primary_path

processor = ReportProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'running', 'timestamp': datetime.now().isoformat()})

@app.route('/save_report', methods=['POST', 'OPTIONS'])
def save_report():
    """Receive and save ChatGPT report"""
    
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
    
    try:
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No report text provided'}), 400
        
        # Parse the report
        report = processor.parse_report_text(data['text'])
        
        # Add metadata
        report['conversation_id'] = data.get('conversationId', '')
        report['url'] = data.get('url', '')
        report['capture_timestamp'] = data.get('timestamp', datetime.now().isoformat())
        
        # Save the report
        filepath = processor.save_report(report)
        
        # Log success
        logging.info(f"Successfully processed report with {len(report['trades'])} trades")
        
        return jsonify({
            'success': True,
            'message': f"Report saved with {len(report['trades'])} trades",
            'filepath': filepath,
            'trades': report['trades']
        })
        
    except Exception as e:
        logging.error(f"Error processing report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_latest', methods=['GET'])
def get_latest_report():
    """Get the latest saved report"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        filepath = os.path.join(processor.research_dir, f"{today}_chatgpt_report.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                report = json.load(f)
            return jsonify(report)
        else:
            return jsonify({'error': 'No report found for today'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list_reports', methods=['GET'])
def list_reports():
    """List all saved reports"""
    try:
        files = [f for f in os.listdir(processor.research_dir) 
                if f.endswith('_chatgpt_report.json')]
        files.sort(reverse=True)
        
        reports = []
        for file in files[:10]:  # Last 10 reports
            filepath = os.path.join(processor.research_dir, file)
            with open(filepath, 'r') as f:
                report = json.load(f)
                reports.append({
                    'filename': file,
                    'date': report.get('date'),
                    'trades_count': len(report.get('trades', [])),
                    'source': report.get('source')
                })
        
        return jsonify({'reports': reports})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("ChatGPT Report Server")
    print("="*60)
    print("Server running on http://localhost:8888")
    print("Install browser extension and enable on ChatGPT")
    print("Reports will be saved automatically")
    print("="*60)
    
    # Run server
    app.run(host='localhost', port=8888, debug=False)