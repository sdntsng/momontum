from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from momontum.data.schema import (
    SCHEMA_VERSION_KEY,
    SchemaValidationError,
    SchemaVersion,
    read_parquet,
    read_schema_version,
    validate_required_schema,
    write_parquet,
)
from momontum.schemas import TICKS_SCHEMA_V1


def _sample_ticks_table() -> pa.Table:
    data = {
        "symbol": ["BTC/USDT", "BTC/USDT"],
        "timestamp": [1700000000000, 1700000000100],
        "datetime": ["2024-01-01T00:00:00Z", "2024-01-01T00:00:00.100Z"],
        "bid": [100.0, 101.0],
        "ask": [101.0, 102.0],
        "bidVolume": [1.0, 1.1],
        "askVolume": [2.0, 2.2],
        "last": [100.5, 101.5],
        "spread": [1.0, 1.0],
        "spread_pct": [0.01, 0.0098],
        "local_timestamp": [1700000000.0, 1700000000.1],
    }
    return pa.Table.from_pydict(data, schema=TICKS_SCHEMA_V1)


def test_write_read_roundtrip_preserves_schema_version(tmp_path: Path) -> None:
    path = tmp_path / "ticks.parquet"
    table = _sample_ticks_table()

    write_parquet(path, table, version=SchemaVersion.V1)

    out = read_parquet(path, expected_version=SchemaVersion.V1)

    assert out.num_rows == table.num_rows
    assert out.schema.metadata is not None
    assert out.schema.metadata[SCHEMA_VERSION_KEY.encode("utf-8")] == b"v1"
    assert read_schema_version(out) == SchemaVersion.V1


def test_validate_required_schema_allows_extra_columns() -> None:
    table = _sample_ticks_table().append_column("extra", pa.array([1, 2], type=pa.int64()))
    validate_required_schema(table, required_schema=TICKS_SCHEMA_V1, allow_extra_columns=True)


def test_read_schema_version_missing_raises(tmp_path: Path) -> None:
    path = tmp_path / "no_version.parquet"

    # Write the file without metadata to simulate a foreign writer
    pq.write_table(_sample_ticks_table().replace_schema_metadata({}), path)

    out = pq.read_table(path)
    try:
        read_schema_version(out)
    except SchemaValidationError as exc:
        assert "Missing required Parquet metadata" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected SchemaValidationError")
