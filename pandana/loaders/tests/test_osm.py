import pytest

from pandana.loaders import osm


@pytest.fixture
def bbox():
    return 37.8659303546, -122.2588003879, 37.8661598571, -122.2585062512


def test_make_osm_query(bbox):
    data = osm.make_osm_query(*bbox)
    assert isinstance(data, dict)
    assert len(data['elements']) == 37
    assert len([e for e in data['elements'] if e['type'] == 'node']) == 33
    assert len([e for e in data['elements'] if e['type'] == 'way']) == 4
