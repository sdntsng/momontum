from .base import BaseStrategy, Signal

class MomentumStrategy(BaseStrategy):
    """
    Momentum-based strategy using ML predictions.
    
    Logic:
    - If Predicted Price > Current Ask + Threshold -> BUY (Expect Upward Momentum)
    - If Predicted Price < Current Bid - Threshold -> SELL (Expect Downward Momentum)
    """
    def __init__(self, threshold=5.0):
        super().__init__("MomentumML")
        self.threshold = threshold
        
    def on_tick(self, record: dict, prediction: dict = None) -> str:
        if not prediction:
            return Signal.HOLD
            
        pred_price = prediction['predicted_price']
        ask = record['ask']
        bid = record['bid']
        
        # Guard against bad data
        if not ask or not bid:
            return Signal.HOLD

        # Long Entry
        if pred_price > (ask + self.threshold):
            return Signal.BUY
            
        # Short Entry
        if pred_price < (bid - self.threshold):
            return Signal.SELL
            
        return Signal.HOLD
