import numpy.testing as npt

from pandana.utils import great_circle_dist as gcd


def test_gcd():
    # tested against geopy
    # https://geopy.readthedocs.org/en/latest/#module-geopy.distance
    lat1 = 41.49008
    lon1 = -71.312796
    lat2 = 41.499498
    lon2 = -81.695391

    expected = 864456.76162966

    npt.assert_allclose(gcd(lat1, lon1, lat2, lon2), expected)
