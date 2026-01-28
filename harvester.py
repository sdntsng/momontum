"""Compatibility entrypoint.

The main streaming harvester implementation lives in `streamer.py`.
This module is kept to avoid breaking imports (e.g. verify scripts).
"""

from streamer import DataHarvester  # re-export


async def main():
    harvester = DataHarvester()
    await harvester.harvest()


__all__ = ["DataHarvester", "main"]
