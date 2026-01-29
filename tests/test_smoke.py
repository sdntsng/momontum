"""Minimal tests to ensure core modules import.

The project is evolving and not all modules have stable public APIs yet.
This test intentionally stays lightweight so CI can still validate basic
health (imports + dependency wiring).
"""


def test_imports() -> None:
    import api.main  # noqa: F401
    import backtesting.backtest  # noqa: F401
    import harvester  # noqa: F401
    import processor  # noqa: F401
    import trader  # noqa: F401
