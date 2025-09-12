"""
Generate today's report with PDF
"""

import json
import os
from datetime import datetime
from openai_research_fetcher import OpenAIResearchFetcher

# Load today's research
research_file = '../../02_data/research/reports/pre_market_daily/2025-09-11_openai_research.json'

with open(research_file, 'r') as f:
    research = json.load(f)

# Initialize fetcher to use PDF generation
fetcher = OpenAIResearchFetcher()

# Generate PDF
pdf_path = os.path.join(fetcher.output_dir, f'{research["date"]}_pre_market_report.pdf')
fetcher.generate_pdf_report(research, pdf_path)

print(f"PDF report generated: {pdf_path}")