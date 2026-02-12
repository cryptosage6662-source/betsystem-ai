"""
Optimized Strategy with Bear Market Reversal Trading
"""

from enum import Enum

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

class HybridTradingStrategy:
    """
    Hybrid strategy combining mean reversion and reversal trading
    """
    
    def __init__(self):
        self.price_history = []
        self.regime = MarketRegime.SIDEWAYS
        
        # Mean reversion params
        self.mr_buy_threshold = 0.40
        self.mr_sell_threshold = 0.60
        
        # Reversal trading params
        self.rv_profit_target = 0.05
        self.rv_stop_loss = 0.08
    
    def detect_regime(self):
        """Detect market regime from price history"""
        if len(self.price_history) < 20:
            return MarketRegime.SIDEWAYS
        
        trend = (self.price_history[-1] - self.price_history[-20]) / self.price_history[-20]
        
        volatility = sum(abs(self.price_history[i] - self.price_history[i-1]) 
                        for i in range(-5, 0)) / 5
        
        if trend < -0.05 and volatility > 0.02:
            return MarketRegime.BEAR
        elif trend > 0.05 and volatility > 0.02:
            return MarketRegime.VOLATILE
        elif trend > 0.02:
            return MarketRegime.BULL
        else:
            return MarketRegime.SIDEWAYS
    
    def get_entry_signal(self, current_price):
        """Generate entry signal based on regime"""
        
        if self.regime == MarketRegime.BULL or self.regime == MarketRegime.SIDEWAYS:
            # Mean reversion
            if current_price < self.mr_buy_threshold:
                return {
                    'signal': 'BUY',
                    'strategy': 'MEAN_REVERSION',
                    'price': current_price,
                    'reason': f'Price ${current_price:.2%} below threshold ${self.mr_buy_threshold:.2%}'
                }
        
        elif self.regime == MarketRegime.BEAR or self.regime == MarketRegime.VOLATILE:
            # Reversal trading
            if len(self.price_history) >= 10:
                m2 = (self.price_history[-1] - self.price_history[-2]) / self.price_history[-2]
                m10 = (self.price_history[-1] - self.price_history[-10]) / self.price_history[-10]
                
                if m2 > 0.01 and m10 < -0.02:
                    return {
                        'signal': 'BUY',
                        'strategy': 'REVERSAL',
                        'price': current_price,
                        'confidence': abs(m10) * 100,
                        'reason': f'Reversal setup detected (m2={m2:.2%}, m10={m10:.2%})'
                    }
        
        return None
    
    def get_exit_signal(self, entry_price, current_price):
        """Generate exit signal"""
        pnl = (current_price - entry_price) / entry_price
        
        if self.regime in [MarketRegime.BEAR, MarketRegime.VOLATILE]:
            # Reversal: tight targets and stops
            if pnl >= self.rv_profit_target:
                return {'signal': 'EXIT', 'reason': f'Quick profit +{pnl:.2%}'}
            if pnl <= -self.rv_stop_loss:
                return {'signal': 'EXIT', 'reason': f'Stop loss -{pnl:.2%}'}
        else:
            # Mean reversion: normal targets and stops
            if current_price >= self.mr_sell_threshold:
                return {'signal': 'EXIT', 'reason': f'Profit target +{pnl:.2%}'}
            if pnl <= -0.10:
                return {'signal': 'EXIT', 'reason': f'Stop loss -{pnl:.2%}'}
        
        return None
