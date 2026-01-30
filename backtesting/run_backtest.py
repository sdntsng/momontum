import pandas as pd
import os
import glob

DATA_DIR = '../data_lake' # Relative to backtesting/

def load_data(symbol, timeframe):
    path = os.path.join(DATA_DIR, f"{symbol.replace('/', '')}_{timeframe}.csv")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return None
    return pd.read_csv(path)

def backtest_strategy(df, symbol, initial_capital=1000, fee_pct=0.001):
    # Calculate Indicators
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['SMA_200'] = df['close'].rolling(window=200).mean()
    
    position = 0 # 0: flat, 1: long
    cash = initial_capital
    holdings = 0
    trades = 0
    
    # We need previous row values, so we iterate
    # A vectorized approach is faster but iteration is clearer for logic
    
    print(f"\n--- Backtesting {symbol} ---")
    
    for i in range(200, len(df)):
        # Current and Previous values
        curr_fast = df.iloc[i]['SMA_50']
        curr_slow = df.iloc[i]['SMA_200']
        prev_fast = df.iloc[i-1]['SMA_50']
        prev_slow = df.iloc[i-1]['SMA_200']
        price = df.iloc[i]['close']
        timestamp = df.iloc[i]['datetime']
        
        # Crossover Logic
        crossover_up = (prev_fast <= prev_slow) and (curr_fast > curr_slow)
        crossover_down = (prev_fast >= prev_slow) and (curr_fast < curr_slow)
        
        if position == 0 and crossover_up:
            # Buy
            holdings = cash / price * (1 - fee_pct)
            cash = 0
            position = 1
            trades += 1
            # print(f"[{timestamp}] BUY @ {price:.2f}")
            
        elif position == 1 and crossover_down:
            # Sell
            cash = holdings * price * (1 - fee_pct)
            holdings = 0
            position = 0
            trades += 1
            # print(f"[{timestamp}] SELL @ {price:.2f}")

    # Mark to market final value
    final_value = cash
    if position == 1:
        final_value = holdings * df.iloc[-1]['close']
        
    pnl = final_value - initial_capital
    pnl_pct = (pnl / initial_capital) * 100
    
    print(f"Initial Capital: ${initial_capital}")
    print(f"Final Value:     ${final_value:.2f}")
    print(f"PnL:             ${pnl:.2f} ({pnl_pct:.2f}%)")
    print(f"Total Trades:    {trades}")
    
    return final_value

def main():
    # Test on generated files
    symbols = ['BTC/USDT', 'ETH/USDT']
    timeframes = ['1h', '4h']
    
    for symbol in symbols:
        for tf in timeframes:
            df = load_data(symbol, tf)
            if df is not None:
                print(f"\nRunning {symbol} on {tf} timeframe...")
                backtest_strategy(df, symbol)

if __name__ == "__main__":
    main()
