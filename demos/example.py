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
import os.path

import pandas as pd
import pandana.network as pdna

storef = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../pandana/tests/osm_sample.h5')
store = pd.HDFStore(storef, "r")
nodes, edges = store.nodes, store.edges
net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to,
                   edges[["weight"]])
store.close()
