<p align="center">
  <img src="assets/logo.png" alt="Momontum Logo" width="200"/>
</p>

<h1 align="center">Momontum</h1>
<p align="center"><em>Momentum-based crypto trading data harvester</em></p>

---

## 🍑 Overview

Momontum is a **production-grade async engine** for streaming and storing cryptocurrency market data. Built for solo practitioners who want to build their own proprietary datasets.

### Core Architecture

| Component | Description |
|-----------|-------------|
| **The Brain** | Strategy module with Online ML support (River) |
| **The Nervous System** | Telegram alerts for real-time monitoring |
| **The Data Lake** | Parquet-based storage optimized for Polars |

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/momontum.git
cd momontum

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Telegram credentials (optional)

# Start harvesting
python harvester.py
```

## 📊 The Harvester

The `harvester.py` script:

1. Connects to **Binance Futures** via WebSocket (using `ccxt.pro`)
2. Streams **Tickers** (bid/ask/spread) in real-time
3. Records both exchange timestamp and local timestamp (for latency analysis)
4. Buffers data in memory, flushes to **Parquet** every 1000 ticks
5. Sends **Telegram alerts** on crashes

### Data Schema

| Field | Description |
|-------|-------------|
| `timestamp` | Exchange timestamp (ms) |
| `datetime` | ISO format datetime |
| `bid` / `ask` | Best bid/ask prices |
| `bidVolume` / `askVolume` | Volume at best bid/ask |
| `last` | Last traded price |
| `spread` | Absolute spread (ask - bid) |
| `spread_pct` | Spread as percentage |
| `local_timestamp` | Your machine time (for latency drift) |

## 🔮 Roadmap

- [x] **Phase 1**: Data Harvester (WebSocket → Parquet)
- [ ] **Phase 2**: Online ML with River (Kalman Filter, Linear Regression)
- [ ] **Phase 3**: Strategy Backtesting with Polars
- [ ] **Phase 4**: Live Trading Execution

## 🛠 Tech Stack

- **ccxt.pro** - Async exchange connectivity
- **Polars** - Lightning-fast DataFrames
- **PyArrow** - Parquet I/O
- **River** - Online/incremental machine learning
- **Telegram** - Real-time alerting

## 📁 Project Structure

```
momontum/
├── assets/
│   └── logo.png
├── data_lake/          # Generated: Parquet files
├── harvester.py        # Main data harvester
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 📝 License

MIT

---

<p align="center">
  <em>Built for builders who trade 🚀</em>
</p>
