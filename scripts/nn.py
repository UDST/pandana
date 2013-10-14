import cPickle, time, sys, string, StringIO
from pyaccess import PyAccess
import psycopg2, cPickle
import numpy

conn_string = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"
#conn_string = "host='urbansim1.webhop.org' port=5433 dbname='denver' user='urbanvision' password='Visua1ization'"
#conn_string = "host='localhost' dbname='bayarea' user='urbanvision' password='Visua1ization'"
#conn_string = "host='localhost' dbname='california' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

#s = "select hhid, x_utm, y_utm from batshh"
#s = "select parcel_id, st_x(centroid), st_y(centroid) from parcels_for_reference"
#s = "select parcel_id, st_x(centroid), st_y(centroid) from parcels2010"
#s = "select tripid, st_x(origpoint), st_y(origpoint) from bats where origpoint is not null"
#s = "select bats_id, st_x(destpoint), st_y(destpoint) from bats where destpoint is not null"
#s = "select gid, st_x(st_transform(setsrid(the_geom,4326),3740)), st_y(st_transform(setsrid(the_geom,4326),3740)) from navteq_restaurants where fac_type = 9996 and poi_name = 'STARBUCKS'"
#s = "select dunsnumber, st_x(st_transform(setsrid(st_point(longitude,latitude),4326),3740)), st_y(st_transform(setsrid(st_point(longitude,latitude),4326),3740)) from nets2011_digestformodel"
s = 'select costar_id, st_x(st_transform(setsrid(st_point(cast("Longitude" as float),cast("Latitude" as float)),4326),3740)), st_y(st_transform(setsrid(st_point(cast("Longitude" as float),cast("Latitude" as float)),4326),3740)) from costar where cast("Longitude" as float) <> 0 and cast("Latitude" as float) <> 0'

print s
cursor.execute(s)

records = cursor.fetchall()
hhids = []
xys = []
for r in records:
    hhid, x, y = r
    hhids.append(hhid)
    xys.append((x,y))

xys = numpy.array(xys,numpy.float32)

#d = cPickle.load(open('/var/www/network_drcog.jar'))
d = cPickle.load(open('../walknetwork.jar'))
pya = PyAccess()
edgeweights = d['edgeweights']
pya.createGraphs(1)
pya.createGraph(0,d['nodeids'],d['nodes'],d['edges'],edgeweights)
nodeids = pya.XYtoNode(xys)
nodeids = [d['nodeids'][x] for x in nodeids]

tblname = "costarrel_osm"
#s = "DROP TABLE if exists hhrel_osm; CREATE TABLE hhrel_osm (hhid int, nodeid int)"
s = "DROP TABLE if exists %s; CREATE TABLE %s (gid int, nodeid int)" % (tblname,tblname)
#s = "DROP TABLE if exists origrel_osm; CREATE TABLE origrel_osm (tripid int, nodeid int)"
#s = "DROP TABLE if exists destrel_osm; CREATE TABLE destrel_osm (tripid int, nodeid int)"
#s = "DROP TABLE if exists sbrel_osm; CREATE TABLE sbrel_osm (gid int, nodeid int)"

cursor.execute(s)

s = ''
for hhid, nid in zip(hhids,nodeids):
    add = nid
    s += "%s,%s\n" % (str(hhid), str(add))

s = StringIO.StringIO(s)
cursor.copy_from(s,tblname,sep=',')
#cursor.copy_from(s,'hhrel_osm',sep=',')
#cursor.copy_from(s,'origrel_osm',sep=',')
#cursor.copy_from(s,'destrel_osm',sep=',')
#cursor.copy_from(s,'sbrel_osm',sep=',')
conn.commit()
