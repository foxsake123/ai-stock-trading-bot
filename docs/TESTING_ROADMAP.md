# Testing Roadmap - AI Trading Bot
**Created**: October 7, 2025
**Current Coverage**: 2.76% (78 lines / 2828 lines)
**Target Coverage**: 50%+ (1414+ lines)
**Current Tests**: 64 passing unit tests

---

## Current State

### Test Suite Overview
```
Total Tests: 64 (all passing)
Test Files: 3
Test Types: Unit tests
Lines Measured: 2828
Lines Covered: 78 (2.76%)
```

### Existing Test Files
1. **tests/unit/test_base_agent.py** (17 tests)
   - Agent initialization and metadata
   - Market data validation
   - Analysis and report generation
   - Logging and edge cases

2. **tests/unit/test_limit_price_reassessment.py** (29 tests)
   - Buy limit price adjustments
   - Market deviation handling
   - Edge cases (None, zero, extreme prices)
   - Price rounding behavior

3. **tests/unit/test_portfolio_utils.py** (18 tests)
   - Position sizing calculations
   - Risk calculations (Kelly Criterion, stop-loss)
   - Cash management and margin detection
   - Portfolio metrics and diversification

### Legacy Test Files
- tests/integration/test_fd_*.py (Financial Datasets API tests)
- tests/integration/test_trade_parsing.py
- tests/test_complete_system.py
- tests/test_live_data_sources.py

---

## Coverage Gap Analysis

### High Priority Modules (0% Coverage)
These modules are critical to trading operations and need tests:

**Agents (agents/)**
- [ ] `bull_researcher.py` - Bull case analysis
- [ ] `bear_researcher.py` - Bear case analysis
- [ ] `alternative_data_agent.py` - Alternative data signals
- [ ] `risk_manager.py` - Risk assessment
- [ ] `trade_validator.py` - Trade validation logic

**Core Trading (agents/core/)**
- [ ] `execute_dee_bot_trades.py` - DEE-BOT execution
- [ ] `execute_shorgan_bot_trades.py` - SHORGAN-BOT execution
- [ ] `generate_dee_bot_recommendations.py` - DEE-BOT signals
- [ ] `generate_shorgan_bot_recommendations.py` - SHORGAN-BOT signals
- [ ] `monitor_dee_bot.py` - Portfolio monitoring

**Automation (scripts/automation/)**
- [ ] `financial_datasets_integration.py` - API integration
- [ ] `consensus_validator.py` - Multi-agent consensus
- [ ] `execute_daily_trades.py` - Daily execution pipeline

**Portfolio Management (scripts/portfolio/)**
- [ ] `rebalance_phase1.py` - Emergency rebalancing
- [ ] `rebalance_phase2.py` - Strategic rebalancing
- [ ] `place_shorgan_stops.py` - Stop-loss management (NEW - Oct 7)
- [ ] `fix_dee_bot_cash.py` - Cash balance restoration (NEW - Oct 7)

**Utilities (scripts/utilities/)**
- [x] `reassess_limit_prices.py` - Limit price optimization (TESTED - Oct 7)
- [ ] `verify_all_research_prices.py` - Price verification (NEW - Oct 7)
- [ ] `cancel_all_pending.py` - Order cancellation
- [ ] `check_remaining_orders.py` - Order monitoring

---

## Phased Testing Plan

### Phase 1: Foundation (COMPLETE) ✅
**Target**: 5% coverage
**Status**: DONE (64 tests, 2.76% coverage)
- [x] Base agent tests (17 tests)
- [x] Portfolio utility tests (18 tests)
- [x] Limit price reassessment tests (29 tests)
- [x] pytest.ini configuration updated
- [x] Test directory structure created

### Phase 2: Core Agents (Target: 20% coverage)
**Estimated Effort**: 8-12 hours
**Priority**: HIGH

**Bull/Bear Researchers** (4-6 hours)
```python
# tests/agents/test_bull_researcher.py
- Test signal generation
- Test conviction scoring
- Test data source integration
- Test catalyst identification
```

**Risk Manager** (2-3 hours)
```python
# tests/agents/test_risk_manager.py
- Test position sizing
- Test stop-loss calculations
- Test portfolio risk aggregation
- Test margin compliance checks
```

**Trade Validator** (2-3 hours)
```python
# tests/agents/test_trade_validator.py
- Test trade validation rules
- Test conflict detection
- Test risk limit enforcement
```

### Phase 3: Trading Execution (Target: 35% coverage)
**Estimated Effort**: 12-16 hours
**Priority**: HIGH

**DEE-BOT Execution** (4-5 hours)
```python
# tests/core/test_execute_dee_bot.py
- Test order generation
- Test beta-neutral rebalancing
- Test long-only compliance
- Mock Alpaca API calls
```

**SHORGAN-BOT Execution** (4-5 hours)
```python
# tests/core/test_execute_shorgan_bot.py
- Test catalyst trade execution
- Test stop-loss placement
- Test short position handling
- Mock Alpaca API calls
```

**Consensus Validator** (4-6 hours)
```python
# tests/automation/test_consensus_validator.py
- Test multi-agent score aggregation
- Test conflict resolution
- Test threshold enforcement
```

### Phase 4: Integration & Automation (Target: 50% coverage)
**Estimated Effort**: 16-20 hours
**Priority**: MEDIUM

**Financial Datasets Integration** (6-8 hours)
```python
# tests/integration/test_fd_full_integration.py
- Test API authentication
- Test data retrieval and parsing
- Test error handling
- Test rate limiting
```

**Daily Automation Pipeline** (6-8 hours)
```python
# tests/automation/test_daily_pipeline.py
- Test end-to-end workflow
- Test error recovery
- Test notification system
- Integration tests with Telegram
```

**Portfolio Management** (4-4 hours)
```python
# tests/portfolio/test_rebalancing.py
- Test Phase 1 rebalancing logic
- Test Phase 2 rebalancing logic
- Test cash restoration
- Test position liquidation
```

---

## Testing Best Practices

### Test Structure
```python
# Arrange
agent = BullResearcher("test_bull_001")
market_data = {"price": 100.00, "volume": 1000000}

# Act
result = agent.analyze("AAPL", market_data)

# Assert
assert result["recommendation"]["action"] == "BUY"
assert result["confidence"] > 0.70
```

### Mocking External APIs
```python
@pytest.fixture
def mock_alpaca_api(mocker):
    """Mock Alpaca API for testing"""
    mock = mocker.patch('alpaca_trade_api.REST')
    mock.return_value.get_account.return_value = MockAccount(
        cash=100000.0,
        portfolio_value=200000.0
    )
    return mock

def test_execute_trade_with_mock(mock_alpaca_api):
    """Test trade execution with mocked API"""
    executor = TradeExecutor(mock_alpaca_api)
    result = executor.execute_buy("AAPL", 100, 150.00)
    assert result["status"] == "success"
```

### Test Markers
```python
@pytest.mark.unit
def test_calculate_position_size():
    """Fast unit test - no external dependencies"""
    pass

@pytest.mark.integration
def test_alpaca_connection():
    """Integration test - requires API connection"""
    pass

@pytest.mark.slow
def test_backtest_full_year():
    """Slow test - takes >10 seconds"""
    pass
```

### Running Tests
```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m unit

# Run without integration tests
pytest -m "not integration"

# Run with coverage report
pytest --cov --cov-report=html

# Run specific file
pytest tests/unit/test_base_agent.py -v
```

---

## Coverage Milestones

| Milestone | Coverage | Tests | Status | ETA |
|-----------|----------|-------|--------|-----|
| Foundation | 5% | 64 | ✅ COMPLETE | Oct 7 |
| Core Agents | 20% | ~150 | 📋 PLANNED | Week 2 |
| Execution | 35% | ~250 | 📋 PLANNED | Week 3 |
| Full System | 50% | ~400 | 🎯 TARGET | Week 4-5 |

---

## Quick Wins (2-4 hours)

These tests provide high coverage return for low effort:

1. **Test Order Parsing** (30 min)
   - Parse markdown trade files
   - Extract symbols, quantities, prices
   - Validation logic

2. **Test Risk Calculations** (1 hour)
   - Position sizing formulas
   - Stop-loss calculations
   - Portfolio risk aggregation

3. **Test Data Validation** (1 hour)
   - Market data validation
   - API response validation
   - Configuration validation

4. **Test Telegram Notifications** (30 min)
   - Message formatting
   - Error handling
   - Mock API calls

---

## Technical Debt

### Issues to Address
1. **Legacy test files not running** - Integration tests may be broken
2. **No CI/CD testing** - Tests not running on PR
3. **No performance benchmarks** - No baseline for regressions
4. **Missing docstring tests** - Code examples not validated

### Recommendations
1. Set up GitHub Actions for automatic testing
2. Add pre-commit hooks to run fast tests
3. Create performance benchmarks for critical paths
4. Add doctest validation for code examples
5. Set up nightly integration test runs

---

## Success Metrics

### Quantitative
- ✅ **Test Count**: 64 → 400+ tests (525% increase)
- 🎯 **Coverage**: 2.76% → 50%+ (1700% increase)
- 🎯 **Test Speed**: <10s for unit tests
- 🎯 **Integration Tests**: <2min full suite

### Qualitative
- ✅ Comprehensive base agent testing
- ✅ Portfolio utility testing
- ✅ Limit price optimization testing
- 🎯 All critical trading paths tested
- 🎯 Regression prevention in place
- 🎯 Confidence in deployment

---

## Resources

### Documentation
- pytest docs: https://docs.pytest.org
- pytest-cov: https://pytest-cov.readthedocs.io
- pytest-mock: https://pytest-mock.readthedocs.io

### Testing Philosophy
- **Unit Tests**: Fast, isolated, no dependencies
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Full system workflow validation
- **TDD**: Write tests before implementation (future)

---

## Next Session Checklist

**Immediate (Next Session)**:
- [ ] Review test failures (if any)
- [ ] Run coverage report and analyze gaps
- [ ] Pick one module from Phase 2 to test

**Short Term (This Week)**:
- [ ] Complete bull/bear researcher tests
- [ ] Add risk manager tests
- [ ] Reach 20% coverage milestone

**Medium Term (Next 2 Weeks)**:
- [ ] Complete core execution tests
- [ ] Add integration tests for Alpaca API
- [ ] Reach 35% coverage milestone

**Long Term (Month)**:
- [ ] Full automation pipeline testing
- [ ] Performance benchmarks
- [ ] CI/CD integration
- [ ] Reach 50% coverage target

---

**Last Updated**: October 7, 2025
**Next Review**: Week of October 14, 2025
**Owner**: Trading System Development Team
