"""
Polymarket Strategy Module - Phase 2: Mean-Reversion Strategy
Implements trading signals for crypto prediction markets based on mean-reversion
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class Signal(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    NONE = "NONE"


@dataclass
class StrategySignal:
    """Represents a trading signal from the strategy"""
    market_id: str
    question: str
    signal: Signal
    current_price: float
    entry_threshold: float
    exit_threshold: float
    position_size: float
    confidence: float  # 0.0 to 1.0
    reason: str
    timestamp: str
    is_uptrend: bool
    recent_momentum: float  # Price change in recent period


class MeanReversionStrategy:
    """
    Mean-Reversion Strategy for Polymarket crypto prediction markets
    
    Logic:
    - On "Up" crypto markets (BTC/ETH price up markets)
    - Buy YES when price < 0.40 (prices are likely to revert upward)
    - Sell when > 0.60 (take profits before mean reversion)
    - Support multiple concurrent positions
    - Max position size: $10 per trade
    """
    
    # Strategy parameters
    BUY_THRESHOLD = 0.40      # Buy YES when price below this
    SELL_THRESHOLD = 0.60     # Sell YES when price above this
    MAX_POSITION_SIZE = 10.0  # Max dollars per trade
    
    # Uptrend detection parameters
    MIN_VOLUME_FOR_TRADE = 1000  # Minimum volume to consider
    MIN_LIQUIDITY = 100          # Minimum liquidity
    
    def __init__(self):
        """Initialize strategy"""
        self.trade_history = []
        self.market_history = {}  # Track recent prices for momentum
    
    def is_uptrend_market(self, market: Dict) -> bool:
        """
        Detect if market is for an "Up" crypto direction
        
        Args:
            market: Market data from API
            
        Returns:
            True if market is about crypto price going up
        """
        question = (market.get("question") or "").upper()
        
        # Keywords for uptrend markets
        uptrend_keywords = ["UP", "ABOVE", "BREAK", "HIGHER", "RISE", "INCREASE", "SURGE"]
        crypto_keywords = ["BTC", "BITCOIN", "ETH", "ETHEREUM", "SOL", "SOLANA", "CRYPTO"]
        
        has_uptrend = any(keyword in question for keyword in uptrend_keywords)
        has_crypto = any(keyword in question for keyword in crypto_keywords)
        
        return has_uptrend and has_crypto
    
    def calculate_momentum(self, market_id: str, current_price: float) -> float:
        """
        Calculate recent price momentum for a market
        
        Args:
            market_id: Market identifier
            current_price: Current YES price
            
        Returns:
            Momentum factor (-1.0 to 1.0)
        """
        if market_id not in self.market_history:
            self.market_history[market_id] = []
        
        history = self.market_history[market_id]
        
        # Keep last 10 price observations
        history.append((datetime.now(timezone.utc), current_price))
        if len(history) > 10:
            history.pop(0)
        
        # Calculate momentum
        if len(history) < 2:
            return 0.0
        
        price_change = current_price - history[0][1]
        # Normalize to -1.0 to 1.0 range (price can be 0 to 1)
        momentum = max(-1.0, min(1.0, price_change * 2))
        
        return momentum
    
    def evaluate_entry(self, market: Dict) -> Tuple[bool, float, str]:
        """
        Evaluate if we should enter a position (BUY YES)
        
        Args:
            market: Market data from API
            
        Returns:
            Tuple of (should_buy, confidence, reason)
        """
        yes_price = market.get("yes_price", 0.5)
        volume = market.get("volume", 0)
        liquidity = market.get("liquidity", 0)
        
        reasons = []
        
        # Check 1: Price below buy threshold
        below_threshold = yes_price < self.BUY_THRESHOLD
        if below_threshold:
            reasons.append(f"price {yes_price:.2%} below threshold {self.BUY_THRESHOLD:.2%}")
        
        # Check 2: Sufficient volume
        has_volume = volume >= self.MIN_VOLUME_FOR_TRADE
        if has_volume:
            reasons.append(f"volume ${volume:,.0f} sufficient")
        
        # Check 3: Sufficient liquidity
        has_liquidity = liquidity >= self.MIN_LIQUIDITY
        if has_liquidity:
            reasons.append(f"liquidity ${liquidity:,.0f} sufficient")
        
        # Check 4: Not about to expire (at least 1 day left)
        days_to_expiry = market.get("days_to_expiry", 0)
        not_expiring = days_to_expiry >= 1
        if not_expiring:
            reasons.append(f"{days_to_expiry} days to expiry")
        
        # Confidence = how many checks pass
        checks_passed = sum([below_threshold, has_volume, has_liquidity, not_expiring])
        confidence = checks_passed / 4.0
        
        should_buy = below_threshold and has_volume and has_liquidity and not_expiring
        
        reason = " | ".join(reasons) if reasons else "conditions not met"
        
        return should_buy, confidence, reason
    
    def evaluate_exit(self, market: Dict, entry_price: float) -> Tuple[bool, float, str]:
        """
        Evaluate if we should exit a position (SELL YES)
        
        Args:
            market: Market data from API
            entry_price: Price we bought at
            
        Returns:
            Tuple of (should_sell, confidence, reason)
        """
        yes_price = market.get("yes_price", 0.5)
        
        reasons = []
        
        # Check 1: Price above sell threshold
        above_threshold = yes_price > self.SELL_THRESHOLD
        if above_threshold:
            reasons.append(f"price {yes_price:.2%} above threshold {self.SELL_THRESHOLD:.2%}")
        
        # Check 2: Price above entry (profitable)
        profitable = yes_price > entry_price
        profit_pct = ((yes_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
        if profitable:
            reasons.append(f"profitable (+{profit_pct:.1f}%)")
        
        # Check 3: Not expiring soon (still tradeable)
        days_to_expiry = market.get("days_to_expiry", 0)
        tradeable = days_to_expiry >= 0.5  # At least half a day left
        if tradeable:
            reasons.append(f"{days_to_expiry:.1f} days left")
        
        # Confidence = how many checks pass
        checks_passed = sum([above_threshold, profitable, tradeable])
        confidence = checks_passed / 3.0
        
        # Exit conditions: either hit profit target or expiring
        should_sell = above_threshold or (not tradeable)
        
        reason = " | ".join(reasons) if reasons else "hold"
        
        return should_sell, confidence, reason
    
    def generate_signal(self, market: Dict) -> Optional[StrategySignal]:
        """
        Generate trading signal for a market
        
        Args:
            market: Market data from API
            
        Returns:
            StrategySignal or None if not tradeable
        """
        # Filter: Only process "Up" crypto markets
        if not self.is_uptrend_market(market):
            return None
        
        market_id = market.get("market_id")
        question = market.get("question", "")
        yes_price = market.get("yes_price", 0.5)
        
        # Calculate momentum
        momentum = self.calculate_momentum(market_id, yes_price)
        
        # Determine signal
        signal = Signal.NONE
        entry_threshold = self.BUY_THRESHOLD
        exit_threshold = self.SELL_THRESHOLD
        confidence = 0.0
        reason = ""
        
        # Check for entry signal
        should_buy, buy_confidence, buy_reason = self.evaluate_entry(market)
        if should_buy:
            signal = Signal.BUY
            confidence = buy_confidence
            reason = buy_reason
        else:
            # Check for exit signal (would apply to existing positions)
            should_sell, sell_confidence, sell_reason = self.evaluate_exit(
                market, 
                self.BUY_THRESHOLD  # Assume we bought near threshold
            )
            if should_sell:
                signal = Signal.SELL
                confidence = sell_confidence
                reason = sell_reason
        
        if signal == Signal.NONE:
            return None
        
        return StrategySignal(
            market_id=market_id,
            question=question,
            signal=signal,
            current_price=yes_price,
            entry_threshold=entry_threshold,
            exit_threshold=exit_threshold,
            position_size=self.MAX_POSITION_SIZE,
            confidence=confidence,
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
            is_uptrend=True,
            recent_momentum=momentum
        )
    
    def generate_signals(self, markets: List[Dict]) -> List[StrategySignal]:
        """
        Generate trading signals for multiple markets
        
        Args:
            markets: List of market data from API
            
        Returns:
            List of StrategySignal objects
        """
        signals = []
        
        for market in markets:
            signal = self.generate_signal(market)
            if signal:
                signals.append(signal)
        
        return signals
    
    def format_signals_for_display(self, signals: List[StrategySignal]) -> str:
        """
        Format signals for display
        
        Args:
            signals: List of strategy signals
            
        Returns:
            Formatted string for display
        """
        if not signals:
            return "No trading signals generated"
        
        output = [f"\n{'='*70}"]
        output.append(f"STRATEGY SIGNALS - {len(signals)} signal(s) generated")
        output.append(f"{'='*70}")
        
        buy_signals = [s for s in signals if s.signal == Signal.BUY]
        sell_signals = [s for s in signals if s.signal == Signal.SELL]
        
        if buy_signals:
            output.append(f"\n📈 BUY SIGNALS ({len(buy_signals)}):")
            for signal in buy_signals:
                output.append(f"  • {signal.question}")
                output.append(f"    Price: {signal.current_price:.2%} (threshold: {signal.entry_threshold:.2%})")
                output.append(f"    Size: ${signal.position_size:.2f} | Confidence: {signal.confidence:.0%}")
                output.append(f"    Reason: {signal.reason}")
        
        if sell_signals:
            output.append(f"\n📉 SELL SIGNALS ({len(sell_signals)}):")
            for signal in sell_signals:
                output.append(f"  • {signal.question}")
                output.append(f"    Price: {signal.current_price:.2%} (threshold: {signal.exit_threshold:.2%})")
                output.append(f"    Size: ${signal.position_size:.2f} | Confidence: {signal.confidence:.0%}")
                output.append(f"    Reason: {signal.reason}")
        
        output.append(f"{'='*70}\n")
        
        return "\n".join(output)


def main():
    """Test the strategy with sample data"""
    from polymarket_api import PolymarketAPI
    
    # Load sample markets
    try:
        with open("sample_markets.json", "r") as f:
            data = json.load(f)
            markets = data.get("markets", [])
    except FileNotFoundError:
        print("sample_markets.json not found. Run polymarket_api.py first.")
        return
    
    # Initialize strategy
    strategy = MeanReversionStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(markets)
    
    # Display results
    print(strategy.format_signals_for_display(signals))
    
    # Save signals to file
    if signals:
        signals_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(signals),
            "signals": [asdict(s) for s in signals]
        }
        with open("signals.json", "w") as f:
            json.dump(signals_data, f, indent=2)
        print(f"Signals saved to signals.json")


if __name__ == "__main__":
    main()
