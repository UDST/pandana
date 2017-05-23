import pandas as pd
from pyaccess import pyAccess

store = pd.HDFStore("pandana/tests/osm_sample.h5", "r")
nodes = store.nodes
edges = store.edges[["from", "to"]]
edge_weights = store.edges[["weight"]]

net = pyAccess(
	nodes.index.values.astype('int32'),
    nodes.as_matrix().astype('float32'),
	edges.as_matrix().astype('int32'),
	edge_weights.as_matrix().astype('float32'),
	False
)