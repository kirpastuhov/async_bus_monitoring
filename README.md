# Buses on the map

Web application shows the movement of buses on the map of Moscow.  

Project uses web sockets ([trio-websocket](https://github.com/HyperionGray/trio-websocket)) 
based on [Trio](https://github.com/python-trio/trio) async implementation.  
![](screenshots/buses.gif)

## Installation

Python version required: `3.11`
* It's recommended to use `venv` or `virtualenv` for better isolation.  
`venv` setup example:
```
python3 -m venv env
source env/bin/activate
```

* Install requirements:  
```
pip3 install -r requirements.txt
```

## How to launch

* Run `python3 server.py`.  
This server is supposed to listen to incoming messages on `127.0.0.1:8080` address   
and send messages to `127.0.0.1:8000` address.
CLI args for `server.py`:
```
Usage: server.py [OPTIONS]

Options:
  --bus_port INTEGER      The port for mocking buses  [default: 8080]
  --browser_port INTEGER  The port for communicating with browser  [default:
                          8000]
  -v, --verbose           Display verbose log output
  --help                  Show this message and exit.
```


* To simulation the buses corrdinates you have would have to run the script `fake_bus.py` in another terminal window.  
CLI args for `fake_bus.py`:
```
Usage: fake_bus.py [OPTIONS]

Options:
  --server TEXT                Server address  [default: ws://127.0.0.1:8080]
  --routes_number INTEGER      Amount of routes. There are 963 routes
                               available  [default: 5]
  --buses_per_route INTEGER    Amount of busses for each route.  [default: 3]
  --websockets_number INTEGER  Amount of open websockets  [default: 3]
  --emulator_id TEXT           Prefix for bus_id in case of running several
                               instances of emulator
  --refresh_timeout FLOAT      Server coordinates refresh rate  [default: 0.1]
  -v, --verbose                Display verbose log output
  --help                       Show this message and exit.

```

* Open `index.html` in your browser.


## Data format

Frontend expects to receive JSON message with a list of buses from server:

```js
{
  "msgType": "Buses",
  "buses": [
    {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
    {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"}
  ]
}
```

Those buses that are not on the `buses` list of the last message from the server will be removed from the map.

The frontend tracks the movement of the user on the map and sends to the server new coordinates of the window:

```js
{
  "msgType": "newBounds",
  "data": {
    "east_lng": 37.65563964843751,
    "north_lat": 55.77367652953477,
    "south_lat": 55.72628839374007,
    "west_lng": 37.54440307617188
  }
}
```

## Used libraries

- [Leaflet](https://leafletjs.com/) - Drawing a map
- [loglevel](https://www.npmjs.com/package/loglevel) for logging