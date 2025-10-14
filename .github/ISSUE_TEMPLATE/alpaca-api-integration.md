---
name: Connect Post-Market Report to Alpaca API
about: Integrate Alpaca API for real-time position data in post-market reports
title: 'Connect post-market report generator to Alpaca API for real-time positions'
labels: enhancement, api-integration, post-market-reporting
assignees: ''
---

## Description

The enhanced post-market report generator currently has placeholder code that needs to be connected to the Alpaca API to fetch actual portfolio positions.

## Current State

Two locations in `research/data/reports/enhanced_post_market_report.py` have TODO comments indicating where API integration is needed:
- **Line 106**: Position fetching logic
- **Line 137**: Position data retrieval

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
- [ ] Unit tests added for position fetching logic
- [ ] Documentation updated with API usage examples

## Related Files

- `research/data/reports/enhanced_post_market_report.py` (main file to modify)
- `daily_premarket_report.py` (reference for API usage patterns)
- `health_check.py` (reference for Alpaca API connection testing)
- `scripts/performance/get_portfolio_status.py` (similar functionality)

## Dependencies

- `alpaca-py` library (already in requirements.txt ✅)
- Alpaca API credentials in `.env` file (already configured ✅)

## Estimated Effort

⏱️ **2-3 hours**

## Priority

🟡 **Medium**

This enhances reporting functionality but is not blocking any critical features.

## Notes

- Similar API integration already exists in `health_check.py` - can use as reference
- Consider caching position data to reduce API calls
- Ensure proper error messages for users if API is unavailable
- May want to add retry logic for transient API failures

## Testing Strategy

1. **Unit Tests**: Mock Alpaca API responses
2. **Integration Tests**: Test with actual paper trading account
3. **Error Cases**: Test API timeout, invalid credentials, network errors
4. **Data Validation**: Verify position data format matches expectations
