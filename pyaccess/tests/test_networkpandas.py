import os.path

import numpy as np
import pandas as pd
import pytest

import pyaccess.networkpandas as nwp


@pytest.fixture(scope="module")
def sample_osm(request):
    store = pd.HDFStore(
        os.path.join(os.path.dirname(__file__), 'osm_sample.h5'), "r")
    nodes, edges = store.nodes, store.edges
    net = nwp.Network(nodes.x, nodes.y, edges["from"], edges.to,
                      edges[["weight"]])

    def fin():
        store.close()
    request.addfinalizer(fin)

    return net


def random_node_ids(net):
    return pd.Series(np.random.choice(net.node_ids, 50))


def test_create_network(sample_osm):
    # smoke test
    pass


def test_agg_variables(sample_osm):
    net = sample_osm

    net.set(random_node_ids(sample_osm))

    s = net.aggregate(500, type="ave", decay="flat")
    assert s.describe()['std'] > 0

    t = net.aggregate(1000, type="ave", decay="flat")
    assert t.describe()['std'] > 0

    u = net.aggregate(2000, type="ave", decay="flat")
    assert u.describe()['std'] > 0
