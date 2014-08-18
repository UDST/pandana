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


def random_node_ids(net, ssize):
    return pd.Series(np.random.choice(net.node_ids, ssize))


def random_data(ssize):
    return pd.Series(np.random.random(ssize))


def test_create_network(sample_osm):
    _ = sample_osm
    # good enough
    return


def test_agg_variables(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(random_node_ids(sample_osm, ssize),
            variable=random_data(ssize))

    for type in nwp.AGGREGATIONS:
        for decay in nwp.DECAYS:
            for distance in [500, 1000, 2000]:
                s = net.aggregate(distance, type=type, decay=decay)
                assert s.describe()['std'] > 0

    # testing w/o setting variable
    ssize = 50
    net.set(random_node_ids(sample_osm, ssize))

    for type in nwp.AGGREGATIONS:
        for decay in nwp.DECAYS:
            for distance in [500, 1000, 2000]:
                s = net.aggregate(distance, type=type, decay=decay)
                if type != "STD":
                    assert s.describe()['std'] > 0
                else:
                    # no variance in data
                    assert s.describe()['std'] == 0