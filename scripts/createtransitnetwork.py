import psycopg2, cPickle, string, StringIO, sys
import numpy, time

conn_string = "host='paris.urbansim.org' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

s = """select shape_id, shape_pt_sequence, 
       ST_X(ST_TRANSFORM(ST_SETSRID(ST_POINT(shape_pt_lon, shape_pt_lat),4326),3740)),
       ST_Y(ST_TRANSFORM(ST_SETSRID(ST_POINT(shape_pt_lon, shape_pt_lat),4326),3740))
       from gtfs_shapes"""
print s
cursor.execute(s)
records = cursor.fetchall()
print "Fetched %d records" % len(records)

nodes = {}
for r in records:
    shape_id, sequence, x, y = r
    nodes[(shape_id,sequence)] = (x,y)

s = "select gst.*, gt.shape_id from gtfs_stop_times gst, gtfs_trips gt where gst.trip_id = gt.trip_id order by trip_id, stop_sequence"
print s
cursor.execute(s)
records = cursor.fetchall()
print "Fetched %d records" % len(records)

trips = {}
for r in records:
    trip_id, arrival, departure, stop_id, sequence, shape_id = r
    trips.setdefault(trip_id,[])
    trips[trip_id].append(((shape_id,sequence),arrival))

s = """select route_id, direction_id, trip_id
from gtfs_trips gt, gtfs_calendar gc
where gt.service_id = gc.service_id and cast(gc.monday as boolean)
order by route_id, trip_id, direction_id"""
print s

cursor.execute(s)
records = cursor.fetchall()
print "Fetched %d records" % len(records)

routes = {}
for r in records:
    route_id, direction, trip_id = r
    key = (route_id, direction)
    routes.setdefault(key,[])
    routes[key].append(trip_id) 

def time_diff(s1,s2):
    #print s1, s2
    t1 = time.mktime(time.strptime(s1,'%H:%M:%S'))
    t2 = time.mktime(time.strptime(s2,'%H:%M:%S'))
    return t2 - t1

def add_time(s1,td):
    t1 = time.mktime(time.strptime(s1,'%H:%M:%S'))+td
    return time.strftime('%H:%M:%S',time.localtime(t1))

def later_than_eight(s1):
    return time_diff('08:00:00',s1)

def later_than_seventeen(s1):
    return time_diff('17:00:00',s1)

edges = {}
edge_count = 0
def make_edge(trip_id):
    global edge_count
    #print trips[trip_id]
    prevarrival = None
    prevstop_id = None
    trip = trips[trip_id]
    for i in range(len(trip)):
         stop_id, arrival = trip[i]
         if arrival == None:
             # is this a data error or a timing error?
             if prevarrival == None: continue
             j = 0
             while i+j < len(trip) and not trip[i+j][1]: j += 1
             if i+j == len(trip): continue # empty times at the end of the trip
             #print prevarrival, trip[i+j][1]
             td = time_diff(prevarrival,trip[i+j][1])/(j+1)
             arrival = add_time(prevarrival,td)
         else:
             if prevarrival == None:
                 prevarrival = arrival
                 prevstop_id = stop_id
                 continue 
             td = time_diff(prevarrival,arrival)
         
         #print td, prevstop_id, stop_id
         if prevstop_id in nodes and stop_id in nodes:
             edges[edge_count] = (td,prevstop_id,stop_id)
             edge_count += 1
         prevarrival = arrival
         if stop_id in nodes:
             prevstop_id = stop_id

for (route,direction),trip_ids in routes.items():
    #print route, direction
    # on second thought, maybe I won't count infrequent routes as providing generalized access
    #if len(trip_ids) < 5: continue
    for trip in trip_ids:
        #print trip
        starttime = trips[trip][0][1]
        # data error - sometimes start time is null in the first element
        if not starttime: starttime = trips[trip][1][1]
        if not starttime: continue
        if int(string.split(starttime,':')[0]) >= 24: continue # after midnight
        # XXX transit is hard - this makes no accounting for the frequency of service
        # a route who's first run after 8AM is 5PM gets the same credit as one that runs every 3 minutes
        if later_than_eight(starttime) > 0:
            if later_than_seventeen(starttime) > 0: continue
            make_edge(trip)
            break


print "Writing out data"
print "Number of nodes: ", len(nodes)
print "Number of edges: ", len(edges)

d = {}
#d['nodeids'] = numpy.array(nodes.keys(),dtype=numpy.int32)
d['nodeids'] = numpy.array([1000000+i for i in range(len(nodes))],dtype=numpy.int32) # make fake node ids
d['nodes'] = numpy.array(nodes.values(),dtype=numpy.float32)
noded = dict(zip(nodes.keys(),range(len(nodes.keys()))))
d['edgeids'] = numpy.array(edges.keys())
d['edges'] = numpy.array([[noded[x[1]],noded[x[2]]] \
								for x in edges.values()],dtype=numpy.int32)
d['edgeweights'] = numpy.array([x[0] for x in edges.values()],dtype=numpy.float32)
d['edgeweights'] /= 60.0 # convert to minutes

cPickle.dump(d,open('transitnetwork.jar','w'))

s = "DROP TABLE if exists transitedges; CREATE TABLE transitedges (eid int, time float, geom geometry)"

conn_string = "host='paris.urbansim.org' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

cursor.execute(s)

s = ''
for eid, (weight,node1,node2) in edges.items():
    s = "insert into transitedges values (%d,%f,ST_GEOMFROMTEXT(\'LINESTRING(%f %f, %f %f)\',3740))" % (eid,weight/60.0,nodes[node1][0],nodes[node1][1],nodes[node2][0],nodes[node2][1])
    cursor.execute(s)
conn.commit()
