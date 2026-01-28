import pytest
from momontum.ledger import PaperLedger

def test_ledger_initialization():
    ledger = PaperLedger(initial_capital=1000.0)
    assert ledger.balance == 1000.0
    assert ledger.positions == {}

def test_ledger_buy():
    ledger = PaperLedger(initial_capital=1000.0)
    # Buy 1 unit at 100
    ledger.place_order("AAPL", 100.0, 1.0, "BUY", 123456789)
    
    # Balance = 1000 - 100 = 900
    assert ledger.balance == 900.0
    assert ledger.get_position("AAPL") == 1.0
    assert ledger.get_avg_price("AAPL") == 100.0

def test_ledger_buy_sell_profit():
    ledger = PaperLedger(initial_capital=1000.0)
    # Buy 1 @ 100
    ledger.place_order("AAPL", 100.0, 1.0, "BUY", 1) 
    assert ledger.balance == 900.0
    
    # Sell 1 @ 110 (Revenue 110, Profit 10)
    trade = ledger.place_order("AAPL", 110.0, 1.0, "SELL", 2)
    
    # Balance = 900 + 110 = 1010
    assert ledger.balance == 1010.0
    assert ledger.get_position("AAPL") == 0.0
    assert trade.pnl == 10.0

def test_ledger_short_cover_profit():
    ledger = PaperLedger(initial_capital=1000.0)
    # Sell 1 @ 100 (Short)
    ledger.place_order("AAPL", 100.0, 1.0, "SELL", 1)
    
    # Balance = 1000 + 100 = 1100
    assert ledger.balance == 1100.0
    assert ledger.get_position("AAPL") == -1.0
    assert ledger.get_avg_price("AAPL") == 100.0
    
    # Buy 1 @ 90 (Cover)
    trade = ledger.place_order("AAPL", 90.0, 1.0, "BUY", 2)
    
    # Balance = 1100 - 90 = 1010
    assert ledger.balance == 1010.0
    assert ledger.get_position("AAPL") == 0.0
    assert trade.pnl == 10.0

def test_ledger_avg_price():
    ledger = PaperLedger(initial_capital=2000.0)
    # Buy 1 @ 100
    ledger.place_order("AAPL", 100.0, 1.0, "BUY", 1)
    assert ledger.get_avg_price("AAPL") == 100.0
    
    # Buy 1 @ 200
    ledger.place_order("AAPL", 200.0, 1.0, "BUY", 2)
    # Total Cost = 300, Qty = 2, Avg = 150
    assert ledger.get_avg_price("AAPL") == 150.0
    assert ledger.get_position("AAPL") == 2.0
    
    # Sell 1 @ 150 (Break even per unit)
    trade = ledger.place_order("AAPL", 150.0, 1.0, "SELL", 3)
    assert trade.pnl == 0.0
    assert ledger.get_position("AAPL") == 1.0
    assert ledger.get_avg_price("AAPL") == 150.0 # Avg price shouldn't change on reduction

def test_equity_calc():
    ledger = PaperLedger(initial_capital=1000.0)
    # Buy 1 @ 100
    ledger.place_order("AAPL", 100.0, 1.0, "BUY", 1)
    # Balance 900, Pos 1
    
    # Price rises to 120
    equity = ledger.get_equity({"AAPL": 120.0})
    # Equity = 900 + (1 * 120) = 1020
    assert equity == 1020.0
