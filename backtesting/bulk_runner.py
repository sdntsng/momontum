import sys
import os
import glob
import polars as pl
import logging
from prettytable import PrettyTable

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor import DataProcessor
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.base import Signal
import config

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("BulkRunner")

def load_data():
    files = glob.glob(os.path.join(config.DATA_DIR, "*.parquet"))
    if not files:
        logger.error("No data found.")
        return None
    df = pl.read_parquet(os.path.join(config.DATA_DIR, "*.parquet"))
    return df.sort("timestamp")

def run_strategy(strategy, records, processor=None):
    """Runs a single strategy over the records and returns metrics."""
    position = None 
    entry_price = 0
    pnl = 0
    trades = 0
    
    # Reset processor for each run if it has state
    # (Our specific processor implementation in this repo is stateful)
    local_processor = DataProcessor() if processor else None

    for record in records:
        prediction = None
        if local_processor:
            prediction = local_processor.process(record)
            
        signal = strategy.on_tick(record, prediction)
        
        # Execution (Simulated)
        mid_price = (
            (record["bid"] + record["ask"]) / 2
            if record["bid"] and record["ask"]
            else record["last"]
        )
        if not mid_price:
            continue

        if position is None:
            if signal == Signal.BUY:
                position = 'LONG'
                entry_price = record['ask']
                trades += 1
            elif signal == Signal.SELL:
                position = 'SHORT'
                entry_price = record['bid']
                trades += 1
                
        elif position == 'LONG':
            if signal == Signal.SELL:
                pnl += (record['bid'] - entry_price)
                position = None
                
        elif position == 'SHORT':
            if signal == Signal.BUY:
                pnl += (entry_price - record['ask'])
                position = None

    return {
        "Strategy": strategy.name,
        "Total PnL": f"{pnl:.2f}",
        "Trades": trades,
        "Avg PnL": f"{pnl/trades:.2f}" if trades > 0 else "0.00"
    }

def main():
    df = load_data()
    if df is None:
        return
    
    # Ensure symbol column exists (handle legacy data)
    if 'symbol' not in df.columns:
        logger.warning("Old data detected (no symbol column). Treating as single asset.")
        df = df.with_columns(pl.lit("LEGACY").alias("symbol"))
    
    symbols = df['symbol'].unique().to_list()
    logger.info(f"Loaded {len(df)} ticks across {len(symbols)} assets: {symbols}")
    
    # Define Strategies to Test
    strategies = [
        MomentumStrategy(threshold=1.0),
        MomentumStrategy(threshold=5.0), # Stricter
        MeanReversionStrategy(window=20, std_dev_mult=2.0),
    ]
    
    results = []
    
    logger.info("🚀 Starting Bulk Backtest...")
    
    for symbol in symbols:
        symbol_df = df.filter(pl.col('symbol') == symbol)
        symbol_records = symbol_df.to_dicts()
        
        logger.info(f"\n--- Testing on {symbol} ({len(symbol_records)} ticks) ---")
        
        for strat in strategies:
            # Determine if strategy needs ML Processor
            processor = True if isinstance(strat, MomentumStrategy) else False
            
            # Run
            metrics = run_strategy(strat, symbol_records, processor=processor)
            metrics['Symbol'] = symbol # Tag result
            results.append(metrics)

    # Display Report
    table = PrettyTable()
    table.field_names = ["Symbol", "Strategy", "Total PnL", "Trades"]
    
    for res in results:
        table.add_row([res["Symbol"], res["Strategy"], res["Total PnL"], res["Trades"]])
        
    print("\n")
    print(table)

if __name__ == "__main__":
    main()
