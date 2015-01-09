import numpy.testing as npt
import pandas.util.testing as pdt
import pytest

import pandana
from pandana.loaders import osm


@pytest.fixture(scope='module')
def bbox1():
    # Intersection of Telegraph and Haste in Berkeley
    # Sample query: http://overpass-turbo.eu/s/6AK
    return 37.8659303546, -122.2588003879, 37.8661598571, -122.2585062512


@pytest.fixture(scope='module')
def bbox2():
    # Telegraph Channing to Durant in Berkeley
    # Sample query: http://overpass-turbo.eu/s/6B0
    return 37.8668405874, -122.2590948685, 37.8679028054, -122.2586363885


@pytest.fixture(scope='module')
def bbox3():
    # West Berkeley including highway 80, frontage roads, and foot paths
    # Sample query: http://overpass-turbo.eu/s/6VE
    return (
        37.85225504880375, -122.30295896530151,
        37.85776128099243, - 122.2954273223877)


@pytest.fixture(scope='module')
def query_data1(bbox1):
    return osm.make_osm_query(*bbox1)


@pytest.fixture(scope='module')
def query_data2(bbox2):
    return osm.make_osm_query(*bbox2)


@pytest.fixture(scope='module')
def dataframes1(query_data1):
    return osm.parse_osm_query(query_data1)


@pytest.fixture(scope='module')
def dataframes2(query_data2):
    return osm.parse_osm_query(query_data2)


def test_make_osm_query(query_data1):
    assert isinstance(query_data1, dict)
    assert len(query_data1['elements']) == 24
    assert len(
        [e for e in query_data1['elements'] if e['type'] == 'node']) == 22
    assert len([e for e in query_data1['elements'] if e['type'] == 'way']) == 2


def test_process_node():
    test_node = {
        'id': 'id',
        'lat': 'lat',
        'lon': 'lon',
        'extra': 'extra'
    }

    expected = {
        'id': 'id',
        'lat': 'lat',
        'lon': 'lon'
    }

    assert osm.process_node(test_node) == expected

    test_node['tags'] = {'highway': 'highway', 'source': 'source'}
    expected['highway'] = 'highway'

    assert osm.process_node(test_node) == expected


def test_process_way():
    test_way = {
        "type": "way",
        "id": 188434143,
        "timestamp": "2014-01-04T22:18:14Z",
        "version": 2,
        "changeset": 19814115,
        "user": "dchiles",
        "uid": 153669,
        "nodes": [
            53020977,
            53041093,
        ],
        "tags": {
            'source': 'source',
            "addr:city": "Berkeley",
            "highway": "secondary",
            "name": "Telegraph Avenue",
        }
    }

    expected_way = {
        'id': test_way['id'],
        'addr:city': test_way['tags']['addr:city'],
        'highway': test_way['tags']['highway'],
        'name': test_way['tags']['name']
    }

    expected_waynodes = [
        {'way_id': test_way['id'], 'node_id': test_way['nodes'][0]},
        {'way_id': test_way['id'], 'node_id': test_way['nodes'][1]}
    ]

    way, waynodes = osm.process_way(test_way)

    assert way == expected_way
    assert waynodes == expected_waynodes


def test_parse_osm_query(dataframes1):
    nodes, ways, waynodes = dataframes1

    assert len(nodes) == 22
    assert len(ways) == 2
    assert len(waynodes.index.unique()) == 2


def test_ways_in_bbox(bbox1, dataframes1):
    nodes, ways, waynodes = osm.ways_in_bbox(*bbox1)
    exp_nodes, exp_ways, exp_waynodes = dataframes1

    pdt.assert_frame_equal(nodes, exp_nodes)
    pdt.assert_frame_equal(ways, exp_ways)
    pdt.assert_frame_equal(waynodes, exp_waynodes)


@pytest.mark.parametrize(
    'network, noset',
    [('walk', {'motorway', 'motorway_link'}),
     ('drive', {'footway', 'cycleway'})])
def test_ways_in_bbox_walk_network(bbox3, network, noset):
    nodes, ways, waynodes = osm.ways_in_bbox(*bbox3, network=network)

    for _, way in ways.iterrows():
        assert way['highway'] not in noset


def test_intersection_nodes1(dataframes1):
    _, _, waynodes = dataframes1
    intersections = osm.intersection_nodes(waynodes)

    assert intersections == {53041093}


def test_intersection_nodes2(dataframes2):
    _, _, waynodes = dataframes2
    intersections = osm.intersection_nodes(waynodes)

    assert intersections == {53099275, 53063555}


def test_node_pairs_two_way(dataframes2):
    nodes, ways, waynodes = dataframes2
    pairs = osm.node_pairs(nodes, ways, waynodes)

    assert len(pairs) == 1

    fn = 53063555
    tn = 53099275

    pair = pairs.loc[(fn, tn)]

    assert pair.from_id == fn
    assert pair.to_id == tn
    npt.assert_allclose(pair.distance, 101.20535797547758)


def test_node_pairs_one_way(dataframes2):
    nodes, ways, waynodes = dataframes2
    pairs = osm.node_pairs(nodes, ways, waynodes, two_way=False)

    assert len(pairs) == 2

    n1 = 53063555
    n2 = 53099275

    for p1, p2 in [(n1, n2), (n2, n1)]:
        pair = pairs.loc[(p1, p2)]

        assert pair.from_id == p1
        assert pair.to_id == p2
        npt.assert_allclose(pair.distance, 101.20535797547758)


def test_network_from_bbox(bbox2):
    net = osm.network_from_bbox(*bbox2)
    assert isinstance(net, pandana.Network)
