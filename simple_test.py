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
	True
)

net.initialize_pois(1, 10, 3)
NUM_NODES = 30
random_node_ids = np.random.choice(np.arange(len(nodes)), NUM_NODES)
print random_node_ids
net.initialize_category(0, random_node_ids)
ret = net.find_all_nearest_pois(10, 3, 0, 0, True)
print pd.DataFrame(ret)[0].value_counts()

net.precompute_range(10)
net.initialize_access_vars(1)
random_vals = np.random.random(NUM_NODES) * 100
print random_vals
net.initialize_access_var(0, random_node_ids, random_vals)
ret = net.get_all_aggregate_accessibility_variables(10, 0, 0, 2)
ret = pd.Series(ret)
print ret[ret > 0]
print ret.describe()

print pd.Series(net.shortest_path(996, 71))
print net.shortest_path_distance(996, 71)