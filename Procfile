# Railway Procfile - AI Trading Bot
# Each service runs as a separate Railway cron job

# Research Generation (Saturday 12 PM ET / 17:00 UTC)
research: python railway_cron.py research

# Trade Generation (Weekdays 8:30 AM ET / 13:30 UTC)
trades: python railway_cron.py trades

# Trade Execution (Weekdays 9:30 AM ET / 14:30 UTC)
execute: python railway_cron.py execute

# Performance Graph (Weekdays 4:30 PM ET / 21:30 UTC)
performance: python railway_cron.py performance
