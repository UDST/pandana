import cPickle, time, sys, string, StringIO, random
from pyaccess import PyAccess
import psycopg2
import psycopg2.extras
import numpy
import yep

RANDOMSAMPLE=1.0

t1 = time.time()

walk = cPickle.load(open('walknetwork.jar'))
pois = cPickle.load(open('allpois.jar'))
accvars_d = cPickle.load(open('accvars.jar'))

s = "SELECT osm_node_id FROM parcels2010 p, buildings2010_base b, parcels2010_geography pg WHERE (b.building_type_id > 3) AND (((p.parcel_id = pg.parcel_id) AND (p.parcel_id = b.parcel_id))) group by pg.osm_node_id"

conn_string = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print s
cursor.execute(s)

records = cursor.fetchall()

pya = PyAccess()

pya.createGraphs(1)
pya.createGraph(0,walk['nodeids'],walk['nodes'],walk['edges'],walk['edgeweights']/1000.0,twoway=1)
nodexy = walk['nodes']
nodeids = walk['nodeids']

id2index = {}
for i in range(nodeids.size):
    id2index[nodeids[i]] = i

nonresindices = []
for r in records:
    if not r['osm_node_id']: continue
    osm_node_id = int(r['osm_node_id'])
    if osm_node_id not in id2index:
        print "WARNING"
        continue
    nonresindices.append(id2index[osm_node_id])
    
print "Precomputing ranges"

pya.precomputeRange(1.5,0) # distance

data = {}

pya.initializeAccVars(1)
c = 1
for key, values in pois.items():
    if not key: key = 'blank'
    key = str(c)+key
    c += 1
    print key
    nodes = pya.XYtoNode(values,gno=0)
    ones = numpy.ones((nodes.size),dtype=numpy.float32)
    pya.initializeAccVar(0,[nodes],ones,preaggregate=0) 
    data[key] = pya.getAllAggregateAccessibilityVariables(.5,0,0,1)[nonresindices]


conn_string = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

keys = data.keys()
keys.sort()

t = ['"%s" float8' % x for x in keys]
t = string.join(t,sep=',')
s = "DROP TABLE IF EXISTS nodes_pois; CREATE TABLE nodes_pois (id int, %s, the_geom geometry)" % t
print s
cursor.execute(s)

nodeids = nodeids[nonresindices]
nodexy = nodexy[nonresindices]
s = ''
cnt = 0
for i in range(len(nodexy)):
    if random.random() > RANDOMSAMPLE: continue
    node = nodexy[i]
    cnt += 1
    t = string.join([str(data[x][i]) for x in keys],sep=',')
    s += "%d,%s,POINT(%f %f)\n" % (nodeids[i],t,node[0],node[1])

s = StringIO.StringIO(s)
cursor.copy_from(s,'nodes_pois',sep=',')
conn.commit()
