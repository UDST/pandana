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
#ifndef POIINDEX_H_INCLUDED
#define POIINDEX_H_INCLUDED

#include <vector>

using std::shared_ptr;

#include "../BasicDefinitions.h"
#include "../DataStructures/BinaryHeap.h"

namespace CH {
    struct BucketEntry {
        NodeID node;
        EdgeWeight distance;
        BucketEntry() : node(UINT_MAX), distance(UINT_MAX) {}
        BucketEntry(NodeID n, EdgeWeight d) : node(n), distance(d) {}
        inline bool operator<(const BucketEntry & other) const {
            return distance < other.distance;
        }
    };

    typedef vector<BucketEntry> Bucket;
    typedef std::map<NodeID, Bucket> BucketIndex;

    //No need to store anything in the Heap for an encountered node besides its distance
    struct _POIHeapData {
        _POIHeapData(NodeID p) {}
      //  NodeID parent;
    };
    typedef BinaryHeap<NodeID, NodeID, EdgeWeight, _POIHeapData, ArrayStorage<NodeID, NodeID> > POIHeap;

    template<typename QueryGraphT>
    class POIIndex {
    public:
        POIIndex(QueryGraphT * _graph, unsigned _maxNumberOfPOIsInBucket, unsigned _maxDistanceToConsider) :
        graph(_graph), maxNumberOfPOIsInBucket(_maxNumberOfPOIsInBucket), maxDistanceToConsider(_maxDistanceToConsider),
        numberOfThreads(1) {
            Initialize();
        }

        POIIndex(QueryGraphT * _graph, unsigned _maxDistanceToConsider, unsigned _maxNumberOfPOIsInBucket, unsigned _numberOfThreads) :
        graph(_graph), maxNumberOfPOIsInBucket(_maxNumberOfPOIsInBucket), maxDistanceToConsider(_maxDistanceToConsider),
        numberOfThreads(_numberOfThreads) {
            Initialize();
        }

        ~POIIndex() {
            bucketIndex.clear();
        }

        inline void addPOIToIndex(const NodeID node){
            CHASSERT(node < graph->GetNumberOfNodes(), "Node ID of POI is out of bounds");
            additionHeap->Clear();
            CHASSERT(additionHeap->Size() == 0, "AdditionHeap not empty");
            //explore search space from node v
            additionHeap->Insert(node, 0, node);
            CHASSERT(additionHeap->Size() == 1, "AdditionHeap not empty");
            //For each encountered node u of the backward search space
            while(additionHeap->Size() > 0) {
                const NodeID currentNode = additionHeap->DeleteMin();
                const unsigned toDistance = additionHeap->GetKey( currentNode );
                if(toDistance > maxDistanceToConsider)
                    return;
                //Add venue to bucket of u
                //INFO("Adding POI at node " << node << " to Bucket at node " << currentNode << " with distance " << toDistance);
                Bucket & bucket = bucketIndex[currentNode];
                bucket.push_back(BucketEntry(node, toDistance));

                //sort bucket by distance
                std::sort(bucket.begin(), bucket.end());

                //if(bucket.size() > 1)
                //    INFO("Bucket at node " << currentNode << " has " << bucket.size() << " entries");

                //if bucket size > max then delete last one
                if(bucket.size() > maxNumberOfPOIsInBucket)
                    bucket.resize(maxNumberOfPOIsInBucket);

                //add further edges from backward search space
                for ( typename QueryGraphT::EdgeIterator edge = graph->BeginEdges( currentNode ); edge < graph->EndEdges(currentNode); ++edge ) {
                    if(graph->GetEdgeData(edge).backward) {
                        const NodeID to = graph->GetTarget(edge);
                        CHASSERT( to < graph->GetNumberOfNodes(), "Edge leads to out of bounds target node ID. Graph corrupted");
                        const EdgeWeight edgeDistance = graph->GetEdgeData(edge).distance;

                        CHASSERT( edgeDistance > 0, "Edge (" << currentNode << "," << to << ") has length " << edgeDistance );

                        //Stalling
                        if(graph->GetEdgeData(edge).forward && additionHeap->WasInserted( to )) {
                            if(additionHeap->GetKey( to ) + edgeDistance < toDistance) {
                                break;
                            }
                        }

                        //New Node discovered -> Add to Heap + Node Info Storage
                        if ( !additionHeap->WasInserted( to ) ) {
                            additionHeap->Insert( to, toDistance + edgeDistance, node );
                        }
                        //Found a shorter Path -> Update distance
                        else if ( toDistance + edgeDistance < additionHeap->GetKey( to ) ) {
                            additionHeap->DecreaseKey( to, toDistance + edgeDistance );
                        }
                    }
                }
            }
        }

        //Also, functions for subset of parameters
        inline void getNearestPOIs(NodeID node, std::vector<BucketEntry>& resultingVenues){
            getNearestPOIs(node, resultingVenues, maxDistanceToConsider, maxNumberOfPOIsInBucket);
        }

        inline void getNearestPOIsWithUpperBoundOnDistance(NodeID node, unsigned maxQueryDistanceToConsider, std::vector<BucketEntry>& resultingVenues){
            getNearestPOIs(node, resultingVenues, maxQueryDistanceToConsider, maxNumberOfPOIsInBucket);
        }

        inline void getNearestPOIsWithUpperBoundOnLocations(NodeID node, unsigned maxQueryNumberOfLocationsToConsider, std::vector<BucketEntry>& resultingVenues){
            getNearestPOIs(node, resultingVenues, maxDistanceToConsider, maxQueryNumberOfLocationsToConsider);
        }

        //Multi-threaded functions

        inline void getNearestPOIs(NodeID node, std::vector<BucketEntry>& resultingVenues, unsigned threadID){
            getNearestPOIs(node, resultingVenues, maxDistanceToConsider, maxNumberOfPOIsInBucket, threadID);
        }

        inline void getNearestPOIsWithUpperBoundOnDistance(NodeID node, unsigned maxQueryDistanceToConsider, std::vector<BucketEntry>& resultingVenues, unsigned threadID){
            getNearestPOIs(node, resultingVenues, maxQueryDistanceToConsider, maxNumberOfPOIsInBucket, threadID);
        }

        inline void getNearestPOIsWithUpperBoundOnLocations(NodeID node, unsigned maxQueryNumberOfLocationsToConsider, std::vector<BucketEntry>& resultingVenues, unsigned threadID){
            getNearestPOIs(node, resultingVenues, maxDistanceToConsider, maxQueryNumberOfLocationsToConsider, threadID);
        }

        //Main query function. Both for single and multithreaded

        inline void getNearestPOIs(NodeID node, std::vector<BucketEntry>& resultingVenues, unsigned _maxDistanceToConsider, unsigned _maxNumberOfPOIsInBucket, unsigned threadID = 0){
            CHASSERT(threadID < numberOfThreads, "Invalid thread ID");
            //INFO("Search for nearest venues close to node " << node);
            //INFO("_maxDistanceToConsider: " << _maxDistanceToConsider << ", _maxNumberOfPOIsInBucket: " << _maxNumberOfPOIsInBucket);
            CHASSERT(0 == resultingVenues.size(), "Resulting vector of getNearestQuery is not empty");
            CHASSERT(_maxDistanceToConsider <= maxDistanceToConsider, "Maximum distance to POIs must not be larger in query than during preprocessing");
            CHASSERT(_maxNumberOfPOIsInBucket <= maxNumberOfPOIsInBucket, "Maximumum number of POIs must not be larger in query than during preprocessing");
            POIHeap & resultHeap = threadDataArray[threadID]->resultHeap;
            POIHeap & queryHeap = threadDataArray[threadID]->queryHeap;
            resultHeap.Clear();

            queryHeap.Clear();
            queryHeap.Insert(node, 0, 0);

            //explore search space from node v
            while(queryHeap.Size() > 0) {
                //for each encountered node in forward search space
                const NodeID currentNode = queryHeap.DeleteMin();
                const unsigned toDistance = queryHeap.GetKey(currentNode);
                //INFO("Looking at node " << node << " with distance " << toDistance);

                //continue only if we are not out of distance limits
                if(toDistance > _maxDistanceToConsider) {
                  //  INFO("Reached maximum distance " << _maxDistanceToConsider << " with distance " << toDistance);
                    break;
                }

                //check if there is a bucket entry at that node
                if(bucketIndex.find(currentNode) != bucketIndex.end()) {
                    Bucket & bucket = bucketIndex[currentNode];
                   // INFO("Found bucket of size " << bucket.size() << " at node " << currentNode);
                    //put all venues at bucket into result heap that are closer than maximum distance
                    for(unsigned i = 0; i < bucket.size(); i++){
                        BucketEntry & b = bucket[i];
                        const unsigned distanceToPOI = toDistance + b.distance;
                        //Do we already know this guy?
                        //INFO("Looking at bucket entry " << b.node << "-" << b.distance);
                        if(resultHeap.WasInserted(b.node)){
                            //Yes, lets check if we encountered it with a smaller distance.
                            if(resultHeap.GetKey(b.node) > distanceToPOI){
                                resultHeap.DecreaseKey(b.node, (distanceToPOI));
                           // } else {
                           //     INFO("Not inserting because distance " << toDistance + b.distance << " to node " << b.node << " is not smaller than " << resultHeap.GetKey(b.node));
                            }
                        }else {
                            //No, so lets insert the entry
                            resultHeap.Insert(b.node, distanceToPOI, 0);

                            //INFO("Adding node " << b.node << " with distance " << (toDistance + b.distance) << " to result");
                        }
                    }
                }
               // INFO("Resulting heap has " << resultHeap.Size() << "/" << _maxNumberOfPOIsInBucket << " entries");

                //Relax further edges
                for ( typename QueryGraphT::EdgeIterator edge = graph->BeginEdges( currentNode ); edge < graph->EndEdges(currentNode); ++edge ) {
                    if(graph->GetEdgeData(edge).forward) {
                        const NodeID to = graph->GetTarget(edge);
                        CHASSERT( to < graph->GetNumberOfNodes(), "Edge leads to out of bounds target node ID. Graph corrupted");
                        const EdgeWeight edgeDistance = graph->GetEdgeData(edge).distance;

                        CHASSERT( edgeDistance > 0, "Edge (" << currentNode << "," << to << ") has length " << edgeDistance );

                        //Stalling
                        if(graph->GetEdgeData(edge).backward && queryHeap.WasInserted( to )) {
                            if(queryHeap.GetKey( to ) + edgeDistance < toDistance) {
                                break;
                            }
                        }

                        //New Node discovered -> Add to Heap + Node Info Storage
                        if ( !queryHeap.WasInserted( to ) ) {
                            queryHeap.Insert( to, toDistance + edgeDistance, 0 );
                        }
                        //Found a shorter Path -> Update distance
                        else if ( toDistance + edgeDistance < queryHeap.GetKey( to ) ) {
                            queryHeap.DecreaseKey( to, toDistance + edgeDistance );
                        }
                    }
                }
            }
            //put the k smallest elements into results vector
            for(unsigned i = 0; i < _maxNumberOfPOIsInBucket && resultHeap.Size() > 0; ++i){
                const NodeID node = resultHeap.DeleteMin();
                const EdgeWeight distance = resultHeap.GetKey(node);
                //INFO("Fixed POI at node " << node << " with distance " << distance);
                CHASSERT(distance >= 0, "Found POI with negative distance");
                if(distance <= _maxDistanceToConsider)
                    resultingVenues.push_back(BucketEntry(node, distance));
            }
            //if(0 < resultingVenues.size() )
            //    INFO("Returning " << resultingVenues.size() << " POIs from search " << queryCount);
            //++queryCount;
        }

    private:
        /** Inits the internal data structures */
        void Initialize() {
            //queryCount = 0;
            additionHeap.reset(new POIHeap(graph->GetNumberOfNodes()));
            //bucketIndex.set_empty_key(UINT_MAX);
            CHASSERT(numberOfThreads > 0, "Number of threads must be a non-negative integer");
            for(unsigned i = 0; i < numberOfThreads; ++i)
                threadDataArray.push_back(std::shared_ptr<_ThreadData>(new _ThreadData(graph->GetNumberOfNodes()) ) );
        }

        struct _ThreadData {
            _ThreadData() {
                assert(false);
            }
            _ThreadData(unsigned size) :queryHeap(size), resultHeap(size) { }
            POIHeap queryHeap;
            POIHeap resultHeap;
        };
        QueryGraphT * graph;
        unsigned maxNumberOfPOIsInBucket;
        unsigned maxDistanceToConsider;
        unsigned numberOfThreads;
        BucketIndex bucketIndex;
        std::shared_ptr<POIHeap> additionHeap;
        std::vector<std::shared_ptr<_ThreadData> > threadDataArray;
        //int queryCount;
    };
}

#endif //POIINDEX_H_INCLUDED
