from __future__ import division

import math


def great_circle_dist(lat1, lon1, lat2, lon2):
    """
    Get the distance (in meters) between two lat/lon points
    via the Haversine formula.

    Parameters
    ----------
    lat1, lon1, lat2, lon2 : float
        Latitude and longitude in degrees.

    Returns
    -------
    dist : float
        Distance in meters.

    """
    radius = 6372795  # meters

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # formula from:
    # http://en.wikipedia.org/wiki/Haversine_formula#The_haversine_formula
    a = math.pow(math.sin(dlat / 2), 2)
    b = math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlon / 2), 2)
    d = 2 * radius * math.asin(math.sqrt(a + b))

    return d
