import pandas as pd

import pandana.network as pdna

store = pd.HDFStore('../pandana/tests/osm_sample.h5', "r")
nodes, edges = store.nodes, store.edges
net = pdna.Network(nodes.x, nodes.y, edges["from"], edges.to,
                   edges[["weight"]])
store.close()
