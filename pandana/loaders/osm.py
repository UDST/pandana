"""
Tools for creating Pandana networks from OpenStreetMap.

"""

import pandas as pd
import requests


from .. import Network


def pdna_network_from_bbox(
        lat_min=None, lng_min=None, lat_max=None, lng_max=None, bbox=None,
        network_type='walk', two_way=True,
        timeout=180, memory=None, max_query_area_size=50 * 1000 * 50 * 1000):
    """
    Make a Pandana network from a bounding lat/lon box via a request to the
    OpenStreetMap Overpass API. Distance will be in meters. Requires installing
    the OSMnet library.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float
    bbox : tuple
        Bounding box formatted as a 4 element tuple:
        (lng_max, lat_min, lng_min, lat_max)
    network_type : {'walk', 'drive'}, optional
        Specify whether the network will be used for walking or driving.
        A value of 'walk' attempts to exclude things like freeways,
        while a value of 'drive' attempts to exclude things like
        bike and walking paths.
    two_way : bool, optional
        Whether the routes are two-way. If True, node pairs will only
        occur once.
    timeout : int, optional
        the timeout interval for requests and to pass to Overpass API
    memory : int, optional
        server memory allocation size for the query, in bytes.
        If none, server will use its default allocation size
    max_query_area_size : float, optional
        max area for any part of the geometry, in the units the geometry is in

    Returns
    -------
    network : pandana.Network

    """
    try:
        ModuleNotFoundError  # Python 3.6+
    except NameError:
        ModuleNotFoundError = ImportError

    try:
        from osmnet.load import network_from_bbox
    except ModuleNotFoundError:
        raise ModuleNotFoundError("OSM downloads require the OSMnet library: "
                                  "https://udst.github.io/osmnet/")

    nodes, edges = network_from_bbox(lat_min=lat_min, lng_min=lng_min,
                                     lat_max=lat_max, lng_max=lng_max,
                                     bbox=bbox, network_type=network_type,
                                     two_way=two_way, timeout=timeout,
                                     memory=memory,
                                     max_query_area_size=max_query_area_size)

    return Network(
        nodes['x'], nodes['y'],
        edges['from'], edges['to'], edges[['distance']])


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

    node = {
        'id': e['id'],
        'lat': e['lat'],
        'lon': e['lon']
    }

    if 'tags' in e:
        for t, v in list(e['tags'].items()):
            if t not in uninteresting_tags:
                node[t] = v

    return node


def make_osm_query(query):
    """
    Make a request to OSM and return the parsed JSON.

    Parameters
    ----------
    query : str
        A string in the Overpass QL format.

    Returns
    -------
    data : dict

    """
    osm_url = 'http://www.overpass-api.de/api/interpreter'
    req = requests.get(osm_url, params={'data': query})
    req.raise_for_status()

    return req.json()


def build_node_query(lat_min, lng_min, lat_max, lng_max, tags=None):
    """
    Build the string for a node-based OSM query.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float
    tags : str or list of str, optional
        Node tags that will be used to filter the search.
        See http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
        for information about OSM Overpass queries
        and http://wiki.openstreetmap.org/wiki/Map_Features
        for a list of tags.

    Returns
    -------
    query : str

    """
    if tags is not None:
        if isinstance(tags, str):
            tags = [tags]
        tags = ''.join('[{}]'.format(t) for t in tags)
    else:
        tags = ''

    query_fmt = (
        '[out:json];'
        '('
        '  node'
        '  {tags}'
        '  ({lat_min},{lng_min},{lat_max},{lng_max});'
        ');'
        'out;')

    return query_fmt.format(
        lat_min=lat_min, lng_min=lng_min, lat_max=lat_max, lng_max=lng_max,
        tags=tags)


def node_query(lat_min, lng_min, lat_max, lng_max, tags=None):
    """
    Search for OSM nodes within a bounding box that match given tags.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float
    tags : str or list of str, optional
        Node tags that will be used to filter the search.
        See http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
        for information about OSM Overpass queries
        and http://wiki.openstreetmap.org/wiki/Map_Features
        for a list of tags.

    Returns
    -------
    nodes : pandas.DataFrame
        Will have 'lat' and 'lon' columns, plus other columns for the
        tags associated with the node (these will vary based on the query).
        Index will be the OSM node IDs.

    """
    node_data = make_osm_query(build_node_query(
        lat_min, lng_min, lat_max, lng_max, tags=tags))

    if len(node_data['elements']) == 0:
        raise RuntimeError('OSM query results contain no data.')

    nodes = [process_node(n) for n in node_data['elements']]
    return pd.DataFrame.from_records(nodes, index='id')
