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

import pandana.network as pdna
from pandana.loaders.pandash5 import _legacy_compatible_hdf_store

if len(sys.argv) > 1:
    # allow test file to be passed as an argument
    storef = sys.argv[1]
else:
    # if no argument provided look for it in the test data
    storef = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../tests/osm_sample.h5'))

if not os.path.isfile(storef):
    raise IOError('Could not find test input file: {!r}'.format(storef))

print('Building network from file: {!r}'.format(storef))

with _legacy_compatible_hdf_store(storef, migrate_legacy=True) as store:
    nodes, edges = store.nodes.copy(), store.edges.copy()
net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to,
                   edges[["weight"]])
