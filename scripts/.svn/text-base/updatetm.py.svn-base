import psycopg2, cPickle
import numpy

conn_string = "host='localhost' dbname='bayarea' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

s = "select id, km, tm_id from osm_topo"

cursor.execute(s)

records = cursor.fetchall()

d = {}
for r in records:
    id, km, tm_id = r
    if not tm_id: continue
    d.setdefault(tm_id,[])
    d[tm_id].append((id, km))

s = ''
for v in d.values():
    ids, kms = zip(*v)
    tot = sum(kms)
    for id in ids:
        s += 'update osm_topo set km_tot = %f where id = %d;' % (tot,id)

cursor.execute(s)
conn.commit()
