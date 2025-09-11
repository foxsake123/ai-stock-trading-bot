# PowerShell script to update the scheduled task to 7AM ET
$TaskName = "Trading-Reports-8AM"
$NewTaskName = "Trading-Reports-7AM"
$ScriptPath = "C:\Users\shorg\ai-stock-trading-bot\send_morning_reports.bat"
$Time = "07:00"

# First, unregister the old task
Write-Host "Removing old 8AM task..."
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Create the new scheduled task for 7AM
$Action = New-ScheduledTaskAction -Execute $ScriptPath
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the new task
Register-ScheduledTask -TaskName $NewTaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Send DEE-BOT and Shorgan-Bot trading reports to Telegram at 7am ET daily"

Write-Host "Scheduled task created successfully!"
Write-Host "Reports will be sent daily at 7:00 AM ET"