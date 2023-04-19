import json
from functools import partial

import trio
from trio_websocket import ConnectionClosed, WebSocketRequest, serve_websocket

message = {
    "msgType": "Buses",
    "buses": [],
}

buses = {}

TALK_TO_BROWSER_DELAY = 0.1


async def echo_server(request: WebSocketRequest):
    ws = await request.accept()

    while True:
        try:
            message = await ws.get_message()
            json_message = json.loads(message)
            bus_id = json_message["busId"]
            buses[bus_id] = json_message
        except ConnectionClosed:
            break


async def talk_to_browser(request: WebSocketRequest):
    ws = await request.accept()
    while True:
        print("HERE")
        try:
            message["buses"] = list(buses.values())
            print(message["buses"])
            print(len(message["buses"]))
            await ws.send_message(json.dumps(message))
            await trio.sleep(TALK_TO_BROWSER_DELAY)
        except ConnectionClosed:
            break


async def main():
    serve = partial(serve_websocket, ssl_context=None)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(serve, echo_server, "127.0.0.1", 8080)
        nursery.start_soon(serve, talk_to_browser, "127.0.0.1", 8000)


trio.run(main)
