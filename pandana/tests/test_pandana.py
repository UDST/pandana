import os.path

import numpy as np
from numpy.testing import assert_allclose
import pandas as pd
import pytest
from pandas.util import testing as pdt
from pandana.testing import skipiftravis

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


# initialize a second network
@pytest.fixture(scope="module")
def second_sample_osm(request):
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


def get_connected_nodes(net):
    net.set(pd.Series(net.node_ids))
    s = net.aggregate(10000, type="COUNT")
    # not all the nodes in the sample network are connected
    # get the nodes in the largest connected subgraph
    # from printing the result out I know the largest subgraph has
    # 477 nodes in the sample data
    connected_nodes = s[s == 477].index.values
    return connected_nodes


def random_connected_nodes(net, ssize):
    return pd.Series(np.random.choice(get_connected_nodes(net), ssize))


def random_x_y(sample_osm, ssize):
    bbox = sample_osm.bbox
    x = pd.Series(np.random.uniform(bbox[0], bbox[2], ssize))
    y = pd.Series(np.random.uniform(bbox[1], bbox[3], ssize))
    return x, y


def test_create_network(sample_osm):
    # smoke test
    pass


def test_agg_variables_accuracy(sample_osm):
    net = sample_osm

    # test accuracy compared to pandas functions
    ssize = 50
    r = random_data(ssize)
    connected_nodes = get_connected_nodes(net)
    nodes = random_connected_nodes(net, ssize)
    net.set(nodes, variable=r)

    s = net.aggregate(100000, type="COUNT").loc[connected_nodes]
    assert s.unique().size == 1
    assert s.iloc[0] == 50

    s = net.aggregate(100000, type="AVE").loc[connected_nodes]
    assert s.describe()['std'] < .01  # assert almost equal
    assert_allclose(s.mean(), r.mean(), atol=1e-3)

    s = net.aggregate(100000, type="MIN").loc[connected_nodes]
    assert s.describe()['std'] < .01  # assert almost equal
    assert_allclose(s.mean(), r.min(), atol=1e-3)

    s = net.aggregate(100000, type="MAX").loc[connected_nodes]
    assert s.describe()['std'] < .01  # assert almost equal
    assert_allclose(s.mean(), r.max(), atol=1e-3)

    r.sort_values(inplace=True)

    s = net.aggregate(100000, type="MEDIAN").loc[connected_nodes]
    assert s.describe()['std'] < .01  # assert almost equal
    assert_allclose(s.mean(), r.iloc[25], atol=1e-2)

    s = net.aggregate(100000, type="25PCT").loc[connected_nodes]
    assert s.describe()['std'] < .01  # assert almost equal
    assert_allclose(s.mean(), r.iloc[12], atol=1e-2)

    s = net.aggregate(100000, type="75PCT").loc[connected_nodes]
    assert s.describe()['std'] < .01  # assert almost equal
    assert_allclose(s.mean(), r.iloc[37], atol=1e-2)

    s = net.aggregate(100000, type="SUM").loc[connected_nodes]
    assert s.describe()['std'] < .05  # assert almost equal
    assert_allclose(s.mean(), r.sum(), atol=1e-2)

    s = net.aggregate(100000, type="STD").loc[connected_nodes]
    assert s.describe()['std'] < .01  # assert almost equal
    assert_allclose(s.mean(), r.std(), atol=1e-2)


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


def test_shortest_path(sample_osm):

    for i in range(10):
        ids = random_connected_nodes(sample_osm, 2)
        path = sample_osm.shortest_path(ids[0], ids[1])
        assert path.size >= 2
        assert ids[0] == path[0]
        assert ids[1] == path[-1]


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

    net = sample_osm
    x, y = random_x_y(sample_osm, 100)
    x.index = ['lab%d' % i for i in range(len(x))]
    y.index = x.index

    net.set_pois("restaurants", x, y)

    d = net.nearest_pois(2000, "restaurants", num_pois=10,
                         include_poi_ids=True)


@skipiftravis
def test_pois2(second_sample_osm):
    net2 = second_sample_osm

    ssize = 50
    np.random.seed(0)
    x, y = random_x_y(second_sample_osm, ssize)

    # make sure poi searches work on second graph
    net2.init_pois(num_categories=1, max_dist=2000, max_pois=10)

    net2.set_pois("restaurants", x, y)

    print(net2.nearest_pois(2000, "restaurants", num_pois=10))
