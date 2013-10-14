import psycopg2, cPickle
import numpy

conn_string = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

pois = {}
'''
for table, whereclause, keyname in [ \
('restaurants','where fac_type != 9996',''), \
('shopping','where fac_type != 5400 and fac_type != 9995',''), \
('fininsts','',''), \
('parkrec','',''), \
('eduinsts','',''), \
('entertn','',''), \
('restaurants','where fac_type = 9996','coffeeshops'), \
('shopping','where fac_type = 5400','grocery'), \
('shopping','where fac_type = 9995','bookstore'), \
]:
     
    s = "select poi_id, ST_X(ST_Transform(SetSRID(the_geom,4326),3740)), ST_Y(ST_Transform(SetSRID(the_geom,4326),3740)) from navteq_%s %s" % \
														(table, whereclause)
'''

c = 1
for keyname, whereclause in [ \
('restaurants','Restaurants'), \
('shopping','Shopping'), \
('fininsts','Banking'), \
('parkrec','Recreation'), \
('eduinsts','Education'), \
('entertn','Entertainment'), \
('coffeeshops','Coffee'), \
('grocery','Groceries'), \
('bookstore','Bookstores'), \
]:
     
    s = "select 1, ST_X(ST_Transform(SetSRID(the_geom,4326),3740)), ST_Y(ST_Transform(SetSRID(the_geom,4326),3740)) from factual_places where position('%s' in category) > 0 and bayarea" % \
														(whereclause)

    print s
    cursor.execute(s)

    records = cursor.fetchall()
    if len(records) == 0:
        print keyname
        assert(0)

    d = {}
    for r in records:
        id, x, y, = r
        id = c
        c += 1
        d[id] = (x,y)

    d = numpy.array(d.values(),dtype=numpy.float32)

    if not keyname: keyname = table
    pois[keyname] = d


conn_string = "host='localhost' dbname='bayarea' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
s = "select gid, ST_X(the_geom), ST_Y(the_geom) from tpp_transit_stops"

print s
cursor.execute(s)

records = cursor.fetchall()

d = {}
for r in records:
    id, x, y, = r
    d[id] = (x,y)

d = numpy.array(d.values(),dtype=numpy.float32)

pois['transit'] = d


cPickle.dump(pois,open('pois.jar','w'))
