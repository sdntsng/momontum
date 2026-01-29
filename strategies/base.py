import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class Signal:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class BaseStrategy(ABC):
    """
    Abstract Base Class for all trading strategies.
    Ensures compatibility with the Bulk Backtester.
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

    @abstractmethod
    def on_tick(
        self, record: Mapping[str, Any], prediction: Mapping[str, Any] | None = None
    ) -> str:
        """
        Process a single market tick and return a Signal.

        Args:
            record (dict): The current market data record (bid, ask, etc.)
            prediction (dict, optional): output from the ML processor.

        Returns:
            str: Signal.BUY, Signal.SELL, or Signal.HOLD
        """
        pass
