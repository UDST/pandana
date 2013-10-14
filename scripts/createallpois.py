import psycopg2, cPickle
import numpy

conn_string = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

pois = {}

c = 1

s = "select category ,ST_X(ST_Transform(SetSRID(the_geom,4326),3740)), ST_Y(ST_Transform(SetSRID(the_geom,4326),3740)) from factual_places where bayarea"

print s
cursor.execute(s)

records = cursor.fetchall()

d = {}
for r in records:
    cat, x, y, = r
    d.setdefault(cat,[]) 
    d[cat].append((x,y))

for k, v in d.items():
    a = numpy.array(v,dtype=numpy.float32)
    pois[k] = a

cPickle.dump(pois,open('allpois.jar','w'))
