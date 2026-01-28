import logging

logger = logging.getLogger(__name__)

class Signal:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class MomontumStrategy:
    """
    Momentum-based strategy using ML predictions.
    
    Logic:
    - If Predicted Price > Current Ask + Threshold -> BUY (Expect Upward Momentum)
    - If Predicted Price < Current Bid - Threshold -> SELL (Expect Downward Momentum)
    """
    def __init__(self, threshold=5.0):
        self.threshold = threshold  # Min expected profit in quote currency (USDT)
        
    def check_signal(self, current_record, prediction):
        """
        Evaluates prediction against current market state to generate a signal.
        """
        if not prediction:
            return Signal.HOLD
            
        pred_price = prediction['predicted_price']
        ask = current_record['ask']
        bid = current_record['bid']
        
        # Guard against bad data
        if not ask or not bid:
            return Signal.HOLD

        # Long Entry: We expect price to go higher than current Ask (plus buffer)
        # We buy at Ask, so we need Price > Ask + Threshold
        if pred_price > (ask + self.threshold):
            return Signal.BUY
            
        # Short Entry: We expect price to go lower than current Bid
        # We sell at Bid, so we need Price < Bid - Threshold
        if pred_price < (bid - self.threshold):
            return Signal.SELL
            
        return Signal.HOLD
