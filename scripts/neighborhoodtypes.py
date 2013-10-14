import psycopg2, cPickle, StringIO
import psycopg2.extras
import numpy
import mdp
import string, time, sys, getopt
from hcluster import pdist, linkage, dendrogram, fclusterdata
from scipy.cluster.vq import *

args = sys.argv[1:]
if not args: args = ['-e','-n','5-15','nodes']
opts, args = getopt.getopt(args, "dbgepn:", [])

employment = design = built = demographics = PCA = True
for o, a in opts:
    if o == "-d": design = False
    if o == "-b": built = False
    if o == "-e": employment = False
    if o == "-g": demographics = False
    if o == "-p": PCA = False
    if o == "-n": 
        if '-' in a:
            a = string.split(a,sep='-')
            assert len(a) == 2
            mincats = int(a[0])
            maxcats = int(a[1])
        else:
            mincats = int(a)
            maxcats = mincats

if not args: tblname = 'nodes_factors'
else:
    assert len(args) == 1
    tblname = args[0]

conn_string = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

s = "select * from %s" % tblname # limit 5000"

badfnames = ['the_geom','id']

print s
cursor.execute(s)

records = cursor.fetchall()
data = []
geom = []
ids = []
for r in records:
    geom.append(r['the_geom'])
    ids.append(r['id'])
    for fname in badfnames: del(r[fname])
    for key in r.keys():
        if not employment and "nets_" in key: del(r[key])
        if not design and "design_" in key: del(r[key])
        if not built and "built_" in key: del(r[key])
        if not demographics and "demo_" in key: del(r[key])
    data.append(r.values())

data = numpy.array(data,dtype=numpy.float32)
data = whiten(data)
data = numpy.minimum(data,8)
data = numpy.maximum(data,-8)
print data.shape

if not len(data):
    print "FATAL ERROR: NO DATA"
    sys.exit()

if PCA: 
    pcan = mdp.nodes.PCANode(output_dim=.8,dtype=numpy.float64)
    print "Computing factors"
    pcar = pcan.execute(data)
    print "Done computing factors"

    print pcan.d
    print pcan.get_explained_variance()
    #print pcan.get_projmatrix(transposed=0)
    #print numpy.dot(data,pcan.get_projmatrix(transposed=1))
    data = pcar
    #data *= pcan.d

print data.shape

cats_l = []
for numcats in range(mincats,maxcats+1):
    print "Num categories = ", numcats
    centroids, cats = kmeans2(data,numcats)
    print cats
    cats_l.append(cats)

NDIM = len(data)

#t = ['factor%d float8' % (i+1) for i in range(NDIM)]
t = ['cat%d float8' % (mincats+i) for i in range(len(cats_l))]
t = string.join(t,sep=',')
s = "DROP TABLE IF EXISTS %s_factors CASCADE; CREATE TABLE %s_factors (id int, %s, the_geom geometry);" % (tblname,tblname,t)
#s = s+"create view parcels2 as SELECT p.parcel_id, p.the_geom, nf.cat7 AS ntype FROM parcels2010 p, buildings2010_base b, parcels2010_geography pg, %s_factors nf WHERE ((((p.shape_area < (1000000)::numeric) AND (p.water = 0)) AND (b.building_type_id > 3)) AND (((p.parcel_id = pg.parcel_id) AND (p.parcel_id = b.parcel_id)) AND (pg.osm_node_id = nf.id)));" % tblname
s = s+"create view parcels2 as SELECT p.parcel_id, p.the_geom, nf.cat10 AS ntype FROM parcels2010 p, parcels2010_geography pg, %s_factors nf WHERE (p.water = 0) AND (((p.parcel_id = pg.parcel_id) AND (pg.osm_node_id = nf.id)));" % tblname
s = s+"create index %s_factors_idx on %s_factors(the_geom);" % (tblname,tblname)

cursor.execute(s)

t2 = time.time()

s = ''
cnt = 0
for i in range(len(geom)):
    cnt += 1
    #t = string.join([str(x) for x in pcar[i]],sep=',')

    cats = []
    for c in cats_l: cats.append(c[i])
    t = string.join([str(x) for x in cats],sep=',')

    #s += "%s,POINT(%f %f)\n" % (t,node[0],node[1])
    s += "%d,%s,%s\n" % (ids[i],t,geom[i])

s = StringIO.StringIO(s)
cursor.copy_from(s,tblname+'_factors',sep=',')
conn.commit()

t3 = time.time()
print "Wrote %d nodes to db in" % cnt, t3-t2
