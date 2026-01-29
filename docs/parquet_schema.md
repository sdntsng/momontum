# Canonical Parquet layout + schema versioning

This repo persists market data (ticks, candles, features, etc.) as Parquet.
This document defines the **canonical on-disk layout** and the **schema versioning strategy**.

> Goal: stable interoperability across pandas/polars/pyarrow and safe evolution of persisted datasets.

---

## 1) Canonical folder layout

All Parquet data lives under a single root directory (configurable), referred to below as `DATA_ROOT`.

### 1.1 Datasets

A dataset is one of:
- `ticks` (raw best-bid/ask/last stream)
- `candles` (OHLC aggregates)
- `features` (derived features for modeling)

Datasets are stored as:

```
DATA_ROOT/
  <dataset>/
    <timeframe>/
      <symbol>/
        YYYY/
          MM/
            DD/
              part-0000.parquet
              part-0001.parquet
              ...
```

Where:
- `<dataset>`: `ticks` | `candles` | `features` | ...
- `<timeframe>`:
  - for ticks: `tick`
  - for candles/features: interval string such as `1min`, `5min`, `1h`, `1d`
- `<symbol>`: exchange symbol in canonical form (example: `BTC/USDT`)
- `YYYY/MM/DD`: UTC date partitions derived from the row timestamps

### 1.2 File naming

Files inside a date partition should be named:

- `part-0000.parquet`, `part-0001.parquet`, ...

There is no requirement that a partition contains exactly one file.

---

## 2) Schemas (required columns + dtypes)

Schemas are defined in code via **PyArrow schemas**.

- `momontum/schemas.py` contains the V1 schemas.
- All timestamps are **UTC epoch milliseconds** unless otherwise specified.

### 2.1 Ticks (schema v1)

Source: `momontum.schemas.TICKS_SCHEMA_V1`

Required columns:

| column | type | notes |
|---|---:|---|
| `symbol` | `string` | exchange symbol |
| `timestamp` | `int64` | exchange timestamp (ms) |
| `datetime` | `string` | exchange ISO8601 timestamp as-provided |
| `bid` | `float64` | best bid |
| `ask` | `float64` | best ask |
| `bidVolume` | `float64` | bid size |
| `askVolume` | `float64` | ask size |
| `last` | `float64` | last traded price |
| `spread` | `float64` | `ask - bid` |
| `spread_pct` | `float64` | `spread / mid` |
| `local_timestamp` | `float64` | local time seconds (float) |

### 2.2 Candles (schema v1)

Source: `momontum.schemas.CANDLES_SCHEMA_V1`

Required columns:

| column | type | notes |
|---|---:|---|
| `symbol` | `string` | exchange symbol |
| `interval` | `string` | interval label such as `1min` |
| `start_ts` | `int64` | bucket start (ms) |
| `end_ts` | `int64` | bucket end (ms) |
| `open` | `float64` | open |
| `high` | `float64` | high |
| `low` | `float64` | low |
| `close` | `float64` | close |
| `n_ticks` | `int64` | number of raw ticks aggregated |

---

## 3) Schema versioning (Parquet metadata)

### 3.1 What gets written

Every Parquet file written by Momontum **must** include a schema version in the Parquet/Arrow schema metadata.

- metadata key: `momontum:schema_version`
- value: a string such as `v1`

This is stored at the Arrow schema level and is preserved by `pyarrow.parquet.write_table()`.

### 3.2 Compatibility rules

- Readers MUST reject files without a schema version.
- Readers MUST reject files with an unknown schema version.
- Readers MAY accept files with extra columns as long as required columns + dtypes match.

### 3.3 Implementation

Code helpers live in `momontum/data/schema.py` and provide:
- `SchemaVersion` enum
- metadata attach/read helpers
- basic table validation (required columns + dtypes)

---

## 4) Recommended usage

When writing:
- build a `pyarrow.Table` with an explicit schema (no dtype inference)
- attach schema version metadata
- write with snappy compression

When reading:
- read Parquet into a `pyarrow.Table`
- validate schema version and required columns before converting to pandas/polars
