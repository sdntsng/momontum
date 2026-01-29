import os
import sys

import polars as pl
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent dir to path to import internal modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtesting.bulk_runner import load_data, run_strategy
from data_lake.asset_manager import AssetManager
from strategies.base import BaseStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy

app = FastAPI(title="Momontum API")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BacktestRequest(BaseModel):
    strategy: str
    basket: list[str]
    params: dict = {}


@app.get("/strategies")
def get_strategies():
    return [
        {"id": "momentum", "name": "Momentum ML", "params": {"threshold": 5.0}},
        {
            "id": "mean_reversion",
            "name": "Mean Reversion",
            "params": {"window": 20, "std_dev_mult": 2.0},
        },
    ]


@app.get("/assets")
def get_assets():
    return {
        "baskets": {
            "TOP_3": AssetManager.TOP_3,
            "TOP_10": AssetManager.TOP_10,
            "MEME": AssetManager.MEME_BASKET,
            "BTC": AssetManager.BTC,
            "ETH": AssetManager.ETH,
        }
    }


@app.post("/backtest")
def run_backtest_api(req: BacktestRequest):
    df = load_data()
    if df is None:
        raise HTTPException(status_code=404, detail="No data found")

    results = []

    strat: BaseStrategy

    # 1. Select Strategy
    if req.strategy == "momentum":
        strat = MomentumStrategy(threshold=req.params.get("threshold", 5.0))
        processor_needed = True
    elif req.strategy == "mean_reversion":
        strat = MeanReversionStrategy(
            window=req.params.get("window", 20), std_dev_mult=req.params.get("std_dev_mult", 2.0)
        )
        processor_needed = False
    else:
        raise HTTPException(status_code=400, detail="Unknown strategy")

    # 2. Filter Data by Basket

    # Check if 'symbol' column exists
    if "symbol" not in df.columns:
        pass

    for symbol in req.basket:
        # Filter for specific symbol
        symbol_df = df.filter(pl.col("symbol") == symbol)
        records = symbol_df.to_dicts()

        if not records:
            continue

        metrics = run_strategy(strat, records, processor=processor_needed)
        metrics["symbol"] = symbol

        results.append(metrics)

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
