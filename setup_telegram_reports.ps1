# Setup Telegram Pre-Market Reports - Fixed Version
# This script configures automated morning reports at 7:00 AM ET

$TaskName = "Trading-Reports-PreMarket"
$ScriptPath = "C:\Users\shorg\ai-stock-trading-bot\06_utils\tools\scheduling\send_morning_reports.bat"
$Time = "07:00"

Write-Host "Setting up Telegram Pre-Market Reports..." -ForegroundColor Green

# Remove any existing task with similar names
$existingTasks = @("Trading-Reports-7AM", "Trading-Reports-8AM", "Trading-Reports-PreMarket")
foreach ($task in $existingTasks) {
    try {
        Unregister-ScheduledTask -TaskName $task -Confirm:$false -ErrorAction Stop
        Write-Host "Removed existing task: $task" -ForegroundColor Yellow
    } catch {
        # Task doesn't exist, continue
    }
}

# Verify the batch file exists
if (Test-Path $ScriptPath) {
    Write-Host "✓ Found batch file at: $ScriptPath" -ForegroundColor Green
} else {
    Write-Host "✗ Batch file not found at: $ScriptPath" -ForegroundColor Red
    Write-Host "Please check the file location!" -ForegroundColor Red
    exit 1
}

# Create the scheduled task
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptPath`""
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Send DEE-BOT and Shorgan-Bot pre-market reports to Telegram at 7:00 AM ET daily" `
        -Force
    
    Write-Host "`n✓ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host "Task Name: $TaskName" -ForegroundColor Cyan
    Write-Host "Schedule: Daily at 7:00 AM ET" -ForegroundColor Cyan
    Write-Host "Script: $ScriptPath" -ForegroundColor Cyan
    
    # Display next run time
    $task = Get-ScheduledTask -TaskName $TaskName
    $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    Write-Host "`nNext Run Time: $($taskInfo.NextRunTime)" -ForegroundColor Yellow
    
} catch {
    Write-Host "✗ Failed to create scheduled task!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "`nTo test the reports manually, run:" -ForegroundColor Green
Write-Host "  cd C:\Users\shorg\ai-stock-trading-bot\06_utils\tools\scheduling" -ForegroundColor Yellow
Write-Host "  .\send_morning_reports.bat" -ForegroundColor Yellow