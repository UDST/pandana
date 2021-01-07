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

# Demonstrate "nodes in range" code - the largest connected subgraph here has 477 nodes,
# per the unit tests

net.set(pd.Series(net.node_ids))
#s = net.aggregate(10000, type='count')
#connected_nodes = s[s==477]

print(net.nodes_in_range(53114882, 5.0))

print(net.node_idx.values)
print(net.node_idx.index.values)
