import cPickle, numpy
import numpy as np, sys, os
from pyaccess import PyAccess

class UrbanAccess():

  def __init__(my,pya=None):
    my.pya=pya

  def process_network(my,MAXDISTANCE,rootdir,mergenetworks=0,walkminutes=0,fixtransit=0):

    loadauto = loadwalk = loadtransit = 1
    my.pya = PyAccess()
    my.pya.createGraphs(3)
    if loadauto:
      auto = cPickle.load(open(os.path.join(rootdir,'travelnetwork.jar')))
      my.pya.createGraph(1,auto['nodeids'],auto['nodes'],auto['edges'],auto['impedances'].transpose(),twoway=0)
      my.pya.precomputeRange(MAXDISTANCE,1) # travel time
    if loadwalk or loadtransit:
      walk = cPickle.load(open(os.path.join(rootdir,'walknetwork.jar')))
      my.network = walk
      factor = 1000.0 if not walkminutes else 80.466 # units on the walk network is either distance or time
      my.pya.createGraph(0,walk['nodeids'],walk['nodes'],walk['edges'],walk['edgeweights']/factor,twoway=1)
      maxdist = 5.0 if not walkminutes else MAXDISTANCE
      my.pya.precomputeRange(maxdist,0) # distance - 4.8=45 mins
    if loadtransit:
      transit = cPickle.load(open(os.path.join(rootdir,'transitnetwork.jar')))

      if mergenetworks and not fixtransit:
        assert 0 # don't do this anymore

      if mergenetworks:
        transit = my.pya.mergenetworks(walk,transit,indexofbase=0,multiplier=(1/80.466)) # convert meters to minutes

      if fixtransit:
        my.remove_disconnected_subgraphs(transit,gno=2,maxdistance=30.0,twoway=0)
        cPickle.dump(transit,open(rootdir+'fixedtransitnetwork.jar','w'))
        print "EXITING BECAUSE WE FIXED TRANSIT NETWORK - CAN'T REPROCESS SAME GRAPH"
        sys.exit()

      my.pya.createGraph(2,transit['nodeids'],transit['nodes'],transit['edges'],transit['edgeweights'],twoway=0)
      my.pya.precomputeRange(MAXDISTANCE,2) # travel time


  def remove_disconnected_subgraphs(my,d,gno=0,twoway=1,maxdistance=2.0):
    SUBGRAPHKEEPTHRESHOLD = 20
    my.pya.createGraph(gno,d['nodeids'],d['nodes'],d['edges'],d['edgeweights'],twoway=twoway)
    numnodes = my.pya.computeAllDesignVariables(maxdistance,"NUMNODES",gno=gno) # nodes within a large distance, 5km
    dropidx = numpy.where(numnodes < SUBGRAPHKEEPTHRESHOLD)[0]
    print "Removing %d nodes" % dropidx.size
   
    # change edges array so it uses nodeids instead of indexes since we're changing indexes
    edges = np.reshape(d['edges'],(-1,1))
    edges = np.array([d['nodeids'][i] for i in edges])

    drop_d = dict(zip(dropidx,dropidx))
    deledges = []
    for i in range(d['edges'].shape[0]):
        edge = d['edges'][i]
        if edge[0] in drop_d or edge[1] in drop_d:
            deledges.append(i)
    d['edges'] = np.reshape(edges,(-1,2))

    deledges = np.array(deledges)
    d['nodeids'] = np.delete(d['nodeids'],dropidx,0)
    nodemap = dict(zip(list(d['nodeids']),range(d['nodeids'].size)))
    d['nodes'] = np.delete(d['nodes'],dropidx,0)
    d['edges'] = np.delete(d['edges'],deledges,0)
    d['edgeweights'] = np.delete(d['edgeweights'],deledges,0)

    edges = np.reshape(d['edges'],(-1,1))
    edges = np.array([nodemap[int(i)] for i in edges],dtype="int32")
    d['edges'] = np.reshape(edges,(-1,2))


  def process_pois(my,rootdir):

    pois = cPickle.load(open(rootdir+'pois.jar'))

    print "Adding POIs"
    
    my.pya.initializePOIs(10,15*1.6,10)
    
    my.pya.initializeCategory(0,pois['coffeeshops'])
    my.pya.initializeCategory(1,pois['restaurants'])
    my.pya.initializeCategory(2,pois['shopping'])
    my.pya.initializeCategory(3,pois['grocery'])
    my.pya.initializeCategory(4,pois['fininsts'])
    my.pya.initializeCategory(5,pois['parkrec'])
    my.pya.initializeCategory(6,pois['eduinsts'])
    my.pya.initializeCategory(7,pois['bookstore'])
    my.pya.initializeCategory(8,pois['entertn'])
    my.pya.initializeCategory(9,pois['transit'])


  def process_variables(my,rootdir):

    print "Reading accessibility variables from disk"
    accvars_d = cPickle.load(open(rootdir+'accvars.jar'))
 
    print "Setting parcels locations"
 
    ids, xy, accvars = accvars_d['parcel_data']
    my.pya.setparcelxys(ids,xy)

    print "Configuring datasets"
    
    ids, pids, accvars = accvars_d['building_data']
    stories,sqft,types,units,year_built,lot_size = accvars
    nodes = my.pya.pids2nodes(pids)
    
    accvarnames = ['stories','sqft','units','singlefamily','multifamily','office','stripretail','bigbox','hoodretail','totalretail','lightindustry','warehouseindustry','heavyindustry','year_built','lot_size']
    
    nets = accvars_d['nets_data']
    
    for sic, (xys, emps) in nets.items():
        accvarnames.append('nets_'+sic)

    costar = accvars_d['costar_data']
    
    for btype, (xys, rent) in costar.items():
        accvarnames.append('costar_'+btype)
    
    demovarnames = ['pop','children','hhs','oldhhs','renthhs','blackhhs','latinohhs','asianhhs','lowincomehhs','highincomehhs','workers','cars','hhswithchildren','averageage','averageincome']
    unitvarnames = ['rent','sale_price','unit_sqft']
    growthvarnames = ['growth_sqft','growth_units','growth_npv']
    accvarnames += demovarnames
    accvarnames += unitvarnames
    accvarnames += growthvarnames
    my.accvarnames = accvarnames
    my.demovarnames = demovarnames
    
    my.pya.initializeAccVars(len(accvarnames))

    print "Adding building data"

    my.pya.initializeAccVar(accvarnames.index('stories'),nodes,stories,preaggregate=0) 
    my.pya.initializeAccVar(accvarnames.index('sqft'),nodes,sqft) 
    my.pya.initializeAccVar(accvarnames.index('units'),nodes,units) 
    valid = numpy.where(year_built > 1800)
    my.pya.initializeAccVar(accvarnames.index('year_built'),my.pya.subset(nodes,valid),year_built[valid],preaggregate=0) 
    sf = numpy.where(types==1)
    my.pya.initializeAccVar(accvarnames.index('lot_size'),my.pya.subset(nodes,sf),lot_size[sf],preaggregate=0) 
    
    singlefamily = units*numpy.array(types==1,dtype=numpy.float32)
    multifamily = units*numpy.array(types!=1,dtype=numpy.float32)
    office = sqft*numpy.array(types==4,dtype=numpy.float32)
    strip = sqft*numpy.array(types==10,dtype=numpy.float32)
    bigbox = sqft*numpy.array(types==11,dtype=numpy.float32)
    neighborhood = sqft*numpy.array(types==12,dtype=numpy.float32)
    lightindustry = sqft*numpy.array(types==7,dtype=numpy.float32)
    warehouseindustry = sqft*numpy.array(types==8,dtype=numpy.float32)
    heavyindustry = sqft*numpy.array(types==9,dtype=numpy.float32)
    totalretail = bigbox+strip+neighborhood
    
    my.pya.initializeAccVar(accvarnames.index('singlefamily'),nodes,singlefamily) 
    my.pya.initializeAccVar(accvarnames.index('multifamily'),nodes,multifamily) 
    my.pya.initializeAccVar(accvarnames.index('office'),nodes,office) 
    my.pya.initializeAccVar(accvarnames.index('bigbox'),nodes,bigbox) 
    my.pya.initializeAccVar(accvarnames.index('hoodretail'),nodes,neighborhood) 
    my.pya.initializeAccVar(accvarnames.index('stripretail'),nodes,strip) 
    my.pya.initializeAccVar(accvarnames.index('totalretail'),nodes,totalretail) 
    my.pya.initializeAccVar(accvarnames.index('lightindustry'),nodes,lightindustry) 
    my.pya.initializeAccVar(accvarnames.index('warehouseindustry'),nodes,warehouseindustry) 
    my.pya.initializeAccVar(accvarnames.index('heavyindustry'),nodes,heavyindustry) 
   
    # HOUSEHOLD DATA
    
    print "Adding household data"

    ids, pids, accvars = accvars_d['household_data']
    accvars = numpy.transpose(accvars)
    race,ageofhead,income,persons,children,tenure,cars,workers = accvars
    nodes = my.pya.pids2nodes(pids)
    
    my.pya.initializeAccVar(accvarnames.index('pop'),nodes,persons) 
    my.pya.initializeAccVar(accvarnames.index('children'),nodes,children) 
    my.pya.initializeAccVar(accvarnames.index('hhs'),nodes,numpy.ones((len(persons),),dtype=numpy.float32)) 
    oldhhs = numpy.array(ageofhead>65,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('oldhhs'),nodes,oldhhs) 
    renthhs = numpy.array(tenure==1,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('renthhs'),nodes,renthhs) 
    blackhhs = numpy.array(race==3,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('blackhhs'),nodes,blackhhs) 
    latinohhs = numpy.array(race==6,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('latinohhs'),nodes,latinohhs) 
    asianhhs = numpy.array(race==4,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('asianhhs'),nodes,asianhhs) 
    lowincomehhs = numpy.array(income<35000,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('lowincomehhs'),nodes,lowincomehhs) 
    highincomehhs = numpy.array(income>75000,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('highincomehhs'),nodes,highincomehhs) 
    hhswithchildren = numpy.array(children>0,dtype=numpy.float32)
    my.pya.initializeAccVar(accvarnames.index('hhswithchildren'),nodes,hhswithchildren) 
    my.pya.initializeAccVar(accvarnames.index('workers'),nodes,workers) 
    my.pya.initializeAccVar(accvarnames.index('cars'),nodes,cars) 
    my.pya.initializeAccVar(accvarnames.index('averageage'),nodes,ageofhead,preaggregate=0) 
    my.pya.initializeAccVar(accvarnames.index('averageincome'),nodes,income,preaggregate=0) 
    
    # UNIT DATA
    
    print "Adding unit data (prices)"

    ids, pids, accvars = accvars_d['unit_data']
    accvars = numpy.transpose(accvars)
    rent,sale_price,unit_sqft,bedrooms = accvars
    nodes = my.pya.pids2nodes(pids)
    
    my.pya.initializeAccVar(accvarnames.index('rent'),nodes,rent,preaggregate=0) 
    my.pya.initializeAccVar(accvarnames.index('sale_price'),nodes,sale_price,preaggregate=0) 
    my.pya.initializeAccVar(accvarnames.index('unit_sqft'),nodes,unit_sqft,preaggregate=0) 
    
    # GROWTH DATA

    print "Adding growth data"
    
    ids, pids, accvars = accvars_d['growth_data']
    accvars = numpy.transpose(accvars)
    sqft,units,npv = accvars
    nodes = my.pya.pids2nodes(pids)
    
    my.pya.initializeAccVar(accvarnames.index('growth_sqft'),nodes,sqft) 
    my.pya.initializeAccVar(accvarnames.index('growth_units'),nodes,units) 
    my.pya.initializeAccVar(accvarnames.index('growth_npv'),nodes,npv) 
    
    # NETS DATA

    print "Adding nets data"
    
    for sic, (xys, emps) in nets.items():
        nodes = [my.pya.XYtoNode(xys,gno=0),my.pya.XYtoNode(xys,gno=1),my.pya.XYtoNode(xys,gno=2,distance=500)]
        my.pya.initializeAccVar(accvarnames.index('nets_'+sic),nodes,emps) 

    # COSTAR DATA

    print "Adding costar data"
    
    for btype, (xys, rents) in costar.items():
        nodes = [my.pya.XYtoNode(xys,gno=0),my.pya.XYtoNode(xys,gno=1),my.pya.XYtoNode(xys,gno=2,distance=500)]
        my.pya.initializeAccVar(accvarnames.index('costar_'+btype),nodes,rents,preaggregate=0) 
