import json
import random
from itertools import cycle, islice
from sys import stderr

import trio
import trio_websocket
from trio_websocket import open_websocket_url

from load_routes import load_routes

BUS_PER_ROUTE = 2


async def main():
    url = "ws://127.0.0.1:8080"

    async with trio.open_nursery() as nursery:
        # Make two concurrent calls to child()
        for route in load_routes():
            bus_ids = [generate_bus_id(route["name"], i) for i in range(BUS_PER_ROUTE)]
            for bus_id in bus_ids:
                nursery.start_soon(run_bus, url, route, bus_id)
                print("HERE", len(nursery.child_tasks))


def generate_bus_id(route_id: str, bus_index: int) -> str:
    return f"{route_id}-{bus_index}"


# send_updates(server_address, receive_channel)


async def create_bus(bus_id: str, route, ws: trio_websocket.WebSocketConnection):
    bus = {"busId": bus_id, "lat": 0, "lng": 0, "route": route["name"]}

    stop = len(route["coordinates"])
    for coords in islice(route["coordinates"], random.randint(1, stop), stop):
        bus["lat"], bus["lng"] = coords
        await ws.send_message(json.dumps(bus, ensure_ascii=True))
        await trio.sleep(0.5)

    for coords in cycle(route["coordinates"]):
        bus["lat"], bus["lng"] = coords
        await ws.send_message(json.dumps(bus, ensure_ascii=True))
        await trio.sleep(0.5)


async def run_bus(url, route, bus_id):
    try:
        async with open_websocket_url(url) as ws:
            print("Creating bus with id", bus_id)
            await create_bus(bus_id, route, ws)
            await trio.sleep(1)

    except OSError as ose:
        print("Connection attempt failed: %s" % ose, file=stderr)


trio.run(main)
