cimport cython
from libcpp cimport bool
from libcpp.vector cimport vector

cimport numpy as np
import numpy as np


cdef extern from "graphalg.h" namespace "MTC::accessibility":
    cdef cppclass Graphalg:
        Graphalg(int*, float*, int, int*, float*, int, bool) except +


cdef extern from "accessibility.h" namespace "MTC::accessibility":
    cdef cppclass Accessibility:
        Accessibility(int) except +
        int numnodes
        void addGraphalg(Graphalg*)
        void initializePOIs(int, double, int)
        void initializeCategory(int, vector[int])
        vector[vector[float]] findAllNearestPOIs(float, int, int, int, bool)


cdef class pyAccess:
    cdef Accessibility *access

    def __cinit__(
        self,
        np.ndarray[int] node_ids,
        np.ndarray[float, ndim=2] node_xys,
        np.ndarray[int, ndim=2] edges,
        np.ndarray[float, ndim=2] edge_weights,
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
        numnodes = len(node_ids)
        numedges = len(edges)
        self.access = new Accessibility(numnodes)

        numimpedances = edge_weights.shape[1]
        for i in range(numimpedances):
            graphalg = new Graphalg(
                &node_ids[0], &node_xys[0, 0], numnodes,
                &edges[0, 0], &edge_weights[i, 0], numedges,
                twoway
            )
            self.access.addGraphalg(graphalg)

    def __dealloc__(self):
        del self.access

    def initialize_pois(self, numcategories, maxdist, maxitems):
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
