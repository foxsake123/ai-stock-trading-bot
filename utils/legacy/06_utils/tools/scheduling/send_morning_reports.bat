@echo off
cd /d "C:\Users\shorg\ai-stock-trading-bot\06_utils\tools\reporting"
python quick_telegram_send.py
echo Reports sent at %date% %time% >> "C:\Users\shorg\ai-stock-trading-bot\telegram_reports.log"
exit