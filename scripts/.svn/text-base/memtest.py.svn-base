import cPickle, time, sys, string, StringIO
from pyaccess import PyAccess
import psycopg2
import numpy
import yep

t1 = time.time()

d = cPickle.load(open('network.jar'))
pois = cPickle.load(open('pois.jar'))
accvars_d = cPickle.load(open('accvars.jar'))

pya = PyAccess()

d['edgeweights'] = d['edgeweights'] / 1000.0
edgeweights = d['edgeweights']
#edgeweights = d['impedances'].transpose()
numimpedances = 1 #edgeweights.shape[0]
print "Number of impedances = %d" % numimpedances

pya.createGraph(1,d['nodeids'],d['nodes'],d['edges'],edgeweights)
#pya.precomputeRange(.5) # distance

ids, xy, accvars = accvars_d['parcel_data']
nodeids = pya.XYtoNode(xy)
node_d = dict(zip(ids,nodeids))

ids, pids, accvars = accvars_d['building_data']
stories,sqft,types,units = accvars

for i in range(len(pids)):
    pids[i] = node_d[pids[i]]

pya.initializeAccVars(1)
while 1:
    pya.initializeAccVar(0,pids,sqft,preaggregate=0) 
    pya.getAllAggregateAccessibilityVariables(.5,0,0,1)
    break
