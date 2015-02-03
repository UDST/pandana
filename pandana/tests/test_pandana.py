import os.path

import numpy as np
import pandas as pd
import pytest
from pandas.util import testing as pdt

import pandana.network as pdna


''' TODO - add tests for
set and aggregate with multiple impedances
multiple graphs
one way streets
'''


@pytest.fixture(scope="module")
def sample_osm(request):
    store = pd.HDFStore(
        os.path.join(os.path.dirname(__file__), 'osm_sample.h5'), "r")
    nodes, edges = store.nodes, store.edges
    net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to,
                       edges[["weight"]])

    net.precompute(2000)

    def fin():
        store.close()
    request.addfinalizer(fin)

    return net


def random_node_ids(net, ssize):
    return pd.Series(np.random.choice(net.node_ids, ssize))


def random_data(ssize):
    return pd.Series(np.random.random(ssize))


def random_x_y(sample_osm, ssize):
    bbox = sample_osm.bbox
    x = pd.Series(np.random.uniform(bbox[0], bbox[2], ssize))
    y = pd.Series(np.random.uniform(bbox[1], bbox[3], ssize))
    return x, y


def test_create_network(sample_osm):
    # smoke test
    pass


def test_agg_variables(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(random_node_ids(sample_osm, ssize),
            variable=random_data(ssize))

    for type in pdna.AGGREGATIONS:
        for decay in pdna.DECAYS:
            for distance in [500, 1000, 2000]:
                s = net.aggregate(distance, type=type, decay=decay)
                assert s.describe()['std'] > 0

    # testing w/o setting variable
    ssize = 50
    net.set(random_node_ids(sample_osm, ssize))

    for type in pdna.AGGREGATIONS:
        for decay in pdna.DECAYS:
            for distance in [500, 1000, 2000]:
                s = net.aggregate(distance, type=type, decay=decay)
                if type != "STD" and type != "STDDEV":
                    assert s.describe()['std'] > 0
                else:
                    # no variance in data
                    assert s.describe()['std'] == 0


def test_missing_nodeid(sample_osm):
    node_ids = random_node_ids(sample_osm, 50)
    # non-existing value
    node_ids.iloc[0] = -1
    sample_osm.set(node_ids)


def test_assign_nodeids(sample_osm):
    ssize = 50
    np.random.seed(0)
    x, y = random_x_y(sample_osm, ssize)
    node_ids1 = sample_osm.get_node_ids(x, y)
    assert len(node_ids1) == ssize
    pdt.assert_index_equal(x.index, node_ids1.index)

    # test with max distance - this max distance is in decimal degrees
    node_ids2 = sample_osm.get_node_ids(x, y, 0.001)
    assert 0 < len(node_ids2) < ssize
    assert len(node_ids2) < len(node_ids1), "Max distance not working"

    node_ids3 = sample_osm.get_node_ids(x, y, 0)
    assert len(node_ids3) == 0


def test_named_variable(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(random_node_ids(sample_osm, ssize),
            variable=random_data(ssize), name="foo")

    net.aggregate(500, type="sum", decay="linear", name="foo")


def test_plot(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(random_node_ids(sample_osm, ssize),
            variable=random_data(ssize))

    s = net.aggregate(500, type="sum", decay="linear")

    sample_osm.plot(s)


def test_pois(sample_osm):
    net = sample_osm

    ssize = 50
    np.random.seed(0)
    x, y = random_x_y(sample_osm, ssize)

    with pytest.raises(AssertionError):
        net.set_pois("restaurants", x, y)

    with pytest.raises(AssertionError):
        net.nearest_pois(2000, "restaurants", num_pois=10)

    net.init_pois(num_categories=1, max_dist=2000, max_pois=10)

    with pytest.raises(AssertionError):
        net.nearest_pois(2000, "restaurants", num_pois=10)

    # boundary condition
    net.init_pois(num_categories=1, max_dist=2000, max_pois=10)

    net.set_pois("restaurants", x, y)

    net.nearest_pois(2000, "restaurants", num_pois=10)

    with pytest.raises(AssertionError):
        net.nearest_pois(2000, "restaurants", num_pois=11)
