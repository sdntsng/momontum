"""Schema definitions for persisted datasets.

We keep schemas in one place so:
- Parquet files have stable, explicit dtypes
- downstream readers (polars/pandas) don't get surprised by inference

All timestamps are UTC epoch milliseconds unless explicitly stated.
"""

from __future__ import annotations

import pyarrow as pa


TICKS_SCHEMA_V1 = pa.schema(
    [
        ("symbol", pa.string()),
        ("timestamp", pa.int64()),  # exchange ts (ms)
        ("datetime", pa.string()),  # exchange ISO8601 (string, as provided)
        ("bid", pa.float64()),
        ("ask", pa.float64()),
        ("bidVolume", pa.float64()),
        ("askVolume", pa.float64()),
        ("last", pa.float64()),
        ("spread", pa.float64()),
        ("spread_pct", pa.float64()),
        ("local_timestamp", pa.float64()),  # local time seconds (float)
    ]
)


CANDLES_SCHEMA_V1 = pa.schema(
    [
        ("symbol", pa.string()),
        ("interval", pa.string()),
        ("start_ts", pa.int64()),  # bucket start (ms)
        ("end_ts", pa.int64()),  # bucket end (ms)
        ("open", pa.float64()),
        ("high", pa.float64()),
        ("low", pa.float64()),
        ("close", pa.float64()),
        ("n_ticks", pa.int64()),
    ]
)
