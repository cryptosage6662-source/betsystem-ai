"""
Polymarket Paper Trading Engine - Phase 2: Trading Execution & Position Management
Simulates real trading without spending actual money
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from polymarket_strategy import MeanReversionStrategy, Signal, StrategySignal


class TradeStatus(Enum):
    """Trade execution status"""
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Position:
    """Represents an open trading position"""
    position_id: str
    market_id: str
    question: str
    entry_time: str
    entry_price: float
    quantity: float  # In terms of position size (dollars)
    signal: str  # Original entry signal reason
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ClosedTrade:
    """Represents a completed trade with P&L"""
    trade_id: str
    market_id: str
    question: str
    entry_time: str
    entry_price: float
    exit_time: str
    exit_price: float
    quantity: float
    p_l: float
    p_l_percent: float
    signal: str
    exit_reason: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TradeMetrics:
    """Performance metrics for trading"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_p_l: float = 0.0
    win_rate: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    max_consecutive_losses: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class PaperTradingEngine:
    """
    Paper Trading Engine for Polymarket crypto prediction markets
    
    Features:
    - Tracks open positions in JSON (positions.json)
    - Executes trades at current market price
    - Calculates unrealized P&L
    - Closes positions on exit signals
    - Tracks closed trades with realized P&L
    - Circuit breaker: stops after 3 consecutive losses
    """
    
    def __init__(self, positions_file: str = "positions.json", trades_file: str = "trades.json"):
        """
        Initialize trading engine
        
        Args:
            positions_file: File to store open positions
            trades_file: File to store trade history
        """
        self.positions_file = positions_file
        self.trades_file = trades_file
        
        # In-memory state
        self.positions: Dict[str, Position] = {}
        self.closed_trades: List[ClosedTrade] = []
        self.metrics = TradeMetrics()
        self.circuit_breaker_active = False
        
        # Load existing state
        self._load_positions()
        self._load_trades()
    
    def _load_positions(self):
        """Load open positions from file"""
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, "r") as f:
                    data = json.load(f)
                    for pos_data in data.get("positions", []):
                        pos = Position(**pos_data)
                        self.positions[pos.position_id] = pos
            except Exception as e:
                print(f"Warning: Could not load positions: {e}")
    
    def _load_trades(self):
        """Load trade history and metrics from file"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, "r") as f:
                    data = json.load(f)
                    
                    # Load closed trades
                    for trade_data in data.get("trades", []):
                        trade = ClosedTrade(**trade_data)
                        self.closed_trades.append(trade)
                    
                    # Load metrics
                    metrics_data = data.get("metrics", {})
                    self.metrics = TradeMetrics(**metrics_data)
                    
                    # Load circuit breaker status
                    self.circuit_breaker_active = data.get("circuit_breaker_active", False)
            except Exception as e:
                print(f"Warning: Could not load trades: {e}")
    
    def _save_positions(self):
        """Save open positions to file"""
        positions_list = [pos.to_dict() for pos in self.positions.values()]
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(positions_list),
            "positions": positions_list
        }
        with open(self.positions_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _save_trades(self):
        """Save trade history to file"""
        trades_list = [trade.to_dict() for trade in self.closed_trades]
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(trades_list),
            "trades": trades_list,
            "metrics": self.metrics.to_dict(),
            "circuit_breaker_active": self.circuit_breaker_active
        }
        with open(self.trades_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _generate_position_id(self, market_id: str) -> str:
        """Generate unique position ID"""
        timestamp = datetime.now(timezone.utc).isoformat().replace(":", "-")
        return f"pos_{market_id}_{timestamp}"
    
    def _generate_trade_id(self, market_id: str) -> str:
        """Generate unique trade ID"""
        timestamp = datetime.now(timezone.utc).isoformat().replace(":", "-")
        return f"trade_{market_id}_{timestamp}"
    
    def open_position(self, signal: StrategySignal) -> Optional[Position]:
        """
        Open a new position based on strategy signal
        
        Args:
            signal: StrategySignal from strategy module
            
        Returns:
            Position object or None if not opened
        """
        # Check circuit breaker
        if self.circuit_breaker_active:
            print(f"⚠️  Circuit breaker active - trading halted after 3 consecutive losses")
            return None
        
        # Only open on BUY signals
        if signal.signal != Signal.BUY:
            return None
        
        # Check if we already have a position in this market
        for pos in self.positions.values():
            if pos.market_id == signal.market_id:
                print(f"⚠️  Position already open in {signal.market_id}")
                return None
        
        # Create position
        position = Position(
            position_id=self._generate_position_id(signal.market_id),
            market_id=signal.market_id,
            question=signal.question,
            entry_time=signal.timestamp,
            entry_price=signal.current_price,
            quantity=signal.position_size,
            signal=signal.reason
        )
        
        self.positions[position.position_id] = position
        self._save_positions()
        
        print(f"✅ BUY: Position opened in {signal.market_id}")
        print(f"   Entry Price: {position.entry_price:.2%} | Size: ${position.quantity:.2f}")
        
        return position
    
    def close_position(self, position_id: str, exit_price: float, exit_reason: str) -> Optional[ClosedTrade]:
        """
        Close an open position
        
        Args:
            position_id: ID of position to close
            exit_price: Price at which we exit
            exit_reason: Reason for closing (exit signal, manual, etc.)
            
        Returns:
            ClosedTrade object or None if position not found
        """
        if position_id not in self.positions:
            return None
        
        position = self.positions[position_id]
        
        # Calculate P&L
        price_diff = exit_price - position.entry_price
        p_l = price_diff * position.quantity * 100  # Scale by quantity
        p_l_percent = ((exit_price - position.entry_price) / position.entry_price * 100) if position.entry_price > 0 else 0
        
        # Create closed trade record
        trade = ClosedTrade(
            trade_id=self._generate_trade_id(position.market_id),
            market_id=position.market_id,
            question=position.question,
            entry_time=position.entry_time,
            entry_price=position.entry_price,
            exit_time=datetime.now(timezone.utc).isoformat(),
            exit_price=exit_price,
            quantity=position.quantity,
            p_l=p_l,
            p_l_percent=p_l_percent,
            signal=position.signal,
            exit_reason=exit_reason
        )
        
        self.closed_trades.append(trade)
        
        # Update metrics
        self._update_metrics(trade)
        
        # Remove position
        del self.positions[position_id]
        
        # Save state
        self._save_positions()
        self._save_trades()
        
        # Log trade
        symbol = "📈" if p_l > 0 else "📉"
        print(f"{symbol} SELL: Position closed in {position.market_id}")
        print(f"   Entry: {position.entry_price:.2%} | Exit: {exit_price:.2%}")
        print(f"   P&L: ${p_l:+.2f} ({p_l_percent:+.1f}%) | Reason: {exit_reason}")
        
        return trade
    
    def _update_metrics(self, trade: ClosedTrade):
        """Update trading metrics after a trade closes"""
        self.metrics.total_trades += 1
        self.metrics.total_p_l += trade.p_l
        
        is_winning = trade.p_l > 0
        
        if is_winning:
            self.metrics.winning_trades += 1
            self.metrics.consecutive_wins += 1
            self.metrics.consecutive_losses = 0  # Reset loss counter
        else:
            self.metrics.losing_trades += 1
            self.metrics.consecutive_losses += 1
            self.metrics.consecutive_wins = 0  # Reset win counter
            
            # Track max consecutive losses
            if self.metrics.consecutive_losses > self.metrics.max_consecutive_losses:
                self.metrics.max_consecutive_losses = self.metrics.consecutive_losses
            
            # Activate circuit breaker after 3 consecutive losses
            if self.metrics.consecutive_losses >= 3:
                self.circuit_breaker_active = True
                print(f"🔴 CIRCUIT BREAKER ACTIVATED after {self.metrics.consecutive_losses} consecutive losses")
        
        # Calculate win rate
        if self.metrics.total_trades > 0:
            self.metrics.win_rate = self.metrics.winning_trades / self.metrics.total_trades * 100
        
        # Calculate average win/loss
        if self.metrics.winning_trades > 0:
            winning_pls = [t.p_l for t in self.closed_trades if t.p_l > 0]
            self.metrics.avg_win = sum(winning_pls) / len(winning_pls)
        
        if self.metrics.losing_trades > 0:
            losing_pls = [t.p_l for t in self.closed_trades if t.p_l <= 0]
            self.metrics.avg_loss = sum(losing_pls) / len(losing_pls) if losing_pls else 0
    
    def reset_circuit_breaker(self, winning_trade: bool = False):
        """
        Reset circuit breaker after conditions are met
        
        Args:
            winning_trade: If True, reset after a winning trade
        """
        if winning_trade and self.metrics.consecutive_losses > 0:
            self.metrics.consecutive_losses = 0
            if self.circuit_breaker_active:
                self.circuit_breaker_active = False
                print(f"🟢 CIRCUIT BREAKER RESET after winning trade")
    
    def calculate_unrealized_pnl(self, market_id: str, current_price: float) -> Tuple[float, float]:
        """
        Calculate unrealized P&L for an open position
        
        Args:
            market_id: Market ID of open position
            current_price: Current market price
            
        Returns:
            Tuple of (unrealized_pnl, unrealized_pnl_percent)
        """
        for position in self.positions.values():
            if position.market_id == market_id:
                price_diff = current_price - position.entry_price
                unrealized_pnl = price_diff * position.quantity * 100
                unrealized_pnl_percent = ((current_price - position.entry_price) / position.entry_price * 100) if position.entry_price > 0 else 0
                return unrealized_pnl, unrealized_pnl_percent
        
        return 0.0, 0.0
    
    def process_signals(self, signals: List[StrategySignal], market_data: Dict[str, Dict]):
        """
        Process strategy signals and execute trades
        
        Args:
            signals: List of StrategySignal objects from strategy
            market_data: Dict of market_id -> market data for price lookups
        """
        print(f"\n{'='*70}")
        print(f"PROCESSING SIGNALS - {len(signals)} signal(s) to process")
        print(f"{'='*70}")
        
        # Process each signal
        for signal in signals:
            if signal.signal == Signal.BUY:
                # Try to open a position
                self.open_position(signal)
            
            elif signal.signal == Signal.SELL:
                # Check for open positions to close
                for position_id, position in list(self.positions.items()):
                    if position.market_id == signal.market_id:
                        self.close_position(position_id, signal.current_price, "Exit signal from strategy")
        
        # Check exit conditions for open positions
        self._check_position_exits(market_data)
    
    def _check_position_exits(self, market_data: Dict[str, Dict]):
        """
        Check if any open positions should be closed based on market data
        
        Args:
            market_data: Dict of market_id -> market data
        """
        for position_id, position in list(self.positions.items()):
            if position.market_id in market_data:
                market = market_data[position.market_id]
                current_price = market.get("yes_price", 0.5)
                days_to_expiry = market.get("days_to_expiry", 0)
                
                # Check for profit-taking
                if current_price > 0.70:  # Good profit
                    self.close_position(position_id, current_price, "Profit target reached (>70%)")
                
                # Check for expiration
                elif days_to_expiry < 0.1:  # Less than 2.4 hours
                    self.close_position(position_id, current_price, "Position expiring soon")
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get summary of current portfolio
        
        Returns:
            Dict with portfolio metrics
        """
        open_positions = len(self.positions)
        total_unrealized_pnl = 0.0
        
        for position in self.positions.values():
            # Would need current market price to calculate actual unrealized P&L
            # For now, just note it
            pass
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "open_positions": open_positions,
            "closed_trades": len(self.closed_trades),
            "total_pnl": self.metrics.total_p_l,
            "win_rate": self.metrics.win_rate,
            "winning_trades": self.metrics.winning_trades,
            "losing_trades": self.metrics.losing_trades,
            "consecutive_losses": self.metrics.consecutive_losses,
            "circuit_breaker_active": self.circuit_breaker_active
        }
    
    def display_summary(self):
        """Display trading summary"""
        summary = self.get_portfolio_summary()
        
        print(f"\n{'='*70}")
        print(f"PORTFOLIO SUMMARY")
        print(f"{'='*70}")
        print(f"Open Positions: {summary['open_positions']}")
        print(f"Closed Trades: {summary['closed_trades']}")
        print(f"Total P&L: ${summary['total_pnl']:+.2f}")
        print(f"Win Rate: {summary['win_rate']:.1f}%")
        print(f"Winning Trades: {summary['winning_trades']} | Losing Trades: {summary['losing_trades']}")
        print(f"Consecutive Losses: {summary['consecutive_losses']}/3")
        print(f"Circuit Breaker: {'🔴 ACTIVE' if summary['circuit_breaker_active'] else '🟢 OFF'}")
        print(f"{'='*70}\n")


def main():
    """Test the trading engine with sample data and signals"""
    from polymarket_strategy import MeanReversionStrategy
    from polymarket_api import PolymarketAPI
    
    # Load sample markets
    try:
        with open("sample_markets.json", "r") as f:
            data = json.load(f)
            markets = data.get("markets", [])
    except FileNotFoundError:
        print("sample_markets.json not found. Run polymarket_api.py first.")
        return
    
    # Create market lookup
    market_data = {m["market_id"]: m for m in markets}
    
    # Initialize strategy
    strategy = MeanReversionStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(markets)
    
    print(strategy.format_signals_for_display(signals))
    
    # Initialize trading engine
    engine = PaperTradingEngine()
    
    # Process signals
    engine.process_signals(signals, market_data)
    
    # Display summary
    engine.display_summary()


if __name__ == "__main__":
    main()
