# Phase 2 Performance Testing - Quick Reference

## Commands

### Run All Tests

```bash
# Complete benchmark suite
python benchmarks/phase2_benchmarks.py

# Performance tests only
pytest tests/performance/test_phase2_performance.py -v -s

# Integration tests only
pytest tests/integration/test_full_pipeline.py -v -s

# Everything
pytest tests/performance/ tests/integration/ -v
```

### Generate Reports

```bash
# Latest results
python scripts/utilities/generate_performance_report.py

# Specific file
python scripts/utilities/generate_performance_report.py --benchmark-file benchmarks/reports/performance_report_20251023.json

# Compare two runs
python scripts/utilities/generate_performance_report.py --compare before.json after.json
```

### Run Specific Tests

```bash
# Debate performance
pytest tests/performance/test_phase2_performance.py::TestDebateMechanismPerformance -v

# Alt data performance
pytest tests/performance/test_phase2_performance.py::TestAlternativeDataPerformance -v

# Memory tests
pytest tests/performance/test_phase2_performance.py::TestMemoryUsage -v

# Concurrent processing
pytest tests/performance/test_phase2_performance.py::TestConcurrentProcessing -v
```

## Performance Requirements

| Component | Target | Command to Test |
|-----------|--------|-----------------|
| Debate (1 ticker) | <30s | `pytest tests/performance/ -k debate_single_ticker` |
| Alt Data (20 tickers) | <60s | `pytest tests/performance/ -k alt_data_20_tickers` |
| Full Pipeline (15 tickers) | <5min | `pytest tests/performance/ -k morning_report` |
| Memory Usage | <1GB | `pytest tests/performance/ -k memory_under_1gb` |

## Quick Checks

### Is Performance Acceptable?

```bash
# Run quick check
pytest tests/performance/test_phase2_performance.py::TestDebateMechanismPerformance::test_debate_single_ticker_under_30_seconds -v

# Look for:
# ✓ PASSED = Good
# ✗ FAILED = Performance issue
```

### Compare Before/After Changes

```bash
# Before changes
python benchmarks/phase2_benchmarks.py
cp benchmarks/reports/performance_report_*.json before.json

# Make changes

# After changes
python benchmarks/phase2_benchmarks.py
cp benchmarks/reports/performance_report_*.json after.json

# Compare
python scripts/utilities/generate_performance_report.py --compare before.json after.json
```

### Check for Memory Leaks

```bash
pytest tests/performance/test_phase2_performance.py::TestMemoryUsage::test_no_memory_leaks -v -s
```

### Check for Race Conditions

```bash
pytest tests/integration/test_full_pipeline.py::TestConsistencyReproducibility::test_results_stability_under_load -v
```

## Expected Results

### Benchmark 1: Debate vs Voting

```
Weighted Voting: ~0.5s
Debate Mechanism: ~15-25s
Quality improvement: +21%
Winner: Debate (quality justifies time)
```

### Benchmark 2: With/Without Alt Data

```
Without Alt Data: ~2-3s
With Alt Data: ~5-8s
Quality improvement: +20%
Time overhead: ~3-5s (acceptable)
```

### Benchmark 3: Sequential vs Concurrent

```
Sequential (10 tickers): ~30-40s
Concurrent (10 tickers): ~8-12s
Speedup: 3-4x
Winner: Concurrent
```

## Troubleshooting

### Debate Too Slow (>25s)

```yaml
# config.yaml
phase2:
  debate_timeout_seconds: 45  # Increase timeout
  debate_min_confidence: 0.60  # Require higher confidence to trigger
```

### Alt Data Too Slow (>10s overhead)

1. Check caching: `pytest tests/performance/ -k caching_performance`
2. Enable concurrent fetching
3. Reduce lookback periods in config.yaml

### High Memory Usage (>500MB)

1. Run memory profiler: `python -m memory_profiler benchmarks/phase2_benchmarks.py`
2. Check for leaks: `pytest tests/performance/ -k memory_leaks`
3. Clear caches more aggressively

### Test Failures

```bash
# See detailed error
pytest tests/performance/test_phase2_performance.py -v -s --tb=long

# Check specific test
pytest tests/performance/test_phase2_performance.py::TestClass::test_name -v -s
```

## Report Locations

```
benchmarks/reports/
├── performance_report_YYYYMMDD_HHMMSS.json  # Raw benchmark data
├── performance_report_YYYYMMDD_HHMMSS.md    # Markdown summary
├── analysis_report_YYYYMMDD_HHMMSS.json     # Detailed analysis
└── analysis_report_YYYYMMDD_HHMMSS.md       # Analysis with insights
```

## Interpretation Guide

### ✅ Good Performance

- All tests pass
- No CRITICAL bottlenecks
- Speedup >2x for concurrent
- Memory <500MB
- Quality improvement >10%

### ⚠️ Needs Attention

- Some tests pass with warnings
- HIGH severity bottlenecks
- Speedup 1.5-2x
- Memory 500-800MB
- Quality improvement 5-10%

### 🔴 Critical Issues

- Test failures
- CRITICAL bottlenecks
- Speedup <1.5x
- Memory >1GB
- Performance regressions

## CI/CD Integration

```bash
# Add to CI pipeline
pytest tests/performance/test_phase2_performance.py --maxfail=1
pytest tests/integration/test_full_pipeline.py --maxfail=1

# Run benchmarks weekly
python benchmarks/phase2_benchmarks.py
python scripts/utilities/generate_performance_report.py

# Alert if CRITICAL bottlenecks detected
```

## Common Issues

### Issue: "Debate timeout"

**Solution:**
```yaml
# config.yaml
phase2:
  debate_timeout_seconds: 45
```

### Issue: "Rate limit exceeded"

**Solution:** Add delays between API calls or use caching

### Issue: "Memory leak detected"

**Solution:** Clear caches, check for circular references

### Issue: "Race condition in concurrent tests"

**Solution:** Use proper async locks, avoid shared mutable state

## Best Practices

1. ✅ Run benchmarks before committing major changes
2. ✅ Check reports for optimization opportunities
3. ✅ Set up weekly automated benchmarks
4. ✅ Track performance trends over time
5. ✅ Address CRITICAL bottlenecks immediately

## Need Help?

1. Check full README: `benchmarks/README.md`
2. Review latest analysis report
3. Run tests with `-v -s` for verbose output
4. Profile with memory_profiler or cProfile
5. Open GitHub issue with benchmark results

---

**Quick Start:** `python benchmarks/phase2_benchmarks.py && python scripts/utilities/generate_performance_report.py`
