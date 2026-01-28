import asyncio
import glob
import pandas as pd
from harvester import DataHarvester
import logging

# Mute logs for checking
logging.getLogger().setLevel(logging.INFO)

async def run_verification():
    print("🧪 Starting Phase 6 Verification (Multi-Asset)...")
    
    # Initialize Harvester with TOP_3 (BTC, ETH, SOL)
    harvester = DataHarvester(basket_name='TOP_3')
    
    # Run for 15 seconds
    task = asyncio.create_task(harvester.harvest())
    
    print("⏳ Running Harvester for 15 seconds...")
    await asyncio.sleep(15)
    
    print("🛑 Stopping Harvester...")
    harvester.stop()
    await task # Wait for cleanup
    
    print("✅ Harvester Stopped.")
    
    # Check Data
    files = glob.glob("data_lake/*.parquet")
    print(f"📂 Found {len(files)} parquet files.")
    
    if not files:
        print("❌ FAILED: No data files created.")
        return

    # Check content of first file
    df = pd.read_parquet(files[0])
    print("\n📄 Sample Data (First File):")
    print(df.columns)
    print(df.head(1))
    
    if 'symbol' in df.columns:
        unique_symbols = []
        for f in files:
            d = pd.read_parquet(f)
            unique_symbols.extend(d['symbol'].unique().tolist())
        
        unique_symbols = list(set(unique_symbols))
        print(f"\n✅ SUCCESS: Captured data for symbols: {unique_symbols}")
    else:
        print("\n❌ FAILED: 'symbol' column missing in parquet.")

if __name__ == "__main__":
    asyncio.run(run_verification())
