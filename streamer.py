"""
Momontum Data Harvester
=======================
Production-grade async engine for streaming crypto market data.

Features:
- Connects to Binance Futures via WebSocket (using ccxt.pro)
- Streams Tickers (Price) and Trades (Volume)
- Buffers data in memory and dumps to Parquet every minute
- Telegram Alert skeleton for crash notifications
- Multi-Asset Support via AssetManager
"""

import asyncio
import ccxt.pro as ccxt
import pandas as pd
import os
from datetime import datetime
import logging

import config
from data_lake.asset_manager import AssetManager
from processor import DataProcessor
from strategies.momentum import MomentumStrategy
from strategies.base import Signal
from trader import Trader

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataHarvester:
    """
    The Universal Harvester - streams market data and persists to Parquet.
    Supports multi-asset concurrent harvesting.
    """
    
    def __init__(self, basket_name: str = config.TARGET_BASKET, exchange_id: str = config.EXCHANGE_ID):
        self.basket_name = basket_name
        self.symbols = AssetManager.get_basket(basket_name)
        self.exchange_id = exchange_id
        
        logger.info(f"🧺 Initializing Harvester for Basket: {basket_name} ({len(self.symbols)} assets)")
        
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            },
        })
        
        # Buffers: { 'BTC/USDT': [records], 'ETH/USDT': [records] }
        self.buffers = {s: [] for s in self.symbols}
        self.is_running = True
        
        # Create storage directory
        if not os.path.exists(config.DATA_DIR):
            os.makedirs(config.DATA_DIR)
            logger.info(f"📁 Created data directory: {config.DATA_DIR}")
            
        # Initialize Brains & Strategies (One per symbol to maintain state)
        self.processors = {s: DataProcessor() for s in self.symbols}
        self.strategies = {s: MomentumStrategy(threshold=5.0) for s in self.symbols}
        
        # Shared Trader (Execution Layer)
        self.trader = Trader(self.exchange, dry_run=True)

    async def send_telegram_alert(self, message: str) -> None:
        """Sends critical alerts to your phone."""
        if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID:
            logger.error(f"🚨 TELEGRAM ALERT: {message}")
        else:
            logger.error(f"ALERT (No Telegram Configured): {message}")

    async def save_buffer(self, symbol: str) -> None:
        """Flushes strictly the buffer for the given symbol."""
        buffer = self.buffers.get(symbol, [])
        if not buffer:
            return

        df = pd.DataFrame(buffer)
        
        # Generate filename: binanceusdm_BTCUSDT_2023-10-27_10-00.parquet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_symbol = symbol.replace('/', '')
        filename = f"{self.exchange_id}_{safe_symbol}_{timestamp}.parquet"
        filepath = os.path.join(config.DATA_DIR, filename)

        # Save using PyArrow engine
        df.to_parquet(filepath, engine='pyarrow', compression='snappy')
        
        logger.info(f"💾 {symbol}: Flushed {len(df)} records to {filename}")
        self.buffers[symbol] = []  # Clear specific buffer

    async def harvest_symbol(self, symbol: str) -> None:
        """Async task to harvest a single symbol."""
        logger.info(f"🚜 Started harvesting {symbol}...")
        
        try:
            while self.is_running:
                try:
                    # Fetch Order Book (L1) - Real-time BBO
                    orderbook = await self.exchange.watch_order_book(symbol, limit=5)
                    
                    bid = orderbook['bids'][0][0] if orderbook['bids'] else None
                    ask = orderbook['asks'][0][0] if orderbook['asks'] else None
                    bid_vol = orderbook['bids'][0][1] if orderbook['bids'] else None
                    ask_vol = orderbook['asks'][0][1] if orderbook['asks'] else None

                    # Flatten the data structure
                    record = {
                        'symbol': symbol, # Add symbol to record
                        'timestamp': orderbook['timestamp'],
                        'datetime': orderbook['datetime'],
                        'bid': bid,
                        'ask': ask,
                        'bidVolume': bid_vol,
                        'askVolume': ask_vol,
                        'last': None, 
                        'spread': ask - bid if ask and bid else None,
                        'spread_pct': ((ask - bid) / bid * 100) if ask and bid else None,
                        'local_timestamp': datetime.now().timestamp()
                    }
                    
                    self.buffers[symbol].append(record)
                    
                    # PROCESS: Feed to The Brain
                    processor = self.processors[symbol]
                    prediction = processor.process(record)
                    
                    if prediction:
                        # Log less frequently for multi-asset to avoid spam
                        # logger.info(f"[{symbol}] 🔮 Pred: {prediction['predicted_price']:.2f}")
                        
                        # SIGNAL GENERATION
                        strategy = self.strategies[symbol]
                        signal = strategy.on_tick(record, prediction)
                        
                        if signal != Signal.HOLD:
                            mid_price = (bid + ask) / 2 if bid and ask else 0
                            # EXECUTION with Symbol
                            await self.trader.execute_trade(symbol, signal, current_price=mid_price)

                    # Flush to disk every N ticks
                    if len(self.buffers[symbol]) >= config.BUFFER_SIZE:
                        await self.save_buffer(symbol)

                except ccxt.NetworkError as e:
                    logger.warning(f"[{symbol}] Network Error: {e}. Reconnecting...")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"[{symbol}] Critical Loop Error: {e}")
                    await asyncio.sleep(5)
        except Exception as e:
             logger.error(f"[{symbol}] Failed to start harvest loop: {e}")

    async def harvest(self) -> None:
        """The Main Event Loop - Spawns tasks for all symbols."""
        logger.info(f"🚜 Starting Multi-Asset Harvester for {len(self.symbols)} assets on {self.exchange_id}...")
        
        await self.exchange.load_markets()
        
        # Create a task for each symbol
        tasks = [asyncio.create_task(self.harvest_symbol(symbol)) for symbol in self.symbols]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Main Loop Crash: {e}")
        finally:
            await self.exchange.close()
            # Save all remaining buffers
            for symbol in self.symbols:
                await self.save_buffer(symbol)
            logger.info("🛑 Harvester stopped. All data saved.")

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
