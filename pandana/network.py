import time
import matplotlib
# this might fix the travis build
matplotlib.use('Agg')
import brewer2mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import _pyaccess

MAX_NUM_NETWORKS = 0
NUM_NETWORKS = 0

AGGREGATIONS = {
    "SUM": 0,
    "AVE": 1,
    "AVERAGE": 1,
    "STD": 5,
    "STDDEV": 5,
    "COUNT": 6
}

DECAYS = {
    "EXP": 0,
    "EXPONENTIAL": 0,
    "LINEAR": 1,
    "FLAT": 2
}


def reserve_num_graphs(num):
    """
    Make a call to this function if you want to run queries on more than
    one Network object

    Parameters
    ----------
    num : int
        The number of networks you want to use

    Returns
    -------
    Nothing
    """
    global NUM_NETWORKS, MAX_NUM_NETWORKS
    assert MAX_NUM_NETWORKS == 0, ("Global memory used so cannot initialize "
                                   "twice")
    assert num > 0
    MAX_NUM_NETWORKS = num
    _pyaccess.create_graphs(num)


class Network:
    """
    Create the transportation network in the city.  Typical data would be
    distance based from OpenStreetMap or possibly using transit data from
    GTFS.

    Parameters
    ----------
    node_x : Pandas Series, flaot
        Defines the x attribute for nodes in the network (e.g. longitude)
    node_y : Pandas Series, float
        Defines the y attribute for nodes in the network (e.g. latitude)
        This param and the one above should have the *same* index which
        should be the node_ids that are referred to in the edges below.
    edge_from : Pandas Series, int
        Defines the node id that begins an edge - should refer to the index
        of the two series objects above
    edge_to : Pandas Series, int
        Defines the node id that ends an edge - should refer to the index
        of the two series objects above
    edge_weights : Pandas DataFrame, all floats
        Specifies one or more *impedances* on the network which define the
        distances between nodes.  Multiple impedances can be used to
        capture travel times at different times of day, for instance
    two_way : boolean, optional
        Whether the edges in this network are two way edges or one way (
        where the one direction is directed from the from node to the to
        node)

    """

    def __init__(self, node_x, node_y, edge_from, edge_to, edge_weights,
                 twoway=True):

        global NUM_NETWORKS, MAX_NUM_NETWORKS

        if MAX_NUM_NETWORKS == 0:
            reserve_num_graphs(1)

        # print NUM_NETWORKS, MAX_NUM_NETWORKS

        assert NUM_NETWORKS < MAX_NUM_NETWORKS, "Adding more networks than " \
                                                "have been reserved"
        self.graph_no = NUM_NETWORKS
        NUM_NETWORKS += 1

        nodes_df = pd.DataFrame({'x': node_x, 'y': node_y})
        edges_df = pd.DataFrame({'from': edge_from, 'to': edge_to}).\
            join(edge_weights)
        self.nodes_df = nodes_df
        self.edges_df = edges_df

        self.impedance_names = list(edge_weights.columns)
        self.variable_names = []
        self.poi_category_names = []
        self.num_poi_categories = -1

        # this maps ids to indexes which are used internally
        self.node_idx = pd.Series(np.arange(len(nodes_df)),
                                  index=nodes_df.index)

        edges = pd.concat([self._node_indexes(edges_df["from"]),
                          self._node_indexes(edges_df["to"])], axis=1)

        _pyaccess.create_graph(self.graph_no,
                               nodes_df.index.values.astype('int32'),
                               nodes_df.as_matrix().astype('float32'),
                               edges.as_matrix().astype('int32'),
                               edges_df[edge_weights.columns].transpose()
                                   .as_matrix().astype('float32'),
                               twoway)

    def _node_indexes(self, node_ids):
        # for some reason, merge is must faster than .loc
        df = pd.merge(pd.DataFrame({"node_ids": node_ids}),
                      pd.DataFrame({"node_idx": self.node_idx}),
                      left_on="node_ids",
                      right_index=True,
                      how="left")
        return df.node_idx

    @property
    def node_ids(self):
        """
        The node ids which will be used as the index of many return series
        """
        return self.node_idx.index

    @property
    def bbox(self):
        """
        The bounding box for nodes in this network [xmin, ymin, xmax, ymax]
        """
        return [self.nodes_df.x.min(), self.nodes_df.y.min(),
                self.nodes_df.x.max(), self.nodes_df.y.max()]

    def set(self, node_ids, variable=None, name="tmp"):
        """
        Characterize urban space with a variable that is related to nodes in
        the network.

        Parameters
        ----------
        node_id : Pandas Series, int
            A series of node_ids which are usually computed using
            get_node_ids on this object.
        variable : Pandas Series, float, optional
            A series which represents some variable defined in urban space.
            It could be the location of buildings, or the income of all
            households - just about anything can be aggregated using the
            network queries provided here and this provides the api to set
            the variable at its disaggregate locations.  Note that node_id
            and variable should have the same index (although the index is
            not actually used).  If variable is not set, then it is assumed
            that the variable is all "ones" at the location specified by
            node_ids.  This could be, for instance, the location of all
            coffee shops which don't really have a variable to aggregate.
        name : string, optional
            Name the variable.  This is optional in the sense that if you don't
            specify it, the default name will be used.  Since the same
            default name is used by aggregate on this object, you can
            alternate between characterize and aggregate calls without
            setting names.

        Returns
        -------
        Nothing
        """

        if variable is None:
            variable = pd.Series(np.ones(len(node_ids)), index=node_ids.index)

        df = pd.DataFrame({name: variable,
                           "node_idx": self._node_indexes(node_ids)})

        t1 = time.time()
        l = len(df)
        df = df.dropna(how="any")
        newl = len(df)
        if l-newl > 0:
            print "Removed %d rows because they contain missing values" % \
                (l-newl)
        # print "check nans in %.3f" % (time.time()-t1)

        if name not in self.variable_names:
            self.variable_names.append(name)
            _pyaccess.initialize_acc_vars(self.graph_no,
                                          len(self.variable_names))

        t1 = time.time()
        _pyaccess.initialize_acc_var(self.graph_no,
                                     self.variable_names.index(name),
                                     df.node_idx.astype('int32'),
                                     df[name].astype('float32'))
        # print "init column in %.3f" % (time.time()-t1)

    def precompute(self, distance):
        """
        Precomputes the range queries (the reachable nodes within this
        maximum distance.  So as long as you use a smaller distance, cached
        results will be used.)

        Parameters
        ----------
        distance : float
            The maximum distance to use

        Returns
        -------
        Nothing
        """
        _pyaccess.precompute_range(distance, self.graph_no)

    def _imp_name_to_num(self, imp_name):
        if imp_name is None:
            assert len(self.impedance_names) == 1,\
                "must pass impedance name if there are multiple impedances set"
            imp_name = self.impedance_names[0]

        assert imp_name in self.impedance_names, "An impedance with that name" \
                                                 "was not found"

        return self.impedance_names.index(imp_name)

    def aggregate(self, distance, type="sum", decay="linear", imp_name=None,
                  name="tmp"):
        """
        Aggregate information for every source node in the network - this is
        really the main purpose of this library.  This allows you to touch
        the data specified by calling set and perform some aggregation on it
        within the specified distance.  For instance, summing the population
        within 1000 meters.

        Parameters
        ----------
        distance : float
            The maximum distance to aggregate data within
        type : string
            The type of aggregation, can be one of "ave", "sum", "std",
            and "count"
        decay : string
            The type of decay to apply, which makes things that are further
            away count less in the aggregation - must be one of "linear",
            "exponential" or "flat" (which means no decay).  Linear is the
            fastest computation to perform.  When performing an "ave",
            the decay is typically "flat"
        imp_name : string, optional
            The impedance name to use for the aggregation on this network.
            Must be one of the impedance names passed in the constructor of
            this object.  If not specified, there must be only one impedance
            passed in the constructor, which will be used.
        name : string, optional
            The variable to aggregate.  This variable will have been created
            and named by a call to set.  If not specified, the default
            variable name will be used so that the most recent call to set
            without giving a name will be the variable used.

        Returns
        -------
        agg : Pandas Series
            Returns a Pandas Series for every origin node in the network,
            with the index which is the same as the node_ids passed to the
            init method and the values are the aggregations for each source
            node in the network.
        """
        agg = AGGREGATIONS[type.upper()]
        decay = DECAYS[decay.upper()]

        imp_num = self._imp_name_to_num(imp_name)

        gno = self.graph_no

        assert name in self.variable_names, "A variable with that name " \
                                            "has not yet been initialized"
        varnum = self.variable_names.index(name)

        res = _pyaccess.get_all_aggregate_accessibility_variables(distance,
                                                                  varnum,
                                                                  agg,
                                                                  decay,
                                                                  gno,
                                                                  imp_num)

        return pd.Series(res, index=self.node_ids)

    def get_node_ids(self, x_col, y_col, mapping_distance=-1):
        """
        Assign node_ids to data specified by x_col and y_col

        Parameters
        ----------
        x_col : Pandas series (float)
            A Pandas Series where values specify the x (e.g. longitude)
            location of dataset.
        y_col : Pandas series (float)
            A Pandas Series where values specify the y (e.g. latitude)
            location of dataset.  x_col and y_col should use the same index.
        mapping_distance : float, optional
            The maximum distance that will be considered a match between the
            x, y data and the nearest node in the network.  If not specified,
            every x, y coordinate will be mapped to the nearest node

        Returns
        -------
        node_ids : Pandas series (int)
            Returns a Pandas Series of node_ids for each x, y in the input data.
            The index is the same as the indexes of the x, y input data,
            and the values are the mapped node_ids. If mapping distance is
            not passed and if there are no nans in the x, y data, this will
            be the same length as the x, y data.  If the mapping is
            imperfect, this function returns all the input x, y's that were
            successfully mapped to node_ids.
        """
        xys = pd.DataFrame({'x': x_col, 'y': y_col}).dropna(how='any')

        # no limit to the mapping distance
        node_ids = _pyaccess.xy_to_node(xys.astype('float32'),
                                        mapping_distance,
                                        self.graph_no)

        s = pd.Series(node_ids, index=xys.index)
        # -1 marks did not get mapped ids
        s = s[s != -1]

        if len(s) == 0:
            return pd.Series()

        # this is not pandas finest moment - might have to revisit this at a
        # later date - need to convert from internal to external ids
        node_ids = pd.Series(self.nodes_df.reset_index().
                             iloc[s]["index"].values,
                             index=s.index)
        return node_ids

    def plot(self, s, width=12, height=15, dpi=50,
             scheme="sequential", color='YlGn', numbins=7,
             bbox=None, log_scale=False):
        """
        Experimental method to write the network to a matplotlib image.
        """
        df = pd.DataFrame({'xcol': self.nodes_df.x.values,
                           'ycol': self.nodes_df.y.values,
                           'zcol': s.values})

        if bbox is not None:
            df = df.query("xcol > %f and ycol > %f and xcol < %f and ycol < "
                          "%f" % tuple(bbox))

        fig = plt.figure(num=None, figsize=(width, height), dpi=dpi,
                         facecolor='b', edgecolor='k')
        ax = fig.add_subplot(111, axisbg='black')

        mpl_cmap = brewer2mpl.get_map(color, scheme, numbins).mpl_colormap
        norm = matplotlib.colors.SymLogNorm(.01) if log_scale else None

        ax.scatter(df.xcol, df.ycol, c=df.zcol,
                   cmap=mpl_cmap,
                   norm=norm,
                   edgecolors='grey',
                   linewidths=0.1)

    def init_pois(self, num_categories, max_dist, max_pois):
        """
        Initialize the point of interest infrastructure.

        Parameters
        ----------
        num_categories : int
            Number of categories of POIs
        max_dist : float
            Maximum distance that will be tested to nearest POIs
        max_pois :
            Maximum number of POIs to return in the nearest query

        Returns
        -------
        Nothing
        """
        if self.num_poi_categories != -1:
            print "Can't initialize twice"
            return

        self.num_poi_categories = num_categories
        self.max_pois = max_pois

        _pyaccess.initialize_pois(num_categories, max_dist, max_pois)

    def set_pois(self, category, x_col, y_col):
        """
        Set the location of all the pois of this category

        Parameters
        ----------
        category : string
            The name of the category for this set of pois
        x_col : Pandas Series (float)
            The x location (longitude) of pois in this category
        y_col : Pandas Series (Float)
            The y location (latitude) of pois in this category

        Returns
        -------
        Nothing
        """
        if self.num_poi_categories == -1:
            assert 0, "Need to call init_pois first"

        if category not in self.poi_category_names:
            assert len(self.poi_category_names) < self.num_poi_categories, \
                "Too many categories set - increase the number when calling " \
                "init_pois"
            self.poi_category_names.append(category)

        xys = pd.DataFrame({'x': x_col, 'y': y_col}).dropna(how='any')

        _pyaccess.initialize_category(self.poi_category_names.index(category),
                                      xys.astype('float32'))

    def nearest_pois(self, distance, category, num_pois=1, max_distance=None,
                     imp_name=None):
        """
        Find the distance to the nearest pois from each source node.  The
        bigger values in this case mean less accessibility.

        Parameters
        ----------
        distance : float
            The maximum distance to look for pois
        category : string
            The name of the category of poi to look for
        num_pois : int
            The number of pois to look for, this also sets the number of
            columns in the DataFrame that gets returned
        max_distance : float, optional
            The value to set the distance to if there is NO poi within the
            specified distance - if not specified, gets set to distance
        imp_name : string, optional
            The impedance name to use for the aggregation on this network.
            Must be one of the impedance names passed in the constructor of
            this object.  If not specified, there must be only one impedance
            passed in the constructor, which will be used.

        Returns
        -------
        d : Pandas DataFrame
            Like aggregate, this series has an index of all the node ids for
            the network.  Unlike aggregate, this method returns a dataframe
            with the number of columns equal to the distances to the Nth
            closest poi.  For instance, if you ask for the 10 closest poi to
            each node, column d[1] wil be the distance to the 1st closest poi of
            that category while column d[2] wil lbe the distance to the 2nd
            closest poi, and so on.
        """
        if max_distance is None:
            max_distance = distance

        if self.num_poi_categories == -1:
            assert 0, "Need to call init_pois first"

        if category not in self.poi_category_names:
            assert 0, "Need to call set_pois for this category"

        if num_pois > self.max_pois:
            assert 0, "Asking for more pois that set in init_pois"

        imp_num = self._imp_name_to_num(imp_name)

        a = _pyaccess.find_all_nearest_pois(distance,
                                            num_pois,
                                            self.poi_category_names.index(
                                                category),
                                            self.graph_no,
                                            imp_num)

        a[a == -1] = max_distance
        df = pd.DataFrame(a, index=self.node_ids)
        df.columns = range(1, num_pois+1)
        return df
