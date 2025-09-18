"""
Local server to receive ChatGPT reports from browser extension
Fixed version with proper directory structure and enhanced parsing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ReportProcessor:
    def __init__(self):
        # Updated paths for new structure
        self.json_dir = 'scripts-and-data/daily-json/chatgpt'
        self.csv_dir = 'scripts-and-data/daily-csv'
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.csv_dir, exist_ok=True)

    def parse_trades(self, data: dict) -> list:
        """Parse trades from extension data"""

        # If trades already provided by extension
        if 'trades' in data and data['trades']:
            return data['trades']

        # Otherwise parse from text
        trades = []
        text = data.get('text', '')
        lines = text.split('\n')

        current_trade = {}

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Look for ticker symbols
            import re

            # Table row pattern: | SYMBOL | ... | X% | $XX | $XX | $XX |
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    # Check for symbol in first part
                    symbol_match = re.match(r'([A-Z]{1,5})', parts[1])
                    if symbol_match:
                        trade = {'symbol': symbol_match.group(1)}

                        # Parse rest of row
                        for part in parts[2:]:
                            # Position size
                            if '%' in part:
                                size_match = re.search(r'(\d+)%', part)
                                if size_match:
                                    trade['size_pct'] = int(size_match.group(1))

                            # Prices with tilde or dollar sign
                            elif '~' in part or '$' in part:
                                price_match = re.search(r'\$?([\d.]+)', part)
                                if price_match:
                                    price = float(price_match.group(1))
                                    if 'entry' not in trade:
                                        trade['entry'] = price
                                        # Check for long/short
                                        if 'short' in part.lower():
                                            trade['action'] = 'SHORT'
                                        else:
                                            trade['action'] = 'LONG'
                                    elif 'stop' not in trade:
                                        trade['stop'] = price
                                    elif 'target' not in trade:
                                        trade['target'] = price

                        if 'symbol' in trade and 'entry' in trade:
                            # Set defaults
                            if 'action' not in trade:
                                trade['action'] = 'LONG'
                            if 'size_pct' not in trade:
                                trade['size_pct'] = 5
                            if 'stop' not in trade:
                                trade['stop'] = trade['entry'] * 0.92
                            if 'target' not in trade:
                                trade['target'] = trade['entry'] * 1.15

                            trades.append(trade)

            # Non-table format
            else:
                # New symbol line
                if re.match(r'^\d+\.?\s*[A-Z]{1,5}', line_clean):
                    if current_trade and 'symbol' in current_trade:
                        trades.append(current_trade)

                    symbol_match = re.search(r'([A-Z]{1,5})', line_clean)
                    if symbol_match:
                        current_trade = {'symbol': symbol_match.group(1)}

                # Parse data for current trade
                if current_trade:
                    line_lower = line.lower()

                    if 'entry' in line_lower or '~' in line:
                        price = re.search(r'\$?([\d.]+)', line)
                        if price and 'entry' not in current_trade:
                            current_trade['entry'] = float(price.group(1))

                    if 'stop' in line_lower:
                        price = re.search(r'\$?([\d.]+)', line)
                        if price:
                            current_trade['stop'] = float(price.group(1))

                    if 'target' in line_lower:
                        price = re.search(r'\$?([\d.]+)', line)
                        if price:
                            current_trade['target'] = float(price.group(1))

                    if '%' in line:
                        size = re.search(r'(\d+)%', line)
                        if size:
                            current_trade['size_pct'] = int(size.group(1))

                    if 'long' in line_lower:
                        current_trade['action'] = 'LONG'
                    elif 'short' in line_lower:
                        current_trade['action'] = 'SHORT'

        # Add last trade
        if current_trade and 'symbol' in current_trade and 'entry' in current_trade:
            # Set defaults
            if 'action' not in current_trade:
                current_trade['action'] = 'LONG'
            if 'size_pct' not in current_trade:
                current_trade['size_pct'] = 5
            if 'stop' not in current_trade:
                current_trade['stop'] = current_trade['entry'] * 0.92
            if 'target' not in current_trade:
                current_trade['target'] = current_trade['entry'] * 1.15

            trades.append(current_trade)

        return trades

    def save_report(self, report: dict) -> str:
        """Save report to JSON file"""

        timestamp = datetime.now()

        # Daily file (overwrites)
        daily_file = f"chatgpt_report_{timestamp.strftime('%Y-%m-%d')}.json"
        daily_path = os.path.join(self.json_dir, daily_file)

        with open(daily_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Timestamped backup
        backup_file = f"chatgpt_report_{timestamp.strftime('%Y-%m-%d_%H%M%S')}.json"
        backup_path = os.path.join(self.json_dir, backup_file)

        with open(backup_path, 'w') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Report saved: {daily_path}")
        return daily_path

processor = ReportProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

@app.route('/save_report', methods=['POST', 'OPTIONS'])
def save_report():
    """Receive and save ChatGPT report"""

    if request.method == 'OPTIONS':
        # Handle preflight
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 204

    try:
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Parse trades
        trades = processor.parse_trades(data)

        # Build report
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'source': 'ChatGPT TradingAgents',
            'trades': trades,
            'trade_count': len(trades),
            'url': data.get('url', ''),
            'raw_text': data.get('text', '')[:10000],  # Limit size
            'extracted_at': datetime.now().isoformat()
        }

        # Save report
        filepath = processor.save_report(report)

        logging.info(f"Processed {len(trades)} trades from ChatGPT")

        return jsonify({
            'success': True,
            'message': f"Saved {len(trades)} trades",
            'trades': trades,
            'filepath': filepath
        })

    except Exception as e:
        logging.error(f"Error processing report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/get_latest', methods=['GET'])
def get_latest_report():
    """Get the latest saved report"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        filepath = os.path.join(processor.json_dir, f"chatgpt_report_{today}.json")

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
        if not os.path.exists(processor.json_dir):
            return jsonify({'reports': []})

        files = [f for f in os.listdir(processor.json_dir)
                if f.startswith('chatgpt_report_') and f.endswith('.json')]
        files.sort(reverse=True)

        reports = []
        for file in files[:10]:  # Last 10 reports
            filepath = os.path.join(processor.json_dir, file)
            try:
                with open(filepath, 'r') as f:
                    report = json.load(f)
                    reports.append({
                        'filename': file,
                        'date': report.get('date'),
                        'trades_count': len(report.get('trades', [])),
                        'source': report.get('source')
                    })
            except:
                continue

        return jsonify({'reports': reports})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("ChatGPT Report Server v2.0")
    print("="*60)
    print("Server running on http://localhost:8888")
    print("Extension status indicator should show green when connected")
    print("Reports saved to: scripts-and-data/daily-json/chatgpt/")
    print("="*60)

    # Run server
    app.run(host='0.0.0.0', port=8888, debug=True)