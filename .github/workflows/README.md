# GitHub Actions Workflows

This directory contains automated workflows for the AI Trading Bot.

## Workflows

### 1. Daily Trading Pipeline (`daily_run.yml`)

**Purpose:** Automated daily execution of the trading pipeline.

**Schedule:**
- Runs Monday-Friday at 6:00 AM ET
- Automatically accounts for EST/EDT timezone changes
- Checks for US market holidays before execution
- Skips weekends automatically

**Triggers:**
- Scheduled: Mon-Fri at 6:00 AM ET (10:00/11:00 UTC depending on DST)
- Manual: Via workflow_dispatch in GitHub UI

**Manual Trigger Options:**
- `skip_market_check`: Set to 'true' to bypass market hours validation (for testing)
- `test_mode`: Set to 'true' for paper trading, 'false' for live trading

**Required Secrets:**
```
ANTHROPIC_API_KEY      - Claude API key for AI analysis
ALPACA_API_KEY         - Alpaca trading API key
ALPACA_SECRET_KEY      - Alpaca secret key
TELEGRAM_BOT_TOKEN     - Telegram bot token for notifications
TELEGRAM_CHAT_ID       - Telegram chat ID for alerts
SLACK_WEBHOOK          - Slack webhook URL for failure notifications
```

**Jobs:**

1. **pre_flight** (5 min timeout)
   - Checks if market is open
   - Validates trading day (no weekends/holidays)
   - Outputs decision to run or skip

2. **run_pipeline** (45 min timeout)
   - Executes daily_pipeline.py
   - Runs all 7 phases:
     - Data collection
     - Agent analysis
     - Bull/Bear debates
     - Strategy allocation
     - Report generation
     - Notifications
     - Intraday monitoring
   - Uploads artifacts (reports, logs, metrics)
   - Sends notifications on failure

3. **summary**
   - Generates workflow summary
   - Provides links to artifacts
   - Reports execution metrics

**Artifacts:**
- `trading-reports-{date}` - Generated reports (retained 30 days)
- `pipeline-logs-{date}` - Execution logs (retained 7 days)
- `metrics-{date}` - Performance metrics (retained 30 days)

**Notifications:**
- **Slack:** Sent on pipeline failure with detailed error info
- **Telegram:** Sent on pipeline failure with summary
- **GitHub:** Job summaries generated for all runs

**Usage:**

Automatic execution (no action needed):
```
Mon-Fri at 6:00 AM ET: Workflow runs automatically
```

Manual execution:
```bash
1. Go to GitHub Actions tab
2. Select "Daily Trading Pipeline"
3. Click "Run workflow"
4. Select branch (usually 'master')
5. Choose options:
   - skip_market_check: true/false
   - test_mode: true/false
6. Click "Run workflow"
```

View results:
```bash
1. Go to Actions tab
2. Click on workflow run
3. View job logs
4. Download artifacts from "Artifacts" section
```

**Cost:**
- GitHub Actions free tier: 2,000 minutes/month
- Pipeline runtime: ~10-15 minutes per execution
- Monthly usage: ~20 trading days × 15 min = ~300 min/month
- **Well within free tier** ✅

### 2. Test Suite (`tests.yml`)

**Purpose:** Automated testing on code changes.

**Triggers:**
- Push to master, main, or develop branches
- Pull requests to master or main
- Manual via workflow_dispatch

**Jobs:**

1. **test** - Unit tests
   - Runs on multiple OS (Ubuntu, Windows, macOS)
   - Python 3.13
   - Coverage reports uploaded to Codecov

2. **integration-tests** - Integration tests
   - Runs only on push to master
   - Requires API secrets
   - Tests real integrations

3. **lint** - Code quality
   - Black formatting check
   - isort import sorting
   - flake8 linting
   - mypy type checking

**Usage:**

Automatic:
```
Tests run automatically on every push/PR
```

Manual:
```bash
1. Go to Actions tab
2. Select "Tests"
3. Click "Run workflow"
```

## Setup Instructions

### 1. Configure Secrets

Go to repository Settings → Secrets and variables → Actions:

**Required for daily_run.yml:**
```
Name                    Description
--------------------    ---------------------------------
ANTHROPIC_API_KEY       Claude Sonnet 4 API key
ALPACA_API_KEY          Alpaca trading API key
ALPACA_SECRET_KEY       Alpaca secret key
TELEGRAM_BOT_TOKEN      Telegram bot token
TELEGRAM_CHAT_ID        Your Telegram chat ID
SLACK_WEBHOOK           Slack incoming webhook URL
```

**Optional for tests.yml:**
```
ALPACA_API_KEY_DEE      DEE-BOT Alpaca API key (for integration tests)
ALPACA_SECRET_KEY_DEE   DEE-BOT Alpaca secret (for integration tests)
```

### 2. Enable Workflows

Workflows are enabled by default when this directory exists in `.github/workflows/`.

To manually enable:
```bash
1. Go to Actions tab
2. Click "I understand my workflows, go ahead and enable them"
```

### 3. Configure Notifications

**Slack:**
```bash
1. Create Slack App: https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Create webhook for your channel
4. Add webhook URL as SLACK_WEBHOOK secret
```

**Telegram:**
```bash
1. Create bot: Message @BotFather on Telegram
2. Get bot token
3. Get your chat ID: Message @userinfobot
4. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID secrets
```

### 4. Update Market Holidays

Edit `.github/workflows/daily_run.yml` annually:

```python
# Update this list for new year
holidays = [
    "2026-01-01",  # New Year's Day
    "2026-01-19",  # MLK Day
    "2026-02-16",  # Presidents Day
    "2026-04-03",  # Good Friday
    "2026-05-25",  # Memorial Day
    "2026-07-03",  # Independence Day (observed)
    "2026-09-07",  # Labor Day
    "2026-11-26",  # Thanksgiving
    "2026-12-25"   # Christmas
]
```

## Monitoring

### View Workflow Status

**GitHub UI:**
```
Repository → Actions tab → Select workflow → View runs
```

**GitHub CLI:**
```bash
# List recent workflow runs
gh run list --workflow=daily_run.yml --limit 10

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

### Check Artifacts

**Web UI:**
```
Actions → Select run → Scroll to "Artifacts" section → Download
```

**CLI:**
```bash
gh run download <run-id> -n trading-reports-2025-10-23
```

### Review Logs

**Real-time (during run):**
```bash
gh run watch <run-id>
```

**After completion:**
```bash
gh run view <run-id> --log
```

## Troubleshooting

### Workflow Not Running

**Symptom:** Scheduled workflow doesn't execute at 6 AM

**Causes:**
1. Workflow file syntax error
2. Repository is private and out of free minutes
3. GitHub Actions disabled
4. Market check skipped execution (holiday/weekend)

**Solutions:**
```bash
# Check workflow syntax
yamllint .github/workflows/daily_run.yml

# Check Actions status
gh run list --workflow=daily_run.yml --limit 5

# Manually trigger
gh workflow run daily_run.yml
```

### Pipeline Fails

**Symptom:** Red X on workflow run

**Solutions:**
1. Check job logs:
   ```bash
   gh run view <run-id> --log
   ```

2. Download and review logs artifact:
   ```bash
   gh run download <run-id> -n pipeline-logs-*
   ```

3. Check Slack/Telegram for error details

4. Review metrics:
   ```bash
   gh run download <run-id> -n metrics-*
   cat data/state/last_run_metrics.json
   ```

### Secrets Not Working

**Symptom:** "Error: Secret not found" or API authentication failures

**Solutions:**
1. Verify secrets exist:
   ```bash
   Settings → Secrets and variables → Actions
   ```

2. Check secret names match exactly (case-sensitive)

3. Re-save secrets (copy-paste without extra spaces)

4. Test manually:
   ```bash
   gh workflow run daily_run.yml
   ```

### Timezone Issues

**Symptom:** Pipeline runs at wrong time

**Solutions:**
1. Verify cron schedule accounts for DST:
   ```yaml
   # EST (Nov-Mar): 6 AM ET = 11:00 UTC
   - cron: '0 11 * * 1-5'

   # EDT (Mar-Nov): 6 AM ET = 10:00 UTC
   - cron: '0 10 * * 1-5'
   ```

2. Check runner timezone:
   ```bash
   # In workflow, add debug step:
   - run: date
   - run: echo $TZ
   ```

### Artifacts Missing

**Symptom:** No artifacts to download after run

**Causes:**
1. Pipeline failed before report generation
2. Retention period expired (30 days for reports, 7 for logs)
3. No reports generated (market closed)

**Solutions:**
```bash
# Check if pipeline reached artifact upload step
gh run view <run-id> --log | grep "Upload"

# Check retention settings in workflow file
```

## Advanced Usage

### Run Specific Phases

To run only certain pipeline phases:

```yaml
# In daily_run.yml, modify command:
command: python scripts/daily_pipeline.py --phases 1,2,3
```

### Increase Timeout

If pipeline takes longer than 45 minutes:

```yaml
# In run_pipeline job:
timeout-minutes: 60  # Increase from 45 to 60
```

### Add More Notifications

Example: Add Discord notification

```yaml
- name: Send Discord notification
  if: failure()
  env:
    DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
  run: |
    curl -X POST $DISCORD_WEBHOOK \
      -H "Content-Type: application/json" \
      -d '{"content": "Pipeline failed for ${{ needs.pre_flight.outputs.market_date }}"}'
```

### Custom Test Matrix

To test multiple Python versions:

```yaml
# In tests.yml:
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]
```

## Security Best Practices

1. **Never commit secrets**
   - Use GitHub Secrets for all API keys
   - Review commits before pushing

2. **Limit workflow permissions**
   ```yaml
   permissions:
     contents: read
     actions: write
   ```

3. **Use read-only mounts when possible**
   - Configs are mounted read-only in workflow

4. **Review artifact contents**
   - Ensure no secrets in uploaded logs/reports

5. **Rotate secrets regularly**
   - Update API keys every 90 days
   - Update webhook URLs if compromised

6. **Monitor workflow activity**
   ```bash
   gh run list --limit 30
   ```

## Maintenance

### Monthly Tasks

- [ ] Review workflow run history
- [ ] Check artifact storage usage
- [ ] Verify secrets are valid
- [ ] Update market holidays (annually)

### Quarterly Tasks

- [ ] Review and optimize workflow runtime
- [ ] Update action versions (@v4 → @v5)
- [ ] Rotate API keys
- [ ] Review notification channels

### Annually Tasks

- [ ] Update market holidays list
- [ ] Review DST schedule changes
- [ ] Update Python version if needed
- [ ] Review GitHub Actions pricing

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub CLI](https://cli.github.com/)
- [Cron Schedule Expressions](https://crontab.guru/)

## Support

For issues with workflows:

1. Check [troubleshooting](#troubleshooting) section
2. Review workflow logs
3. Check GitHub Status: https://www.githubstatus.com/
4. Open issue in repository with workflow run ID
