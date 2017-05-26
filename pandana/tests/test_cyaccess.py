# test direct use of cyccess (c++/cython extension)

import pandas as pd
import numpy as np
import pytest
import os
from numpy.testing import assert_almost_equal
from pandana.cyaccess import cyaccess


@pytest.fixture(scope="module")
def nodes_and_edges(request):
    store = pd.HDFStore(
        os.path.join(os.path.dirname(__file__), 'osm_sample.h5'), "r")
    nodes = store.nodes
    edges = store.edges[["from", "to"]]
    edge_weights = store.edges[["weight"]]

    def fin():
        store.close()
    request.addfinalizer(fin)

    return nodes, edges, edge_weights


@pytest.fixture(scope="module")
def net(nodes_and_edges):
    nodes, edges, edge_weights = nodes_and_edges

    # this kinda sucks, but internally node ids are indexes, not
    node_locations = pd.Series(np.arange(len(nodes)), index=nodes.index)
    edges["from"] = node_locations.loc[edges["from"]].values
    edges["to"] = node_locations.loc[edges["to"]].values

    net = cyaccess(
        nodes.index.values,
        nodes.as_matrix(),
        edges.as_matrix(),
        edge_weights.transpose().as_matrix(),
        True
    )

    net.precompute_range(10)

    return net


def test_agg_analysis(net, nodes_and_edges):
    nodes = nodes_and_edges[0]
    NUM_NODES = 30
    net.initialize_access_vars(1)
    np.random.seed(0)
    random_node_ids = np.random.choice(np.arange(len(nodes)), NUM_NODES)
    random_vals = np.random.random(NUM_NODES) * 100
    net.initialize_access_var(0, random_node_ids, random_vals)
    ret = net.get_all_aggregate_accessibility_variables(10, 0, "sum", "flat")
    ret = pd.Series(ret)
    assert_almost_equal(ret[0], 159.208338, decimal=4)
    assert_almost_equal(ret[50], 94.466888, decimal=4)

    # test missing aggregation type
    ret = net.get_all_aggregate_accessibility_variables(10, 0, "this is", "bogus")
    assert np.alltrue(np.isnan(ret))


def test_poi_analysis(net, nodes_and_edges):
    nodes = nodes_and_edges[0]
    net.initialize_pois(1, 10, 3)
    NUM_NODES = 30
    np.random.seed(0)
    random_node_ids = np.random.choice(np.arange(len(nodes)), NUM_NODES)
    net.initialize_category(0, random_node_ids)
    ret = net.find_all_nearest_pois(10, 3, 0, 0, True)
    df = pd.DataFrame(ret)
    assert df.loc[0, 0] == 6
    assert df.loc[0, 1] == 25
    assert df.loc[0, 2] == 20
    s = df[0].value_counts()
    assert s[-1] == 1081
    assert s[5] == 1


def test_shortest_path(net):
    route = pd.Series(net.shortest_path(996, 71))
    # interestingly this route has two shortest poths both of length 24
    assert len(route) == 24
    assert route[12] == 1314
    assert route.iloc[20] == 345
    assert net.shortest_path_distance(996, 71) == 23
