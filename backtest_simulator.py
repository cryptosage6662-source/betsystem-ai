"""
Polymarket Backtesting Simulator - Phase 3: Historical Data Generation
Simulates realistic price movements and market conditions for backtesting
"""

import json
import math
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class MarketScenario(Enum):
    """Market scenarios for simulation"""
    BULL = "bull"           # Prices trending upward
    BEAR = "bear"           # Prices trending downward
    SIDEWAYS = "sideways"   # Prices moving sideways with volatility
    VOLATILE = "volatile"   # High volatility, random walks


@dataclass
class PriceSnapshot:
    """A snapshot of market price at a point in time"""
    timestamp: str
    yes_price: float
    no_price: float
    volume: float
    volatility: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class HistoricalDataSimulator:
    """
    Simulates realistic historical price data for backtesting
    
    Features:
    - Generate price series with mean reversion
    - Support multiple market scenarios (bull, bear, sideways, volatile)
    - Simulate volume and volatility changes
    - Create realistic price movements with volatility clustering
    - Support variable date ranges
    """
    
    def __init__(self, 
                 start_date: datetime = None,
                 num_days: int = 30,
                 scenario: MarketScenario = MarketScenario.BULL,
                 initial_yes_price: float = 0.45):
        """
        Initialize the simulator
        
        Args:
            start_date: Starting date for simulation (default: 30 days ago)
            num_days: Number of days to simulate
            scenario: Market scenario (BULL, BEAR, SIDEWAYS, VOLATILE)
            initial_yes_price: Starting YES price (0.0 to 1.0)
        """
        self.scenario = scenario
        self.num_days = num_days
        self.initial_yes_price = initial_yes_price
        
        # Set start date
        if start_date is None:
            self.start_date = datetime.now(timezone.utc) - timedelta(days=num_days)
        else:
            self.start_date = start_date
        
        # Scenario parameters
        self._setup_scenario_params()
        
        # Price history
        self.prices: List[PriceSnapshot] = []
        self.market_id = f"sim_{scenario.value}_{int(datetime.now(timezone.utc).timestamp())}"
    
    def _setup_scenario_params(self):
        """Setup parameters based on scenario"""
        if self.scenario == MarketScenario.BULL:
            # Uptrend with mean reversion
            self.drift = 0.003  # 0.3% daily drift upward
            self.volatility = 0.02  # 2% daily volatility
            self.mean_price = 0.65  # Trend toward higher prices
            self.mean_reversion_speed = 0.1  # Weak mean reversion
            self.base_volume = 5000.0
            
        elif self.scenario == MarketScenario.BEAR:
            # Downtrend
            self.drift = -0.003  # -0.3% daily drift downward
            self.volatility = 0.025  # 2.5% daily volatility
            self.mean_price = 0.35  # Trend toward lower prices
            self.mean_reversion_speed = 0.08
            self.base_volume = 4500.0
            
        elif self.scenario == MarketScenario.SIDEWAYS:
            # Ranging market
            self.drift = 0.0  # No trend
            self.volatility = 0.015  # 1.5% daily volatility
            self.mean_price = 0.50  # Revert to middle
            self.mean_reversion_speed = 0.15  # Strong mean reversion
            self.base_volume = 3000.0
            
        else:  # VOLATILE
            # High volatility, random walks
            self.drift = 0.0  # No trend
            self.volatility = 0.04  # 4% daily volatility (high)
            self.mean_price = 0.50
            self.mean_reversion_speed = 0.05  # Weak mean reversion
            self.base_volume = 6000.0
    
    def _generate_price_movement(self, current_price: float) -> float:
        """
        Generate next price movement using geometric Brownian motion
        with mean reversion
        
        Args:
            current_price: Current price
            
        Returns:
            Next price
        """
        # Brownian motion component
        random_shock = random.gauss(0, self.volatility)
        
        # Drift component (scenario-specific trend)
        drift_component = self.drift
        
        # Mean reversion component
        price_deviation = current_price - self.mean_price
        reversion_component = -self.mean_reversion_speed * price_deviation
        
        # Combine components
        log_return = drift_component + reversion_component + random_shock
        
        # Calculate new price
        new_price = current_price * math.exp(log_return)
        
        # Clamp to valid range [0.01, 0.99]
        new_price = max(0.01, min(0.99, new_price))
        
        return new_price
    
    def _generate_volume(self, base_volatility: float) -> float:
        """
        Generate trading volume with clustering
        
        Args:
            base_volatility: Current volatility level
            
        Returns:
            Volume amount
        """
        # Volume tends to increase with volatility
        volatility_factor = 1 + (base_volatility / self.volatility) * 0.5
        
        # Add some randomness
        noise = random.gauss(1.0, 0.2)
        
        volume = self.base_volume * volatility_factor * noise
        return max(500, volume)  # Minimum volume
    
    def generate_price_series(self) -> List[PriceSnapshot]:
        """
        Generate a series of price snapshots
        
        Returns:
            List of PriceSnapshot objects
        """
        self.prices = []
        current_price = self.initial_yes_price
        current_time = self.start_date
        current_volatility = self.volatility
        
        # Generate daily snapshots
        for day in range(self.num_days):
            # Generate intraday prices (4 snapshots per day for better resolution)
            for hour in [6, 12, 18, 23]:  # Morning, midday, evening, night
                current_price = self._generate_price_movement(current_price)
                
                # Update volatility (volatility clustering)
                if random.random() < 0.1:  # 10% chance of regime change
                    current_volatility = self.volatility * random.uniform(0.7, 1.5)
                
                volume = self._generate_volume(current_volatility)
                
                # Create snapshot
                timestamp = current_time + timedelta(hours=hour)
                snapshot = PriceSnapshot(
                    timestamp=timestamp.isoformat(),
                    yes_price=current_price,
                    no_price=1.0 - current_price,
                    volume=volume,
                    volatility=current_volatility
                )
                self.prices.append(snapshot)
            
            # Move to next day
            current_time += timedelta(days=1)
        
        return self.prices
    
    def get_price_at_time(self, target_time: datetime) -> Optional[PriceSnapshot]:
        """
        Get the closest price snapshot to a given time
        
        Args:
            target_time: Target datetime
            
        Returns:
            PriceSnapshot or None if not found
        """
        if not self.prices:
            return None
        
        # Find closest timestamp
        closest = min(
            self.prices,
            key=lambda p: abs(
                datetime.fromisoformat(p.timestamp) - target_time
            )
        )
        
        return closest
    
    def get_prices_in_range(self, 
                           start_time: datetime, 
                           end_time: datetime) -> List[PriceSnapshot]:
        """
        Get all price snapshots in a time range
        
        Args:
            start_time: Start of range
            end_time: End of range
            
        Returns:
            List of PriceSnapshot objects in range
        """
        if not self.prices:
            return []
        
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()
        
        return [p for p in self.prices 
                if start_iso <= p.timestamp <= end_iso]
    
    def export_to_json(self, filepath: str = None) -> str:
        """
        Export price series to JSON file
        
        Args:
            filepath: Output file path (auto-generated if not specified)
            
        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = f"historical_data_{self.scenario.value}.json"
        
        # Calculate statistics
        prices = [p.yes_price for p in self.prices]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market_id": self.market_id,
            "scenario": self.scenario.value,
            "start_date": self.start_date.isoformat(),
            "num_days": self.num_days,
            "num_snapshots": len(self.prices),
            "initial_price": self.initial_yes_price,
            "final_price": self.prices[-1].yes_price if self.prices else None,
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "price_range": max_price - min_price,
            "statistics": {
                "min_price": min_price,
                "max_price": max_price,
                "avg_price": avg_price,
                "price_change_pct": ((self.prices[-1].yes_price - self.initial_yes_price) / 
                                    self.initial_yes_price * 100) if self.prices else 0,
            },
            "prices": [p.to_dict() for p in self.prices]
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Exported {len(self.prices)} price snapshots to {filepath}")
        return filepath
    
    def print_summary(self):
        """Print summary of generated data"""
        if not self.prices:
            print("No price data generated yet")
            return
        
        prices = [p.yes_price for p in self.prices]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        final_price = prices[-1]
        
        print(f"\n{'='*60}")
        print(f"HISTORICAL DATA SIMULATION - {self.scenario.value.upper()}")
        print(f"{'='*60}")
        print(f"Market ID: {self.market_id}")
        print(f"Period: {self.start_date.date()} to {self.start_date.date() + timedelta(days=self.num_days)}")
        print(f"Snapshots: {len(self.prices)}")
        print(f"\nPrice Statistics:")
        print(f"  Initial: {self.initial_yes_price:.4f}")
        print(f"  Final: {final_price:.4f}")
        print(f"  Min: {min_price:.4f}")
        print(f"  Max: {max_price:.4f}")
        print(f"  Average: {avg_price:.4f}")
        print(f"  Range: {max_price - min_price:.4f}")
        print(f"  Return: {(final_price - self.initial_yes_price) / self.initial_yes_price * 100:+.2f}%")
        print(f"\nScenario Parameters:")
        print(f"  Drift: {self.drift:+.4f}")
        print(f"  Volatility: {self.volatility:.4f}")
        print(f"  Mean Price: {self.mean_price:.4f}")
        print(f"  Mean Reversion Speed: {self.mean_reversion_speed:.4f}")
        print(f"{'='*60}\n")


class BacktestDataManager:
    """Manages multiple historical datasets for backtesting"""
    
    def __init__(self):
        """Initialize data manager"""
        self.simulators: Dict[str, HistoricalDataSimulator] = {}
    
    def add_scenario(self, 
                    scenario: MarketScenario,
                    num_days: int = 30,
                    initial_yes_price: float = 0.45) -> HistoricalDataSimulator:
        """
        Add a new scenario to the dataset
        
        Args:
            scenario: Market scenario
            num_days: Number of days to simulate
            initial_yes_price: Initial price
            
        Returns:
            HistoricalDataSimulator instance
        """
        simulator = HistoricalDataSimulator(
            num_days=num_days,
            scenario=scenario,
            initial_yes_price=initial_yes_price
        )
        simulator.generate_price_series()
        self.simulators[scenario.value] = simulator
        return simulator
    
    def get_scenario(self, scenario: MarketScenario) -> Optional[HistoricalDataSimulator]:
        """Get a specific scenario"""
        return self.simulators.get(scenario.value)
    
    def export_all(self, prefix: str = "backtest_data"):
        """Export all scenarios to JSON files"""
        exports = {}
        for scenario_name, simulator in self.simulators.items():
            filepath = f"{prefix}_{scenario_name}.json"
            simulator.export_to_json(filepath)
            exports[scenario_name] = filepath
        return exports


def main():
    """Generate sample historical data for backtesting"""
    
    # Create data manager
    manager = BacktestDataManager()
    
    # Generate scenarios
    print("Generating historical data for all scenarios...\n")
    
    for scenario in [MarketScenario.BULL, MarketScenario.BEAR, 
                     MarketScenario.SIDEWAYS, MarketScenario.VOLATILE]:
        sim = manager.add_scenario(scenario, num_days=30, initial_yes_price=0.45)
        sim.print_summary()
    
    # Export all
    print("Exporting all scenarios...")
    exports = manager.export_all("historical_data")
    
    print(f"\n{'='*60}")
    print(f"Export Summary:")
    for scenario, filepath in exports.items():
        print(f"  • {scenario}: {filepath}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
