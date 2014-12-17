"""
Tools for creating Pandana networks from Open Street Map.

"""
import requests


def osm_query(lat_min, lng_min, lat_max, lng_max):
    """
    Construct an OSM way query for a bounding box.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float

    Returns
    -------
    query : str

    """
    query_fmt = (
        '[out:json];'
        '('
        '  way({lat_min},{lng_min},{lat_max},{lng_max});'
        '  >;'  # the '>' makes it recurse so we get ways and way nodes
        ');'
        'out;')
    return query_fmt.format(
        lat_min=lat_min, lng_min=lng_min, lat_max=lat_max, lng_max=lng_max)


def make_osm_query(lat_min, lng_min, lat_max, lng_max):
    """
    Make a request to OSM and return the parsed JSON.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float

    Returns
    -------
    data : dict

    """
    osm_url = 'http://www.overpass-api.de/api/interpreter'
    query = osm_query(lat_min, lng_min, lat_max, lng_max)

    req = requests.get(osm_url, params={'data': query})
    req.raise_for_status()

    return req.json()

