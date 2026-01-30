import ccxt
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configuration
DATA_DIR = './data_lake'
SYMBOLS = ['BTC/USDT', 'ETH/USDT']
TIMEFRAMES = ['1h', '4h']
DAYS_BACK = 365

def fetch_data(symbol, timeframe, days):
    print(f"Fetching {symbol} {timeframe} data for last {days} days...")
    
    # Initialize exchange (public data only, no keys needed)
    exchange = ccxt.binance({
        'enableRateLimit': True
    })
    
    # Calculate start time
    now = exchange.milliseconds()
    since = now - (days * 24 * 60 * 60 * 1000)
    
    all_candles = []
    
    while since < now:
        try:
            # Fetch candles
            candles = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
            
            if not candles:
                break
                
            # Update 'since' to the last timestamp + 1 timeframe duration
            # But simplest is just taking the last timestamp + 1ms to avoid overlap/dupes if the API behaves nicely
            # Or use the last candle's time + 1 unit.
            # Safe way: use the last candle timestamp + 1 to move forward
            last_timestamp = candles[-1][0]
            since = last_timestamp + 1
            
            all_candles.extend(candles)
            print(f"  Fetched {len(candles)} candles, total: {len(all_candles)} (Latest: {datetime.fromtimestamp(last_timestamp/1000)})")
            
            # Rate limit handling is automatic with enableRateLimit=True, but strictly:
            # time.sleep(exchange.rateLimit / 1000)
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            break

    # Convert to DataFrame
    df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Drop duplicates if any
    df = df.drop_duplicates(subset=['timestamp'])
    
    # Save to CSV
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    safe_symbol = symbol.replace('/', '')
    filename = f"{DATA_DIR}/{safe_symbol}_{timeframe}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")

def main():
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            fetch_data(symbol, tf, DAYS_BACK)

if __name__ == "__main__":
    main()
