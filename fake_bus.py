import itertools
import json
import random
import sys
from dataclasses import asdict
from itertools import cycle, islice

import asyncclick as click
import trio
from loguru import logger
from trio_websocket import open_websocket_url

from schemas import Bus
from utils import generate_bus_id, load_routes, relaunch_on_disconnect


@click.command()
@click.option(
    "--server",
    default="ws://127.0.0.1:8080",
    show_default=True,
    type=str,
    help="Server address",
)
@click.option(
    "--routes_number",
    default=5,
    show_default=True,
    type=int,
    help="Amount of routes. There are 963 routes available",
)
@click.option(
    "--buses_per_route",
    default=3,
    show_default=True,
    type=int,
    help="Amount of busses for each route.",
)
@click.option(
    "--websockets_number",
    default=3,
    show_default=True,
    type=int,
    help="Amount of open websockets",
)
@click.option(
    "--emulator_id",
    default="",
    show_default=True,
    type=str,
    help="Prefix for bus_id in case of running several instances of emulator",
)
@click.option(
    "--refresh_timeout",
    default=0.1,
    show_default=True,
    type=float,
    help="Server coordinates refresh rate",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Display verbose log output",
)
async def main(
    server: str,
    routes_number: int,
    buses_per_route: int,
    websockets_number: int,
    emulator_id: str,
    refresh_timeout: float,
    verbose: bool,
):
    send_channels = []

    if not verbose:
        logger.remove()
        logger.add(sys.stderr, level="ERROR")

    async with trio.open_nursery() as nursery:
        for _ in range(websockets_number):
            send_channel, recieve_channel = trio.open_memory_channel(0)
            send_channels.append(send_channel)

            nursery.start_soon(send_updates, server, recieve_channel, refresh_timeout)

        for bus_number in range(1, buses_per_route + 1):
            for route in itertools.islice(load_routes(), routes_number):
                bus_id = generate_bus_id(emulator_id, route["name"], bus_number)

                send_channel = random.choice(send_channels)
                nursery.start_soon(run_bus, send_channel, route, bus_id)


@relaunch_on_disconnect
async def send_updates(
    server_address: str,
    receive_channel: trio.MemoryReceiveChannel,
    refresh_timeout: float,
):
    try:
        async with open_websocket_url(server_address) as ws:
            while True:
                async for value in receive_channel:
                    await ws.send_message(value)
                    await trio.sleep(refresh_timeout)
    except OSError as ose:
        logger.error(f"Connection attempt failed: {ose}")


async def create_bus(bus_id: str, route: dict, send_channel: trio.MemorySendChannel):
    stop = len(route["coordinates"])
    for coords in islice(route["coordinates"], random.randint(1, stop), stop):
        latitude, longtitude = coords
        bus = Bus(busId=bus_id, lat=latitude, lng=longtitude, route=route["name"])
        await send_channel.send(json.dumps(asdict(bus), ensure_ascii=True))

    for coords in cycle(route["coordinates"]):
        latitude, longtitude = coords
        bus = Bus(busId=bus_id, lat=latitude, lng=longtitude, route=route["name"])
        await send_channel.send(json.dumps(asdict(bus), ensure_ascii=True))


async def run_bus(send_channel: trio.MemorySendChannel, route: dict, bus_id: str):
    try:
        await create_bus(bus_id, route, send_channel)
    except OSError as ose:
        logger.error(f"Connection attempt failed: {ose}")


if __name__ == "__main__":
    main(_anyio_backend="trio")
