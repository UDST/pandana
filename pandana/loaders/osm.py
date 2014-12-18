"""
Tools for creating Pandana networks from Open Street Map.

"""
import pandas as pd
import requests

uninteresting_tags = {
    'source',
    'source_ref',
    'source:ref',
    'history',
    'attribution',
    'created_by',
    'tiger:tlid',
    'tiger:upload_uuid',
}


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
        '  way'
        '  ["highway"]'
        '  ({lat_min},{lng_min},{lat_max},{lng_max});'
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


def process_node(e):
    """
    Process a node element entry into a dict suitable for going into
    a Pandas DataFrame.

    Parameters
    ----------
    e : dict

    Returns
    -------
    node : dict

    """
    node = {
        'id': e['id'],
        'lat': e['lat'],
        'lon': e['lon']
    }

    if 'tags' in e:
        for t, v in e['tags'].items():
            if t not in uninteresting_tags:
                node[t] = v

    return node


def process_way(e):
    """
    Process a way element entry into a list of dicts suitable for going into
    a Pandas DataFrame.

    Parameters
    ----------
    e : dict

    Returns
    -------
    way : dict
    waynodes : list of dict

    """
    way = {
        'id': e['id']
    }

    if 'tags' in e:
        for t, v in e['tags'].items():
            if t not in uninteresting_tags:
                way[t] = v

    waynodes = []

    for n in e['nodes']:
        waynodes.append({'way_id': e['id'], 'node_id': n})

    return way, waynodes


def parse_osm_query(data):
    """
    Convert OSM query data to DataFrames of ways and way-nodes.

    Parameters
    ----------
    data : dict
        Result of an OSM query.

    Returns
    -------
    nodes, ways, waynodes : pandas.DataFrame

    """
    nodes = []
    ways = []
    waynodes = []

    for e in data['elements']:
        if e['type'] == 'node':
            nodes.append(process_node(e))
        elif e['type'] == 'way':
            w, wn = process_way(e)
            ways.append(w)
            waynodes.extend(wn)

    return (
        pd.DataFrame.from_records(nodes, index='id'),
        pd.DataFrame.from_records(ways, index='id'),
        pd.DataFrame.from_records(waynodes, index='way_id'))


def ways_in_bbox(lat_min, lng_min, lat_max, lng_max):
    """
    Get DataFrames of OSM data in a bounding box.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float

    Returns
    -------
    nodes, ways, waynodes : pandas.DataFrame

    """
    return parse_osm_query(make_osm_query(lat_min, lng_min, lat_max, lng_max))
