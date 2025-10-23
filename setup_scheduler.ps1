## AI Trading Bot - Task Scheduler Setup (PowerShell)
## Creates daily automation task for 6:00 PM ET

Write-Host "Setting up Task Scheduler for AI Trading Research..." -ForegroundColor Cyan
Write-Host ""

# Define task parameters
$taskName = "AI Trading - Evening Research"
$pythonPath = "C:\Python313\python.exe"
$scriptPath = "C:\Users\shorg\ai-stock-trading-bot\scripts\automation\daily_claude_research.py"

# Create scheduled task
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory "C:\Users\shorg\ai-stock-trading-bot"
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00PM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the task (force = overwrite if exists)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null

Write-Host "✓ Task created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Name: $taskName" -ForegroundColor Yellow
Write-Host "Schedule: Daily at 6:00 PM ET" -ForegroundColor Yellow
Write-Host "Script: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# Verify the task
$task = Get-ScheduledTask -TaskName $taskName
$taskInfo = Get-ScheduledTaskInfo -TaskName $taskName

Write-Host "✓ Task verified and active!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Run Time: $($taskInfo.NextRunTime)" -ForegroundColor Yellow
Write-Host "State: $($task.State)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Setup complete! The research will run automatically at 6:00 PM daily." -ForegroundColor Green
