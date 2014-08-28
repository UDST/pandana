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
