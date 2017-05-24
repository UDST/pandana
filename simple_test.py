import pandas as pd
import numpy as np
from pyaccess import pyAccess

store = pd.HDFStore("pandana/tests/osm_sample.h5", "r")
nodes = store.nodes
edges = store.edges[["from", "to"]]
edge_weights = store.edges[["weight"]]

net = pyAccess(
	nodes.index.values,
    nodes.as_matrix(),
	edges.as_matrix(),
	edge_weights.as_matrix(),
	False
)

net.initialize_pois(1, 10, 3)
random_node_ids = np.random.choice(np.arange(len(nodes)), 100)
net.initialize_category(0, random_node_ids)
print net.find_all_nearest_pois(3, 2, 0, 0, False)