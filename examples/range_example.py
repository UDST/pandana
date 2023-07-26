import sys
import time

import pandana

import numpy as np
import pandas as pd
from pympler.asizeof import asizeof

print()
print("Loading data...")
t0 = time.time()
store = pd.HDFStore('examples/data/bayareanetwork.h5', 'r')
nodes, edges = store.nodes, store.edges
print(round(time.time()-t0, 1), ' sec.')

print()
print("Initializing network...")
t0 = time.time()
net = pandana.Network(nodes.x, nodes.y, edges.from_int, edges.to_int, edges[['weight']])
store.close()
print(round(time.time()-t0, 1), ' sec.')

print()
print("Calculating nodes in 100m range...")
t0 = time.time()
r = net.nodes_in_range([53114882, 53107159], 100.0)
print(round(time.time()-t0, 1), ' sec.')

# print(net.node_idx.values)
# print(net.node_idx.index.values)

print(asizeof(r))  # 88.8 million bytes raw

print()

# dataframe.info()
# dataframe.memory_usage(deep=True)
# .set_index(['1', '2'], inplace=True)
