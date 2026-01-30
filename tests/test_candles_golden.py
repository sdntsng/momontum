from __future__ import annotations

import pandas as pd

from momontum.candles import build_candles_from_ticks_df


def test_build_candles_golden(sample_ticks_df: pd.DataFrame) -> None:
    res = build_candles_from_ticks_df(sample_ticks_df, interval="1min")
    out = res.candles

    # We have 2 candle buckets.
    assert len(out) == 2

    # mid prices: (99+101)/2=100, (100+102)/2=101
    c0 = out.iloc[0].to_dict()
    assert c0["open"] == 100.0
    assert c0["high"] == 101.0
    assert c0["low"] == 100.0
    assert c0["close"] == 101.0
    assert c0["n_ticks"] == 2

    # mid prices: (101+103)/2=102, (98+100)/2=99
    c1 = out.iloc[1].to_dict()
    assert c1["open"] == 102.0
    assert c1["high"] == 102.0
    assert c1["low"] == 99.0
    assert c1["close"] == 99.0
    assert c1["n_ticks"] == 2
