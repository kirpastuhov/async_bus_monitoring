from dataclasses import dataclass


@dataclass
class Bus:
    busId: str
    lat: float
    lng: float
    route: str

    def __post_init__(self):
        if not isinstance(self.busId, str):
            raise TypeError("busId should be of type str")

        if not isinstance(self.lat, float):
            raise TypeError("lat should be of type float")

        if not isinstance(self.lng, float):
            raise TypeError("lng should be of type float")

        if not isinstance(self.route, str):
            raise TypeError("route should be of type str")


@dataclass
class WindowBounds:
    south_lat: float = 0.0
    north_lat: float = 0.0
    west_lng: float = 0.0
    east_lng: float = 0.0

    def is_inside(self, lat: float, lng: float) -> bool:
        lat_inside = self.south_lat < lat < self.north_lat
        lng_inside = self.west_lng < lng < self.east_lng
        return lat_inside and lng_inside

    def update(self, south_lat, north_lat, west_lng, east_lng):
        print("Updating Window bounds")
        self.south_lat = south_lat
        self.north_lat = north_lat
        self.west_lng = west_lng
        self.east_lng = east_lng

    def __post_init__(self):
        if not isinstance(self.south_lat, float):
            raise TypeError("south_lat should be of type float")

        if not isinstance(self.north_lat, float):
            raise TypeError("north_lat should be of type float")

        if not isinstance(self.west_lng, float):
            raise TypeError("west_lng should be of type float")

        if not isinstance(self.east_lng, float):
            raise TypeError("east_lng should be of type float")
