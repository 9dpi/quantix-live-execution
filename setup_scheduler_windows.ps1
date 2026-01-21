# Windows Task Scheduler Setup for AUTO v0

# Step 1: Set environment variable (persistent)
[System.Environment]::SetEnvironmentVariable("AUTO_V0_ENABLED", "true", "User")

# Step 2: Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "D:\Automator_Prj\Quantix_MPV\quantix-live-execution\auto_scheduler.py" -WorkingDirectory "D:\Automator_Prj\Quantix_MPV\quantix-live-execution"

$trigger = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "Quantix AUTO v0 Scheduler" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "AUTO v0 polling mechanism (60s interval, 1/day gate enforcement)"

Write-Host "✅ Scheduled task created: Quantix AUTO v0 Scheduler"
Write-Host "📋 Task will start automatically at system startup"
Write-Host "🛑 To disable: Set AUTO_V0_ENABLED=false"
