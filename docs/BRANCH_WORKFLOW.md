# Git Branch Workflow for Trading Bot

## Daily Workflow

### 1. Create a Feature Branch
```bash
# Always start from latest master
git checkout master
git pull origin master

# Create new branch for your work
git checkout -b feature/sept-19-trades
# or
git checkout -b fix/dee-bot-calculations
# or
git checkout -b update/daily-positions
```

### 2. Make Your Changes
```bash
# Edit files as needed
# Test your changes locally
python scripts/test_strategy.py

# Commit changes
git add -A
git commit -m "Add defensive rebalancing logic for DEE-BOT"
```

### 3. Push to GitHub
```bash
# Push your feature branch
git push origin feature/sept-19-trades
```

### 4. Create Pull Request
- Go to GitHub repository
- Click "Compare & pull request" button
- Add description of changes
- Review the diff (changes)
- Click "Create pull request"

### 5. Merge to Master
- Review all changes one more time
- Click "Merge pull request"
- Delete the feature branch

## Branch Naming Conventions

- `feature/` - New features (feature/add-options-trading)
- `fix/` - Bug fixes (fix/telegram-report-error)
- `update/` - Updates/improvements (update/dee-bot-positions)
- `hotfix/` - Urgent production fixes (hotfix/stop-loss-trigger)

## Emergency Trades

For time-sensitive market actions, you can:
1. Create a `hotfix/` branch
2. Make minimal required changes
3. Create PR with "URGENT" label
4. Self-approve and merge immediately

## Benefits

1. **Safety**: Can't accidentally break master
2. **History**: Clear record of all changes
3. **Rollback**: Easy to revert bad changes
4. **Testing**: Can test branches before merging
5. **Documentation**: PRs document why changes were made

## Example Day

```bash
# Morning: Update positions
git checkout -b update/sept-19-positions
# ... make changes ...
git push origin update/sept-19-positions
# Create PR, merge

# Afternoon: Fix calculation bug
git checkout master
git pull
git checkout -b fix/pnl-calculation
# ... fix bug ...
git push origin fix/pnl-calculation
# Create PR, merge

# Evening: Add new feature
git checkout master
git pull
git checkout -b feature/trailing-stops
# ... develop feature ...
git push origin feature/trailing-stops
# Create PR, review tomorrow, then merge
```

## Commands Reference

```bash
# See all branches
git branch -a

# Switch branches
git checkout branch-name

# Delete local branch
git branch -d branch-name

# Update master
git checkout master
git pull origin master

# See what changed
git diff master...feature/my-branch
```