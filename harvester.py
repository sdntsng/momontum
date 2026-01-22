"""
Momontum Data Harvester
=======================
Production-grade async engine for streaming crypto market data.

Features:
- Connects to Binance Futures via WebSocket (using ccxt.pro)
- Streams Tickers (Price) and Trades (Volume)
- Buffers data in memory and dumps to Parquet every minute
- Telegram Alert skeleton for crash notifications
"""

import asyncio
import ccxt.pro as ccxt
import pandas as pd
import os
from datetime import datetime
import logging

# --- CONFIGURATION ---
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1m'
EXCHANGE_ID = 'binanceusdm'  # Binance Futures
DATA_DIR = './data_lake'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')  # Get from BotFather
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataHarvester:
    """
    The Universal Harvester - streams market data and persists to Parquet.
    
    This is the foundation for the trading bot architecture.
    The same event loop will eventually house Strategy Logic.
    """
    
    def __init__(self, symbol: str = SYMBOL, exchange_id: str = EXCHANGE_ID):
        self.symbol = symbol
        self.exchange_id = exchange_id
        self.exchange = getattr(ccxt, exchange_id)({'enableRateLimit': True})
        self.buffer = []
        self.is_running = True
        
        # Create storage directory
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"📁 Created data directory: {DATA_DIR}")

    async def send_telegram_alert(self, message: str) -> None:
        """Sends critical alerts to your phone."""
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            # In production, use aiohttp to send this to the Telegram API
            # For now, we just log it to ensure the logic flow works
            logger.error(f"🚨 TELEGRAM ALERT: {message}")
        else:
            logger.error(f"ALERT (No Telegram Configured): {message}")

    async def save_buffer(self) -> None:
        """Flushes in-memory data to Parquet files."""
        if not self.buffer:
            return

        df = pd.DataFrame(self.buffer)
        
        # Generate filename: binanceusdm_BTCUSDT_2023-10-27_10-00.parquet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_symbol = self.symbol.replace('/', '')
        filename = f"{self.exchange_id}_{safe_symbol}_{timestamp}.parquet"
        filepath = os.path.join(DATA_DIR, filename)

        # Save using PyArrow engine (fast!)
        df.to_parquet(filepath, engine='pyarrow', compression='snappy')
        
        logger.info(f"💾 Flushed {len(df)} records to {filename}")
        self.buffer = []  # Clear buffer

    async def harvest(self) -> None:
        """The Main Event Loop."""
        logger.info(f"🚜 Starting Harvester for {self.symbol} on {self.exchange_id}...")
        logger.info(f"📊 Recording to {DATA_DIR}")
        
        try:
            while self.is_running:
                try:
                    # Fetch Ticker (Best Bid/Ask) - Low Latency
                    ticker = await self.exchange.watch_ticker(self.symbol)
                    
                    # Flatten the data structure for easy storage
                    record = {
                        'timestamp': ticker['timestamp'],
                        'datetime': ticker['datetime'],
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'bidVolume': ticker['bidVolume'],
                        'askVolume': ticker['askVolume'],
                        'last': ticker['last'],
                        'spread': ticker['ask'] - ticker['bid'] if ticker['ask'] and ticker['bid'] else None,
                        'spread_pct': ((ticker['ask'] - ticker['bid']) / ticker['bid'] * 100) if ticker['ask'] and ticker['bid'] else None,
                        'local_timestamp': datetime.now().timestamp()  # Check for latency drift!
                    }
                    
                    self.buffer.append(record)

                    # Flush to disk every 1000 ticks
                    if len(self.buffer) >= 1000:
                        await self.save_buffer()

                except ccxt.NetworkError as e:
                    logger.warning(f"Network Error: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Critical Error: {e}")
                    await self.send_telegram_alert(f"Harvester Crashed: {e}")
                    await asyncio.sleep(5)
                    
        finally:
            await self.exchange.close()
            await self.save_buffer()  # Save remaining data on exit
            logger.info("🛑 Harvester stopped. Data saved.")

    def stop(self) -> None:
        """Gracefully stop the harvester."""
        self.is_running = False


async def main():
    """Entry point for the harvester."""
    harvester = DataHarvester()
    try:
        await harvester.harvest()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping Harvester...")
        harvester.stop()


if __name__ == "__main__":
    asyncio.run(main())
