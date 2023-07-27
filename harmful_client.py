import json
from itertools import cycle

import asyncclick as click
import trio
from loguru import logger
from trio_websocket import open_websocket_url

ERRORS = [
    json.dumps(
        {
            "data": {
                "south_lat": 1,
                "north_lat": 1,
                "west_lng": 2,
                "east_lng": 2,
            }
        }
    ),
    json.dumps({"msgType": "Error Msg Type"}),
    json.dumps({"msgType": "newBounds", "data": {"lat": 123, "north_lat": 565}}),
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
            except Exception as e:
                logger.error(f"Connection attempt failed: {e}")

            await trio.sleep(5)


if __name__ == "__main__":
    main(_anyio_backend="trio")
