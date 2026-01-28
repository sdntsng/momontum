from typing import Dict, Any
from ..ledger import PaperLedger
from .runner import Strategy

class BuyAndHoldStrategy:
    """
    Simple strategy that buys on the first candle and holds.
    """
    def __init__(self):
        self.bought = False

    def on_candle(self, candle: Dict[str, Any], ledger: PaperLedger) -> None:
        if not self.bought:
            price = candle["close"]
            symbol = candle["symbol"]
            timestamp = candle["start_ts"]
            
            # Buy as much as possible with 99% of balance
            balance = ledger.get_balance()
            if balance > 10: # Minimum amount
                quantity = (balance * 0.99) / price
                ledger.place_order(symbol, price, quantity, "BUY", timestamp)
                self.bought = True

class GoldenCrossStrategy:
    """
    Simple SMA Crossover strategy.
    """
    def __init__(self, short_window: int = 50, long_window: int = 200):
        self.short_window = short_window
        self.long_window = long_window
        self.history = []
        self.position = 0 # 0: none, 1: long

    def on_candle(self, candle: Dict[str, Any], ledger: PaperLedger) -> None:
        price = candle["close"]
        symbol = candle["symbol"]
        timestamp = candle["start_ts"]
        
        self.history.append(price)
        
        if len(self.history) > self.long_window:
            self.history.pop(0)
            
        if len(self.history) >= self.long_window:
            short_ma = sum(self.history[-self.short_window:]) / self.short_window
            long_ma = sum(self.history[-self.long_window:]) / self.long_window
            
            if short_ma > long_ma and self.position == 0:
                # Buy
                balance = ledger.get_balance()
                if balance > 10:
                    quantity = (balance * 0.99) / price
                    ledger.place_order(symbol, price, quantity, "BUY", timestamp)
                    self.position = 1
                    
            elif short_ma < long_ma and self.position == 1:
                # Sell
                qty = ledger.get_position(symbol)
                if qty > 0:
                    ledger.place_order(symbol, price, qty, "SELL", timestamp)
                    self.position = 0
