import pandas as pd
import numpy as np
import pytest
from .. import networkpandas as nwp


@pytest.fixture(scope="module")
def sample_osm():
    store = pd.HDFStore('osm_sample.h5', "r")
    nodes, edges = store.nodes, store.edges
    net = nwp.Network(nodes.x, nodes.y, edges["from"], edges.to,
                      edges[["weight"]])
    return net


def random_node_ids(net):
    return pd.Series(np.random.choice(net.node_ids, 50))


def test_create_network(sample_osm):
    _ = sample_osm
    # good enough
    return


def test_agg_variables(sample_osm):
    net = sample_osm

    net.set(random_node_ids(sample_osm))

    s = net.aggregate(500, type="ave", decay="flat")
    assert s.describe()['std'] > 0

    t = net.aggregate(1000, type="ave", decay="flat")
    assert t.describe()['std'] > 0

    u = net.aggregate(2000, type="ave", decay="flat")
    assert u.describe()['std'] > 0
