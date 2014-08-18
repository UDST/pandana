
    # this function merges the two networks - the first argument is presumed to be the base local street network 
    # while the second argument is a regional network that provides "shortcuts" - canonical example is transit
    # the third agument is the index of the already created walk network
    # the fourth argument is multiplier of edgeweights in the base network (to match units)
    def mergenetworks(my,basenet,addnet,indexofbase=0,multiplier=1.0):
        basenet = copy.deepcopy(basenet)
        NUMNODES = basenet['nodes'].shape[0]
        basenet['edgeweights'] *= multiplier
        # find nearest street node to every transit node
        baseids = my.XYtoNode(addnet['nodes'],gno=indexofbase,distance=-1) 
        assert numpy.intersect1d(basenet['nodeids'],addnet['nodeids']).size == 0
        basenet['nodeids'] = numpy.concatenate((basenet['nodeids'],addnet['nodeids']))
        basenet['nodes'] = numpy.concatenate((basenet['nodes'],addnet['nodes']))
        newedges = []
        newedgeweights = []
        for e in addnet['edges']:
            newe = (baseids[e[0]],e[0]+NUMNODES)
            newedges.append(newe)
            newedgeweights.append(4.0)
            newe = (e[1]+NUMNODES,baseids[e[1]])
            newedges.append(newe)
            newedgeweights.append(0.5)
        newedges = numpy.array(newedges,dtype="int32")
        newedgeweights = numpy.array(newedgeweights,dtype="float32")

        # the indices move over
        addnet['edges']+=NUMNODES
        revedges = numpy.transpose(numpy.vstack((basenet['edges'][:,1],basenet['edges'][:,0])))

        basenet['edges'] = numpy.concatenate((basenet['edges'],revedges,addnet['edges'],newedges))
        basenet['edgeweights'] = numpy.concatenate((basenet['edgeweights'],basenet['edgeweights'],addnet['edgeweights'],newedgeweights))

        return basenet

    def initializePOIs(my,numcategories,maxdist,maxitems):
        _pyaccess.initialize_pois(numcategories,maxdist,maxitems)

    def initializeCategory(my,cat,latlongs):
        _pyaccess.initialize_category(cat,latlongs)

    def findAllNearestPOIs(my,radius,category):
        l = _pyaccess.find_all_nearest_pois(radius,category)
        return [x if x != -1 else radius for x in l]

    def getAllOpenWalkscores(my):
        return _pyaccess.get_all_open_walkscores()

    def getAllModelResults(my,radius,varindexes,varcoeffs,distcoeff=0.0, \
                                                asc=0.0,denom=-1.0,nestdenom=-1.0,mu=1.0,gno=0,impno=0):
        varindexes = np.array(varindexes,dtype="int32")
        varcoeffs = np.array(varcoeffs,dtype="float32")
        return _pyaccess.get_all_model_results(radius,varindexes,varcoeffs,distcoeff,asc,denom,nestdenom,mu,gno,impno)

    def getAllWeightedAverages(my,index,localradius=.5,regionalradius=3.0,minimumobservations=10,agg=1,decay=2):
        local = my.getAllAggregateAccessibilityVariables(localradius,index,agg,decay) #,gno=j)
        localcnt = my.getAllAggregateAccessibilityVariables(localradius,index,6,2) #,gno=j)
        regional = my.getAllAggregateAccessibilityVariables(regionalradius,index,agg,decay) #,gno=j)
        regionalcnt = my.getAllAggregateAccessibilityVariables(regionalradius,index,6,2) #,gno=j)
        localcnt[numpy.where(localcnt>minimumobservations)[0]] = minimumobservations
        localprop = localcnt / float(minimumobservations)
        regionalprop = 1.0-localprop
        weightedave = local*localprop+regional*regionalprop
        weightedave[numpy.where(regionalcnt<minimumobservations)[0]] = 0
        return weightedave

    def sampleAllNodesinRange(my,samplesize,radius,gno=0,impno=0):
        return _pyaccess.sample_all_nodes_in_range(samplesize,radius,gno,impno)

    def getNodesinRange(my,nodeid,radius,gno=0,impno=0):
        return _pyaccess.get_nodes_in_range(nodeid,radius,gno,impno)

    def Distance(my,srcnode,destnode,gno=0,impno=0):
        return _pyaccess.route_distance(srcnode,destnode,gno,impno)
