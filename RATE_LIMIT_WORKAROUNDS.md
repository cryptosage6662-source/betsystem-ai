# Rate Limit Workarounds - Testing Guide

## Problem
OpenClaw/Claude API has rate limits (~50K input tokens/min). Large backtesting runs can hit these limits when spawning sub-agents.

## Solutions

### ✅ Solution 1: Run Heavy Computation Locally (RECOMMENDED)
**Best for:** Backtesting, optimization, large simulations

Instead of `sessions_spawn()`:
```python
# ❌ DON'T DO THIS (hits rate limits)
sessions_spawn(task="Run 72 backtests...")

# ✅ DO THIS (local execution)
exec(command="cd workspace && python3 backtest_script.py")
```

**Why it works:**
- No sub-agent creation = no API calls for agent spin-up
- Direct execution on the sandbox
- Full parallelization available
- No token usage for prompt/response overhead

### ✅ Solution 2: Batch Processing with Sleep
**Best for:** Multiple sequential tests

```bash
# Run in batches with delays
python3 test1.py && sleep 5 && python3 test2.py && sleep 5 && python3 test3.py
```

This prevents rate limit spikes by spacing out API calls.

### ✅ Solution 3: Inline Scripts with `exec`
**Best for:** Anything up to ~500 lines of Python

```python
exec(command="""cd /workspace && python3 << 'EOF'
# Your entire test script here
# Can be hundreds of lines
# Runs locally without spawning
EOF
""", timeout=300)
```

**Advantages:**
- No agent spawning
- No rate limit concerns
- Can run for 5+ minutes
- Full access to workspace files

### ✅ Solution 4: Split into Smaller Tasks
**Best for:** Very large operations (1000+ backtests)

Instead of 1000 tests in one run:
```
Day 1: Run 100 tests (configs 1-20)
Day 2: Run 100 tests (configs 21-40)
Day 3: Run 100 tests (configs 41-60)
...
```

Or split by bankroll/scenario:
```
Task 1: All scenarios for $100 (6 configs × 4 markets = 24 tests)
Task 2: All scenarios for $1,000 (24 tests)
Task 3: All scenarios for $10,000 (24 tests)
```

### ✅ Solution 5: Use Pre-Computed Data
**Best for:** Testing different strategies on same data

```python
# Generate data once
python3 << 'EOF'
from backtest_simulator import HistoricalDataSimulator, MarketScenario
for scenario in MarketScenario:
    sim = HistoricalDataSimulator(scenario=scenario)
    sim.generate_price_series()
    sim.export_to_json(f"data_{scenario.value}.json")
EOF

# Then test 100 different strategies on this pre-generated data
# No need to regenerate data each time
```

### ✅ Solution 6: Cache Results
**Best for:** Testing variations

```python
# First run: Full backtest
results = run_full_backtest()
save_to_json("backtest_results.json", results)

# Subsequent runs: Analyze existing results without re-running
metrics = analyze_cached_results("backtest_results.json")
```

---

## Rate Limit Detection & Prevention

### Signs You're About to Hit Limits
- Scripts suddenly fail with 429 errors
- Agent spawn requests hang
- API calls time out unexpectedly

### Quick Prevention Checklist
- [ ] Using `exec()` instead of `sessions_spawn()` for heavy work?
- [ ] Running backtests locally (inline Python)?
- [ ] Adding sleep(5) between API-heavy operations?
- [ ] Using cached results when possible?
- [ ] Batching similar work into single requests?

---

## Our Successful Pattern

**What worked in our 72-backtest run:**

```python
# ✅ SUCCESSFUL APPROACH
exec(command="""
cd /data/.openclaw/workspace && python3 << 'EOF'
# Entire 72-backtest suite in one inline script
# No sub-agents, no rate limits, completes in 2-3 minutes
EOF
""", timeout=180)
```

**Why this succeeded:**
1. Single `exec()` call = 1 API interaction
2. All 72 backtests run in parallel/sequentially locally
3. No agent spawning overhead
4. Result: Complete backtest suite in ~3 minutes

---

## Testing Scenarios & Recommended Approach

| Scenario | Tests | Recommended Method | Est. Time |
|----------|-------|-------------------|-----------|
| Single strategy test | 1 | exec() inline | 30s |
| Position sizing opt | 72 | exec() inline | 3 min |
| Multi-strategy comp | 200 | Batch with splits | 15 min |
| Full system test | 1000+ | Day-by-day | 1 hour spread |

---

## When to Use Sub-Agents (sessions_spawn)

**Only use `sessions_spawn()` for:**
- Tasks that need different models/reasoning
- Results that need to come back as separate messages
- Long-running tasks with progress updates
- Research that benefits from parallel exploration

**Don't use for:**
- Backtesting (too many iterations)
- Data generation (better local)
- Bulk computations (waste of spawns)

---

## Code Template: Heavy Testing Without Limits

```python
#!/usr/bin/env python3
"""
Template for large-scale testing without rate limit concerns
"""

import json
import os

def main():
    # Configuration
    configs = [...]  # 100 configs? 1000? No problem
    
    results = {}
    
    # Process all configs locally
    for i, config in enumerate(configs):
        print(f"Processing {i+1}/{len(configs)}...")
        
        result = expensive_computation(config)
        results[config_name] = result
        
        # Optional: Save checkpoint every 50 iterations
        if (i + 1) % 50 == 0:
            with open(f"checkpoint_{i+1}.json", "w") as f:
                json.dump(results, f)
    
    # Save final results
    with open("final_results.json", "w") as f:
        json.dump(results, f)
    
    print("✅ Complete!")

if __name__ == "__main__":
    main()
```

Then call from main session:
```python
exec(command="cd /workspace && python3 test_suite.py", timeout=600)
```

---

## Summary

**For testing purposes, always:**

1. ✅ Use `exec()` for heavy computational work
2. ✅ Keep scripts inline when possible
3. ✅ Cache results to avoid recomputation
4. ✅ Add sleep() between API calls
5. ✅ Batch similar operations together
6. ❌ Avoid `sessions_spawn()` for testing
7. ❌ Don't make 100s of small API calls in a loop

**Result:** Unlimited testing without hitting rate limits!
