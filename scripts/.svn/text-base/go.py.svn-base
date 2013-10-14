import cPickle, time, sys, string, StringIO, random
from pyaccess import PyAccess
import psycopg2
import numpy
import yep

'''
crime data
school data
street width / parking / urban design (trees, furniture, art)
tourist destinations (photos)
political party affiliation
twitter density
vacancy rates
permits
heightmaps
'''

RANDOMSAMPLE=1.0
MAXDISTANCE=45

t1 = time.time()

import accessutils
ua = accessutils.UrbanAccess(MAXDISTANCE,'./')
pya = ua.pya

t2 = time.time()

print "Computing design variables"
 
data = {}

data['design_linealstreetfeet'] = pya.computeAllDesignVariables(.5,"LINEALSTREETFEET")
data['design_numnodes'] = pya.computeAllDesignVariables(.5,"NUMNODES")
data['design_pct4wayintersections'] = pya.computeAllDesignVariables(.5,"PCT4WAYINTERSECTIONS")
'''
data['design_averageblocklength'] = pya.computeAllDesignVariables(.5,"AVERAGEBLOCKLENGTH")
data['design_numstreetedges'] = pya.computeAllDesignVariables(.5,"NUMSTREETEDGES")
data['design_culdesacs'] = pya.computeAllDesignVariables(.5,"NUMCULDESACS")
data['design_aveedgecurvature'] = pya.computeAllDesignVariables(.5,"AVEEDGECURVATURE")
data['design_numaccesspoints'] = pya.computeAllDesignVariables(.5,"NUMACCESSPOINTS")
'''

data['built_disttogrocery'] = pya.findAllNearestPOIs(15*1.6,3)
data['built_disttopark'] = pya.findAllNearestPOIs(15*1.6,5)
data['travel_transit'] = pya.findAllNearestPOIs(15*1.6,9)
data['built_walkscores'] = pya.getAllOpenWalkscores()

#yep.start('aggregate.prof')
numimpedances = 1
for i in range(len(ua.accvarnames)):
  for j in range(numimpedances):
    name = ua.accvarnames[i]
    prefix = ''
    if name in ua.demovarnames: prefix = 'demo_'
    elif 'nets_' not in name: prefix = 'built_'
    fname = prefix+name
    print fname
    if name in ['stories','averageincome','averageage','rent','sale_price','unit_sqft','year_built','lot_size']:
        fname = prefix+name+'_average_local'
        data[fname] = pya.getAllAggregateAccessibilityVariables(.5,i,1,2) #,gno=j)
    elif 'nets' in name and 'loc' not in name:
      for dist in [15,30,45]:
        if dist > MAXDISTANCE: continue
        fname = prefix+name+'_regional'
        rng = [1] # only AM by default
        if 'ret' in name: rng = [4] # only PM for retail
        if 'all' in name: rng = range(5) # for all, do all 5 time slices
        for k in rng: # impedances
            impfname = fname+str(k)+'_'+str(dist)
            data[impfname] = pya.getAllAggregateAccessibilityVariables(dist,i,0,1,gno=1,impno=k)
            data[impfname] = pya.convertgraphs(1,0,data[impfname])
        tranfname = fname+'_transit_' + str(dist)
        data[tranfname] = pya.getAllAggregateAccessibilityVariables(dist,i,0,1,gno=2)
        data[tranfname] = pya.convertgraphs(2,0,data[tranfname],500)
    else:
        dists = [.5]
        if 'nets' in name: dists = [.5,1,2,3,4.8]
        for dist in dists:
            if dist == .5: fname = prefix+name+'_local'
            elif dist == 4.8: fname = prefix+name+'_local_5'
            else: fname = prefix+name+'_local_'+str(dist)
            data[fname] = pya.getAllAggregateAccessibilityVariables(dist,i,0,1) #,gno=j)
#yep.stop()
#sys.exit()

for i in range(numimpedances):
    def doshare(prefix,outname,inname1,inname2,impednum):
        outname = '%s_%s_to_%s_ratio_local' % (prefix,inname1,inname2)
        inname1 = '%s_%s_local' % (prefix,inname1)
        inname2 = '%s_%s_local' % (prefix,inname2)
        data[outname] = numpy.nan_to_num(numpy.divide(data[inname1],data[inname2]))
    doshare('built','multifamily','multifamily','units',i)
    doshare('built','singlefamily','singlefamily','units',i)
    doshare('demo','children','children','pop',i)
    del(data['demo_children_local'])
    doshare('demo','highincometohh','highincomehhs','hhs',i)
    del(data['demo_highincomehhs_local'])
    doshare('demo','lowincometohh','lowincomehhs','hhs',i)
    del(data['demo_lowincomehhs_local'])
    doshare('demo','black','blackhhs','hhs',i)
    del(data['demo_blackhhs_local'])
    doshare('demo','latino','latinohhs','hhs',i)
    del(data['demo_latinohhs_local'])
    doshare('demo','asian','asianhhs','hhs',i)
    del(data['demo_asianhhs_local'])
    doshare('demo','workers','workers','pop',i)
    del(data['demo_workers_local'])
    doshare('demo','cars','cars','pop',i)
    del(data['demo_cars_local'])
    doshare('demo','renters','renthhs','hhs',i)
    del(data['demo_renthhs_local'])
    doshare('demo','old','oldhhs','hhs',i)
    del(data['demo_oldhhs_local'])
    doshare('demo','hhswithchildren','hhswithchildren','hhs',i)
    del(data['demo_hhswithchildren_local'])
    doshare('demo','householdsize','pop','hhs',i)

data['nets_ret_reg_regional_transit_45'] = data['nets_ret_reg_regional_transit_45'] - data['nets_ret_loc_local_5']
data['nets_ret_loc_local_3'] = data['nets_ret_loc_local_3'] - data['nets_ret_loc_local_2'] 
data['nets_ret_reg_regional4_15'] = data['nets_ret_reg_regional4_15'] - data['nets_ret_loc_local_2']
data['nets_ret_loc_local_2'] = data['nets_ret_loc_local_2'] - data['nets_ret_loc_local_1']

t2 = time.time()


conn_string = "host='localhost' dbname='sandbox' user='urbanvision' password='Visua1ization'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

#for key, value in data.items():
#    data[key] = (value - numpy.mean(value))/numpy.std(value)

keys = data.keys()
keys.sort()

NODESTABLE = 'nodes_jesus'
t = ['%s float8' % x for x in keys]
t = string.join(t,sep=',')
s = "DROP TABLE IF EXISTS %s; CREATE TABLE %s (id int, %s, the_geom POLYGON)" % (NODESTABLE,NODESTABLE,t)

cursor.execute(s)

s = ''
nodexy = ua.network['nodes']
nodeids = ua.network['nodeids']
cnt = 0
for i in range(len(nodexy)):
    if random.random() > RANDOMSAMPLE: continue
    node = nodexy[i]
    cnt += 1
    t = string.join([str(data[x][i]) for x in keys],sep=',')
    s += "%d,%s,POINT(%f %f)\n" % (nodeids[i],t,node[0],node[1])

s = StringIO.StringIO(s)
cursor.copy_from(s,NODESTABLE,sep=',')
conn.commit()

t3 = time.time()
print "Wrote %d nodes to db in" % cnt, t3-t2
