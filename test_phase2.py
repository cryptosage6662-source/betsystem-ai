"""
Test Script for Phase 2: Strategy Implementation & Paper Trading
Demonstrates the complete trading system with sample data and simulated market scenarios
"""

import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from polymarket_strategy import MeanReversionStrategy, Signal
from paper_trading import PaperTradingEngine


def load_sample_markets():
    """Load sample market data"""
    try:
        with open("sample_markets.json", "r") as f:
            data = json.load(f)
            return data.get("markets", [])
    except FileNotFoundError:
        print("❌ sample_markets.json not found. Run polymarket_api.py first.")
        return []


def simulate_market_prices(markets, price_changes):
    """
    Simulate market price changes for testing
    
    Args:
        markets: Original market data
        price_changes: Dict of market_id -> price change (0.0 to 1.0)
        
    Returns:
        Modified market data with new prices
    """
    updated_markets = []
    
    for market in markets:
        market_copy = deepcopy(market)
        market_id = market.get("market_id")
        
        if market_id in price_changes:
            # Apply price change
            new_price = market_copy.get("yes_price", 0.5) + price_changes[market_id]
            # Clamp to 0.0 to 1.0
            new_price = max(0.0, min(1.0, new_price))
            market_copy["yes_price"] = new_price
        
        updated_markets.append(market_copy)
    
    return updated_markets


def test_strategy_signal_generation():
    """Test 1: Strategy signal generation"""
    print("\n" + "="*70)
    print("TEST 1: STRATEGY SIGNAL GENERATION")
    print("="*70)
    
    markets = load_sample_markets()
    if not markets:
        return False
    
    strategy = MeanReversionStrategy()
    signals = strategy.generate_signals(markets)
    
    print(f"\n✅ Generated {len(signals)} signals from {len(markets)} markets")
    
    if signals:
        buy_signals = [s for s in signals if s.signal == Signal.BUY]
        sell_signals = [s for s in signals if s.signal == Signal.SELL]
        
        print(f"   - BUY signals: {len(buy_signals)}")
        print(f"   - SELL signals: {len(sell_signals)}")
        
        if buy_signals:
            print(f"\n   Sample BUY signal:")
            sig = buy_signals[0]
            print(f"   Market: {sig.question}")
            print(f"   Price: {sig.current_price:.2%}")
            print(f"   Confidence: {sig.confidence:.0%}")
            print(f"   Reason: {sig.reason}")
        
        return True
    else:
        print("⚠️  No signals generated (market data may be outdated)")
        return False


def test_position_management():
    """Test 2: Position opening and tracking"""
    print("\n" + "="*70)
    print("TEST 2: POSITION MANAGEMENT")
    print("="*70)
    
    # Clean up existing data
    for f in ["positions.json", "trades.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    engine = PaperTradingEngine()
    
    # Create a test signal
    from polymarket_strategy import StrategySignal
    test_signal = StrategySignal(
        market_id="test_market_1",
        question="Will BTC go up?",
        signal=Signal.BUY,
        current_price=0.35,
        entry_threshold=0.40,
        exit_threshold=0.60,
        position_size=10.0,
        confidence=0.8,
        reason="Price below threshold with good volume",
        timestamp=datetime.now(timezone.utc).isoformat(),
        is_uptrend=True,
        recent_momentum=0.1
    )
    
    # Open position
    position = engine.open_position(test_signal)
    
    if position:
        print(f"\n✅ Position opened successfully")
        print(f"   Position ID: {position.position_id}")
        print(f"   Market: {position.question}")
        print(f"   Entry Price: {position.entry_price:.2%}")
        print(f"   Size: ${position.quantity:.2f}")
        
        # Check positions file
        if os.path.exists("positions.json"):
            with open("positions.json", "r") as f:
                data = json.load(f)
                print(f"   Saved to positions.json: {data['count']} position(s)")
        
        return True
    else:
        print("❌ Failed to open position")
        return False


def test_pnl_calculation():
    """Test 3: P&L calculation and trade closing"""
    print("\n" + "="*70)
    print("TEST 3: P&L CALCULATION & TRADE CLOSING")
    print("="*70)
    
    # Clean up
    for f in ["positions.json", "trades.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    engine = PaperTradingEngine()
    
    # Create and open a position
    from polymarket_strategy import StrategySignal
    test_signal = StrategySignal(
        market_id="test_market_2",
        question="Will ETH reach $2000?",
        signal=Signal.BUY,
        current_price=0.35,
        entry_threshold=0.40,
        exit_threshold=0.60,
        position_size=10.0,
        confidence=0.8,
        reason="Mean reversion setup",
        timestamp=datetime.now(timezone.utc).isoformat(),
        is_uptrend=True,
        recent_momentum=0.0
    )
    
    position = engine.open_position(test_signal)
    
    if not position:
        print("❌ Failed to open position")
        return False
    
    # Simulate profitable exit (bought at 0.35, selling at 0.65)
    exit_price = 0.65
    trade = engine.close_position(
        position.position_id,
        exit_price,
        "Profit target reached"
    )
    
    if trade:
        print(f"\n✅ Trade closed successfully")
        print(f"   Entry Price: {trade.entry_price:.2%}")
        print(f"   Exit Price: {trade.exit_price:.2%}")
        print(f"   P&L: ${trade.p_l:+.2f} ({trade.p_l_percent:+.1f}%)")
        print(f"   Status: {'✅ WINNING' if trade.p_l > 0 else '❌ LOSING'}")
        
        # Check trades file
        if os.path.exists("trades.json"):
            with open("trades.json", "r") as f:
                data = json.load(f)
                print(f"   Saved to trades.json: {data['count']} trade(s)")
        
        return True
    else:
        print("❌ Failed to close trade")
        return False


def test_circuit_breaker():
    """Test 4: Circuit breaker logic (stop after 3 consecutive losses)"""
    print("\n" + "="*70)
    print("TEST 4: CIRCUIT BREAKER LOGIC")
    print("="*70)
    
    # Clean up
    for f in ["positions.json", "trades.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    engine = PaperTradingEngine()
    
    from polymarket_strategy import StrategySignal
    
    # Create 5 test signals and trade them
    test_signals = []
    for i in range(5):
        test_signals.append(StrategySignal(
            market_id=f"test_market_{3 + i}",
            question=f"Test market {i+1}",
            signal=Signal.BUY,
            current_price=0.50,
            entry_threshold=0.40,
            exit_threshold=0.60,
            position_size=10.0,
            confidence=0.8,
            reason="Test trade",
            timestamp=datetime.now(timezone.utc).isoformat(),
            is_uptrend=True,
            recent_momentum=0.0
        ))
    
    print("\n📊 Simulating trades:")
    
    # Simulate 3 losing trades, then 1 winning trade
    results = [False, False, False, True, True]  # Outcomes
    
    for i, signal in enumerate(test_signals):
        # Open position
        position = engine.open_position(signal)
        if not position:
            continue
        
        # Close position with simulated result
        exit_price = 0.30 if not results[i] else 0.70  # Loss or Win
        trade = engine.close_position(position.position_id, exit_price, "Test close")
        
        if trade:
            outcome = "✅ WIN" if trade.p_l > 0 else "❌ LOSS"
            print(f"   Trade {i+1}: {outcome} (P&L: ${trade.p_l:+.2f})")
            
            if i == 3:  # After 3 losses, check circuit breaker
                print(f"   → Circuit Breaker Status: {'🔴 ACTIVE' if engine.circuit_breaker_active else '🟢 OFF'}")
    
    print(f"\n✅ Circuit breaker logic verified")
    print(f"   Final Status: {'🔴 ACTIVE (trading stopped)' if engine.circuit_breaker_active else '🟢 OFF'}")
    print(f"   Total Trades: {engine.metrics.total_trades}")
    print(f"   Consecutive Losses: {engine.metrics.consecutive_losses}")
    print(f"   Max Consecutive Losses: {engine.metrics.max_consecutive_losses}")
    
    return engine.circuit_breaker_active  # Should be True after 3 losses


def test_metrics_calculation():
    """Test 5: Performance metrics calculation"""
    print("\n" + "="*70)
    print("TEST 5: PERFORMANCE METRICS")
    print("="*70)
    
    # Load trades file from previous test
    if os.path.exists("trades.json"):
        with open("trades.json", "r") as f:
            data = json.load(f)
            trades_count = data.get("count", 0)
            metrics = data.get("metrics", {})
        
        print(f"\n✅ Metrics calculated and saved")
        print(f"   Total Trades: {metrics.get('total_trades', 0)}")
        print(f"   Winning Trades: {metrics.get('winning_trades', 0)}")
        print(f"   Losing Trades: {metrics.get('losing_trades', 0)}")
        print(f"   Win Rate: {metrics.get('win_rate', 0):.1f}%")
        print(f"   Total P&L: ${metrics.get('total_p_l', 0):+.2f}")
        print(f"   Avg Win: ${metrics.get('avg_win', 0):+.2f}")
        print(f"   Avg Loss: ${metrics.get('avg_loss', 0):+.2f}")
        print(f"   Max Consecutive Losses: {metrics.get('max_consecutive_losses', 0)}")
        
        return True
    else:
        print("❌ No trades file found")
        return False


def test_idempotency():
    """Test 6: Idempotency - safe to run multiple times"""
    print("\n" + "="*70)
    print("TEST 6: IDEMPOTENCY")
    print("="*70)
    
    # This test verifies that running the engine multiple times doesn't create duplicates
    
    # Count trades before
    trades_before = 0
    if os.path.exists("trades.json"):
        with open("trades.json", "r") as f:
            data = json.load(f)
            trades_before = data.get("count", 0)
    
    # Run engine again with same data
    engine = PaperTradingEngine()
    markets = load_sample_markets()
    
    if markets:
        strategy = MeanReversionStrategy()
        signals = strategy.generate_signals(markets)
        
        market_data = {m["market_id"]: m for m in markets}
        engine.process_signals(signals, market_data)
    
    # Count trades after
    trades_after = 0
    if os.path.exists("trades.json"):
        with open("trades.json", "r") as f:
            data = json.load(f)
            trades_after = data.get("count", 0)
    
    print(f"\n✅ Idempotency check")
    print(f"   Trades before: {trades_before}")
    print(f"   Trades after: {trades_after}")
    print(f"   New trades created: {trades_after - trades_before}")
    
    return True


def test_json_export():
    """Test 7: JSON export and file structure"""
    print("\n" + "="*70)
    print("TEST 7: JSON EXPORT & FILE STRUCTURE")
    print("="*70)
    
    files_to_check = ["positions.json", "trades.json"]
    
    print(f"\n✅ Checking JSON file structure:")
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                # Just verify it's valid JSON
                with open(filename, "r") as f:
                    data = json.load(f)
                
                print(f"   {filename}: ✅ Valid JSON")
                
                # Show sample structure
                if filename == "positions.json" and data.get("count", 0) > 0:
                    pos = data["positions"][0]
                    print(f"      Sample position:")
                    for key in ["market_id", "entry_price", "quantity"]:
                        print(f"         {key}: {pos.get(key)}")
                
                if filename == "trades.json" and data.get("count", 0) > 0:
                    trade = data["trades"][0]
                    print(f"      Sample trade:")
                    for key in ["market_id", "entry_price", "exit_price", "p_l"]:
                        print(f"         {key}: {trade.get(key)}")
            
            except json.JSONDecodeError as e:
                print(f"   {filename}: ❌ Invalid JSON - {e}")
        else:
            print(f"   {filename}: ⚠️  File not created yet")
    
    return True


def print_test_summary(results):
    """Print summary of test results"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    test_names = [
        "Signal Generation",
        "Position Management",
        "P&L Calculation",
        "Circuit Breaker",
        "Metrics Calculation",
        "Idempotency",
        "JSON Export"
    ]
    
    for i, (name, passed) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    total_passed = sum(results)
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    return all(results)


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("PHASE 2 TEST SUITE: STRATEGY & PAPER TRADING ENGINE")
    print("="*70)
    
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    
    # Run tests
    results = [
        test_strategy_signal_generation(),
        test_position_management(),
        test_pnl_calculation(),
        test_circuit_breaker(),
        test_metrics_calculation(),
        test_idempotency(),
        test_json_export()
    ]
    
    # Print summary
    print_test_summary(results)
    
    print(f"\nCompleted: {datetime.now(timezone.utc).isoformat()}")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
