cimport cython
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.pair cimport pair

import numpy as np
cimport numpy as np

# resources
# http://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html
# http://www.birving.com/blog/2014/05/13/passing-numpy-arrays-between-python-and/


cdef extern from "accessibility.h" namespace "MTC::accessibility":
    cdef cppclass Accessibility:
        Accessibility(int, vector[vector[long]], vector[vector[double]], bool) except +
        vector[string] aggregations
        vector[string] decays
        void initializeCategory(double, int, string, vector[long])
        pair[vector[vector[double]], vector[vector[int]]] findAllNearestPOIs(
            float, int, string, int)
        void initializeAccVar(string, vector[long], vector[double])
        vector[double] getAllAggregateAccessibilityVariables(
            float, string, string, string, int)
        vector[int] Route(int, int, int)
        vector[vector[int]] Routes(vector[long], vector[long], int)
        double Distance(int, int, int)
        vector[double] Distances(vector[long], vector[long], int)
        void precomputeRangeQueries(double)


cdef np.ndarray[double] convert_vector_to_array_dbl(vector[double] vec):
    cdef np.ndarray arr = np.zeros(len(vec), dtype="double")
    for i in range(len(vec)):
        arr[i] = vec[i]
    return arr


cdef np.ndarray[double, ndim = 2] convert_2D_vector_to_array_dbl(
        vector[vector[double]] vec):
    cdef np.ndarray arr = np.empty_like(vec, dtype="double")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            arr[i][j] = vec[i][j]
    return arr


cdef np.ndarray[int, ndim = 2] convert_2D_vector_to_array_int(
        vector[vector[int]] vec):
    cdef np.ndarray arr = np.empty_like(vec, dtype="int")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            arr[i][j] = vec[i][j]
    return arr


cdef class cyaccess:
    cdef Accessibility * access

    def __cinit__(
        self,
        np.ndarray[long] node_ids,
        np.ndarray[double, ndim=2] node_xys,
        np.ndarray[long, ndim=2] edges,
        np.ndarray[double, ndim=2] edge_weights,
        bool twoway=True
    ):
        """
        node_ids: vector of node identifiers
        node_xys: the spatial locations of the same nodes
        edges: a pair of node ids which comprise each edge
        edge_weights: the weights (impedances) that apply to each edge
        twoway: whether the edges should all be two-way or whether they
            are directed from the first to the second node
        """
        # you're right, neither the node ids nor the location xys are used in here
        # anymore - I'm hesitant to out-and-out remove it as we might still use
        # it for something someday
        self.access = new Accessibility(len(node_ids), edges, edge_weights, twoway)

    def __dealloc__(self):
        del self.access

    def initialize_category(
        self,
        double maxdist,
        int maxitems,
        string category,
        np.ndarray[long] node_ids
    ):
        """
        maxdist - the maximum distance that will later be used in
            find_all_nearest_pois
        maxitems - the maximum number of items that will later be requested
            in find_all_nearest_pois
        category - the category name
        node_ids - an array of nodeids which are locations where this poi occurs
        """
        self.access.initializeCategory(maxdist, maxitems, category, node_ids)

    def find_all_nearest_pois(
        self,
        double radius,
        int num_of_pois,
        string category,
        int impno=0
    ):
        """
        radius - search radius
        num_of_pois - number of pois to search for
        category - the category name
        impno - the impedance id to use
        return_nodeids - whether to return the nodeid locations of the nearest
            not just the distances
        """
        ret = self.access.findAllNearestPOIs(radius, num_of_pois, category, impno)

        return convert_2D_vector_to_array_dbl(ret.first),\
            convert_2D_vector_to_array_int(ret.second)

    def initialize_access_var(
        self,
        string category,
        np.ndarray[long] node_ids,
        np.ndarray[double] values
    ):
        """
        category - category name
        node_ids: vector of node identifiers
        values: vector of values that are location at the nodes
        """
        self.access.initializeAccVar(category, node_ids, values)

    def get_available_aggregations(self):
        return self.access.aggregations

    def get_available_decays(self):
        return self.access.decays

    def get_all_aggregate_accessibility_variables(
        self,
        double radius,
        category,
        aggtyp,
        decay,
        int impno=0,
    ):
        """
        radius - search radius
        category - category name
        aggtyp - aggregation type, see docs
        decay - decay type, see docs
        impno - the impedance id to use
        """
        ret = self.access.getAllAggregateAccessibilityVariables(
            radius, category, aggtyp, decay, impno)

        return convert_vector_to_array_dbl(ret)

    def shortest_path(self, int srcnode, int destnode, int impno=0):
        """
        srcnode - node id origin
        destnode - node id destination
        impno - the impedance id to use
        """
        return self.access.Route(srcnode, destnode, impno)

    def shortest_paths(self, np.ndarray[long] srcnodes, 
            np.ndarray[long] destnodes, int impno=0):
        """
        srcnodes - node ids of origins
        destnodes - node ids of destinations
        impno - impedance id
        """
        return self.access.Routes(srcnodes, destnodes, impno)

    def shortest_path_distance(self, int srcnode, int destnode, int impno=0):
        """
        srcnode - node id origin
        destnode - node id destination
        impno - the impedance id to use
        """
        return self.access.Distance(srcnode, destnode, impno)

    def shortest_path_distances(self, np.ndarray[long] srcnodes, 
            np.ndarray[long] destnodes, int impno=0):
        """
        srcnodes - node ids of origins
        destnodes - node ids of destinations
        impno - impedance id
        """
        return self.access.Distances(srcnodes, destnodes, impno)

    def precompute_range(self, double radius):
        self.access.precomputeRangeQueries(radius)
