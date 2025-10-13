# Windows Task Scheduler Installation Guide - Pre-Market Report Generator

This guide explains how to set up automated daily execution of the pre-market report generator using Windows Task Scheduler.

## Overview

The Windows Task Scheduler configuration will:
- Run the pre-market report generator daily at 6:00 PM ET (18:00)
- Execute Monday through Friday only (skip weekends)
- Stop if execution exceeds 1 hour
- Run whether user is logged in or not
- Log all execution history

## Prerequisites

1. **Windows 10 or Windows 11** (Windows Server 2016+ also supported)
2. **Python 3.8+** installed and in PATH
3. **Project directory** set up with all dependencies installed
4. **.env file** configured with API keys
5. **Administrator access** (required for Task Scheduler configuration)

## Installation Methods

You can install the scheduled task using either:
- **Method 1:** Import XML file (Quick - 2 minutes)
- **Method 2:** GUI configuration (Detailed - 5 minutes)

Choose the method that works best for you.

---

## Method 1: Import XML File (Recommended)

### Step 1.1: Edit XML Configuration

Before importing, you must customize the XML file with your paths.

Open `systemd/premarket_report_task.xml` in a text editor and update:

**1. Python Path (Line 50):**
```xml
<!-- Change this line: -->
<Command>C:\Users\CHANGE_USERNAME\AppData\Local\Programs\Python\Python313\python.exe</Command>

<!-- To your actual Python path. Find it with: -->
<!-- where python -->
<Command>C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\python.exe</Command>
```

**2. Working Directory (Line 52):**
```xml
<!-- Change this line: -->
<WorkingDirectory>C:\Users\CHANGE_USERNAME\ai-stock-trading-bot</WorkingDirectory>

<!-- To your actual project directory: -->
<WorkingDirectory>C:\Users\YourUsername\ai-stock-trading-bot</WorkingDirectory>
```

**3. User SID (Line 20) - Optional but Recommended:**
```xml
<!-- Change this line: -->
<UserId>S-1-5-21-CHANGE-THIS-TO-YOUR-USER-SID</UserId>

<!-- To your actual Windows SID. Find it with PowerShell: -->
<!-- (Get-WmiObject Win32_UserAccount -Filter "Name='$env:USERNAME'").SID -->
<UserId>S-1-5-21-1234567890-1234567890-1234567890-1001</UserId>
```

### Step 1.2: Import Task via Command Line

Open **Command Prompt as Administrator** and run:

```cmd
cd C:\Users\YourUsername\ai-stock-trading-bot\systemd
schtasks /create /tn "PreMarketReport" /xml premarket_report_task.xml
```

Expected output:
```
SUCCESS: The scheduled task "PreMarketReport" has successfully been created.
```

### Step 1.3: Verify Task Creation

```cmd
schtasks /query /tn "PreMarketReport" /v /fo list
```

You should see:
- **HostName:** Your computer name
- **TaskName:** \PreMarketReport
- **Next Run Time:** Next weekday at 6:00 PM
- **Status:** Ready
- **Task To Run:** python.exe daily_premarket_report.py

### Step 1.4: Test Task Execution

Trigger the task manually to verify it works:

```cmd
schtasks /run /tn "PreMarketReport"
```

Expected output:
```
SUCCESS: Attempted to run the scheduled task "PreMarketReport".
```

Check the report was generated:
```cmd
dir C:\Users\YourUsername\ai-stock-trading-bot\reports\premarket
```

You should see:
- `premarket_report_YYYY-MM-DD.md`
- `premarket_metadata_YYYY-MM-DD.json`
- `latest.md`

---

## Method 2: GUI Configuration (Manual Setup)

### Step 2.1: Open Task Scheduler

1. Press **Win + R** to open Run dialog
2. Type `taskschd.msc` and press Enter
3. Task Scheduler window will open

### Step 2.2: Create New Task

1. In the right panel, click **"Create Task..."** (NOT "Create Basic Task")
2. The Create Task dialog will open with multiple tabs

### Step 2.3: General Tab

Configure the following settings:

**Name:**
```
PreMarketReport
```

**Description:**
```
Daily Pre-Market Trading Report Generator - Runs Monday through Friday at 6:00 PM ET to generate next-day trading analysis using Claude AI.
```

**Security options:**
- ☑ Run whether user is logged on or not
- ☐ Do not store password (unchecked)
- ☑ Run with highest privileges (if needed)

**Configure for:**
- Select: **Windows 10** or **Windows 11** (match your OS)

### Step 2.4: Triggers Tab

1. Click **"New..."** button
2. Configure trigger settings:

**Begin the task:**
- Select: **On a schedule**

**Settings:**
- ☑ Daily
- Start: **[Today's date]** at **6:00:00 PM**
- Recur every: **1** days

**Advanced settings:**
- ☑ Stop task if it runs longer than: **1 hour**
- ☑ Enabled

**Weekly schedule:**
- Click "Weekly" radio button
- Recur every: **1** weeks
- Select days: ☑ Monday ☑ Tuesday ☑ Wednesday ☑ Thursday ☑ Friday
- ☐ Saturday ☐ Sunday (unchecked)

3. Click **OK**

### Step 2.5: Actions Tab

1. Click **"New..."** button
2. Configure action:

**Action:**
- Select: **Start a program**

**Program/script:**
```
C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\python.exe
```
*Note: Find your Python path with: `where python` in Command Prompt*

**Add arguments:**
```
daily_premarket_report.py
```

**Start in:**
```
C:\Users\YourUsername\ai-stock-trading-bot
```

3. Click **OK**

### Step 2.6: Conditions Tab

Configure the following:

**Power:**
- ☐ Start the task only if the computer is on AC power (unchecked)
- ☐ Stop if the computer switches to battery power (unchecked)
- ☐ Wake the computer to run this task (unchecked)

**Network:**
- ☑ Start only if the following network connection is available: **Any connection**

### Step 2.7: Settings Tab

Configure the following:

**General:**
- ☑ Allow task to be run on demand
- ☑ Run task as soon as possible after a scheduled start is missed
- ☑ If the task fails, restart every: **15 minutes**
- Attempt to restart up to: **3** times

**Execution time limit:**
- ☑ Stop the task if it runs longer than: **1 hour**

**Multiple instances:**
- If the task is already running, then the following rule applies:
- Select: **Do not start a new instance**

### Step 2.8: Save Task

1. Click **OK** to save the task
2. If prompted, enter your Windows password
3. The task will now appear in the Task Scheduler Library

---

## Verification and Testing

### Verify Task is Created

**Option 1: Command Line**
```cmd
schtasks /query /tn "PreMarketReport"
```

**Option 2: Task Scheduler GUI**
1. Open Task Scheduler
2. Navigate to **Task Scheduler Library**
3. Find **PreMarketReport** in the list
4. Right-click → **Properties** to view configuration

### Check Next Run Time

**Command Line:**
```cmd
schtasks /query /tn "PreMarketReport" /fo list | findstr "Next Run Time"
```

**GUI:**
1. Task Scheduler Library
2. Select **PreMarketReport**
3. Check "Next Run Time" in the bottom panel

### Manual Test Run

**Option 1: Command Line**
```cmd
schtasks /run /tn "PreMarketReport"
```

**Option 2: GUI**
1. Task Scheduler Library
2. Right-click **PreMarketReport**
3. Click **Run**

**Option 3: Batch File**
```cmd
cd C:\Users\YourUsername\ai-stock-trading-bot\systemd
run_report.bat
```

### Verify Report Generation

After running, check:

```cmd
dir C:\Users\YourUsername\ai-stock-trading-bot\reports\premarket
```

You should see:
- `premarket_report_2025-10-14.md` (dated report)
- `premarket_metadata_2025-10-14.json` (metadata)
- `latest.md` (symlink or copy)

---

## Environment Variables Setup

### Option 1: User Environment Variables (Recommended)

1. Press **Win + Pause/Break** (or right-click **This PC** → **Properties**)
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **User variables**, click **New**

Add each variable:
```
Variable name:  ANTHROPIC_API_KEY
Variable value: your_anthropic_api_key_here

Variable name:  ALPACA_API_KEY
Variable value: your_alpaca_api_key

Variable name:  ALPACA_SECRET_KEY
Variable value: your_alpaca_secret_key

Variable name:  ALPACA_BASE_URL
Variable value: https://paper-api.alpaca.markets

Variable name:  EMAIL_ENABLED
Variable value: true

Variable name:  EMAIL_SENDER
Variable value: your_email@gmail.com

Variable name:  EMAIL_PASSWORD
Variable value: your_gmail_app_password

Variable name:  EMAIL_RECIPIENT
Variable value: recipient@example.com

Variable name:  SLACK_WEBHOOK
Variable value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

Variable name:  DISCORD_WEBHOOK
Variable value: https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

5. Click **OK** on all dialogs
6. **Restart Command Prompt** for changes to take effect

### Option 2: .env File (Already Configured)

If you already have a `.env` file in your project root, the script will automatically load it. No additional configuration needed.

**Verify .env file exists:**
```cmd
type C:\Users\YourUsername\ai-stock-trading-bot\.env
```

---

## Viewing Execution Logs

### Method 1: Task Scheduler History

**Enable Task History (if disabled):**
1. Open Task Scheduler
2. In the right panel, click **"Enable All Tasks History"**

**View Task History:**
1. Task Scheduler Library
2. Select **PreMarketReport**
3. Click **History** tab (bottom panel)
4. Look for events:
   - **Task Started** (Event ID: 100)
   - **Task Completed** (Event ID: 102)
   - **Task Failed** (Event ID: 103)

**Export History:**
1. Right-click on event
2. Select **Save Selected Events As...**
3. Save as `.evtx` or `.xml` file

### Method 2: Event Viewer

1. Press **Win + R** → type `eventvwr.msc` → Enter
2. Navigate to:
   ```
   Event Viewer (Local)
   → Applications and Services Logs
   → Microsoft
   → Windows
   → TaskScheduler
   → Operational
   ```
3. Filter by **Source:** TaskScheduler
4. Look for **Task Name:** PreMarketReport

### Method 3: Python Script Output

The script logs to the console. To capture output:

**Option 1: Redirect to file in task action**
```
Program: cmd.exe
Arguments: /c "python daily_premarket_report.py > logs\premarket_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1"
```

**Option 2: Use run_report.bat with logging:**

Edit `systemd/run_report.bat`:
```batch
@echo off
cd /d C:\Users\YourUsername\ai-stock-trading-bot

REM Create logs directory if needed
if not exist logs mkdir logs

REM Run with logging
python daily_premarket_report.py > logs\premarket_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1

type logs\premarket_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
pause
```

---

## Managing the Scheduled Task

### Common Commands

**Check task status:**
```cmd
schtasks /query /tn "PreMarketReport"
```

**Enable task:**
```cmd
schtasks /change /tn "PreMarketReport" /enable
```

**Disable task:**
```cmd
schtasks /change /tn "PreMarketReport" /disable
```

**Delete task:**
```cmd
schtasks /delete /tn "PreMarketReport" /f
```

**View detailed information:**
```cmd
schtasks /query /tn "PreMarketReport" /v /fo list
```

**Export task XML:**
```cmd
schtasks /query /tn "PreMarketReport" /xml > PreMarketReport_backup.xml
```

### Modifying Schedule

**Option 1: Command Line**
```cmd
REM Change time to 5:30 PM
schtasks /change /tn "PreMarketReport" /st 17:30:00
```

**Option 2: GUI**
1. Task Scheduler Library
2. Right-click **PreMarketReport** → **Properties**
3. Go to **Triggers** tab
4. Double-click the trigger to edit
5. Change settings as needed
6. Click **OK**

---

## Troubleshooting

### Task Not Running

**Check if task is enabled:**
```cmd
schtasks /query /tn "PreMarketReport" /v /fo list | findstr "Status"
```

Should show: `Status: Ready`

If disabled:
```cmd
schtasks /change /tn "PreMarketReport" /enable
```

**Check task history:**
1. Task Scheduler
2. PreMarketReport → History tab
3. Look for error events (Event ID 103)

### Python Not Found

**Error:** "The system cannot find the file specified"

**Solution 1: Verify Python path**
```cmd
where python
```

Update task with correct Python path.

**Solution 2: Use full path in task:**
```cmd
C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\python.exe
```

### Working Directory Issues

**Error:** "No such file or directory" or "Cannot find module"

**Solution:** Verify working directory is set correctly in task action:
```cmd
schtasks /query /tn "PreMarketReport" /xml
```

Check `<WorkingDirectory>` element matches your project path.

### Import Errors

**Error:** "ModuleNotFoundError: No module named 'anthropic'"

**Solution 1: Install dependencies**
```cmd
cd C:\Users\YourUsername\ai-stock-trading-bot
pip install -r requirements.txt
```

**Solution 2: Use virtual environment**

If you use a virtual environment, update task action:
```
Program: C:\Users\YourUsername\ai-stock-trading-bot\venv\Scripts\python.exe
Arguments: daily_premarket_report.py
```

### API Key Errors

**Error:** "ANTHROPIC_API_KEY not set"

**Solution 1: Check .env file exists**
```cmd
type C:\Users\YourUsername\ai-stock-trading-bot\.env
```

**Solution 2: Add environment variables** (see Environment Variables Setup section)

**Solution 3: Verify .env file format**
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
# No spaces around =
# No quotes unless value has spaces
# One variable per line
```

### Permission Denied

**Error:** "Access is denied" or "Permission denied"

**Solution 1: Run as administrator**

Edit task:
1. Task Scheduler → PreMarketReport → Properties
2. General tab
3. ☑ Run with highest privileges
4. OK

**Solution 2: Check file permissions**
```cmd
icacls C:\Users\YourUsername\ai-stock-trading-bot
```

Ensure your user has Full Control.

### Task Hangs/Times Out

**Error:** Task runs for 1 hour then stops

**Solution:** Increase timeout in task settings:

```cmd
schtasks /change /tn "PreMarketReport" /v /et 2:00:00
```

Or in GUI:
1. Properties → Settings tab
2. "Stop the task if it runs longer than:" → **2 hours**

---

## Testing the Batch File

### Option 1: Double-click

1. Navigate to `systemd/` folder in Windows Explorer
2. Double-click `run_report.bat`
3. Watch the console output
4. Press any key when done

### Option 2: Command Line

```cmd
cd C:\Users\YourUsername\ai-stock-trading-bot\systemd
run_report.bat
```

### Option 3: With Test Mode

Edit `run_report.bat` to add `--test` flag:
```batch
python daily_premarket_report.py --test
```

This will generate a mock report without calling Claude API.

---

## Advanced Configuration

### Email on Task Failure

Add an email action to the task:

1. Task Scheduler → PreMarketReport → Properties
2. Actions tab → New
3. Action: **Send an e-mail** (deprecated in Windows 10+, use PowerShell script instead)

**Alternative: PowerShell script for email:**

Create `systemd/send_error_email.ps1`:
```powershell
$From = "your_email@gmail.com"
$To = "recipient@example.com"
$Subject = "PreMarketReport Task Failed"
$Body = "The scheduled task PreMarketReport has failed. Please check logs."
$SMTPServer = "smtp.gmail.com"
$SMTPPort = 587
$Credential = New-Object System.Management.Automation.PSCredential ($From, (ConvertTo-SecureString "your_app_password" -AsPlainText -Force))

Send-MailMessage -From $From -To $To -Subject $Subject -Body $Body -SmtpServer $SMTPServer -Port $SMTPPort -UseSsl -Credential $Credential
```

Add trigger in task:
1. Triggers tab → New
2. Begin the task: **On an event**
3. Log: **Microsoft-Windows-TaskScheduler/Operational**
4. Source: **TaskScheduler**
5. Event ID: **103** (Task failed)

### Run Multiple Instances

If you need to allow multiple simultaneous runs:

1. Settings tab
2. "If the task is already running:" → **Run a new instance in parallel**

**Warning:** Not recommended for this task as reports could conflict.

### Retry on Failure

Configure automatic retries:

1. Settings tab
2. ☑ If the task fails, restart every: **15 minutes**
3. Attempt to restart up to: **3 times**

---

## Uninstallation

### Remove Scheduled Task

**Command Line:**
```cmd
schtasks /delete /tn "PreMarketReport" /f
```

**GUI:**
1. Task Scheduler Library
2. Right-click **PreMarketReport**
3. Select **Delete**
4. Confirm

### Backup Before Removal

Export task configuration before deleting:
```cmd
schtasks /query /tn "PreMarketReport" /xml > PreMarketReport_backup.xml
```

---

## Additional Notes

### Time Zone Considerations

- Windows Task Scheduler uses your system timezone
- Ensure your Windows timezone is set to **Eastern Time (US & Canada)**
- Verify with:
  ```cmd
  tzutil /g
  ```

  Should show: `Eastern Standard Time`

- To change timezone:
  ```cmd
  tzutil /s "Eastern Standard Time"
  ```

### Daylight Saving Time

- Task Scheduler automatically handles DST transitions
- Your task will always run at 6:00 PM local Eastern Time
- No manual adjustment needed for EDT/EST

### Multiple Users

If multiple users need to run this task:

**Option 1: System-wide task**
- Configure for: **All users**
- Run whether user is logged on or not

**Option 2: Per-user tasks**
- Each user imports their own task
- Update paths to match user profile

### Security Best Practices

1. **Secure .env file:**
   ```cmd
   icacls .env /inheritance:r /grant:r "%USERNAME%:F"
   ```

2. **Don't store passwords in task XML**
   - Use .env file or Windows environment variables

3. **Run with least privilege:**
   - Uncheck "Run with highest privileges" unless needed

4. **Backup task configuration:**
   ```cmd
   schtasks /query /tn "PreMarketReport" /xml > backup\task.xml
   ```

---

## Summary Checklist

After following this guide, verify:

- ✅ Task shows in Task Scheduler Library
- ✅ Next run time is correct (next weekday at 6:00 PM)
- ✅ Manual test run succeeds
- ✅ Report files are generated in `reports/premarket/`
- ✅ Task history shows successful execution
- ✅ Environment variables or .env file configured
- ✅ Batch file works for manual testing

**Quick verification:**
```cmd
schtasks /query /tn "PreMarketReport"
schtasks /run /tn "PreMarketReport"
dir C:\Users\YourUsername\ai-stock-trading-bot\reports\premarket
```

---

## Support

For issues with:
- **Task Scheduler:** Check Event Viewer (eventvwr.msc)
- **Report generation:** See main README.md troubleshooting section
- **Python errors:** Run `python daily_premarket_report.py --test` manually

## Additional Resources

- [Microsoft Task Scheduler Documentation](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [Schtasks Command Reference](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks)
- Main project README.md for report generator configuration

---

**Version:** 1.0.0
**Last Updated:** October 13, 2025
**Tested On:** Windows 10 (21H2, 22H2), Windows 11 (22H2, 23H2)
