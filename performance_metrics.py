"""
Polymarket Performance Analytics - Phase 3: Metrics Calculation
Calculates comprehensive trading performance metrics
"""

import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    
    # Summary metrics
    total_return: float  # Total return %
    total_return_dollars: float
    annualized_return: float  # Annualized return %
    
    # Trade metrics
    num_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float  # Win rate %
    
    # P&L metrics
    total_pnl: float
    avg_trade_pnl: float
    median_trade_pnl: float
    best_trade: float
    worst_trade: float
    profit_factor: float  # Sum of wins / abs(sum of losses)
    
    # Risk metrics
    max_drawdown: float  # Max drawdown %
    max_drawdown_dollars: float
    avg_trade_duration: float  # Days
    best_trade_duration: float
    worst_trade_duration: float
    
    # Volatility metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Win/Loss streaks
    longest_win_streak: int
    longest_loss_streak: int
    avg_win: float
    avg_loss: float
    win_loss_ratio: float
    
    # Expectancy
    expectancy: float  # Average trade PnL
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class PerformanceAnalyzer:
    """
    Analyzes trading performance and calculates metrics
    
    Features:
    - Calculate return metrics (total, annualized)
    - Calculate risk metrics (max drawdown, volatility)
    - Calculate efficiency metrics (Sharpe ratio, Sortino ratio)
    - Win/loss analysis
    - Trade duration analysis
    - Compare vs benchmark (buy-and-hold)
    """
    
    def __init__(self, 
                 initial_capital: float = 1000.0,
                 risk_free_rate: float = 0.02):
        """
        Initialize analyzer
        
        Args:
            initial_capital: Starting capital
            risk_free_rate: Annual risk-free rate for Sharpe/Sortino
        """
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
    
    def calculate_metrics(self,
                         equity_values: List[float],
                         trades: List[Dict],
                         timestamps: List[str],
                         num_days: int = 30) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics
        
        Args:
            equity_values: List of equity values over time
            trades: List of completed trades
            timestamps: List of timestamps
            num_days: Number of trading days
            
        Returns:
            PerformanceMetrics object
        """
        
        # Basic return metrics
        total_return = ((equity_values[-1] - self.initial_capital) / 
                       self.initial_capital * 100) if equity_values else 0
        total_return_dollars = equity_values[-1] - self.initial_capital if equity_values else 0
        
        # Annualized return (365 days per year)
        years = num_days / 365.0
        annualized_return = (((equity_values[-1] / self.initial_capital) ** (1 / years) - 1) 
                            * 100) if equity_values and years > 0 else 0
        
        # Trade analysis
        closed_trades = [t for t in trades if t.get("status") == "closed"]
        winning_trades = [t for t in closed_trades if t.get("p_l", 0) > 0]
        losing_trades = [t for t in closed_trades if t.get("p_l", 0) <= 0]
        
        num_trades = len(closed_trades)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        
        win_rate = (winning_count / num_trades * 100) if num_trades > 0 else 0
        
        # P&L metrics
        pnl_values = [t.get("p_l", 0) for t in closed_trades]
        total_pnl = sum(pnl_values)
        avg_trade_pnl = total_pnl / num_trades if num_trades > 0 else 0
        median_trade_pnl = self._median(pnl_values)
        
        best_trade = max(pnl_values) if pnl_values else 0
        worst_trade = min(pnl_values) if pnl_values else 0
        
        # Profit factor
        winning_pnl = sum(t.get("p_l", 0) for t in winning_trades)
        losing_pnl = abs(sum(t.get("p_l", 0) for t in losing_trades))
        profit_factor = winning_pnl / losing_pnl if losing_pnl > 0 else 0
        
        # Risk metrics
        max_drawdown, max_drawdown_dollars = self._calculate_max_drawdown(equity_values)
        
        # Trade duration analysis
        durations = [t.get("days_held", 0) for t in closed_trades]
        avg_trade_duration = sum(durations) / len(durations) if durations else 0
        best_trade_duration = max(durations) if durations else 0
        worst_trade_duration = min(durations) if durations else 0
        
        # Volatility metrics
        returns = self._calculate_returns(equity_values)
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        sortino_ratio = self._calculate_sortino_ratio(returns)
        calmar_ratio = (annualized_return / abs(max_drawdown) 
                       if max_drawdown != 0 else 0)
        
        # Win/Loss streaks
        longest_win_streak = self._calculate_longest_streak(closed_trades, True)
        longest_loss_streak = self._calculate_longest_streak(closed_trades, False)
        
        # Win/Loss averages
        avg_win = (sum(t.get("p_l", 0) for t in winning_trades) / 
                  winning_count if winning_count > 0 else 0)
        avg_loss = (sum(t.get("p_l", 0) for t in losing_trades) / 
                   losing_count if losing_count > 0 else 0)
        
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Expectancy
        expectancy = avg_trade_pnl
        
        return PerformanceMetrics(
            total_return=total_return,
            total_return_dollars=total_return_dollars,
            annualized_return=annualized_return,
            num_trades=num_trades,
            winning_trades=winning_count,
            losing_trades=losing_count,
            win_rate=win_rate,
            total_pnl=total_pnl,
            avg_trade_pnl=avg_trade_pnl,
            median_trade_pnl=median_trade_pnl,
            best_trade=best_trade,
            worst_trade=worst_trade,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            max_drawdown_dollars=max_drawdown_dollars,
            avg_trade_duration=avg_trade_duration,
            best_trade_duration=best_trade_duration,
            worst_trade_duration=worst_trade_duration,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            longest_win_streak=longest_win_streak,
            longest_loss_streak=longest_loss_streak,
            avg_win=avg_win,
            avg_loss=avg_loss,
            win_loss_ratio=win_loss_ratio,
            expectancy=expectancy
        )
    
    def _median(self, values: List[float]) -> float:
        """Calculate median of a list"""
        if not values:
            return 0.0
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        if n % 2 == 0:
            return (sorted_vals[n//2 - 1] + sorted_vals[n//2]) / 2
        else:
            return sorted_vals[n//2]
    
    def _calculate_returns(self, equity_values: List[float]) -> List[float]:
        """Calculate daily returns from equity curve"""
        if len(equity_values) < 2:
            return []
        
        returns = []
        for i in range(1, len(equity_values)):
            if equity_values[i-1] != 0:
                ret = (equity_values[i] - equity_values[i-1]) / equity_values[i-1]
                returns.append(ret)
        
        return returns
    
    def _calculate_max_drawdown(self, equity_values: List[float]) -> Tuple[float, float]:
        """
        Calculate maximum drawdown
        
        Returns:
            Tuple of (max_drawdown_percent, max_drawdown_dollars)
        """
        if not equity_values:
            return 0.0, 0.0
        
        max_equity = equity_values[0]
        max_dd = 0.0
        max_dd_dollars = 0.0
        
        for equity in equity_values:
            if equity > max_equity:
                max_equity = equity
            
            dd = (max_equity - equity) / max_equity * 100 if max_equity > 0 else 0
            dd_dollars = max_equity - equity
            
            if dd > max_dd:
                max_dd = dd
                max_dd_dollars = dd_dollars
        
        return max_dd, max_dd_dollars
    
    def _calculate_sharpe_ratio(self, returns: List[float], 
                               periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: List of daily returns
            periods_per_year: Trading periods per year (default 252 for daily)
            
        Returns:
            Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
        
        # Daily risk-free rate
        daily_rf_rate = (1 + self.risk_free_rate) ** (1/periods_per_year) - 1
        
        # Annualized Sharpe
        sharpe = (avg_return - daily_rf_rate) / std_dev * math.sqrt(periods_per_year)
        
        return sharpe
    
    def _calculate_sortino_ratio(self, returns: List[float],
                                periods_per_year: int = 252) -> float:
        """
        Calculate Sortino ratio (only penalizes downside volatility)
        
        Args:
            returns: List of daily returns
            periods_per_year: Trading periods per year
            
        Returns:
            Sortino ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        
        # Downside volatility (only negative returns)
        downside_returns = [r for r in returns if r < 0]
        if downside_returns:
            downside_variance = sum(r ** 2 for r in downside_returns) / len(returns)
            downside_std = math.sqrt(downside_variance)
        else:
            downside_std = 0.0
        
        if downside_std == 0:
            return 0.0
        
        daily_rf_rate = (1 + self.risk_free_rate) ** (1/periods_per_year) - 1
        
        sortino = (avg_return - daily_rf_rate) / downside_std * math.sqrt(periods_per_year)
        
        return sortino
    
    def _calculate_longest_streak(self, trades: List[Dict], 
                                 is_winning: bool = True) -> int:
        """
        Calculate longest win or loss streak
        
        Args:
            trades: List of trade dicts
            is_winning: True for win streak, False for loss streak
            
        Returns:
            Length of longest streak
        """
        if not trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            is_win = trade.get("p_l", 0) > 0
            
            if (is_winning and is_win) or (not is_winning and not is_win):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def compare_with_benchmark(self,
                              equity_values: List[float],
                              benchmark_returns: List[float]) -> Dict:
        """
        Compare strategy performance with benchmark
        
        Args:
            equity_values: Strategy equity curve
            benchmark_returns: Benchmark daily returns
            
        Returns:
            Comparison metrics
        """
        strategy_returns = self._calculate_returns(equity_values)
        
        # Strategy metrics
        strategy_total = (equity_values[-1] / self.initial_capital - 1) * 100 if equity_values else 0
        
        # Benchmark metrics
        benchmark_total = ((1 + sum(benchmark_returns) / len(benchmark_returns)) ** 
                          len(benchmark_returns) - 1) * 100 if benchmark_returns else 0
        
        # Excess return
        excess_return = strategy_total - benchmark_total
        
        # Correlation
        correlation = self._calculate_correlation(
            strategy_returns, benchmark_returns
        )
        
        # Alpha/Beta (simplified)
        beta = correlation if len(strategy_returns) > 0 else 0
        
        return {
            "strategy_return": strategy_total,
            "benchmark_return": benchmark_total,
            "excess_return": excess_return,
            "correlation": correlation,
            "beta": beta
        }
    
    def _calculate_correlation(self, series1: List[float], 
                              series2: List[float]) -> float:
        """Calculate correlation between two series"""
        if not series1 or not series2 or len(series1) < 2 or len(series2) < 2:
            return 0.0
        
        # Truncate to same length
        min_len = min(len(series1), len(series2))
        series1 = series1[:min_len]
        series2 = series2[:min_len]
        
        mean1 = sum(series1) / len(series1)
        mean2 = sum(series2) / len(series2)
        
        cov = sum((series1[i] - mean1) * (series2[i] - mean2) 
                 for i in range(len(series1))) / len(series1)
        
        std1 = math.sqrt(sum((x - mean1) ** 2 for x in series1) / len(series1))
        std2 = math.sqrt(sum((x - mean2) ** 2 for x in series2) / len(series2))
        
        if std1 * std2 == 0:
            return 0.0
        
        return cov / (std1 * std2)
    
    def calculate_monthly_returns(self, 
                                  timestamps: List[str],
                                  equity_values: List[float]) -> Dict[str, float]:
        """
        Calculate returns by month
        
        Args:
            timestamps: List of timestamps
            equity_values: List of equity values
            
        Returns:
            Dict of month -> return %
        """
        monthly_data = {}
        
        for i, timestamp in enumerate(timestamps):
            dt = datetime.fromisoformat(timestamp)
            month_key = dt.strftime("%Y-%m")
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "start_equity": equity_values[i],
                    "end_equity": equity_values[i]
                }
            else:
                monthly_data[month_key]["end_equity"] = equity_values[i]
        
        monthly_returns = {}
        for month, data in monthly_data.items():
            start = data["start_equity"]
            end = data["end_equity"]
            ret = (end - start) / start * 100 if start > 0 else 0
            monthly_returns[month] = ret
        
        return monthly_returns


def analyze_backtest_results(results_file: str) -> Dict:
    """
    Analyze backtest results from JSON file
    
    Args:
        results_file: Path to backtest results JSON
        
    Returns:
        Dict with analysis for all scenarios
    """
    
    with open(results_file, "r") as f:
        data = json.load(f)
    
    analysis = {}
    
    for scenario_name, scenario_data in data.get("scenarios", {}).items():
        analyzer = PerformanceAnalyzer()
        
        equity_values = [s.get("equity", 0) for s in scenario_data.get("state_history", [])]
        timestamps = [s.get("timestamp", "") for s in scenario_data.get("state_history", [])]
        trades = scenario_data.get("trades", [])
        
        # Calculate metrics
        metrics = analyzer.calculate_metrics(
            equity_values=equity_values,
            trades=trades,
            timestamps=timestamps,
            num_days=30
        )
        
        # Monthly returns
        monthly_returns = analyzer.calculate_monthly_returns(timestamps, equity_values)
        
        analysis[scenario_name] = {
            "metrics": metrics.to_dict(),
            "monthly_returns": monthly_returns
        }
    
    return analysis


def main():
    """Analyze backtest results"""
    
    results_file = "backtest_results/backtest_results.json"
    
    try:
        analysis = analyze_backtest_results(results_file)
        
        print(f"\n{'='*70}")
        print(f"PERFORMANCE ANALYSIS - ALL SCENARIOS")
        print(f"{'='*70}")
        
        for scenario, data in analysis.items():
            metrics = data["metrics"]
            
            print(f"\n{scenario.upper()}:")
            print(f"  Total Return: {metrics['total_return']:+.2f}%")
            print(f"  Annualized Return: {metrics['annualized_return']:+.2f}%")
            print(f"  Win Rate: {metrics['win_rate']:.1f}%")
            print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
            print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"  Trades: {metrics['num_trades']}")
        
        print(f"{'='*70}\n")
        
        # Save analysis
        with open("backtest_results/performance_analysis.json", "w") as f:
            # Convert to serializable format
            output = {}
            for scenario, data in analysis.items():
                output[scenario] = {
                    "metrics": data["metrics"],
                    "monthly_returns": data["monthly_returns"]
                }
            json.dump(output, f, indent=2)
        
        print("Analysis saved to backtest_results/performance_analysis.json")
        
    except FileNotFoundError:
        print(f"Error: {results_file} not found. Run backtest.py first.")


if __name__ == "__main__":
    main()
