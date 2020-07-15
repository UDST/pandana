import os
import time

import numpy as np
import pandas as pd
import pandana.network as pdna

print()
print('Initializing Pandana network...')
print()

storef = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../pandana/tests/osm_sample.h5'))

store = pd.HDFStore(storef, "r")
nodes, edges = store.nodes, store.edges
net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to, edges[["weight"]])
store.close()
print()
print()

print('Performing multithreading assessment...')
print()
print('This times the execution of two small Pandana operations, one always')
print('single-threaded and the other potentially multithreaded.')
print()
print('Typical execution time ratios:')
print('- with successful 8-thread multithreading: 1.5 to 2.0')
print('- without multithreading: 0.2 to 0.5')
print()

node_ids = net.get_node_ids(nodes.x, nodes.y)
t0 = time.time()
net.set(node_ids, variable=nodes.x, name='longitude')
single = time.time()-t0

t0 = time.time()
net.precompute(10000)
multi = time.time()-t0

print('Your execution time ratio: {}'.format(single/multi))
print()