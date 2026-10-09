import math

class Loc_LatLng:
    M_PI            = 3.141592653589793
    M_PI_2          = M_PI / 2
    M_2PI           = M_PI * 2
    DEG_TO_RAD      = M_PI / 180
    RAD_TO_DEG      = 180  / M_PI

    RADIUS_OF_EARTH = 6378100
    LATLON_TO_M     = 0.011131884502145034
    LATLON_TO_M_INV = 89.83204953368922
    LATLON_TO_CM    = 1.1131884502145034

    # Semi-major axis of the Earth, in meters
    WGS84_A = 6378137
    # Inverse flattening of the Earth
    WGS84_IF = 298.257223563
    # The flattening of the Earth
    WGS84_F = 1 / WGS84_IF
    # Semi-minor axis of the Earth in meters
    WGS84_B = WGS84_A * (1 - WGS84_IF)

    def __init__(self, origin_lat, origin_lng):
        self.origin_lat = origin_lat
        self.origin_lng = origin_lng

    def delta_distance_m(self, lat2, lng2, lat1, lng1):
        lat_m = (lat2 - lat1) * self.LATLON_TO_M
        lng_m = (lng2 - lng1) * math.cos(lat2*(1e-7)*self.DEG_TO_RAD) * self.LATLON_TO_M
        return (math.sqrt(lat_m**2 + lng_m**2), lat_m, lng_m)

    def origin_distance_m(self,lat,lng):
        lat_m = (lat - self.origin_lat) * self.LATLON_TO_M
        lng_m = (lng - self.origin_lng) * math.cos(lat*1e-7*self.DEG_TO_RAD) * self.LATLON_TO_M
        return (math.sqrt(lat_m**2 + lng_m**2), lat_m, lng_m)

    def pos2gps(self, origin_lat, origin_lng, pos_n, pos_e):
        lat = origin_lat + pos_n / self.LATLON_TO_M
        lng = origin_lng + pos_e / self.LATLON_TO_M / math.cos(lat*1e-7*self.DEG_TO_RAD)
        return (lat, lng)