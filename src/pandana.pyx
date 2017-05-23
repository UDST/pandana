cimport cython
from libcpp cimport bool

cimport numpy as np
import numpy as np


cdef extern from "graphalg.h" namespace "MTC::accessibility":
    cdef cppclass Graphalg:
        Graphalg() except +
        void Build(int*, float*, int, int*, float*, int, bool)


cdef extern from "accessibility.h" namespace "MTC::accessibility":
    cdef cppclass Accessibility:
        Accessibility() except +
        Accessibility(int) except +
        int numnodes
        void addGraphalg(Graphalg*)


cdef class pyAccess:
    cdef Accessibility accessibility_ptr

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
        self.accessibility_ptr = Accessibility(numnodes)

        numimpedances = edge_weights.shape[1]
        for i in range(numimpedances):
            graph_ptr = new Graphalg()
            graph_ptr.Build(&node_ids[0], &node_xys[0, 0], numnodes,
                            &edges[0, 0], &edge_weights[i, 0], numedges,
                            twoway)
            self.accessibility_ptr.addGraphalg(graph_ptr)
