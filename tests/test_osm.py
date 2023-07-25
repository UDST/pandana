import pytest

import pandana
from pandana.loaders import osm
from pandana.testing import skipifci


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


# This needs to be fixed in UrbanAccess
# @skipifci
# def test_network_from_bbox(bbox2):
#     net = osm.pdna_network_from_bbox(*bbox2)
#     assert isinstance(net, pandana.Network)


def test_build_node_query_no_tags(bbox1):
    query = osm.build_node_query(*bbox1)

    assert query == (
        '[out:json];'
        '('
        '  node'
        '  '
        '  ({},{},{},{});'
        ');'
        'out;').format(*bbox1)


def test_build_node_query_str_tag(bbox1):
    tag = '"tag"'
    query = osm.build_node_query(*bbox1, tags=tag)

    assert query == (
        '[out:json];'
        '('
        '  node'
        '  ["tag"]'
        '  ({},{},{},{});'
        ');'
        'out;').format(*bbox1)


def test_build_node_query_tag_list(bbox1):
    tags = ['"tag1"="tag1"', '"tag2"!~"tag2|tag2"']
    query = osm.build_node_query(*bbox1, tags=tags)

    assert query == (
        '[out:json];'
        '('
        '  node'
        '  ["tag1"="tag1"]["tag2"!~"tag2|tag2"]'
        '  ({},{},{},{});'
        ');'
        'out;').format(*bbox1)


def test_node_query(bbox2):
    tags = '"amenity"="restaurant"'
    cafes = osm.node_query(*bbox2, tags=tags)

    assert len(cafes) == 2
    assert 'lat' in cafes.columns
    assert 'lon' in cafes.columns
    assert cafes['name'][1419597327] == 'Cream'


def test_node_query_raises():
    with pytest.raises(RuntimeError):
        osm.node_query(37.8, -122.282, 37.8, -122.252)
