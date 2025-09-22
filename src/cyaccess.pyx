#cython: language_level=3

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
        Accessibility(int, vector[vector[long long]], vector[vector[double]], bool) except +
        vector[string] aggregations
        vector[string] decays
        void initializeCategory(double, int, string, vector[long long])
        pair[vector[vector[double]], vector[vector[int]]] findAllNearestPOIs(
            float, int, string, int)
        pair[vector[vector[double]], vector[vector[int]]] findNearestPOIsPartial(
            int, float, int, string, int)
        pair[vector[vector[vector[double]]], vector[vector[vector[int]]]] findBatchNearestPOIs(
            vector[long long], float, int, string, int)
        void initializeAccVar(string, vector[long long], vector[double])
        vector[double] getAllAggregateAccessibilityVariables(
            float, string, string, string, int)
        vector[vector[double]] getBatchAggregateAccessibilityVariables(
            vector[long long], float, string, string, string, int)
        vector[int] Route(int, int, int)
        vector[vector[int]] Routes(vector[long long], vector[long long], int)
        double Distance(int, int, int)
        vector[double] Distances(vector[long long], vector[long long], int)
        vector[vector[pair[long long, float]]] Range(vector[long long], float, int, vector[long long])
        vector[vector[pair[long long, float]]] HybridRange(vector[long long], float, int, vector[long long], int)
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


cdef convert_3D_vector_to_array_dbl(vector[vector[vector[double]]] vec):
    """Convert 3D C++ vector to Python list of 2D numpy arrays"""
    result = []
    cdef np.ndarray[double, ndim = 2] arr
    for i in range(vec.size()):
        arr = np.empty((vec[i].size(), vec[i][0].size() if vec[i].size() > 0 else 0), dtype="double")
        for j in range(vec[i].size()):
            for k in range(vec[i][j].size()):
                arr[j][k] = vec[i][j][k]
        result.append(arr)
    return result


cdef convert_3D_vector_to_array_int(vector[vector[vector[int]]] vec):
    """Convert 3D C++ vector to Python list of 2D numpy arrays"""
    result = []
    cdef np.ndarray[int, ndim = 2] arr
    for i in range(vec.size()):
        arr = np.empty((vec[i].size(), vec[i][0].size() if vec[i].size() > 0 else 0), dtype="int")
        for j in range(vec[i].size()):
            for k in range(vec[i][j].size()):
                arr[j][k] = vec[i][j][k]
        result.append(arr)
    return result


cdef class cyaccess:
    cdef Accessibility * access

    def __cinit__(
        self,
        np.ndarray[long long] node_ids,
        np.ndarray[double, ndim=2] node_xys,
        np.ndarray[long long, ndim=2] edges,
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
        np.ndarray[long long] node_ids
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

    def find_nearest_pois_partial(
        self,
        int source_node,
        double radius,
        int num_of_pois,
        string category,
        int impno=0
    ):
        """
        Enhanced POI search using partial ordering optimization
        
        source_node - the source node to search from
        radius - search radius
        num_of_pois - number of pois to search for (optimized for small k)
        category - the category name
        impno - the impedance id to use
        """
        ret = self.access.findNearestPOIsPartial(source_node, radius, num_of_pois, category, impno)
        
        return convert_2D_vector_to_array_dbl(ret.first),\
            convert_2D_vector_to_array_int(ret.second)

    def find_batch_nearest_pois(
        self,
        vector[long long] source_nodes,
        double radius,
        int num_of_pois,
        string category,
        int impno=0
    ):
        """
        Enhanced batch POI search with frontier compression concepts
        
        source_nodes - list of source nodes to search from
        radius - search radius
        num_of_pois - number of pois to search for each source
        category - the category name
        impno - the impedance id to use
        """
        ret = self.access.findBatchNearestPOIs(source_nodes, radius, num_of_pois, category, impno)
        
        return convert_3D_vector_to_array_dbl(ret.first),\
            convert_3D_vector_to_array_int(ret.second)

    def initialize_access_var(
        self,
        string category,
        np.ndarray[long long] node_ids,
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

    def get_batch_aggregate_accessibility_variables(
        self,
        np.ndarray[long long] source_nodes,
        double radius,
        category,
        aggtyp,
        decay,
        int impno=0,
    ):
        """
        Enhanced batch accessibility computation with frontier compression
        
        source_nodes - array of node ids to compute accessibility from
        radius - search radius
        category - category name
        aggtyp - aggregation type, see docs
        decay - decay type, see docs
        impno - the impedance id to use
        """
        ret = self.access.getBatchAggregateAccessibilityVariables(
            source_nodes, radius, category, aggtyp, decay, impno)

        return convert_2D_vector_to_array_dbl(ret)

    def shortest_path(self, int srcnode, int destnode, int impno=0):
        """
        srcnode - node id origin
        destnode - node id destination
        impno - the impedance id to use
        """
        return self.access.Route(srcnode, destnode, impno)

    def shortest_paths(self, np.ndarray[long long] srcnodes, 
            np.ndarray[long long] destnodes, int impno=0):
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

    def shortest_path_distances(self, np.ndarray[long long] srcnodes, 
            np.ndarray[long long] destnodes, int impno=0):
        """
        srcnodes - node ids of origins
        destnodes - node ids of destinations
        impno - impedance id
        """
        return self.access.Distances(srcnodes, destnodes, impno)
    
    def precompute_range(self, double radius):
        self.access.precomputeRangeQueries(radius)

    def nodes_in_range(self, vector[long long] srcnodes, float radius, int impno, 
            np.ndarray[long long] ext_ids):
        """
        srcnodes - node ids of origins
        radius - maximum range in which to search for nearby nodes
        impno - the impedance id to use
        ext_ids - all node ids in the network
        """
        return self.access.Range(srcnodes, radius, impno, ext_ids)

    def hybrid_nodes_in_range(self, vector[long long] srcnodes, float radius, int impno, 
            np.ndarray[long long] ext_ids, int k_rounds=3):
        """
        Enhanced range query using hybrid approach with bounded relaxation concepts
        
        srcnodes - node ids of origins
        radius - maximum range in which to search for nearby nodes
        impno - the impedance id to use
        ext_ids - all node ids in the network
        k_rounds - number of bounded relaxation rounds (default: 3)
        """
        return self.access.HybridRange(srcnodes, radius, impno, ext_ids, k_rounds)
