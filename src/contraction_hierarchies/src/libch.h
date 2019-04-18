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
#ifndef LIBCH_H_INCLUDED
#define LIBCH_H_INCLUDED

#include <cassert>
#include <ostream>
#include <iostream>
#include <string>
#include <vector>
#include <map>

#include "BasicDefinitions.h"
#include "Contractor/ContractionCleanup.h"
#include "Contractor/Contractor.h"
#include "DataStructures/SimpleCHQuery.h"
#include "DataStructures/StaticGraph.h"
#include "POIIndex/POIIndex.h"

#define FILE_LOG(logINFO) (std::cout)

struct _HeapData {
    NodeID parent;
    _HeapData( NodeID p ) : parent(p) { }
};

typedef BinaryHeap< NodeID, NodeID, EdgeWeight, _HeapData, ArrayStorage<NodeID, NodeID> > Heap;

typedef ContractionCleanup::Edge::EdgeData EdgeData;
typedef StaticGraph<EdgeData>::InputEdge InputEdge;
typedef StaticGraph< EdgeData > QueryGraph;
typedef vector<SimpleCHQuery<EdgeData, QueryGraph, Heap> > QueryObjectVector;

typedef CH::POIIndex< QueryGraph > CHPOIIndex;
typedef std::string POIKeyType;
typedef std::map<POIKeyType, CHPOIIndex> CHPOIIndexMap;

namespace CH {

//Note: latitude and longitude are multiplied by 10^6 and internally represented by integers.

struct Node {
    Node(unsigned i, int lt, int ln) : id(i), lat(lt), lon(ln) {}
    Node(unsigned i, float lt, float ln) : id(i), lat(lt*LATLON_MULTIPLIER), lon(ln*LATLON_MULTIPLIER) {}
    Node(unsigned i, double lt, double ln) : id(i), lat(lt*LATLON_MULTIPLIER), lon(ln*LATLON_MULTIPLIER) {}
    unsigned id;
    int lat;
    int lon;
};

struct Edge {
    bool operator< (const Edge& e) const {
        if (source() == e.source()) {
            if (target() == e.target()) {
                if (weight() == e.weight()) {
                    return (isForward() && isBackward() &&
                            ((! e.isForward()) || (! e.isBackward())));
                }
                return (weight() < e.weight());
            }
            return (target() < e.target());
        }
        return (source() < e.source());
    }

    /** Default constructor. target and weight are set to 0.*/
    Edge() : _source(0), _target(0), _id(0), forward(0), _weight(0), backward(0) { assert(false); } //shall not be used.

    explicit Edge(NodeID s, NodeID t, EdgeID n, EdgeWeight w, bool f, bool b) : //, short ty) :
            _source(s), _target(t), _id(n), forward(f), _weight(w), backward(b) { }

    NodeID target() const {return _target; }
    NodeID source() const {return _source; }
    NodeID name() const { return _id; }
    EdgeWeight weight() const {return _weight; }

    bool isBackward() const { return backward; }
    bool isForward() const { return forward; }

    unsigned _source;
    unsigned _target;
    unsigned _id;
    bool forward;
    unsigned _weight;
    bool backward;
};

typedef std::vector<std::pair<NodeID, unsigned> > ReachedNode;

	//The CH Interface will have the following functions:
    class ContractionHierarchies {

	public:
        ContractionHierarchies();
		ContractionHierarchies(unsigned numberOfThreads);
		~ContractionHierarchies(void);

		void reset(void);
		std::string GetVersionString ();
		void SetNodeVector( const vector<Node> & nv);
		void SetEdgeVector( const vector<Edge> & e);
		void RunPreprocessing();
        int computeLengthofShortestPath(const Node &s, const Node& t);
        int computeLengthofShortestPath(const Node &s, const Node& t, unsigned threadID);
        int computeShortestPath(const Node &s, const Node& t, vector<NodeID> & ResultingPath);
        int computeShortestPath(const Node &s, const Node& t, vector<NodeID> & ResultingPath, unsigned threadID);
        int computeVerificationLengthofShortestPath(const Node &s, const Node& t);
        void computeReachableNodesWithin(const Node &s, unsigned maxDistance, std::vector<std::pair<NodeID, unsigned> > & ResultingNodes);
        void computeReachableNodesWithin(const Node &s, unsigned maxDistance, std::vector<std::pair<NodeID, unsigned> > & ResultingNodes, unsigned threadID);

        void createPOIIndex(const POIKeyType &category, unsigned _maxDistanceToConsider, unsigned _maxNumberOfPOIsInBucket);
        void addPOIToIndex(const POIKeyType &category, NodeID node);

        void getNearest(const POIKeyType &category, NodeID node, std::vector<BucketEntry>& resultingVenues);
        void getNearest(const POIKeyType &category, NodeID node, std::vector<BucketEntry>& resultingVenues, unsigned threadID);
        void getNearestWithUpperBoundOnLocations(const POIKeyType &category, NodeID node, EdgeWeight maxLocations,
                                                 std::vector<BucketEntry>& resultingVenues);
        void getNearestWithUpperBoundOnLocations(const POIKeyType &category, NodeID node, EdgeWeight maxLocations,
                                                 std::vector<BucketEntry>& resultingVenues, unsigned threadID);
        void getNearestWithUpperBoundOnDistance(const POIKeyType &category, NodeID node, unsigned maxLocations,
                                                std::vector<BucketEntry>& resultingVenues);
        void getNearestWithUpperBoundOnDistance(const POIKeyType &category, NodeID node, unsigned maxLocations,
                                                std::vector<BucketEntry>& resultingVenues, unsigned threadID);
        void getNearestWithUpperBoundOnDistanceAndLocations(const POIKeyType &category, NodeID node,
                                                            EdgeWeight maxDistance, unsigned maxLocations, std::vector<BucketEntry>& resultingVenues);
        void getNearestWithUpperBoundOnDistanceAndLocations(const POIKeyType &category, NodeID node,
                                                            EdgeWeight maxDistance, unsigned maxLocations,
                                                            std::vector<BucketEntry>& resultingVenues, unsigned threadID);

	private:
		unsigned numberOfThreads;
		QueryGraph * BuildRangeGraph(const int nodes, const std::vector< Edge >& inputEdges);
		vector<Node> nodeVector;
		vector<Edge> edgeList;

		Contractor* contractor;
		QueryGraph * staticGraph;
		QueryGraph * rangeGraph;
		vector<SimpleCHQuery<EdgeData, QueryGraph, Heap> *> queryObjects;
        CHPOIIndexMap poiIndexMap;
	};
}

#endif
