cimport cython

cimport numpy as np
import numpy as np

cdef extern from "graphalg.h" namespace "MTC::accessibility":
  cdef cppclass Accessibility:
    Graphalg(int) except +

cdef extern from "accessibility.h" namespace "MTC::accessibility":
  cdef cppclass Accessibility:
    Accessibility(int) except +
    int numnodes


@cython.boundscheck(False)
@cython.wraparound(False)
def create_graph(
  # vector of node ids
  np.ndarray[int] node_ids,
  # vector of spatial locations
  np.ndarray[double, ndim=2] node_xys,
  # vector of edges (tuple of node ids)
  np.ndarray[int, ndim=2] edges,
  # weights for those edges (can be 2D)
  np.ndarray[double, ndim=2] edge_weights,
  # whether edges are bi-directional
  cdef bool twoway
  ):

  numnodes = len(node_ids)
  numedges = len(edges)
  accessibility_ptr = new Accessibility(numnodes)

  numimpedances = edge_weights.shape[1]
  for i in range(numimpedances):
    graph_ptr = new Graphalg(node_ids, node_xys, numnodes, edges,
                             edge_weights[i], numedges, twoway)
    # need to fix this - this should be a method that is called
    # to add a new graphalg object to the accessibility object
    accessibility_ptr.ga.push_back(graph_ptr);

  # now what?  create a wrapper class right?
  # http://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html#create-cython-wrapper-class
