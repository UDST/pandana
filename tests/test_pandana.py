import os.path

import numpy as np
import pandas as pd
import pytest

import pandana.network as pdna

from numpy.testing import assert_allclose
from pandas.testing import assert_index_equal

from pandana.testing import skipifci


@pytest.fixture(scope="module")
def sample_osm(request):
    store = pd.HDFStore(os.path.join(os.path.dirname(__file__), "osm_sample.h5"), "r")
    nodes, edges = store.nodes, store.edges

    net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to, edges[["weight"]])

    net.precompute(2000)

    def fin():
        store.close()

    request.addfinalizer(fin)

    return net


# initialize a second network
@pytest.fixture(scope="module")
def second_sample_osm(request):
    store = pd.HDFStore(os.path.join(os.path.dirname(__file__), "osm_sample.h5"), "r")
    nodes, edges = store.nodes, store.edges
    net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to, edges[["weight"]])

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


def test_agg_variables_accuracy(sample_osm):
    net = sample_osm

    # test accuracy compared to Pandas functions
    ssize = 50
    r = random_data(ssize)
    connected_nodes = get_connected_nodes(net)
    nodes = random_connected_nodes(net, ssize)
    net.set(nodes, variable=r)

    s = net.aggregate(100000, type="count").loc[connected_nodes]
    assert s.unique().size == 1
    assert s.iloc[0] == 50

    s = net.aggregate(100000, type="AVE").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.mean(), atol=1e-3)

    s = net.aggregate(100000, type="mean").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.mean(), atol=1e-3)

    s = net.aggregate(100000, type="min").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.min(), atol=1e-3)

    s = net.aggregate(100000, type="max").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.max(), atol=1e-3)

    r.sort_values(inplace=True)

    s = net.aggregate(100000, type="median").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.iloc[25], atol=1e-2)

    s = net.aggregate(100000, type="25pct").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.iloc[12], atol=1e-2)

    s = net.aggregate(100000, type="75pct").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.iloc[37], atol=1e-2)

    s = net.aggregate(100000, type="SUM").loc[connected_nodes]
    assert s.describe()["std"] < 0.05  # assert almost equal
    assert_allclose(s.mean(), r.sum(), atol=1e-2)

    s = net.aggregate(100000, type="std").loc[connected_nodes]
    assert s.describe()["std"] < 0.01  # assert almost equal
    assert_allclose(s.mean(), r.std(), atol=1e-2)


def test_non_integer_nodeids(request):

    store = pd.HDFStore(os.path.join(os.path.dirname(__file__), "osm_sample.h5"), "r")
    nodes, edges = store.nodes, store.edges

    # convert to string!
    nodes.index = nodes.index.astype("str")
    edges["from"] = edges["from"].astype("str")
    edges["to"] = edges["to"].astype("str")

    net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to, edges[["weight"]])

    def fin():
        store.close()

    request.addfinalizer(fin)

    # test accuracy compared to Pandas functions
    ssize = 50
    r = random_data(ssize)
    connected_nodes = get_connected_nodes(net)
    random_nodes = random_connected_nodes(net, ssize)
    net.set(random_nodes, variable=r)

    s = net.aggregate(100000, type="count").loc[connected_nodes]
    assert list(nodes.index), list(s.index)


def test_agg_variables(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(random_node_ids(sample_osm, ssize), variable=random_data(ssize))

    for type in net.aggregations:
        for decay in net.decays:
            for distance in [5, 10, 20]:
                t = type.decode(encoding="UTF-8")
                d = decay.decode(encoding="UTF-8")
                s = net.aggregate(distance, type=t, decay=d)
                assert s.describe()["std"] > 0

    # testing w/o setting variable
    ssize = 50
    net.set(random_node_ids(sample_osm, ssize))

    for type in net.aggregations:
        for decay in net.decays:
            for distance in [5, 10, 20]:
                t = type.decode(encoding="UTF-8")
                d = decay.decode(encoding="UTF-8")
                s = net.aggregate(distance, type=t, decay=d)
                if t != "std":
                    assert s.describe()["std"] > 0
                else:
                    # no variance in data
                    assert s.describe()["std"] == 0


def test_non_float_node_values(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(
        random_node_ids(sample_osm, ssize),
        variable=(random_data(ssize) * 100).astype("int"),
    )

    for type in net.aggregations:
        for decay in net.decays:
            for distance in [5, 10, 20]:
                t = type.decode(encoding="UTF-8")
                d = decay.decode(encoding="UTF-8")
                s = net.aggregate(distance, type=t, decay=d)
                assert s.describe()["std"] > 0


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
    # check a couple of assignments for accuracy
    assert node_ids1.loc[48] == 1840703798
    assert node_ids1.loc[43] == 257739973
    assert_index_equal(x.index, node_ids1.index)

    # test with max distance - this max distance is in decimal degrees
    node_ids2 = sample_osm.get_node_ids(x, y, 0.0005)
    assert 0 < len(node_ids2) < ssize
    assert len(node_ids2) < len(node_ids1), "Max distance not working"
    assert len(node_ids2) == 14

    node_ids3 = sample_osm.get_node_ids(x, y, 0)
    assert len(node_ids3) == 0


def test_named_variable(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(random_node_ids(sample_osm, ssize), variable=random_data(ssize), name="foo")

    net.aggregate(500, type="sum", decay="linear", name="foo")


"""
def test_plot(sample_osm):
    net = sample_osm

    ssize = 50
    net.set(random_node_ids(sample_osm, ssize),
            variable=random_data(ssize))

    s = net.aggregate(500, type="sum", decay="linear")

    sample_osm.plot(s)
"""


def test_shortest_path(sample_osm):

    for i in range(10):
        ids = random_connected_nodes(sample_osm, 2)
        path = sample_osm.shortest_path(ids[0], ids[1])
        assert path.size >= 2
        assert ids[0] == path[0]
        assert ids[1] == path[-1]


def test_shortest_paths(sample_osm):

    nodes = random_connected_nodes(sample_osm, 100)
    vec_paths = sample_osm.shortest_paths(nodes[0:50], nodes[50:100])

    for i in range(50):
        path = sample_osm.shortest_path(nodes[i], nodes[i + 50])
        assert np.array_equal(vec_paths[i], path)

    # check mismatched OD lists
    try:
        vec_paths = sample_osm.shortest_paths(nodes[0:51], nodes[50:100])
        assert 0
    except ValueError as e:
        pass


def test_shortest_path_length(sample_osm):

    for i in range(10):
        ids = random_connected_nodes(sample_osm, 2)
        len = sample_osm.shortest_path_length(ids[0], ids[1])
        assert len >= 0


def test_shortest_path_lengths(sample_osm):

    nodes = random_connected_nodes(sample_osm, 100)
    lens = sample_osm.shortest_path_lengths(nodes[0:50], nodes[50:100])
    for len in lens:
        assert len >= 0

    # check mismatched OD lists
    try:
        lens = sample_osm.shortest_path_lengths(nodes[0:51], nodes[50:100])
        assert 0
    except ValueError as e:
        pass


def test_pois(sample_osm):
    net = sample_osm

    ssize = 50
    np.random.seed(0)
    x, y = random_x_y(sample_osm, ssize)

    with pytest.raises(AssertionError):
        net.nearest_pois(2000, "restaurants", num_pois=10)

    with pytest.raises(AssertionError):
        net.nearest_pois(2000, "restaurants", num_pois=10)

    # boundary condition
    net.set_pois("restaurants", 2000, 10, x, y)

    net.nearest_pois(2000, "restaurants", num_pois=10)

    with pytest.raises(AssertionError):
        net.nearest_pois(2000, "restaurants", num_pois=11)

    net = sample_osm
    x, y = random_x_y(sample_osm, 100)
    x.index = ["lab%d" % i for i in range(len(x))]
    y.index = x.index

    net.set_pois("restaurants", 2000, 10, x, y)

    d = net.nearest_pois(2000, "restaurants", num_pois=10, include_poi_ids=True)


def test_pois2(second_sample_osm):
    net2 = second_sample_osm

    ssize = 50
    np.random.seed(0)
    x, y = random_x_y(second_sample_osm, ssize)

    # make sure POI searches work on second graph
    net2.set_pois("restaurants", 2000, 10, x, y)

    net2.nearest_pois(2000, "restaurants", num_pois=10)


def test_pois_pandana3(second_sample_osm):
    net2 = second_sample_osm

    ssize = 50
    np.random.seed(0)
    x, y = random_x_y(second_sample_osm, ssize)
    pdna.reserve_num_graphs(1)

    net2.init_pois(num_categories=1, max_dist=2000, max_pois=10)

    # make sure POI searches work on second graph
    net2.set_pois(category="restaurants", x_col=x, y_col=y)

    net2.nearest_pois(2000, "restaurants", num_pois=10)


def test_pois_pandana3_pos_args(second_sample_osm):
    net2 = second_sample_osm

    ssize = 50
    np.random.seed(0)
    x, y = random_x_y(second_sample_osm, ssize)
    pdna.reserve_num_graphs(1)

    net2.init_pois(1, 2000, 10)

    # make sure poi searches work on second graph
    net2.set_pois("restaurants", x, y)

    net2.nearest_pois(2000, "restaurants", num_pois=10)


# test items are sorted


def test_sorted_pois(sample_osm):
    net = sample_osm

    ssize = 1000
    x, y = random_x_y(sample_osm, ssize)

    # set two categories
    net.set_pois("restaurants", 2000, 10, x, y)

    test = net.nearest_pois(2000, "restaurants", num_pois=10)

    for ind, row in test.iterrows():
        # make sure it's sorted
        assert_allclose(row, row.sort_values())


def test_repeat_pois(sample_osm):
    net = sample_osm

    def get_nearest_nodes(x, y, x2=None, y2=None, n=2):
        coords_dict = [{"x": x, "y": y, "var": 1} for i in range(2)]
        if x2 and y2:
            coords_dict.append({"x": x2, "y": y2, "var": 1})
        df = pd.DataFrame(coords_dict)
        sample_osm.set_pois("restaurants", 2000, 10, df["x"], df["y"])
        res = sample_osm.nearest_pois(
            2000, "restaurants", num_pois=5, include_poi_ids=True
        )
        return res

    # these are the min-max values of the network
    # -122.3383688 -122.2962223
    # 47.5950005 47.6150548

    test1 = get_nearest_nodes(-122.31, 47.60)
    test2 = get_nearest_nodes(-122.254116, 37.869361)
    # Same coords as the first call, should yield same result
    test3 = get_nearest_nodes(-122.31, 47.60)
    assert test1.equals(test3)

    test4 = get_nearest_nodes(-122.31, 47.60, -122.32, 47.61, n=3)
    assert_allclose(
        test4.loc[53114882], [7, 13, 13, 2000, 2000, 2, 0, 1, np.nan, np.nan]
    )
    assert_allclose(
        test4.loc[53114880], [6, 14, 14, 2000, 2000, 2, 0, 1, np.nan, np.nan]
    )
    assert_allclose(
        test4.loc[53227769],
        [2000, 2000, 2000, 2000, 2000, np.nan, np.nan, np.nan, np.nan, np.nan],
    )


def test_nodes_in_range(sample_osm):
    net = sample_osm

    np.random.seed(0)
    ssize = 10
    x, y = random_x_y(net, 10)
    snaps = net.get_node_ids(x, y)

    test1 = net.nodes_in_range(snaps, 1)
    net.precompute(10)
    test5 = net.nodes_in_range(snaps, 5)
    test11 = net.nodes_in_range(snaps, 11)
    assert test1.weight.max() == 1
    assert test5.weight.max() == 5
    assert test11.weight.max() == 11

    focus_id = snaps[0]
    all_distances = net.shortest_path_lengths(
        [focus_id] * len(net.node_ids), net.node_ids
    )
    all_distances = np.asarray(all_distances)
    assert (all_distances <= 1).sum() == len(
        test1.query("source == {}".format(focus_id))
    )
    assert (all_distances <= 5).sum() == len(
        test5.query("source == {}".format(focus_id))
    )
    assert (all_distances <= 11).sum() == len(
        test11.query("source == {}".format(focus_id))
    )
