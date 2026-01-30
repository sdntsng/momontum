from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq


def test_cli_candles_build_smoke(sample_ticks_parquet: Path, tmp_path: Path) -> None:
    out = tmp_path / "candles.parquet"
    cmd = [
        sys.executable,
        "-m",
        "momontum",
        "candles",
        "build",
        str(sample_ticks_parquet),
        "--interval",
        "1min",
        "--output",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr

    table = pq.read_table(out)
    assert table.num_rows == 2
    assert set(table.column_names) >= {"symbol", "open", "close", "n_ticks"}
