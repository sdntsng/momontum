import polars as pl
import logging
from typing import Protocol, Dict, Any, Optional
from pathlib import Path

from ..ledger import PaperLedger

logger = logging.getLogger(__name__)

class Strategy(Protocol):
    def on_candle(self, candle: Dict[str, Any], ledger: PaperLedger) -> None:
        """
        Process a single candle and update the ledger (place orders) if needed.
        
        Args:
            candle: Dictionary containing candle data (open, high, low, close, start_ts, etc.)
            ledger: The PaperLedger instance to execute trades against.
        """
        ...

class BacktestRunner:
    def __init__(self, data_path: str | Path, strategy: Strategy, ledger: PaperLedger):
        self.data_path = Path(data_path)
        self.strategy = strategy
        self.ledger = ledger

    def run(self) -> PaperLedger:
        logger.info(f"Starting backtest on {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {self.data_path}")

        # Load data using Polars
        # specific to the schema in momontum/schemas.py (CANDLES_SCHEMA_V1)
        # Expected cols: symbol, interval, start_ts, end_ts, open, high, low, close, n_ticks
        
        try:
            df = pl.read_parquet(self.data_path)
        except Exception as e:
            logger.error(f"Failed to read parquet: {e}")
            raise

        if df.is_empty():
            logger.warning("Parquet file is empty.")
            return self.ledger

        # Sort by timestamp to ensure chronological order
        if "start_ts" in df.columns:
            df = df.sort("start_ts")
        
        logger.info(f"Loaded {len(df)} candles.")

        # Iterate through candles
        # Using iter_rows(named=True) creates a dict for each row
        count = 0
        for candle in df.iter_rows(named=True):
            self.strategy.on_candle(candle, self.ledger)
            count += 1
            
        logger.info(f"Backtest completed. Processed {count} candles.")
        logger.info(f"Final Balance: {self.ledger.get_balance():.2f}")
        
        # Calculate final equity using the last close price
        last_close = df["close"][-1]
        last_symbol = df["symbol"][0] # Assuming single symbol per file for now
        
        equity = self.ledger.get_equity({last_symbol: last_close})
        logger.info(f"Final Equity: {equity:.2f}")

        return self.ledger
