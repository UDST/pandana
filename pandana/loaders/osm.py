"""
Tools for creating Pandana networks from Open Street Map.

"""
from itertools import islice, izip

import pandas as pd
import requests

from .. import Network
from ..utils import great_circle_dist as gcd

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


def build_network_osm_query(
        lat_min, lng_min, lat_max, lng_max, network_type='walk'):
    """
    Construct an OSM way query for a bounding box.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float
    network_type : {'walk', 'drive'}, optional
        Specify whether the network will be used for walking or driving.
        A value of 'walk' attempts to exclude things like freeways,
        while a value of 'drive' attempts to exclude things like
        bike and walking paths.

    Returns
    -------
    query : str

    """
    query_fmt = (
        '[out:json];'
        '('
        '  way'
        '  ["highway"]'
        '  {filters}'
        '  ({lat_min},{lng_min},{lat_max},{lng_max});'
        '  >;'  # the '>' makes it recurse so we get ways and way nodes
        ');'
        'out;')

    if network_type == 'walk':
        filters = '["highway"!~"motor"]'
    elif network_type == 'drive':
        filters = '["highway"!~"foot|cycle"]'
    else:
        raise ValueError('Invalid network_type argument')

    return query_fmt.format(
        lat_min=lat_min, lng_min=lng_min, lat_max=lat_max, lng_max=lng_max,
        filters=filters)


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


def parse_network_osm_query(data):
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
    if len(data['elements']) == 0:
        raise RuntimeError('OSM query results contain no data.')

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


def ways_in_bbox(lat_min, lng_min, lat_max, lng_max, network_type='walk'):
    """
    Get DataFrames of OSM data in a bounding box.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float
    network_type : {'walk', 'drive'}, optional
        Specify whether the network will be used for walking or driving.
        A value of 'walk' attempts to exclude things like freeways,
        while a value of 'drive' attempts to exclude things like
        bike and walking paths.

    Returns
    -------
    nodes, ways, waynodes : pandas.DataFrame

    """
    return parse_network_osm_query(make_osm_query(build_network_osm_query(
        lat_min, lng_min, lat_max, lng_max, network_type=network_type)))


def intersection_nodes(waynodes):
    """
    Returns a set of all the nodes that appear in 2 or more ways.

    Parameters
    ----------
    waynodes : pandas.DataFrame
        Mapping of way IDs to node IDs as returned by `ways_in_bbox`.

    Returns
    -------
    intersections : set
        Node IDs that appear in 2 or more ways.

    """
    counts = waynodes.node_id.value_counts()
    return set(counts[counts > 1].index.values)


def node_pairs(nodes, ways, waynodes, two_way=True):
    """
    Create a table of node pairs with the distances between them.

    Parameters
    ----------
    nodes : pandas.DataFrame
        Must have 'lat' and 'lon' columns.
    ways : pandas.DataFrame
        Table of way metadata.
    waynodes : pandas.DataFrame
        Table linking way IDs to node IDs. Way IDs should be in the index,
        with a column called 'node_ids'.
    two_way : bool, optional
        Whether the routes are two-way. If True, node pairs will only
        occur once.

    Returns
    -------
    pairs : pandas.DataFrame
        Will have columns of 'from_id', 'to_id', and 'distance'.
        The index will be a MultiIndex of (from id, to id).
        The distance metric is in meters.

    """
    def pairwise(l):
        return izip(islice(l, 0, len(l)), islice(l, 1, None))
    intersections = intersection_nodes(waynodes)
    waymap = waynodes.groupby(level=0, sort=False)
    pairs = []

    for id, row in ways.iterrows():
        nodes_in_way = waymap.get_group(id).node_id.values
        nodes_in_way = filter(lambda x: x in intersections, nodes_in_way)

        if len(nodes_in_way) < 2:
            # no nodes to connect in this way
            continue

        for from_node, to_node in pairwise(nodes_in_way):
            fn = nodes.loc[from_node]
            tn = nodes.loc[to_node]

            distance = gcd(fn.lat, fn.lon, tn.lat, tn.lon)

            pairs.append({
                'from_id': from_node,
                'to_id': to_node,
                'distance': distance
            })

            if not two_way:
                pairs.append({
                    'from_id': to_node,
                    'to_id': from_node,
                    'distance': distance
                })

    pairs = pd.DataFrame.from_records(pairs)
    pairs.index = pd.MultiIndex.from_arrays(
        [pairs['from_id'].values, pairs['to_id'].values])

    return pairs


def network_from_bbox(
        lat_min, lng_min, lat_max, lng_max, network_type='walk', two_way=True):
    """
    Make a Pandana network from a bounding lat/lon box.

    Parameters
    ----------
    lat_min, lng_min, lat_max, lng_max : float
    network_type : {'walk', 'drive'}, optional
        Specify whether the network will be used for walking or driving.
        A value of 'walk' attempts to exclude things like freeways,
        while a value of 'drive' attempts to exclude things like
        bike and walking paths.
    two_way : bool, optional
        Whether the routes are two-way. If True, node pairs will only
        occur once.

    Returns
    -------
    network : pandana.Network

    """
    nodes, ways, waynodes = ways_in_bbox(
        lat_min, lng_min, lat_max, lng_max, network_type)
    pairs = node_pairs(nodes, ways, waynodes, two_way=two_way)

    # make the unique set of nodes that ended up in pairs
    node_ids = sorted(
        set(pairs['from_id'].unique()).union(set(pairs['to_id'].unique())))
    nodes = nodes.loc[node_ids]

    return Network(
        nodes['lon'], nodes['lat'],
        pairs['from_id'], pairs['to_id'], pairs[['distance']])


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
