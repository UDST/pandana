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

#ifndef SIMPLECHQUERY_H_INCLUDED
#define SIMPLECHQUERY_H_INCLUDED
template<class EdgeDataT, class GraphT, class HeapT>
class SimpleCHQuery {
public:
    SimpleCHQuery(GraphT * g, GraphT * r) : _graph(g), _range(r) {
        _forwardHeap = new HeapT(_graph->GetNumberOfNodes());
        _backwardHeap = new HeapT(_graph->GetNumberOfNodes());
        _rangeHeap = new HeapT(_range->GetNumberOfNodes());
    }
    ~SimpleCHQuery() {
        CHDELETE( _forwardHeap);
        CHDELETE( _backwardHeap);
        CHDELETE( _rangeHeap);
    }

    unsigned int ComputeDistanceBetweenNodes(NodeID start, NodeID target) {
        // double time = get_timestamp();
        NodeID middle = ( NodeID ) 0;
        unsigned int _upperbound = std::numeric_limits<unsigned int>::max();
        _forwardHeap->Clear();
        _backwardHeap->Clear();

        _forwardHeap->Insert(start, 0, start);
        _backwardHeap->Insert(target, 0, target);

        while(_forwardHeap->Size() + _backwardHeap->Size() > 0) {
            if ( _forwardHeap->Size() > 0 ) {
                _RoutingStep( _forwardHeap, _backwardHeap, true, &middle, &_upperbound );
            }
            if ( _backwardHeap->Size() > 0 ) {
                _RoutingStep( _backwardHeap, _forwardHeap, false, &middle, &_upperbound );
            }
        }
        // std::cout << "distance computed in " << (get_timestamp() - time) << " s" << std::endl;
        return _upperbound;
    }

    unsigned int ComputeRoute(const NodeID start, const NodeID target, vector<NodeID> & path) {
        // double time = get_timestamp();
        NodeID middle = ( NodeID ) 0;
        unsigned int _upperbound = std::numeric_limits<unsigned int>::max();
        _forwardHeap->Clear();
        _backwardHeap->Clear();

        _forwardHeap->Insert(start, 0, start);
        _backwardHeap->Insert(target, 0, target);

        while(_forwardHeap->Size() + _backwardHeap->Size() > 0) {
            if ( _forwardHeap->Size() > 0 ) {
                _RoutingStep( _forwardHeap, _backwardHeap, true, &middle, &_upperbound );
            }
            if ( _backwardHeap->Size() > 0 ) {
                _RoutingStep( _backwardHeap, _forwardHeap, false, &middle, &_upperbound );
            }
        }

        if ( _upperbound == std::numeric_limits< unsigned int >::max() ) {
            return _upperbound;
        }

        NodeID pathNode = middle;
        deque< NodeID > packedPath;

        while ( pathNode != start ) {
            pathNode = _forwardHeap->GetData( pathNode ).parent;
            packedPath.push_front( pathNode );
        }
        //        NodeID realStart = pathNode;
        packedPath.push_back( middle );
        pathNode = middle;

        while ( pathNode != target ){
            pathNode = _backwardHeap->GetData( pathNode ).parent;
            packedPath.push_back( pathNode );
        }

        path.push_back( packedPath[0] );
        for(deque<NodeID>::size_type i = 0; i < packedPath.size()-1; i++) {
            _UnpackEdge(packedPath[i], packedPath[i+1], path);
        }

        packedPath.clear();

        return _upperbound;
    }


    void RangeQuery(const NodeID start, const unsigned int maxDistance, std::vector<std::pair<NodeID, unsigned> > & resultNodes) {
        _rangeHeap->Clear();
        _rangeHeap->Insert(start, 0, start);
        
        while(_rangeHeap->Size() > 0) {
            const NodeID node = _rangeHeap->DeleteMin(); //_forwardHeap->DeleteMin();
            const unsigned distance = _rangeHeap->GetKey( node ); //_forwardHeap->GetKey( node );
            resultNodes.push_back(std::make_pair(node, distance));
            
            for ( typename GraphT::EdgeIterator edge = _range->BeginEdges( node ); edge < _range->EndEdges(node); edge++ ) {
                const NodeID to = _range->GetTarget(edge);
                const EdgeWeight edgeWeight = _range->GetEdgeData(edge).distance;
                
                assert( edgeWeight > 0 );
                const unsigned int toDistance = distance + edgeWeight;
                
                if(toDistance <= maxDistance && _range->GetEdgeData(edge).forward) {
                    //New Node discovered -> Add to Heap + Node Info Storage
                    if ( !_rangeHeap->WasInserted( to ) ) {
                        _rangeHeap->Insert( to, toDistance, node );
                    }
                    //Found a shorter Path -> Update distance
                    else if ( toDistance < _rangeHeap->GetKey( to ) ) {
                        _rangeHeap->GetData( to ).parent = node;
                        _rangeHeap->DecreaseKey( to, toDistance );
                        //new parent
                    }
                }
            }
        }
    }
    
    //Don't use in production code. This is for verification purposes only
    int SimpleDijkstraQuery(const NodeID start, const NodeID target) {
        HeapT dijkstraHeap( _range->GetNumberOfNodes() );
        dijkstraHeap.Insert(start, 0, start);
        while(dijkstraHeap.Size() > 0) {
            const NodeID node = dijkstraHeap.DeleteMin(); 
            const unsigned distance = dijkstraHeap.GetKey( node );
            if(node == target) {
                return distance;
            }
            
            for ( typename GraphT::EdgeIterator edge = _range->BeginEdges( node ); edge < _range->EndEdges(node); edge++ ) {
                const NodeID to = _range->GetTarget(edge);
                const EdgeWeight edgeWeight = _range->GetEdgeData(edge).distance;
                
                assert( edgeWeight > 0 );
                const unsigned int toDistance = distance + edgeWeight;
                
                if(_range->GetEdgeData(edge).forward) {
                    //New Node discovered -> Add to Heap + Node Info Storage
                    if ( !dijkstraHeap.WasInserted( to ) ) {
                        dijkstraHeap.Insert( to, toDistance, node );
                    }
                    //Found a shorter Path -> Update distance
                    else if ( toDistance < dijkstraHeap.GetKey( to ) ) {
                        dijkstraHeap.GetData( to ).parent = node;
                        dijkstraHeap.DecreaseKey( to, toDistance );
                        //new parent
                    }
                }
            }
        }
        return INT_MAX;
    }
private:

    void _RoutingStep(HeapT * _forwardHeap, HeapT *_backwardHeap, const bool& forwardDirection, NodeID * middle, unsigned int * _upperbound) {
        const NodeID node = _forwardHeap->DeleteMin();
        const unsigned int distance = _forwardHeap->GetKey( node );
        if ( _backwardHeap->WasInserted( node ) ) {
            const unsigned int newDistance = _backwardHeap->GetKey( node ) + distance;
            if ( newDistance < *_upperbound ) {
                *middle = node;
                *_upperbound = newDistance;
            }
        }
        if ( distance > *_upperbound ) {
            _forwardHeap->DeleteAll();
            return;
        }

        for ( typename GraphT::EdgeIterator edge = _graph->BeginEdges( node ); edge < _graph->EndEdges(node); edge++ ) {
            const NodeID to = _graph->GetTarget(edge);
            const EdgeWeight edgeWeight = _graph->GetEdgeData(edge).distance;

            assert( edgeWeight > 0 );

            //Stalling
            bool backwardDirectionFlag = (!forwardDirection) ? _graph->GetEdgeData(edge).forward : _graph->GetEdgeData(edge).backward;
            if(_forwardHeap->WasInserted( to )) {
                if(backwardDirectionFlag) {
                    if(_forwardHeap->GetKey( to ) + edgeWeight < distance) {
                        return;
                    }
                }
            }
        }
        for ( typename GraphT::EdgeIterator edge = _graph->BeginEdges( node ); edge < _graph->EndEdges(node); edge++ ) {
            const NodeID to = _graph->GetTarget(edge);
            const EdgeWeight edgeWeight = _graph->GetEdgeData(edge).distance;

            assert( edgeWeight > 0 );
            const unsigned int toDistance = distance + edgeWeight;


            bool forwardDirectionFlag = (forwardDirection ? _graph->GetEdgeData(edge).forward : _graph->GetEdgeData(edge).backward );
            if(forwardDirectionFlag) {
                //New Node discovered -> Add to Heap + Node Info Storage
                if ( !_forwardHeap->WasInserted( to ) ) {
                    _forwardHeap->Insert( to, toDistance, node );
                }
                //Found a shorter Path -> Update distance
                else if ( toDistance < _forwardHeap->GetKey( to ) ) {
                    _forwardHeap->GetData( to ).parent = node;
                    _forwardHeap->DecreaseKey( to, toDistance );
                    //new parent
                }
            }
        }
    }

    bool _UnpackEdge( const NodeID source, const NodeID target, std::vector< NodeID >& path ) {
        assert(source != target);
        //find edge first.
        typename GraphT::EdgeIterator smallestEdge = SPECIAL_EDGEID;
        EdgeWeight smallestWeight = UINT_MAX;
        for(typename GraphT::EdgeIterator eit = _graph->BeginEdges(source); eit < _graph->EndEdges(source); eit++) {
            const EdgeWeight weight = _graph->GetEdgeData(eit).distance;
            {
                if(_graph->GetTarget(eit) == target && weight < smallestWeight && _graph->GetEdgeData(eit).forward) {
                    smallestEdge = eit; smallestWeight = weight;
                }
            }
        }
        if(smallestEdge == SPECIAL_EDGEID) {
            for(typename GraphT::EdgeIterator eit = _graph->BeginEdges(target); eit < _graph->EndEdges(target); eit++) {
                const EdgeWeight weight = _graph->GetEdgeData(eit).distance;
                {
                    if(_graph->GetTarget(eit) == source && weight < smallestWeight && _graph->GetEdgeData(eit).backward) {
                        smallestEdge = eit; smallestWeight = weight;
                    }
                }
            }
        }

        assert(smallestWeight != SPECIAL_EDGEID); //no edge found. This should not happen at all!

        const EdgeDataT& ed = _graph->GetEdgeData(smallestEdge);
        if(ed.shortcut)
        {//unpack
            const NodeID middle = ed.middleName.middle;
            _UnpackEdge(source, middle, path);
            _UnpackEdge(middle, target, path);
            return false;
        } else {
            assert(!ed.shortcut);
            path.push_back(target);
            return true;
        }
    }


    GraphT * _graph;
    GraphT * _range;
    HeapT * _forwardHeap;
    HeapT * _backwardHeap;
    HeapT * _rangeHeap;

};

#endif 
