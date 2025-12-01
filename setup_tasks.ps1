# Task Scheduler Setup Script - Run as Administrator
# Right-click PowerShell -> Run as Administrator, then run this script

$pythonPath = "C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe"
$projectDir = "C:\Users\shorg\ai-stock-trading-bot"

Write-Host "Creating AI Trading automation tasks..." -ForegroundColor Cyan

# Task 1: Morning Trade Generation (8:30 AM weekdays)
$action1 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$projectDir\scripts\automation\generate_todays_trades_v2.py" -WorkingDirectory $projectDir
$trigger1 = New-ScheduledTaskTrigger -Daily -At 8:30AM
Register-ScheduledTask -TaskName "AI Trading - Morning Trade Generation" -Action $action1 -Trigger $trigger1 -Force
Write-Host "[OK] Created: Morning Trade Generation (8:30 AM)" -ForegroundColor Green

# Task 2: Trade Execution (9:30 AM weekdays)
$action2 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$projectDir\scripts\automation\execute_daily_trades.py" -WorkingDirectory $projectDir
$trigger2 = New-ScheduledTaskTrigger -Daily -At 9:30AM
Register-ScheduledTask -TaskName "AI Trading - Trade Execution" -Action $action2 -Trigger $trigger2 -Force
Write-Host "[OK] Created: Trade Execution (9:30 AM)" -ForegroundColor Green

# Task 3: Performance Graph (4:30 PM weekdays)
$action3 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$projectDir\scripts\performance\generate_performance_graph.py" -WorkingDirectory $projectDir
$trigger3 = New-ScheduledTaskTrigger -Daily -At 4:30PM
Register-ScheduledTask -TaskName "AI Trading - Performance Graph" -Action $action3 -Trigger $trigger3 -Force
Write-Host "[OK] Created: Performance Graph (4:30 PM)" -ForegroundColor Green

# Task 4: Weekend Research (Saturday 12:00 PM)
$action4 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$projectDir\scripts\automation\daily_claude_research.py" -WorkingDirectory $projectDir
$trigger4 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 12:00PM
Register-ScheduledTask -TaskName "AI Trading - Weekend Research" -Action $action4 -Trigger $trigger4 -Force
Write-Host "[OK] Created: Weekend Research (Saturday 12 PM)" -ForegroundColor Green

Write-Host ""
Write-Host "Verifying tasks..." -ForegroundColor Cyan
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI Trading*"} | Format-Table TaskName, State -AutoSize

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
