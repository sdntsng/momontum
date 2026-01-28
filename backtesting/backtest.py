import sys
import os
import glob
import polars as pl
import logging

# Add parent directory to path so we can import internal modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor import DataProcessor
from strategy import MomontumStrategy, Signal
import config

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Backtester")

def load_data():
    """Loads and sorts all parquet data."""
    files = glob.glob(os.path.join(config.DATA_DIR, "*.parquet"))
    if not files:
        logger.error("No data found in data_lake")
        return None
        
    logger.info(f"Loading {len(files)} files...")
    # Polars is fast
    df = pl.read_parquet(os.path.join(config.DATA_DIR, "*.parquet"))
    df = df.sort("timestamp")
    return df

def run_backtest():
    df = load_data()
    if df is None:
        return

    logger.info(f"Running backtest on {len(df)} ticks...")
    
    processor = DataProcessor()
    strategy = MomontumStrategy(threshold=1.0) # Lower threshold for testing?
    
    trades = []
    position = None # None, 'LONG', 'SHORT'
    entry_price = 0
    pnl = 0
    
    # Iterate through ticks (using to_dicts for simplicity, though slower than pure polars ops)
    # For River (online learning), we MUST iterate row by row.
    records = df.to_dicts()
    
    for i, record in enumerate(records):
        # 1. Process
        prediction = processor.process(record)
        
        # 2. Strategy
        signal = strategy.check_signal(record, prediction)
        
        # 3. Execution Simulation
        if position is None:
            if signal == Signal.BUY:
                position = 'LONG'
                entry_price = record['ask'] # Buy at Ask
                logger.info(f"[{i}] OPEN LONG @ {entry_price}")
            elif signal == Signal.SELL:
                position = 'SHORT'
                entry_price = record['bid'] # Sell at Bid
                logger.info(f"[{i}] OPEN SHORT @ {entry_price}")
                
        elif position == 'LONG':
            # Simple Exit Logic: If signal flips or Stop Loss / Take Profit
            # For now: Exit if we get a SELL signal
            if signal == Signal.SELL:
                exit_price = record['bid']
                trade_pnl = exit_price - entry_price
                pnl += trade_pnl
                logger.info(f"[{i}] CLOSE LONG @ {exit_price} | PnL: {trade_pnl:.2f}")
                position = None
                trades.append(trade_pnl)
                
        elif position == 'SHORT':
            if signal == Signal.BUY:
                exit_price = record['ask']
                trade_pnl = entry_price - exit_price # Short PnL
                pnl += trade_pnl
                logger.info(f"[{i}] CLOSE SHORT @ {exit_price} | PnL: {trade_pnl:.2f}")
                position = None
                trades.append(trade_pnl)

    logger.info(f"Backtest Complete. Total PnL: {pnl:.2f} USDT")
    logger.info(f"Total Trades: {len(trades)}")

if __name__ == "__main__":
    run_backtest()
