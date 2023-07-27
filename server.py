import json
import sys
from contextlib import suppress
from functools import partial

import asyncclick as click
import trio
from loguru import logger
from trio_websocket import ConnectionClosed, WebSocketConnection, WebSocketRequest, serve_websocket

from schemas import WindowBounds
from utils import validate_message

buses = {}

TALK_TO_BROWSER_DELAY = 1


async def echo_server(request: WebSocketRequest):
    ws = await request.accept()

    while True:
        try:
            message = await ws.get_message()
            logger.debug(f"Server got message: {message}")

            validated_message = validate_message(message)
            logger.debug(f"Validated Message {validated_message}")
            errors = validated_message.get("errors", [])

            if errors:
                error_message = json.dumps({"msgType": "Errors", "errors": errors})
                await ws.send_message(error_message)
            else:
                message = validated_message.get("message", {})
                bus_id = message.get("busId", None)
                buses[bus_id] = message

        except ConnectionClosed:
            break


async def handle_browser(request: WebSocketRequest):
    ws = await request.accept()
    bounds = WindowBounds()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(listen_to_browser, ws, bounds)
        nursery.start_soon(talk_to_browser, ws, bounds)


async def talk_to_browser(ws, bounds: WindowBounds):
    while True:
        try:
            message = {"msgType": "Buses", "buses": [bus for bus in buses.values() if bounds.is_inside(bus["lat"], bus["lng"])]}
            await ws.send_message(json.dumps(message))
            await trio.sleep(TALK_TO_BROWSER_DELAY)

        except ConnectionClosed:
            break


async def listen_to_browser(ws: WebSocketConnection, bounds: WindowBounds):
    while True:
        try:
            message = await ws.get_message()
            json_message = json.loads(message)
            bounds.update(**json_message["data"])

        except ConnectionClosed:
            pass


@click.command()
@click.option(
    "--bus_port",
    default=8080,
    show_default=True,
    type=int,
    help="The port for mocking buses",
)
@click.option(
    "--browser_port",
    default=8000,
    show_default=True,
    type=int,
    help="The port for communicating with browser",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    # default=False,
    show_default=True,
    help="Display verbose log output",
)
async def main(bus_port: int, browser_port: int, verbose: bool):
    url = "127.0.0.1"
    serve = partial(serve_websocket, ssl_context=None)

    if not verbose:
        logger.remove()
        logger.add(sys.stderr, level="ERROR")

    async with trio.open_nursery() as nursery:
        nursery.start_soon(serve, echo_server, url, bus_port)
        nursery.start_soon(serve, handle_browser, url, browser_port)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        main(_anyio_backend="trio")
