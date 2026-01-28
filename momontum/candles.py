"""Candle generation from tick/BBO data.

Input tick records are expected to match :data:`momontum.schemas.TICKS_SCHEMA_V1`.
We compute OHLC from mid-price = (bid+ask)/2.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .schemas import CANDLES_SCHEMA_V1, TICKS_SCHEMA_V1


@dataclass(frozen=True)
class CandleBuildResult:
    candles: pd.DataFrame


def _normalize_interval(interval: str) -> str:
    interval = interval.strip().lower()
    # pandas supports "1min" or "1t"; standardize to "1min"-style.
    if interval.endswith("m") and interval[:-1].isdigit():
        return f"{interval[:-1]}min"
    if interval.endswith("min") and interval[:-3].isdigit():
        return interval
    if interval.endswith("h") and interval[:-1].isdigit():
        return f"{interval[:-1]}h"
    return interval


def build_candles_from_ticks_df(ticks: pd.DataFrame, *, interval: str = "1min") -> CandleBuildResult:
    """Aggregate tick rows into candle rows."""
    if ticks.empty:
        out = pd.DataFrame(
            columns=[
                "symbol",
                "interval",
                "start_ts",
                "end_ts",
                "open",
                "high",
                "low",
                "close",
                "n_ticks",
            ]
        )
        return CandleBuildResult(out)

    interval = _normalize_interval(interval)

    df = ticks.copy()
    if "timestamp" not in df.columns:
        raise ValueError("ticks must include 'timestamp' (epoch ms)")

    # mid price
    df["mid"] = (df["bid"].astype(float) + df["ask"].astype(float)) / 2.0

    # time bucket
    ts = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["bucket"] = ts.dt.floor(interval)

    grouped = df.groupby(["symbol", "bucket"], sort=True)
    agg = grouped["mid"].agg([("open", "first"), ("high", "max"), ("low", "min"), ("close", "last")])
    agg["n_ticks"] = grouped.size().astype("int64")

    agg = agg.reset_index()
    agg["interval"] = interval

    # bucket -> start/end ts
    agg["start_ts"] = (agg["bucket"].astype("int64") // 10**6).astype("int64")
    # end_ts is inclusive-ish: end of bucket (start + interval) - 1ms
    bucket_end = (agg["bucket"] + pd.to_timedelta(interval)).astype("int64") // 10**6
    agg["end_ts"] = bucket_end.astype("int64") - 1

    out = agg[[
        "symbol",
        "interval",
        "start_ts",
        "end_ts",
        "open",
        "high",
        "low",
        "close",
        "n_ticks",
    ]].copy()

    return CandleBuildResult(out)


def _iter_parquet_files(inputs: Sequence[str | Path]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files.extend(sorted(p.glob("*.parquet")))
        else:
            files.append(p)
    return files


def read_ticks(inputs: Sequence[str | Path]) -> pd.DataFrame:
    files = _iter_parquet_files(inputs)
    if not files:
        raise FileNotFoundError("No parquet inputs found")

    dfs: list[pd.DataFrame] = []
    for f in files:
        table = pq.read_table(f)
        # best effort align to schema (we tolerate missing cols from older files)
        for name in TICKS_SCHEMA_V1.names:
            if name not in table.column_names:
                table = table.append_column(name, pa.nulls(table.num_rows))
        table = table.select(TICKS_SCHEMA_V1.names)
        dfs.append(table.to_pandas())

    return pd.concat(dfs, ignore_index=True)


def write_candles(df: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df, schema=CANDLES_SCHEMA_V1, preserve_index=False)
    pq.write_table(table, output_path, compression="snappy")


def build_candles(
    inputs: Sequence[str | Path],
    *,
    interval: str = "1min",
    output_path: str | Path,
) -> CandleBuildResult:
    ticks = read_ticks(inputs)
    res = build_candles_from_ticks_df(ticks, interval=interval)
    write_candles(res.candles, output_path)
    return res
