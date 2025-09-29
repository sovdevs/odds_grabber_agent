# src/main.py
from __future__ import annotations

from apify import Actor

async def main() -> None:
    """Define a main entry point for the Apify Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Apify platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        Actor.log.info('Hello from the Actor!')
        await Actor.push_data({"test": "hello", "number": 42})
        Actor.log.info("Test item pushed to dataset.")