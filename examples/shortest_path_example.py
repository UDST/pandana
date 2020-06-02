"""
This is a simple test of pandana functionality. If it runs with no errors
you should see output something like:

> python demos/example.py
Generating contraction hierarchies with 4 threads.
Setting CH node vector of size 1498
Setting CH edge vector of size 1702
[info src/contraction_hierarchies/src/libch.cpp:205] Range graph removed 1900 edges of 3404
. 10% . 20% . 30% . 40% . 50% . 60% . 70% . 80% . 90% . 100%
 100%

Depending on whether your installed copy of pandana was built with OpenMP
support it may be run with multiple threads or only 1.

"""
from __future__ import print_function

import os.path
import sys
import time

import numpy as np
import pandas as pd
import pandana.network as pdna

if len(sys.argv) > 1:
    # allow test file to be passed as an argument
    storef = sys.argv[1]
else:
    # if no argument provided look for it in the test data
    storef = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../pandana/tests/osm_sample.h5'))

if not os.path.isfile(storef):
    raise IOError('Could not find test input file: {!r}'.format(storef))

print('Building network from file: {!r}'.format(storef))

store = pd.HDFStore(storef, "r")
nodes, edges = store.nodes, store.edges
net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to,
                   edges[["weight"]])
store.close()
print()

# Demonstrate shortest path code
print('Shortest path 1:')
a = nodes.index[0]
print(a)
b = nodes.index[-1]
print(b)

print(net.shortest_path(a,b))
print(net.shortest_path_length(a,b))

print('Shortest path 2:')
a = nodes.index[5]
print(a)
b = nodes.index[50]
print(b)

print(net.shortest_path(a,b))
print(net.shortest_path_length(a,b))

print('Repeat with vectorized calculations:')
nodes_a = [nodes.index[0], nodes.index[5]]
nodes_b = [nodes.index[-1], nodes.index[50]]
print(net.shortest_path_lengths(nodes_a, nodes_b))

# Performance comparison
print('Performance comparison for 10k distance calculations:')
n = 10000

nodes_a = np.random.choice(nodes.index, n)
nodes_b = np.random.choice(nodes.index, n)

t0 = time.time()
for i in range(n):
    _ = net.shortest_path_length(nodes_a[i], nodes_b[i])
print('Loop time = {} sec'.format(time.time() - t0))

t0 = time.time()
_ = net.shortest_path_lengths(nodes_a, nodes_b)
print('Vectorized time = {} sec'.format(time.time() - t0))
