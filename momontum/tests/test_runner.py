import pytest
from unittest.mock import MagicMock, patch
import polars as pl
from pathlib import Path
from momontum.backtest.runner import BacktestRunner
from momontum.ledger import PaperLedger

def test_runner_execution():
    # Mock strategy
    strategy = MagicMock()
    ledger = PaperLedger()
    
    # Create a dummy DataFrame
    data = {
        "symbol": ["AAPL", "AAPL"],
        "start_ts": [1000, 2000],
        "close": [100.0, 101.0],
        "open": [100.0, 101.0],
        "high": [100.0, 101.0],
        "low": [100.0, 101.0],
        "n_ticks": [1, 1],
        "interval": ["1min", "1min"],
        "end_ts": [1999, 2999]
    }
    df = pl.DataFrame(data)
    
    # Patch polars.read_parquet
    with patch("polars.read_parquet", return_value=df) as mock_read:
        # Patch Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            runner = BacktestRunner("dummy.parquet", strategy, ledger)
            runner.run()
            
            mock_read.assert_called()
            assert strategy.on_candle.call_count == 2
            
            # Verify call arguments
            # strategy.on_candle(candle_dict, ledger)
            calls = strategy.on_candle.call_args_list
            assert calls[0][0][0]["start_ts"] == 1000
            assert calls[1][0][0]["start_ts"] == 2000
