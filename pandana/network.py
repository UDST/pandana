from __future__ import division, print_function

import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree

from .cyaccess import cyaccess
from .loaders import pandash5 as ph5
import warnings


def reserve_num_graphs(num):
    """
    This function was previously used to reserve memory space for multiple
    graphs. It is no longer needed in Pandana 0.4+, and will be removed in a
    future version.

    Parameters
    ----------
    num : int
        Number of graphs to be reserved in memory

    """
    warnings.warn(
        "Function reserve_num_graphs() is no longer needed in Pandana 0.4+\
         and will be removed in a future version",
        DeprecationWarning,
    )
    return None


class Network:
    """
    Create the transportation network in the city.  Typical data would be
    distance based from OpenStreetMap or travel time from GTFS transit data.

    Parameters
    ----------
    node_x : pandas.Series, float
        Defines the x attribute for nodes in the network (e.g. longitude)
    node_y : pandas.Series, float
        Defines the y attribute for nodes in the network (e.g. latitude)
        This param and the one above should have the *same* index which
        should be the node_ids that are referred to in the edges below.
    edge_from : pandas.Series, int
        Defines the node ID that begins an edge - should refer to the index
        of the two series objects above
    edge_to : pandas.Series, int
        Defines the node ID that ends an edge - should refer to the index
        of the two series objects above
    edge_weights : pandas.DataFrame, all numerics
        Specifies one or more *impedances* on the network which define the
        distances between nodes.  Multiple impedances can be used to
        capture travel times at different times of day, for instance
    twoway : boolean, optional
        Whether the edges in this network are two way edges or one way (
        where the one direction is directed from the from node to the to
        node). If twoway = True, it is assumed that the from and to ID in the
        edge table occurs once and that travel can occur in both directions
        on the single edge record. Pandana will internally flip and append
        the from and to IDs to the original edges to create a two direction
        network. If twoway = False, it is assumed that travel can only occur
        in the explicit direction indicated by the from and to ID in the edge
        table.

    """

    def __init__(self, node_x, node_y, edge_from, edge_to, edge_weights, twoway=True):
        nodes_df = pd.DataFrame({"x": node_x, "y": node_y})
        edges_df = pd.DataFrame({"from": edge_from, "to": edge_to}).join(edge_weights)

        self.nodes_df = nodes_df
        self.edges_df = edges_df

        self.impedance_names = list(edge_weights.columns)
        self.variable_names = set()
        self.poi_category_names = []
        self.poi_category_indexes = {}

        # this maps IDs to indexes which are used internally
        # this is a constant source of headaches, but all node identifiers
        # in the c extension are actually indexes ordered from 0 to numnodes-1
        # node IDs are thus translated back and forth in the python layer,
        # which allows non-integer node IDs as well
        self.node_idx = pd.Series(
            np.arange(len(nodes_df), dtype="int"), index=nodes_df.index
        )

        edges = pd.concat(
            [self._node_indexes(edges_df["from"]), self._node_indexes(edges_df["to"])],
            axis=1,
        )

        self.net = cyaccess(
            self.node_idx.values,
            nodes_df.astype("double").values,
            edges.values,
            edges_df[edge_weights.columns].transpose().astype("double").values,
            twoway,
        )

        self._twoway = twoway

        self.kdtree = KDTree(nodes_df.values)

    @classmethod
    def from_hdf5(cls, filename):
        """
        Load a previously saved Network from a Pandas HDF5 file.

        Parameters
        ----------
        filename : str

        Returns
        -------
        network : pandana.Network

        """
        return ph5.network_from_pandas_hdf5(cls, filename)

    def save_hdf5(self, filename, rm_nodes=None):
        """
        Save network data to a Pandas HDF5 file.

        Only the nodes and edges of the actual network are saved,
        points-of-interest and data attached to nodes are not saved.

        Parameters
        ----------
        filename : str
        rm_nodes : array_like
            A list, array, Index, or Series of node IDs that should *not*
            be saved as part of the Network.

        """
        ph5.network_to_pandas_hdf5(self, filename, rm_nodes)

    def _node_indexes(self, node_ids):
        # for some reason, merge is must faster than .loc
        df = pd.merge(
            pd.DataFrame({"node_ids": node_ids}),
            pd.DataFrame({"node_idx": self.node_idx}),
            left_on="node_ids",
            right_index=True,
            how="left",
        )
        return df.node_idx

    @property
    def aggregations(self):
        return self.net.get_available_aggregations()

    @property
    def decays(self):
        return self.net.get_available_decays()

    @property
    def node_ids(self):
        """
        The node IDs which will be used as the index of many return series
        """
        return self.node_idx.index

    @property
    def bbox(self):
        """
        The bounding box for nodes in this network [xmin, ymin, xmax, ymax]
        """
        return [
            self.nodes_df.x.min(),
            self.nodes_df.y.min(),
            self.nodes_df.x.max(),
            self.nodes_df.y.max(),
        ]

    def shortest_path(self, node_a, node_b, imp_name=None):
        """
        Return the shortest path between two node IDs in the network. Must
        provide an impedance name if more than one is available.

        Parameters
        ----------
        node_a : int
            Source node ID
        node_b : int
            Destination node ID
        imp_name : string, optional
            The impedance name to use for the shortest path

        Returns
        -------
        path : np.ndarray
            Nodes that are traversed in the shortest path

        """
        # map to internal node indexes
        node_idx = self._node_indexes(pd.Series([node_a, node_b]))
        node_a = node_idx.iloc[0]
        node_b = node_idx.iloc[1]

        imp_num = self._imp_name_to_num(imp_name)

        path = self.net.shortest_path(node_a, node_b, imp_num)

        # map back to external node IDs
        return self.node_ids.values[path]

    def shortest_paths(self, nodes_a, nodes_b, imp_name=None):
        """
        Vectorized calculation of shortest paths. Accepts a list of origins
        and list of destinations and returns a corresponding list of
        shortest path routes. Must provide an impedance name if more than
        one is available.

        Added in Pandana v0.6.

        Parameters
        ----------
        nodes_a : list-like of ints
            Source node IDs
        nodes_b : list-like of ints
            Corresponding destination node IDs
        imp_name : string
            The impedance name to use for the shortest path

        Returns
        -------
        paths : list of np.ndarray
            Nodes traversed in each shortest path

        """
        if len(nodes_a) != len(nodes_b):
            raise ValueError(
                "Origin and destination counts don't match: {}, {}".format(
                    len(nodes_a), len(nodes_b)
                )
            )

        # map to internal node indexes
        nodes_a_idx = self._node_indexes(pd.Series(nodes_a)).values
        nodes_b_idx = self._node_indexes(pd.Series(nodes_b)).values

        imp_num = self._imp_name_to_num(imp_name)

        paths = self.net.shortest_paths(nodes_a_idx, nodes_b_idx, imp_num)

        # map back to external node ids
        return [self.node_ids.values[p] for p in paths]

    def shortest_path_length(self, node_a, node_b, imp_name=None):
        """
        Return the length of the shortest path between two node IDs in the
        network. Must provide an impedance name if more than one is
        available.

        If you have a large number of paths to calculate, don't use this
        function! Use the vectorized one instead.

        Added in Pandana v0.5.

        Parameters
        ----------
        node_a : int
            Source node ID
        node_b : int
            Destination node ID
        imp_name : string
            The impedance name to use for the shortest path

        Returns
        -------
        length : float

        """
        # map to internal node indexes
        node_idx = self._node_indexes(pd.Series([node_a, node_b]))
        node_a = node_idx.iloc[0]
        node_b = node_idx.iloc[1]

        imp_num = self._imp_name_to_num(imp_name)

        len = self.net.shortest_path_distance(node_a, node_b, imp_num)

        if len == 4294967.295:
            warnings.warn(
                "Unsigned integer: shortest path distance is trying to be calculated between\
                external %s and %s unconntected nodes" % (node_a, node_b)
            )

        return len

    def shortest_path_lengths(self, nodes_a, nodes_b, imp_name=None):
        """
        Vectorized calculation of shortest path lengths. Accepts a list of
        origins and list of destinations and returns a corresponding list
        of shortest path lengths. Must provide an impedance name if more
        than one is available.

        Added in Pandana v0.5.

        Parameters
        ----------
        nodes_a : list-like of ints
            Source node IDs
        nodes_b : list-like of ints
            Corresponding destination node IDs
        imp_name : string
            The impedance name to use for the shortest path

        Returns
        -------
        lengths : list of floats

        """
        if len(nodes_a) != len(nodes_b):
            raise ValueError(
                "Origin and destination counts don't match: {}, {}".format(
                    len(nodes_a), len(nodes_b)
                )
            )

        # map to internal node indexes
        nodes_a_idx = self._node_indexes(pd.Series(nodes_a)).values
        nodes_b_idx = self._node_indexes(pd.Series(nodes_b)).values

        imp_num = self._imp_name_to_num(imp_name)

        lens = self.net.shortest_path_distances(nodes_a_idx, nodes_b_idx, imp_num)

        if 4294967.295 in lens:
            unconnected_idx = [i for i, v in enumerate(lens) if v == 4294967.295]
            unconnected_nodes = [(nodes_a[i], nodes_b[i]) for i in unconnected_idx]
            warnings.warn(
                "Unsigned integer: shortest path distance is trying to be calculated \
                between the following external unconnected nodes: %s" % (unconnected_nodes))

        return lens

    def set(self, node_ids, variable=None, name="tmp"):
        """
        Characterize urban space with a variable that is related to nodes in
        the network.

        Parameters
        ----------
        node_ids : pandas.Series, int
            A series of node_ids which are usually computed using
            get_node_ids on this object.
        variable : pandas.Series, numeric, optional
            A series which represents some variable defined in urban space.
            It could be the location of buildings, or the income of all
            households - just about anything can be aggregated using the
            network queries provided here and this provides the api to set
            the variable at its disaggregate locations.  Note that node_id
            and variable should have the same index (although the index is
            not actually used).  If variable is not set, then it is assumed
            that the variable is all "ones" at the location specified by
            node_ids.  This could be, for instance, the location of all
            coffee shops which don't really have a variable to aggregate. The
            variable is connected to the closest node in the Pandana network
            which assumes no impedance between the location of the variable
            and the location of the closest network node.
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
        df = pd.DataFrame({name: variable, "node_idx": self._node_indexes(node_ids)})

        length = len(df)
        df = df.dropna(how="any")
        newl = len(df)
        if length - newl > 0:
            print(
                "Removed %d rows because they contain missing values" % (length - newl)
            )

        self.variable_names.add(name)

        self.net.initialize_access_var(
            name.encode("utf-8"),
            df.node_idx.values.astype("int"),
            df[name].values.astype("double"),
        )

    def precompute(self, distance):
        """
        Precomputes the range queries (the reachable nodes within this
        maximum distance.  So as long as you use a smaller distance, cached
        results will be used.)

        Parameters
        ----------
        distance : float
            The maximum distance to use. This will usually be a distance unit
            in meters however if you have customized the impedance this could
            be in other units such as utility or time etc.

        Returns
        -------
        Nothing
        """
        self.net.precompute_range(distance)

    def nodes_in_range(self, nodes, radius, imp_name=None):
        """
        Computes the range queries (the reachable nodes within this maximum
        distance) for each input node.

        Parameters
        ----------
        nodes : list-like of ints
            Source node IDs
        radius : float
            Maximum distance to use. This will usually be a distance unit in
            meters however if you have customized the impedance (using the
            imp_name option) this could be in other units such as utility or
            time etc.
        imp_name : string, optional
            The impedance name to use for the aggregation on this network.
            Must be one of the impedance names passed in the constructor of
            this object.  If not specified, there must be only one impedance
            passed in the constructor, which will be used.

        Returns
        -------
        d : pandas.DataFrame
            Like nearest_pois, this is a dataframe containing the input node
            index, the index of the nearby nodes within the search radius,
            and the distance (according to the requested impedance) from the
            source to the nearby node.
        """
        imp_num = self._imp_name_to_num(imp_name)
        imp_name = self.impedance_names[imp_num]
        ext_ids = self.node_idx.index.values

        raw_result = self.net.nodes_in_range(nodes, radius, imp_num, ext_ids)
        clean_result = pd.concat(
            [
                pd.DataFrame(r, columns=["destination", imp_name]).assign(source=ix)
                for r, ix in zip(raw_result, nodes)
            ]
        )[["source", "destination", imp_name]]
        return (
            clean_result.drop_duplicates(subset=["source", "destination"])
            .reset_index(drop=True)
            .query("{} <= {}".format(imp_name, radius))
        )

    def _imp_name_to_num(self, imp_name):
        if imp_name is None:
            assert (
                len(self.impedance_names) == 1
            ), "must pass impedance name if there are multiple impedances set"
            imp_name = self.impedance_names[0]

        assert imp_name in self.impedance_names, (
            "An impedance with that name" "was not found"
        )

        return self.impedance_names.index(imp_name)

    def aggregate(
        self, distance, type="sum", decay="linear", imp_name=None, name="tmp"
    ):
        """
        Aggregate information for every source node in the network - this is
        really the main purpose of this library.  This allows you to touch
        the data specified by calling set and perform some aggregation on it
        within the specified distance.  For instance, summing the population
        within 1000 meters.

        Parameters
        ----------
        distance : float
            The maximum distance to aggregate data within. 'distance' can
            represent any impedance unit that you have set as your edge
            weight. This will usually be a distance unit in meters however
            if you have customized the impedance this could be in other
            units such as utility or time etc.
        type : string, optional (default 'sum')
            The type of aggregation: 'mean' (with 'ave', 'avg', 'average'
            as aliases), 'std' (or 'stddev'), 'sum', 'count', 'min', 'max',
            'med' (or 'median'), '25pct', or '75pct'. (Quantiles are
            computed by sorting so may be slower than the others.)
        decay : string, optional (default 'linear')
            The type of decay to apply, which makes things that are further
            away count less in the aggregation: 'linear', 'exponential', or
            'flat' (no decay).

            *Additional notes:* see ``aggregateAccessibilityVariable`` in
            accessibility.cpp to read through the code that applies decays.
            The exponential decay function is exp(-1*distance/radius)*var.
            The decay setting only operates on 'sum' and 'mean' aggregations.
            If you apply decay to a 'mean', the result will NOT be a weighted
            average; it will be the mean of the post-decay values. (So for a
            'mean' aggregation, you need to explicitly set decay to 'flat'
            unless you want that.)

        imp_name : string, optional
            The impedance name to use for the aggregation on this network.
            Must be one of the impedance names passed in the constructor of
            this object.  If not specified, there must be only one impedance
            passed in the constructor, which will be used.
        name : string, optional
            The variable to aggregate.  This variable will have been created
            and named by a call to ``set``.  If not specified, the default
            variable name will be used so that the most recent call to set
            without giving a name will be the variable used.

        Returns
        -------
        agg : pandas.Series
            Returns a Pandas Series for every origin node in the network,
            with the index which is the same as the node_ids passed to the
            init method and the values are the aggregations for each source
            node in the network.
        """

        imp_num = self._imp_name_to_num(imp_name)
        type = type.lower()

        # Resolve aliases
        if type in ["ave", "avg", "average"]:
            type = "mean"

        if type in ["stddev"]:
            type = "std"

        if type in ["med"]:
            type = "median"

        assert name in self.variable_names, (
            "A variable with that name " "has not yet been initialized"
        )

        res = self.net.get_all_aggregate_accessibility_variables(
            distance,
            name.encode("utf-8"),
            type.encode("utf-8"),
            decay.encode("utf-8"),
            imp_num,
        )

        return pd.Series(res, index=self.node_ids)

    def get_node_ids(self, x_col, y_col, mapping_distance=None):
        """
        Assign node_ids to data specified by x_col and y_col.

        Parameters
        ----------
        x_col : pandas.Series (float)
            A Pandas Series where values specify the x (e.g. longitude)
            location of dataset.
        y_col : pandas.Series (float)
            A Pandas Series where values specify the y (e.g. latitude)
            location of dataset.  x_col and y_col should use the same index.
        mapping_distance : float, optional
            The maximum distance that will be considered a match between the
            x, y data and the nearest node in the network.  This will usually
            be a distance unit in meters however if you have customized the
            impedance this could be in other units such as utility or time
            etc. If not specified, every x, y coordinate will be mapped to
            the nearest node.

        Returns
        -------
        node_ids : pandas.Series (int)
            Returns a Pandas Series of node_ids for each x, y in the
            input data. The index is the same as the indexes of the
            x, y input data, and the values are the mapped node_ids.
            If mapping distance is not passed and if there are no nans in the
            x, y data, this will be the same length as the x, y data.
            If the mapping is imperfect, this function returns all the
            input x, y's that were successfully mapped to node_ids.
        """
        xys = pd.DataFrame({"x": x_col, "y": y_col})

        distances, indexes = self.kdtree.query(xys.values)
        indexes = np.transpose(indexes)[0]
        distances = np.transpose(distances)[0]

        node_ids = self.nodes_df.iloc[indexes].index

        df = pd.DataFrame({"node_id": node_ids, "distance": distances}, index=xys.index)

        if mapping_distance is not None:
            df = df[df.distance <= mapping_distance]

        return df.node_id

    def plot(
        self,
        data,
        bbox=None,
        plot_type="scatter",
        fig_kwargs=None,
        plot_kwargs=None,
        cbar_kwargs=None,
    ):
        """
        Plot an array of data on a map using Matplotlib, automatically matching
        the data to the Pandana network node positions. Keyword arguments are
        passed to the plotting routine.

        Modified in Pandana v0.6 to eliminate usage of Matplotlib's deprecated
        Basemap toolkit. No longer accepts bmap_kwargs and no longer returns
        a Basemap object.

        Parameters
        ----------
        data : pandas.Series
            Numeric data with the same length and index as the nodes
            in the network.
        bbox : tuple, optional
            (lat_min, lng_min, lat_max, lng_max)
        plot_type : {'hexbin', 'scatter'}, optional
        fig_kwargs : dict, optional
            Keyword arguments that will be passed to matplotlib.pyplot.subplots.
            Use this to specify things like figure size or background color.
        plot_kwargs : dict, optional
            Keyword arguments that will be passed to the matplotlib plotting
            command. Use this to control plot styles and color maps.
        cbar_kwargs : dict, optional
            Keyword arguments that will be passed to matplotlib.pyplot.colorbar.
            Use this to control color bar location and label.

        Returns
        -------
        fig : matplotlib.Figure
        ax : matplotlib.Axes

        """
        try:
            ModuleNotFoundError  # Python 3.6+
        except NameError:
            ModuleNotFoundError = ImportError

        try:
            import matplotlib
            import matplotlib.pyplot as plt
        except (ModuleNotFoundError, RuntimeError):
            raise ModuleNotFoundError("Pandana's network.plot() requires Matplotlib")

        fig_kwargs = fig_kwargs or {"figsize": (10, 8)}
        plot_kwargs = plot_kwargs or {"cmap": "hot_r", "s": 1}
        cbar_kwargs = cbar_kwargs or {}

        if not bbox:
            bbox = (
                self.nodes_df.y.min(),
                self.nodes_df.x.min(),
                self.nodes_df.y.max(),
                self.nodes_df.x.max(),
            )

        fig, ax = plt.subplots(**fig_kwargs)

        x, y = (self.nodes_df.x.values, self.nodes_df.y.values)

        if plot_type == "scatter":
            plot = plt.scatter(x, y, c=data.values, **plot_kwargs)
        elif plot_type == "hexbin":
            plot = plt.hexbin(x, y, C=data.values, **plot_kwargs)

        colorbar = plt.colorbar(plot, **cbar_kwargs)

        plt.show()

        return fig, ax

    def init_pois(self, num_categories, max_dist, max_pois):
        """
        Initialize the point of interest (POI) infrastructure.
        This is no longer needed in Pandana 0.4+ and will be removed in a
        future version.

        Parameters
        ----------
        num_categories : int
            Number of categories of POIs
        max_dist : float
            Maximum distance that will be tested to nearest POIs. This will
            usually be a distance unit in meters however if you have
            customized the impedance this could be in other
            units such as utility or time etc.
        max_pois : int
            Maximum number of POIs to return in the nearest query

        """
        self.num_categories = num_categories
        self.max_dist = max_dist
        self.max_pois = max_pois
        warnings.warn(
            "Method init_pois() is no longer needed in Pandana 0.4+ and will be removed in a \
            future version; maxdist and maxitems should now be passed to set_pois()",
            DeprecationWarning,
        )
        return None

    def set_pois(self, category=None, maxdist=None, maxitems=None, x_col=None, y_col=None,
                 mapping_distance=None):
        """
        Set the location of all the points of interest (POIs) of this category.
         The POIs are connected to the closest node in the Pandana network
         which assumes no impedance between the location of the variable and
         the location of the closest network node.

        Parameters
        ----------
        category : string
            The name of the category for this set of POIs
        maxdist : float
            The maximum distance that will later be used in
            find_all_nearest_pois()
        maxitems : int
            The maximum number of items that will later be requested
            in find_all_nearest_pois()
        x_col : pandas.Series (float)
            The x location (longitude) of POIs in this category
        y_col : pandas.Series (float)
            The y location (latitude) of POIs in this category
        mapping_distance : float, optional
            The maximum distance that will be considered a match between the
            POIs and the nearest node in the network.  This will usually
            be a distance unit in meters however if you have customized the
            impedance this could be in other units such as utility or time
            etc. If not specified, every POI will be mapped to
            the nearest node.

        Returns
        -------
        Nothing

        """
        # condition to check if missing arguments for keyword arguments using set_pois() from v0.3
        if maxitems is None:
            print("Reading parameters from init_pois()")
            maxitems = self.max_pois

        # condition to check for positional arguments in set_pois() from v0.3
        elif isinstance(maxitems, type(pd.Series())):
            y_col = maxitems
            maxitems = self.max_pois

        if maxdist is None:
            print("Reading parameters from init_pois()")
            maxdist = self.max_dist

        elif isinstance(maxdist, type(pd.Series())):
            x_col = maxdist
            maxdist = self.max_dist

        if category not in self.poi_category_names:
            self.poi_category_names.append(category)

        self.max_pois = maxitems

        node_ids = self.get_node_ids(x_col, y_col, mapping_distance=mapping_distance)

        self.poi_category_indexes[category] = node_ids.index

        node_idx = self._node_indexes(node_ids)

        self.net.initialize_category(
            maxdist, maxitems, category.encode("utf-8"), node_idx.values
        )

    def nearest_pois(
        self,
        distance,
        category,
        num_pois=1,
        max_distance=None,
        imp_name=None,
        include_poi_ids=False,
    ):
        """
        Find the distance to the nearest points of interest (POI)s from each
        source node.  The bigger values in this case mean less accessibility.

        Parameters
        ----------
        distance : float
            The maximum distance to look for POIs. This will usually be a
            distance unit in meters however if you have customized the
            impedance this could be in other units such as utility or time
            etc.
        category : string
            The name of the category of POI to look for
        num_pois : int
            The number of POIs to look for, this also sets the number of
            columns in the DataFrame that gets returned
        max_distance : float, optional
            The value to set the distance to if there is no POI within the
            specified distance - if not specified, gets set to distance. This
            will usually be a distance unit in meters however if you have
            customized the impedance this could be in other units such as
            utility or time etc.
        imp_name : string, optional
            The impedance name to use for the aggregation on this network.
            Must be one of the impedance names passed in the constructor of
            this object.  If not specified, there must be only one impedance
            passed in the constructor, which will be used.
        include_poi_ids : bool, optional
            If this flag is set to true, the call will add columns to the
            return DataFrame - instead of just returning the distance for
            the nth POI, it will also return the id of that POI.  The names
            of the columns with the POI IDs will be poi1, poi2, etc - it
            will take roughly twice as long to include these IDs as to not
            include them

        Returns
        -------
        d : pandas.DataFrame
            Like aggregate, this series has an index of all the node ids for
            the network.  Unlike aggregate, this method returns a dataframe
            with the number of columns equal to the distances to the Nth
            closest POI.  For instance, if you ask for the 10 closest poi to
            each node, column d[1] wil be the distance to the 1st closest POI
            of that category while column d[2] will be the distance to the 2nd
            closest POI, and so on.
        """
        if max_distance is None:
            max_distance = distance

        if category not in self.poi_category_names:
            assert 0, "Need to call set_pois for this category"

        if num_pois > self.max_pois:
            assert 0, "Asking for more POIs than set in init_pois"

        imp_num = self._imp_name_to_num(imp_name)

        dists, poi_ids = self.net.find_all_nearest_pois(
            distance, num_pois, category.encode("utf-8"), imp_num
        )
        dists[dists == -1] = max_distance

        df = pd.DataFrame(dists, index=self.node_ids)
        df.columns = list(range(1, num_pois + 1))

        if include_poi_ids:
            df2 = pd.DataFrame(poi_ids, index=self.node_ids)
            df2.columns = ["poi%d" % i for i in range(1, num_pois + 1)]
            for col in df2.columns:
                # if this is still all working according to plan at this point
                # the great magic trick is now to turn the integer position of
                # the poi, which is painstakingly returned from the c++ code,
                # and turn it into the actual index that was used when it was
                # initialized as a pandas.Series - this really is pandas-like
                # thinking.  it's complicated on the inside, but quite
                # intuitive to the user I think
                s = df2[col].astype("int")
                df2[col] = self.poi_category_indexes[category].values[s]
                df2.loc[s == -1, col] = np.nan

            df = pd.concat([df, df2], axis=1)

        return df

    def low_connectivity_nodes(self, impedance, count, imp_name=None):
        """
        Identify nodes that are connected to fewer than some threshold
        of other nodes within a given distance.

        Parameters
        ----------
        impedance : float
            Distance within which to search for other connected nodes. This
            will usually be a distance unit in meters however if you have
            customized the impedance this could be in other units such as
            utility or time etc.
        count : int
            Threshold for connectivity. If a node is connected to fewer
            than this many nodes within `impedance` it will be identified
            as "low connectivity".
        imp_name : string, optional
            The impedance name to use for the aggregation on this network.
            Must be one of the impedance names passed in the constructor of
            this object.  If not specified, there must be only one impedance
            passed in the constructor, which will be used.

        Returns
        -------
        node_ids : array
            List of "low connectivity" node IDs.

        """
        # set a counter variable on all nodes
        self.set(self.node_ids.to_series(), name="counter")

        # count nodes within impedance range
        agg = self.aggregate(impedance, type="count", imp_name=imp_name, name="counter")

        return np.array(agg[agg < count].index)
