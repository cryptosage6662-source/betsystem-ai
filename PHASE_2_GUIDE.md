# Phase 2: Strategy Implementation & Paper Trading Engine

**Status:** Complete ✅  
**Date:** February 11, 2026  
**Version:** 1.0

---

## Overview

Phase 2 builds on the Phase 1 API module to create a complete **paper trading system** for Polymarket crypto prediction markets. It includes:

1. **Mean-Reversion Strategy** - Automated trading signals
2. **Paper Trading Engine** - Position management and trade execution
3. **Circuit Breaker Logic** - Risk management after consecutive losses
4. **Trade Logging** - Historical tracking with P&L calculations
5. **Performance Metrics** - Win rate, total P&L, and trading statistics

**Key Feature:** The system is **cron-ready**, **idempotent**, and **JSON-based** for easy integration into production systems.

---

## Deliverables

### 1. `polymarket_strategy.py` - Strategy Signal Generation

**Purpose:** Generates trading signals based on mean-reversion logic.

**Key Classes:**

- `Signal` (Enum) - Trading signal types: BUY, SELL, HOLD, NONE
- `StrategySignal` (Dataclass) - Represents a single trading signal
- `MeanReversionStrategy` - Main strategy class

**Core Logic:**

```python
# Mean-Reversion on "Up" Crypto Markets
class MeanReversionStrategy:
    BUY_THRESHOLD = 0.40      # Buy YES when price < 40%
    SELL_THRESHOLD = 0.60     # Sell YES when price > 60%
    MAX_POSITION_SIZE = 10.0  # Max $10 per trade
```

**How it Works:**

1. **Filters markets** for crypto "Up" predictions (BTC/ETH/SOL price direction)
2. **Detects uptrends** by checking for positive recent momentum
3. **Generates BUY signals** when:
   - YES price < 0.40 (undervalued, likely to revert up)
   - Sufficient volume (> $1000)
   - Sufficient liquidity (> $100)
   - Not expiring soon (≥ 1 day)
4. **Generates SELL signals** when:
   - YES price > 0.60 (take profits)
   - OR position is expiring

**Methods:**

```python
# Main entry point
signals = strategy.generate_signals(markets: List[Dict]) -> List[StrategySignal]

# Single market
signal = strategy.generate_signal(market: Dict) -> Optional[StrategySignal]

# Utility methods
strategy.is_uptrend_market(market) -> bool
strategy.calculate_momentum(market_id, price) -> float
strategy.evaluate_entry(market) -> Tuple[bool, float, str]
strategy.evaluate_exit(market, entry_price) -> Tuple[bool, float, str]
```

**Example Usage:**

```python
from polymarket_strategy import MeanReversionStrategy

strategy = MeanReversionStrategy()
signals = strategy.generate_signals(markets)

for signal in signals:
    print(f"{signal.signal.value}: {signal.question}")
    print(f"  Price: {signal.current_price:.2%}")
    print(f"  Confidence: {signal.confidence:.0%}")
```

---

### 2. `paper_trading.py` - Paper Trading Engine

**Purpose:** Executes trades, tracks positions, calculates P&L, and manages risk.

**Key Classes:**

- `TradeStatus` (Enum) - Trade status: OPEN, CLOSED
- `Position` (Dataclass) - Open position
- `ClosedTrade` (Dataclass) - Completed trade with P&L
- `TradeMetrics` (Dataclass) - Performance metrics
- `PaperTradingEngine` - Main trading engine

**Core Functionality:**

1. **Position Management**
   - Track open positions in `positions.json`
   - Support multiple concurrent positions
   - Prevent duplicate positions in same market
   - Idempotent (safe to run multiple times)

2. **Trade Execution**
   - Execute trades at current market price
   - Enter on BUY signals
   - Exit on SELL signals or when expiring

3. **P&L Calculation**
   - Unrealized P&L for open positions
   - Realized P&L for closed trades
   - P&L percentage calculation

4. **Circuit Breaker**
   - Track consecutive losses
   - Stop trading after 3 consecutive losses
   - Prevent new positions during circuit breaker
   - Reset on winning trade

5. **State Management**
   - Auto-load existing positions on init
   - Auto-save after every trade
   - Persist state to JSON files

**Data Files:**

**positions.json** - Open positions
```json
{
  "timestamp": "2026-02-11T22:32:00+00:00",
  "count": 2,
  "positions": [
    {
      "position_id": "pos_12345_2026-02-11T22:32:00",
      "market_id": "67890",
      "question": "Will BTC break $50k?",
      "entry_time": "2026-02-11T22:30:00+00:00",
      "entry_price": 0.35,
      "quantity": 10.0,
      "signal": "price < 0.40 | volume sufficient"
    }
  ]
}
```

**trades.json** - Historical trades
```json
{
  "timestamp": "2026-02-11T22:32:00+00:00",
  "count": 5,
  "trades": [
    {
      "trade_id": "trade_12345_2026-02-11T22:30:00",
      "market_id": "67890",
      "question": "Will BTC break $50k?",
      "entry_time": "2026-02-11T22:30:00+00:00",
      "entry_price": 0.35,
      "exit_time": "2026-02-11T22:31:00+00:00",
      "exit_price": 0.65,
      "quantity": 10.0,
      "p_l": 30.0,
      "p_l_percent": 85.7,
      "signal": "price < 0.40",
      "exit_reason": "Profit target reached"
    }
  ],
  "metrics": {
    "total_trades": 5,
    "winning_trades": 3,
    "losing_trades": 2,
    "total_p_l": 45.50,
    "win_rate": 60.0,
    "consecutive_wins": 1,
    "consecutive_losses": 0,
    "max_consecutive_losses": 2,
    "avg_win": 22.50,
    "avg_loss": -8.25
  },
  "circuit_breaker_active": false
}
```

**Methods:**

```python
# Position management
engine.open_position(signal: StrategySignal) -> Optional[Position]
engine.close_position(position_id: str, exit_price: float, exit_reason: str) -> Optional[ClosedTrade]

# Trade processing
engine.process_signals(signals: List[StrategySignal], market_data: Dict) -> None

# P&L
engine.calculate_unrealized_pnl(market_id: str, current_price: float) -> Tuple[float, float]

# Circuit breaker
engine.reset_circuit_breaker(winning_trade: bool = False) -> None

# Portfolio info
engine.get_portfolio_summary() -> Dict
engine.display_summary() -> None
```

**Example Usage:**

```python
from paper_trading import PaperTradingEngine

engine = PaperTradingEngine()

# Process strategy signals
engine.process_signals(signals, market_data)

# Check status
summary = engine.get_portfolio_summary()
print(f"Open positions: {summary['open_positions']}")
print(f"Total P&L: ${summary['total_pnl']:.2f}")
print(f"Win rate: {summary['win_rate']:.1f}%")
```

---

### 3. `test_phase2.py` - Comprehensive Test Suite

**Purpose:** Demonstrates all Phase 2 features with sample data.

**Tests:**

1. **Signal Generation** - Verify strategy generates signals
2. **Position Management** - Create, track, save positions
3. **P&L Calculation** - Calculate and verify profits/losses
4. **Circuit Breaker** - Test 3-loss stop mechanism
5. **Metrics Calculation** - Verify performance stats
6. **Idempotency** - Safe to run multiple times
7. **JSON Export** - Verify file structure

**Run Tests:**

```bash
python3 test_phase2.py
```

**Expected Output:**

```
======================================================================
PHASE 2 TEST SUITE: STRATEGY & PAPER TRADING ENGINE
======================================================================

======================================================================
TEST 1: STRATEGY SIGNAL GENERATION
======================================================================

✅ Generated 8 signals from 53 markets
   - BUY signals: 5
   - SELL signals: 3

   Sample BUY signal:
   Market: Will BTC go above $50k by March?
   Price: 35.00%
   Confidence: 80%
   Reason: price 0.35 below threshold 0.40 | volume sufficient

[... more tests ...]

======================================================================
TEST SUMMARY
======================================================================
1. Signal Generation: ✅ PASS
2. Position Management: ✅ PASS
3. P&L Calculation: ✅ PASS
4. Circuit Breaker: ✅ PASS
5. Metrics Calculation: ✅ PASS
6. Idempotency: ✅ PASS
7. JSON Export: ✅ PASS

Total: 7/7 tests passed
```

---

### 4. `positions.json` - Current Open Positions

**Auto-managed** by the trading engine. Stores all currently open positions with entry prices and sizes.

**Update:** Every time a position is opened or closed.

---

### 5. `trades.json` - Historical Trade Log

**Auto-managed** by the trading engine. Stores all closed trades with P&L and performance metrics.

**Update:** Every time a trade closes.

---

## How to Use

### Quick Start

1. **Ensure Phase 1 is complete** - Must have `polymarket_api.py` and `sample_markets.json`

2. **Run the test suite to verify everything works:**
   ```bash
   python3 test_phase2.py
   ```

3. **Use in your own code:**
   ```python
   from polymarket_strategy import MeanReversionStrategy
   from paper_trading import PaperTradingEngine
   from polymarket_api import PolymarketAPI

   # 1. Fetch live markets
   api = PolymarketAPI()
   markets = api.discover_crypto_markets(limit=1000)

   # 2. Generate signals
   strategy = MeanReversionStrategy()
   signals = strategy.generate_signals(markets)

   # 3. Execute trades
   engine = PaperTradingEngine()
   market_data = {m["market_id"]: m for m in markets}
   engine.process_signals(signals, market_data)

   # 4. Check results
   engine.display_summary()
   ```

### Running as a Cron Job

The system is designed to be called once per market scan:

```bash
# Run every hour to process new signals
0 * * * * cd /path/to/polymarket && python3 -c "
from polymarket_api import PolymarketAPI
from polymarket_strategy import MeanReversionStrategy
from paper_trading import PaperTradingEngine

api = PolymarketAPI()
markets = api.discover_crypto_markets()
strategy = MeanReversionStrategy()
signals = strategy.generate_signals(markets)
engine = PaperTradingEngine()
market_data = {m['market_id']: m for m in markets}
engine.process_signals(signals, market_data)
"
```

### Monitoring Trading Activity

**Check positions:**
```bash
cat positions.json | python3 -m json.tool
```

**Check trade history:**
```bash
cat trades.json | python3 -m json.tool | head -50
```

**Get summary:**
```python
from paper_trading import PaperTradingEngine
engine = PaperTradingEngine()
engine.display_summary()
```

---

## Configuration

### Strategy Parameters

Edit `polymarket_strategy.py`:

```python
class MeanReversionStrategy:
    BUY_THRESHOLD = 0.40          # Buy when YES price below this
    SELL_THRESHOLD = 0.60         # Sell when YES price above this
    MAX_POSITION_SIZE = 10.0      # Max dollars per trade
    MIN_VOLUME_FOR_TRADE = 1000   # Min volume
    MIN_LIQUIDITY = 100           # Min liquidity
```

### Circuit Breaker Parameters

Edit `paper_trading.py`:

```python
# Current: Stop after 3 consecutive losses
# Line: if self.metrics.consecutive_losses >= 3:
```

---

## Architecture

```
Polymarket Paper Trading System
├── Phase 1: API Module
│   └── polymarket_api.py (Phase 1 - already complete)
│
├── Phase 2: Strategy & Trading (THIS PHASE)
│   ├── polymarket_strategy.py
│   │   ├── Signal generation
│   │   ├── Momentum detection
│   │   └── Entry/exit logic
│   │
│   ├── paper_trading.py
│   │   ├── Position management
│   │   ├── P&L calculation
│   │   ├── Circuit breaker
│   │   └── State persistence
│   │
│   ├── test_phase2.py
│   │   └── 7 comprehensive tests
│   │
│   └── State Files
│       ├── positions.json (open positions)
│       └── trades.json (closed trades + metrics)
│
└── Future Phases
    ├── Phase 3: Backtesting
    ├── Phase 4: Live Trading
    └── Phase 5-8: Production System
```

---

## Key Features

### ✅ Cron-Ready
- Single function call executes one market scan
- No interactive mode or waiting required
- Auto-saves all state to JSON files

### ✅ Idempotent
- Safe to run multiple times
- Won't create duplicate trades
- Uses position_id to prevent re-entry

### ✅ JSON-Based State
- All data in human-readable JSON files
- Easy to inspect and debug
- Can be integrated with other systems

### ✅ Paper Trading Only
- No real money spent
- No actual orders placed
- Safe for testing and development

### ✅ Production-Ready
- Full error handling
- State recovery
- Circuit breaker for risk management
- Comprehensive logging

---

## Example Trading Session

```bash
$ python3 test_phase2.py

======================================================================
STRATEGY SIGNALS - 5 signal(s) generated
======================================================================

📈 BUY SIGNALS (3):
  • Will BTC break $50k by March 1st?
    Price: 35.00% (threshold: 40.00%)
    Size: $10.00 | Confidence: 80%
    Reason: price 0.35 below threshold 0.40 | volume sufficient

  • Will ETH be above $2000?
    Price: 38.00% (threshold: 40.00%)
    Size: $10.00 | Confidence: 75%

  • Will SOL reach $100?
    Price: 32.00% (threshold: 40.00%)
    Size: $10.00 | Confidence: 70%

======================================================================
PROCESSING SIGNALS - 5 signal(s) to process
======================================================================

✅ BUY: Position opened in market_12345
   Entry Price: 35.00% | Size: $10.00

✅ BUY: Position opened in market_23456
   Entry Price: 38.00% | Size: $10.00

✅ BUY: Position opened in market_34567
   Entry Price: 32.00% | Size: $10.00

📉 SELL: Position closed in market_12345
   Entry: 35.00% | Exit: 65.00%
   P&L: $30.00 (+85.7%) | Reason: Profit target reached

======================================================================
PORTFOLIO SUMMARY
======================================================================
Open Positions: 2
Closed Trades: 1
Total P&L: $30.00
Win Rate: 100.0%
Winning Trades: 1 | Losing Trades: 0
Consecutive Losses: 0/3
Circuit Breaker: 🟢 OFF
======================================================================
```

---

## Performance Metrics

The system tracks:

- **Total P&L** - Sum of all realized profits/losses
- **Win Rate** - Percentage of winning trades
- **Consecutive Losses** - Current losing streak (triggers circuit breaker at 3)
- **Average Win/Loss** - Mean profit/loss per trade
- **Max Consecutive Losses** - Worst losing streak encountered

Example output from `trades.json`:

```json
"metrics": {
  "total_trades": 15,
  "winning_trades": 9,
  "losing_trades": 6,
  "total_p_l": 145.50,
  "win_rate": 60.0,
  "consecutive_wins": 2,
  "consecutive_losses": 0,
  "max_consecutive_losses": 3,
  "avg_win": 22.15,
  "avg_loss": -12.50
}
```

---

## Circuit Breaker Mechanics

**Purpose:** Stop trading after losing streak to prevent emotional trading and limit drawdown.

**How It Works:**

1. **Normal Trading**: System processes BUY/SELL signals normally
2. **After Loss**: Consecutive loss counter increments
3. **After 3 Losses**: 🔴 Circuit breaker activates
   - No new positions can be opened
   - Existing positions remain open
   - System waits for a winning trade
4. **After Win**: 🟢 Circuit breaker resets
   - Trading resumes normally
   - Counter goes to 0

**Example Scenario:**

```
Trade 1: LOSS (-$5)     → Consecutive Losses: 1/3
Trade 2: LOSS (-$3)     → Consecutive Losses: 2/3
Trade 3: LOSS (-$7)     → Consecutive Losses: 3/3 → 🔴 CIRCUIT BREAKER ACTIVE
Trade 4 BUY SIGNAL:     → Rejected (circuit breaker active)
Trade 5: SELL (WIN +$10) → Consecutive Losses: 0 → 🟢 CIRCUIT BREAKER RESET
Trade 6 BUY SIGNAL:     → Accepted (trading resumed)
```

---

## Troubleshooting

### No signals generated?
- Check `sample_markets.json` exists and has recent data
- Ensure markets have "Up" direction keywords (BTC up, ETH higher, etc.)
- Verify YES prices are between 0.0 and 1.0
- Check market volume > $1000 and liquidity > $100

### Positions not opening?
- Check circuit breaker isn't active
- Verify signal.signal == Signal.BUY
- Check no duplicate position in same market
- Ensure position_size is reasonable ($10 default)

### P&L looks wrong?
- Verify entry_price and exit_price are between 0.0-1.0
- Check quantity matches position_size
- Ensure P&L = (exit_price - entry_price) * quantity * 100

### Files not saving?
- Check file permissions
- Verify JSON is valid
- Ensure working directory is correct

---

## Next Steps

### Phase 3: Backtesting
- Historical market data
- Performance simulation
- Risk metrics

### Phase 4: Live Trading
- Real Polymarket API integration
- Order submission
- Risk management

### Phase 5+: Production System
- Monitoring dashboard
- Email/Slack alerts
- Advanced risk controls

---

## Summary

**Phase 2 complete!** You now have:

✅ Mean-reversion strategy that generates trading signals  
✅ Paper trading engine that executes simulated trades  
✅ Circuit breaker that stops trading after 3 consecutive losses  
✅ Comprehensive trade logging with P&L tracking  
✅ Performance metrics (win rate, total P&L, etc.)  
✅ 7-test suite verifying all functionality  
✅ JSON-based state persistence  
✅ Cron-ready for automated trading  

**Ready for:** Phase 3 (Backtesting) or Phase 4 (Live Trading)

---

## Files

- `polymarket_strategy.py` - Strategy module
- `paper_trading.py` - Trading engine
- `test_phase2.py` - Test suite
- `positions.json` - Open positions (auto-generated)
- `trades.json` - Trade history (auto-generated)
- `signals.json` - Latest signals (auto-generated)
- `PHASE_2_GUIDE.md` - This documentation

---

**Version:** 1.0  
**Last Updated:** February 11, 2026  
**Status:** Production Ready ✅
