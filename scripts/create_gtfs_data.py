import csv, os, psycopg2, string, zipfile, StringIO

conn_string = "host='paris.urbansim.org' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

def create_table(createtablesql,filename,tblname,fieldnames):
    s = "DROP TABLE if exists %s" % tblname
    cursor.execute(s)
    cursor.execute(createtablesql)

    s = ''
    for zipf, zipfname in zipfiles:
        zf = zipf.open(filename)
        f = csv.DictReader(zf)
        for row in f:
            if filename == "shapes.txt" and float(row['shape_pt_lat']) < 0: # a couple rows got this backwards
                row['shape_pt_lat'], row['shape_pt_lon'] = row['shape_pt_lon'], row['shape_pt_lat']
            if zipfname == "gtfs_ferry.zip" and filename == "shapes.txt": continue # ferry shape data is bad

            s += string.join([row[x] if row[x] else '\N' for x in fieldnames],sep='|') + '\n'
    s = StringIO.StringIO(s)
    cursor.copy_from(s,tblname,sep='|')

tblconfigs = [ \
( \
"""
CREATE TABLE "public"."gtfs_trips" (
"route_id" int4,
"service_id" varchar(255),
"trip_id" varchar(255),
"trip_headsign" varchar(255),
"direction_id" varchar(255),
"shape_id" int4
)
""", \
"trips.txt", \
"gtfs_trips", \
["route_id","service_id","trip_id","trip_headsign","direction_id","shape_id"] \
), \
( \
"""
CREATE TABLE "public"."gtfs_routes" (
"route_id" int4,
"agency_id" varchar(255),
"route_short_name" varchar(255),
"route_long_name" varchar(255),
"route_type" varchar(255)
);
""", \
"routes.txt", \
"gtfs_routes", \
["route_id","agency_id","route_short_name","route_long_name","route_type"] \
), \
( \
"""
CREATE TABLE "public"."gtfs_shapes" (
"shape_id" int4,
"shape_pt_lat" float4,
"shape_pt_lon" float4,
"shape_pt_sequence" int4
);
""", \
"shapes.txt", \
"gtfs_shapes", \
["shape_id","shape_pt_lat","shape_pt_lon","shape_pt_sequence"] \
), \
( \
"""
CREATE TABLE "public"."gtfs_calendar" (
"service_id" varchar(255),
"monday" varchar(255),
"tuesday" varchar(255),
"wednesday" varchar(255),
"thursday" varchar(255),
"friday" varchar(255),
"saturday" varchar(255),
"sunday" varchar(255),
"start_date" varchar(255),
"end_date" varchar(255)
);
""", \
"calendar.txt", \
"gtfs_calendar", \
["service_id","monday","tuesday","wednesday","thursday","friday","saturday","sunday","start_date","end_date"] \
), \
( \
"""
CREATE TABLE "public"."gtfs_stops" (
"stop_id" int4,
"stop_name" varchar(255),
"stop_lat" varchar(255),
"stop_lon" varchar(255)
);
""", \
"stops.txt", \
"gtfs_stops", \
["stop_id","stop_name","stop_lat","stop_lon"] \
), \
( \
"""
CREATE TABLE "public"."gtfs_stop_times" (
"trip_id" varchar(32),
"arrival_time" varchar(255),
"departure_time" varchar(255),
"stop_id" int4,
"stop_sequence" int4
);
""", \
"stop_times.txt", \
"gtfs_stop_times", \
["trip_id","arrival_time","departure_time","stop_id","stop_sequence"] \
), \
]

zipfiles = [(zipfile.ZipFile(os.path.join('gtfs',x)),x) for x in ['gtfs_ferry.zip']]
for createtablesql,filename,tblname,fieldnames in tblconfigs:
    print "loading", tblname
    create_table(createtablesql,filename,tblname,fieldnames)

# this ain't pretty AT ALL but the ferry data didn't get stored in the same shape format as the others
# this line creates the shape data for the ferry gtfs
s = """drop table if exists gtfs_shapes_ferry; select shape_id, gs.stop_lat, gs.stop_lon, stop_sequence into gtfs_shapes_ferry from gtfs_stop_times gst, gtfs_trips gt, gtfs_stops gs where gst.trip_id = gt.trip_id and gs.stop_id = gst.stop_id group by shape_id, gs.stop_lat, gs.stop_lon, stop_sequence"""
cursor.execute(s)

zipfiles = [(zipfile.ZipFile(os.path.join('gtfs',x)),x) for x in os.listdir('gtfs')]

for createtablesql,filename,tblname,fieldnames in tblconfigs:
    print "loading", tblname
    create_table(createtablesql,filename,tblname,fieldnames)

s = "insert into gtfs_shapes select cast(shape_id as integer), cast(stop_lat as real), cast(stop_lon as real), cast(stop_sequence as integer) from gtfs_shapes_ferry"
cursor.execute(s)
conn.commit()
