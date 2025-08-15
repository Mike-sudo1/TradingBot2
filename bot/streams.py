"""WebSocket stream management for Binance bookTicker."""
from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Dict, List

import websockets
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

BINANCE_WS = "wss://stream.binance.com:9443/stream"


class StreamError(Exception):
    pass


async def _connect(url: str):
    return await websockets.connect(url, ping_interval=20, ping_timeout=20)


async def subscribe_book_ticker(symbols: List[str]) -> AsyncIterator[Dict]:
    """Yield bookTicker messages for symbols."""
    stream_names = "/".join(f"{s.lower()}@bookTicker" for s in symbols)
    url = f"{BINANCE_WS}?streams={stream_names}"

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type(Exception),
    ):
        with attempt:
            ws = await _connect(url)
            try:
                async for message in ws:
                    data = json.loads(message)
                    yield data
            finally:
                await ws.close()


__all__ = ["subscribe_book_ticker"]
