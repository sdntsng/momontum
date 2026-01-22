import numpy as np
from .base import BaseStrategy, Signal

class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy.
    
    Logic:
    - Calculates moving average of the spread.
    - If spread > MA + 2*StdDev -> Expect spread to close -> Signal based on direction.
    - Simplified Data Lake version: 
      - If current price is significantly deviation from VWAP/MA -> Bet on return to mean.
    
    For this implementation, let's use a dynamic window on 'last' price or 'mid' price.
    """
    def __init__(self, window=20, std_dev_mult=2.0):
        super().__init__("MeanReversion")
        self.window = window
        self.mult = std_dev_mult
        self.prices = []
        
    def on_tick(self, record: dict, prediction: dict = None) -> str:
        # Use mid price if last is unavailable
        price = record['last'] if record['last'] else (record['bid'] + record['ask']) / 2
        if not price:
            return Signal.HOLD
            
        self.prices.append(price)
        if len(self.prices) > self.window:
            self.prices.pop(0)
            
        if len(self.prices) < self.window:
            return Signal.HOLD
            
        # Calculate Bollinger Bands
        ma = np.mean(self.prices)
        std = np.std(self.prices)
        upper = ma + (std * self.mult)
        lower = ma - (std * self.mult)
        
        # Mean Reversion Logic
        # Price high -> Sell
        if price > upper:
            return Signal.SELL
        # Price low -> Buy
        elif price < lower:
            return Signal.BUY
            
        return Signal.HOLD
