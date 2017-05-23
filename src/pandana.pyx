cimport cython
from libcpp cimport bool

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


cdef class pyAccess:
    cdef Accessibility *access

    def __cinit__(
        self,
        # vector of node ids
        np.ndarray[int] node_ids,
        # vector of spatial locations
        np.ndarray[float, ndim=2] node_xys,
        # vector of edges (tuple of node ids)
        np.ndarray[int, ndim=2] edges,
        # weights for those edges (can be 2D)
        np.ndarray[float, ndim=2] edge_weights,
        # whether edges are bi-directional
        bool twoway = False
    ):
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