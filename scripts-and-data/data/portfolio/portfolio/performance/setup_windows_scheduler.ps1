# PowerShell script to set up Windows Task Scheduler for daily performance tracking
# Run this script as Administrator

$taskName = "AI Trading Bot Performance Tracker"
$taskDescription = "Runs daily at 4:15 PM ET to track and report trading performance"
$scriptPath = "C:\Users\shorg\ai-stock-trading-bot\Performance_Tracking\run_daily_performance.bat"

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute $scriptPath

# Create trigger for 4:15 PM daily (adjust for your timezone)
# Note: Windows Task Scheduler uses local time
$trigger = New-ScheduledTaskTrigger -Daily -At "16:15"

# Set task to run only on weekdays
$trigger.DaysOfWeek = @("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description $taskDescription `
        -RunLevel Highest `
        -Force
    
    Write-Host "✓ Task scheduled successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Yellow
    Write-Host "  Name: $taskName"
    Write-Host "  Time: Daily at 4:15 PM (weekdays only)"
    Write-Host "  Script: $scriptPath"
    Write-Host ""
    Write-Host "To manage this task:" -ForegroundColor Cyan
    Write-Host "  - Open Task Scheduler (taskschd.msc)"
    Write-Host "  - Look for: $taskName"
    Write-Host ""
    Write-Host "To run the task manually:" -ForegroundColor Cyan
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'"
    
} catch {
    Write-Host "✗ Failed to create scheduled task" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this script as Administrator" -ForegroundColor Yellow
}