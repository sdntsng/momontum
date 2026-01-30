from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from momontum.schemas import TICKS_SCHEMA_V1


@pytest.fixture
def sample_ticks_df() -> pd.DataFrame:
    # Two minutes of ticks for one symbol.
    # timestamps are in ms.
    return pd.DataFrame(
        [
            {"symbol": "BTC/USDT", "timestamp": 1_700_000_000_000, "datetime": "", "bid": 99.0, "ask": 101.0, "bidVolume": 1.0, "askVolume": 1.0, "last": None, "spread": 2.0, "spread_pct": 2.0, "local_timestamp": 0.0},
            {"symbol": "BTC/USDT", "timestamp": 1_700_000_010_000, "datetime": "", "bid": 100.0, "ask": 102.0, "bidVolume": 1.0, "askVolume": 1.0, "last": None, "spread": 2.0, "spread_pct": 2.0, "local_timestamp": 0.0},
            # next minute bucket
            {"symbol": "BTC/USDT", "timestamp": 1_700_000_060_000, "datetime": "", "bid": 101.0, "ask": 103.0, "bidVolume": 1.0, "askVolume": 1.0, "last": None, "spread": 2.0, "spread_pct": 2.0, "local_timestamp": 0.0},
            {"symbol": "BTC/USDT", "timestamp": 1_700_000_065_000, "datetime": "", "bid": 98.0, "ask": 100.0, "bidVolume": 1.0, "askVolume": 1.0, "last": None, "spread": 2.0, "spread_pct": 2.0, "local_timestamp": 0.0},
        ]
    )


@pytest.fixture
def sample_ticks_parquet(tmp_path: Path, sample_ticks_df: pd.DataFrame) -> Path:
    path = tmp_path / "ticks.parquet"
    table = pa.Table.from_pandas(sample_ticks_df, schema=TICKS_SCHEMA_V1, preserve_index=False)
    pq.write_table(table, path, compression="snappy")
    return path
