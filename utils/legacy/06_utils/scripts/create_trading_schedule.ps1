# PowerShell script to create Windows scheduled task for trading bot
# Run this as Administrator

$taskName = "Morning Trading Bot 930AM"
$description = "Runs AI trading bot at market open (9:30 AM ET)"
$scriptPath = "C:\Users\shorg\ai-stock-trading-bot\run_morning_trades.bat"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Task '$taskName' already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create the action (what to run)
$action = New-ScheduledTaskAction -Execute $scriptPath

# Create the trigger (when to run - 9:30 AM every weekday)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 9:30AM

# Create principal (who runs it)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description $description
    
    Write-Host "Successfully created scheduled task: $taskName" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  - Runs at: 9:30 AM ET every weekday"
    Write-Host "  - Script: $scriptPath"
    Write-Host "  - Run level: Highest privileges"
    Write-Host ""
    Write-Host "To test the task now, run:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'"
    Write-Host ""
    Write-Host "To view task status:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo"
    
} catch {
    Write-Host "Failed to create scheduled task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure you're running PowerShell as Administrator" -ForegroundColor Yellow
}