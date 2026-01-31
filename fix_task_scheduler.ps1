$tasks = @(
    'AI Trading - Evening Research',
    'AI Trading - Morning Trade Generation',
    'AI Trading - Trade Execution',
    'AI Trading - Daily Performance Graph',
    'AI Trading - Weekend Research'
)

$workingDir = 'C:\Users\shorg\ai-stock-trading-bot'

foreach ($taskName in $tasks) {
    try {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
        $action = $task.Actions[0]
        $action.WorkingDirectory = $workingDir
        Set-ScheduledTask -TaskName $taskName -Action $action | Out-Null
        Write-Host "[OK] Fixed: $taskName"
    } catch {
        Write-Host "[SKIP] $taskName - $_"
    }
}

Write-Host ""
Write-Host "Verifying fixes..."
foreach ($taskName in $tasks) {
    try {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
        $wd = $task.Actions[0].WorkingDirectory
        Write-Host "[CHECK] $taskName : $wd"
    } catch {
        Write-Host "[ERROR] $taskName not found"
    }
}
