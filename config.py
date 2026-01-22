import os
from dotenv import load_dotenv

load_dotenv()

# Trading Settings
# Defines which basket of coins to trade. Options: 'BTC', 'ETH', 'TOP_3', 'TOP_10', 'MEME_BASKET'
TARGET_BASKET = 'BTC' 
TIMEFRAME = '1m'
EXCHANGE_ID = 'binanceusdm'  # Binance Futures

# Data Settings
DATA_DIR = './data_lake'
BUFFER_SIZE = 50  # Flush every 50 ticks (Low for testing, increase for prod)

# Alerting
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Exchange Keys (Required for Execution)
API_KEY = os.getenv('BINANCE_API_KEY', '')
API_SECRET = os.getenv('BINANCE_API_SECRET', '')
