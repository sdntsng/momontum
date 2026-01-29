"""Parquet schema versioning + validation utilities.

This module defines:
- canonical schema version identifiers
- a stable metadata key for Parquet/Arrow schema metadata
- helpers to read/write Parquet while preserving `schema_version`

We store the version in Arrow schema metadata because PyArrow persists it into
Parquet file metadata.

See: docs/parquet_schema.md
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SCHEMA_VERSION_KEY = "momontum:schema_version"


class SchemaVersion(str, Enum):
    """Known schema versions.

    Use string enum values so they serialize cleanly into Parquet metadata.
    """

    V1 = "v1"


class SchemaValidationError(ValueError):
    """Raised when persisted data does not match an expected schema."""


def attach_schema_version(table: pa.Table, *, version: SchemaVersion) -> pa.Table:
    """Return a copy of *table* with schema_version stored in schema metadata."""

    existing = dict(table.schema.metadata or {})
    existing[SCHEMA_VERSION_KEY.encode("utf-8")] = version.value.encode("utf-8")
    return table.replace_schema_metadata(existing)


def read_schema_version(table: pa.Table) -> SchemaVersion:
    """Read schema_version from a Table's schema metadata.

    Raises:
        SchemaValidationError: if missing/unknown.
    """

    md = table.schema.metadata or {}
    raw = md.get(SCHEMA_VERSION_KEY.encode("utf-8"))
    if raw is None:
        raise SchemaValidationError(f"Missing required Parquet metadata key {SCHEMA_VERSION_KEY!r}")

    try:
        value = raw.decode("utf-8")
    except Exception as exc:  # pragma: no cover
        raise SchemaValidationError(
            f"Invalid {SCHEMA_VERSION_KEY!r} metadata value: {raw!r}"
        ) from exc

    try:
        return SchemaVersion(value)
    except ValueError as exc:
        raise SchemaValidationError(
            f"Unknown schema version {value!r} (key {SCHEMA_VERSION_KEY!r})"
        ) from exc


def _format_list(items: Iterable[str]) -> str:
    return ", ".join(items)


def validate_required_schema(
    table: pa.Table, *, required_schema: pa.Schema, allow_extra_columns: bool = True
) -> None:
    """Validate that *table* includes all required fields with matching dtypes."""

    table_schema = table.schema

    missing: list[str] = []
    type_mismatches: list[str] = []

    for field in required_schema:
        if table_schema.get_field_index(field.name) == -1:
            missing.append(field.name)
            continue

        actual = table_schema.field(field.name)
        if actual.type != field.type:
            type_mismatches.append(f"{field.name}: expected {field.type}, got {actual.type}")

    if missing or type_mismatches:
        parts: list[str] = []
        if missing:
            parts.append(f"missing columns: [{_format_list(missing)}]")
        if type_mismatches:
            parts.append(f"dtype mismatches: [{_format_list(type_mismatches)}]")
        raise SchemaValidationError("; ".join(parts))

    if not allow_extra_columns and table_schema.names != required_schema.names:
        raise SchemaValidationError(
            "Unexpected extra columns present; "
            f"expected {required_schema.names}, got {table_schema.names}"
        )


def write_parquet(
    path: str | Path,
    table: pa.Table,
    *,
    version: SchemaVersion,
    compression: str = "snappy",
) -> None:
    """Write a Parquet file with schema_version attached."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    table_with_md = attach_schema_version(table, version=version)
    pq.write_table(table_with_md, path, compression=compression)


def read_parquet(
    path: str | Path,
    *,
    expected_version: SchemaVersion | None = None,
) -> pa.Table:
    """Read a Parquet file and (optionally) enforce schema version."""

    table = pq.read_table(Path(path))
    actual_version = read_schema_version(table)

    if expected_version is not None and actual_version != expected_version:
        raise SchemaValidationError(
            f"Schema version mismatch: expected {expected_version.value}, "
            f"got {actual_version.value}"
        )

    return table
