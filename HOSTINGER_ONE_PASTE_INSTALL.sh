#!/bin/bash
# Polymarket Trading System - One-Paste Installation
# Copy-paste THIS ENTIRE SCRIPT into your Hostinger terminal via Termius on iPhone
# It will deploy everything automatically

set -e

echo "🚀 POLYMARKET TRADING - AUTOMATIC DEPLOYMENT"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create workspace
echo "📁 Creating workspace..."
cd /root
mkdir -p polymarket_trading
cd polymarket_trading

# Initialize data files
echo "📝 Initializing data files..."
python3 << 'INIT'
import json
with open('positions.json', 'w') as f:
    json.dump({'positions': [], 'cash': 100.0, 'equity': 100.0, 'high_water': 100.0, 'max_drawdown': 0.0, 'consecutive_losses': 0}, f, indent=2)
with open('trades.json', 'w') as f:
    json.dump([], f, indent=2)
with open('equity_live.json', 'w') as f:
    json.dump([], f, indent=2)
print('✅ Data files created')
INIT

# Create polymarket_live.py
echo "⚙️  Creating polymarket_live.py..."
cat > polymarket_live.py << 'POLYSCRIPT'
#!/usr/bin/env python3
"""
Phase 4: Live Trading Integration for Polymarket
Real-time 15-minute trading loop with hybrid strategy (mean-reversion + reversal trading)
Paper trading only - no real money at risk
"""

import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
import os

# ==================== CONFIG ====================
API_BASE = "https://gamma-api.polymarket.com"
POSITION_FILE = "/root/polymarket_trading/positions.json"
TRADES_FILE = "/root/polymarket_trading/trades.json"
EQUITY_FILE = "/root/polymarket_trading/equity_live.json"

# Strategy parameters (optimized from Phase 3)
MEAN_REVERSION_CONFIG = {
    "entry_threshold": 0.40,
    "exit_threshold": 0.60,
    "stop_loss": 0.10,
    "profit_target": 0.60,
}

REVERSAL_CONFIG = {
    "momentum_2_threshold": 0.01,
    "momentum_10_threshold": -0.02,
    "stop_loss": 0.08,
    "profit_target": 0.05,
}

BANKROLL = 100.0
POSITION_SIZE = 0.003
MIN_LIQUIDITY = 100.0
CIRCUIT_BREAKER = 3

# ==================== MARKET DISCOVERY ====================
def get_crypto_markets() -> List[Dict]:
    """Fetch UP/DOWN crypto markets from Polymarket"""
    try:
        result = subprocess.run(["curl", "-s", f"{API_BASE}/markets"], capture_output=True, text=True, timeout=10)
        all_markets = json.loads(result.stdout)
        
        crypto_keywords = ["BTC", "ETH", "SOL", "bitcoin", "ethereum", "solana"]
        outcome_keywords = ["up", "down", "higher", "lower", "+", "-"]
        
        crypto_markets = []
        for market in all_markets:
            if market.get("closed") or not market.get("active"):
                continue
            liquidity = float(market.get("liquidityNum", 0))
            if liquidity < MIN_LIQUIDITY:
                continue
            
            question = market.get("question", "").upper()
            is_crypto = any(kw in question for kw in crypto_keywords)
            
            try:
                outcomes = market.get("outcomes", [])
                if isinstance(outcomes, str):
                    outcomes = json.loads(outcomes)
                is_binary = len(outcomes) == 2
            except:
                is_binary = False
            
            outcome_text = " ".join([o.upper() for o in outcomes]) if outcomes else ""
            is_directional = any(kw in outcome_text for kw in outcome_keywords)
            
            if is_crypto and is_binary and is_directional:
                try:
                    prices = market.get("outcomePrices", [])
                    if isinstance(prices, str):
                        prices = json.loads(prices)
                    prices = [float(p) for p in prices]
                    market["outcomes_dict"] = {o: prices[i] for i, o in enumerate(outcomes)}
                    crypto_markets.append(market)
                except:
                    pass
        
        return crypto_markets
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

# ==================== STRATEGY LOGIC ====================
def calculate_momentum(prices: List[float], period: int) -> float:
    if len(prices) < period + 1:
        return 0.0
    return (prices[-1] - prices[-period]) / prices[-period] if prices[-period] != 0 else 0.0

def detect_market_regime(price_history: List[float]) -> str:
    if len(price_history) < 10:
        return "unknown"
    recent = price_history[-10:]
    price_change = (recent[-1] - recent[0]) / recent[0]
    volatility = statistics.stdev(recent)
    if volatility > 0.15:
        return "volatile"
    elif price_change > 0.05:
        return "bull"
    elif price_change < -0.05:
        return "bear"
    else:
        return "sideways"

def should_enter_mean_reversion(yes_price: float, price_history: List[float]) -> Tuple[bool, str]:
    if yes_price < MEAN_REVERSION_CONFIG["entry_threshold"]:
        regime = detect_market_regime(price_history)
        if regime in ["bull", "sideways"]:
            return True, "mean_reversion"
    return False, ""

def should_enter_reversal(price_history: List[float]) -> Tuple[bool, str]:
    if len(price_history) < 10:
        return False, ""
    momentum_2 = calculate_momentum(price_history, 2)
    momentum_10 = calculate_momentum(price_history, 10)
    regime = detect_market_regime(price_history)
    if (momentum_2 > REVERSAL_CONFIG["momentum_2_threshold"] and 
        momentum_10 < REVERSAL_CONFIG["momentum_10_threshold"] and
        regime in ["bear", "volatile"]):
        return True, "reversal"
    return False, ""

def generate_signal(market: Dict, price_history: List[float]) -> Tuple[Optional[str], str]:
    try:
        outcomes_dict = market.get("outcomes_dict", {})
        yes_price = outcomes_dict.get("YES", outcomes_dict.get("Up", 0.5))
        mr_entry, mr_reason = should_enter_mean_reversion(yes_price, price_history)
        if mr_entry:
            return "BUY", mr_reason
        rev_entry, rev_reason = should_enter_reversal(price_history)
        if rev_entry:
            return "BUY", rev_reason
        return "HOLD", ""
    except Exception as e:
        print(f"Error generating signal: {e}")
        return None, ""

# ==================== POSITION TRACKING ====================
def load_positions() -> Dict:
    if os.path.exists(POSITION_FILE):
        try:
            with open(POSITION_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"positions": [], "cash": BANKROLL, "equity": BANKROLL, "high_water": BANKROLL, "max_drawdown": 0.0, "consecutive_losses": 0}

def save_positions(positions: Dict):
    with open(POSITION_FILE, 'w') as f:
        json.dump(positions, f, indent=2)

def load_trades() -> List[Dict]:
    if os.path.exists(TRADES_FILE):
        try:
            with open(TRADES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_trades(trades: List[Dict]):
    with open(TRADES_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

def update_position_pnl(positions: Dict, market: Dict):
    try:
        outcomes_dict = market.get("outcomes_dict", {})
        yes_price = outcomes_dict.get("YES", outcomes_dict.get("Up", 0.5))
        for position in positions["positions"]:
            if position["market_id"] == market.get("id"):
                entry_price = position["entry_price"]
                shares = position["shares"]
                current_value = shares * yes_price
                cost_basis = shares * entry_price
                unrealized_pnl = current_value - cost_basis
                unrealized_pnl_pct = unrealized_pnl / cost_basis if cost_basis != 0 else 0
                position["current_price"] = yes_price
                position["unrealized_pnl"] = unrealized_pnl
                position["unrealized_pnl_pct"] = unrealized_pnl_pct
                positions["equity"] = positions["cash"] + sum(p.get("unrealized_pnl", 0) for p in positions["positions"])
                if positions["equity"] > positions["high_water"]:
                    positions["high_water"] = positions["equity"]
                drawdown = (positions["high_water"] - positions["equity"]) / positions["high_water"]
                if drawdown > positions["max_drawdown"]:
                    positions["max_drawdown"] = drawdown
    except Exception as e:
        print(f"Error updating position P&L: {e}")

def execute_trade(positions: Dict, market: Dict, signal: str, strategy: str) -> bool:
    try:
        if signal != "BUY":
            return False
        if positions["consecutive_losses"] >= CIRCUIT_BREAKER:
            print(f"⛔ Circuit breaker active ({CIRCUIT_BREAKER} losses). Skipping trade.")
            return False
        outcomes_dict = market.get("outcomes_dict", {})
        yes_price = outcomes_dict.get("YES", outcomes_dict.get("Up", 0.5))
        position_amount = positions["cash"] * POSITION_SIZE
        shares = position_amount / yes_price
        if position_amount > positions["cash"]:
            print(f"Insufficient cash: need ${position_amount:.2f}, have ${positions['cash']:.2f}")
            return False
        position = {
            "market_id": market.get("id"),
            "market_question": market.get("question"),
            "entry_time": datetime.now().isoformat(),
            "entry_price": yes_price,
            "shares": shares,
            "amount": position_amount,
            "strategy": strategy,
            "current_price": yes_price,
            "unrealized_pnl": 0.0,
            "unrealized_pnl_pct": 0.0,
        }
        if strategy == "reversal":
            position["stop_loss_pct"] = REVERSAL_CONFIG["stop_loss"]
            position["profit_target_pct"] = REVERSAL_CONFIG["profit_target"]
        else:
            position["stop_loss_pct"] = MEAN_REVERSION_CONFIG["stop_loss"]
            position["profit_target_pct"] = MEAN_REVERSION_CONFIG["profit_target"]
        positions["positions"].append(position)
        positions["cash"] -= position_amount
        trade = {
            "timestamp": datetime.now().isoformat(),
            "type": "BUY",
            "market": market.get("question"),
            "strategy": strategy,
            "price": yes_price,
            "shares": shares,
            "amount": position_amount,
            "position_id": len(positions["positions"]) - 1,
        }
        trades = load_trades()
        trades.append(trade)
        save_trades(trades)
        print(f"✅ BUY: {market.get('question', 'Unknown')[:50]} @ {yes_price:.3f}, {shares:.1f} shares, ${position_amount:.2f} ({strategy})")
        return True
    except Exception as e:
        print(f"Error executing trade: {e}")
        return False

def check_exit_conditions(positions: Dict, market: Dict) -> Tuple[bool, str]:
    try:
        for i, position in enumerate(positions["positions"]):
            if position["market_id"] != market.get("id"):
                continue
            pnl_pct = position["unrealized_pnl_pct"]
            if pnl_pct >= position["profit_target_pct"]:
                return True, f"profit_target ({pnl_pct:.2%})"
            if pnl_pct <= -position["stop_loss_pct"]:
                return True, f"stop_loss ({pnl_pct:.2%})"
        return False, ""
    except Exception as e:
        print(f"Error checking exits: {e}")
        return False, ""

def close_position(positions: Dict, market: Dict, exit_reason: str) -> bool:
    try:
        outcomes_dict = market.get("outcomes_dict", {})
        yes_price = outcomes_dict.get("YES", outcomes_dict.get("Up", 0.5))
        for i, position in enumerate(positions["positions"]):
            if position["market_id"] == market.get("id"):
                realized_pnl = position["unrealized_pnl"]
                sell_amount = position["shares"] * yes_price
                positions["cash"] += sell_amount
                positions["consecutive_losses"] = 0 if realized_pnl > 0 else positions["consecutive_losses"] + 1
                trade = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "SELL",
                    "market": market.get("question"),
                    "price": yes_price,
                    "shares": position["shares"],
                    "amount": sell_amount,
                    "realized_pnl": realized_pnl,
                    "realized_pnl_pct": position["unrealized_pnl_pct"],
                    "exit_reason": exit_reason,
                    "position_id": i,
                }
                trades = load_trades()
                trades.append(trade)
                save_trades(trades)
                pnl_emoji = "✅" if realized_pnl > 0 else "❌"
                print(f"{pnl_emoji} SELL: {market.get('question', 'Unknown')[:50]} @ {yes_price:.3f}, P&L: ${realized_pnl:.2f} ({position['unrealized_pnl_pct']:.2%}) [{exit_reason}]")
                positions["positions"].pop(i)
                return True
        return False
    except Exception as e:
        print(f"Error closing position: {e}")
        return False

# ==================== MAIN TRADING LOOP ====================
def run_trading_cycle(price_history_cache: Dict) -> Dict:
    print(f"\n{'='*60}")
    print(f"Trading Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    positions = load_positions()
    markets = get_crypto_markets()
    
    if not markets:
        print("No crypto markets found. Skipping cycle.")
        return positions
    
    markets = sorted(markets, key=lambda m: m.get("liquidity", 0), reverse=True)[:5]
    
    for market in markets:
        market_id = market.get("id")
        if market_id not in price_history_cache:
            price_history_cache[market_id] = []
        outcomes_dict = market.get("outcomes_dict", {})
        yes_price = outcomes_dict.get("YES", outcomes_dict.get("Up", 0.5))
        price_history_cache[market_id].append(yes_price)
        if len(price_history_cache[market_id]) > 20:
            price_history_cache[market_id] = price_history_cache[market_id][-20:]
        update_position_pnl(positions, market)
        should_exit, exit_reason = check_exit_conditions(positions, market)
        if should_exit:
            close_position(positions, market, exit_reason)
        has_position = any(p["market_id"] == market_id for p in positions["positions"])
        if not has_position:
            signal, strategy = generate_signal(market, price_history_cache[market_id])
            if signal:
                execute_trade(positions, market, signal, strategy)
        print(f"  {market.get('question', 'Unknown')[:50]}: ${yes_price:.3f}")
    
    positions["equity"] = positions["cash"] + sum(p.get("unrealized_pnl", 0) for p in positions["positions"])
    save_positions(positions)
    
    equity_log = {
        "timestamp": datetime.now().isoformat(),
        "cash": positions["cash"],
        "equity": positions["equity"],
        "positions_count": len(positions["positions"]),
        "max_drawdown": positions["max_drawdown"],
    }
    
    if os.path.exists(EQUITY_FILE):
        try:
            with open(EQUITY_FILE, 'r') as f:
                equity_history = json.load(f)
        except:
            equity_history = []
    else:
        equity_history = []
    
    equity_history.append(equity_log)
    with open(EQUITY_FILE, 'w') as f:
        json.dump(equity_history, f, indent=2)
    
    print(f"\nPortfolio: Cash=${positions['cash']:.2f}, Equity=${positions['equity']:.2f}, Max DD={positions['max_drawdown']:.2%}")
    return positions

if __name__ == "__main__":
    print("🚀 Polymarket Live Trading System - Phase 4")
    print(f"Bankroll: ${BANKROLL:.2f}, Position Size: {POSITION_SIZE:.2%}")
    price_history_cache = {}
    try:
        run_trading_cycle(price_history_cache)
        print("\n✅ Cycle completed successfully")
    except KeyboardInterrupt:
        print("\n⛔ Trading stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
POLYSCRIPT

echo "✅ polymarket_live.py created"

# Create dashboard.py
echo "⚙️  Creating dashboard.py..."
cat > dashboard.py << 'DASHSCRIPT'
#!/usr/bin/env python3
import json, os, statistics
from datetime import datetime
from typing import Dict, List

def load_positions() -> Dict:
    if os.path.exists("/root/polymarket_trading/positions.json"):
        try:
            with open("/root/polymarket_trading/positions.json") as f:
                return json.load(f)
        except:
            pass
    return {"positions": [], "cash": 100.0, "equity": 100.0, "max_drawdown": 0.0, "consecutive_losses": 0}

def load_trades() -> List[Dict]:
    if os.path.exists("/root/polymarket_trading/trades.json"):
        try:
            with open("/root/polymarket_trading/trades.json") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            pass
    return []

def load_equity_history() -> List[Dict]:
    if os.path.exists("/root/polymarket_trading/equity_live.json"):
        try:
            with open("/root/polymarket_trading/equity_live.json") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            pass
    return []

def calculate_metrics(trades: List[Dict], equity_history: List[Dict]) -> Dict:
    sells = [t for t in trades if t["type"] == "SELL"]
    if not sells:
        return {"total_trades": 0, "winning_trades": 0, "losing_trades": 0, "win_rate": 0.0, "total_pnl": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "profit_factor": 0.0, "max_drawdown": 0.0, "sharpe_ratio": 0.0}
    wins = [t["realized_pnl"] for t in sells if t["realized_pnl"] > 0]
    losses = [t["realized_pnl"] for t in sells if t["realized_pnl"] <= 0]
    total_pnl = sum(t["realized_pnl"] for t in sells)
    win_rate = len(wins) / len(sells) if sells else 0
    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = statistics.mean(losses) if losses else 0
    gross_profit = sum(wins) if wins else 0
    gross_loss = abs(sum(losses)) if losses else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    if equity_history:
        equities = [e["equity"] for e in equity_history]
        max_drawdown = max([(equities[0] - e) / equities[0] for e in equities] + [0])
        if len(equities) > 1:
            returns = [(equities[i+1] - equities[i]) / equities[i] for i in range(len(equities)-1)]
            sharpe_ratio = (statistics.mean(returns) * 252) / (statistics.stdev(returns) * (252**0.5)) if returns and statistics.stdev(returns) > 0 else 0.0
        else:
            sharpe_ratio = 0.0
    else:
        max_drawdown = 0.0
        sharpe_ratio = 0.0
    return {"total_trades": len(sells), "winning_trades": len(wins), "losing_trades": len(losses), "win_rate": win_rate, "total_pnl": total_pnl, "avg_win": avg_win, "avg_loss": avg_loss, "profit_factor": profit_factor, "max_drawdown": max_drawdown, "sharpe_ratio": sharpe_ratio}

def print_dashboard():
    positions = load_positions()
    trades = load_trades()
    equity_history = load_equity_history()
    metrics = calculate_metrics(trades, equity_history)
    print("\n" + "="*70)
    print(" " * 15 + "POLYMARKET PAPER TRADING DASHBOARD")
    print("="*70)
    print(f"\n📊 PORTFOLIO STATUS")
    print(f"  Bankroll:              ${positions.get('cash', 0):.2f}")
    print(f"  Current Equity:        ${positions.get('equity', 0):.2f}")
    print(f"  P&L:                   ${positions.get('equity', 100) - 100:.2f} ({(positions.get('equity', 100) / 100 - 1) * 100:.2f}%)")
    print(f"  Max Drawdown:          {positions.get('max_drawdown', 0):.2%}")
    print(f"  Consecutive Losses:    {positions.get('consecutive_losses', 0)}/3 🔴" if positions.get('consecutive_losses', 0) >= 3 else f"  Consecutive Losses:    {positions.get('consecutive_losses', 0)}/3")
    if positions.get("positions"):
        print(f"\n🔓 OPEN POSITIONS ({len(positions['positions'])})")
        for i, pos in enumerate(positions["positions"], 1):
            emoji = "📈" if pos["unrealized_pnl_pct"] > 0 else "📉"
            print(f"  {i}. {pos['market_question'][:40]}")
            print(f"     Entry: ${pos['entry_price']:.3f} | Current: ${pos['current_price']:.3f}")
            print(f"     P&L: ${pos['unrealized_pnl']:.2f} ({pos['unrealized_pnl_pct']:.2%}) {emoji}")
    else:
        print(f"\n🔓 OPEN POSITIONS: None")
    print(f"\n📈 PERFORMANCE METRICS")
    print(f"  Total Trades:          {metrics['total_trades']}")
    print(f"  Winning Trades:        {metrics['winning_trades']}")
    print(f"  Losing Trades:         {metrics['losing_trades']}")
    print(f"  Win Rate:              {metrics['win_rate']:.1%}")
    print(f"  Total P&L:             ${metrics['total_pnl']:.2f}")
    print(f"  Avg Win:               ${metrics['avg_win']:.2f}")
    print(f"  Avg Loss:              ${metrics['avg_loss']:.2f}")
    print(f"  Profit Factor:         {metrics['profit_factor']:.2f}")
    print(f"  Max Drawdown:          {metrics['max_drawdown']:.2%}")
    print(f"  Sharpe Ratio:          {metrics['sharpe_ratio']:.2f}")
    if trades:
        print(f"\n💬 RECENT TRADES (Last 5)")
        for trade in trades[-5:]:
            if trade["type"] == "SELL":
                pnl_emoji = "✅" if trade["realized_pnl"] > 0 else "❌"
                print(f"  🔴 SELL {pnl_emoji} {trade['market'][:35]} @ ${trade['price']:.3f} | P&L: ${trade['realized_pnl']:.2f}")
            else:
                print(f"  🟢 BUY {trade['market'][:35]} @ ${trade['price']:.3f} ({trade['strategy']})")
    if equity_history:
        print(f"\n📊 EQUITY CURVE (Last 10)")
        for e in equity_history[-10:]:
            time_str = e["timestamp"].split("T")[1][:5]
            eq = e["equity"]
            pnl_pct = (eq / 100 - 1) * 100
            pnl_emoji = "📈" if pnl_pct > 0 else "📉"
            print(f"  {time_str}: ${eq:.2f} ({pnl_pct:+.2f}%) {pnl_emoji}")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    print_dashboard()
DASHSCRIPT

echo "✅ dashboard.py created"

# Setup cron
echo ""
echo "⏰ Setting up 15-minute cron job..."
(crontab -l 2>/dev/null | grep -v "polymarket_trading" || echo "") | crontab -
(crontab -l 2>/dev/null || echo ""; echo "*/15 * * * * cd /root/polymarket_trading && python3 polymarket_live.py >> trading.log 2>&1") | crontab -
echo "✅ Cron job installed"

# Test
echo ""
echo "🧪 Testing trading engine..."
python3 polymarket_live.py 2>&1 | head -20

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✓ Workspace:     /root/polymarket_trading"
echo "✓ Files:         polymarket_live.py, dashboard.py"
echo "✓ Cron job:      Active (runs every 15 minutes)"
echo ""
echo "📱 USE ON YOUR iPhone WITH TERMIUS:"
echo "   1. Connect via Termius"
echo "   2. Run: python3 dashboard.py"
echo "   3. Check daily"
echo ""
echo "✅ System is LIVE! Trading every 15 minutes!"
echo "════════════════════════════════════════════════════════════════"
