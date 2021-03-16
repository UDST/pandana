/*
    open source routing machine
    Copyright (C) Dennis Luxen, others 2010

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU AFFERO General Public License as published by
the Free Software Foundation; either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see http://www.gnu.org/licenses/agpl.txt.
 */

#include "libch.h"
#include "POIIndex/POIIndex.h"
#if defined(_OPENMP) && (defined(__amd64__) || defined(__i386__))
#include "Util/HyperThreading.h"
#endif
namespace CH {

inline ostream& operator<< (ostream& os, const Edge& e) {
    os << "[" << e.name() << "]= (" << e.source() << (e.backward ? "<" : "") << "-" << (e.forward ? ">" : "") << e.target() << ")|" << e.weight();
    return os;
}
    ContractionHierarchies::ContractionHierarchies() : numberOfThreads(1){
        contractor  = NULL;
        staticGraph = NULL;
        rangeGraph = NULL;
    }

    ContractionHierarchies::ContractionHierarchies(unsigned _n) : numberOfThreads(_n){
        CHASSERT(numberOfThreads != 0, "At least one query thread must be given");
        contractor  = NULL;
        staticGraph = NULL;
		rangeGraph = NULL;
//#ifdef _OPENMP
//        omp_set_num_threads(12);
//#endif
    }

    ContractionHierarchies::~ContractionHierarchies() {
        nodeVector.clear();

        for(unsigned i = 0; i < queryObjects.size(); i++) {
            delete queryObjects[i];
        }
        poiIndexMap.clear();
        queryObjects.clear();
        
        //delete all objects, clean up space
        CHDELETE (contractor );
        CHDELETE (staticGraph);
        CHDELETE (rangeGraph);

    }

	void ContractionHierarchies::reset(void) {

	}

	void ContractionHierarchies::SetNodeVector( const vector<Node> & nv){

        nodeVector.reserve(nv.size());

		//fill node vector and construct map on the way
		for(unsigned i = 0; i < nv.size(); i++) {
			//copy element
			this->nodeVector.push_back(nv[i]);
		}
	}

	void ContractionHierarchies::SetEdgeVector( const vector<Edge> & ev) {

		CHASSERT(this->nodeVector.size(), "NodeVector unset");
		CHASSERT(!this->edgeList.size(), "EdgeList already set");

		//fill edge vector and check if each target and source node exists
		for(unsigned i = 0; i < ev.size(); i++) {
			this->edgeList.push_back(ev[i]);
		}
		CHASSERT(ev.size() == this->edgeList.size(), "edge lists sizes differ");
		this->contractor = new Contractor( this->nodeVector.size(), this->edgeList );
        this->rangeGraph = BuildRangeGraph(this->nodeVector.size(), this->edgeList);        
	}

	std::string ContractionHierarchies::GetVersionString () {
		return std::string("CH for UrbanSim 0.1");
	}

	void ContractionHierarchies::RunPreprocessing() {
		//build CH
		this->contractor->Run();

		//clean CH
		std::vector< ContractionCleanup::Edge > contractedEdges;
		this->contractor->GetEdges( contractedEdges );
		ContractionCleanup * cleanup = new ContractionCleanup(this->nodeVector.size(), contractedEdges);
		contractedEdges.clear();
		cleanup->Run();

		std::vector< InputEdge> cleanedEdgeList;
		cleanup->GetData(cleanedEdgeList);
		delete cleanup;

		//build query object
		this->staticGraph = new QueryGraph(this->nodeVector.size(), cleanedEdgeList);
		for(unsigned i = 0; i < numberOfThreads; ++i) {
		    queryObjects.push_back(new SimpleCHQuery<EdgeData, QueryGraph, Heap>(this->staticGraph, this->rangeGraph));
		}
		//std::cout << "finished constructing query objects" << std::endl;
		//deconstruct contractor?
		CHDELETE(this->contractor);
		//std::cout << "destructed contractor" << std::endl;
	}

	QueryGraph * ContractionHierarchies::BuildRangeGraph(const int nodes, const std::vector< Edge >& inputEdges) {
	    QueryGraph * _graph;
        std::vector< InputEdge > edges;
        edges.reserve( 2 * inputEdges.size() );
        for ( std::vector< Edge >::const_iterator i = inputEdges.begin(), e = inputEdges.end(); i != e; ++i ) {
            InputEdge edge;
            edge.source = i->source();
            edge.target = i->target();

            edge.data.distance = std::max((int)i->weight(), 1 );

            assert( edge.data.distance > 0 );
            edge.data.shortcut = false;
            edge.data.middleName.nameID = i->name();
            edge.data.forward = i->isForward();
            edge.data.backward = i->isBackward();
            edges.push_back( edge );
            std::swap( edge.source, edge.target );
            edge.data.forward = i->isBackward();
            edge.data.backward = i->isForward();
            edges.push_back( edge );
        }
        sort( edges.begin(), edges.end() );
        NodeID edge = 0;
        for ( NodeID i = 0; i < edges.size(); ) {
            const NodeID source = edges[i].source;
            const NodeID target = edges[i].target;
            const NodeID middle = edges[i].data.middleName.nameID;

            assert(edges[i].data.distance > 0);
            
           // const short type = 0; //edges[i].data.type;
            //assert(type >= 0);
            //remove eigenloops
            if ( source == target ) {
                i++;
                continue;
            }
            InputEdge forwardEdge;
            InputEdge backwardEdge;
            forwardEdge.source = backwardEdge.source = source;
            forwardEdge.target = backwardEdge.target = target;
            forwardEdge.data.forward = backwardEdge.data.backward = true;
            forwardEdge.data.backward = backwardEdge.data.forward = false;
            //forwardEdge.data.type = backwardEdge.data.type = type;
            forwardEdge.data.middleName.nameID = backwardEdge.data.middleName.nameID = middle;
            forwardEdge.data.shortcut = backwardEdge.data.shortcut = false;
            forwardEdge.data.distance = backwardEdge.data.distance = std::numeric_limits<int>::max();
            //remove parallel edges
            while ( i < edges.size() && edges[i].source == source && edges[i].target == target ) {
                if ( edges[i].data.forward )
                    forwardEdge.data.distance = std::min( edges[i].data.distance, forwardEdge.data.distance );
                if ( edges[i].data.backward )
                    backwardEdge.data.distance = std::min( edges[i].data.distance, backwardEdge.data.distance );
                
                assert(edges[i].data.distance > 0);
                assert(forwardEdge.data.distance > 0);
                assert(backwardEdge.data.distance > 0);

                i++;
            }
            assert(forwardEdge.data.distance > 0);
            assert(backwardEdge.data.distance > 0);
            //merge edges (s,t) and (t,s) into bidirectional edge
            if ( forwardEdge.data.distance == backwardEdge.data.distance ) {
                if ( (int)forwardEdge.data.distance != std::numeric_limits< int >::max() ) {
                    forwardEdge.data.backward = true;
                    edges[edge++] = forwardEdge;
                    assert(forwardEdge.data.distance > 0);
                //    INFO("src: " << forwardEdge.source << ", tgt: " << forwardEdge.target << ", dst: " << forwardEdge.data.distance);
                }
            } else { //insert seperate edges
                if ( (int)forwardEdge.data.distance != std::numeric_limits< int >::max() ) {
                    edges[edge++] = forwardEdge;
                //    INFO("src: " << forwardEdge.source << ", tgt: " << forwardEdge.target << ", dst: " << forwardEdge.data.distance);
                }
                if ( (int)backwardEdge.data.distance != std::numeric_limits< int >::max() ) {
                    edges[edge++] = backwardEdge;
                //    INFO("src: " << backwardEdge.source << ", tgt: " << backwardEdge.target << ", dst: " << backwardEdge.data.distance);
                }
            }
        }
        
        FILE_LOG(logINFO) << "Range graph removed " << edges.size() - edge 
                          << " edges of " << edges.size() << "\n";
        
        //INFO("Range graph removed " << edges.size() - edge << " edges of " << edges.size());
        assert(edge <= edges.size());
        edges.resize( edge );
        _graph = new QueryGraph( nodes, edges );
        std::vector< InputEdge >().swap( edges );
        return _graph;
    }

    int ContractionHierarchies::computeLengthofShortestPath(const Node &s, const Node& t){
        return computeLengthofShortestPath(s, t, 0);
    }

	int ContractionHierarchies::computeLengthofShortestPath(const Node &s, const Node& t, unsigned threadID){
		CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
		CHASSERT(queryObjects.size() > threadID, "Accessing invalid threadID");
		NodeID start(UINT_MAX);
		NodeID target(UINT_MAX);

		if(s.id < nodeVector.size()) {
			start = s.id;
		} else {
			return UINT_MAX;
		}

		if(t.id < nodeVector.size()) {
			target = t.id;
		} else {
			return UINT_MAX;
		}
		return this->queryObjects[threadID]->ComputeDistanceBetweenNodes(start, target);
	}

    int ContractionHierarchies::computeVerificationLengthofShortestPath(const Node &s, const Node& t){
		CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
		NodeID start(UINT_MAX);
		NodeID target(UINT_MAX);
        
		if(s.id < nodeVector.size()) {
			start = s.id;
		} else {
			return UINT_MAX;
		}
        
		if(t.id < nodeVector.size()) {
			target = t.id;
		} else {
			return UINT_MAX;
		}
		return this->queryObjects[0]->SimpleDijkstraQuery(start, target);
	}

    int ContractionHierarchies::computeShortestPath(const Node &s, const Node& t, vector<NodeID> & ResultingPath){
        return computeShortestPath(s, t, ResultingPath, 0);
    }
    
	int ContractionHierarchies::computeShortestPath(const Node &s, const Node& t, vector<NodeID> & ResultingPath, unsigned threadID){
		CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
        CHASSERT(queryObjects.size() > threadID, "Accessing invalid threadID");
		NodeID start(UINT_MAX);
		NodeID target(UINT_MAX);

        if(s.id < nodeVector.size()) {
            start = s.id;
        } else {
            return UINT_MAX;
        }

        if(t.id < nodeVector.size()) {
            target = t.id;
        } else {
            return UINT_MAX;
        }
		return queryObjects[threadID]->ComputeRoute(start, target, ResultingPath);
	}

    void ContractionHierarchies::computeReachableNodesWithin(const Node &s, unsigned maxDistance, std::vector<std::pair<NodeID, unsigned> > & ResultingNodes){
        computeReachableNodesWithin(s, maxDistance, ResultingNodes, 0);
    }

	void ContractionHierarchies::computeReachableNodesWithin(const Node &s, unsigned maxDistance, std::vector<std::pair<NodeID, unsigned> > & ResultingNodes, unsigned threadID){
		CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
        CHASSERT(queryObjects.size() > threadID, "Accessing invalid threadID");
        NodeID start(UINT_MAX);

        if(s.id < nodeVector.size()) {
            start = s.id;
        } else {
            return;
        }

        queryObjects[threadID]->RangeQuery(start, maxDistance, ResultingNodes);
	}
    
    /** POI queries single threaded */
    void ContractionHierarchies::createPOIIndex(const POIKeyType &category, unsigned maxDistanceToConsider,
                                                unsigned maxNumberOfPOIsInBucket)
    {
         CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
         if(poiIndexMap.find(category) != poiIndexMap.end())
             poiIndexMap.erase(poiIndexMap.find(category));

         // reinitialize this bucket
         poiIndexMap.insert(CHPOIIndexMap::value_type(category, CHPOIIndex(this->staticGraph, maxDistanceToConsider,
                                                                           maxNumberOfPOIsInBucket, numberOfThreads)));
    }
    

    void ContractionHierarchies::addPOIToIndex(const POIKeyType &category, NodeID node)
    {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.addPOIToIndex(node);
    }
    

    void ContractionHierarchies::getNearest(const POIKeyType &category, NodeID node, std::vector<BucketEntry>& resultingVenues) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIs(node, resultingVenues);
    }
    

    void ContractionHierarchies::getNearestWithUpperBoundOnDistance(const POIKeyType &category, NodeID node, EdgeWeight maxDistance,
                                                                    std::vector<BucketEntry>& resultingVenues) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIsWithUpperBoundOnDistance(node, maxDistance, resultingVenues);
    }


    void ContractionHierarchies::getNearestWithUpperBoundOnLocations(const POIKeyType &category, NodeID node, unsigned maxLocations,
                                                                     std::vector<BucketEntry>& resultingVenues) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIsWithUpperBoundOnLocations(node, maxLocations, resultingVenues);
    }
    

    void ContractionHierarchies::getNearestWithUpperBoundOnDistanceAndLocations(const POIKeyType &category, NodeID node,
                                                                                EdgeWeight maxDistance, unsigned maxLocations,
                                                                                std::vector<BucketEntry>& resultingVenues) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIs(node, resultingVenues, maxDistance, maxLocations);
    }
    

    /** POI queries multi-threaded */    
    void ContractionHierarchies::getNearest(const POIKeyType &category, NodeID node, std::vector<BucketEntry>& resultingVenues,
                                            unsigned threadID) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIs(node, resultingVenues, threadID);
    }

    
    void ContractionHierarchies::getNearestWithUpperBoundOnDistance(const POIKeyType &category, NodeID node,
                                                                    EdgeWeight maxDistance, std::vector<BucketEntry>& resultingVenues,
                                                                    unsigned threadID) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIsWithUpperBoundOnDistance(node, maxDistance, resultingVenues, threadID);
    }
    

    void ContractionHierarchies::getNearestWithUpperBoundOnLocations(const POIKeyType &category, NodeID node, unsigned maxLocations,
                                                                     std::vector<BucketEntry>& resultingVenues, unsigned threadID) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIsWithUpperBoundOnLocations(node, maxLocations, resultingVenues, threadID);
    }


    void ContractionHierarchies::getNearestWithUpperBoundOnDistanceAndLocations(const POIKeyType &category, NodeID node,
                                                                                EdgeWeight maxDistance, unsigned maxLocations,
                                                                                std::vector<BucketEntry>& resultingVenues, unsigned threadID) {
        CHASSERT(this->staticGraph != NULL, "Preprocessing not finished");
	CHPOIIndexMap::iterator category_poi = poiIndexMap.find(category);
        if(category_poi != poiIndexMap.end())
            category_poi->second.getNearestPOIs(node, resultingVenues, maxDistance, maxLocations, threadID);
    }

}
