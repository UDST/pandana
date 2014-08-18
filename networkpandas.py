import _pyaccess
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import brewer2mpl

NUM_NETWORKS = 0
NETWORKS = {}
VAR_NAME_TO_IND = {}
CAT_NAME_TO_IND = {}

AGGREGATIONS = {
    "SUM": 0,
    "AVE": 1,
    "STD": 5,
    "COUNT": 6
}

DECAYS = {
    "EXP": 0,
    "LINEAR": 1,
    "FLAT": 2
}


def reserve_num_graphs(num):
    global NUM_NETWORKS
    assert NUM_NETWORKS == 0, "Global memory used so cannot initialize twice"
    assert num > 0
    NUM_NETWORKS = num
    _pyaccess.create_graphs(num)


def from_networkx(G):
    nids = []
    lats = []
    lons = []
    for n in G.nodes_iter():
        n = G.node[n]['data']
        nids.append(n.id)
        lats.append(n.lat)
        lons.append(n.lon)
    nodes = pd.DataFrame({'x': lons, 'y': lats}, index=nids)

    froms = []
    tos = []
    weights = []
    for e in G.edges_iter():
        e = G.get_edge_data(*e)['data']
        #print e
        froms.append(G.node[e.nds[0]]['data'].id)
        tos.append(G.node[e.nds[1]]['data'].id)
        #print e.tags
        weights.append(1)
    edges = pd.DataFrame({'from': froms, 'to': tos, 'weight': weights})

    return nodes, edges


class Network:

    def _node_indexes(self, node_ids):
        df = pd.merge(pd.DataFrame({"node_ids": node_ids}),
                      pd.DataFrame({"node_idx": self.node_idx}),
                      left_on="node_ids",
                      right_index=True,
                      how="left")
        return df.node_idx

    @property
    def node_ids(self):
        return self.node_idx.index

    @property
    def nodes(self):
        return self.nodes

    def __init__(self, name, nodes_df, edges_df, xcol='x', ycol='y',
                 fromcol='from', tocol='to', weights_cols=['weight'],
                 twoway=False, mapping_distance=-1):

        if NUM_NETWORKS == 0:
            reserve_num_graphs(1)

        assert len(NETWORKS) < NUM_NETWORKS, "Adding more networks than have " \
                                             "been reserved"

        self.graph_no = len(NETWORKS)
        self.node_idx = pd.Series(np.arange(len(nodes_df)),
                                  index=nodes_df.index)
        self.nodes = nodes_df[[xcol, ycol]]
        self.mapping_distance = mapping_distance
        self.weights_cols = weights_cols

        NETWORKS[name] = self.graph_no

        edges = pd.concat([self._node_indexes(edges_df[fromcol]),
                           self._node_indexes(edges_df[tocol])], axis=1)

        _pyaccess.create_graph(self.graph_no,
                               nodes_df.index.astype('int32'),
                               nodes_df[[xcol, ycol]].astype('float32'),
                               edges.astype('int32'),
                               edges_df[weights_cols].transpose()
                                   .astype('float32'),
                               twoway)

    def initialize(self, df, node_id_col="node_id", col=None, name="tmp"):

        t1 = time.time()
        if col:
            df = df.dropna(subset=[col])
        print "up %.3f" % (time.time()-t1)

        t1 = time.time()
        if isinstance(node_id_col, str):
            l = len(df)
            df = df.dropna(subset=[node_id_col])
            newl = len(df)
            if newl-l > 0:
                print "Removed %d rows because there are missing node_ids" % \
                      (newl-l)
            node_ids = df[node_id_col].astype("int32")
        print "up %.3f" % (time.time()-t1)

        t1 = time.time()
        # aggregating ones if there aren't actual values to aggregate
        # like, could be lat/long for locations of coffee shops rather
        # than a continuous floating point vector
        aggvar = df[col].astype('float32') if col is not None else \
            np.ones(len(df.index), dtype='float32')
        print "up %.3f" % (time.time()-t1)

        t1 = time.time()
        if name in VAR_NAME_TO_IND:
            varnum = VAR_NAME_TO_IND[name]
        else:
            _pyaccess.initialize_acc_vars(self.graph_no, len(VAR_NAME_TO_IND)+1)
            varnum = VAR_NAME_TO_IND[name] = len(VAR_NAME_TO_IND)
        print "up %.3f" % (time.time()-t1)

        t1 = time.time()
        node_idxs = self._node_indexes(node_ids).values.astype('int32')
        print "%.3f" % (time.time()-t1)

        t1 = time.time()
        _pyaccess.initialize_acc_var(self.graph_no,
                                     varnum,
                                     node_idxs,
                                     aggvar)
        print "%.3f" % (time.time()-t1)

    def precompute(self, distance):
        _pyaccess.precompute_range(distance, self.graph_no)

    def compute(self, distance, agg="sum", decay="linear", imp_name=None,
                name="tmp"):

        agg = AGGREGATIONS[agg.upper()]
        decay = DECAYS[decay.upper()]

        if imp_name is None:
            assert len(self.weights_cols) == 1,\
                "must pass impedance name if there are multiple impedances set"
            imp_name = self.weights_cols[0]

        imp_num = self.weights_cols.index(imp_name)

        gno = self.graph_no

        assert name in VAR_NAME_TO_IND, "A variable with that name has not " \
                                        "yet been initialized"
        varnum = VAR_NAME_TO_IND[name]

        res = _pyaccess.get_all_aggregate_accessibility_variables(distance,
                                                                  varnum,
                                                                  agg,
                                                                  decay,
                                                                  gno,
                                                                  imp_num)

        return pd.Series(res, index=self.node_ids)

    def add_node_ids(self, df, xname='x', yname='y', node_id_col="node_id"):
        xys = df[[xname, yname]]
        # no limit to the mapping distance
        node_ids = _pyaccess.xy_to_node(xys,
                                        self.mapping_distance,
                                        self.graph_no)
        df[node_id_col] = node_ids
        return df

    def plot(self, s, width=24, height=30, dpi=300, color='YlGn', numbins=7):
        df = pd.DataFrame({'x': self.nodes.x.values,
                           'y': self.nodes.y.values,
                           'z': s.values})
        plt.figure(num=None, figsize=(width, height), dpi=dpi, edgecolor='k')
        plt.scatter(df.x, df.y, c=df.z,
                    cmap=brewer2mpl.get_map(color, 'sequential', numbins).
                    mpl_colormap,
                    edgecolors='grey',
                    linewidths=0.1)

    def initialize_pois(self, numcategories, maxdist, maxitems):
        _pyaccess.initialize_pois(numcategories, maxdist, maxitems)

    def initialize_poi_category(self, category, xcol, ycol):
        if category not in CAT_NAME_TO_IND:
            CAT_NAME_TO_IND[category] = len(CAT_NAME_TO_IND)

        df = pd.concat([xcol, ycol], axis=1)
        print df.describe()

        _pyaccess.initialize_category(CAT_NAME_TO_IND[category],
                                      df.as_matrix().astype('float32'))

    def compute_nearest_pois(my, distance, category):
        assert category in CAT_NAME_TO_IND, "Category not initialized"

        return _pyaccess.find_all_nearest_pois(distance,
                                               CAT_NAME_TO_IND[category])