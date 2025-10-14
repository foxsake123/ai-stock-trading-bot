# GitHub Issues to Create from TODO Comments
**Date**: October 13, 2025
**Status**: Ready for creation

---

## Overview

This document lists all TODO/FIXME comments found in the codebase that should be converted to tracked GitHub issues.

**Total TODOs Found**: 2
**Files Affected**: 1

---

## Issues to Create

### Issue #1: Connect Post-Market Report to Alpaca API

**File**: `research/data/reports/enhanced_post_market_report.py`
**Lines**: 106, 137
**Priority**: Medium
**Labels**: `enhancement`, `api-integration`, `post-market-reporting`

**Title**: Connect post-market report generator to Alpaca API for real-time positions

**Description**:
```markdown
## Description
The enhanced post-market report generator currently has placeholder code that needs to be connected to the Alpaca API to fetch actual portfolio positions.

## Current State
Two locations in the code have TODO comments indicating where API integration is needed:
- Line 106: Position fetching logic
- Line 137: Position data retrieval

## Expected Behavior
The post-market report should:
1. Connect to Alpaca API using credentials from environment variables
2. Fetch current positions for both DEE-BOT and SHORGAN-BOT portfolios
3. Include real-time position data in the generated reports
4. Handle API errors gracefully with fallback messaging

## Implementation Details
```python
# Current code (line 106 & 137):
# TODO: Connect to Alpaca API to get actual positions

# Suggested implementation:
from alpaca.trading.client import TradingClient
import os

def get_current_positions(bot_type):
    """
    Fetch current positions from Alpaca API

    Args:
        bot_type: Either 'DEE' or 'SHORGAN'

    Returns:
        List of current positions with quantities and market values
    """
    try:
        client = TradingClient(
            api_key=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY')
        )

        positions = client.get_all_positions()

        # Filter positions by bot type if needed
        # (implementation depends on how portfolios are separated)

        return positions
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []
```

## Acceptance Criteria
- [ ] Alpaca API client properly initialized with credentials
- [ ] Current positions retrieved successfully
- [ ] Position data includes: symbol, quantity, market value, P&L
- [ ] Error handling implemented for API failures
- [ ] Integration tested with paper trading account
- [ ] Documentation updated with API usage

## Related Files
- `research/data/reports/enhanced_post_market_report.py` (main file)
- `daily_premarket_report.py` (reference for API usage patterns)
- `health_check.py` (reference for Alpaca API connection testing)

## Dependencies
- `alpaca-py` library (already in requirements.txt)
- Alpaca API credentials in `.env` file

## Estimated Effort
2-3 hours

## Notes
- Similar API integration already exists in `health_check.py` - can use as reference
- Consider caching position data to reduce API calls
- Ensure proper error messages for users if API is unavailable
```

---

## Summary

### By Priority
- **High**: 0 issues
- **Medium**: 1 issue (Alpaca API integration)
- **Low**: 0 issues

### By Category
- **API Integration**: 1 issue
- **Enhancement**: 1 issue

### Next Steps

1. **Create GitHub Issue #1**:
   ```bash
   gh issue create --title "Connect post-market report generator to Alpaca API for real-time positions" \
                   --label "enhancement,api-integration,post-market-reporting" \
                   --body-file docs/issue_templates/alpaca_api_integration.md
   ```

2. **Add to Project Board**: Assign to "Enhancements" column

3. **Link to Milestone**: Consider adding to next sprint/release milestone

4. **Assign Owner**: Assign to appropriate developer

---

## Additional Recommendations

While only 2 TODO comments were found in the code, consider creating additional issues for:

### From Repository Review (October 13, 2025)

1. **Increase Test Coverage to 50%+**
   - Current: 30.60%
   - Target: 50%+
   - Priority: High
   - Estimated: 8-12 hours

2. **Fix Integration Test Failures**
   - 14/304 tests failing
   - Mostly in test_integration.py
   - Priority: Medium
   - Estimated: 2-3 hours

3. **Add Visual Architecture Diagram**
   - Replace ASCII art in README
   - Use draw.io or mermaid
   - Priority: Low
   - Estimated: 2 hours

4. **Pin Production Dependencies**
   - Create requirements-lock.txt
   - Pin exact versions
   - Priority: Medium
   - Estimated: 1 hour

5. **Refactor Large Files**
   - `daily_premarket_report.py` (620 lines)
   - `backtest_recommendations.py` (735 lines)
   - Priority: Low
   - Estimated: 4-6 hours

6. **Add Performance Testing**
   - Load testing
   - API latency benchmarks
   - Priority: Low
   - Estimated: 4-6 hours

7. **Security Audit**
   - Run `safety check`
   - Run `pip-audit`
   - Review for vulnerabilities
   - Priority: Medium
   - Estimated: 2-3 hours

---

## Issue Template

Use this template when creating new issues from TODOs:

```markdown
## Description
[Brief description of what needs to be done]

## Current State
[What currently exists - include TODO location]

## Expected Behavior
[What should happen after implementation]

## Implementation Details
[Code snippets or technical approach]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests added
- [ ] Documentation updated

## Related Files
- file1.py (description)
- file2.py (description)

## Dependencies
- Dependency 1
- Dependency 2

## Estimated Effort
X hours

## Notes
[Additional context or considerations]
```

---

## Cleanup Actions

After creating GitHub issues:

1. **Update Code Comments**:
   ```python
   # Before:
   # TODO: Connect to Alpaca API to get actual positions

   # After:
   # See GitHub Issue #123: Connect post-market report to Alpaca API
   # TODO tracked in: https://github.com/username/repo/issues/123
   ```

2. **Add Issue Reference**:
   - Link issue number in code comments
   - Link to project board
   - Add to sprint planning

3. **Update Documentation**:
   - Add issue to CHANGELOG "Planned" section
   - Update NEXT_STEPS_ROADMAP.md
   - Reference in relevant documentation

---

## GitHub CLI Commands

```bash
# List all issues
gh issue list

# Create new issue
gh issue create --title "Issue title" --body "Description" --label "enhancement"

# View issue
gh issue view 123

# Close completed issue
gh issue close 123

# Add to project
gh issue edit 123 --add-project "Project Name"

# Assign to user
gh issue edit 123 --assignee username
```

---

**Generated**: October 13, 2025
**Last Updated**: October 13, 2025
**Status**: Ready for GitHub issue creation
