# Setting Up Automated Research Generation

## ✅ Research Generated Successfully
Your research for **October 23, 2025** has been generated and sent to Telegram!

## 🔧 To Enable Daily Automation

### Option 1: Task Scheduler (Recommended - Runs Even When Python Closes)

**Steps:**
1. Right-click on `setup_scheduler.bat`
2. Select **"Run as administrator"**
3. Click "Yes" when prompted by User Account Control
4. The task will be created for 6:00 PM ET daily

**Or manually via Command Prompt (as Administrator):**
```batch
schtasks /create /tn "AI Trading - Evening Research" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts\automation\daily_claude_research.py" /sc daily /st 18:00 /f
```

**To verify it's working:**
```batch
schtasks /query /tn "AI Trading - Evening Research"
```

### Option 2: Python Background Service (Alternative)

If Task Scheduler doesn't work, you can run a Python service:

```bash
# Start the background service (keeps running)
python scripts/automation/run_scheduler_service.py
```

This will run continuously and execute research generation at 6:00 PM ET daily.

## 📊 What Gets Generated Daily

Every evening at 6:00 PM ET:
- **DEE-BOT Research Report** (Markdown + PDF)
- **SHORGAN-BOT Research Report** (Markdown + PDF)
- **Combined Report** (claude_research.md)
- **Telegram Notifications** (PDFs sent automatically)

Files saved to: `reports/premarket/{YYYY-MM-DD}/`

## ⚠️ Important Notes

- Research is generated for **tomorrow's trading date**
- Requires active internet connection
- Uses Claude Sonnet 4 with Extended Thinking (~$0.16 per report)
- PDFs automatically sent to Telegram (bot token in .env)

## 🔍 Troubleshooting

**If research doesn't generate:**
1. Check Task Scheduler is running: `schtasks /query /tn "AI Trading - Evening Research"`
2. Verify Python path is correct in the task
3. Check logs in the reports directory
4. Run manually: `python scripts/automation/daily_claude_research.py --force`

**Check if automation is working:**
```bash
# Tomorrow morning, check for today's report:
ls reports/premarket/2025-10-23/
```

## 📞 Next Steps

After setting up automation:
1. Tomorrow (Oct 23) at 6 PM - Research will auto-generate
2. Check Telegram for PDF notifications
3. Review reports before market open (9:30 AM)
4. Generate trades: `python scripts/automation/generate_todays_trades_v2.py`
