from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Trade:
    symbol: str
    side: str  # "BUY" or "SELL"
    price: float
    quantity: float
    timestamp: int
    fee: float = 0.0
    pnl: float = 0.0  # Realized PnL for closing trades


class PaperLedger:
    """
    In-memory ledger for paper trading and backtesting.
    Tracks cash balance and positions.
    """

    def __init__(self, initial_capital: float = 10000.0, fee_rate: float = 0.0):
        self.initial_capital = initial_capital
        self.balance = initial_capital
        self.fee_rate = fee_rate
        
        # symbol -> signed quantity (positive=long, negative=short)
        self.positions: Dict[str, float] = {}
        
        # symbol -> average entry price
        self.avg_prices: Dict[str, float] = {}
        
        self.trades: List[Trade] = []

    def get_balance(self) -> float:
        return self.balance

    def get_position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)

    def get_avg_price(self, symbol: str) -> float:
        return self.avg_prices.get(symbol, 0.0)

    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """Calculate total equity (balance + unrealized PnL)."""
        equity = self.balance
        for symbol, qty in self.positions.items():
            if qty == 0:
                continue
            current_price = current_prices.get(symbol)
            if current_price is None:
                # Fallback to avg price if current not available (no change in value)
                current_price = self.avg_prices.get(symbol, 0.0)
            
            # Equity = Cash Balance + Market Value of Positions
            equity += (qty * current_price)
            
        return equity

    def place_order(self, symbol: str, price: float, quantity: float, side: str, timestamp: int) -> Trade:
        """
        Execute a trade (market order assumed filled immediately at 'price').
        Updates balance and positions.
        """
        # quantity is always positive in input
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        cost = price * quantity
        fee = cost * self.fee_rate
        
        self.balance -= fee
        
        if side == "BUY":
            self.balance -= cost
            signed_qty = quantity
        elif side == "SELL":
            self.balance += cost
            signed_qty = -quantity
        else:
            raise ValueError(f"Invalid side: {side}")
            
        current_qty = self.positions.get(symbol, 0.0)
        current_avg = self.avg_prices.get(symbol, 0.0)
        
        # Update Average Price Logic (Weighted Average)
        # Only update average price if increasing position size
        # If reducing, average price stays same.
        # If flipping, the new average is the entry price of the new leg.
        
        new_qty = current_qty + signed_qty
        
        # Check if we are increasing position in the same direction
        if (current_qty >= 0 and signed_qty > 0) or (current_qty <= 0 and signed_qty < 0):
            # Increasing
            total_cost = (abs(current_qty) * current_avg) + (abs(signed_qty) * price)
            total_qty = abs(new_qty)
            if total_qty > 0:
                self.avg_prices[symbol] = total_cost / total_qty
        
        elif (current_qty > 0 and new_qty < 0) or (current_qty < 0 and new_qty > 0):
            # Flipping position
            # The part that closed the old position uses old avg (implicitly for PnL calc)
            # The new part uses new price
            self.avg_prices[symbol] = price
            
        elif new_qty == 0:
            self.avg_prices[symbol] = 0.0
            
        # Else: reducing position, avg price unchanged
        
        self.positions[symbol] = new_qty

        # Calculate Realized PnL for reporting
        realized_pnl = 0.0
        if (current_qty > 0 and signed_qty < 0) or (current_qty < 0 and signed_qty > 0):
            # We closed some amount
            qty_closed = min(abs(current_qty), abs(signed_qty))
            # PnL = (Exit - Entry) * Qty * Direction
            # If Long (current > 0), Exit=Price, Entry=Avg, Dir=1
            # If Short (current < 0), Exit=Price, Entry=Avg, Dir=-1
            # Wait, Short: Entry=100. Exit=90. Profit 10.
            # (90 - 100) * -1 = -10 * -1 = 10. Correct.
            direction = 1 if current_qty > 0 else -1
            realized_pnl = (price - current_avg) * qty_closed * direction
            # Note: This realized_pnl is NOT added to balance here because balance was already updated by cash flow.
            # We just track it for reporting.

        trade = Trade(
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            timestamp=timestamp,
            fee=fee,
            pnl=realized_pnl
        )
        self.trades.append(trade)
        return trade
