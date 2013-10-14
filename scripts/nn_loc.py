from pyaccess.pyaccess import PyAccess
import pandas as pd, numpy as np, cPickle

d = cPickle.load(open('mrcog_network.jar'))
pya = PyAccess()
pya.createGraphs(1)
pya.createGraph(0,d['nodeids'],d['nodes'],d['edges'],d['edgeweights'])

df = pd.read_csv('mrcog_parcel_centroids.csv')
xys = np.array(df[['x','y']],dtype="float32")
nodeids = pya.XYtoNode(xys)
#nodeids = [d['nodeids'][x] for x in nodeids]
df["nodeid"] = nodeids
df.to_csv('mrcog_parcel_centroids_wnodeid.csv',index=False)
