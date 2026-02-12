"""
Polymarket Backtesting Engine - Phase 3: Historical Simulation
Runs trading strategy on historical data and tracks performance
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

from backtest_simulator import HistoricalDataSimulator, PriceSnapshot, MarketScenario
from polymarket_strategy import MeanReversionStrategy, Signal, StrategySignal


class BacktestTradeStatus(Enum):
    """Trade status in backtest"""
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class BacktestTrade:
    """Represents a trade in backtest"""
    trade_id: str
    entry_time: str
    entry_price: float
    exit_time: Optional[str] = None
    exit_price: Optional[float] = None
    quantity: float = 10.0  # Position size in dollars
    p_l: float = 0.0
    p_l_percent: float = 0.0
    status: str = "open"
    entry_reason: str = ""
    exit_reason: str = ""
    days_held: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class BacktestState:
    """State snapshot during backtest"""
    timestamp: str
    price: float
    equity: float
    cash: float
    positions: int
    open_trades: List[str] = field(default_factory=list)
    total_return: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class BacktestEngine:
    """
    Backtesting engine that runs strategies on historical data
    
    Features:
    - Execute trades at historical prices
    - Track open positions
    - Calculate realized and unrealized P&L
    - Monitor equity curve
    - Handle circuit breaker logic
    - Support multiple scenarios
    """
    
    def __init__(self, 
                 initial_capital: float = 1000.0,
                 position_size: float = 10.0):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital in dollars
            position_size: Default position size per trade
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        
        # Portfolio state
        self.cash = initial_capital
        self.equity = initial_capital
        self.trades: List[BacktestTrade] = []
        self.open_positions: Dict[str, BacktestTrade] = {}
        
        # Performance tracking
        self.state_history: List[BacktestState] = []
        self.circuit_breaker_active = False
        self.consecutive_losses = 0
        
        # Strategy instance
        self.strategy = MeanReversionStrategy()
        
        # Trade counter
        self.trade_counter = 0
    
    def _generate_trade_id(self) -> str:
        """Generate unique trade ID"""
        self.trade_counter += 1
        return f"bt_{self.trade_counter}"
    
    def _can_open_trade(self) -> bool:
        """Check if we can open a new trade"""
        # Circuit breaker check
        if self.circuit_breaker_active:
            return False
        
        # Sufficient capital check
        if self.cash < self.position_size:
            return False
        
        # Max concurrent positions: 5
        if len(self.open_positions) >= 5:
            return False
        
        return True
    
    def execute_entry(self, 
                     entry_price: float,
                     reason: str,
                     timestamp: str) -> Optional[BacktestTrade]:
        """
        Execute a position entry
        
        Args:
            entry_price: Entry price
            reason: Reason for entry
            timestamp: Entry timestamp
            
        Returns:
            BacktestTrade or None if not opened
        """
        if not self._can_open_trade():
            return None
        
        # Create trade
        trade = BacktestTrade(
            trade_id=self._generate_trade_id(),
            entry_time=timestamp,
            entry_price=entry_price,
            quantity=self.position_size,
            status="open",
            entry_reason=reason
        )
        
        # Update portfolio
        self.cash -= self.position_size
        self.open_positions[trade.trade_id] = trade
        
        return trade
    
    def execute_exit(self,
                    trade_id: str,
                    exit_price: float,
                    reason: str,
                    timestamp: str) -> Optional[BacktestTrade]:
        """
        Execute a position exit
        
        Args:
            trade_id: Trade ID to close
            exit_price: Exit price
            reason: Reason for exit
            timestamp: Exit timestamp
            
        Returns:
            Closed BacktestTrade or None if not found
        """
        if trade_id not in self.open_positions:
            return None
        
        trade = self.open_positions[trade_id]
        
        # Calculate P&L
        price_change = exit_price - trade.entry_price
        p_l = price_change * trade.quantity * 100
        p_l_percent = (price_change / trade.entry_price * 100) if trade.entry_price > 0 else 0
        
        # Calculate days held
        entry_dt = datetime.fromisoformat(trade.entry_time)
        exit_dt = datetime.fromisoformat(timestamp)
        days_held = (exit_dt - entry_dt).total_seconds() / 86400
        
        # Update trade
        trade.exit_time = timestamp
        trade.exit_price = exit_price
        trade.p_l = p_l
        trade.p_l_percent = p_l_percent
        trade.status = "closed"
        trade.exit_reason = reason
        trade.days_held = days_held
        
        # Update portfolio
        self.cash += trade.quantity + p_l
        
        # Track circuit breaker
        if p_l < 0:
            self.consecutive_losses += 1
            if self.consecutive_losses >= 3:
                self.circuit_breaker_active = True
        else:
            self.consecutive_losses = 0
            self.circuit_breaker_active = False
        
        # Move to closed trades
        del self.open_positions[trade_id]
        self.trades.append(trade)
        
        return trade
    
    def update_unrealized_pnl(self, current_price: float):
        """
        Update unrealized P&L for open positions
        
        Args:
            current_price: Current market price
        """
        unrealized = 0.0
        
        for trade in self.open_positions.values():
            price_change = current_price - trade.entry_price
            unrealized += price_change * trade.quantity * 100
        
        # Update equity
        self.equity = self.cash + unrealized
    
    def record_state(self, timestamp: str, price: float):
        """
        Record current portfolio state
        
        Args:
            timestamp: Current timestamp
            price: Current price
        """
        self.update_unrealized_pnl(price)
        
        state = BacktestState(
            timestamp=timestamp,
            price=price,
            equity=self.equity,
            cash=self.cash,
            positions=len(self.open_positions),
            open_trades=list(self.open_positions.keys()),
            total_return=(self.equity - self.initial_capital) / self.initial_capital * 100
        )
        self.state_history.append(state)
    
    def run(self,
            historical_data: HistoricalDataSimulator) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            historical_data: HistoricalDataSimulator with price data
            
        Returns:
            Dict with backtest results
        """
        print(f"\n{'='*70}")
        print(f"BACKTEST ENGINE - Running on {historical_data.scenario.value}")
        print(f"{'='*70}")
        
        # Reset state
        self.cash = self.initial_capital
        self.equity = self.initial_capital
        self.trades = []
        self.open_positions = {}
        self.state_history = []
        self.circuit_breaker_active = False
        self.consecutive_losses = 0
        self.trade_counter = 0
        
        prices = historical_data.prices
        
        # Process each price snapshot
        for i, snapshot in enumerate(prices):
            current_price = snapshot.yes_price
            timestamp = snapshot.timestamp
            
            # Check for exit signals (profit taking, expiration)
            self._check_exits(current_price, timestamp)
            
            # Check for entry signals
            # For backtest, we use price thresholds from strategy
            self._check_entries(current_price, timestamp)
            
            # Record state
            self.record_state(timestamp, current_price)
            
            # Print progress
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(prices)} snapshots | "
                      f"Equity: ${self.equity:.2f} | "
                      f"Positions: {len(self.open_positions)}")
        
        # Close any remaining open positions at final price
        final_price = prices[-1].yes_price
        final_time = prices[-1].timestamp
        for trade_id in list(self.open_positions.keys()):
            self.execute_exit(trade_id, final_price, "Backtest ended", final_time)
        
        # Compile results
        results = self._compile_results(historical_data.scenario)
        
        print(f"\n{'='*70}")
        print(f"BACKTEST COMPLETED")
        print(f"Total Trades: {len(self.trades)}")
        print(f"Final Equity: ${self.equity:.2f}")
        print(f"Total Return: {(self.equity - self.initial_capital) / self.initial_capital * 100:+.2f}%")
        print(f"{'='*70}\n")
        
        return results
    
    def _check_entries(self, current_price: float, timestamp: str):
        """
        Check if we should enter a position
        
        Args:
            current_price: Current price
            timestamp: Current timestamp
        """
        # Buy signal: price below 0.40 (mean reversion)
        if current_price < 0.40:
            # Check if we already have a position
            has_entry = any(t.entry_price < 0.42 for t in self.open_positions.values())
            
            if not has_entry:
                self.execute_entry(current_price, 
                                  f"Mean reversion signal (price {current_price:.2%})",
                                  timestamp)
    
    def _check_exits(self, current_price: float, timestamp: str):
        """
        Check if we should exit any positions
        
        Args:
            current_price: Current price
            timestamp: Current timestamp
        """
        for trade_id, trade in list(self.open_positions.items()):
            # Exit signal: price above 0.60 (profit taking)
            if current_price > 0.60:
                self.execute_exit(trade_id, current_price,
                                "Profit target reached (>60%)",
                                timestamp)
            
            # Stop loss: price below entry - 10%
            elif current_price < trade.entry_price * 0.90:
                self.execute_exit(trade_id, current_price,
                                "Stop loss (-10%)",
                                timestamp)
    
    def _compile_results(self, scenario: MarketScenario) -> Dict:
        """
        Compile backtest results
        
        Args:
            scenario: Market scenario
            
        Returns:
            Dict with results
        """
        completed_trades = [t for t in self.trades if t.status == "closed"]
        winning_trades = [t for t in completed_trades if t.p_l > 0]
        losing_trades = [t for t in completed_trades if t.p_l <= 0]
        
        return {
            "scenario": scenario.value,
            "initial_capital": self.initial_capital,
            "final_equity": self.equity,
            "total_return_dollars": self.equity - self.initial_capital,
            "total_return_percent": (self.equity - self.initial_capital) / self.initial_capital * 100,
            "num_trades": len(completed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(completed_trades) * 100 if completed_trades else 0,
            "total_pnl": sum(t.p_l for t in completed_trades),
            "avg_trade_pnl": sum(t.p_l for t in completed_trades) / len(completed_trades) if completed_trades else 0,
            "best_trade": max((t.p_l for t in completed_trades), default=0),
            "worst_trade": min((t.p_l for t in completed_trades), default=0),
            "avg_trade_duration": sum(t.days_held for t in completed_trades) / len(completed_trades) if completed_trades else 0,
            "max_consecutive_losses": 0,
            "trades": [t.to_dict() for t in completed_trades],
            "state_history": [s.to_dict() for s in self.state_history]
        }
    
    def get_equity_curve(self) -> Tuple[List[str], List[float]]:
        """
        Get equity curve for visualization
        
        Returns:
            Tuple of (timestamps, equity_values)
        """
        timestamps = [s.timestamp for s in self.state_history]
        equities = [s.equity for s in self.state_history]
        return timestamps, equities


def run_backtest_scenario(scenario: MarketScenario, 
                         num_days: int = 30,
                         initial_capital: float = 1000.0) -> Dict:
    """
    Run complete backtest for a scenario
    
    Args:
        scenario: Market scenario to backtest
        num_days: Number of days to simulate
        initial_capital: Starting capital
        
    Returns:
        Dict with backtest results
    """
    # Generate historical data
    simulator = HistoricalDataSimulator(
        num_days=num_days,
        scenario=scenario,
        initial_yes_price=0.45
    )
    simulator.generate_price_series()
    
    # Run backtest
    engine = BacktestEngine(initial_capital=initial_capital)
    results = engine.run(simulator)
    
    return results


def main():
    """Run backtests on all scenarios"""
    
    all_results = {}
    
    for scenario in [MarketScenario.BULL, MarketScenario.BEAR,
                     MarketScenario.SIDEWAYS, MarketScenario.VOLATILE]:
        results = run_backtest_scenario(scenario, num_days=30)
        all_results[scenario.value] = results
    
    # Save results
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenarios": all_results
    }
    
    os.makedirs("backtest_results", exist_ok=True)
    
    with open("backtest_results/backtest_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to backtest_results/backtest_results.json")
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"BACKTEST SUMMARY - ALL SCENARIOS")
    print(f"{'='*70}")
    for scenario, results in all_results.items():
        print(f"\n{scenario.upper()}:")
        print(f"  Final Equity: ${results['final_equity']:.2f}")
        print(f"  Total Return: {results['total_return_percent']:+.2f}%")
        print(f"  Num Trades: {results['num_trades']}")
        print(f"  Win Rate: {results['win_rate']:.1f}%")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
