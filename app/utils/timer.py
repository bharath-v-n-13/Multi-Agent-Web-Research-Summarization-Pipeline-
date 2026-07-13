import time
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator, Dict

@contextmanager
def sync_timer() -> Generator[Dict[str, float], None, None]:
    """
    Synchronous context manager to measure execution time.
    Usage:
        with sync_timer() as t:
            # run code
        print(t['elapsed'])
    """
    result = {"elapsed": 0.0}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start

@asynccontextmanager
async def async_timer() -> AsyncGenerator[Dict[str, float], None]:
    """
    Asynchronous context manager to measure execution time.
    Usage:
        async with async_timer() as t:
            # run async code
        print(t['elapsed'])
    """
    result = {"elapsed": 0.0}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start
