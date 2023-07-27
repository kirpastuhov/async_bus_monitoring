import json
from itertools import cycle

import asyncclick as click
import trio
from loguru import logger
from trio_websocket import ConnectionClosed, open_websocket_url

ERRORS = [
    json.dumps({"busId": "1111", "lat": 11.11}),
    json.dumps({"lng": 11.11, "route": "11"}),
    json.dumps({"busId": "1111", "lat": "11.11", "lng": 11.11, "route": 11}),
    json.dumps({"busId": "111", "lat": [11.11], "lng": [11.100], "route": "11"}),
    "abc",
    '{ "busId": [] }',
]


@click.command()
@click.option(
    "--server",
    default="ws://127.0.0.1:8080",
    show_default=True,
    type=str,
    help="Server address",
)
async def main(server: str):
    async with open_websocket_url(server) as ws:
        for error in cycle(ERRORS):
            try:
                await ws.send_message(error)
                logger.info(f"Send msg {error}")

                message = await ws.get_message()
                logger.error(f"Received message: {message}")
            except (OSError, ConnectionClosed) as e:
                logger.error(f"Connection failed: {e}")
            await trio.sleep(5)


if __name__ == "__main__":
    main(_anyio_backend="trio")
