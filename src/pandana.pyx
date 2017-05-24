cimport cython
from libcpp cimport bool
from libcpp.vector cimport vector

cimport numpy as np
import numpy as np


# resources
# http://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html
# http://www.birving.com/blog/2014/05/13/passing-numpy-arrays-between-python-and/

cdef extern from "graphalg.h" namespace "MTC::accessibility":
    cdef cppclass Graphalg:
        Graphalg(vector[long], vector[vector[double]], vector[vector[long]],
            vector[double], bool) except +


cdef extern from "accessibility.h" namespace "MTC::accessibility":
    cdef cppclass Accessibility:
        Accessibility(int) except +
        int numnodes
        void addGraphalg(Graphalg*)
        void initializePOIs(int, double, int)
        void initializeCategory(int, vector[long])
        vector[vector[double]] findAllNearestPOIs(float, int, int, int, bool)


cdef class pyAccess:
    cdef Accessibility *access


    def __cinit__(
        self,
        np.ndarray[long] node_ids,
        np.ndarray[double, ndim=2] node_xys,
        np.ndarray[long, ndim=2] edges,
        np.ndarray[double, ndim=2] edge_weights,
        bool twoway = False
    ):
        """
        node_ids: vector of node identifiers
        node_xys: the spatial locations of the same nodes
        edges: a pair of node ids which comprise each edge
        edge_weights: the weights (impedances) that apply to each edge
        twoway: whether the edges should all be two-way or whether they
            are directed from the first to the second node
        """
        self.access = new Accessibility(len(node_ids))

        for i in range(edge_weights.shape[1]):
            self.access.addGraphalg(new Graphalg(
                node_ids, node_xys, edges, edge_weights[i], twoway))


    def __dealloc__(self):
        del self.access


    def initialize_pois(self, numcategories, maxdist, maxitems):
        """
        """
        self.access.initializePOIs(numcategories, maxdist, maxitems)


    def initialize_category(
        self,
        int category,
        node_ids
    ):
        """
        category - the category number
        node_ids - an array of nodeids which are locations where this poi occurs
        """
        self.access.initializeCategory(category, node_ids)


    def find_all_nearest_pois(
        self,
        double radius,
        int num_of_pois,
        int category,
        int impno,
        bool return_nodeids
    ):
        """
        radius - search radius
        num_of_pois - number of pois to search for
        category - category id
        impno - the impedance id to use
        return_nodeids - whether to return the nodeid locations of the nearest
            not just the distances
        """
        return self.access.findAllNearestPOIs(
            radius, num_of_pois, category, impno, return_nodeids)
