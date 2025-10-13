#!/usr/bin/env python3
"""
Flask Web Dashboard for Pre-Market Reports
Provides web interface for viewing, downloading, and listing trading reports.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import json

from flask import Flask, render_template, send_file, jsonify, abort
import markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)
app.config['REPORTS_DIR'] = Path('reports/premarket')

# Reports directory constant
REPORTS_DIR = Path('reports/premarket')


def get_all_reports() -> List[Dict]:
    """
    Get list of all reports with metadata.

    Returns:
        List of dicts with report information sorted by date (newest first)
    """
    reports = []

    # Find all report markdown files
    for report_file in REPORTS_DIR.glob('premarket_report_*.md'):
        try:
            # Extract date from filename (premarket_report_2025-10-14.md)
            filename = report_file.name
            date_str = filename.replace('premarket_report_', '').replace('.md', '')

            # Try to load corresponding metadata
            metadata_file = REPORTS_DIR / f'premarket_metadata_{date_str}.json'
            metadata = {}

            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

            # Build report info
            report_info = {
                'trading_date': date_str,
                'filename': filename,
                'generated_at': metadata.get('generation_date', 'Unknown'),
                'portfolio_value': metadata.get('portfolio_value', 0),
                'model': metadata.get('model', 'Unknown')
            }

            reports.append(report_info)

        except Exception as e:
            logger.error(f"Error processing report {report_file}: {e}")
            continue

    # Sort by trading date (newest first)
    reports.sort(key=lambda x: x['trading_date'], reverse=True)

    return reports


def load_report_markdown(date: str) -> Optional[str]:
    """
    Load report markdown file by date.

    Args:
        date: Trading date in YYYY-MM-DD format

    Returns:
        Markdown content or None if not found
    """
    report_file = REPORTS_DIR / f'premarket_report_{date}.md'

    if not report_file.exists():
        logger.warning(f"Report not found: {report_file}")
        return None

    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading report {report_file}: {e}")
        return None


def convert_markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown to HTML with extensions.

    Args:
        markdown_text: Markdown content

    Returns:
        HTML string
    """
    return markdown.markdown(
        markdown_text,
        extensions=['tables', 'fenced_code']
    )


@app.route('/')
def index():
    """
    Index page - list all reports.
    """
    logger.info("GET / - Listing all reports")

    try:
        reports = get_all_reports()
        logger.info(f"Found {len(reports)} reports")

        return render_template('index.html', reports=reports)

    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return f"Error loading reports: {str(e)}", 500


@app.route('/report/<date>')
def view_report(date: str):
    """
    View specific report by date.

    Args:
        date: Trading date in YYYY-MM-DD format
    """
    logger.info(f"GET /report/{date} - Viewing report")

    try:
        # Load markdown
        markdown_content = load_report_markdown(date)

        if markdown_content is None:
            logger.warning(f"Report not found: {date}")
            abort(404, description=f"Report for {date} not found")

        # Convert to HTML
        html_content = convert_markdown_to_html(markdown_content)

        return render_template(
            'report.html',
            date=date,
            html_content=html_content
        )

    except Exception as e:
        logger.error(f"Error rendering report {date}: {e}")
        return f"Error loading report: {str(e)}", 500


@app.route('/latest')
def latest_report():
    """
    View latest report (latest.md symlink).
    """
    logger.info("GET /latest - Viewing latest report")

    try:
        latest_file = REPORTS_DIR / 'latest.md'

        if not latest_file.exists():
            logger.warning("Latest report not found")
            abort(404, description="No latest report available")

        # Read latest.md
        with open(latest_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert to HTML
        html_content = convert_markdown_to_html(markdown_content)

        return render_template(
            'report.html',
            date='Latest',
            html_content=html_content
        )

    except Exception as e:
        logger.error(f"Error rendering latest report: {e}")
        return f"Error loading latest report: {str(e)}", 500


@app.route('/download/<date>')
def download_report(date: str):
    """
    Download report markdown file.

    Args:
        date: Trading date in YYYY-MM-DD format
    """
    logger.info(f"GET /download/{date} - Downloading report")

    try:
        report_file = REPORTS_DIR / f'premarket_report_{date}.md'

        if not report_file.exists():
            logger.warning(f"Report not found for download: {date}")
            abort(404, description=f"Report for {date} not found")

        return send_file(
            report_file,
            as_attachment=True,
            download_name=f'premarket_report_{date}.md'
        )

    except Exception as e:
        logger.error(f"Error downloading report {date}: {e}")
        return f"Error downloading report: {str(e)}", 500


@app.route('/api/reports')
def api_reports():
    """
    JSON API - list all reports with metadata.

    Returns:
        JSON array of report objects
    """
    logger.info("GET /api/reports - API request for reports list")

    try:
        reports = get_all_reports()
        logger.info(f"API returning {len(reports)} reports")

        return jsonify({
            'success': True,
            'count': len(reports),
            'reports': reports
        })

    except Exception as e:
        logger.error(f"Error in API endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors.
    """
    logger.warning(f"404 error: {error.description}")
    return render_template('404.html', error=error.description), 404


@app.errorhandler(500)
def server_error(error):
    """
    Handle 500 errors.
    """
    logger.error(f"500 error: {error}")
    return "Internal server error", 500


if __name__ == '__main__':
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("Starting Pre-Market Report Dashboard")
    logger.info(f"Reports directory: {REPORTS_DIR.absolute()}")
    logger.info("Server: http://0.0.0.0:5000")
    logger.info("=" * 80)

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
