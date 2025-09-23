# Weekly PDF Upload Folder

## Purpose
This folder is for uploading weekly deep research PDFs from ChatGPT.

## How to Use

### Method 1: Manual Upload
1. Download your weekly deep research PDFs from ChatGPT
2. Place them in this folder
3. Run the batch file: `upload_weekly_pdfs.bat`
4. PDFs will be automatically archived to `docs/index/reports-pdf/weekly/`

### Method 2: Direct Archive
```bash
python scripts-and-data/automation/archive_weekly_pdfs.py path/to/your/file.pdf
```

### Method 3: Automated (Every Sunday 10 PM)
The system automatically checks this folder and archives any PDFs found.

## Naming Conventions
For best organization, name your PDFs with keywords:
- Include "dee" or "defensive" for DEE-BOT reports
- Include "shorgan" or "catalyst" for SHORGAN-BOT reports
- Example: `dee_bot_weekly_research_2025-09-23.pdf`
- Example: `shorgan_weekly_catalyst_report.pdf`

## Archive Structure
PDFs are organized by week:
```
docs/index/reports-pdf/weekly/
├── Week_2025_W38/
│   ├── dee-bot_weekly_research_20250923_115400.pdf
│   └── shorgan-bot_weekly_research_20250923_115401.pdf
├── dee-bot_weekly_latest.pdf
└── shorgan-bot_weekly_latest.pdf
```

## Features
- Automatic weekly folder organization
- Maintains "latest" copies for quick access
- Creates searchable index
- Preserves original timestamps
- Moves processed files to `processed/` subfolder