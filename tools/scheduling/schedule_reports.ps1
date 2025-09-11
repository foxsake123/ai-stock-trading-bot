# PowerShell script to schedule daily trading reports at 8am ET
$TaskName = "Trading-Reports-8AM"
$ScriptPath = "C:\Users\shorg\ai-stock-trading-bot\send_morning_reports.bat"
$Time = "08:00"

# Create the scheduled task
$Action = New-ScheduledTaskAction -Execute $ScriptPath
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Send DEE-BOT and Shorgan-Bot trading reports to Telegram at 8am ET daily"

Write-Host "✓ Scheduled task '$TaskName' created successfully!"
Write-Host "Reports will be sent daily at 8:00 AM ET"
Write-Host ""
Write-Host "To view the task: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "To remove the task: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"