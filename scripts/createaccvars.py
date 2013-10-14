import psycopg2, cPickle
import numpy

conn_string = "host='localhost' dbname='bayarea' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

s = "select parcel_id, shape_area, ST_X(ST_Centroid(the_geom)), ST_Y(ST_Centroid(the_geom)) from parcels2010"

print s
cursor.execute(s)

records = cursor.fetchall()

ids = []
parcel_xy = []
shape_area = []
for r in records:
    id, area, x, y, = r
    ids.append(id)
    parcel_xy.append((x,y))
    shape_area.append(area)

ids = numpy.array(ids,dtype=numpy.int32)
parcel_xy = numpy.array(parcel_xy,dtype=numpy.float32)
shape_area = numpy.array(shape_area,dtype=numpy.float32)

d = {}
d['parcel_data'] = (ids,parcel_xy,[shape_area])

s = "select building_id, b.parcel_id, stories, building_sqft, building_type_id, residential_units, year_built, shape_area from buildings2010 as b, buildings2010_sta as sta, parcels2010 as p where b.building_id = sta.id and scenario = 1 and b.parcel_id = p.parcel_id"

print s
cursor.execute(s)

records = cursor.fetchall()

ids = []
parcel_ids = []
stories = []
sqfts = []
types = []
units = []
years = []
areas = []
for r in records:
    id, pid, story, sqft, typ, unit, year, area = r
    ids.append(id)
    parcel_ids.append(pid)
    if story == None: story = 0
    stories.append(story)
    if sqft == None: sqft = 0
    sqfts.append(sqft)
    if typ == None: typ = 0
    types.append(typ)
    if unit == None: unit = 0
    units.append(unit)
    if year == None: year = 0
    years.append(year)
    if area == None: area = 0
    areas.append(area)

ids = numpy.array(ids,dtype=numpy.int32)
parcel_ids = numpy.array(parcel_ids,dtype=numpy.int32)
stories = numpy.array(stories,dtype=numpy.float32)
sqfts = numpy.array(sqfts,dtype=numpy.float32)
types = numpy.array(types,dtype=numpy.float32)
units = numpy.array(units,dtype=numpy.float32)
years = numpy.array(years,dtype=numpy.float32)
areas = numpy.array(areas,dtype=numpy.float32)

d['building_data'] = (ids,parcel_ids,[stories,sqfts,types,units,years,areas])

s = "select household_id, b.parcel_id, race_id, age_of_head, income, persons, children, h.tenure, cars, workers from households2000 h, buildings2010 b where b.building_id = h.building_id"

print s
cursor.execute(s)

records = cursor.fetchall()

ids = []
parcel_ids = []
data = []
for r in records:
    id, pid, r = r[0], r[1], r[2:]
    ids.append(id)
    parcel_ids.append(pid)
    data.append(r)

ids = numpy.array(ids,dtype=numpy.int32)
parcel_ids = numpy.array(parcel_ids,dtype=numpy.int32)
data = numpy.array(data,dtype=numpy.float32)

d['household_data'] = (ids,parcel_ids,data)

s = "select residential_unit_id, b.parcel_id, rent, sale_price, unit_sqft, bedrooms from residential_units u, buildings2010 b where b.building_id = u.building_id and rent > 0 and rent < 4000 and sale_price > 0 and sale_price < 2000000"

print s
cursor.execute(s)

records = cursor.fetchall()

ids = []
parcel_ids = []
data = []
for r in records:
    id, pid, r = r[0], r[1], r[2:]
    ids.append(id)
    parcel_ids.append(pid)
    data.append(r)

ids = numpy.array(ids,dtype=numpy.int32)
parcel_ids = numpy.array(parcel_ids,dtype=numpy.int32)
data = numpy.array(data,dtype=numpy.float32)

d['unit_data'] = (ids,parcel_ids,data)

s = "select \"PropertyType\", averageweightedrent, st_x(st_transform(setsrid(st_point(cast(\"Longitude\" as float),cast(\"Latitude\" as float)),4326),3740)), st_y(st_transform(setsrid(st_point(cast(\"Longitude\" as float),cast(\"Latitude\" as float)),4326),3740)) from costar where cast(\"Latitude\" as float) > 0 and cast(averageweightedrent as float) > 0 and \"PropertyType\" in ('Industrial','Flex','Office','Retail')"

print s
cursor.execute(s)

records = cursor.fetchall()
sics = {}

for r in records:
    sicgroup, emp, x, y = r
    sics.setdefault(sicgroup,[])
    sics[sicgroup].append((x,y,emp))

for key, value in sics.iteritems():
    x, y, emp = zip(*value)
    xys = numpy.array(zip(x,y),dtype=numpy.float32)
    emps = numpy.array(emp,dtype=numpy.float32)
    emps[numpy.where(emps>60)[0]] = 60 # max out at 60
    sics[key] = (xys,emps)

d['costar_data'] = sics 

conn_string2 = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn2 = psycopg2.connect(conn_string2)
cursor2 = conn2.cursor()
s = "select sicgroup, emp, st_x(st_transform(setsrid(the_geom,4326),3740)), st_y(st_transform(setsrid(the_geom,4326),3740)) from nets"

print s
cursor2.execute(s)

records = cursor2.fetchall()
sics = {}

sics.setdefault('all',[])
for r in records:
    sicgroup, emp, x, y = r
    sics['all'].append((x,y,emp))
    if sicgroup in ['ret_loc','ret_reg','info','fire','health','man_lgt','logis']:
        sics.setdefault(sicgroup,[])
        sics[sicgroup].append((x,y,emp))

for key, value in sics.iteritems():
    x, y, emp = zip(*value)
    xys = numpy.array(zip(x,y),dtype=numpy.float32)
    emps = numpy.array(emp,dtype=numpy.float32)
    sics[key] = (xys,emps)

d['nets_data'] = sics

s = "select gid, pid, nonres_sqft, res_units, npv from buildings_run452"

print s
cursor2.execute(s)

records = cursor2.fetchall()

ids = []
parcel_ids = []
data = []
for r in records:
    id, pid, r = r[0], r[1], r[2:]
    ids.append(id)
    parcel_ids.append(pid)
    data.append(r)

ids = numpy.array(ids,dtype=numpy.int32)
parcel_ids = numpy.array(parcel_ids,dtype=numpy.int32)
data = numpy.array(data,dtype=numpy.float32)

d['growth_data'] = (ids,parcel_ids,data)

cPickle.dump(d,open('accvars.jar','w'))
