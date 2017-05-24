import pandas as pd
import numpy as np
from pandana.cyaccess import cyaccess

store = pd.HDFStore("pandana/tests/osm_sample.h5", "r")
nodes = store.nodes
edges = store.edges[["from", "to"]]

node_locations = pd.Series(np.arange(len(nodes)), index=nodes.index)
edges["from"] = node_locations.loc[edges["from"]].values
edges["to"] = node_locations.loc[edges["to"]].values
# print edges

edge_weights = store.edges[["weight"]]

net = cyaccess(
	nodes.index.values,
    nodes.as_matrix(),
	edges.as_matrix(),
	edge_weights.transpose().as_matrix(),
	False
)

net.initialize_pois(1, 10, 3)
random_node_ids = np.random.choice(np.arange(len(nodes)), 30)
print random_node_ids
net.initialize_category(0, random_node_ids)
ret = net.find_all_nearest_pois(10, 3, 0, 0, True)
print
print pd.DataFrame(ret)[0].value_counts()