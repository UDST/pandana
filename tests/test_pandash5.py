import os
import tempfile

import pandas as pd
import pytest

from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

from pandana import Network
from pandana.loaders import pandash5 as ph5
from pandana.testing import skipifci


@pytest.fixture(scope='module')
def nodes():
    return pd.DataFrame(
        {'x': [1, 2, 3, 4] * 3,
         'y': [1] * 4 + [2] * 4 + [3] * 4})


@pytest.fixture(scope='module')
def edges():
    return pd.DataFrame(
        {'from': [0, 4, 5, 6, 2, 2, 6, 10, 9, 7],
         'to': [4, 5, 6, 2, 1, 3, 10, 9, 8, 11]})


@pytest.fixture(scope='module')
def impedance_names():
    return ['distance', 'time']


@pytest.fixture(scope='module')
def edge_weights(edges, impedance_names):
    return pd.DataFrame(
        {impedance_names[0]: [1] * len(edges),
         impedance_names[1]: list(range(1, len(edges) + 1))})


@pytest.fixture(scope='module')
def two_way():
    return True


@pytest.fixture(scope='module')
def network(nodes, edges, edge_weights, two_way):
    return Network(
        nodes['x'], nodes['y'], edges['from'], edges['to'], edge_weights,
        two_way)


@pytest.fixture(scope='module')
def edges_df(edges, edge_weights):
    return edges.join(edge_weights)


@pytest.fixture(scope='module')
def rm_nodes():
    return [0, 7, 6]


@pytest.fixture
def tmpfile(request):
    fname = tempfile.NamedTemporaryFile().name

    def cleanup():
        if os.path.exists(fname):
            os.remove(fname)
    request.addfinalizer(cleanup)

    return fname


@skipifci
def test_remove_nodes(network, rm_nodes):
    # node 0 is connected to node 4, which is in turn connected to node 5
    # node 7 is connected to node 11, which has no other connections
    # node 6 is connected to nodes 2, 5, and 10,
    #     which all have other connections
    nodes, edges = ph5.remove_nodes(network, rm_nodes)

    exp_nodes = pd.DataFrame(
        {'x': [2, 3, 4, 1, 2, 1, 2, 3, 4],
         'y': [1, 1, 1, 2, 2, 3, 3, 3, 3]},
        index=[1, 2, 3, 4, 5, 8, 9, 10, 11])

    exp_edges = pd.DataFrame(
        {'from': [4, 2, 2, 10, 9],
         'to': [5, 1, 3, 9, 8],
         'distance': [1, 1, 1, 1, 1],
         'time': [2, 5, 6, 8, 9]},
        index=[1, 4, 5, 7, 8])
    exp_edges = exp_edges[['from', 'to', 'distance', 'time']]  # order columns

    assert_frame_equal(nodes, exp_nodes)
    assert_frame_equal(edges, exp_edges)


@skipifci
def test_network_to_pandas_hdf5(
        tmpfile, network, nodes, edges_df, impedance_names, two_way):
    ph5.network_to_pandas_hdf5(network, tmpfile)

    store = pd.HDFStore(tmpfile)

    assert_frame_equal(store['nodes'], nodes)
    assert_frame_equal(store['edges'], edges_df)
    assert_series_equal(store['two_way'], pd.Series([two_way]))
    assert_series_equal(
        store['impedance_names'], pd.Series(impedance_names))


@skipifci
def test_network_to_pandas_hdf5_removal(
        tmpfile, network, impedance_names, two_way, rm_nodes):
    nodes, edges = ph5.remove_nodes(network, rm_nodes)
    ph5.network_to_pandas_hdf5(network, tmpfile, rm_nodes)

    store = pd.HDFStore(tmpfile)

    assert_frame_equal(store['nodes'], nodes)
    assert_frame_equal(store['edges'], edges)
    assert_series_equal(store['two_way'], pd.Series([two_way]))
    assert_series_equal(
        store['impedance_names'], pd.Series(impedance_names))


@skipifci
def test_network_from_pandas_hdf5(
        tmpfile, network, nodes, edges_df, impedance_names, two_way):
    ph5.network_to_pandas_hdf5(network, tmpfile)
    new_net = ph5.network_from_pandas_hdf5(Network, tmpfile)

    assert_frame_equal(new_net.nodes_df, nodes)
    assert_frame_equal(new_net.edges_df, edges_df)
    assert new_net._twoway == two_way
    assert new_net.impedance_names == impedance_names


@skipifci
def test_network_save_load_hdf5(
        tmpfile, network, impedance_names, two_way, rm_nodes):
    network.save_hdf5(tmpfile, rm_nodes)
    new_net = Network.from_hdf5(tmpfile)

    nodes, edges = ph5.remove_nodes(network, rm_nodes)

    assert_frame_equal(new_net.nodes_df, nodes)
    assert_frame_equal(new_net.edges_df, edges)
    assert new_net._twoway == two_way
    assert new_net.impedance_names == impedance_names


# this is an odd place for this test because it's not related to HDF5,
# but my test Network is perfect.
@skipifci
def test_network_low_connectivity_nodes(network, impedance_names):
    nodes = network.low_connectivity_nodes(10, 3, imp_name=impedance_names[0])
    assert list(nodes) == [7, 11]
