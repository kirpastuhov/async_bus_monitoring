import json
import os
from functools import wraps

import trio
from loguru import logger
from trio_websocket import ConnectionClosed, HandshakeError

from schemas import Bus, WindowBounds


def generate_bus_id(emulator_id: str, route_id: str, bus_index: int):
    if emulator_id:
        return f"{emulator_id}-{route_id}-{bus_index}"
    return f"{route_id}-{bus_index}"


def load_routes(directory_path="routes"):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, "r", encoding="utf8") as file:
                yield json.load(file)


def relaunch_on_disconnect(async_function):
    @wraps(async_function)
    async def wrapper(*args, **kwds):
        counter = 3

        while True:
            try:
                await async_function(*args, **kwds)

            except (HandshakeError, ConnectionClosed) as e:
                logger.error("Connection Error, retrying...")
                await trio.sleep(counter)

    return wrapper


def validate_message(message: str) -> dict:
    result = {"message": {}, "errors": []}

    try:
        json_message = json.loads(message)
        logger.info(f"json_msg {json_message}")
        msg_type = json_message.get("msgType", None)

        if "msgType" in json_message:
            if json_message.get("msgType", None) != "newBounds":
                logger.warning(f"Validation Error: Invalid message type '{msg_type}'")
                result["errors"].append("Requires msgType specified")
            else:
                _ = WindowBounds(**json_message)

        else:
            _ = Bus(**json_message)

        return {"message": json_message, "errors": []}

    except TypeError:
        logger.warning("Validation Error: Invalid data")
        return {"message": {}, "errors": ["Invalid data"]}

    except json.JSONDecodeError:
        logger.warning("Validation Error: Got invalid JSON")
        return {"message": {}, "errors": ["Requires valid JSON"]}
